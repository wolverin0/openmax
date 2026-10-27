"""Verification test for Stage 383A (MK1-251 E2E-R3 Bidirectional Stress)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
R_383A = ROOT / "artifacts" / "autoresearch" / "stage383a_live_wa_mk1_251_bidir_e2e_v7.json"


def test_stage383a_mk1_251_bidir_e2e_v7_receipt() -> None:
    assert R_383A.exists(), f"Missing {R_383A}"
    data = json.loads(R_383A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    e2e = data["e2e_round"]
    assert e2e["round_id"] == "S383A-E2E-R3"
    assert len(e2e["windows"]) == 4
    for w in e2e["windows"]:
        assert "boca7_mk1_251_e2e_rtt" in w
        assert w["boca7_mk1_251_e2e_rtt"]["p50_ms"] > 0.0
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
