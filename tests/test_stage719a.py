"""Pytest suite for Stage 719A 800+ Live-Window Cross-Lane Scorecard."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage719a_800window_scorecard():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage719a_800window_cross_lane_scorecard.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "719A"
    assert data["status"] == "CONFIRMED"
    w = data["live_window_breakdown"]
    assert w["wa_champion_v12_windows"] == 316
    assert w["ltu_champion_v18_windows"] == 240
    assert w["total_counterbalanced_live_windows"] >= 800


def test_stage719a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE719A_800WINDOW_CROSS_LANE_SCORECARD.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
