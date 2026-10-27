"""Stage 404A verification tests — 200-Window Live Milestone R46..R49."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage404a_receipt_and_5pillar() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage404a_live_wa_200window_milestone_r46_49.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 404A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_wa_total_windows_including_e2e"] == 200
    assert data["milestone_200_live_windows_achieved"] is True
    assert [r["round_id"] for r in data["rounds"]] == ["S404A-R46", "S404A-R47", "S404A-R48", "S404A-R49"]
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
