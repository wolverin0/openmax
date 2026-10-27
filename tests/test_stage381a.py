"""Verification test for Stage 381A (R37..R39, 160 Cumulative Windows)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
R_381A = ROOT / "artifacts" / "autoresearch" / "stage381a_live_wa_ampdu_rts_bidir_r37_39.json"


def test_stage381a_ampdu_rts_autocorking_r37_to_r39_receipt() -> None:
    assert R_381A.exists(), f"Missing {R_381A}"
    data = json.loads(R_381A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["protocol"] == "A1 -> B1 -> A2 -> B2"
    assert data["cumulative_wa_rf_windows_r1_to_r39"] == 156
    assert data["cumulative_wa_total_windows_including_e2e"] == 160
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    rounds = data["rounds"]
    assert len(rounds) == 3
    assert [r["round_id"] for r in rounds] == ["S381A-R37", "S381A-R38", "S381A-R39"]
    for r in rounds:
        assert len(r["windows"]) == 4
        assert r["decision"] in ("PROMOTE_ARM_B", "RETAIN_ARM_A")
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
