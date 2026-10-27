"""Unit tests for Stage 110A SimPy + Pymoo 4-Address WDS EAPOL-Key 2/4 Race & 37-Channel Scan Simulation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.research.stage110a_wds_eapol_convergence_sim import (
    AIROS8_CHANNEL_DWELL_MS,
    AIROS8_SCAN_CHANNEL_COUNT,
    AIROS8_SCAN_CYCLE_PERIOD_S,
    BEACON_INT_BOUNDS_TU,
    DEFAULT_OUT_JSON,
    EAPOL_RETRY_TIMEOUT_BOUNDS_MS,
    IE_FREE_WINDOW_BOUNDS_S,
    compute_beacon_airtime_overhead_pct,
    simulate_wds_eapol_convergence_simpy,
)


def test_stage110a_constants_and_beacon_airtime_monotonicity() -> None:
    """Verify exact airOS 8.7.11 37-channel scan constants and beacon airtime overhead scaling."""
    assert AIROS8_SCAN_CHANNEL_COUNT == 37
    assert AIROS8_SCAN_CYCLE_PERIOD_S == 37.0
    assert AIROS8_CHANNEL_DWELL_MS == 150.0
    assert BEACON_INT_BOUNDS_TU == (15, 100)
    assert IE_FREE_WINDOW_BOUNDS_S == (15.0, 90.0)
    assert EAPOL_RETRY_TIMEOUT_BOUNDS_MS == (20.0, 1000.0)

    oh_15 = compute_beacon_airtime_overhead_pct(beacon_int_tu=15, ie_free_window_s=40.0)
    oh_30 = compute_beacon_airtime_overhead_pct(beacon_int_tu=30, ie_free_window_s=40.0)
    oh_50 = compute_beacon_airtime_overhead_pct(beacon_int_tu=50, ie_free_window_s=40.0)
    oh_100 = compute_beacon_airtime_overhead_pct(beacon_int_tu=100, ie_free_window_s=40.0)

    assert oh_15 > oh_30 > oh_50 > oh_100 > 0.0
    assert 2.5 <= oh_15 <= 4.0
    assert 0.4 <= oh_100 <= 0.7

    with pytest.raises(ValueError):
        compute_beacon_airtime_overhead_pct(beacon_int_tu=10, ie_free_window_s=40.0)


def test_stage110a_simpy_wds_eapol_race_and_scan_convergence_physics() -> None:
    """Verify SimPy discrete-event physics across stock, aggressive 20ms, and Pareto-optimal regimes."""
    stock = simulate_wds_eapol_convergence_simpy(
        beacon_int_tu=100,
        ie_free_window_s=20.0,
        eapol_retry_timeout_ms=1000.0,
        n_trajectories=120,
        seed=11001,
    )
    knee = simulate_wds_eapol_convergence_simpy(
        beacon_int_tu=30,
        ie_free_window_s=40.0,
        eapol_retry_timeout_ms=80.0,
        n_trajectories=120,
        seed=11001,
    )
    too_fast_20ms = simulate_wds_eapol_convergence_simpy(
        beacon_int_tu=30,
        ie_free_window_s=40.0,
        eapol_retry_timeout_ms=20.0,
        n_trajectories=120,
        seed=11001,
    )

    assert stock.automatic_execution_allowed is False
    assert knee.automatic_execution_allowed is False

    # 1. Both experience the initial 4-address WDS AP_VLAN bind race on attempt 0
    assert stock.eapol_2of4_initial_race_drop_prob > 0.90
    assert knee.eapol_2of4_initial_race_drop_prob > 0.90

    # 2. Stock (1000 ms retry timeout + 20s < 37s IE-free window) triggers rescans and huge p50/p95/p99
    assert stock.eapol_timeout_rescan_rate_pct > 50.0
    assert knee.eapol_timeout_rescan_rate_pct == 0.0
    assert knee.convergence_p50_s < stock.convergence_p50_s * 0.55
    assert knee.convergence_p95_s < stock.convergence_p95_s * 0.50
    assert knee.convergence_p99_s < stock.convergence_p99_s * 0.50

    # 3. 20 ms retry fires before 34 ms WDS netdev bind -> slower p95 EAPOL completion than 80 ms sweet spot
    assert knee.eapol_handshake_p95_ms < too_fast_20ms.eapol_handshake_p95_ms


def test_stage110a_saved_artifact_and_5pillar_compliance() -> None:
    """Verify the generated Stage 110A JSON artifact, Pareto front, and 5-pillar research gate."""
    assert DEFAULT_OUT_JSON.exists(), f"Missing artifact: {DEFAULT_OUT_JSON}"
    payload = json.loads(DEFAULT_OUT_JSON.read_text(encoding="utf-8"))

    assert payload["stage"] == "110A"
    assert payload["automatic_execution_allowed"] is False
    assert payload["five_pillar_compliance"]["compliant"] is True

    constants = payload["hardware_and_protocol_constants"]
    assert constants["scan_channel_count"] == 37
    assert constants["scan_cycle_period_s"] == 37.0
    assert constants["channel_dwell_ms"] == 150.0

    pareto = payload["pymoo_nsga2_pareto_summary"]
    assert pareto["algorithm"] == "NSGA-II"
    assert pareto["unique_pareto_front_count"] >= 4
    assert pareto["hypervolume_3d"] > 0.0

    imp = payload["pareto_knee_improvement_vs_stock"]
    assert imp["convergence_p50_delta_pct"] < -45.0
    assert imp["convergence_p95_delta_pct"] < -50.0
    assert imp["convergence_p99_delta_pct"] < -50.0
    assert imp["eapol_handshake_p95_delta_pct"] < -85.0
