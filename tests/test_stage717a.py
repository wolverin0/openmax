"""Pytest suite for Stage 717A Guarida Tower v7 Synchronized 10ms 67/33 Pareto."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage717a_pareto_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage717a_guarida_tower_v7_synchronized_67_33_pareto.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "717A"
    assert data["status"] == "CONFIRMED"
    assert data["selected_champion"] == "GUARIDA_V7_SYNC_10MS_67_33_AND_EVM_ALIGNED_CHAMPION"
    assert data["tower_aggregate_gain_pct"] == 48.16


def test_stage717a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE717A_GUARIDA_TOWER_V7_SYNCHRONIZED_67_33_PARETO.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
