#!/usr/bin/env python3
"""Unit tests for PB-050 & PB-051 Scheduler Timing & Slot Gate Harness."""

from __future__ import annotations

import json

from controller.pb_050_051_scheduler_timing_harness import (
    DEFAULT_FIXTURE_OUTPUT_PATH,
    SdrBurstObservation,
    build_pb_050_051_fixture_report,
    compute_burst_edge_jitter_cdf,
    evaluate_pb051_target_slot_feasibility,
)


def test_pb_050_host_vs_target_jitter_cdf_and_guard_floor() -> None:
    report = build_pb_050_051_fixture_report()
    assert report["automatic_execution_allowed"] is False

    comp = report["pb050_host_vs_target_timing_comparison"]
    host = comp["host_queue_gating_15ms"]
    target = comp["target_tsf_timer_2ms"]

    # Host queue-gating has millisecond-scale p99 jitter and cannot credibly run sub-ms slots
    assert host["jitter_p99_us"] > 1000.0
    assert host["minimum_safe_guard_interval_us"] > 2500.0
    assert host["sub_ms_slots_physically_credible"] is False

    # Target TSF timer has <100us p99 jitter and <300us guard floor at 6km
    assert target["jitter_p99_us"] < 100.0
    assert target["minimum_safe_guard_interval_us"] < 300.0
    assert target["sub_ms_slots_physically_credible"] is True
    assert comp["p99_jitter_reduction_factor"] > 15.0


def test_pb_051_out_of_slot_leakage_detector_catches_csma_violations() -> None:
    # Create 100 bursts with 2 out-of-slot violations (2.0% leakage > 0.5% threshold)
    obs = []
    for i in range(100):
        sched_start = i * 2000.0
        obs_start = sched_start + 15.0
        # Make bursts 10 and 20 overflow past the usable slot end
        obs_end = (sched_start + 1950.0) if i in (10, 20) else (sched_start + 1500.0)
        obs.append(
            SdrBurstObservation(
                burst_id=i,
                peer_id="cpe_near",
                scheduled_slot_start_us=sched_start,
                scheduled_slot_duration_us=2000.0,
                assigned_guard_us=250.0,
                observed_rf_start_us=obs_start,
                observed_rf_end_us=obs_end,
            )
        )

    timing = compute_burst_edge_jitter_cdf(obs, distance_km=6.0)
    assert timing["out_of_slot_violations"] == 2
    assert timing["out_of_slot_violation_rate_pct"] == 2.0


def test_pb_051_feasibility_gate_promotion_and_saved_artifact() -> None:
    saved = build_pb_050_051_fixture_report()
    pb051 = saved["pb051_target_scheduler_feasibility"]
    assert pb051["overall_feasibility_verdict"] == "SYNTHETIC_PASS"
    assert pb051["criteria_checks"]["p99_jitter_le_250us"] is True
    assert pb051["criteria_checks"]["out_of_slot_leakage_lt_0_5pct"] is True
    assert pb051["criteria_checks"]["paired_hidden_node_qoe_promoted"] is False
    assert pb051["diagnostic_passed"] is True
    assert pb051["physical_promotion_accepted"] is False
    assert pb051["paired_qoe_decision"]["verdict"] == "SYNTHETIC_PASS"
