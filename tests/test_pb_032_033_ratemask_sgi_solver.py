#!/usr/bin/env python3
"""Unit tests for controller/pb_032_033_ratemask_sgi_solver.py (T-PB-GEM1-17)."""

from __future__ import annotations

import json

from controller.pb_032_033_ratemask_sgi_solver import (
    DEFAULT_OUTPUT_PATH,
    build_pb_032_033_qualification_report,
    compute_silicon_slot_and_ack_us,
    solve_pb033_micro_regime,
)


def test_silicon_slot_and_ack_equations_match_lap120_88mhz_registers() -> None:
    # coverage_class=0 -> slot=9us (792 cycles), ack=30us (2640 cycles)
    assert compute_silicon_slot_and_ack_us(0) == (9.0, 30.0)
    # coverage_class=13 (6000m) -> slot=48us (4224 cycles), ack=69us (6072 cycles)
    assert compute_silicon_slot_and_ack_us(13) == (48.0, 69.0)
    # coverage_class=31 (14000m) -> slot=102us (8976 cycles), ack=123us (10824 cycles)
    assert compute_silicon_slot_and_ack_us(31) == (102.0, 123.0)


def test_pb033_micro_regime_solver_switches_sgi_ampdu_and_rts_correctly() -> None:
    # 1km clean single-CPE -> SGI=True, HTT_AMPDU=64, MCS_CEIL=9, RTS=2347 (off)
    r_near = solve_pb033_micro_regime(
        distance_km=1.0,
        channel_width_mhz=20,
        cinr_db=32.0,
        delay_spread_rms_ns=45.0,
        active_ul_cpes=1,
        mac_retry_rate_pct=1.1,
    )
    assert r_near.sgi_400ns_enabled is True
    assert r_near.recommended_htt_max_ampdu == 64
    assert r_near.recommended_vht_mcs_ceiling == 9
    assert r_near.rts_threshold_bytes == 2347

    # 6km high multipath (135ns delay spread) -> SGI=False (LGI 800ns), HTT_AMPDU=32, MCS_CEIL=8
    r_multipath = solve_pb033_micro_regime(
        distance_km=6.0,
        channel_width_mhz=20,
        cinr_db=25.0,
        delay_spread_rms_ns=135.0,
        active_ul_cpes=1,
        mac_retry_rate_pct=2.2,
    )
    assert r_multipath.sgi_400ns_enabled is False
    assert r_multipath.recommended_htt_max_ampdu == 32
    assert r_multipath.rts_threshold_bytes == 2347

    # 14km 2-CPE contention -> SGI=False, HTT_AMPDU=16, MCS_CEIL=7, RTS=256
    r_far_cont = solve_pb033_micro_regime(
        distance_km=14.0,
        channel_width_mhz=20,
        cinr_db=19.5,
        delay_spread_rms_ns=160.0,
        active_ul_cpes=2,
        mac_retry_rate_pct=5.4,
    )
    assert r_far_cont.sgi_400ns_enabled is False
    assert r_far_cont.recommended_htt_max_ampdu == 16
    assert r_far_cont.recommended_vht_mcs_ceiling == 7
    assert r_far_cont.rts_threshold_bytes == 256


def test_pb_032_033_saved_qualification_artifact(tmp_path) -> None:
    source = tmp_path / "synthetic_silicon.json"
    source.write_text(json.dumps({"evidence_state": "SYNTHETIC",
        "pb_050_hardware_timing_and_clock_jitter": {"n160_paired_clock_benchmark": {
            "measured_clock_ratio_cycles_per_us_median": 88.0,
            "single_pcie_mmio_syscall_us_p50": 197.08,
            "single_pcie_mmio_syscall_us_p99": 588.24}},
        "pb_031_ldpc_ampdu_tpc_authority": {
            "PHY_BB_LDPC_CNTL1_0x29c04": "0xffffff55",
            "PHY_BB_LDPC_CNTL2_0x29c08": "0x00000000"}}))
    saved = build_pb_032_033_qualification_report(source)
    assert saved["paired_evidence_state"] == "SYNTHETIC"
    assert saved["physical_promotion_accepted"] is False
    assert saved["automatic_execution_allowed"] is False
    assert saved["live_silicon_provenance"]["PHY_BB_LDPC_CNTL1_0x29c04"] == "0xffffff55"
    assert saved["paired_ab_evaluation"]["verdict"] == "SYNTHETIC_PASS"
