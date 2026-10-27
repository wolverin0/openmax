"""Tests for Phase 0 Workstream D: Paired A/B/A/B Gatekeeper, Lexicographic Hierarchy, and A/A Null Replay."""

from __future__ import annotations

import pytest

from analysis.regression_gate.gatekeeper import (
    RegressionGatekeeper,
    RunMetrics,
    build_paired_blocks,
    run_aa_null_replay_validation,
)


def _make_paired_runs(
    n_blocks: int = 6,
    base_gp: float = 80.0,
    cand_gp: float = 90.0,
    base_p95: float = 8.0,
    cand_p95: float = 8.2,
    base_p99: float = 14.0,
    cand_p99: float = 14.2,
    base_fair: float = 0.96,
    cand_fair: float = 0.96,
    width_mhz: int = 20,
) -> list[RunMetrics]:
    runs: list[RunMetrics] = []
    for k in range(n_blocks):
        jitter = (k % 3 - 1) * 0.4
        runs.append(
            RunMetrics(
                run_id=f"A_{k}",
                arm="A",
                goodput_mbps=base_gp + jitter,
                p95_lat_ms=base_p95,
                p99_lat_ms=base_p99,
                loss_pct=0.2,
                jain_fairness=base_fair,
                channel_width_mhz=width_mhz,
                block_index=k,
                worst_peer_goodput_mbps=20.0,
            )
        )
        runs.append(
            RunMetrics(
                run_id=f"B_{k}",
                arm="B",
                goodput_mbps=cand_gp + jitter,
                p95_lat_ms=cand_p95,
                p99_lat_ms=cand_p99,
                loss_pct=0.2,
                jain_fairness=cand_fair,
                channel_width_mhz=width_mhz,
                block_index=k,
                worst_peer_goodput_mbps=22.0,
            )
        )
    return runs


def test_hard_safety_gates_checked_first() -> None:
    gk = RegressionGatekeeper()
    runs = _make_paired_runs(n_blocks=4)
    runs[1].firmware_resets = 1
    decision = gk.evaluate_paired(runs)
    assert decision.verdict == "REJECT"
    assert "firmware reset" in decision.rationale.lower()


def test_full_lexicographic_hierarchy_p99_p95_fairness_goodput_per_mhz() -> None:
    gk = RegressionGatekeeper(
        max_p99_regression_pct=10.0,
        max_p95_regression_pct=10.0,
        max_fairness_drop_pct=5.0,
        min_goodput_gain_pct=5.0,
    )

    # 1. p99 regression rejects even with strong goodput gain
    runs_p99_bad = _make_paired_runs(n_blocks=6, base_p99=10.0, cand_p99=12.5)
    dec_p99 = gk.evaluate_paired(runs_p99_bad)
    assert dec_p99.verdict == "REJECT"
    assert "p99" in dec_p99.summary.lower()

    # 2. p95 regression rejects even when p99 is within bounds
    runs_p95_bad = _make_paired_runs(n_blocks=6, base_p95=8.0, cand_p95=9.5, base_p99=15.0, cand_p99=15.2)
    dec_p95 = gk.evaluate_paired(runs_p95_bad)
    assert dec_p95.verdict == "REJECT"
    assert "p95" in dec_p95.summary.lower()

    # 3. Fairness drop rejects even when p99 and p95 are clean
    runs_fair_bad = _make_paired_runs(n_blocks=6, base_fair=0.95, cand_fair=0.85)
    dec_fair = gk.evaluate_paired(runs_fair_bad)
    assert dec_fair.verdict == "REJECT"
    assert "fairness" in dec_fair.summary.lower()

    # 4. Insufficient goodput_per_mhz gain rejects
    runs_low_gain = _make_paired_runs(n_blocks=6, base_gp=80.0, cand_gp=82.0)
    dec_gain = gk.evaluate_paired(runs_low_gain)
    assert dec_gain.verdict == "REJECT"
    assert "throughput" in dec_gain.summary.lower()


def test_n2_never_promotes_and_distinguishes_keep_for_replication_vs_promote() -> None:
    gk = RegressionGatekeeper(min_blocks_for_keep=5, min_blocks_for_promote=6)

    # N=2 blocks cannot be promoted under strict 4-state evaluation
    runs_n2 = _make_paired_runs(n_blocks=2, base_gp=80.0, cand_gp=95.0)
    dec_n2 = gk.evaluate_paired(runs_n2, holdout_replicated=True)
    assert dec_n2.verdict == "INCONCLUSIVE"
    assert dec_n2.promotion_stage == "INCONCLUSIVE"

    # N=5 blocks without holdout replication -> KEEP_FOR_REPLICATION (two-sided exact sign-flip p = 2/32 = 0.0625; N=6 gives 2/64 = 0.03125 <= 0.05)
    runs_n6_no_holdout = _make_paired_runs(n_blocks=6, base_gp=80.0, cand_gp=92.0)
    dec_keep_rep = gk.evaluate_paired(runs_n6_no_holdout, holdout_replicated=False)
    assert dec_keep_rep.verdict == "KEEP_FOR_REPLICATION"
    assert dec_keep_rep.promotion_stage == "KEEP_FOR_REPLICATION"
    assert dec_keep_rep.ci_95_goodput_per_mhz_delta_pct[0] > 0.0

    # N=6 blocks WITH holdout replication -> PROMOTE
    dec_promote = gk.evaluate_paired(runs_n6_no_holdout, holdout_replicated=True)
    assert dec_promote.verdict == "PROMOTE"
    assert dec_promote.promotion_stage == "PROMOTE"


def test_temporal_drift_detection_marks_inconclusive() -> None:
    gk = RegressionGatekeeper(max_drift_pct=15.0)
    runs = _make_paired_runs(n_blocks=6, base_gp=80.0, cand_gp=92.0)
    # Inject strong non-stationary drift into the last baseline block
    for r in runs:
        if r.arm == "A" and r.block_index == 5:
            r.goodput_mbps = 55.0
            r.goodput_per_mhz = 55.0 / 20.0
    dec = gk.evaluate_paired(runs, holdout_replicated=True)
    assert dec.verdict == "INCONCLUSIVE"
    assert dec.drift_detected is True


def test_mismatched_channel_width_in_paired_block_raises() -> None:
    runs = _make_paired_runs(n_blocks=2)
    runs[1].channel_width_mhz = 40
    with pytest.raises(ValueError, match="channel_width_mhz mismatch"):
        build_paired_blocks(runs)


def test_aa_null_replay_false_positive_rate_bounded() -> None:
    baseline_pool = [
        RunMetrics(
            run_id=f"base_{i}",
            arm="A",
            goodput_mbps=82.0 + (i % 5 - 2) * 1.2,
            p95_lat_ms=7.8 + (i % 3) * 0.2,
            p99_lat_ms=13.5 + (i % 4) * 0.3,
            loss_pct=0.1,
            jain_fairness=0.96,
            channel_width_mhz=20,
            worst_peer_goodput_mbps=19.5,
        )
        for i in range(20)
    ]
    gk = RegressionGatekeeper(alpha=0.05, min_goodput_gain_pct=5.0)
    report = run_aa_null_replay_validation(
        baseline_pool=baseline_pool,
        gatekeeper=gk,
        pairs_per_trial=6,
        num_trials=300,
        seed=20261024,
    )
    assert report["passes_null_calibration"] is True
    assert report["false_positive_rate"] <= 0.05
