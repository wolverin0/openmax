from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "autoresearch"
    / "stage466a_multi_radio_v47_suite_gate_receipt.json"
)
DOC_PATH = ROOT / "docs" / "STAGE466A_MULTI_RADIO_V47_SUITE_GATE.md"


def test_stage461a_to_466a_multi_radio_v47_suite_gate() -> None:
    assert RECEIPT_PATH.exists(), f"Missing {RECEIPT_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-466A"
    assert data["status"] == "CONFIRMED"
    assert data["all_stages_passed"] is True
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_250"] is False
    assert len(data["audited_stages"]) == 5
    for st in data["audited_stages"]:
        assert st["passed"] is True, f"Stage failed audit: {st}"
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, f"5-pillar audit failed: {audit}"

    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
