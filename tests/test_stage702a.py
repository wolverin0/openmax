"""Pytest suite for Stage 702A Guarida Panel2 & Panel3 67/33 & EVM Playbook."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage702a_playbook_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage702a_guarida_panel2_panel3_67_33_and_evm_playbook.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "702A"
    assert data["status"] == "CONFIRMED"
    p2 = data["sectors"]["Panel2_Guarida_82"]
    p3 = data["sectors"]["Panel3_Guarida_83"]
    assert p2["dl_airtime_gain_pct"] == 34.84
    assert p2["priority_cpe_alignment"]["evm_gap_db"] == 11.61
    assert p3["priority_cpe_alignment"]["evm_gap_db"] == 16.26


def test_stage702a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE702A_GUARIDA_PANEL2_PANEL3_67_33_AND_EVM_PLAYBOOK.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
