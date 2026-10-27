from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage501a_to_506a_suite() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage506a_500stage_ground_up_milestone_gate_receipt.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "506A"
    assert data["status"] == "CONFIRMED"
    assert data["verified_stages"] == ["501A", "502A", "503A", "504A", "505A", "506A"]
    for stg, a_chk in data["artifact_checks"].items():
        assert a_chk["exists"], f"Missing artifact for {stg}"
        assert a_chk["status"] == "CONFIRMED"
        assert a_chk["has_five_pillar_compliance"] is True
        assert a_chk["zero_safety_violations"] is True
    for stg, d_chk in data["doc_checks"].items():
        assert d_chk["exists"], f"Missing doc for {stg}"
        assert d_chk["under_220_lines"] is True
        assert d_chk["has_doc_head_open"] is True
        assert d_chk["has_doc_head_close"] is True
    assert data["highlights"]["stage501a_cumulative_live_windows"] == 156
    assert data["highlights"]["stage505a_v11_hsqs_images"] >= 20
    assert not any(data["safety_audit"].values())
