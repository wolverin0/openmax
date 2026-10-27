from __future__ import annotations

import json
from pathlib import Path

from tools.observability.audit_stage534a_panel1_guarida_84_openwrt_per_sta_airtime_and_rc import (
    build_stage534a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage534a_panel1_guarida_84_openwrt_per_sta_airtime_and_rc.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE534A_PANEL1_GUARIDA_84_OPENWRT_PER_STA_AIRTIME_AND_RC.md"


def test_stage534a_panel1_openwrt_audit() -> None:
    assert ARTIFACT_PATH.exists()
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    live = build_stage534a_report()
    assert data["stage"] == "534A"
    assert data["writes_performed"] == 0
    assert data["sector_aggregate_summary"] == live["sector_aggregate_summary"]
    assert data["sector_aggregate_summary"]["active_stations"] == 3
    assert data["sector_aggregate_summary"]["sector_weighted_tx_retry_rate_pct"] == 1.227
    assert len(data["per_station_audit"]) == 3


def test_stage534a_5pillar_and_doc_budget() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, audit
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
