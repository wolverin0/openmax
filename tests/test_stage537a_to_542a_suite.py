from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage537a_to_542a_suite() -> None:
    verif_path = REPO_ROOT / "artifacts" / "verification" / "stage542a_ltu_v12_and_universal_squashfs_v12_gate_receipt.json"
    assert verif_path.exists()
    data = json.loads(verif_path.read_text(encoding="utf-8"))
    assert data["stage"] == "542A"
    assert data["status"] == "CONFIRMED"
    assert data["verified_stages"] == ["537A", "538A", "539A", "540A", "541A", "542A"]
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
    assert data["highlights"]["stage537a_cumulative_live_windows"] == 168
    assert data["highlights"]["stage541a_v12_hsqs_images"] == 180
    assert not any(data["safety_audit"].values())
