#!/usr/bin/env python3
"""Unit & Binary Verification Suite for Stage 129A:
Complete Ubiquiti `WA`, `XC`, `2XC`, `XW`, and `XM` Model Compatibility Matrix & OpenMAX Installer Matcher.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.firmware.detect_and_match_openmax_image import (
    OUT_JSON,
    build_stage129a_receipt,
    build_unified_catalog,
    detect_and_match_from_board_info,
    match_by_sysid,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


def test_stage129a_receipt_passes_5pillar_gate_and_binary_counts():
    receipt = build_stage129a_receipt()
    assert OUT_JSON.exists(), f"Missing {OUT_JSON}"
    saved = json.loads(OUT_JSON.read_text(encoding="utf-8"))

    gate = audit_stage_receipt_5pillars(saved)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"
    assert saved["stage"] == "129A"
    assert saved["status"] == "CONFIRMED"
    assert saved["safety_verification"]["pbe5ac_241_242_touched"] is False
    assert saved["safety_verification"]["guarida_poe_switches_200_201_touched"] is False
    assert saved["safety_verification"]["flash_writes_performed"] == 0

    pa = saved["pillar_a_ground_up_re_and_knob_catalog"]
    assert pa["dissected_elf_binaries"]["wa_8725_ubnthal_ko"]["board_records_count"] == 31
    assert pa["dissected_elf_binaries"]["xc_8725_ubnthal_ko"]["board_records_count"] == 34
    assert pa["dissected_elf_binaries"]["xw_636_ubnthal_ko"]["board_records_count"] == 30
    assert pa["total_hal_records_decoded"] == 95
    assert pa["unique_sysids_mapped_count"] >= 50


def test_detect_and_match_wa_xc_xw_xm_models():
    cat = build_unified_catalog()

    # 1. PowerBeam 5AC Gen2 (0xe3d6) AP & STA
    pbe_ap = detect_and_match_from_board_info(
        "board.sysid=0xe3d6\nboard.model=PBE-5AC-Gen2\nboard.name=PowerBeam 5AC\n",
        role="ap",
        catalog=cat,
    )
    assert pbe_ap["matched"] is True
    assert pbe_ap["resolved_family"] == "WA"
    assert pbe_ap["openmax_kit_category"] == "wa_universal_kit"
    assert pbe_ap["recommended_factory_image"] == "openwrt-24.10.4-powerbeam-5ac-gen2-factory-ap.bin"
    assert len(pbe_ap["recommended_factory_sha256"]) == 64
    assert pbe_ap["recommended_factory_sha256"] == cat["by_sysid"]["0xe3d6"]["openwrt_24_10_4_images"]["factory_ap_sha256"]

    pbe_sta = detect_and_match_from_board_info(
        "board.sysid=0xe3d6\nboard.model=PBE-5AC-Gen2\nboard.name=PowerBeam 5AC\n",
        role="sta",
        catalog=cat,
    )
    assert pbe_sta["recommended_factory_image"] == "openwrt-24.10.4-powerbeam-5ac-gen2-factory-sta.bin"
    assert len(pbe_sta["recommended_factory_sha256"]) == 64
    assert pbe_sta["recommended_factory_sha256"] == cat["by_sysid"]["0xe3d6"]["openwrt_24_10_4_images"]["factory_sta_sha256"]

    # 2. LiteBeam 5AC Gen2 (0xe7f9) AP & STA
    lbe_ap = detect_and_match_from_board_info(
        "board.sysid=0xe7f9\nboard.model=LBE-5AC-Gen2\nboard.name=LiteBeam 5AC\n",
        role="ap",
        catalog=cat,
    )
    assert lbe_ap["matched"] is True
    assert lbe_ap["resolved_family"] == "WA"
    assert lbe_ap["recommended_factory_image"] == "openwrt-24.10.4-litebeam-5ac-gen2-factory-ap.bin"
    assert len(lbe_ap["recommended_factory_sha256"]) == 64
    assert lbe_ap["recommended_factory_sha256"] == cat["by_sysid"]["0xe7f9"]["openwrt_24_10_4_images"]["factory_ap_sha256"]

    # 3. LiteAP AC LAP-120 (0xe8e5) & NanoStation 5AC Loco (0xe7fa)
    lap = match_by_sysid("0xe8e5", role="ap", catalog=cat)
    assert lap["matched"] is True and lap["resolved_family"] == "WA"
    assert lap["recommended_factory_image"] == "openwrt-24.10.4-lap-120-factory-ap.bin"

    loco = match_by_sysid("0xe7fa", role="sta", catalog=cat)
    assert loco["matched"] is True and loco["resolved_family"] == "WA"
    assert loco["recommended_factory_image"] == "openwrt-24.10.4-nanostation-ac-loco-factory-sta.bin"

    # 4. Rocket Prism 5AC Gen2 (0xe7e9, XC)
    rp = detect_and_match_from_board_info(
        "board.sysid=0xe7e9\nboard.model=RP-5AC-Gen2\nboard.cpurevision=0x00001130\n",
        role="ap",
        catalog=cat,
    )
    assert rp["matched"] is True
    assert rp["resolved_family"] == "XC"
    assert rp["openmax_kit_category"] == "xc_kit"

    # 5. LiteBeam M5 XW (0xe865) & LiteBeam M5 XM (0xe4a2)
    xw = match_by_sysid("0xe865", role="sta", catalog=cat)
    assert xw["matched"] is True and xw["resolved_family"] == "XW"
    assert xw["openmax_kit_category"] == "xw_kit"

    xm = match_by_sysid("0xe4a2", role="sta", catalog=cat)
    assert xm["matched"] is True and xm["resolved_family"] == "XM"
    assert xm["openmax_kit_category"] == "xm_rc_poststart_mode_b"

    # 6. Unknown sysid fails closed
    unk = match_by_sysid("0xffff", catalog=cat)
    assert unk["matched"] is False
    assert "fail-closed" in unk["error"]
