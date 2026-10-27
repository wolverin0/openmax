#!/usr/bin/env python3
"""Unit tests for PB-000..PB-070 Master End-to-End Ladder Orchestrator."""

from __future__ import annotations

import json

from controller.pb_master_ladder_orchestrator import (
    DEFAULT_AUDIT_OUTPUT_PATH,
    build_master_ladder_readiness_audit,
)


def test_master_ladder_maps_all_16_gates_with_zero_missing_files() -> None:
    report = build_master_ladder_readiness_audit()
    assert report["automatic_execution_allowed"] is False
    assert report["all_16_gates_mapped"] is True
    assert len(report["gates"]) == 16
    assert report["missing_files_count"] == 0
    assert report["missing_files"] == []
    assert report["hardware_auto_exec_violations"] == []

    # Verify every module and artifact entry has a valid 64-hex-char SHA-256
    for g in report["gates"]:
        for item in g["modules_verified"] + g["offline_artifacts_verified"]:
            assert item["exists"] is True
            assert item["size_bytes"] > 0
            assert isinstance(item["sha256"], str) and len(item["sha256"]) == 64


def test_master_ladder_scorecard_and_preflight_safety_gates() -> None:
    assert DEFAULT_AUDIT_OUTPUT_PATH.exists()
    saved = json.loads(DEFAULT_AUDIT_OUTPUT_PATH.read_text(encoding="utf-8"))

    t1 = saved["preflight_safety_checks"]["track1_channel_and_timing"]
    t2 = saved["preflight_safety_checks"]["track2_utf_and_sub20mhz"]
    assert t1["status"] == "BLOCKED_AWAITING_OPERATOR_GATE"
    assert t1["authorized_for_hardware_execution"] is False
    assert t2["status"] == "BLOCKED_AWAITING_OPERATOR_GATE"
    assert t2["authorized_for_hardware_execution"] is False

    scorecard = saved["quantitative_workstream_scorecard"]
    assert scorecard["pb010_wmi_opcodes_mapped"] == 5
    assert scorecard["pb011_sgmt_containers_verified"] == 8
    assert scorecard["pb030_grid_points_evaluated"] == 20
    assert len(scorecard["pb031_promoted_phy_treatments"]) == 3
    assert scorecard["pb040_inert_diff_byte_count"] == 4
    assert scorecard["pb050_p99_jitter_reduction_factor"] > 15.0
    assert scorecard["pb051_feasibility_verdict"] == "PASSED_FEASIBILITY_GATE"
    assert scorecard["pb060_promoted_candidate_ids"] == ["CAND_01_10MHZ_LDPC_STBC_AQL3000"]
    assert scorecard["pb070_custom_phy_verdict"] == "LOCKED_CONCENTRATE_ON_MAC_AND_POLICY"


def test_master_ladder_simulated_progression_unlocks_next_bench_tracks() -> None:
    # Simulate PB-000 also marked PASSED alongside PB-001, PB-010, PB-011
    sim = build_master_ladder_readiness_audit(
        passed_overrides={"PB-000", "PB-001", "PB-010", "PB-011"}
    )
    unblocked = set(sim["currently_unblocked_gate_ids"])
    assert "PB-020" in unblocked
    assert "PB-021" in unblocked
    assert "PB-050" in unblocked
    # PB-040 still requires PB-020, and PB-070 still requires PB-023, PB-031, PB-040
    assert "PB-040" not in unblocked
    assert "PB-070" not in unblocked
