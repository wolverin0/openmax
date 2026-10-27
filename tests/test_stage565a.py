"""Stage 565A verification suite (R57..R59 = 240 cumulative live windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage565a_receipt_and_pb050_v2_ram_staging() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage565a_live_wa_pb050_v2_and_pacing_r57_59.json"
    assert p.exists(), "Missing stage565a receipt"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 565A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["cumulative_wa_total_windows_including_e2e"] == 240
    assert data["pb050_v2_ram_staging"]["pb050_v2_seg2_0x0040c140"] == "0x0bb8 (3000 ms)"
    assert len(data["rounds"]) == 3
    res = audit_stage_receipt_5pillars(data)
    assert res["compliant"] is True, f"5-pillar failure: {res['failures']}"
