"""Pytest for Stage 723A (Cross-Fleet Champion v56.0 Bundle)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage723a_receipt_and_doc() -> None:
    p_json = ROOT / "artifacts/autoresearch/stage723a_cross_fleet_champion_v56_bundle.json"
    p_doc = ROOT / "docs/STAGE723A_CROSS_FLEET_CHAMPION_V56_BUNDLE.md"
    assert p_json.exists()
    assert p_doc.exists()
    data = json.loads(p_json.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-723A"
    assert data["status"] == "CONFIRMED"
    assert data["champion_version"] == "v56.0"
    assert data["ptp_champion_v4_vht40_mbps"] == 25.47
    assert data["window_totals"]["total_cross_lane_windows"] == 796
    assert data["five_pillar_compliant"] is True
    doc_text = p_doc.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 200
    assert doc_text.count("<!-- doc-head:") == 1
