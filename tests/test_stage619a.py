"""Pytest suite for Stage 619A Guarida Panel1 7935B vs 3839B A-MSDU Mixed-Fleet Pareto."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage619a_pareto_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage619a_guarida_panel1_amsdu_7935_vs_3839_mixed_fleet_pareto.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "619A"
    assert data["status"] == "CONFIRMED"
    assert data["stage534a_grounding"]["goodput_gain_pct"] == 25.26
    assert data["selected_champion"] == "ADAPTIVE_SNR_GATED_AMSDU_CHAMPION"


def test_stage619a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE619A_GUARIDA_PANEL1_AMSDU_7935_VS_3839_MIXED_FLEET_PARETO.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
