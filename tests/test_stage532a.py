from __future__ import annotations

import json
from pathlib import Path

from tools.re.dissect_stage532a_athbox_vs_umac_scn_stats_aliasing_map import (
    build_stage532a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage532a_athbox_vs_umac_scn_stats_aliasing_map.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE532A_ATHBOX_VS_UMAC_SCN_STATS_ALIASING_MAP.md"


def test_stage532a_scn_stats_aliasing_map() -> None:
    assert ARTIFACT_PATH.exists()
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    live = build_stage532a_report()
    assert data["stage"] == "532A"
    assert data["writes_performed"] == 0
    assert data["summary_counts"] == live["summary_counts"]
    assert data["summary_counts"]["total_mapped_fields"] == 25
    assert data["summary_counts"]["genuine_counters"] == 19
    assert data["summary_counts"]["struct_aliased_or_composite_counters"] == 3
    assert data["summary_counts"]["unpopulated_always_zero_counters"] == 3


def test_stage532a_5pillar_and_doc_budget() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, audit
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
