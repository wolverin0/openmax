#!/usr/bin/env python3
"""Unit tests for Stage 80C Updated 571-Knob Coverage Ledger and FMX-DISC-21..23 Curation Sync."""

from __future__ import annotations

from pathlib import Path

from tools.research.run_stage80c_571knob_and_discoveries_v23_sync import (
    CURATED_DISCOVERIES_DOC,
    CURRENT_STATE_DOC,
    DEFAULT_OUTPUT_JSON,
    EXPECTED_CATALOG_SHA256,
    MASTER_INDEX_DOC,
    run_stage80c_571knob_and_discoveries_v23_sync,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE80C_DOC = REPO_ROOT / "docs" / "STAGE80C_571KNOB_AND_FMX_DISC_23_MASTER_SYNC.md"


def test_stage80c_571knob_ledger_and_fmx_disc_21_to_23_sync() -> None:
    payload = run_stage80c_571knob_and_discoveries_v23_sync()
    assert DEFAULT_OUTPUT_JSON.exists()

    gate = audit_stage_receipt_5pillars(payload)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"

    summary = payload["ledger_summary"]
    assert summary["total_catalog_knobs"] == 571
    assert summary["catalog_sha256"] == EXPECTED_CATALOG_SHA256
    assert summary["catalog_byte_immutable"] is True
    assert summary["historical_discoveries_count"] == 23
    assert summary["new_discoveries_curated"] == ["FMX-DISC-21", "FMX-DISC-22", "FMX-DISC-23"]
    assert "STAGE79A_PTP_CHAMPION_V7" in summary["active_ptp_champion"]

    disc_ids = [d["discovery_id"] for d in payload["fmx_discoveries_21_to_23"]]
    assert disc_ids == ["FMX-DISC-21", "FMX-DISC-22", "FMX-DISC-23"]


def test_stage80c_curated_docs_respect_220_line_budget_and_include_fmx_disc_21_to_23() -> None:
    for doc_path in (CURATED_DISCOVERIES_DOC, MASTER_INDEX_DOC, CURRENT_STATE_DOC, STAGE80C_DOC):
        assert doc_path.exists(), f"Missing {doc_path}"
        text = doc_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) < 220, f"{doc_path.name} has {len(lines)} lines (must be < 220)"
        assert lines[0].startswith("<!-- doc-head:"), f"{doc_path.name} missing doc-head on line 1"
        assert text.count("<!-- doc-head:") == 1, f"{doc_path.name} has multiple doc-head blocks"
        for token in ("FMX-DISC-21", "FMX-DISC-22", "FMX-DISC-23", "set_multiq"):
            assert token in text, f"{doc_path.name} missing token {token}"
