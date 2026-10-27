from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage409a_to_414a_ground_up_v9_bundle_end_to_end() -> None:
    receipt_paths = [
        REPO_ROOT / "artifacts" / "autoresearch" / "stage409a_wmi_retry_and_hook_loader.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage410a_sub20mhz_nlos_profile.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage411a_edge_micro_worker_c_classifier.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage412a_universal_wa_xc_xw_v9_squashfs_bake.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage413a_tester_selector_v4_receipt.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage414a_ground_up_v9_bundle_receipt.json",
    ]
    for p in receipt_paths:
        assert p.exists(), f"Missing receipt {p}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert audit_stage_receipt_5pillars(data)["compliant"] is True

    doc_paths = [
        REPO_ROOT / "docs" / "STAGE409A_WMI_RETRY_AND_HOOK_LOADER.md",
        REPO_ROOT / "docs" / "STAGE410A_SUB20MHZ_NLOS_PROFILE.md",
        REPO_ROOT / "docs" / "STAGE411A_EDGE_MICRO_WORKER_C_CLASSIFIER.md",
        REPO_ROOT / "docs" / "STAGE412A_UNIVERSAL_WA_XC_XW_V9_SQUASHFS_BAKE.md",
        REPO_ROOT / "docs" / "STAGE413A_TESTER_SELECTOR_V4.md",
    ]
    for dp in doc_paths:
        assert dp.exists(), f"Missing doc {dp}"
        lines = dp.read_text(encoding="utf-8").splitlines()
        assert len(lines) < 220, f"{dp} exceeds 220 lines"
        assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1

    for sh in [
        REPO_ROOT / "firmware" / "openwrt" / "common" / "fmx_wmi_retry_and_hook_loader.sh",
        REPO_ROOT / "firmware" / "openwrt" / "common" / "fmx_sub20mhz_nlos_profile.sh",
        REPO_ROOT / "firmware" / "openwrt" / "common" / "99-fmx-wa-universal-champion-v9",
        REPO_ROOT / "controller" / "fmx_micro_worker.c",
    ]:
        assert sh.exists()
        assert "\r\n" not in sh.read_text(encoding="utf-8")
