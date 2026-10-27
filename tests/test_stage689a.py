"""Pytest for Stage 689A (Cross-Fleet Champion v55.0 Bundle)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage689a_receipt_and_doc() -> None:
    p_json = ROOT / "artifacts/autoresearch/stage689a_cross_fleet_champion_v55_bundle.json"
    p_doc = ROOT / "docs/STAGE689A_CROSS_FLEET_CHAMPION_V55_BUNDLE.md"
    assert p_json.exists()
    assert p_doc.exists()
    data = json.loads(p_json.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-689A"
    assert data["status"] == "CONFIRMED"
    assert data["champion_version"] == "v55.0"
    assert data["guarida_v6_aggregate_capacity_mbps"] == 457.90
    assert data["window_totals"]["total_cross_lane_windows"] == 728
    assert data["five_pillar_compliant"] is True
    doc_text = p_doc.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 200
    assert doc_text.count("<!-- doc-head:") == 1
