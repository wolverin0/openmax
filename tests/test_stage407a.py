"""Stage 407A verification tests — 49-Round 200-Window Universal WA Champion v8."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage407a_receipt_and_5pillar() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage407a_cumulative_49round_200window_wa_champion_v8.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 407A"
    assert data["status"] == "CONFIRMED"
    assert data["total_counterbalanced_rounds"] == 49
    assert data["total_live_windows_including_stage162a_e2e"] == 200
    assert data["milestone_49_rounds_200_windows_achieved"] is True
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
