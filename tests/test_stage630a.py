"""Stage 630A verification suite (R67..R70 = 284 cumulative live windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage630a_receipt_and_284window_milestone() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage630a_live_wa_70round_284window_milestone_r67_70.json"
    assert p.exists(), "Missing stage630a receipt"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 630A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["cumulative_wa_total_windows_including_e2e"] == 284
    assert data["milestone_70_rounds_284_windows_achieved"] is True
    assert len(data["rounds"]) == 4
    res = audit_stage_receipt_5pillars(data)
    assert res["compliant"] is True, f"5-pillar failure: {res['failures']}"
