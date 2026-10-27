from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "autoresearch"
    / "stage464a_multi_radio_11round_132window_scorecard.json"
)
DOC_PATH = (
    ROOT / "docs" / "STAGE464A_MULTI_RADIO_11ROUND_132WINDOW_SCORECARD.md"
)


def test_stage464a_scorecard_receipt_and_5pillars() -> None:
    assert RECEIPT_PATH.exists(), f"Missing {RECEIPT_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-464A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_250"] is False
    agg = data["campaign_totals"]
    assert agg["rounds_per_radio"] == 11
    assert agg["total_counterbalanced_windows"] == 132
    assert agg["total_paired_ab_comparisons"] == 66
    assert agg["all_radios_statistically_significant"] is True
    for rkey in ("XC_198", "2XC_253", "XM_20"):
        rstat = data["radios"][rkey]
        assert rstat["rounds_count"] == 11
        assert rstat["windows_count"] == 44
        assert rstat["paired_ab_comparisons"] == 22
        assert len(rstat["source_receipts"]) == 11
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, f"5-pillar audit failed: {audit}"

    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
