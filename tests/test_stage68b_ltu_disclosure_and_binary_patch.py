"""
Pytest verification suite for Stage 68B — LTU Unified Binary Patcher (`Stage 64A` +
`Stage 63B` `.rodata` `nop` Patch), Live Hardware Verification, and Vendor-Safe
Coordinated Bug Disclosure Report (`docs/UBIQUITI_LTU_FIRMWARE_BUG_DISCLOSURE_REPORT.md`).
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.ltu.patch_ltu_ame_core_binary import run_all_ltu_patches

REPO_ROOT = Path(__file__).resolve().parents[1]
DISCLOSURE_DOC_PATH = REPO_ROOT / "docs" / "UBIQUITI_LTU_FIRMWARE_BUG_DISCLOSURE_REPORT.md"
RECEIPT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage68b_ltu_binary_patch_and_disclosure_20261026.json"
)


def test_stage68b_ubiquiti_disclosure_report_is_vendor_safe_and_complete() -> None:
    """Verify the Ubiquiti / HackerOne disclosure report is <220 lines, bilingual, and vendor-safe."""
    assert DISCLOSURE_DOC_PATH.is_file(), f"Missing {DISCLOSURE_DOC_PATH}"
    txt = DISCLOSURE_DOC_PATH.read_text(encoding="utf-8")
    lines = txt.splitlines()
    assert len(lines) < 220, f"Disclosure report has {len(lines)} lines (must be < 220)"
    assert txt.startswith("<!-- doc-head:")

    # Verify bilingual executive summary and HackerOne / DMCA 1201(f)/(j) framing
    for required in (
        "https://hackerone.com/ui",
        "17 U.S.C. § 1201(f)",
        "17 U.S.C. § 1201(j)",
        "English Summary",
        "Resumen Ejecutivo (Español)",
        "LTU-BUG-01",
        "LTU-BUG-02",
        "LTU-BUG-03",
        "LTU-BUG-04",
        "LTU-BUG-05",
        "LTU-BUG-06",
        "LTU-BUG-07",
        "ame_core_set_automcsUpDown",
        "mcsUpThrd_1024",
        "gBDHandleOnce",
        "f0280000.gmac0",
        "sched_ap_mcs_limit_level",
        "ul_hybrid_routine",
        "frame_len_store",
        "pb_boost_store",
        "ini_store",
    ):
        assert required in txt, f"Missing required disclosure token: {required}"

    # Ensure regulatory power table modifications are NOT included in the vendor report
    assert "table_ptpPwrRange" not in txt


def test_stage68b_unified_binary_patcher_includes_automcs_rodata_nop_fix(tmp_path: Path) -> None:
    """Verify tools/ltu/patch_ltu_ame_core_binary.py patches LTU-BUG-03 .rodata stores with 0 .rel.text overlaps."""
    summary = run_all_ltu_patches(tmp_path)
    assert summary["Status"] == "CONFIRMED"
    assert summary["zero_relocation_corruption_verified"] is True

    for key in ("afltu_2.4.2_ame_core", "aflturocket_2.4.2_ame_core"):
        mod_res = summary["modules_patched"][key]
        assert mod_res["elf_verify_patch"]["total_overlapped_relocations"] == 0
        rodata_fix = mod_res["automcsUpDown_rodata_oops_fix"]
        assert rodata_fix["symbol"] == "ame_core_set_automcsUpDown"
        assert rodata_fix["rel_text_overlapped"] is False
        assert len(rodata_fix["patches"]) == 2
        assert rodata_fix["patches"][0]["before_hex"] == "002083e5"
        assert rodata_fix["patches"][0]["after_hex"] == "0000a0e1"
        assert rodata_fix["patches"][1]["before_hex"] == "0020c3e5"
        assert rodata_fix["patches"][1]["after_hex"] == "0000a0e1"


def test_stage68b_live_hardware_verification_receipt() -> None:
    """Verify the Stage 68B live hardware verification receipt on LTU-Lite #1."""
    assert RECEIPT_PATH.is_file(), f"Missing {RECEIPT_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "68B"
    assert data["status"] == "CONFIRMED"

    checks = data["live_checks_passed"]
    assert checks["frame_len_store_preserves_duty_cycle_750"] is True
    assert checks["automcsUpDown_writes_all_11_data_fields_with_exit_0"] is True
    assert checks["sched_mcs_unlocks_4096l_12x"] is True
    assert checks["ap_ptmp_run_verified"] is True
    assert len(data["ubiquiti_disclosure_report"]["disclosed_bugs"]) == 7
