"""Deterministic tests for the Stage 12 Multi-CPE PtMP Hidden-Node & TDMA vs CSMA/CA Simulator
and the PtMP Operating Mode Selector."""

from __future__ import annotations

import json
import pytest

from controller.ptmp_mode_selector import (
    PtMPModeSelector,
    select_ptmp_operating_mode,
)
from tools.sim.fmx_ptmp_hidden_node_tdma_vs_csma_sim import (
    ALL_MODES,
    DEFAULT_SWEEP_OUTPUT,
    MODE_A_CSMA_AQL_ONLY,
    MODE_A_PLUS_RTS_CTS_256B,
    MODE_B_AIRMAX_TDMA_HYBRID,
    MODE_STOCK_CSMA_UNPROTECTED,
    PtMPSimConfig,
    SEED_DEFAULT,
    SWEEP_D_VALUES,
    SWEEP_H_VALUES,
    SWEEP_N_VALUES,
    run_full_n2_to_n32_sweep,
    simulate_ptmp_sector,
    simulate_stage7_3station_benchmark,
    timing_for_distance_km,
)


def test_stage7_hardware_calibration_anchor():
    """Verify SimPy 3-station hidden-node benchmark reproduces Stage 7 physical measurements."""
    rts_off = simulate_stage7_3station_benchmark(rts_cts_256b=False, ac_vo_bypass=False, seed=SEED_DEFAULT)
    rts_on = simulate_stage7_3station_benchmark(rts_cts_256b=True, ac_vo_bypass=True, seed=SEED_DEFAULT)

    assert rts_off["alone_ul_sum_mbps"] == pytest.approx(243.92, abs=0.05)
    assert rts_off["total_sector_ul_mbps"] == pytest.approx(150.40, abs=0.25)
    assert rts_off["per_station_ul_mbps"]["sxt"] == pytest.approx(1.97, abs=0.10)
    assert rts_off["sxt_loaded_p50_rtt_ms"] == pytest.approx(143.0, abs=2.0)

    assert rts_on["total_sector_ul_mbps"] == pytest.approx(178.17, abs=0.25)
    assert rts_on["per_station_ul_mbps"]["sxt"] == pytest.approx(6.03, abs=0.10)
    assert rts_on["sxt_loaded_p50_rtt_ms"] == pytest.approx(6.80, abs=0.35)

    gain_pct = (rts_on["total_sector_ul_mbps"] - rts_off["total_sector_ul_mbps"]) / rts_off["total_sector_ul_mbps"] * 100.0
    assert gain_pct == pytest.approx(18.46, abs=0.3)

    sxt_recovery = rts_on["per_station_ul_mbps"]["sxt"] / rts_off["per_station_ul_mbps"]["sxt"]
    assert sxt_recovery == pytest.approx(3.06, abs=0.1)


def test_distance_timing_table_and_interpolation():
    """Verify exact coverage_class, slot_time_us, and ack_timeout_us at R98..R102 anchors and interpolated km."""
    t3 = timing_for_distance_km(3.0)
    assert t3["coverage_class"] == 6
    assert t3["slot_time_us"] == 27
    assert t3["ack_timeout_us"] == 54

    t6 = timing_for_distance_km(6.0)
    assert t6["coverage_class"] == 13
    assert t6["slot_time_us"] == 48
    assert t6["ack_timeout_us"] == 96

    t9 = timing_for_distance_km(9.0)
    assert t9["coverage_class"] == 20
    assert t9["slot_time_us"] == 69
    assert t9["ack_timeout_us"] == 138

    t12 = timing_for_distance_km(12.0)
    assert t12["coverage_class"] == 27
    assert t12["slot_time_us"] == 90
    assert t12["ack_timeout_us"] == 180

    t14 = timing_for_distance_km(14.0)
    assert t14["coverage_class"] == 31
    assert t14["slot_time_us"] == 102
    assert t14["ack_timeout_us"] == 204

    t_interp = timing_for_distance_km(4.5)
    assert 6 < t_interp["coverage_class"] < 13
    assert t_interp["ack_timeout_us"] == 2 * t_interp["slot_time_us"]

    with pytest.raises(ValueError):
        timing_for_distance_km(0.0)
    with pytest.raises(ValueError):
        timing_for_distance_km(45.0)


def test_single_cpe_and_multi_cpe_physics_ordering():
    """Verify physical ordering across the 4 modes at N=1, N=4, and N=16."""
    # 1) At N=1, d=3.0km, h=0.0: MODE_A_CSMA_AQL_ONLY beats RTS/CTS and TDMA (no overhead needed)
    m_aql_1 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=1, hidden_node_fraction=0.0, distance_km=3.0, mode=MODE_A_CSMA_AQL_ONLY))
    m_rts_1 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=1, hidden_node_fraction=0.0, distance_km=3.0, mode=MODE_A_PLUS_RTS_CTS_256B))
    m_tdma_1 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=1, hidden_node_fraction=0.0, distance_km=3.0, mode=MODE_B_AIRMAX_TDMA_HYBRID))
    m_stock_1 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=1, hidden_node_fraction=0.0, distance_km=3.0, mode=MODE_STOCK_CSMA_UNPROTECTED))

    assert m_aql_1["metrics"]["aggregate_ul_goodput_mbps"] > m_rts_1["metrics"]["aggregate_ul_goodput_mbps"]
    assert m_aql_1["metrics"]["aggregate_ul_goodput_mbps"] > m_tdma_1["metrics"]["aggregate_ul_goodput_mbps"]
    assert m_aql_1["metrics"]["p95_rtt_ms"] < m_stock_1["metrics"]["p95_rtt_ms"] * 0.25

    # 2) At N=4, d=3.0km, h=0.50: MODE_A_PLUS_RTS_CTS_256B beats unprotected CSMA and TDMA
    m_stock_4 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=4, hidden_node_fraction=0.50, distance_km=3.0, mode=MODE_STOCK_CSMA_UNPROTECTED))
    m_aql_4 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=4, hidden_node_fraction=0.50, distance_km=3.0, mode=MODE_A_CSMA_AQL_ONLY))
    m_rts_4 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=4, hidden_node_fraction=0.50, distance_km=3.0, mode=MODE_A_PLUS_RTS_CTS_256B))
    m_tdma_4 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=4, hidden_node_fraction=0.50, distance_km=3.0, mode=MODE_B_AIRMAX_TDMA_HYBRID))

    assert m_rts_4["metrics"]["aggregate_ul_goodput_mbps"] > m_aql_4["metrics"]["aggregate_ul_goodput_mbps"] * 1.8
    assert m_rts_4["metrics"]["aggregate_ul_goodput_mbps"] > m_stock_4["metrics"]["aggregate_ul_goodput_mbps"] * 2.5
    assert m_rts_4["metrics"]["aggregate_ul_goodput_mbps"] > m_tdma_4["metrics"]["aggregate_ul_goodput_mbps"]
    assert m_rts_4["metrics"]["qoe_score"] > m_tdma_4["metrics"]["qoe_score"]

    # 3) At N=16, d=6.0km, h=0.75: MODE_B_AIRMAX_TDMA_HYBRID beats all CSMA/RTS modes
    m_stock_16 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=16, hidden_node_fraction=0.75, distance_km=6.0, mode=MODE_STOCK_CSMA_UNPROTECTED))
    m_aql_16 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=16, hidden_node_fraction=0.75, distance_km=6.0, mode=MODE_A_CSMA_AQL_ONLY))
    m_rts_16 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=16, hidden_node_fraction=0.75, distance_km=6.0, mode=MODE_A_PLUS_RTS_CTS_256B))
    m_tdma_16 = simulate_ptmp_sector(PtMPSimConfig(n_cpes=16, hidden_node_fraction=0.75, distance_km=6.0, mode=MODE_B_AIRMAX_TDMA_HYBRID))

    assert m_tdma_16["metrics"]["aggregate_ul_goodput_mbps"] > m_rts_16["metrics"]["aggregate_ul_goodput_mbps"] * 1.35
    assert m_tdma_16["metrics"]["aggregate_ul_goodput_mbps"] > m_aql_16["metrics"]["aggregate_ul_goodput_mbps"] * 4.0
    assert m_tdma_16["metrics"]["jain_fairness"] > 0.95
    assert m_tdma_16["metrics"]["p95_rtt_ms"] < m_rts_16["metrics"]["p95_rtt_ms"] * 0.65
    assert m_tdma_16["metrics"]["p95_rtt_ms"] < m_stock_16["metrics"]["p95_rtt_ms"] * 0.10


def test_ptmp_mode_selector_policy_decisions():
    """Verify deterministic policy selector across single-CPE, hidden-node, dense, and legacy-vendor regimes."""
    selector = PtMPModeSelector(seed=SEED_DEFAULT)

    # Case 1: Single active uploader -> MODE_A_CSMA_AQL_ONLY
    r1 = selector.select(active_uploading_cpes=1, hidden_node_fraction=0.50, max_distance_km=3.0, has_legacy_m5_or_mikrotik_cpes=False)
    assert r1["selected_mode"] == MODE_A_CSMA_AQL_ONLY
    assert r1["automatic_execution_allowed"] is False

    # Case 2: 4 active uploaders, h=0.0 (all mutually visible) -> MODE_A_CSMA_AQL_ONLY
    r2 = selector.select(active_uploading_cpes=4, hidden_node_fraction=0.0, max_distance_km=3.0, has_legacy_m5_or_mikrotik_cpes=False)
    assert r2["selected_mode"] == MODE_A_CSMA_AQL_ONLY

    # Case 3: 4 active uploaders, h=0.50 (hidden nodes), homogeneous AC -> MODE_A_PLUS_RTS_CTS_256B
    r3 = selector.select(active_uploading_cpes=4, hidden_node_fraction=0.50, max_distance_km=3.0, has_legacy_m5_or_mikrotik_cpes=False)
    assert r3["selected_mode"] == MODE_A_PLUS_RTS_CTS_256B
    assert r3["gain_vs_stock_csma_ul_pct"] > 150.0

    # Case 4: 12 active uploaders, h=0.50, homogeneous AC -> MODE_B_AIRMAX_TDMA_HYBRID
    r4 = selector.select(active_uploading_cpes=12, hidden_node_fraction=0.50, max_distance_km=6.0, has_legacy_m5_or_mikrotik_cpes=False)
    assert r4["selected_mode"] == MODE_B_AIRMAX_TDMA_HYBRID
    assert r4["predicted_jain_fairness"] > 0.96
    assert r4["rtt_p95_cut_vs_stock_csma_multiplier"] > 10.0

    # Case 5: 12 active uploaders, h=0.50, but WITH legacy M5 or MikroTik CPEs -> MODE_A_PLUS_RTS_CTS_256B
    r5 = selector.select(active_uploading_cpes=12, hidden_node_fraction=0.50, max_distance_km=6.0, has_legacy_m5_or_mikrotik_cpes=True)
    assert r5["selected_mode"] == MODE_A_PLUS_RTS_CTS_256B
    assert r5["candidate_modes"][MODE_B_AIRMAX_TDMA_HYBRID]["eligible"] is False
    assert "MikroTik" in r5["candidate_modes"][MODE_B_AIRMAX_TDMA_HYBRID]["ineligible_reason"]


def test_ptmp_mode_selector_input_validation():
    """Verify strict validation of selector and simulator inputs."""
    with pytest.raises(ValueError):
        select_ptmp_operating_mode(0, 0.5, 3.0, False)
    with pytest.raises(ValueError):
        select_ptmp_operating_mode(10, -0.1, 3.0, False)
    with pytest.raises(ValueError):
        select_ptmp_operating_mode(10, 1.2, 3.0, False)
    with pytest.raises(ValueError):
        select_ptmp_operating_mode(10, 0.5, 0.0, False)
    with pytest.raises(ValueError):
        select_ptmp_operating_mode(10, 0.5, 3.0, "yes")  # type: ignore[arg-type]


def test_saved_sweep_artifact_integrity_and_reproducibility():
    """Verify the saved JSON artifact matches the 300-point grid schema and deterministic seed replay."""
    assert DEFAULT_SWEEP_OUTPUT.exists(), f"Missing artifact {DEFAULT_SWEEP_OUTPUT}"
    saved = json.loads(DEFAULT_SWEEP_OUTPUT.read_text(encoding="utf-8"))

    assert saved["schema_version"] == 1
    assert saved["seed"] == SEED_DEFAULT
    assert saved["evidence_boundary"]["automatic_execution_allowed"] is False
    assert saved["sweep_dimensions"]["n_cpes"] == list(SWEEP_N_VALUES)
    assert saved["sweep_dimensions"]["hidden_node_fraction"] == list(SWEEP_H_VALUES)
    assert saved["sweep_dimensions"]["distance_km"] == list(SWEEP_D_VALUES)
    assert saved["sweep_dimensions"]["modes"] == list(ALL_MODES)
    assert saved["sweep_dimensions"]["total_grid_points"] == 300
    assert saved["sweep_dimensions"]["total_mode_evaluations"] == 1200
    assert len(saved["grid_results"]) == 300

    wins = saved["mode_win_counts_across_300_grid_points"]
    assert wins[MODE_STOCK_CSMA_UNPROTECTED] == 0
    assert wins[MODE_A_CSMA_AQL_ONLY] > 0
    assert wins[MODE_A_PLUS_RTS_CTS_256B] > 0
    assert wins[MODE_B_AIRMAX_TDMA_HYBRID] > 0
    assert sum(wins.values()) == 300

    # Verify deterministic replay matches saved JSON byte-for-byte
    replayed = run_full_n2_to_n32_sweep(seed=SEED_DEFAULT)
    assert replayed == saved
