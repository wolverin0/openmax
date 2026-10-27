#!/usr/bin/env python3
"""
Unified Pytest Suite for the 3-Stage Megamission (`Stage 164A -> Stage 165A -> Stage 166A`):
  - Stage 164A: WA SquashFS v5 Re-Bake with R1..R15 Champion (`vm.min_free_kbytes=4096`, `aql_threshold=4000`)
  - Stage 165A: Universal XC (`QCA9558` + `QCA9880` `128 MB` RAM) OpenWrt 24.10.4 Champion Kit
  - Stage 166A: Universal XW (`AR9342` `64 MB` M5) & XM (`AR7241` `32 MB` M5) OpenWrt `ath9k` Champion Kit
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.firmware.bake_stage164a_to_166a_universal_kits import (
    STAGE164A_RECEIPT_JSON,
    STAGE165A_RECEIPT_JSON,
    STAGE166A_RECEIPT_JSON,
    XC_6BOARD_MANIFEST,
    XC_KIT_DIR,
    XW_XM_BOARD_MANIFEST,
    XW_XM_KIT_DIR,
    verify_r1_r15_wa_champion_knobs,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
KIT_DIR = REPO_ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit"
UNIV_DIR = REPO_ROOT / "firmware" / "openwrt" / "wa_universal_kit_v34"
DOC_164A = REPO_ROOT / "docs" / "STAGE164A_WA_SQUASHFS_V5_R15_CHAMPION_BAKE.md"
DOC_165A = REPO_ROOT / "docs" / "STAGE165A_XC_FAMILY_UNIVERSAL_KIT.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_stage164a_wa_squashfs_v5_r15_champion_bake() -> None:
    assert STAGE164A_RECEIPT_JSON.exists(), f"Missing {STAGE164A_RECEIPT_JSON}"
    r = json.loads(STAGE164A_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert r["stage"] == "164A"
    assert r["status"] == "CONFIRMED"
    assert r["live_radios_241_242_20_250_touched"] is False

    audit = audit_stage_receipt_5pillars(r)
    assert audit["compliant"] is True, f"Stage 164A 5-pillar failed: {audit}"
    assert r["pillar_e_memory_master_claim_id"] == "mm-ae2a"

    champ_txt = (KIT_DIR / "99-fmx-wa-universal-champion").read_text(encoding="utf-8")
    checks = verify_r1_r15_wa_champion_knobs(champ_txt)
    assert all(checks.values())

    for ptp_fn in (
        "99-fmx-pbe5ac-ptp",
        "99-fmx-pbe5ac-ptp-ap",
        "99-fmx-pbe5ac-ptp-ap-241",
        "99-fmx-pbe5ac-ptp-sta",
        "99-fmx-pbe5ac-ptp-sta-242",
    ):
        ptp_txt = (KIT_DIR / ptp_fn).read_text(encoding="utf-8")
        assert "\r\n" not in ptp_txt
        assert "vm.min_free_kbytes=4096" in ptp_txt
        assert 'echo 4000 > "$phy_dir/aql_threshold"' in ptp_txt

    for slug in ("powerbeam-5ac-gen2", "litebeam-5ac-gen2", "lap-120", "nanostation-ac-loco"):
        b = r["wa_universal_boards"][slug]
        assert b["factory_ap"]["open_header_crc_valid"] is True
        assert b["factory_ap"]["part_rootfs_crc_valid"] is True
        assert b["sysupgrade_ap"]["fwtool_signature_crc_valid"] is True
        assert _sha256(UNIV_DIR / f"openwrt-24.10.4-{slug}-factory-ap.bin") == b["factory_ap"]["sha256"]

    assert DOC_164A.exists()
    doc_lines = DOC_164A.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert doc_lines[0].startswith("<!-- doc-head:")


def test_stage165a_xc_128mb_universal_kit() -> None:
    assert STAGE165A_RECEIPT_JSON.exists(), f"Missing {STAGE165A_RECEIPT_JSON}"
    r = json.loads(STAGE165A_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert r["stage"] == "165A"
    assert r["status"] == "CONFIRMED"
    assert r["live_radios_241_242_20_250_touched"] is False

    audit = audit_stage_receipt_5pillars(r)
    assert audit["compliant"] is True, f"Stage 165A 5-pillar failed: {audit}"
    assert r["pillar_e_memory_master_claim_id"] == "mm-37fa"

    xc_sh = XC_KIT_DIR / "99-fmx-xc-universal-champion"
    assert xc_sh.exists()
    txt = xc_sh.read_text(encoding="utf-8")
    assert "\r\n" not in txt
    assert 'FMX_XC_MIN_FREE_KBYTES="${FMX_XC_MIN_FREE_KBYTES:-6144}"' in txt
    assert 'FMX_XC_FQ_MEM_LIMIT="${FMX_XC_FQ_MEM_LIMIT:-8388608}"' in txt
    assert 'FMX_XC_FQ_LIMIT="${FMX_XC_FQ_LIMIT:-2048}"' in txt
    assert 'FMX_XC_AP_FQ_QUANTUM="${FMX_XC_AP_FQ_QUANTUM:-3028}"' in txt
    assert 'FMX_XC_STA_FQ_QUANTUM="${FMX_XC_STA_FQ_QUANTUM:-1514}"' in txt
    assert 'FMX_XC_AQL_THRESHOLD="${FMX_XC_AQL_THRESHOLD:-4000}"' in txt
    assert 'FMX_XC_BQL_MIN="${FMX_XC_BQL_MIN:-6056}"' in txt

    manifest = json.loads((XC_KIT_DIR / "xc_board_manifest.json").read_text(encoding="utf-8"))
    assert set(manifest.keys()) == {"0xe7f9", "0xe7f8", "0xe7f5", "0xe3f5", "0xe4f5", "0xe6e5"}
    assert len(XC_6BOARD_MANIFEST) == 6

    assert DOC_165A.exists()
    doc_lines = DOC_165A.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert doc_lines[0].startswith("<!-- doc-head:")


def test_stage166a_xw_xm_ath9k_universal_kit() -> None:
    assert STAGE166A_RECEIPT_JSON.exists(), f"Missing {STAGE166A_RECEIPT_JSON}"
    r = json.loads(STAGE166A_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert r["stage"] == "166A"
    assert r["status"] == "CONFIRMED"
    assert r["live_radios_241_242_20_250_touched"] is False

    audit = audit_stage_receipt_5pillars(r)
    assert audit["compliant"] is True, f"Stage 166A 5-pillar failed: {audit}"
    assert r["pillar_e_memory_master_claim_id"] == "mm-1375"

    xw_xm_sh = XW_XM_KIT_DIR / "99-fmx-xw-xm-ath9k-champion"
    assert xw_xm_sh.exists()
    txt = xw_xm_sh.read_text(encoding="utf-8")
    assert "\r\n" not in txt
    assert 'FMX_MIN_FREE_KBYTES="${FMX_MIN_FREE_KBYTES:-2048}"' in txt
    assert 'FMX_MIN_FREE_KBYTES="${FMX_MIN_FREE_KBYTES:-3072}"' in txt
    assert 'FMX_FQ_MEM_LIMIT="${FMX_FQ_MEM_LIMIT:-1572864}"' in txt
    assert 'FMX_FQ_MEM_LIMIT="${FMX_FQ_MEM_LIMIT:-2621440}"' in txt
    assert 'FMX_ATH9K_ANI="${FMX_ATH9K_ANI:-1}"' in txt
    assert 'FMX_ATH9K_AIRTIME_FLAGS="${FMX_ATH9K_AIRTIME_FLAGS:-7}"' in txt

    manifest = json.loads((XW_XM_KIT_DIR / "xw_xm_board_manifest.json").read_text(encoding="utf-8"))
    assert set(manifest.keys()) == {"XW_64MB", "XM_32MB"}
    assert manifest["XW_64MB"]["ram_mb"] == 64
    assert manifest["XM_32MB"]["ram_mb"] == 32
    assert len(XW_XM_BOARD_MANIFEST) == 2
