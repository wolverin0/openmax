#!/usr/bin/env python3
"""Unit & Binary Verification Suite for Stage 125A:
LiteBeam 5AC Gen2 & PowerBeam 5AC Gen2 Public Release Guide (`docs/GUIA_UNIVERSAL_POWERBEAM_LITEBEAM_OPENMAX.md`)
and One-Click Universal WA Flash Verifier (`tools/verify/verify_stage125a_wa_public_release_readiness.py`).
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage125a_wa_public_release_readiness import (
    GUIDE_PATH,
    OUT_JSON,
    verify_stage125a_public_release_readiness,
    verify_universal_guide_doc,
)


def test_universal_guide_doc_budget_and_bilingual_completeness():
    res = verify_universal_guide_doc(GUIDE_PATH)
    assert res["all_checks_passed"] is True, f"Guide checks failed: {res}"
    assert res["line_count"] < 200
    assert res["doc_head_count"] == 1
    assert res["bridges_present_count"] == 13


def test_stage125a_one_click_verifier_and_5pillar_gate():
    receipt = verify_stage125a_public_release_readiness()
    assert OUT_JSON.exists()
    saved = json.loads(OUT_JSON.read_text(encoding="utf-8"))

    gate = audit_stage_receipt_5pillars(saved)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"
    assert saved["stage"] == "125A"
    assert saved["status"] == "CONFIRMED"
    assert saved["safety_verification"]["pbe5ac_241_242_touched"] is False
    assert saved["safety_verification"]["guarida_poe_switches_200_201_touched"] is False
    assert saved["safety_verification"]["flash_writes_performed"] == 0

    matrix = {b["board_slug"]: b for b in saved["one_click_flash_matrix"]}
    assert set(matrix.keys()) == {
        "powerbeam-5ac-gen2",
        "litebeam-5ac-gen2",
        "lap-120",
        "nanostation-ac-loco",
    }
    for slug, b in matrix.items():
        assert b["factory_ap_crc_valid"] is True, f"{slug} factory_ap CRC invalid"
        assert b["factory_sta_crc_valid"] is True, f"{slug} factory_sta CRC invalid"
        assert b["sysupgrade_ap_crc_valid"] is True, f"{slug} sysupgrade_ap CRC invalid"
        assert b["sysupgrade_sta_crc_valid"] is True, f"{slug} sysupgrade_sta CRC invalid"

    parity = receipt["powerbeam_vs_litebeam_parity_summary"]
    assert parity["powerbeam_5ac_gen2_sysid"] == "0xe3d6"
    assert parity["litebeam_5ac_gen2_sysid"] == "0xe7f9"
    assert parity["identical_squashfs_rootfs"] is True
    assert parity["identical_mac80211_teb_ko"] is True
    assert parity["identical_fmx_admitter_v2"] is True
    assert parity["identical_bridge_01_13_tuning"] is True
