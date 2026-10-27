"""Stage 415A — regression tests.

Pins the two named PLL entry points, the total absence of the clock identifiers, the AC/XW timing
asymmetry, and the SGMT census that shows the bandwidths are not `u32` scalars. Both recovery
counters must stay at zero.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "qca988x_xtensa_pll_clock_divider_sub20mhz_re.py"
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage415a_qca988x_xtensa_pll_sub20mhz_re.json")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


@pytest.fixture(scope="module")
def by(ok: list[dict]) -> dict[str, dict]:
    return {r["module"]: r for r in ok}


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "415A"
    for k in ("meta", "modules", "sgmt_segments", "summary", "gaps"):
        assert k in report


def test_five_modules(ok: list[dict]) -> None:
    assert len(ok) == 5
    assert {r["module"].split(":")[1] for r in ok} == {"ath_hal.ko", "umac.ko"}


def test_pll_entry_points_are_real_symbols(report: dict, by: dict[str, dict]) -> None:
    assert report["summary"]["init_pll_present"] == 1
    assert report["summary"]["set_power_mode_present"] == 1
    assert report["summary"]["pll_symbols_present"] == ["ar9300_init_pll",
                                                        "ar9300_set_power_mode"]
    for ver in ("WA.v8.7.25", "XC.v8.7.25"):
        hal = by[f"{ver}:ath_hal.ko"]
        assert hal["pll_symbols_present"]["ar9300_init_pll"] is True


def test_clock_names_absent(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["clock_name_hits"] == 0
    assert report["summary"]["clock_names_absent"] is True
    for r in ok:
        for tok in ("mac_clock", "adc_clock", "dac_clock", "clkdiv",
                    "clock_div", "quarter_rate", "half_rate"):
            assert r["clock_names"][tok] == 0, (r["module"], tok)


def test_timing_tokens(report: dict, by: dict[str, dict]) -> None:
    s = report["summary"]
    assert s["modules_with_slot_time"] == 4
    assert s["modules_with_ack_timeout"] == 2
    assert s["timing_token_hits"] == 33
    for ver in ("WA.v8.7.25", "XC.v8.7.25"):
        hal = by[f"{ver}:ath_hal.ko"]
        assert hal["timing"]["slot_time"] == 1
        assert hal["timing"]["ack_timeout"] == 2
        assert hal["timing"]["SIFS"] == 0


def test_xw_names_sifs_instead(by: dict[str, dict]) -> None:
    xw = by["XW.v6.3.6:ath_hal.ko"]
    assert xw["timing"]["SIFS"] == 2
    assert xw["timing"]["slot_time"] == 0
    assert xw["timing"]["ack_timeout"] == 0
    # and it does not carry the PLL symbol
    assert xw["pll_symbols_present"]["ar9300_init_pll"] is False
    # the two hits are runtime adjustment messages, not a bare name
    ctx = " ".join(xw["timing_contexts"]["SIFS"])
    assert "Changing SIFS from %d to %d" in ctx
    assert "Restoring SIFS/EIFS/SLOT to %d" in ctx


def test_umac_carries_bandwidth_vocabulary(by: dict[str, dict]) -> None:
    for ver in ("WA.v8.7.25", "XC.v8.7.25"):
        u = by[f"{ver}:umac.ko"]
        assert u["timing"]["chan_width"] == 1
        assert u["timing"]["bw_"] == 4


def test_sgmt_bandwidths_are_not_u32_scalars(report: dict) -> None:
    s = report["summary"]
    assert s["sgmt_segments"] == 2
    assert s["sgmt_bandwidth_u32"] == {"5": 1, "10": 0, "20": 0, "40": 0, "80": 0}
    for seg in report["sgmt_segments"]:
        assert seg["as_u32"]["10"] == 0
        assert seg["as_u32"]["20"] == 0
        assert seg["as_u32"]["40"] == 0
        assert seg["as_u32"]["80"] == 0


def test_no_table_recovered(report: dict) -> None:
    assert report["summary"]["pll_table_recovered"] == 0
    assert report["summary"]["divider_table_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "no table was bound" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no firmware loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
