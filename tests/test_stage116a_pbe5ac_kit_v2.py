#!/usr/bin/env python3
"""
Tests for Stage 116A — PowerBeam 5AC Gen2 OpenWrt 24.10.4 Kit v2 Integrity &
Dynamic phy*-ap0 Admitter Validator.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage116a_pbe5ac_kit_v2 import verify_stage116a_kit_v2

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_JSON = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage116a_pbe5ac_kit_v2_receipt.json"
)
ADMITTER_SH = (
    REPO_ROOT
    / "firmware"
    / "openwrt"
    / "pbe5ac_gen2_ptp_kit"
    / "fmx_pbe5ac_admitter.sh"
)


def test_stage116a_receipt_passes_5pillars() -> None:
    assert RECEIPT_JSON.exists(), f"Missing {RECEIPT_JSON}"
    receipt = json.loads(RECEIPT_JSON.read_text(encoding="utf-8"))
    assert receipt["stage"] == "116A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["live_radios_241_242_touched"] is False

    audit = audit_stage_receipt_5pillars(receipt)
    assert audit["compliant"], f"5-Pillar gate failed: {audit}"
    assert str(receipt["pillar_e_memory_master_claim_id"]).startswith("mm-")


def test_stage116a_dynamic_phy_admitter_and_beacon_int_30() -> None:
    receipt = verify_stage116a_kit_v2()
    assert receipt["all_kit_v2_checks_passed"] is True

    adm = receipt["admitter_v2_verification"]
    assert adm["all_checks_passed"] is True
    checks = adm["checks"]
    assert checks["has_resolve_obj_fn"] is True
    assert checks["uses_ubus_wildcard_phy_ap0"] is True
    assert checks["uses_sysfs_wildcard_phy_ap0"] is True
    assert checks["uses_wds_wildcard_phy_ap0_sta"] is True
    assert checks["has_runtime_listener_rebind_on_phy_change"] is True
    assert checks["has_beacon_int_30_enforcer"] is True
    assert checks["has_65s_ie_free_window"] is True
    assert checks["has_45s_ie_open_window"] is True
    assert checks["ie_c2_len_120_hex_60_bytes"] is True
    assert checks["ie_c3_len_120_hex_60_bytes"] is True

    phys = [p["resolved_ubus_obj"] for p in adm["simulated_dynamic_phy_transitions"]]
    assert phys == [
        "hostapd.phy0-ap0",
        "hostapd.phy1-ap0",
        "hostapd.phy2-ap0",
        "hostapd.phy3-ap0",
    ]


def test_stage116a_uci_hotplug_and_mac80211_teb_ko() -> None:
    receipt = json.loads(RECEIPT_JSON.read_text(encoding="utf-8"))
    uci = receipt["uci_and_hotplug_verification"]
    for script_name in (
        "99-fmx-pbe5ac-ptp-ap",
        "99-fmx-pbe5ac-ptp-ap-241",
        "99-fmx-pbe5ac-ptp-sta",
        "99-fmx-pbe5ac-ptp-sta-242",
    ):
        assert uci[script_name]["all_checks_passed"] is True

    teb = receipt["mac80211_teb_patch_verification"]
    assert teb["matches_expected_teb_sha256"] is True
    assert teb["module_layout_size_bytes"] == 352
    assert teb["skb_data_offset_hex"] == "0xa8"
