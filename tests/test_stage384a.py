"""Verification test for Stage 384A (Panel1-Guarida .84 v7 Rollout & Cooperative 3-CPE rc_stats/fw_stats)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
R_384A = ROOT / "artifacts" / "autoresearch" / "stage384a_live_panel1_guarida_v7_and_rcstats.json"


def test_stage384a_panel1_guarida_v7_and_rcstats_receipt() -> None:
    assert R_384A.exists(), f"Missing {R_384A}"
    data = json.loads(R_384A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["hostapd_restarted"] is False
    assert data["safety_boundaries"]["zero_rf_disconnect_verified"] is True
    assert data["safety_boundaries"]["active_cpes_count"] == 3
    v7_k = data["v7_verified_knobs"]
    assert v7_k["net.ipv4.tcp_autocorking"] == 0
    assert v7_k["net.core.gro_normal_batch"] == 16
    assert v7_k["net.ipv4.tcp_early_retrans"] == 4
    assert len(data["cooperative_3cpe_rc_stats_and_aqm"]) > 50
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
