"""Pytest verification for Stage 779A (264-Window Multi-Radio Milestone Campaign)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "artifacts" / "autoresearch" / "stage779a_multi_radio_264w_milestone_campaign.json"
DOC = ROOT / "docs" / "STAGE779A_MULTI_RADIO_264W_MILESTONE_CAMPAIGN.md"


def test_stage779a_receipt_and_doc() -> None:
    assert RECEIPT.exists(), f"Missing {RECEIPT}"
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-779A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_isolation"]["touched_241"] is False
    assert data["safety_isolation"]["touched_242"] is False
    assert data["safety_isolation"]["touched_250"] is False
    ms = data["milestone_summary"]
    assert ms["cumulative_multi_radio_windows"] == 264
    assert ms["new_windows_executed"] == 12
    assert ms["cross_lane_window_totals"]["wa_openwrt_lane_windows"] == 344
    assert ms["cross_lane_window_totals"]["wa_vht20_peak_goodput_mbps"] == 78.51
    assert ms["cross_lane_window_totals"]["ltu_lane_windows"] == 264
    assert ms["cross_lane_window_totals"]["total_counterbalanced_windows_all_lanes"] == 872
    assert ms["arm_b_mean_goodput_mbps"] > ms["arm_a_mean_goodput_mbps"]
    assert ms["arm_b_mean_rtt_p95_ms"] < ms["arm_a_mean_rtt_p95_ms"]

    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
