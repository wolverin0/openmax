from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage413a_tester_selector_v4() -> None:
    receipt_path = REPO_ROOT / "artifacts/autoresearch/stage413a_tester_selector_v4_receipt.json"
    doc_path = REPO_ROOT / "docs/STAGE413A_TESTER_SELECTOR_V4.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "413A"
    assert data["status"] == "CONFIRMED"
    assert data["selector_version"] == "v4"
    assert data["dry_run_default"] is True
    assert data["mandatory_mtd_backup_gate"]["backup_hash_verified_before_write"] is True
    bundles = data["supported_bundles_v4"]
    assert "WA_v9_SquashFS" in bundles
    assert "LTU_Safe_Kit_v8_120Window" in bundles
    assert bundles["LTU_Safe_Kit_v8_120Window"]["zero_dev_ame_touches"] is True
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
