"""Pytest suite for Stage 663A Guarida Tower v6 (PB060-TXOP-CABQ-SCHED + 7935B A-MSDU) Pareto."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage663a_pareto_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage663a_guarida_tower_v6_pb060_and_amsdu_7935b_pareto.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "663A"
    assert data["status"] == "CONFIRMED"
    assert data["pb060_specification"]["patch_id"] == "PB060-TXOP-CABQ-SCHED"
    assert data["selected_champion"] == "GUARIDA_V6_PB060_TXOP_CABQ_AND_7935B_CHAMPION"
    assert data["tower_aggregate_gain_pct"] == 40.99


def test_stage663a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE663A_GUARIDA_TOWER_V6_PB060_AND_AMSDU_7935B_PARETO.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
