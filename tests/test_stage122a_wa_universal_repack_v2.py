#!/usr/bin/env python3
"""
Tests for Stage 122A — mac80211.ko 4-Address EAPOL RX_DROP_MONITOR Bypass &
Universal WA Repack v2 (PowerBeam 5AC Gen2 0xe3d6 + LiteBeam 5AC Gen2 0xe7f9).
"""

from __future__ import annotations

import json
import tarfile
from pathlib import Path

from firmware.openwrt.pbe5ac_gen2_ptp_kit.patch_mac80211_teb import (
    TEB_4ADDR_DIRECT_KO,
    TEB_4ADDR_KO,
    apply_and_verify_teb_patch,
)
from tools.firmware.build_wa_family_universal_kit import (
    UNIVERSAL_V2_OVERLAY_TAR,
    build_and_verify_wa_family_universal_kit,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE122A_RECEIPT = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage122a_wa_universal_repack_v2_receipt.json"
)


def test_stage122a_receipt_passes_5pillars() -> None:
    assert STAGE122A_RECEIPT.exists(), f"Missing {STAGE122A_RECEIPT}"
    receipt = json.loads(STAGE122A_RECEIPT.read_text(encoding="utf-8"))
    assert receipt["stage"] == "122A"
    assert receipt["live_hardware_contact_241_242"] is False

    audit = audit_stage_receipt_5pillars(receipt)
    assert audit["compliant"], f"5-Pillar gate failed: {audit}"
    assert str(receipt["pillar_e_memory_master_claim_id"]).startswith("mm-")


def test_stage122a_mac80211_4addr_eapol_bypass_variants() -> None:
    res = apply_and_verify_teb_patch()
    assert res["matches_expected_teb_sha256"] is True
    assert TEB_4ADDR_KO.exists()
    assert TEB_4ADDR_DIRECT_KO.exists()

    assert res["rx_4addr_preserve_event_patched_words_hex"] == {
        "0x037598": "0x14400006",
        "0x0375b4": "0x1000f91c",
        "0x0375b8": "0x24070004",
    }
    assert res["rx_4addr_direct_0x3757c_patched_words_hex"] == {
        "0x03757c": "0x1000f92a",
        "0x037580": "0x24070004",
    }


def test_stage122a_universal_wa_kit_and_overlay_v2() -> None:
    receipt = build_and_verify_wa_family_universal_kit(write_images=False)
    ka = receipt["kernel_and_admitter_verification"]
    assert ka["admitter_v2"]["has_dynamic_phy_ap0_resolution"] is True
    assert ka["admitter_v2"]["has_beacon_int_30"] is True
    assert ka["admitter_v2"]["has_65s_ie_free_window"] is True
    assert ka["universal_wa_champion"]["supports_pbe5ac_gen2_and_lbe5ac_gen2"] is True
    assert ka["universal_wa_champion"]["supports_openwrt_and_airos8_rc_poststart"] is True

    assert UNIVERSAL_V2_OVERLAY_TAR.exists()
    with tarfile.open(UNIVERSAL_V2_OVERLAY_TAR, "r:gz") as tf:
        names = tf.getnames()
    assert names == [
        "etc/hotplug.d/net/99-fmx-wa-universal-champion",
        "usr/sbin/fmx_pbe5ac_admitter.sh",
        "lib/modules/6.6.110/mac80211.ko",
        "usr/sbin/fmx_ptp_rollback_watchdog.sh",
    ]
    assert "powerbeam-5ac-gen2" in receipt["boards"]
    assert "litebeam-5ac-gen2" in receipt["boards"]
