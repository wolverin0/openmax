"""Stage 629A verification suite (R64..R66 = 268 cumulative live windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage629a_receipt_and_pb050_v3_ram_staging() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage629a_live_wa_pb050_v3_and_sgi_guard_r64_66.json"
    assert p.exists(), "Missing stage629a receipt"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 629A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["cumulative_wa_total_windows_including_e2e"] == 268
    assert data["pb050_v3_and_helpers_staging"]["pb050_v3_seg2_0x0040c140"] == "0x1388 (5000 ms)"
    assert len(data["rounds"]) == 3
    res = audit_stage_receipt_5pillars(data)
    assert res["compliant"] is True, f"5-pillar failure: {res['failures']}"
