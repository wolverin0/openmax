"""Unit and integration tests for Stage 102A (T-S102A-571KNOB-UNTESTED-CANDIDATES-PARETO-SWEEP)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage102a_571knob_untested_pareto_sweep import (
    DEFAULT_OUTPUT_PATH,
    TOP_12_UNTESTED_KNOB_SPECS,
    audit_571knob_catalog_against_stage_receipts,
    run_stage102a_verification,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "STAGE102A_571KNOB_UNTESTED_PARETO_SWEEP.md"


def test_stage102a_catalog_audit_571_knobs_and_top12() -> None:
    audit = audit_571knob_catalog_against_stage_receipts()
    assert audit["total_knobs"] == 571
    assert audit["empirically_tested_knobs_count"] + audit["untested_knobs_count"] == 571
    assert audit["stage_receipts_scanned"] >= 400
    assert len(audit["top_12_untested_priority_knobs"]) == 12

    archs = {k["platform_arch"] for k in audit["top_12_untested_priority_knobs"]}
    assert archs == {"WA", "XC", "XW", "AF-LTU"}
    interfaces = {k["interface_type"] for k in audit["top_12_untested_priority_knobs"]}
    assert interfaces == {"sysctl", "debugfs", "module_param", "sysfs"}


def test_stage102a_simpy_nsga2_pareto_receipt_and_5pillars(tmp_path: Path) -> None:
    out_file = tmp_path / "stage102a_test.json"
    receipt = run_stage102a_verification(out_path=out_file)
    assert out_file.exists()
    assert DEFAULT_OUTPUT_PATH.exists()

    gate = audit_stage_receipt_5pillars(receipt)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"

    sweep = receipt["simpy_pymoo_pareto_sweep"]
    assert sweep["nsga2_config"]["n_var"] == 12
    assert sweep["nsga2_config"]["n_obj"] == 3
    assert sweep["nsga2_config"]["n_ieq_constr"] == 2
    assert len(sweep["oat_12knob_sensitivity_ranking"]) == 12
    assert sweep["pareto_front_count"] >= 1

    knee = sweep["nsga2_knee_champion"]
    assert knee["feasible"] is True
    assert knee["voip_loss_pct"] == 0.0
    assert knee["airtime_utilization_pct"] <= 94.0

    jc = sweep["joint_counterbalanced_verification"]
    assert jc["protocol"] == "A1->B1->A2->B2"
    assert jc["watchdog_seconds"] == 45
    assert jc["deltas"]["goodput_delta_pct"] > 10.0
    assert jc["deltas"]["p95_rtt_delta_pct"] < -10.0
    assert jc["deltas"]["pareto_score_delta_pct"] > 10.0


def test_stage102a_markdown_doc_budget_and_doc_head() -> None:
    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 180, f"Doc has {len(lines)} lines (must be < 180)"
    assert lines[0].startswith("<!-- doc-head:"), "Doc must start with <!-- doc-head: on line 1"
    doc_heads = [ln for ln in lines if "<!-- doc-head:" in ln]
    assert len(doc_heads) == 1
    for token in (
        "T-S102A-571KNOB-UNTESTED-CANDIDATES-PARETO-SWEEP",
        "wa_8_7_25_proc_sys_dev_uph_wifi0_swr_limit",
        "xc_8_7_25_proc_sys_dev_uph_wifi0_gqparam",
        "ct_special_7",
        "ltu_ap_2_4_2_sys_class_ame_ame_ctrl_dev_ofdma_subbands",
        "+20.102%",
        "-17.379%",
    ):
        assert token in text, f"Missing token {token} in {DOC_PATH.name}"
