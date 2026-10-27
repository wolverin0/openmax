"""Verification test for Stage 382A (R40..R42, 172 Cumulative Windows!)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
R_382A = ROOT / "artifacts" / "autoresearch" / "stage382a_live_wa_fwstats_rescue_v7_r40_42.json"


def test_stage382a_fwstats_rescue_v7_r40_to_r42_receipt() -> None:
    assert R_382A.exists(), f"Missing {R_382A}"
    data = json.loads(R_382A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["protocol"] == "A1 -> B1 -> A2 -> B2"
    assert data["cumulative_wa_rf_windows_r1_to_r42"] == 168
    assert data["cumulative_wa_total_windows_including_e2e"] == 172
    assert data["milestone_172_live_windows_achieved"] is True
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    rounds = data["rounds"]
    assert len(rounds) == 3
    assert [r["round_id"] for r in rounds] == ["S382A-R40", "S382A-R41", "S382A-R42"]
    for r in rounds:
        assert len(r["windows"]) == 4
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
