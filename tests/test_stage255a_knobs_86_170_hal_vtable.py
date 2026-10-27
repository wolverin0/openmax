"""Stage 255A — regression tests for knobs 86..170 against the 253A HAL vtable.

Pins the new structural fact (this slice is exclusively `umac.ko`, zero `ath_dev.ko` literals)
and repeats the 254A guard: the tool must not manufacture vtable attribution from the unsound
low-half match.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "dissect_stage255a_knobs_86_170_hal_vtable.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage255a_knobs_86_170_hal_vtable.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "255A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report


def test_slice_bounds(report: dict) -> None:
    sl = report["meta"]["slice"]
    assert sl["lo"] == 85 and sl["hi"] == 170 and sl["count"] == 85


def test_four_modules(ok: list[dict]) -> None:
    assert len(ok) == 4


def test_umac_holds_all_85(ok: list[dict]) -> None:
    for r in ok:
        if r["module"].endswith("umac.ko"):
            assert r["knobs_with_literal"] == 85, r["module"]


def test_ath_dev_holds_none(ok: list[dict]) -> None:
    # the structural fact this stage adds: slice 2 is exclusively upper-MAC
    for r in ok:
        if r["module"].endswith("ath_dev.ko"):
            assert r["knobs_with_literal"] == 0, r["module"]


def test_no_attribution_manufactured(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["knobs_reaching_vtable"] == 0
    for r in ok:
        assert r["knobs_reaching_vtable"] == 0
    assert report["summary"]["slot_histogram"] == {}


def test_method_limit_is_declared(report: dict) -> None:
    gaps = " ".join(report["gaps"])
    assert "unsound" in gaps or "not sound" in gaps


def test_vtable_offsets_carried(report: dict) -> None:
    offs = report["meta"]["vtable_offsets_from_253a"]
    assert len(offs) == 11 and 4 in offs


def test_row_consistency(ok: list[dict]) -> None:
    for r in ok:
        for k in r["knobs"]:
            if not k["literal_present"]:
                assert "rodata_section" not in k
                continue
            assert k["rodata_section"].startswith(".rodata")
            if k["text_sites"]:
                assert k["function"] is not None
            else:
                assert k["function"] is None


def test_radio_safety(report: dict) -> None:
    assert "no module loaded" in report["meta"]["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
