"""Stage 486A — regression tests.

Pins the triple absence (FastLock, quadrature cal, split-frequency LO), the two substring
coincidences (`rx_lo` in `tpc_rx_log`, `split` in `c_string_smart_split`), and the real DCXO
subsystem. All three recovery counters must stay 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage486a_ltu_ad9361_fastlock_and_cal_table_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage486a_ltu_ad9361_fastlock_and_cal_table_re.json")

AD9361_NAMES = ["ame_ad9361_set_rf_err_skip", "ame_ad9361_set_rf_reset_ongoing"]


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def row(report: dict) -> dict:
    return report["modules"][0]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "486A"
    for k in ("meta", "absence", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_eab_driver_absent(report: dict) -> None:
    assert report["absence"]["eab_driver"] == 0
    assert report["summary"]["eab_driver_present"] is False


def test_single_module(row: dict, report: dict) -> None:
    assert row["status"] == "ok"
    assert row["module"] == "ame_core.ko"
    assert row["bytes"] == 3282052
    assert report["summary"]["module_ok"] == 1


def test_three_mechanisms_absent(row: dict, report: dict) -> None:
    s = report["summary"]
    assert s["fastlock_tokens"] == 0
    assert s["synth_tokens"] == 0
    assert s["quad_tokens"] == 0
    assert s["calib_tokens"] == 0
    assert s["qec_tokens"] == 0
    assert s["tx_lo_tokens"] == 0
    assert s["pll_tokens"] == 0
    for tok in ("fastlock", "fast_lock", "synth", "quad", "calib", "qec", "tx_lo", "pll"):
        assert row["mechanism"][tok] == 0, tok


def test_lo_and_split_are_substrings(row: dict, report: dict) -> None:
    s = report["summary"]
    assert s["rx_lo_is_coincidence"] == 1
    assert s["split_is_coincidence"] == 1
    rx = " ".join(row["ambiguous"]["rx_lo"]["contexts"])
    assert "tpc_rx_log" in rx
    split = " ".join(row["ambiguous"]["split"]["contexts"])
    assert "smart_split" in split


def test_ad9361_is_error_and_reset_only(report: dict) -> None:
    s = report["summary"]
    assert s["ad9361_tokens"] == 2
    assert s["ad9361_symbol_count"] == 0
    assert s["ad9361_name_count"] == 2
    assert s["ad9361_names"] == AD9361_NAMES


def test_dcxo_is_the_real_subsystem(row: dict, report: dict) -> None:
    s = report["summary"]
    assert s["dcxo_tokens"] == 68
    assert s["dcxo_symbol_count"] == 30
    assert s["dcxo_name_count"] == 43
    assert s["dcxo_subsystem_named"] == 1
    # ELF symbols
    elsyms = " ".join(row["dcxo_symbols"])
    for tok in ("ame_bbp_op_dcxo", "ame_bbp_rt_keep_dcxo_sync", "ame_dcxo_sync"):
        assert tok in elsyms, tok
    # string-level names (full list lives on the row; the summary truncates to 24)
    names = " ".join(row["dcxo_names"])
    for tok in ("bbp_rf_dcxo_sync_start", "bbp_rf_dcxo_sync_track",
                "bbp_rf_dcxo_sync_adjust", "bbp_rf_dcxo_adj"):
        assert tok in names, tok


def test_dcxo_distinguishes_gps_from_tcxo(row: dict) -> None:
    names = " ".join(row["dcxo_names"])
    assert "bbp_rf_dcxo_is_sync_by_gps" in names
    assert "bbp_rf_dcxo_is_sync_by_tcxo" in names
    assert "bbp_rf_dcxo_set_sync_mode" in names
    assert "bbp_rf_dcxo_get_gps_state" in names


def test_nothing_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["fastlock_profile_recovered"] == 0
    assert s["tx_quad_cal_table_recovered"] == 0
    assert s["split_frequency_lo_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "0 hits" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
