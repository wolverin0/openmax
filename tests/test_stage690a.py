"""Pytest for Stage 690A (SimPy PtP PowerBeam 5AC Gen2 VHT20 vs VHT40 vs VHT80 Near-Field ISI)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage690a_receipt_and_doc() -> None:
    p_json = ROOT / "artifacts/autoresearch/stage690a_ptp_vht40_vs_vht80_near_field_isi_sim.json"
    p_doc = ROOT / "docs/STAGE690A_PTP_VHT40_VS_VHT80_NEAR_FIELD_ISI_SIM.md"
    assert p_json.exists()
    assert p_doc.exists()
    data = json.loads(p_json.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-690A"
    assert data["status"] == "CONFIRMED"
    assert data["champion_goodput_mbps"] == 24.83
    assert data["five_pillar_compliant"] is True
    doc_text = p_doc.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 200
    assert doc_text.count("<!-- doc-head:") == 1
