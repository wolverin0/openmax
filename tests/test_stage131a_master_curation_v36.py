#!/usr/bin/env python3
"""Unit tests for Stage 131A: MAC80211 v3 Authorized-Gated 4-Address AP_VLAN Trigger & Master Curation v36.0."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage131a_master_curation_v36 import (
    EXPECTED_DIRECT_SHA256,
    EXPECTED_V2_SHA256,
    EXPECTED_V3_SHA256,
    MASTER_DOCS,
    RECEIPT_OUT,
    verify_mac80211_v3_authorized_gated_patch,
    verify_stage131a,
)


def test_mac80211_v3_authorized_gated_patch_invariants() -> None:
    v3_info = verify_mac80211_v3_authorized_gated_patch()
    assert v3_info["claim_status"] == "CONFIRMED"
    assert v3_info["v2_preserve_event_sha256"] == EXPECTED_V2_SHA256
    assert v3_info["direct_0x3757c_sha256"] == EXPECTED_DIRECT_SHA256
    assert v3_info["v3_authorized_gated_sha256"] == EXPECTED_V3_SHA256
    assert v3_info["wlan_sta_authorized_bit"] == 3
    assert v3_info["wlan_sta_4addr_event_bit"] == 19
    words = v3_info["v3_site_words_0x03757c_to_0x0375b8"]
    assert words["0x037580"] == "0x30640008"  # andi $a0, $v1, 0x0008
    assert words["0x037584"] == "0x1080000b"  # beqz $a0, 0x0375b4
    assert words["0x0375ac"] == "0x0c000000"  # jal cfg80211_rx_unexpected_4addr_frame
    assert words["0x0375b4"] == "0x1000f91c"  # b 0x035a28
    assert words["0x0375b8"] == "0x24070004"  # addiu $a3, $zero, 4


def test_stage131a_master_curation_v36_and_5pillar_gate() -> None:
    receipt = verify_stage131a()
    assert RECEIPT_OUT.exists()
    loaded = json.loads(RECEIPT_OUT.read_text(encoding="utf-8"))
    assert loaded["stage_id"] == "Stage 131A"
    assert loaded["curation_version"] == "v36.0"
    assert loaded["hardware_safety"]["touched_241"] is False
    assert loaded["hardware_safety"]["touched_242"] is False
    assert loaded["hardware_safety"]["flash_writes"] == 0

    gate = audit_stage_receipt_5pillars(loaded)
    assert gate["compliant"] is True

    for key, path in MASTER_DOCS.items():
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        assert len(lines) < 215, f"{key} has {len(lines)} lines"
        assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
        assert receipt["master_curation_v36_docs"][key]["has_fmx_disc_41"] is True
