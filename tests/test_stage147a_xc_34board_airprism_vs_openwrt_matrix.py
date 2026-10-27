#!/usr/bin/env python3
"""Unit & Binary Verification Suite for Stage 147A:
XC-Family 34-Board OpenWrt & AirPrism Compatibility Matrix (`18` Active AirPrism/HSR records across
`7` sysids vs `16` Passive Dish/Horn/CPE/Lite XC records across `6` sysids).
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage147a_xc_34board_airprism_vs_openwrt_matrix.json"
)

ACTIVE_AIRPRISM_HSR_SYSIDS = {
    "0xe7e7",
    "0xe7e9",
    "0xe7e5",
    "0xe7e6",
    "0xe7e8",
    "0xdc97",
    "0xe3f5",
}
PASSIVE_OPENWRT_DIRECT_SYSIDS = {
    "0xe1f5",
    "0xe3d5",
    "0xe5f5",
    "0xe4f5",
    "0xe3d7",
    "0xe3d8",
}


def test_stage147a_xc_34_board_records_and_5pillar_gate():
    assert ARTIFACT_PATH.exists(), f"Missing {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "147A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_verification"]["pbe5ac_241_242_touched"] is False
    assert data["safety_verification"]["guarida_poe_switches_200_201_touched"] is False
    assert data["safety_verification"]["flash_writes_performed"] == 0

    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"

    pa = data["pillar_a_ground_up_re_and_knob_catalog"]
    assert pa["total_xc_records_verified"] == 34
    assert pa["unique_xc_sysids_verified"] == 13
    assert pa["active_airprism_hsr_records_count"] == 18
    assert pa["active_airprism_hsr_sysids_count"] == 7
    assert pa["passive_openwrt_direct_records_count"] == 16
    assert pa["passive_openwrt_direct_sysids_count"] == 6

    records = data["xc_34_board_records"]
    assert len(records) == 34
    assert [r["record_index"] for r in records] == list(range(34))


def test_stage147a_active_airprism_vs_passive_openwrt_classification():
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    records = data["xc_34_board_records"]
    sysids = data["xc_unique_sysid_matrix"]

    assert set(sysids.keys()) == (ACTIVE_AIRPRISM_HSR_SYSIDS | PASSIVE_OPENWRT_DIRECT_SYSIDS)

    for r in records:
        if r["sysid"] in ACTIVE_AIRPRISM_HSR_SYSIDS:
            assert r["xc_class"] == "ACTIVE_AIRPRISM_HSR_PRESERVE_AIROS8_RC_POSTSTART_MODE_B"
            assert r["has_active_airprism_filter"] is True
            assert r["has_hsr_spectrum_scanner"] is True
            assert r["has_hsr_bit28"] is True
            assert r["hsr_param"] > 0
            assert r["can_run_openwrt_without_losing_airprism"] is False
            knobs_joined = " ".join(r["rc_poststart_knobs"])
            assert "set_multiq 3" in knobs_joined
            assert "daprot" in knobs_joined
            assert "ff_mcast_airtime_limit" in knobs_joined
            assert "ACVOMinfree=0" in knobs_joined
            assert "enable_tx_tcp_cksum" in knobs_joined
        else:
            assert r["sysid"] in PASSIVE_OPENWRT_DIRECT_SYSIDS
            assert r["xc_class"] == "PASSIVE_XC_DIRECT_OPENWRT_ATH79_COMPATIBLE"
            assert r["radio0_caps_hex"] == "0xace00814"
            assert r["has_airprism_bit30"] is False
            assert r["has_hsr_bit28"] is False
            assert r["hsr_param"] == 0
            assert r["has_active_airprism_filter"] is False
            assert r["has_hsr_spectrum_scanner"] is False
            assert r["can_run_openwrt_without_losing_airprism"] is True
            assert "qca9558_ubnt_" in r["openwrt_dts_reference"]
