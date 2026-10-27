#!/usr/bin/env python3
"""
Tests for Stage 136A — WA Universal Champion Asymmetric fq_quantum Integration
(AP=3028 2xMTU per FMX-DISC-34 / STA=1514 1xMTU) & mac80211_241_v3.ko Verification.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from firmware.openwrt.pbe5ac_gen2_ptp_kit.patch_mac80211_teb import (
    EXPECTED_TEB_4ADDR_V2_SHA256,
    EXPECTED_TEB_241_V3_SHA256,
    TEB_4ADDR_KO,
    TEB_4ADDR_V3_KO,
    TEB_241_V3_KO,
    apply_and_verify_teb_patch,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
KIT_DIR = REPO_ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit"
UNIVERSAL_SCRIPT = KIT_DIR / "99-fmx-wa-universal-champion"
AP_SCRIPT = KIT_DIR / "99-fmx-pbe5ac-ptp-ap"
AP_241_SCRIPT = KIT_DIR / "99-fmx-pbe5ac-ptp-ap-241"
STA_SCRIPT = KIT_DIR / "99-fmx-pbe5ac-ptp-sta"
STA_242_SCRIPT = KIT_DIR / "99-fmx-pbe5ac-ptp-sta-242"
STAGE136A_RECEIPT = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage136a_wa_asymmetric_quantum_and_v3_ko_receipt.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_stage136a_receipt_passes_5pillars() -> None:
    assert STAGE136A_RECEIPT.exists(), f"Missing {STAGE136A_RECEIPT}"
    receipt = json.loads(STAGE136A_RECEIPT.read_text(encoding="utf-8"))
    assert receipt["stage"] == "136A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["live_radios_241_242_touched"] is False

    audit = audit_stage_receipt_5pillars(receipt)
    assert audit["compliant"], f"5-Pillar gate failed: {audit}"
    assert str(receipt["pillar_e_memory_master_claim_id"]).startswith("mm-")


def test_stage136a_asymmetric_fq_quantum_in_wa_scripts() -> None:
    txt = UNIVERSAL_SCRIPT.read_text(encoding="utf-8")
    assert "\r\n" not in txt
    assert 'FMX_AP_FQ_QUANTUM="${FMX_AP_FQ_QUANTUM:-3028}"' in txt
    assert 'FMX_STA_FQ_QUANTUM="${FMX_STA_FQ_QUANTUM:-1514}"' in txt
    assert "/sys/class/net/phy*-ap0" in txt
    assert "/sys/class/net/phy*-sta0" in txt

    ap_txt = AP_SCRIPT.read_text(encoding="utf-8")
    assert "\r\n" not in ap_txt
    assert 'echo 3028 > "$phy_dir/aqm/fq_quantum"' in ap_txt

    ap_241_txt = AP_241_SCRIPT.read_text(encoding="utf-8")
    assert "\r\n" not in ap_241_txt
    assert 'echo 3028 > "$phy_dir/aqm/fq_quantum"' in ap_241_txt

    sta_txt = STA_SCRIPT.read_text(encoding="utf-8")
    assert "\r\n" not in sta_txt
    assert 'echo 1514 > "$phy_dir/aqm/fq_quantum"' in sta_txt

    sta_242_txt = STA_242_SCRIPT.read_text(encoding="utf-8")
    assert "\r\n" not in sta_242_txt
    assert 'echo 1514 > "$phy_dir/aqm/fq_quantum"' in sta_242_txt


def test_stage136a_mac80211_v2_and_241_v3_ko_hashes_and_dissection() -> None:
    res = apply_and_verify_teb_patch()
    assert res["matches_expected_teb_4addr_v2_sha256"] is True
    assert res["teb_4addr_preserve_event_sha256"] == EXPECTED_TEB_4ADDR_V2_SHA256
    assert (
        EXPECTED_TEB_4ADDR_V2_SHA256
        == "c65dc2e2a87274e3073debf4c507606422a5ea1b08cbfe2e40beed58263e81cc"
    )
    assert _sha256(TEB_4ADDR_KO) == EXPECTED_TEB_4ADDR_V2_SHA256

    assert res["matches_expected_teb_241_v3_sha256"] is True
    assert res["teb_241_v3_sha256"] == EXPECTED_TEB_241_V3_SHA256
    assert (
        EXPECTED_TEB_241_V3_SHA256
        == "e43115c06316ce2d1b643d1900deb41839f7e07aba50f1537e6ed7a17b45e2f5"
    )
    assert _sha256(TEB_241_V3_KO) == EXPECTED_TEB_241_V3_SHA256

    assert TEB_4ADDR_V3_KO.exists()
    assert (
        _sha256(TEB_4ADDR_V3_KO)
        == "fe4f730fccaa68848a70c952e40c0438b32d413993f22887a0e72fed5eebaae6"
    )

    assert res["rx_4addr_241_v3_patched_words_hex"] == {
        "0x037578": "0x24070004",
        "0x03757c": "0x8c430074",
        "0x037580": "0x30640008",
        "0x037584": "0x1080f928",
        "0x037588": "0x3c010008",
        "0x03758c": "0x00612024",
        "0x037590": "0x1480f925",
        "0x037594": "0x00611825",
        "0x037598": "0xac430074",
        "0x0375b4": "0x1000f91c",
        "0x0375b8": "0x24070004",
    }
