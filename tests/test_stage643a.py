"""Pytest suite for Stage 643A Guarida Full-Tower v5 Pareto."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage643a_pareto_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage643a_guarida_full_tower_v5_60_61_82_83_84_pareto.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "643A"
    assert data["status"] == "CONFIRMED"
    assert data["selected_champion"] == "GUARIDA_V5_FULL_TOWER_CHAMPION"
    assert data["tower_topology"]["total_endpoints"] == 34
    assert data["aggregate_gain_pct"] == 35.78


def test_stage643a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE643A_GUARIDA_FULL_TOWER_V5_60_61_82_83_84_PARETO.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
