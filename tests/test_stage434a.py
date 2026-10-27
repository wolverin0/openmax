from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / "artifacts" / "autoresearch" / "stage434a_multi_radio_10round_120window_scorecard.json"
DOC_PATH = ROOT / "docs" / "STAGE434A_MULTI_RADIO_10ROUND_120WINDOW_SCORECARD.md"


def test_stage434a_scorecard_receipt_and_5pillars() -> None:
    assert RECEIPT_PATH.exists(), f"Missing {RECEIPT_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-434A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_250"] is False
    agg = data["campaign_totals"]
    assert agg["rounds_per_radio"] == 10
    assert agg["total_counterbalanced_windows"] == 120
    assert agg["total_paired_ab_comparisons"] == 60
    assert agg["all_radios_statistically_significant"] is True
    for rkey in ("XC_198", "2XC_253", "XM_20"):
        rstat = data["radios"][rkey]
        assert rstat["rounds_count"] == 10
        assert rstat["windows_count"] == 40
        assert rstat["paired_ab_comparisons"] == 20
        assert len(rstat["source_receipts"]) == 10
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, f"5-pillar audit failed: {audit}"

    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
