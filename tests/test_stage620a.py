"""Pytest suite for Stage 620A Guarida Panel2 39us Slot Guard & Requeue Alerter."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage620a_alerter_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage620a_guarida_panel2_39us_slot_guard_and_requeue_alerter.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "620A"
    assert data["status"] == "CONFIRMED"
    g = data["stage533a_grounding"]
    assert g["panel2_slot_guard_us"] == 39.0
    assert g["panel2_guard_overhead_pct"] == 26.0
    assert g["cbp_dur_900us_overhead_pct"] == 4.33


def test_stage620a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE620A_GUARIDA_PANEL2_39US_SLOT_GUARD_AND_REQUEUE_ALERTER.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
