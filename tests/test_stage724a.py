"""Pytest for Stage 724A (SimPy PtMP Mixed OpenWrt 7935B vs airOS 8 3839B A-MSDU Airtime Sim)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage724a_receipt_and_doc() -> None:
    p_json = ROOT / "artifacts/autoresearch/stage724a_ptmp_mixed_openwrt_vs_airos8_amsdu_airtime_sim.json"
    p_doc = ROOT / "docs/STAGE724A_PTMP_MIXED_OPENWRT_VS_AIROS8_AMSDU_AIRTIME_SIM.md"
    assert p_json.exists()
    assert p_doc.exists()
    data = json.loads(p_json.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-724A"
    assert data["status"] == "CONFIRMED"
    assert data["payload_density_ratio_7935_vs_3839"] == 1.95
    assert data["goodput_100pct_mbps"] > data["goodput_0pct_mbps"]
    assert data["five_pillar_compliant"] is True
    doc_text = p_doc.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 200
    assert doc_text.count("<!-- doc-head:") == 1
