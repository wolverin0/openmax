"""Pytest for Stage 655A (650-Stage Milestone Audit & 216-Window Multi-Radio Milestone)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage655a_receipt_and_doc() -> None:
    p_json = ROOT / "artifacts/autoresearch/stage655a_multi_radio_216w_and_650stage_audit.json"
    p_doc = ROOT / "docs/STAGE655A_MULTI_RADIO_216W_AND_650STAGE_AUDIT.md"
    assert p_json.exists()
    assert p_doc.exists()
    data = json.loads(p_json.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-655A"
    assert data["status"] == "CONFIRMED"
    assert data["milestone_stage"] == 650
    assert data["cumulative_multi_radio_windows"] == 216
    assert data["new_windows_in_stage655a"] == 12
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_250"] is False
    assert data["five_pillar_compliant"] is True
    doc_text = p_doc.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 200
    assert doc_text.count("<!-- doc-head:") == 1
