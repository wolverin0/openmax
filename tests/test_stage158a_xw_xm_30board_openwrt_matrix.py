#!/usr/bin/env python3
"""Unit & Binary Verification Suite for Stage 158A:
XW 30-Board (`XW.v6.3.6` `ubnthal.ko`) + XM (`32 MB` vs `64 MB` RAM Safety Gate) OpenWrt DTB Matrix
and Guarida Panel2/Panel3 28-CPE Mapping.
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
    / "stage158a_xw_xm_30board_openwrt_matrix.json"
)


def test_stage158a_xw_30_board_records_and_5pillar_gate():
    assert ARTIFACT_PATH.exists(), f"Missing {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "158A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_verification"]["pbe5ac_241_242_touched"] is False
    assert data["safety_verification"]["guarida_poe_switches_200_201_touched"] is False
    assert data["safety_verification"]["flash_writes_performed"] == 0

    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"

    pa = data["pillar_a_ground_up_re_and_knob_catalog"]
    assert pa["xw_30_records_count"] == 30
    assert pa["xw_production_boards_count"] == 29
    assert pa["xw_dual_port_poe_gpio2_sysids"] == ["0xe855", "0xe866"]
    assert pa["guarida_panel2_panel3_cpes_mapped_count"] == 28

    records = data["xw_30_board_records"]
    assert len(records) == 30
    assert [r["record_index"] for r in records] == list(range(30))


def test_stage158a_xw_dual_port_poe_and_xm_32mb_ram_safety_gate():
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    xw_records = data["xw_30_board_records"]
    xm_matrix = data["xm_ram_safety_matrix"]
    g_sum = data["guarida_panel2_panel3_28cpe_summary"]

    assert g_sum["panel2_22_cpes_count"] == 22
    assert g_sum["panel3_6_cpes_count"] == 6
    assert g_sum["total_panel2_panel3_cpes"] == 28

    # Verify XW dual-port PoE passthrough GPIO 2 boards (0xe855 NSM5 XW and 0xe866 NSM2 XW)
    for r in xw_records:
        if r["sysid"] in {"0xe855", "0xe866"}:
            assert r["board_phycount"] == 2
            assert r["poe_passthrough_gpio"] == 2
            assert r["ram_safety_gate"] == "PASS_64MB_XW_DUAL_PORT_POE_GPIO2_DTB_REQUIRED"
        elif r["sysid"] == "0x0205":
            assert r["openwrt_24_10_4_direct_safe"] is False
        else:
            assert r["ram_mib"] == 64
            assert r["openwrt_24_10_4_direct_safe"] is True

    # Verify XM 32MB OOM safety gate blocks OpenWrt 24.10.4 flashing while preserving WDS interop
    for m in xm_matrix:
        assert m["zero_touch_wds_interop_with_openwrt_wa_ap"] is True
        if m["ram_mib"] == 32:
            assert m["openwrt_24_10_4_direct_safe"] is False
            assert m["ram_safety_gate"] == "BLOCK_OPENWRT_24_10_4_ON_32MB_XM_KEEP_AIROS6_RC_POSTSTART_MODE_B"
