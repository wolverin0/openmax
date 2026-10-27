"""Pytest suite for Stage 617A QCA988x TxBF, SU-BF Sounding, STBC & LDPC Adaptive Helper."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage617a_helper_and_receipt():
    helper = ROOT / "firmware" / "openwrt" / "common" / "fmx_qca988x_txbf_stbc_ldpc_helper.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage617a_qca988x_txbf_stbc_ldpc_adaptive_helper.json"
    assert helper.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "617A"
    assert data["status"] == "CONFIRMED"
    assert "FAR_FIELD_LDPC_SUBF_OPTIMAL" in data["profiles"]
    assert data["safety"]["touched_protected_nodes"] is False


def test_stage617a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE617A_QCA988X_TXBF_STBC_LDPC_ADAPTIVE_HELPER.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
