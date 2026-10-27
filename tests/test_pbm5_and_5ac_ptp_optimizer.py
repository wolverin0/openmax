#!/usr/bin/env python3
"""Unit tests for PowerBeam M5 (XW.v6.3.2) & PowerBeam 5AC (WA.v8.7.25) PtP/PtMP Distance Optimizer."""

from __future__ import annotations

import json

import pytest

from tools.bench.pbm5_and_5ac_ptp_optimizer import (
    CANONICAL_DISTANCES_KM,
    DEFAULT_MATRIX_OUTPUT_PATH,
    build_pbm5_and_5ac_optimization_matrix,
    evaluate_no_ack_rate_pathology,
    recommend_wa_5ac_profile,
    recommend_xw_m5_profile,
)


def test_xw_m5_profile_adapts_ampduframes_ackdistance_and_commands_across_1_to_14km() -> None:
    p1 = recommend_xw_m5_profile(1.0, channel_width_mhz=20)
    p6 = recommend_xw_m5_profile(6.0, channel_width_mhz=20)
    p14 = recommend_xw_m5_profile(14.0, channel_width_mhz=20, is_ptmp_hidden_node=True)

    # Near/mid links use ampduframes=24; long links (10..14km) reduce to ampduframes=16
    assert p1.ampduframes == 24
    assert p6.ampduframes == 24
    assert p14.ampduframes == 16

    # no_ack_rate must remain 0 to protect TCP against L2 PER
    assert p1.ubnt_poll_no_ack_rate == 0
    assert p14.ubnt_poll_no_ack_rate == 0

    # PtP uses fixed_frame=0; hidden-node PtMP enables fixed_frame=1 (8ms)
    assert p1.ubnt_poll_fixed_frame == 0
    assert p14.ubnt_poll_fixed_frame == 1
    assert p14.tdd_frame_duration_ms == 8

    # ACK distance scales monotonically with 15% safety margin
    assert p1.ackdistance_m == 1500
    assert p6.ackdistance_m == 6900
    assert p14.ackdistance_m == 16100

    cmds = p6.render_xw_shell_commands()
    assert any("/proc/sys/dev/ubnt_poll/fixed_frame" in c for c in cmds)
    assert any("/proc/sys/dev/ubnt_poll/no_ack_rate" in c for c in cmds)
    assert any("iwpriv ath0 ampduframes 24" in c for c in cmds)
    assert any("sfq perturb 10 quantum 1514 limit 64" in c for c in cmds)


def test_no_ack_rate_pathology_is_strictly_rejected_by_gatekeeper() -> None:
    res = evaluate_no_ack_rate_pathology(channel_width_mhz=20, distance_km=6.0)
    assert res["gate_decision"]["verdict"] == "REJECT"
    assert res["gate_decision"]["p99_delta_pct"] > 100.0


def test_wa_5ac_and_xw_m5_matrix_promotes_all_5_distances_and_matches_saved_artifact() -> None:
    assert DEFAULT_MATRIX_OUTPUT_PATH.exists()
    saved = json.loads(DEFAULT_MATRIX_OUTPUT_PATH.read_text(encoding="utf-8"))
    assert saved["automatic_execution_allowed"] is False
    assert saved["distances_evaluated_km"] == list(CANONICAL_DISTANCES_KM)

    for row in saved["xw_m5_distance_matrix_20mhz"]:
        assert row["paired_ab_evaluation"]["gate_decision"]["verdict"] == "PROMOTE"
    for row in saved["wa_5ac_distance_matrix_20mhz"]:
        assert row["paired_ab_evaluation"]["gate_decision"]["verdict"] == "PROMOTE"

    for comp in saved["cross_generation_5ac_vs_m5_comparison"]:
        assert comp["wa_5ac_vs_xw_m5_gain_pct"] > 50.0
        assert comp["wa_5ac_optimized_p99_ms"] < comp["xw_m5_optimized_p99_ms"]


def test_invalid_channel_width_or_distance_rejected() -> None:
    with pytest.raises(ValueError):
        recommend_xw_m5_profile(6.0, channel_width_mhz=15)
    with pytest.raises(ValueError):
        recommend_wa_5ac_profile(0.0, channel_width_mhz=20)
