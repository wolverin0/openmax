from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.re.patch_stage78b_umac_and_ath_dev_bugs import run_stage78b_patcher

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = REPO_ROOT / "artifacts/autoresearch/stage78b_umac_and_ath_dev_binary_patch_20261026.json"
STAGE78B_DOC_PATH = REPO_ROOT / "docs/STAGE78B_UMAC_AND_ATH_DEV_BINARY_PATCHER_AND_REMEDIATION.md"
VENDOR_REPORT_PATH = REPO_ROOT / "docs/UBIQUITI_AIRMAX_AC_UPH_BUG_DISCLOSURE_REPORT.md"
REMEDIATION_SH_PATH = REPO_ROOT / "artifacts/curation/fmx_stage78b_umac_athdev_runtime_remediation.sh"


def test_stage78b_artifact_and_zero_relocation_overlaps() -> None:
    assert ARTIFACT_PATH.exists(), f"Missing {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "78B"
    assert data["task_id"] == "T-S78B-UMAC-KO-AND-ATH-DEV-KO-BINARY-PATCHER-AND-VENDOR-REPORT"
    assert data["claim_status"] == "CONFIRMED"
    assert data["relocation_audit_verdict"] == "PASS_ZERO_RELOCATION_OVERLAPS"

    patched_modules = data["patched_modules"]
    assert set(patched_modules.keys()) == {
        "wa_umac_ko",
        "xc_umac_ko",
        "wa_ath_dev_ko",
        "xc_ath_dev_ko",
    }

    assert patched_modules["wa_umac_ko"]["patches_applied_count"] == 5
    assert patched_modules["xc_umac_ko"]["patches_applied_count"] == 5
    assert patched_modules["wa_ath_dev_ko"]["patches_applied_count"] == 11
    assert patched_modules["xc_ath_dev_ko"]["patches_applied_count"] == 11

    for key, mod in patched_modules.items():
        assert mod["relocation_overlaps_count"] == 0, f"Relocation overlap in {key}"
        assert mod["relocation_audit_verdict"] == "PASS_ZERO_RELOCATION_OVERLAPS"
        out_file = REPO_ROOT / mod["patched_path"]
        assert out_file.exists(), f"Missing patched module {out_file}"
        raw = out_file.read_bytes()
        assert len(raw) == mod["size_bytes"]
        assert hashlib.sha256(raw).hexdigest() == mod["patched_sha256"]
        assert mod["patched_sha256"] != mod["source_sha256"]
        for p in mod["patches"]:
            assert p["relocation_overlap"] is False


def test_stage78b_idempotent_rerun_and_runtime_script() -> None:
    report = run_stage78b_patcher()
    assert report["relocation_audit_verdict"] == "PASS_ZERO_RELOCATION_OVERLAPS"
    assert REMEDIATION_SH_PATH.exists()
    sh_text = REMEDIATION_SH_PATH.read_text(encoding="utf-8")
    for token in (
        "set_multiq 3",
        "enable_tx_tcp_cksum",
        "ethtool -K",
        "aggr_swretry 4",
        "ACBKMinfree:48",
        "ACBEMinfree:32",
        "ACVIMinfree:16",
        "ACVOMinfree:1",
    ):
        assert token in sh_text, f"Missing {token} in remediation script"


def test_stage78b_docs_line_budget_and_doc_head() -> None:
    for doc_path in (STAGE78B_DOC_PATH, VENDOR_REPORT_PATH):
        assert doc_path.exists(), f"Missing {doc_path}"
        text = doc_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) < 220, f"{doc_path.name} exceeds 220 lines ({len(lines)})"
        assert text.count("<!-- doc-head:") == 1, f"{doc_path.name} must have exactly 1 <!-- doc-head -->"
    vendor_text = VENDOR_REPORT_PATH.read_text(encoding="utf-8")
    for bug_id in (
        "UMAC-BUG-01",
        "UMAC-BUG-02",
        "UMAC-BUG-03",
        "UMAC-BUG-04",
        "UMAC-BUG-05",
        "ATHDEV-BUG-01",
        "ATHDEV-BUG-02",
        "ATHDEV-BUG-03",
        "ATHDEV-BUG-04",
    ):
        assert bug_id in vendor_text, f"Missing {bug_id} in vendor disclosure report"
