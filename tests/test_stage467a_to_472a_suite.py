from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage467a_to_472a_suite() -> None:
    s471_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage471a_master_ground_up_readiness_scorecard.json"
    s472_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage472a_v10_suite_gate_receipt.json"
    assert s471_path.exists()
    assert s472_path.exists()

    s471 = json.loads(s471_path.read_text(encoding="utf-8"))
    s472 = json.loads(s472_path.read_text(encoding="utf-8"))

    assert s471["stage"] == "471A"
    assert s471["status"] == "CONFIRMED"
    assert len(s471["pillars_scorecard"]) == 5
    assert s471["cumulative_bench_metrics"]["ltu_110_live_windows"] == 144
    assert s471["cumulative_bench_metrics"]["wa_xc_xw_v10_hsqs_images"] >= 20

    assert s472["stage"] == "472A"
    assert s472["status"] == "CONFIRMED"
    assert s472["verified_stages"] == ["467A", "468A", "469A", "470A", "471A", "472A"]
    for stg, a_chk in s472["artifact_checks"].items():
        assert a_chk["exists"], f"Missing artifact for {stg}"
        assert a_chk["status"] == "CONFIRMED"
        assert a_chk["has_five_pillar_compliance"] is True
        assert a_chk["zero_safety_violations"] is True
    for stg, d_chk in s472["doc_checks"].items():
        assert d_chk["exists"], f"Missing doc for {stg}"
        assert d_chk["under_220_lines"] is True
        assert d_chk["has_doc_head_open"] is True
        assert d_chk["has_doc_head_close"] is True
    assert not any(s472["safety_audit"].values())
