"""Stage 254A — regression tests for knobs 1..85 against the 253A HAL vtable.

Pins two things: every knob in this slice is a real literal in `umac.ko`, and the tool did NOT
manufacture a vtable attribution. The zero is recorded as a method limit, and a test fails if a
future run starts reporting attribution from the unsound low-half match.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "dissect_stage254a_knobs_1_85_hal_vtable.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage254a_knobs_1_85_hal_vtable.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "254A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report


def test_slice_is_85(report: dict) -> None:
    assert report["meta"]["slice"]["count"] == 85
    assert report["meta"]["slice"]["boundary"] == "airOS_UMAC_UPH"
    assert report["summary"]["knobs"] == 85


def test_four_modules(ok: list[dict]) -> None:
    assert len(ok) == 4
    assert {r["module"] for r in ok} == {"WA.v8.7.25:umac.ko", "WA.v8.7.25:ath_dev.ko",
                                         "XC.v8.7.25:umac.ko", "XC.v8.7.25:ath_dev.ko"}


def test_umac_holds_all_85_literals(ok: list[dict]) -> None:
    for r in ok:
        if r["module"].endswith("umac.ko"):
            assert r["knobs_with_literal"] == 85, r["module"]


def test_ath_dev_holds_only_three(ok: list[dict]) -> None:
    for r in ok:
        if r["module"].endswith("ath_dev.ko"):
            assert r["knobs_with_literal"] == 3


def test_no_attribution_was_manufactured(report: dict, ok: list[dict]) -> None:
    # the low-16 match is unsound, so the tool must not claim any attribution
    assert report["summary"]["knobs_reaching_vtable"] == 0
    for r in ok:
        assert r["knobs_reaching_vtable"] == 0
    assert report["summary"]["slot_histogram"] == {}


def test_limit_is_declared_not_hidden(report: dict) -> None:
    gaps = " ".join(report["gaps"])
    assert "not that this knob is the argument" in gaps or "not sound" in gaps or \
           "a knob referenced" in gaps


def test_vtable_offsets_carried_from_253a(report: dict) -> None:
    offs = report["meta"]["vtable_offsets_from_253a"]
    assert 4 in offs and 8 in offs and 520 in offs
    assert len(offs) == 11


def test_every_knob_row_is_consistent(ok: list[dict]) -> None:
    for r in ok:
        for k in r["knobs"]:
            if not k["literal_present"]:
                # absent in this module: no rodata/text attribution must be claimed
                assert "rodata_section" not in k
                assert "function" not in k
                continue
            assert k["rodata_section"].startswith(".rodata")
            assert k["rodata_offset"].startswith("0x")
            # a literal can exist without any lui/addiu low-half match; in that case the
            # function is None and no attribution is claimed
            if k["text_sites"]:
                assert k["function"] is not None
            else:
                assert k["function"] is None
                assert k["vtable_slots"] == []
                assert k["reaches_253a_vtable"] is False


def test_radio_safety(report: dict) -> None:
    assert "no module loaded" in report["meta"]["scope"]
    assert "no radio contacted" in report["meta"]["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
