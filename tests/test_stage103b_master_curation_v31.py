#!/usr/bin/env python3
"""Unit tests for Stage 103B Master Curation v31.0 (`T-S103B-MASTER-CURATION-V31-S102-AND-H1-SUBMITTED-SYNC`)."""

from __future__ import annotations

import json

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage103b_master_curation_v31 import (
    OUTPUT_JSON_PATH,
    TARGET_DOCS,
    run_stage103b_verification,
)


def test_stage103b_master_curation_v31_execution_and_receipt() -> None:
    receipt = run_stage103b_verification()
    assert OUTPUT_JSON_PATH.exists()
    assert receipt["stage"] == "103B"
    assert receipt["curation_version"] == "v31.0"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["all_docs_passed"] is True

    s102a = receipt["synchronized_receipts"]["stage102a_571knob_pareto"]
    assert s102a["total_knobs"] == 571
    assert s102a["stage_receipts_scanned"] == 451
    assert s102a["empirically_tested_knobs_count"] == 53
    assert s102a["untested_knobs_count"] == 518
    assert s102a["pareto_front_count"] == 5
    assert s102a["knee_goodput_mbps"] == 50.156
    assert s102a["counterbalanced_pareto_delta_pct"] == 18.384

    s102b = receipt["synchronized_receipts"]["stage102b_observability_v30_sync"]
    assert s102b["exporter_ready"] is True
    assert s102b["required_metrics_present"] is True
    assert s102b["required_alerts_present"] is True
    assert s102b["synchronized_domains_count"] == 4
    assert s102b["total_grafana_panels"] == 47
    assert s102b["stage102b_panel_ids"] == [44, 45, 46, 47]

    s102e = receipt["synchronized_receipts"]["stage102e_ltu_superframe_pacing"]
    assert s102e["sched_mcs_limit_symbol_end"] == 59
    assert s102e["sched_max_agg_cnt"] == 8
    assert s102e["multi_ack_enable"] == 1
    assert s102e["netdev_budget"] == 640
    assert s102e["dev_weight"] == 80
    assert s102e["soc_bulk_tcp_arm_b_median_mbps"] == 180.579
    assert s102e["soc_bulk_tcp_arm_b_peak_mbps"] == 200.758
    assert s102e["scheduler_giveup_max"] == 0
    assert s102e["symbol_giveup_max"] == 0

    w4c = receipt["synchronized_receipts"]["stage81a_w4c_ubntbox_applets"]
    assert w4c["images_audited"] == 2
    assert w4c["ubntbox_bytes"] == 899180
    assert w4c["got_calls_per_image"] == 4346
    assert w4c["resolved_calls_per_image"] == 3694
    assert w4c["cgi_files"] == 5
    assert w4c["applets_with_sinks"] == 0

    h1 = receipt["synchronized_receipts"]["hackerone_report_4148356"]
    assert h1["report_id"] == "#4148356"
    assert h1["state"] == "New / Open"
    assert h1["verified_in_docs"] is True


def test_stage103b_docs_line_budgets_and_5pillar_gate() -> None:
    loaded = json.loads(OUTPUT_JSON_PATH.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True, f"5-pillar gate failed: {audit}"

    for doc_path in TARGET_DOCS:
        assert doc_path.exists(), f"Missing {doc_path.name}"
        lines = doc_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) < 215, f"{doc_path.name} has {len(lines)} lines (>= 215)"
        doc_heads = [ln for ln in lines if "<!-- doc-head" in ln]
        assert len(doc_heads) == 1, f"{doc_path.name} must have exactly 1 doc-head"
