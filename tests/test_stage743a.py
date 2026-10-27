"""Pytest suite for Stage 743A Guarida Tower v8 (activity_aging & aggr_limit_bytes) Pareto."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage743a_pareto_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage743a_guarida_tower_v8_activity_aging_and_dl_aggr_pareto.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "743A"
    assert data["status"] == "CONFIRMED"
    assert data["selected_champion"] == "GUARIDA_V8_ACTIVITY_AGING_AND_DL_AGGR_CHAMPION"
    assert data["tower_aggregate_gain_pct"] == 53.46
    assert data["stage681a_735a_grounding"]["activity_aging_champion_ms"] == 250


def test_stage743a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE743A_GUARIDA_TOWER_V8_ACTIVITY_AGING_AND_DL_AGGR_PARETO.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
