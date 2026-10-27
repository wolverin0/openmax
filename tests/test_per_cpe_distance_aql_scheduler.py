"""Unit and integration tests for Stage 12 Mixed-Distance Per-CPE AQL & Airtime Scheduler."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from controller.per_cpe_distance_aql_scheduler import (
    CONFIRMED_R97_R109_ANCHORS,
    PerCPEDistanceAQLScheduler,
    compute_per_cpe_schedule,
    coverage_class_to_timings,
    distance_to_coverage_class,
)
from tools.sim.fmx_mixed_distance_near_far_ptmp_sim import (
    POLICIES,
    build_mixed_distance_sector_cpes,
    evaluate_single_link_r97_r109_anchors,
    run_mixed_distance_sector_sim,
)


def test_coverage_class_and_slot_timings_match_r82_r97_r109() -> None:
    """Verify QCA988x coverage_class, slot_time_us, and ack_timeout_us match physical bench receipts."""
    expected = [
        (100, 0, 9, 18),
        (1000, 2, 15, 30),
        (3000, 6, 27, 54),
        (6000, 13, 48, 96),
        (9000, 20, 69, 138),
        (12000, 27, 90, 180),
        (14000, 31, 102, 204),
    ]
    for dist_m, exp_cc, exp_slot, exp_ack in expected:
        cc = distance_to_coverage_class(dist_m)
        assert cc == exp_cc
        timings = coverage_class_to_timings(cc)
        assert timings["slot_time_us"] == exp_slot
        assert timings["ack_timeout_us"] == exp_ack


def test_per_cpe_schedule_regime_and_distance_scaling_laws() -> None:
    """Verify AP BE(regime) and CPE BE(d, regime) scaling across DL, Bidir, and UL."""
    # 1. Pure DL (R103..R107): AP BE=1900/3800, CPE BE=2100/4200
    dl_rec = compute_per_cpe_schedule(
        distance_m=6000,
        rx_mcs=8,
        tx_mcs=8,
        ul_dl_ratio=0.05,
        contract_tier_mbps=50.0,
        active_sector_cpes=1,
        active_flow_count=2,
    )
    assert dl_rec.traffic_regime == "unidir_dl"
    assert (dl_rec.ap_be_low_us, dl_rec.ap_be_high_us) == (1900, 3800)
    assert (dl_rec.cpe_be_low_us, dl_rec.cpe_be_high_us) == (2100, 4200)
    assert dl_rec.automatic_execution_allowed is False

    # 2. Single-CPE Bidir 2-flow at 9km (R97): AP BE=1800/3600, CPE BE=2100/4200
    r97_rec = compute_per_cpe_schedule(
        distance_m=9000,
        rx_mcs=8,
        tx_mcs=8,
        ul_dl_ratio=1.0,
        contract_tier_mbps=50.0,
        active_sector_cpes=1,
        active_flow_count=2,
    )
    assert r97_rec.traffic_regime == "bidir_2flow"
    assert (r97_rec.ap_be_low_us, r97_rec.ap_be_high_us) == (1800, 3600)
    assert (r97_rec.cpe_be_low_us, r97_rec.cpe_be_high_us) == (2100, 4200)

    # 3. Bidir 8-flow across 3..14km (R98..R102): AP BE=1550/3100, CPE BE=2100/4200
    r99_rec = compute_per_cpe_schedule(
        distance_m=6000,
        rx_mcs=8,
        tx_mcs=8,
        ul_dl_ratio=1.0,
        contract_tier_mbps=50.0,
        active_sector_cpes=1,
        active_flow_count=8,
    )
    assert r99_rec.traffic_regime == "bidir_mixed"
    assert (r99_rec.ap_be_low_us, r99_rec.ap_be_high_us) == (1550, 3100)
    assert (r99_rec.cpe_be_low_us, r99_rec.cpe_be_high_us) == (2100, 4200)

    # 4. Pure UL (R82 100m, R108 1000m, R109 3000m, and 9000m):
    # CPE BE scales monotonically to prevent long-slot turnaround TXQ starvation.
    ul_100m = compute_per_cpe_schedule(100, 8, 8, ul_dl_ratio=10.0)
    ul_1km = compute_per_cpe_schedule(1000, 8, 8, ul_dl_ratio=10.0)
    ul_3km = compute_per_cpe_schedule(3000, 8, 8, ul_dl_ratio=10.0)
    ul_9km = compute_per_cpe_schedule(9000, 5, 5, ul_dl_ratio=10.0)

    assert ul_100m.ap_be_low_us == 1520
    assert ul_100m.cpe_be_low_us == 2100
    assert ul_1km.cpe_be_low_us == 2650
    assert ul_3km.cpe_be_low_us == 3150
    assert ul_9km.cpe_be_low_us > ul_3km.cpe_be_low_us
    assert ul_1km.predicted_ul_dip_recovered_pct > 4.0
    assert ul_3km.predicted_ul_dip_recovered_pct > 6.0


def test_airtime_weight_monotonicity_and_sla_floor() -> None:
    """Verify near high-MCS stations receive higher airtime_weight than far low-MCS stations with >=144 SLA floor."""
    near_rec = compute_per_cpe_schedule(distance_m=500, rx_mcs=9, tx_mcs=9, ul_dl_ratio=1.0, contract_tier_mbps=80.0)
    mid_rec = compute_per_cpe_schedule(distance_m=4000, rx_mcs=7, tx_mcs=7, ul_dl_ratio=1.0, contract_tier_mbps=50.0)
    far_rec = compute_per_cpe_schedule(distance_m=14000, rx_mcs=3, tx_mcs=3, ul_dl_ratio=1.0, contract_tier_mbps=30.0)

    assert near_rec.ap_sta_airtime_weight > mid_rec.ap_sta_airtime_weight > far_rec.ap_sta_airtime_weight
    assert far_rec.ap_sta_airtime_weight >= 144
    assert near_rec.ap_sta_airtime_weight <= 512


def test_single_link_r97_r109_anchors_recovery() -> None:
    """Verify all 14 R82/R97..R109 anchors and adaptive UL recovery at 1km (R108) and 3km (R109)."""
    anchors = {a["anchor_id"]: a for a in evaluate_single_link_r97_r109_anchors()}
    assert len(anchors) == 14

    r108 = anchors["R108_unidir_ul_2flow_1km"]
    assert r108["static_asym_goodput_mbps"] < r108["stock_goodput_mbps"] * 0.93
    assert r108["adaptive_goodput_mbps"] >= r108["stock_goodput_mbps"] * 0.985
    assert r108["adaptive_p95_rtt_ms"] < 15.0

    r109 = anchors["R109_unidir_ul_2flow_3km"]
    assert r109["static_asym_goodput_mbps"] < r109["stock_goodput_mbps"] * 0.92
    assert r109["adaptive_goodput_mbps"] >= r109["stock_goodput_mbps"] * 0.985
    assert r109["adaptive_p95_rtt_ms"] < 16.0


def test_sector_scheduler_and_simpy_dominance() -> None:
    """Verify PerCPEDistanceAQLScheduler and SimPy mixed-distance policy dominance."""
    profiles = build_mixed_distance_sector_cpes(n_cpes=8, traffic_regime="bidir_mixed", hidden_node_fraction=0.50)
    scheduler = PerCPEDistanceAQLScheduler(hidden_node_risk=True)
    plan = scheduler.compute_sector_schedule(profiles, explicit_regime="bidir_mixed")

    assert plan["active_sector_cpes"] == 8
    assert plan["ap_radio_coverage_class"] == 31  # 14km farthest CPE
    assert plan["ap_radio_slot_time_us"] == 102
    assert plan["mean_near_airtime_weight"] > plan["mean_mid_airtime_weight"] > plan["mean_far_airtime_weight"]
    assert plan["automatic_execution_allowed"] is False

    runs = {
        p: run_mixed_distance_sector_sim(
            n_cpes=8,
            traffic_regime="bidir_mixed",
            hidden_node_fraction=0.50,
            policy=p,
            sim_duration_s=2.0,
        )
        for p in POLICIES
    }
    stock = runs["STOCK_UNWEIGHTED"]
    static = runs["STATIC_ASYM_AQL"]
    adaptive = runs["ADAPTIVE_DISTANCE_REGIME_AQL_PLUS_AIRTIME_WEIGHT"]

    assert adaptive["fmx_loss"] < static["fmx_loss"] < stock["fmx_loss"]
    assert adaptive["aggregate_goodput_mbps"] > static["aggregate_goodput_mbps"]
    assert adaptive["aggregate_goodput_mbps"] > stock["aggregate_goodput_mbps"]
    assert adaptive["p95_rtt_ms"] < 10.0
    assert stock["p95_rtt_ms"] > 35.0


def test_saved_mixed_distance_sweep_artifact_integrity() -> None:
    """Verify the saved JSON artifact exists, covers all 24 sector scenarios, and enforces safety flags."""
    artifact_path = Path("artifacts/ptmp_sim/mixed_distance_near_far_ptmp_sweep_20261024.json")
    assert artifact_path.exists()
    data = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert data["study_id"] == "FMX-STAGE12-MIXED-DISTANCE-NEAR-FAR-AQL-SCHEDULER-20261024"
    assert data["automatic_execution_allowed"] is False
    assert data["grid_summary"]["total_sector_scenarios"] == 24
    assert data["grid_summary"]["total_simpy_sector_runs"] == 72
    assert data["grid_summary"]["policy_win_counts"]["ADAPTIVE_DISTANCE_REGIME_AQL_PLUS_AIRTIME_WEIGHT"] == 24
