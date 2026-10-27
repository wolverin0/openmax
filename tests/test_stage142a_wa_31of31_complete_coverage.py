#!/usr/bin/env python3
"""Unit & Binary Verification Suite for Stage 142A:
Complete 31-of-31 WA Family Coverage (`15` single-PHY `1port` sysids / `28` board records +
`2` dual-PHY `2port` GPIO 3 PoE passthrough sysids / `3` board records `0xe7fb` `NS-5AC` & `0xe7fc` `NBE-5AC-Gen2`).
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.firmware.detect_and_match_openmax_image import (
    STAGE142A_OUT_JSON,
    WA_SYSID_DTB_TOPOLOGY,
    WA_SYSID_TO_UNIVERSAL_SLUG,
    build_stage142a_receipt,
    build_unified_catalog,
    match_by_sysid,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage125a_wa_public_release_readiness import (
    GUIDE_PATH,
    verify_universal_guide_doc,
)


SINGLE_PHY_PBE_DTB_SYSIDS = {
    "0xe3d6",
    "0xe3d9",
    "0xe6f5",
    "0xe7f5",
    "0xe7f7",
    "0xe9f5",
    "0xe2c5",
    "0xe2c7",
}
SINGLE_PHY_LBE_LAP_LOCO_DTB_SYSIDS = {
    "0xe7f9",
    "0xe7fe",
    "0xe7ff",
    "0xe8f5",
    "0xe8e5",
    "0xe7fd",
    "0xe7fa",
}
DUAL_PHY_2PORT_POE_SYSIDS = {"0xe7fb", "0xe7fc"}


def test_stage142a_receipt_passes_5pillar_gate_and_31of31_counts():
    receipt = build_stage142a_receipt()
    assert STAGE142A_OUT_JSON.exists(), f"Missing {STAGE142A_OUT_JSON}"
    saved = json.loads(STAGE142A_OUT_JSON.read_text(encoding="utf-8"))

    gate = audit_stage_receipt_5pillars(saved)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"
    assert saved["stage"] == "142A"
    assert saved["status"] == "CONFIRMED"
    assert saved["safety_verification"]["pbe5ac_241_242_touched"] is False
    assert saved["safety_verification"]["guarida_poe_switches_200_201_touched"] is False
    assert saved["safety_verification"]["flash_writes_performed"] == 0

    pa = saved["pillar_a_ground_up_re_and_knob_catalog"]
    assert pa["total_wa_records_verified"] == 31
    assert pa["unique_wa_sysids_verified"] == 17
    assert pa["single_phy_1port_records_count"] == 28
    assert pa["single_phy_1port_sysids_count"] == 15
    assert pa["dual_phy_2port_records_count"] == 3
    assert pa["dual_phy_2port_sysids_count"] == 2
    assert receipt["pillar_d_scientific_pareto_validation"]["wa_31_of_31_coverage_ratio"] == 1.0


def test_stage142a_all_15_single_phy_and_2_dual_phy_wa_sysids_matched():
    cat = build_unified_catalog()
    assert set(WA_SYSID_TO_UNIVERSAL_SLUG.keys()) == (
        SINGLE_PHY_PBE_DTB_SYSIDS | SINGLE_PHY_LBE_LAP_LOCO_DTB_SYSIDS | DUAL_PHY_2PORT_POE_SYSIDS
    )
    assert set(WA_SYSID_DTB_TOPOLOGY.keys()) == set(WA_SYSID_TO_UNIVERSAL_SLUG.keys())

    # 1. Verify all 8 4-LED 74HC164 single-PHY sysids map to powerbeam-5ac-gen2
    for sid in SINGLE_PHY_PBE_DTB_SYSIDS:
        m = match_by_sysid(sid, platform_hint="WA", role="ap", catalog=cat)
        assert m["matched"] is True
        assert m["resolved_family"] == "WA"
        assert m["wa_universal_image_slug"] == "powerbeam-5ac-gen2"
        assert m["wa_dtb_port_topology"] == "1port_single_ar8035"
        assert m["openwrt_dtsi_include"] == "ar9342_ubnt_wa_1port.dtsi"
        assert m["can_run_1port_pbe_lbe_dtb_directly"] is True
        assert m["board_phycount"] == 1
        assert m["poe_passthrough_gpio"] is None
        assert m["recommended_factory_image"] == "openwrt-24.10.4-powerbeam-5ac-gen2-factory-ap.bin"

    # 2. Verify all 7 direct-GPIO LED single-PHY sysids map to litebeam-5ac-gen2 / lap-120 / nanostation-ac-loco
    for sid in SINGLE_PHY_LBE_LAP_LOCO_DTB_SYSIDS:
        m = match_by_sysid(sid, platform_hint="WA", role="sta", catalog=cat)
        assert m["matched"] is True
        assert m["resolved_family"] == "WA"
        assert m["wa_dtb_port_topology"] == "1port_single_ar8035"
        assert m["openwrt_dtsi_include"] == "ar9342_ubnt_wa_1port.dtsi"
        assert m["can_run_1port_pbe_lbe_dtb_directly"] is True
        assert m["board_phycount"] == 1
        assert m["poe_passthrough_gpio"] is None
        if sid in {"0xe7f9", "0xe7fe", "0xe7ff", "0xe8f5"}:
            assert m["wa_universal_image_slug"] == "litebeam-5ac-gen2"
        elif sid in {"0xe8e5", "0xe7fd"}:
            assert m["wa_universal_image_slug"] == "lap-120"
        elif sid == "0xe7fa":
            assert m["wa_universal_image_slug"] == "nanostation-ac-loco"

    # Verify LAP-GPS (0xe7fd) has GPIO 11 GPS UART metadata
    lap_gps = match_by_sysid("0xe7fd", platform_hint="WA", role="ap", catalog=cat)
    assert lap_gps["aux_gps_gpio"] == 11

    # 3. Verify 2-port dual-PHY GPIO 3 PoE passthrough sysids (0xe7fb NS-5AC & 0xe7fc NBE-5AC-Gen2)
    for sid in DUAL_PHY_2PORT_POE_SYSIDS:
        m = match_by_sysid(sid, platform_hint="WA", role="ap", catalog=cat)
        assert m["matched"] is True
        assert m["resolved_family"] == "WA"
        assert m["wa_dtb_port_topology"] == "2port_dual_eth_gpio3_poe_passthrough"
        assert m["openwrt_dtsi_include"] == "ar9342_ubnt_wa_2ports.dtsi"
        assert m["can_run_1port_pbe_lbe_dtb_directly"] is False
        assert m["board_phycount"] == 2
        assert m["poe_passthrough_gpio"] == 3


def test_stage142a_universal_guide_documents_all_31_wa_boards_and_2port_poe():
    res = verify_universal_guide_doc(GUIDE_PATH)
    assert res["all_checks_passed"] is True
    assert res["line_count"] < 200
    assert res["doc_head_count"] == 1

    txt = GUIDE_PATH.read_text(encoding="utf-8") + "\n" + STAGE142A_OUT_JSON.read_text(encoding="utf-8")
    for token in [
        "0xe3d6",
        "0xe3d9",
        "0xe6f5",
        "0xe7f5",
        "0xe7f7",
        "0xe9f5",
        "0xe2c5",
        "0xe2c7",
        "0xe7f9",
        "0xe7fe",
        "0xe7ff",
        "0xe8f5",
        "0xe8e5",
        "0xe7fd",
        "0xe7fa",
        "0xe7fb",
        "0xe7fc",
        "wa_2ports.dtsi",
        "GPIO 3",
    ]:
        assert token in txt, f"Missing {token} in {GUIDE_PATH} / {STAGE142A_OUT_JSON}"
