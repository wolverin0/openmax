#!/usr/bin/env python3
"""Unit tests for Stage 101B Master Curation v30.0 (`T-S101B-MASTER-CURATION-V30-W4B-S101A-AND-H1-LIVE-POC-SYNC`)."""

from __future__ import annotations

import json

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage101b_master_curation_v30 import (
    OUTPUT_JSON_PATH,
    TARGET_DOCS,
    run_stage101b_verification,
)


def test_stage101b_master_curation_v30_execution_and_receipt() -> None:
    receipt = run_stage101b_verification()
    assert OUTPUT_JSON_PATH.exists()
    assert receipt["stage"] == "101B"
    assert receipt["curation_version"] == "v30.0"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["all_docs_passed"] is True

    w4b = receipt["synchronized_receipts"]["stage81a_w4b"]
    assert w4b["modules_audited"] == 8
    assert w4b["ctl_arrays"] == 16
    assert w4b["ctl_entries"] == 80
    assert w4b["ctl_world_writable"] == 0
    assert w4b["maxlen_checked"] == 72
    assert w4b["maxlen_overflows"] == 0
    assert w4b["sscanf_sites"] == 22
    assert w4b["sscanf_unbounded"] == 4

    s101a = receipt["synchronized_receipts"]["stage101a_champion_v23"]
    assert s101a["daemon_path_on_ap"] == "/usr/sbin/fmx_wds_churn_healer.sh"
    assert s101a["auto_heal_recovery_delta_pct"] == -55.56
    assert s101a["survivor_wa_to_mk1_p95_delta_pct"] == -65.91
    assert s101a["voip_jitter_delta_pct"] == -55.081
    assert s101a["arm_b_voip_loss_pct"] == 0.0
    assert s101a["pareto_delta_pct"] == 6.3928

    h1 = receipt["synchronized_receipts"]["h1_ltu_suid_live_poc"]
    assert h1["all_live_poc_tokens_present"] is True


def test_stage101b_docs_line_budgets_and_5pillar_gate() -> None:
    loaded = json.loads(OUTPUT_JSON_PATH.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True, f"5-pillar gate failed: {audit}"

    for doc_path in TARGET_DOCS:
        assert doc_path.exists(), f"Missing {doc_path.name}"
        lines = doc_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) < 215, f"{doc_path.name} has {len(lines)} lines (>= 215)"
        doc_heads = [ln for ln in lines if "<!-- doc-head" in ln]
        assert len(doc_heads) == 1, f"{doc_path.name} must have exactly 1 doc-head"
