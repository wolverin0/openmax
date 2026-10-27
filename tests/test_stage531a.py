from __future__ import annotations

import json
from pathlib import Path

from tools.observability.audit_stage531a_guarida_panel2_panel3_per_cpe_64evm_forensics import (
    build_stage531a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage531a_guarida_panel2_panel3_per_cpe_64evm_forensics.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE531A_GUARIDA_PANEL2_PANEL3_PER_CPE_64EVM_FORENSICS.md"


def test_stage531a_per_cpe_64evm_forensics() -> None:
    assert ARTIFACT_PATH.exists()
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    live = build_stage531a_report()
    assert data["stage"] == "531A"
    assert data["writes_performed"] == 0
    assert data["sosa_joaquin_forensic_spotlight"] == live["sosa_joaquin_forensic_spotlight"]
    sosa = data["sosa_joaquin_forensic_spotlight"]
    assert sosa["abs_delta_rssi_db"] == 0
    assert sosa["max_abs_evm_gap_db"] == 16.26
    assert sosa["hidden_evm_excess_over_rssi_db"] == 16.26
    assert len(data["online_panel2_panel3_cpe_ranking"]) == 10


def test_stage531a_5pillar_and_doc_budget() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, audit
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
