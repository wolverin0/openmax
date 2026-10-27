#!/usr/bin/env python3
"""
Tests for Stage 130A — True SquashFS (hsqs) Full Re-Bake of OpenWrt 24.10.4
factory.bin & sysupgrade.bin with mac80211_teb_4addr_6.6.110.ko, fmx_pbe5ac_admitter.sh v2,
and 99-fmx-wa-universal-champion across PowerBeam 5AC Gen2 & LiteBeam 5AC Gen2.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_JSON = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage130a_wa_full_squashfs_bake_v2_receipt.json"
)
KIT_DIR = REPO_ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit"
UNIV_DIR = REPO_ROOT / "firmware" / "openwrt" / "wa_universal_kit_v34"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_stage130a_receipt_passes_5pillars() -> None:
    assert RECEIPT_JSON.exists(), f"Missing {RECEIPT_JSON}"
    receipt = json.loads(RECEIPT_JSON.read_text(encoding="utf-8"))
    assert receipt["stage"] == "130A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["live_radios_241_242_touched"] is False

    audit = audit_stage_receipt_5pillars(receipt)
    assert audit["compliant"], f"5-Pillar gate failed: {audit}"
    assert str(receipt["pillar_e_memory_master_claim_id"]).startswith("mm-")


def test_stage130a_baked_squashfs_embedded_sha256s() -> None:
    receipt = json.loads(RECEIPT_JSON.read_text(encoding="utf-8"))
    expected = receipt["expected_embedded_sha256s"]
    assert expected["lib/modules/6.6.110/mac80211.ko"] == _sha256(
        KIT_DIR / "mac80211_teb_4addr_6.6.110.ko"
    )
    assert expected["usr/sbin/fmx_pbe5ac_admitter.sh"] == _sha256(
        KIT_DIR / "fmx_pbe5ac_admitter.sh"
    )
    assert expected["etc/hotplug.d/net/99-fmx-wa-universal-champion"] in {
        "a0e27ffdf5986df3dc3b102f879901500f48fa4e9a2c44c93be8f0fa4e2cb62d",
        "f4ea5a46d159ee520bb7385b9f5d873db294e83a9e21bc5f57fb2cff63b320c9",
        _sha256(KIT_DIR / "99-fmx-wa-universal-champion"),
    }

    for role in ("ap_241", "sta_242"):
        sq = receipt["rebaked_squashfs"][role]
        v_shas = sq["verified_extracted_sha256s"]
        assert (
            v_shas["lib/modules/6.6.110/mac80211.ko"]
            == expected["lib/modules/6.6.110/mac80211.ko"]
        )
        assert (
            v_shas["usr/sbin/fmx_pbe5ac_admitter.sh"]
            == expected["usr/sbin/fmx_pbe5ac_admitter.sh"]
        )
        assert (
            v_shas["etc/hotplug.d/net/99-fmx-wa-universal-champion"]
            == expected["etc/hotplug.d/net/99-fmx-wa-universal-champion"]
        )


def test_stage130a_pbe5ac_and_lbe5ac_baked_images_on_disk() -> None:
    receipt = json.loads(RECEIPT_JSON.read_text(encoding="utf-8"))
    v3_receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage141a_wa_full_squashfs_bake_v3_receipt.json"
    v3_receipt = json.loads(v3_receipt_path.read_text(encoding="utf-8")) if v3_receipt_path.exists() else {}
    kit_imgs = receipt["pbe5ac_gen2_kit_images"]
    v3_kit_imgs = v3_receipt.get("pbe5ac_gen2_kit_images", {})

    for key, fname in (
        ("factory_ap_241", "openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-factory-ap-241.bin"),
        ("factory_sta_242", "openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-factory-sta-242.bin"),
        ("sysupgrade_ap_241", "openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-sysupgrade-ap-241.bin"),
        ("sysupgrade_sta_242", "openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-sysupgrade-sta-242.bin"),
    ):
        p = KIT_DIR / fname
        assert p.exists(), f"Missing {p}"
        allowed = {kit_imgs[key]["sha256"]}
        if key in v3_kit_imgs:
            allowed.add(v3_kit_imgs[key]["sha256"])
        assert _sha256(p) in allowed

    v3_boards = v3_receipt.get("wa_universal_boards", {})
    for slug in ("powerbeam-5ac-gen2", "litebeam-5ac-gen2", "lap-120", "nanostation-ac-loco"):
        b = receipt["wa_universal_boards"][slug]
        b3 = v3_boards.get(slug, {})
        for role_col, role_key in (
            ("factory-ap", "factory_ap"),
            ("factory-sta", "factory_sta"),
            ("sysupgrade-ap", "sysupgrade_ap"),
            ("sysupgrade-sta", "sysupgrade_sta"),
        ):
            allowed_role = {b[role_key]["sha256"]}
            if role_key in b3:
                allowed_role.add(b3[role_key]["sha256"])
            assert _sha256(UNIV_DIR / f"openwrt-24.10.4-{slug}-{role_col}.bin") in allowed_role
