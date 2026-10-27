from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "autoresearch"
    / "stage495a_live_xm20_round12_144window_autoresearch.json"
)
DOC_PATH = (
    ROOT / "docs" / "STAGE495A_LIVE_XM20_ROUND12_144WINDOW_AUTORESEARCH.md"
)


def test_stage495a_live_xm20_round12_144window_autoresearch() -> None:
    assert RECEIPT_PATH.exists(), f"Missing {RECEIPT_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-495A"
    assert data["status"] == "CONFIRMED"
    assert (
        data["milestone_reached"]
        == "144_COUNTERBALANCED_WINDOWS_ACROSS_XC_2XC_XM"
    )
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_250"] is False
    assert data["safety_boundaries"]["flash_writes_count"] == 0
    assert len(data["counterbalanced_windows"]) == 4
    assert [w["window_id"] for w in data["counterbalanced_windows"]] == [
        "W1_A1",
        "W2_B1",
        "W3_A2",
        "W4_B2",
    ]
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, f"5-pillar audit failed: {audit}"

    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
