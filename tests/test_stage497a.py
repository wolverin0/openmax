from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    ROOT / "artifacts" / "autoresearch" / "stage497a_cross_fleet_champion_v48.json"
)
DOC_PATH = ROOT / "docs" / "STAGE497A_CROSS_FLEET_CHAMPION_V48.md"


def test_stage497a_cross_fleet_champion_v48() -> None:
    assert RECEIPT_PATH.exists(), f"Missing {RECEIPT_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-497A"
    assert data["champion_version"] == "v48.0"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_250"] is False
    assert data["scorecard_reference"]["total_counterbalanced_windows"] == 144
    assert data["scorecard_reference"]["total_paired_ab_comparisons"] == 72
    profiles = data["fleet_profiles"]
    for fam in ("XC", "2XC", "XM", "WA", "XW", "LTU"):
        assert fam in profiles
    assert len(profiles["XC"]["rounds_integrated"]) == 12
    assert len(profiles["2XC"]["rounds_integrated"]) == 12
    assert len(profiles["XM"]["rounds_integrated"]) == 12
    assert profiles["WA"]["key_knobs"]["pb050_rc_probe_dampener_integrated"] is True
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, f"5-pillar audit failed: {audit}"

    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
