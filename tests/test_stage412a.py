from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage412a_universal_wa_xc_xw_v9_squashfs_bake() -> None:
    receipt_path = REPO_ROOT / "artifacts/autoresearch/stage412a_universal_wa_xc_xw_v9_squashfs_bake.json"
    doc_path = REPO_ROOT / "docs/STAGE412A_UNIVERSAL_WA_XC_XW_V9_SQUASHFS_BAKE.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "412A"
    assert data["status"] == "CONFIRMED"
    assert data["total_verified_hsqs_images"] >= 20
    assert data["all_images_have_hsqs_superblock"] is True
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
