#!/usr/bin/env python3
"""Stage 458A — Consolidated Verification Suite for Stages 453A..458A
(`ast_rxorn` 230.72M `process_rx_stats` Struct-Offset Aliasing, 5-Snapshot `.60 <-> .61`
64-Element EVM Audit, `Panel2 .82` `139.75M` `mpdus_requed` vs `Panel3 .83` `9.52M`
`excess_retries`, Guarida 50% Blind Chain RSSI False-Negative Matrix, SimPy + pymoo NSGA-II
`.60 <-> .61` Notch Mitigation Pareto, and `FMX-DISC-47/48` Curation).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage458a_guarida_evm_and_rxorn_suite import build_stage458a_report

REPO_ROOT = Path(__file__).resolve().parents[1]

STAGE_JSONS = [
    ("453A", REPO_ROOT / "artifacts" / "autoresearch" / "stage453a_guarida_bh_230m_ast_rxorn_and_pcie_ce_ring_re.json"),
    ("454A", REPO_ROOT / "artifacts" / "autoresearch" / "stage454a_guarida_60_61_subcarrier_notch_and_cinr_gap.json"),
    ("455A", REPO_ROOT / "artifacts" / "autoresearch" / "stage455a_ubnt_poll_UL_slot_starvation_and_requeue_re.json"),
    ("456A", REPO_ROOT / "artifacts" / "autoresearch" / "stage456a_blind_rssi_vs_64subcarrier_evm_false_negative_matrix.json"),
    ("457A", REPO_ROOT / "artifacts" / "autoresearch" / "stage457a_guarida_backbone_60_61_notch_mitigation_pareto.json"),
    ("458A", REPO_ROOT / "artifacts" / "autoresearch" / "stage458a_guarida_evm_and_rxorn_suite_receipt.json"),
]

STAGE_DOCS = [
    REPO_ROOT / "docs" / "STAGE453A_GUARIDA_BH_230M_AST_RXORN_AND_PCIE_CE_RING_RE.md",
    REPO_ROOT / "docs" / "STAGE454A_GUARIDA_60_61_SUBCARRIER_NOTCH_AND_CINR_GAP.md",
    REPO_ROOT / "docs" / "STAGE455A_UBNT_POLL_UL_SLOT_STARVATION_AND_REQUEUE_RE.md",
    REPO_ROOT / "docs" / "STAGE456A_BLIND_RSSI_VS_64SUBCARRIER_EVM_FALSE_NEGATIVE_MATRIX.md",
    REPO_ROOT / "docs" / "STAGE457A_GUARIDA_BACKBONE_60_61_NOTCH_MITIGATION_PARETO.md",
    REPO_ROOT / "docs" / "STAGE458A_GUARIDA_EVM_AND_RXORN_SUITE.md",
    REPO_ROOT / "docs" / "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md",
]


@pytest.mark.parametrize(("expected_stage", "json_path"), STAGE_JSONS)
def test_stage453a_to_458a_receipts_and_5pillars(expected_stage: str, json_path: Path) -> None:
    assert json_path.exists(), f"Missing receipt: {json_path}"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["stage"] == expected_stage
    assert data["status"] == "COMPLETED"
    assert data["claim_status"] == "CONFIRMED"
    assert data["writes_performed"] == 0
    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, gate


@pytest.mark.parametrize("doc_path", STAGE_DOCS)
def test_stage453a_to_458a_markdown_line_budget_and_doc_head(doc_path: Path) -> None:
    assert doc_path.exists(), f"Missing doc: {doc_path}"
    text = doc_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"{doc_path.name} has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1, f"{doc_path.name} must have exactly 1 doc-head comment"


def test_stage458a_consolidated_suite_and_curated_discoveries() -> None:
    report = build_stage458a_report()
    assert report["all_checks_passed"] is True
    assert report["curated_discoveries_verified"]["FMX-DISC-47"] is True
    assert report["curated_discoveries_verified"]["FMX-DISC-48"] is True
