"""Stage 257A — regression tests for the exact `.rel.text` relocation join.

Pins the two defects that were fixed and the resulting numbers:

  * `st_value` must be added to the addend;
  * HI16/LO16 pairing must be positional, not a global per-register dict.

If either regresses, the attribution count collapses back to 2 and this suite fails.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "dissect_stage257a_reltext_rodata_knob_vtable_join.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage257a_reltext_rodata_knob_vtable_join.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "257A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report


def test_six_modules(ok: list[dict]) -> None:
    assert len(ok) == 6
    mods = {r["module"].split(":")[1] for r in ok}
    assert mods == {"umac.ko", "ath_dev.ko", "ubnt_poll_host.ko"}


def test_join_is_not_the_broken_two(report: dict) -> None:
    # 2 was the count with the global per-register dict; the positional join gives 106
    assert report["summary"]["knobs_attributed"] == 106
    assert report["summary"]["knobs_attributed"] > 100, \
        "attribution collapsed: the HI16/LO16 pairing likely regressed to a global dict"


def test_per_module_attribution(ok: list[dict]) -> None:
    by = {r["module"]: r for r in ok}
    for image in ("WA.v8.7.25", "XC.v8.7.25"):
        assert by[f"{image}:umac.ko"]["attributed"] == 41
        assert by[f"{image}:ath_dev.ko"]["attributed"] == 0
        assert by[f"{image}:ubnt_poll_host.ko"]["attributed"] == 12


def test_literal_counts(ok: list[dict]) -> None:
    by = {r["module"]: r for r in ok}
    assert by["WA.v8.7.25:umac.ko"]["knobs_in_module"] == 320
    assert by["WA.v8.7.25:ath_dev.ko"]["knobs_in_module"] == 6
    assert by["WA.v8.7.25:ubnt_poll_host.ko"]["knobs_in_module"] == 33


def test_zero_vtable_reach_is_now_meaningful(report: dict) -> None:
    # with sound attribution, zero is a finding rather than an instrument failure
    assert report["summary"]["knobs_reaching_253a"] == 0
    assert report["summary"]["slot_histogram"] == {}


def test_attributed_rows_have_a_function(ok: list[dict]) -> None:
    for r in ok:
        for k in r["knobs"]:
            if k["sites"]:
                assert k["function"] is not None
                assert k["function"].startswith("0x")
                assert k["rodata_offset"].startswith("0x")


def test_unattributed_rows_are_marked(ok: list[dict]) -> None:
    for r in ok:
        for k in r["knobs"]:
            if not k["sites"]:
                assert k["function"] is None
                assert k["reaches_253a"] is False


def test_method_is_documented(report: dict) -> None:
    m = report["meta"]["method"]
    assert "R_MIPS_HI16" in m and "R_MIPS_LO16" in m


def test_vtable_offsets_carried(report: dict) -> None:
    offs = report["meta"]["vtable_offsets_from_253a"]
    assert len(offs) == 11 and 4 in offs


def test_radio_safety(report: dict) -> None:
    assert "no module loaded" in report["meta"]["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
