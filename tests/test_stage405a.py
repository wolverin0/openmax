"""Stage 405A verification tests — MK1-251 4-Class DiffServ E2E-R4."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage405a_receipt_and_5pillar() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage405a_live_wa_mk1_251_4class_diffserv_e2e_v8.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 405A"
    assert data["status"] == "CONFIRMED"
    assert data["e2e_round"]["round_id"] == "S405A-E2E-R4"
    assert len(data["e2e_round"]["windows"]) == 4
    assert "EF_0xb8_AC_VO_VoIP" in data["e2e_round"]["windows"][1]["diffserv_4class_mk1_251"]
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
