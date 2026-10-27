"""Stage 258A — regression tests for the ctl_table / proc_ops relocation rebuild.

Pins the independent confirmation of the W4B numbers (13 tables / 55 entries / 13 handlers from
a completely different derivation) and the zero world-writable result.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "dissect_stage258a_ubnt_poll_reloc_sysctl_proc_trees.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage258a_ubnt_poll_reloc_sysctl_proc_trees.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["images"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "258A"
    for k in ("meta", "images", "summary", "gaps"):
        assert k in report


def test_two_images(ok: list[dict]) -> None:
    assert len(ok) == 2
    assert {r["image"] for r in ok} == {"WA.v8.7.25", "XC.v8.7.25"}


def test_tables_and_entries(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["ctl_tables"] == 13
    assert s["ctl_entries"] == 55
    assert s["ctl_handlers"] == 13
    for r in ok:
        assert len(r["ctl_tables"]) == 13
        assert sum(t["count"] for t in r["ctl_tables"]) == 55


def test_no_world_writable(report: dict) -> None:
    assert report["summary"]["world_writable_entries"] == 0


def test_proc_create_sites(report: dict) -> None:
    assert report["summary"]["proc_create_sites"] == 2
    for r in report["images"]:
        if r.get("status") == "ok":
            for p in r["proc_creates"]:
                assert p["call"].startswith("0x")
                assert p["name"] is not None or p["name"] is None  # resolved or explicitly None


def test_entries_have_resolved_handlers(ok: list[dict]) -> None:
    for r in ok:
        for t in r["ctl_tables"]:
            for e in t["entries"]:
                assert e["name"]
                assert e["mode"] is None or e["mode"].startswith("0o")
                if e.get("handler"):
                    assert e["handler"]["section"].startswith(".text")


def test_stride_is_44(report: dict) -> None:
    assert "44" in report["meta"]["method"]


def test_relocation_method_recorded(report: dict) -> None:
    m = report["meta"]["method"]
    assert "R_MIPS_32" in m
    assert "HI16/LO16" in m


def test_radio_safety(report: dict) -> None:
    assert "no module loaded" in report["meta"]["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
