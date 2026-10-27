"""Pytest suite for Stage 718A Zero-FP Observability Engine v7 (PCIe CE0..CE7 Auditor)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage718a_ce_auditor_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage718a_zero_fp_observability_engine_v7_pcie_ce_auditor.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "718A"
    assert data["status"] == "CONFIRMED"
    assert len(data["ce_ring_topology"]) == 8
    assert data["pktlog_audit"]["pktlog_filter_required"] == "0x0"
    assert data["pktlog_audit"]["ce4_tx_ring_entries"] == 2048


def test_stage718a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE718A_ZERO_FP_OBSERVABILITY_ENGINE_V7_PCIE_CE_AUDITOR.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
