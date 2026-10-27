"""Pytest for Stage 658A (SimPy Guarida 32-CPE Triple-Play under PB-040 + PB-050 + PB-060)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage658a_receipt_and_doc() -> None:
    p_json = ROOT / "artifacts/autoresearch/stage658a_guarida_32cpe_pb060_voip_iptv_bulk_sim.json"
    p_doc = ROOT / "docs/STAGE658A_GUARIDA_32CPE_PB060_VOIP_IPTV_BULK_SIM.md"
    assert p_json.exists()
    assert p_doc.exists()
    data = json.loads(p_json.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-658A"
    assert data["status"] == "CONFIRMED"
    assert data["guarida_topology"]["total_panels"] == 3
    assert data["guarida_topology"]["total_cpes"] == 32
    assert data["triple_stack_summary"]["max_iptv_loss_pct"] == 0.0
    assert data["five_pillar_compliant"] is True
    doc_text = p_doc.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 200
    assert doc_text.count("<!-- doc-head:") == 1
