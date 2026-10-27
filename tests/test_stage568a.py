"""Stage 568A verification suite (Panel1-Guarida v10 rollout & 20h+ 3-CPE audit)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage568a_receipt_and_panel1_3cpe_audit() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage568a_live_panel1_guarida_84_v10_rollout_audit.json"
    assert p.exists(), "Missing stage568a receipt"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 568A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["zero_rf_disconnect_verified"] is True
    assert data["safety_boundaries"]["active_cpes_count"] == 3
    assert len(data["live_3cpe_20h_uptime_and_station_audit"]["cpes_audited"]) == 3
    res = audit_stage_receipt_5pillars(data)
    assert res["compliant"] is True, f"5-pillar failure: {res['failures']}"
