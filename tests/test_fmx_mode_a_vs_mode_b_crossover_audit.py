"""
Unit & Physical Invariant Tests for Mode A vs. Mode B Crossover Boundary Audit
==============================================================================
Verifies:
  1. Exact mac80211 / ath10k coverage-class, slot-time, ACK/CTS-timeout, and
     hidden-node RTS vulnerability window laws across d = 1..14 km.
  2. Exact alignment with Stage 12 R60-R80 declared distance timing anchors.
  3. Monotonicity of Bianchi + hidden-node RTS collision probability p_c(N, d, alpha_HN).
  4. Monotonicity of critical crossover station counts N*(d) across d = 1..14 km
     and across hidden-node regimes (Regime 3 <= Regime 2 <= Regime 1).
  5. Completeness and schema integrity of the generated JSON audit artifact.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis.simulation.fmx_mode_a_vs_mode_b_crossover_audit import (
    REGIMES,
    STAGE12_EMPIRICAL_ANCHORS,
    compute_distance_timing,
    evaluate_point,
    run_full_audit,
    solve_mode_a_bianchi_hidden_node,
)


def test_distance_timing_monotonicity_and_stage12_anchors() -> None:
    """Verify strict monotonicity of coverage class, slot time, ACK timeout, and T_vuln across 1..14 km."""
    distances = [1.0, 1.5, 2.0, 3.0, 4.0, 4.5, 5.0, 6.0, 7.0, 7.5, 8.0, 9.0, 10.0, 10.5, 11.0, 12.0, 13.0, 13.5, 14.0]
    timings = [compute_distance_timing(d) for d in distances]

    for prev, curr in zip(timings, timings[1:]):
        assert curr.d_km > prev.d_km
        assert curr.coverage_class > prev.coverage_class, f"Coverage class did not strictly increase from {prev.d_km} to {curr.d_km}"
        assert curr.slot_time_us > prev.slot_time_us
        assert curr.ack_cts_timeout_us > prev.ack_cts_timeout_us
        assert curr.rts_vuln_window_us > prev.rts_vuln_window_us
        assert curr.slot_time_us == pytest.approx(9.0 + 3.0 * curr.coverage_class)
        assert curr.ack_cts_timeout_us == pytest.approx(18.0 + 6.0 * curr.coverage_class)

    # Check exact Stage 12 anchor matches within 1..14 km
    for d_anchor in [1.5, 3.0, 4.5, 6.0, 7.5, 9.0, 10.5, 12.0, 13.5]:
        t = compute_distance_timing(d_anchor)
        exp = STAGE12_EMPIRICAL_ANCHORS[d_anchor]
        assert t.coverage_class == int(exp["class"])
        assert t.slot_time_us == pytest.approx(exp["slot_us"])
        assert t.ack_cts_timeout_us == pytest.approx(exp["ack_us"])


def test_bianchi_hidden_node_collision_monotonicity() -> None:
    """Verify that RTS collision probability increases monotonically with N_eff and alpha_HN."""
    timing = compute_distance_timing(6.0)
    prev_p = -1.0
    for n_eff in [1.0, 2.0, 4.0, 8.0, 16.0, 32.0]:
        _, p_coll, mean_slots = solve_mode_a_bianchi_hidden_node(n_eff, timing, alpha_hn=0.5)
        assert 0.0 <= p_coll < 1.0
        assert p_coll > prev_p
        assert mean_slots >= 7.5
        prev_p = p_coll

    # Verify increasing alpha_HN (hidden-node pair fraction) strictly increases collision probability
    _, p_low, _ = solve_mode_a_bianchi_hidden_node(6.0, timing, alpha_hn=0.15)
    _, p_mid, _ = solve_mode_a_bianchi_hidden_node(6.0, timing, alpha_hn=0.50)
    _, p_high, _ = solve_mode_a_bianchi_hidden_node(6.0, timing, alpha_hn=1.00)
    assert p_low < p_mid < p_high


def test_mode_a_vs_mode_b_boundary_regimes_and_monotonicity() -> None:
    """
    Verify that:
      - At small N and short distance (e.g. N=2, d=1.5 km), Mode A beats Mode B on UL goodput,
        interactive AC_VO p95 latency, and composite FMX score across all regimes.
      - At large N and long distance (e.g. N=24..32, d=12..14 km), Mode B beats Mode A on
        UL goodput, total goodput, and composite FMX score across all regimes.
      - Crossover N*(d) is monotone non-increasing with distance d across 1..14 km.
    """
    for regime_id, regime in REGIMES.items():
        pt_small = evaluate_point(2, 1.5, regime)
        assert pt_small.winner_ul_goodput == "Mode A", f"Expected Mode A UL win at N=2, d=1.5km in {regime_id}"
        assert pt_small.winner_interactive_p95_rtt == "Mode A", f"Expected Mode A latency win at N=2, d=1.5km in {regime_id}"
        assert pt_small.winner_fmx_composite == "Mode A", f"Expected Mode A FMX win at N=2, d=1.5km in {regime_id}"

        pt_large = evaluate_point(32, 14.0, regime)
        assert pt_large.winner_ul_goodput == "Mode B", f"Expected Mode B UL win at N=32, d=14km in {regime_id}"
        assert pt_large.winner_total_goodput == "Mode B", f"Expected Mode B Total GP win at N=32, d=14km in {regime_id}"
        assert pt_large.winner_fmx_composite == "Mode B", f"Expected Mode B FMX win at N=32, d=14km in {regime_id}"
        assert pt_large.winner_interactive_p95_rtt == "Mode B", f"Expected Mode B p95 win at N=32, d=14km in {regime_id}"

    result = run_full_audit()
    for regime_id in REGIMES:
        rows = result["regimes"][regime_id]["crossover_by_distance"]
        for metric_key in ["n_star_ul_goodput", "n_star_total_goodput", "n_star_fmx_composite", "n_star_interactive_p95"]:
            vals = [r[metric_key] if r[metric_key] is not None else 999 for r in rows]
            for prev_v, curr_v in zip(vals, vals[1:]):
                assert curr_v <= prev_v, (
                    f"Non-monotonic crossover {metric_key} in {regime_id}: {vals}"
                )

    # Verify ordering across regimes at every distance: N*(R3) <= N*(R2) <= N*(R1)
    r3_rows = result["regimes"]["regime_3_saturated_full_hn"]["crossover_by_distance"]
    r2_rows = result["regimes"]["regime_2_typical_wisp_sector"]["crossover_by_distance"]
    r1_rows = result["regimes"]["regime_1_low_hn_narrow_sector"]["crossover_by_distance"]
    for r3, r2, r1 in zip(r3_rows, r2_rows, r1_rows):
        for metric_key in ["n_star_ul_goodput", "n_star_total_goodput", "n_star_fmx_composite", "n_star_interactive_p95"]:
            v3 = r3[metric_key] or 999
            v2 = r2[metric_key] or 999
            v1 = r1[metric_key] or 999
            assert v3 <= v2 <= v1, f"Regime ordering violated at d={r3['d_km']} for {metric_key}: {v3}, {v2}, {v1}"


def test_saved_artifact_schema_and_completeness() -> None:
    """Verify the saved JSON artifact exists and contains all 31 x 19 x 3 = 1,767 evaluations."""
    artifact_path = Path("artifacts/autoresearch/mode_a_vs_mode_b_crossover_20261024.json")
    assert artifact_path.exists(), "Expected mode_a_vs_mode_b_crossover_20261024.json to exist"
    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert data["audit_id"] == "FMX-STAGE12-MODE-A-VS-MODE-B-CROSSOVER-20261024"
    assert data["scope"]["n_cpes_min"] == 2
    assert data["scope"]["n_cpes_max"] == 32
    assert len(data["distance_timing_table"]) == 19
    for regime_id in REGIMES:
        regime_data = data["regimes"][regime_id]
        assert len(regime_data["crossover_by_distance"]) == 19
        assert len(regime_data["grid"]) == 31 * 19
