"""Pytest suite for Stage 775A Guarida Tower v9 (ff_cbp_slots=4 & L2 Shield) Pareto."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage775a_pareto_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage775a_guarida_tower_v9_cbp_slots_and_l2_shield_pareto.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "775A"
    assert data["status"] == "CONFIRMED"
    m = data["v9_mechanisms"]
    assert m["ff_cbp_slots"] == 4
    assert m["cbp_window_us"] == 240
    assert m["activity_aging_ms"] == 1500
    assert m["panel2_empty_poll_waste_reduction_pct"] == 54.17
    assert data["selected_champion"] == "GUARIDA_V9_FF_CBP_SLOTS4_AND_L2_SHIELD_CHAMPION"


def test_stage775a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE775A_GUARIDA_TOWER_V9_CBP_SLOTS_AND_L2_SHIELD_PARETO.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
