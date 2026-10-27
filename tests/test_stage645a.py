"""Pytest suite for Stage 645A 650-Stage Milestone Cross-Lane Scorecard."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage645a_scorecard_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage645a_650stage_milestone_cross_lane_scorecard.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "645A"
    assert data["status"] == "CONFIRMED"
    w = data["live_window_scorecard"]
    assert w["wa_champion_v10_windows"] >= 256
    assert w["ltu_champion_v15_windows"] >= 204
    assert w["multi_radio_cross_family_windows"] >= 204
    assert w["total_counterbalanced_live_windows"] == 700


def test_stage645a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE645A_650STAGE_MILESTONE_CROSS_LANE_SCORECARD.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
