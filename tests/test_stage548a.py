"""Tests for Stage 548A: athbox scn_stats Struct-Offset Aliasing Filter."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage548a_athbox_scn_stats_zero_false_positive_filter.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE548A_ATHBOX_SCN_STATS_ZERO_FALSE_POSITIVE_FILTER.md"


def test_stage548a_zero_false_positive_filter():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "548A"
    assert data["false_positive_alerts_after_filter"] == 0
    assert "0x0b5044" in data["struct_offset_aliasing_summary"]["writer_function"]
    assert "0x0d" in data["struct_offset_aliasing_summary"]["writer_condition"]
    for rad in data["evaluated_guarida_radios"]:
        assert rad["alert_triggered"] is False
        assert rad["lockstep_ratio_pct"] > 90.0
    assert "five_pillar_compliance" in data


def test_stage548a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
