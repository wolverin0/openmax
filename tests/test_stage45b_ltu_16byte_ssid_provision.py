#!/usr/bin/env python3
"""
Unit tests for Stage 45B (LTU 16-byte SSID "FMX-LTU", alternating 5500/5520 scan list, +15 dBm distance power).
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.bench.deploy_stage40a_ltu_poststart import LTU1_RC_POSTSTART, LTU2_RC_POSTSTART
from tools.bench.run_stage45b_ltu_16byte_ssid_and_boca7_provisioner import (
    BEACON_MAX_SSID_BYTES,
    OUT_JSON_PATH,
    STAGE45B_ALTERNATING_FREQ_LIST,
    STAGE45B_SSID,
    validate_stage45b_ssid,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage45b_ssid_length_and_poststart_invariants() -> None:
    """Verify FMX-LTU is strictly <= 16 bytes and configured in both LTU1 and LTU2 poststart scripts."""
    assert validate_stage45b_ssid(STAGE45B_SSID) is True
    assert len(STAGE45B_SSID.encode("utf-8")) == 7 <= BEACON_MAX_SSID_BYTES
    assert validate_stage45b_ssid("FuturaMAX-LTU-Bench") is False

    assert 'ssid = "FMX-LTU"' in LTU1_RC_POSTSTART
    assert "txpwr = 15" in LTU1_RC_POSTSTART
    assert "antenna_gain = 13" in LTU1_RC_POSTSTART
    assert "board_ssid = 0xae08" in LTU1_RC_POSTSTART

    assert 'ssid = "FMX-LTU"' in LTU2_RC_POSTSTART
    assert 'amecli ssid "FMX-LTU"' in LTU2_RC_POSTSTART
    assert f"amecli freq_list {STAGE45B_ALTERNATING_FREQ_LIST}" in LTU2_RC_POSTSTART
    assert "txpwr = 15" in LTU2_RC_POSTSTART
    assert "antenna_gain = 13" in LTU2_RC_POSTSTART


def test_stage45b_artifact_and_report_completeness() -> None:
    """Verify Stage 45B JSON receipt and markdown report exist and confirm FMX-LTU on LTU-Lite #1."""
    assert OUT_JSON_PATH.exists(), f"Missing Stage 45B artifact: {OUT_JSON_PATH}"
    data = json.loads(OUT_JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 45B"
    assert data["task_id"] == "T-S45B-LTU-16BYTE-SSID-FMX-LTU-AND-BOCA7-AUTO-PROVISIONER"
    assert data["root_causes_fixed"]["beacon_16byte_ssid_truncation"]["new_ssid"] == "FMX-LTU"
    assert data["root_causes_fixed"]["beacon_16byte_ssid_truncation"]["new_ssid_len_bytes"] == 7

    ltu1 = data["ltu1_boca5"]
    assert "AP-PTMP(Run)" in ltu1["common_info"]
    assert "SSID:FMX-LTU " in ltu1["common_info"]
    assert ltu1["ssid_exact_match"] is True

    report_path = (
        REPO_ROOT / "docs" / "STAGE45B_LTU_16BYTE_SSID_TRUNCATION_AND_OTA_PROVISIONING.md"
    )
    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "FMX-LTU" in text
    assert "5500 5520 5500 5520" in text
