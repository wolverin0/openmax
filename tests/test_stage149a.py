from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage149a_ltu_4096qam_and_tdma_re_receipt.json"


def test_stage149a_receipt_exists_and_binaries_dissected() -> None:
    assert RECEIPT_PATH.exists(), f"Missing {RECEIPT_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "149A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_envelope"]["touched_dev_ame_nodes"] is False
    assert data["safety_envelope"]["touched_241_or_242"] is False

    bins = data["binaries_dissected"]
    assert bins["cpe_ame_core_ko"]["size_bytes"] > 200000
    assert bins["ap_ame_core_ko"]["size_bytes"] > 200000
    assert bins["cpe_cds_mac_mod_ko_eab"]["size_bytes"] > 10000
    assert bins["cpe_ame_dev_ko"]["size_bytes"] > 10000


def test_stage149a_4096qam_tables_and_tdma_scheduler() -> None:
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    tables = data["ltu_4096qam_12x_tables"]
    th = tables["rate_control_thresholds"]
    assert th["startThrd_4096"] == 97
    assert th["stayThrd_4096"] == 90
    assert th["maxMCS"] == 31

    assert tables["table_ptpPwrRange_12_mod_bands_dbm"] == [28, 28, 28, 28, 27, 26, 25, 25, 24, 23, 22, 22]
    assert tables["table_ptmpAPPwrRange_12_mod_bands_dbm"] == [27, 27, 27, 27, 26, 25, 24, 24, 23, 22, 21, 21]
    assert len(tables["sensitivity_32_mcs_slots_dBm"]) == 32
    assert tables["ame_bbp_op_evm_mcs_map"]["present"] is True

    ladder = tables["synthesized_12_band_modulation_ladder"]
    assert len(ladder) == 12
    assert ladder[-1]["modulation"] == "4096-QAM-5/6 (12x)"
    assert ladder[-1]["Order_bits_per_sym"] == 12
    assert ladder[-1]["ptp_tx_pwr_backoff_dbm"] == 22
    assert ladder[-1]["ptmp_ap_tx_pwr_backoff_dbm"] == 21

    tdma = data["tdma_split_duty_scheduler_and_eab"]
    assert tdma["symbol_duration_us"] == 25.0
    assert len(tdma["superframe_options"]) == 3
    assert len(tdma["eab_cds_mac_mod_key_symbols"]) >= 10


def test_stage149a_five_pillars() -> None:
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    for k in (
        "pillar_1_binary_re",
        "pillar_2_closed_loop_reactor",
        "pillar_3_counterbalanced_harness",
        "pillar_4_scientific_skills",
        "pillar_5_memory_master",
    ):
        assert data[k]["status"] == "CONFIRMED"
