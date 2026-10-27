"""Stage 567A verification suite (S567A-E2E-R6 MK1-251 4-Class DiffServ E2E v10 stress)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage567a_receipt_and_4class_diffserv_e2e_v10() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage567a_live_wa_mk1_251_e2e_v10_milestone.json"
    assert p.exists(), "Missing stage567a receipt"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 567A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["e2e_round"]["round_id"] == "S567A-E2E-R6"
    assert len(data["e2e_round"]["windows"]) == 4
    res = audit_stage_receipt_5pillars(data)
    assert res["compliant"] is True, f"5-pillar failure: {res['failures']}"
