"""Unit tests for the FuturaMAX Karpathy-style autoresearch harness."""

from __future__ import annotations

from pathlib import Path
import pytest

from orchestration.autoresearch import (
    AutoresearchDecision,
    BenchmarkObservation,
    FmxAutoresearchHarness,
    MutableWirelessPolicy,
    ObjectiveConfig,
    compute_fmx_objective,
    compute_pareto_frontier,
)


def test_policy_bounds_validation() -> None:
    valid = MutableWirelessPolicy(
        policy_id="p1",
        description="AQL 4096 KB + CoDel 4ms",
        aql_txq_limit_ac_be_kb=4096,
        aql_threshold_kb=4096,
        codel_target_ms=4.0,
        codel_interval_ms=80.0,
        vht_mcs_max_index=9,
    )
    assert valid.validate_bounds() == []

    invalid = MutableWirelessPolicy(
        policy_id="bad_11ax",
        description="Invalid MCS 11 and AQL 64 KB",
        aql_txq_limit_ac_be_kb=64,
        vht_mcs_max_index=11,
    )
    errors = invalid.validate_bounds()
    assert len(errors) == 2
    assert any("aql_txq_limit_ac_be_kb" in e for e in errors)
    assert any("vht_mcs_max_index" in e for e in errors)


def test_compute_fmx_objective_keep_discard_crash() -> None:
    cfg = ObjectiveConfig(
        target_goodput_mbps=80.0,
        baseline_rtt_ms=5.0,
        rtt_budget_ms=25.0,
        max_p99_rtt_ms=100.0,
        max_packet_loss_pct=2.0,
        min_improvement_delta=0.005,
    )

    # 1. Baseline observation -> KEEP
    base_obs = BenchmarkObservation(
        goodput_rx_mbps=55.0,
        p50_rtt_ms=8.0,
        p95_rtt_ms=28.0,
        p99_rtt_ms=45.0,
        packet_loss_pct=0.0,
        jain_fairness=0.92,
        retry_rate=0.06,
    )
    base_eval = compute_fmx_objective(base_obs, cfg, best_fmx_loss=None)
    assert base_eval.decision == AutoresearchDecision.KEEP
    assert not base_eval.disqualified

    # 2. Improved latency + goodput (AQL + FQ-CoDel tuned) -> KEEP
    better_obs = BenchmarkObservation(
        goodput_rx_mbps=60.0,
        p50_rtt_ms=6.0,
        p95_rtt_ms=14.0,
        p99_rtt_ms=22.0,
        packet_loss_pct=0.0,
        jain_fairness=0.97,
        retry_rate=0.04,
    )
    better_eval = compute_fmx_objective(better_obs, cfg, best_fmx_loss=base_eval.fmx_loss)
    assert better_eval.decision == AutoresearchDecision.KEEP
    assert better_eval.fmx_loss < base_eval.fmx_loss

    # 3. Higher goodput but p99 latency blows past max_p99_rtt_ms gate -> DISCARD
    bloat_obs = BenchmarkObservation(
        goodput_rx_mbps=75.0,
        p50_rtt_ms=25.0,
        p95_rtt_ms=85.0,
        p99_rtt_ms=140.0,
        packet_loss_pct=0.5,
        jain_fairness=0.80,
        retry_rate=0.10,
    )
    bloat_eval = compute_fmx_objective(bloat_obs, cfg, best_fmx_loss=better_eval.fmx_loss)
    assert bloat_eval.decision == AutoresearchDecision.DISCARD
    assert bloat_eval.disqualified
    assert "p99 RTT" in bloat_eval.reason

    # 4. Station drop or unverified restoration -> CRASH
    drop_obs = BenchmarkObservation(
        goodput_rx_mbps=65.0,
        p50_rtt_ms=6.0,
        p95_rtt_ms=12.0,
        p99_rtt_ms=18.0,
        station_drops=1,
    )
    drop_eval = compute_fmx_objective(drop_obs, cfg, best_fmx_loss=better_eval.fmx_loss)
    assert drop_eval.decision == AutoresearchDecision.CRASH
    assert drop_eval.disqualified


def test_harness_loop_and_results_tsv(tmp_path: Path) -> None:
    tsv_file = tmp_path / "results.tsv"
    harness = FmxAutoresearchHarness(tsv_path=tsv_file)

    # Iteration 1: Baseline (KEEP)
    p_base = MutableWirelessPolicy(
        policy_id="base_24m",
        description="baseline AQL 24MB default",
        aql_txq_limit_ac_be_kb=24000,
        complexity_cost=2,
    )
    e1 = harness.run_iteration(
        "a1b2c3d",
        p_base,
        lambda _: BenchmarkObservation(
            goodput_rx_mbps=52.0,
            p50_rtt_ms=10.0,
            p95_rtt_ms=35.0,
            p99_rtt_ms=55.0,
            jain_fairness=0.90,
        ),
    )
    assert e1.decision == AutoresearchDecision.KEEP
    assert harness.incumbent_policy.policy_id == "base_24m"

    # Iteration 2: Worse policy (DISCARD -> reverts incumbent to base_24m)
    p_worse = MutableWirelessPolicy(
        policy_id="huge_queue",
        description="increase AQL to 48MB",
        aql_txq_limit_ac_be_kb=48000,
        complexity_cost=3,
    )
    e2 = harness.run_iteration(
        "b2c3d4e",
        p_worse,
        lambda _: BenchmarkObservation(
            goodput_rx_mbps=52.5,
            p50_rtt_ms=18.0,
            p95_rtt_ms=65.0,
            p99_rtt_ms=95.0,
            jain_fairness=0.84,
        ),
    )
    assert e2.decision == AutoresearchDecision.DISCARD
    assert harness.incumbent_policy.policy_id == "base_24m"

    # Iteration 3: Tighter AQL 3000 KB (KEEP -> advances incumbent to tight_aql_3m)
    p_better = MutableWirelessPolicy(
        policy_id="tight_aql_3m",
        description="tighten AQL to 3000 KB + CoDel 4ms",
        aql_txq_limit_ac_be_kb=3000,
        codel_target_ms=4.0,
        complexity_cost=2,
    )
    e3 = harness.run_iteration(
        "c3d4e5f",
        p_better,
        lambda _: BenchmarkObservation(
            goodput_rx_mbps=56.0,
            p50_rtt_ms=6.0,
            p95_rtt_ms=13.5,
            p99_rtt_ms=21.0,
            jain_fairness=0.98,
        ),
    )
    assert e3.decision == AutoresearchDecision.KEEP
    assert harness.incumbent_policy.policy_id == "tight_aql_3m"

    # Iteration 4: Out-of-bounds knob -> CRASH, incumbent remains tight_aql_3m
    p_invalid = MutableWirelessPolicy(
        policy_id="bad_mcs11",
        description="invalid MCS 11 on 802.11ac",
        vht_mcs_max_index=11,
    )
    e4 = harness.run_iteration(
        "d4e5f6g",
        p_invalid,
        lambda _: pytest.fail("benchmark_fn should not be called when policy bounds fail"),
    )
    assert e4.decision == AutoresearchDecision.CRASH
    assert harness.incumbent_policy.policy_id == "tight_aql_3m"

    rows = harness.ledger.read_all()
    assert [r.status for r in rows] == ["keep", "discard", "keep", "crash"]
    assert rows[2].commit == "c3d4e5f"
    assert rows[2].goodput_mbps == 56.0


def test_compute_pareto_frontier_from_runs() -> None:
    runs = [
        {
            "commit": "iter0_base",
            "observation": {"goodput_rx_mbps": 75.5, "p95_rtt_ms": 39.45, "p99_rtt_ms": 41.48},
            "evaluation": {"disqualified": False},
        },
        {
            "commit": "iter1_aql2000",
            "observation": {"goodput_rx_mbps": 75.0, "p95_rtt_ms": 17.20, "p99_rtt_ms": 17.68},
            "evaluation": {"disqualified": False},
        },
        {
            "commit": "iter4_dominated",
            "observation": {"goodput_rx_mbps": 56.9, "p95_rtt_ms": 15.52, "p99_rtt_ms": 15.96},
            "evaluation": {"disqualified": False},
        },
        {
            "commit": "iter6_rc28",
            "observation": {"goodput_rx_mbps": 66.15, "p95_rtt_ms": 9.59, "p99_rtt_ms": 9.73},
            "evaluation": {"disqualified": False},
        },
        {
            "commit": "iter7_rifs1",
            "observation": {"goodput_rx_mbps": 71.05, "p95_rtt_ms": 11.28, "p99_rtt_ms": 11.41},
            "evaluation": {"disqualified": False},
        },
    ]
    pareto = compute_pareto_frontier(runs)
    commits = [r["commit"] for r in pareto]
    # iter4_dominated (56.9 Mbps, 15.52 ms) is strictly dominated by iter7_rifs1 (71.05 Mbps, 11.28 ms)
    assert "iter4_dominated" not in commits
    assert commits == ["iter6_rc28", "iter7_rifs1", "iter1_aql2000", "iter0_base"]

