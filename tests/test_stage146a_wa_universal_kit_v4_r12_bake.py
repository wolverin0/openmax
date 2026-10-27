#!/usr/bin/env python3
"""
Tests for Stage 146A — WA Universal Kit v4 SquashFS (`hsqs`) Full Re-Bake with
R1..R12 Universal WA Champion (`99-fmx-wa-universal-champion`: `tcp_limit_output_bytes=65536`,
`netdev_max_backlog=1500`, `AC_BK=500/1000`, `coverage_class=0`, `AP fq_quantum=3028` / `STA fq_quantum=1514`,
`fq_limit=1024`, `fq_mem=3MB`, `aql_threshold=4500`, `dev_weight=48`, `netdev_budget=480`, `BQL=4542/36288/600`)
and `mac80211_teb_4addr_v3_6.6.110.ko` (`fe4f730f...`) across all 16 Universal WA images and 4 PBE-5AC-Gen2 Kit images.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.firmware.bake_stage141a_wa_full_squashfs_v3 import (
    EXPECTED_ADMITTER_V2_SHA256,
    EXPECTED_MAC80211_V3_SHA256,
)
from tools.firmware.bake_stage146a_wa_full_squashfs_v4 import (
    STAGE146A_RECEIPT_JSON,
    UNIVERSAL_V4_OVERLAY_TAR,
    verify_r1_r12_wa_champion_knobs,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
KIT_DIR = REPO_ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit"
UNIV_DIR = REPO_ROOT / "firmware" / "openwrt" / "wa_universal_kit_v34"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_stage146a_receipt_passes_5pillars_and_safety() -> None:
    assert STAGE146A_RECEIPT_JSON.exists(), f"Missing {STAGE146A_RECEIPT_JSON}"
    receipt = json.loads(STAGE146A_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert receipt["stage"] == "146A"
    assert receipt["stage_id"] == "Stage 146A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["live_radios_241_242_touched"] is False
    assert receipt["hardware_safety"]["touched_241"] is False
    assert receipt["hardware_safety"]["touched_242"] is False
    assert receipt["hardware_safety"]["flash_writes"] == 0
    assert receipt["total_universal_images_baked"] == 16
    assert receipt["total_pbe5ac_kit_images_baked"] == 4

    audit = audit_stage_receipt_5pillars(receipt)
    assert audit["compliant"] is True, f"5-Pillar gate failed: {audit}"
    assert receipt["pillar_e_memory_master_claim_id"] == "mm-94db"


def test_stage146a_baked_squashfs_v4_embedded_sha256s_and_r1_r12_knobs() -> None:
    receipt = json.loads(STAGE146A_RECEIPT_JSON.read_text(encoding="utf-8"))
    expected = receipt["expected_embedded_sha256s"]

    assert expected["lib/modules/6.6.110/mac80211.ko"] == EXPECTED_MAC80211_V3_SHA256
    assert expected["lib/modules/6.6.110/mac80211.ko"] == _sha256(
        KIT_DIR / "mac80211_teb_4addr_v3_6.6.110.ko"
    )
    assert expected["usr/sbin/fmx_pbe5ac_admitter.sh"] == EXPECTED_ADMITTER_V2_SHA256
    assert expected["usr/sbin/fmx_pbe5ac_admitter.sh"] == _sha256(
        KIT_DIR / "fmx_pbe5ac_admitter.sh"
    )
    champ_sha = expected["etc/hotplug.d/net/99-fmx-wa-universal-champion"]
    assert len(champ_sha) == 64

    champ_txt = (KIT_DIR / "99-fmx-wa-universal-champion").read_text(encoding="utf-8")
    knob_checks = verify_r1_r12_wa_champion_knobs(champ_txt)
    assert all(knob_checks.values())

    assert UNIVERSAL_V4_OVERLAY_TAR.exists()

    for role in ("ap_241", "sta_242"):
        sq = receipt["rebaked_squashfs"][role]
        v_shas = sq["verified_extracted_sha256s"]
        assert v_shas["lib/modules/6.6.110/mac80211.ko"] == EXPECTED_MAC80211_V3_SHA256
        assert v_shas["usr/sbin/fmx_pbe5ac_admitter.sh"] == EXPECTED_ADMITTER_V2_SHA256
        assert v_shas["etc/hotplug.d/net/99-fmx-wa-universal-champion"] == champ_sha


def test_stage146a_all_16_universal_and_4_pbe5ac_images_on_disk_and_crc_valid() -> None:
    receipt = json.loads(STAGE146A_RECEIPT_JSON.read_text(encoding="utf-8"))
    kit_imgs = receipt["pbe5ac_gen2_kit_images"]

    for key, fname in (
        ("factory_ap_241", "openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-factory-ap-241.bin"),
        ("factory_sta_242", "openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-factory-sta-242.bin"),
        ("sysupgrade_ap_241", "openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-sysupgrade-ap-241.bin"),
        ("sysupgrade_sta_242", "openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-sysupgrade-sta-242.bin"),
    ):
        p = KIT_DIR / fname
        assert p.exists(), f"Missing {p}"
        assert _sha256(p) == kit_imgs[key]["sha256"]

    for slug in ("powerbeam-5ac-gen2", "litebeam-5ac-gen2", "lap-120", "nanostation-ac-loco"):
        b = receipt["wa_universal_boards"][slug]
        for f_role in ("factory_ap", "factory_sta"):
            assert b[f_role]["open_header_crc_valid"] is True
            assert b[f_role]["part_kernel_crc_valid"] is True
            assert b[f_role]["part_rootfs_crc_valid"] is True
        for s_role in ("sysupgrade_ap", "sysupgrade_sta"):
            assert b[s_role]["fwtool_metadata_crc_valid"] is True
            assert b[s_role]["fwtool_signature_crc_valid"] is True

        assert _sha256(UNIV_DIR / f"openwrt-24.10.4-{slug}-factory-ap.bin") == b["factory_ap"]["sha256"]
        assert _sha256(UNIV_DIR / f"openwrt-24.10.4-{slug}-factory-sta.bin") == b["factory_sta"]["sha256"]
        assert _sha256(UNIV_DIR / f"openwrt-24.10.4-{slug}-sysupgrade-ap.bin") == b["sysupgrade_ap"]["sha256"]
        assert _sha256(UNIV_DIR / f"openwrt-24.10.4-{slug}-sysupgrade-sta.bin") == b["sysupgrade_sta"]["sha256"]
