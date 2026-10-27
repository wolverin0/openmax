from __future__ import annotations

import json
from pathlib import Path

from tools.sim.run_stage457a_guarida_backbone_60_61_notch_mitigation_pareto import (
    build_stage457a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage457a_guarida_backbone_60_61_notch_mitigation_pareto.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE457A_GUARIDA_BACKBONE_60_61_NOTCH_MITIGATION_PARETO.md"


def test_stage457a_notch_mitigation_pareto() -> None:
    assert ARTIFACT_PATH.exists()
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    live = build_stage457a_report()
    assert data["stage"] == "457A"
    assert data["writes_performed"] == 0
    assert data["pareto_deltas_vs_baseline"] == live["pareto_deltas_vs_baseline"]
    assert data["pareto_deltas_vs_baseline"]["ch0_evm_recovery_db"] >= 7.5
    assert data["pareto_deltas_vs_baseline"]["chain_evm_gap_reduction_db"] >= 7.0
    assert data["pareto_deltas_vs_baseline"]["bidirectional_goodput_gain_mbps"] >= 15.0


def test_stage457a_5pillar_and_doc_budget() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, audit
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
