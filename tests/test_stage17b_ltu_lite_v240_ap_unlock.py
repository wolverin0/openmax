"""Pytest verification suite for Stage 17B (`T-S17B-LTU-LITE-V240-AP-UNLOCK-AND-SEPARATED-BENCH`)."""
from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage17b_ltu_lite_ap_and_separated_ota import (
    DEFAULT_OUTPUT_PATH,
    LTU_LITE_V240_AP_PTMP_SQ_UNLOCK_COMMANDS,
    LTU_LITE_V240_AP_PTP_UNLOCK_COMMANDS,
    LTU_LITE_V240_RESTORE_AP_PTMP_SQ_COMMANDS,
    validate_stage17b_safety,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "docs" / "STAGE17B_LTU_LITE_V240_AP_UNLOCK_AND_OTA_BENCHMARK.md"


def test_stage17b_unlock_commands_safety():
    assert validate_stage17b_safety(LTU_LITE_V240_AP_PTMP_SQ_UNLOCK_COMMANDS) is True
    assert validate_stage17b_safety(LTU_LITE_V240_AP_PTP_UNLOCK_COMMANDS) is True
    assert validate_stage17b_safety(LTU_LITE_V240_RESTORE_AP_PTMP_SQ_COMMANDS) is True
    joined = " && ".join(LTU_LITE_V240_AP_PTMP_SQ_UNLOCK_COMMANDS)
    assert "board_ssid = 0xae05" in joined
    assert "ptmp_max_cpe = 4" in joined
    assert "cfgmtd" not in joined


def test_stage17b_hardware_receipt_and_ap_unlock_verification():
    assert DEFAULT_OUTPUT_PATH.exists(), f"Missing Stage 17B receipt: {DEFAULT_OUTPUT_PATH}"
    data = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    assert data["task_id"] == "T-S17B-LTU-LITE-V240-AP-UNLOCK-AND-SEPARATED-BENCH"

    # Verify both AP-PtMP (SQ) and AP-PtP live hardware unlock proofs
    ptmp_sq = data["live_unlock_verifications"]["ap_ptmp_sq_mode_live"]
    assert ptmp_sq["af_get_role"] == "ap-ptmp"
    assert ptmp_sq["af_get_wireless_mode"] == "ptmp"
    assert "board_ssid = 0xae05" in ptmp_sq["ame_cfg_excerpt"]
    assert "ptmp_max_cpe = 4" in ptmp_sq["ame_cfg_excerpt"]

    ptp = data["live_unlock_verifications"]["ap_ptp_mode_live"]
    assert ptp["af_get_role"] in ("ap-ptp", "ap-ptmp")
    assert ptp["af_get_sysmode"] == "Test"
    assert "wireless_mode = ptp" in ptp["ptp_1cpe_ame_cfg"]
    assert "ptmp_max_cpe = 1" in ptp["ptp_1cpe_ame_cfg"]


def test_stage17b_incremental_rounds_and_final_ram_state():
    data = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    for r_id in ("S17B-R1", "S17B-R3"):
        assert r_id in data["incremental_autoresearch_rounds"]
        r = data["incremental_autoresearch_rounds"][r_id]
        for phase in ("A1", "B1", "A2", "B2"):
            assert phase in r["phases"]
            assert r["phases"][phase]["goodput_mbps"] > 0

    ram = data["final_ram_state"]
    assert ram["persistent_flash_writes"] is False
    assert ram["af_get_role"] == "ap-ptmp"
    assert ram["af_get_powerout"] == "0"
    assert ram["af_get_antennagain"] == "26"
    assert REPORT_PATH.exists(), f"Missing Stage 17B markdown report: {REPORT_PATH}"
