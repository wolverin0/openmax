"""Pytest suite for Stage 594A Guarida SOSA_Joaquin & 34-Endpoint EVM Alerter."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage594a_alerter_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage594a_guarida_sosa_joaquin_and_34endpoint_evm_alerter.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "594A"
    assert data["status"] == "CONFIRMED"
    g = data["stage456a_grounding"]
    assert g["total_guarida_endpoints"] == 34
    assert g["sosa_joaquin_rssi_diff_db"] == 1.0
    assert g["sosa_joaquin_evm_gap_db"] == 16.13
    assert g["evm_alerter_false_negative_rate_pct"] == 0.0


def test_stage594a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE594A_GUARIDA_SOSA_JOAQUIN_AND_34ENDPOINT_EVM_ALERTER.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
