"""Stage 566A verification suite (R60..R63 = 256 cumulative live windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage566a_receipt_and_256window_milestone() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage566a_live_wa_256window_milestone_r60_63.json"
    assert p.exists(), "Missing stage566a receipt"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 566A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["cumulative_wa_total_windows_including_e2e"] == 256
    assert data["milestone_256_live_windows_achieved"] is True
    assert len(data["rounds"]) == 4
    res = audit_stage_receipt_5pillars(data)
    assert res["compliant"] is True, f"5-pillar failure: {res['failures']}"
