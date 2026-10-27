"""Stage 253A — regression tests for the HAL calling-convention recovery.

Pins the concrete convention: the dominant dispatch is `lw $t9, 4($s2)` + `jalr $t9`, and the
attach functions themselves carry zero dispatches (they build the vtable, they do not call
through it).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "dissect_stage253a_hal_calling_convention.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage253a_hal_calling_convention.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok_modules(report: dict) -> list[dict]:
    return [r for r in report["images"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    for key in ("meta", "images", "summary", "gaps"):
        assert key in report
    assert report["meta"]["stage"] == "253A"


def test_four_modules(ok_modules: list[dict]) -> None:
    assert len(ok_modules) == 4
    assert {r["module"] for r in ok_modules} == {"ath_hal.ko", "umac.ko"}


def test_six_functions_located(report: dict) -> None:
    names = {fn for r in report["images"] if r.get("status") == "ok"
             for fn in r["functions"]}
    for expected in ("ath_hal_attach", "_ath_hal_attach", "ath_attach",
                     "__ath_attach", "ol_ath_attach", "__ol_ath_attach"):
        assert expected in names, f"{expected} not located"


def test_jalr_sites_resolved(report: dict) -> None:
    s = report["summary"]
    assert s["functions_found"] == 12
    assert s["jalr_sites"] == 90
    assert s["distinct_vtable_offsets"] == 11


def test_dominant_slot_is_offset_4_from_s2(report: dict) -> None:
    s = report["summary"]
    assert s["top_offsets"].get("4") == 48, "offset 4 must dominate"
    assert s["base_registers"].get("$s2") == 70, "$s2 must dominate as base"
    assert s["base_registers"]["$s2"] > sum(v for k, v in s["base_registers"].items()
                                            if k != "$s2")


def test_attach_functions_do_not_dispatch(ok_modules: list[dict]) -> None:
    # the attach path builds the vtable; it does not call through it
    for r in ok_modules:
        for fn in ("ath_hal_attach", "_ath_hal_attach"):
            if fn in r["functions"]:
                assert r["functions"][fn]["jalr_count"] == 0, f"{fn} unexpectedly dispatches"


def test_ath_attach_carries_most_sites(ok_modules: list[dict]) -> None:
    counts = {fn: f["jalr_count"] for r in ok_modules
              for fn, f in r["functions"].items() if fn == "ath_attach"}
    assert counts and all(v == 41 for v in counts.values())


def test_slots_carry_base_and_offset(ok_modules: list[dict]) -> None:
    for r in ok_modules:
        for fn, f in r["functions"].items():
            for s in f["slots"]:
                assert s["vtable_base"].startswith("$")
                assert isinstance(s["vtable_offset"], int)
                assert s["jalr_at"].startswith("0x")
                assert s["load_at"].startswith("0x")


def test_no_register_write_claimed(report: dict) -> None:
    gaps = " ".join(report["gaps"])
    assert "which of the 11 offsets is the register-write accessor" in gaps
    assert report["summary"]["distinct_vtable_offsets"] >= 11


def test_radio_safety(report: dict) -> None:
    assert "no module loaded" in report["meta"]["scope"]
    assert "no radio contacted" in report["meta"]["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before, "receipt is not deterministic"
