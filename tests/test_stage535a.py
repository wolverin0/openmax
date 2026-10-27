from __future__ import annotations

import json
from pathlib import Path

from tools.observability.build_stage535a_guarida_34endpoint_zero_fp_maintenance_dossier_v3 import (
    build_stage535a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage535a_guarida_34endpoint_zero_fp_maintenance_dossier_v3.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE535A_GUARIDA_34ENDPOINT_ZERO_FP_MAINTENANCE_DOSSIER_V3.md"


def test_stage535a_maintenance_dossier_v3() -> None:
    assert ARTIFACT_PATH.exists()
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    live = build_stage535a_report()
    assert data["stage"] == "535A"
    assert data["writes_performed"] == 0
    assert data["guarida_34endpoint_population_audit"] == live["guarida_34endpoint_population_audit"]
    assert data["guarida_34endpoint_population_audit"]["total_endpoints"] == 34
    assert len(data["prioritized_maintenance_interventions"]) == 5


def test_stage535a_5pillar_and_doc_budget() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, audit
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
