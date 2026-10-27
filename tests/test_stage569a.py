"""Stage 569A verification suite (Cumulative 63-Round 256-Window WA Champion v10)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage569a_receipt_and_63round_256window_ledger() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage569a_cumulative_63round_256window_wa_champion_v10.json"
    assert p.exists(), "Missing stage569a receipt"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 569A"
    assert data["status"] == "CONFIRMED"
    assert data["total_counterbalanced_rounds"] == 63
    assert data["total_live_wa_triple_play_windows"] == 252
    assert data["total_live_windows_including_stage162a_e2e"] == 256
    assert data["milestone_63_rounds_256_windows_achieved"] is True
    assert len(data["rounds_r1_to_r63_ledger"]) == 63
    res = audit_stage_receipt_5pillars(data)
    assert res["compliant"] is True, f"5-pillar failure: {res['failures']}"
