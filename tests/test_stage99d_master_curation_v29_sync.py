#!/usr/bin/env python3
"""
Tests for Stage 99D (`T-S99D-MASTER-CURATION-V29-SYNC`).
"""

from __future__ import annotations

import json

from tools.research.run_stage99d_master_curation_v29_sync import (
    CORE_DOCS,
    DEFAULT_OUT_JSON,
    run_stage99d_master_curation_v29_sync,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


def test_stage99d_master_curation_v29_sync() -> None:
    receipt = run_stage99d_master_curation_v29_sync()
    assert DEFAULT_OUT_JSON.exists()
    assert receipt["stage"] == "99D"
    assert receipt["curation_version"] == "v29.0"
    assert receipt["status"] == "CONFIRMED"

    stages = receipt["synchronized_stages"]
    assert stages["Stage_97A"]["p50_rtt_delta_pct"] == -54.84
    assert stages["Stage_97A"]["pareto_delta_pct"] == 3.8216
    assert stages["Stage_97C_and_99B"]["superframe_symbols"] == 80
    assert stages["Stage_97C_and_99B"]["dl_symbols"] == 61
    assert stages["Stage_97C_and_99B"]["ul_symbols"] == 19
    assert stages["Stage_97C_and_99B"]["pymoo_pareto_front_count"] == 13
    assert stages["Stage_98A_98B_98C_98D"]["stage98d_tcp_goodput_mbps"] == 34.377
    assert stages["Stage_98A_98B_98C_98D"]["stage98c_total_bugs_consolidated"] == 38


def test_stage99d_core_docs_and_5pillar_gate() -> None:
    loaded = json.loads(DEFAULT_OUT_JSON.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True, f"5-pillar gate failed: {audit}"

    for doc_path in CORE_DOCS:
        assert doc_path.exists(), f"Missing {doc_path.name}"
        text = doc_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) < 220, f"{doc_path.name} has {len(lines)} lines (>= 220)"
        doc_heads = [ln for ln in lines if "<!-- doc-head" in ln]
        assert len(doc_heads) == 1, f"{doc_path.name} must have exactly 1 doc-head"
