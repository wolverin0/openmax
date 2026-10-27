#!/usr/bin/env python3
"""Pytest suite for Stage 348A — PB-021 Per-PPDU 16-Pilot EVM & 12.5 ns Hardware Ranging Extractor."""

from __future__ import annotations

import json
import math

from tools.re.build_stage348a_pb021_ppdu_evm_ranging_extractor import (
    ARTIFACT_OUT,
    C_EXTRACTOR_HEADER_OUT,
    RX_PPDU_END_QCA988X_DWORDS,
    RX_PPDU_END_QCA988X_SIZE_BYTES,
    build_stage348a_report,
    dissect_rx_ppdu_end_qca988x,
    synthesize_rx_ppdu_end_qca988x,
)


def test_stage348a_struct_layout_and_report() -> None:
    report = build_stage348a_report()
    assert ARTIFACT_OUT.exists()
    assert C_EXTRACTOR_HEADER_OUT.exists()
    loaded = json.loads(ARTIFACT_OUT.read_text(encoding="utf-8"))
    assert loaded["stage"] == "348A"
    assert loaded["memory_master_claim_id"] == "mm-22d6"
    spec = loaded["struct_rx_ppdu_end_qca988x_specification"]
    assert spec["total_size_bytes"] == RX_PPDU_END_QCA988X_SIZE_BYTES == 84
    assert spec["total_dwords"] == RX_PPDU_END_QCA988X_DWORDS == 21
    assert math.isclose(spec["locationing_tick_ns"], 12.5, rel_tol=1e-6)
    assert math.isclose(spec["rtt_two_way_spatial_step_m"], 1.8737, rel_tol=1e-4)
    assert len(spec["dword_layout"]) == 21


def test_stage348a_binary_dissector_roundtrip() -> None:
    s0 = [-31] * 16
    s1 = [-25] * 16
    raw = synthesize_rx_ppdu_end_qca988x(
        stream0_pilot_evm_db=s0,
        stream1_pilot_evm_db=s1,
        tsf_timestamp=0xAABBCCDD,
        wb_timestamp_us=1000,
        locationing_timestamp=40,  # 40 * 12.5 ns = 500.0 ns
        peer_idx=12,
        ppdu_done=True,
    )
    assert len(raw) == 84
    parsed = dissect_rx_ppdu_end_qca988x(raw)
    assert parsed["evm_summary"]["stream0_mean_evm_db"] == -31.0
    assert parsed["evm_summary"]["stream1_mean_evm_db"] == -25.0
    assert parsed["evm_summary"]["stream_evm_delta_db"] == 6.0
    assert parsed["timestamps_and_ranging"]["locationing_timestamp_tick_80mhz"] == 40
    assert parsed["timestamps_and_ranging"]["fractional_time_ns"] == 500.0
    assert parsed["timestamps_and_ranging"]["composite_timestamp_ns"] == 1_000_500.0
    assert parsed["phy_and_mac_status"]["peer_idx"] == 12
    assert parsed["phy_and_mac_status"]["ppdu_done"] is True
