"""Stage 633A verification suite (Cumulative 70-Round 284-Window WA Champion v11)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage633a_receipt_and_70round_284window_ledger() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage633a_cumulative_70round_284window_wa_champion_v11.json"
    assert p.exists(), "Missing stage633a receipt"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 633A"
    assert data["status"] == "CONFIRMED"
    assert data["total_counterbalanced_rounds"] == 70
    assert data["total_live_wa_triple_play_windows"] == 280
    assert data["total_live_windows_including_stage162a_e2e"] == 284
    assert data["milestone_70_rounds_284_windows_achieved"] is True
    assert len(data["rounds_r1_to_r70_ledger"]) == 70
    res = audit_stage_receipt_5pillars(data)
    assert res["compliant"] is True, f"5-pillar failure: {res['failures']}"
