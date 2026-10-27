"""Pytest for Stage 721A (240-Window Multi-Radio Milestone Campaign)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage721a_receipt_and_doc() -> None:
    p_json = ROOT / "artifacts/autoresearch/stage721a_multi_radio_240w_milestone_campaign.json"
    p_doc = ROOT / "docs/STAGE721A_MULTI_RADIO_240W_MILESTONE_CAMPAIGN.md"
    assert p_json.exists()
    assert p_doc.exists()
    data = json.loads(p_json.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-721A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_multi_radio_windows"] == 240
    assert data["new_windows_in_stage721a"] == 12
    assert data["integrated_lanes"]["total_cross_lane_windows"] == 796
    assert data["integrated_lanes"]["ptp_champion_v4_vht40_goodput_mbps"] == 25.47
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_250"] is False
    assert data["five_pillar_compliant"] is True
    doc_text = p_doc.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 200
    assert doc_text.count("<!-- doc-head:") == 1
