from __future__ import annotations

import json
from pathlib import Path

from tools.observability.build_stage456a_blind_rssi_vs_64subcarrier_evm_false_negative_matrix import (
    build_stage456a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage456a_blind_rssi_vs_64subcarrier_evm_false_negative_matrix.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE456A_BLIND_RSSI_VS_64SUBCARRIER_EVM_FALSE_NEGATIVE_MATRIX.md"


def test_stage456a_false_negative_matrix() -> None:
    assert ARTIFACT_PATH.exists()
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    live = build_stage456a_report()
    assert data["stage"] == "456A"
    assert data["writes_performed"] == 0
    summary = data["guarida_population_summary"]
    assert summary == live["guarida_population_summary"]
    assert summary["total_sector_cpes"] == 32
    assert summary["total_radio_endpoints_audited"] == 34
    assert summary["online_links_with_64evm_vectors"] == 12
    assert summary["strict_2db_rssi_false_negatives"] == 5
    assert summary["moderate_3db_rssi_false_negatives"] == 6
    assert summary["max_hidden_evm_excess_over_rssi_delta_db"] == 15.13


def test_stage456a_5pillar_and_doc_budget() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, audit
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
