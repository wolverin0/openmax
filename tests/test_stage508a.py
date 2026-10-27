"""Stage 508A verification suite (R53..R56 = 228 cumulative live windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage508a_receipt_and_228window_milestone() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage508a_live_wa_cca_agc_and_ani_immunity_r53_56.json"
    assert p.exists(), "Missing stage508a receipt"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 508A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["cumulative_wa_total_windows_including_e2e"] == 228
    assert data["milestone_228_live_windows_achieved"] is True
    assert len(data["rounds"]) == 4
    res = audit_stage_receipt_5pillars(data)
    assert res["compliant"] is True, f"5-pillar failure: {res['failures']}"
