#!/usr/bin/env python3
"""Unit tests for Stage 79B Closed-Loop Auto-Remediation Orchestrator & Guarida Canary Readiness Gate."""

from __future__ import annotations

from pathlib import Path

from tools.telemetry.run_stage79b_closed_loop_auto_remediation_orchestrator import (
    DEFAULT_OUTPUT_JSON,
    run_stage79b_closed_loop_auto_remediation_orchestrator,
    verify_stage79b_preflight_safety_filter,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "STAGE79B_CLOSED_LOOP_AUTO_REMEDIATION_ORCHESTRATOR.md"


def test_stage79b_orchestrator_all_5_regimes_and_5pillar_gate() -> None:
    payload = run_stage79b_closed_loop_auto_remediation_orchestrator()
    assert DEFAULT_OUTPUT_JSON.exists()

    gate = audit_stage_receipt_5pillars(payload)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"

    summary = payload["orchestrator_summary"]
    assert summary["execution_mode"] == "DRY_RUN_SHADOW_EXECUTION"
    assert summary["automatic_execution_allowed"] is False
    assert summary["live_devices_touched"] is False
    assert summary["live_bench_links_evaluated"] == 5
    assert summary["regimes_covered"] == 5
    assert summary["all_live_links_noop_keep_champion"] is True
    assert summary["frozen_collector_rf_mutation_blocked"] is True
    assert summary["all_active_remediations_pass_safety_filter"] is True
    assert summary["negative_safety_probes_correctly_rejected"] is True

    matrix = payload["five_regime_remediation_matrix"]
    # 0: NORMAL_LOAD
    r0 = matrix["REGIME_0_NORMAL_LOAD"]
    assert r0["action_id"] == "NO_OP_KEEP_CHAMPION"
    assert r0["kuma_push_allowed"] is True
    assert r0["rf_remediation_commands"] == []

    # 1: CO_CHANNEL_INTERFERENCE
    r1 = matrix["REGIME_1_CO_CHANNEL_INTERFERENCE"]
    assert r1["action_id"] == "APPLY_STAGE71B_73A_AIRPRISM_50MHZ_AND_DAPROT2"
    r1_cmds = "\n".join(r1["rf_remediation_commands"])
    assert "daprot" in r1_cmds
    assert "ff_mcast_airtime_limit" in r1_cmds
    assert "45" in r1_cmds

    # 2: BAD_APPLE_AIRTIME_HOG
    r2 = matrix["REGIME_2_BAD_APPLE_AIRTIME_HOG"]
    assert r2["action_id"] == "APPLY_STAGE72A_75A_MULTIQ3_AQL_AND_BNG_CAKE"
    r2_cmds = "\n".join(r2["rf_remediation_commands"])
    assert "set_multiq 3" in r2_cmds
    assert "aql_threshold" in r2_cmds
    assert "1500 3000" in r2_cmds
    assert "cake" in r2_cmds

    # 3: LTU_BUG05_LNA_DEAFNESS
    r3 = matrix["REGIME_3_LTU_BUG05_LNA_DEAFNESS"]
    assert r3["action_id"] == "APPLY_STAGE63B_68B_LTU_LNA_AND_RPS_REMEDIATION"
    r3_cmds = "\n".join(r3["rf_remediation_commands"])
    assert "rx_gain=low" in r3_cmds
    assert "tx_power_Auto=0" in r3_cmds
    assert "tx_power=24" in r3_cmds
    assert "max_tx_mod_idx=12" in r3_cmds
    assert "/sys/class/net/eth0/queues/rx-0/rps_cpus" in r3_cmds
    assert "/sys/class/net/eab0/queues/rx-0/rps_cpus" in r3_cmds

    # 4: FROZEN_COLLECTOR_FALSE_ALARM
    r4 = matrix["REGIME_4_FROZEN_COLLECTOR_FALSE_ALARM"]
    assert r4["action_id"] == "SUPPRESS_RF_FALSE_ALARM_RESTART_COLLECTOR_ONLY"
    assert r4["rf_mutation_blocked"] is True
    assert r4["kuma_push_allowed"] is False
    assert r4["rf_remediation_commands"] == []
    assert any("fmx-rf-collector" in c for c in r4["collector_self_restart_commands"])


def test_stage79b_preflight_safety_filter_enforces_backbone_and_mtd_guards() -> None:
    safe_res = verify_stage79b_preflight_safety_filter(["echo 2 > /proc/sys/dev/uph_wifi0/daprot"])
    assert safe_res["all_safety_checks_passed"] is True
    assert safe_res["protects_ether2_sw_poe200"] is True
    assert safe_res["protects_mtd0_mtd1_mtd5"] is True

    bad_poe = verify_stage79b_preflight_safety_filter(["/interface ethernet disable ether2-sw-poe200"])
    assert bad_poe["protects_ether2_sw_poe200"] is False
    assert bad_poe["all_safety_checks_passed"] is False

    bad_mtd = verify_stage79b_preflight_safety_filter(["mtd write /tmp/u-boot.bin mtd0"])
    assert bad_mtd["protects_mtd0_mtd1_mtd5"] is False
    assert bad_mtd["all_safety_checks_passed"] is False


def test_stage79b_doc_budget_and_header() -> None:
    assert DOC_PATH.exists()
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
