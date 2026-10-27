from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage669a_to_674a_suite() -> None:
    auto_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage674a_ltu_228window_v17_and_squashfs_v17_gate_receipt.json"
    verif_path = REPO_ROOT / "artifacts" / "verification" / "stage674a_ltu_228window_v17_and_squashfs_v17_gate_receipt.json"
    assert auto_path.exists()
    assert verif_path.exists()
    data = json.loads(auto_path.read_text(encoding="utf-8"))
    assert data["stage"] == "674A"
    assert data["status"] == "CONFIRMED"
    assert data["verified_stages"] == ["669A", "670A", "671A", "672A", "673A", "674A"]
    for stg, a_chk in data["artifact_checks"].items():
        assert a_chk["exists"], f"Missing artifact for {stg}"
        assert a_chk["status"] == "CONFIRMED"
        assert a_chk["has_five_pillar_compliance"] is True
        assert a_chk["zero_safety_violations"] is True
    for stg, d_chk in data["doc_checks"].items():
        assert d_chk["exists"], f"Missing doc for {stg}"
        assert d_chk["under_200_lines"] is True
        assert d_chk["has_doc_head_open"] is True
        assert d_chk["has_doc_head_close"] is True
    assert data["highlights"]["stage669a_cumulative_live_windows"] == 228
    assert data["highlights"]["stage673a_v17_hsqs_images"] == 180
    assert not any(data["safety_audit"].values())
