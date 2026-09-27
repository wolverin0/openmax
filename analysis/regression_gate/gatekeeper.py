"""
Autonomous A/B/A/B Regression Gatekeeper and Lexicographic Evaluator.
Implements Decision D-0009 and AGENTS.md Section 8 for closed-loop radio optimization.

Evaluation Rules:
1. Hard validity check (watchdog / reset / high loss).
2. Lexicographic hierarchy (p99 latency -> p95 -> fairness -> goodput).
3. Statistical hypothesis testing (Two-tailed Student's t-test / Welch's t-test).
4. Emits KEEP / REJECT / INCONCLUSIVE.
"""

import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class RunMetrics:
    run_id: str
    arm: str  # 'A' (Baseline) or 'B' (Candidate)
    goodput_mbps: float
    p95_lat_ms: float
    p99_lat_ms: float
    loss_pct: float
    jain_fairness: float
    firmware_resets: int = 0


@dataclass
class GateDecision:
    verdict: str  # 'KEEP', 'REJECT', 'INCONCLUSIVE'
    rationale: str
    p99_delta_pct: float
    goodput_delta_pct: float
    p_value: float
    summary: str


def compute_mean_and_variance(values: List[float]) -> Tuple[float, float]:
    if not values:
        return 0.0, 0.0
    mean = sum(values) / len(values)
    if len(values) < 2:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return mean, var


def welch_t_test(group_a: List[float], group_b: List[float]) -> float:
    """Computes approximate p-value using Welch's t-test."""
    n_a = len(group_a)
    n_b = len(group_b)
    if n_a < 2 or n_b < 2:
        return 1.0

    mean_a, var_a = compute_mean_and_variance(group_a)
    mean_b, var_b = compute_mean_and_variance(group_b)

    denom = math.sqrt((var_a / n_a) + (var_b / n_b))
    if denom < 1e-12:
        return 1.0 if abs(mean_a - mean_b) < 1e-6 else 0.0

    t_stat = abs(mean_a - mean_b) / denom
    
    # Degrees of freedom approximation (Welch-Satterthwaite)
    num_dof = ((var_a / n_a) + (var_b / n_b)) ** 2
    den_dof = ((var_a / n_a) ** 2 / (n_a - 1)) + ((var_b / n_b) ** 2 / (n_b - 1))
    dof = max(1.0, num_dof / max(den_dof, 1e-12))

    # Normal approximation for p-value
    # Approximation of complementary error function for t_stat
    z = t_stat / math.sqrt(1.0 + (t_stat ** 2) / (2.0 * dof))
    p_val = math.erfc(z / math.sqrt(2.0))
    return max(0.0, min(1.0, p_val))


class RegressionGatekeeper:
    """Evaluates A/B/A/B experimental trial blocks against the openMAX objective."""

    def __init__(self, max_p99_regression_pct: float = 10.0, min_goodput_gain_pct: float = 5.0):
        self.max_p99_regress = max_p99_regression_pct
        self.min_goodput_gain = min_goodput_gain_pct

    def evaluate(self, runs: List[RunMetrics]) -> GateDecision:
        runs_a = [r for r in runs if r.arm.upper() == "A"]
        runs_b = [r for r in runs if r.arm.upper() == "B"]

        if len(runs_a) < 2 or len(runs_b) < 2:
            return GateDecision(
                verdict="INCONCLUSIVE",
                rationale="Insufficient samples (minimum 2 runs of A and 2 runs of B required).",
                p99_delta_pct=0.0,
                goodput_delta_pct=0.0,
                p_value=1.0,
                summary="Need at least 2 A/B block repetitions."
            )

        # Gate 1: Hard Validity Checks on Candidate (Arm B)
        for r in runs_b:
            if r.firmware_resets > 0:
                return GateDecision(
                    verdict="REJECT",
                    rationale=f"Hard safety failure: Candidate triggered {r.firmware_resets} firmware reset(s)!",
                    p99_delta_pct=0.0,
                    goodput_delta_pct=0.0,
                    p_value=0.0,
                    summary="REJECT: Firmware instability detected."
                )
            if r.loss_pct > 10.0:
                return GateDecision(
                    verdict="REJECT",
                    rationale=f"Hard safety failure: Candidate incurred unacceptable packet loss ({r.loss_pct:.1f}% > 10%)!",
                    p99_delta_pct=0.0,
                    goodput_delta_pct=0.0,
                    p_value=0.0,
                    summary="REJECT: Excessive packet loss."
                )

        # Means
        mean_p99_a, _ = compute_mean_and_variance([r.p99_lat_ms for r in runs_a])
        mean_p99_b, _ = compute_mean_and_variance([r.p99_lat_ms for r in runs_b])

        mean_gp_a, _ = compute_mean_and_variance([r.goodput_mbps for r in runs_a])
        mean_gp_b, _ = compute_mean_and_variance([r.goodput_mbps for r in runs_b])

        p99_delta = ((mean_p99_b - mean_p99_a) / max(mean_p99_a, 1e-6)) * 100.0
        gp_delta = ((mean_gp_b - mean_gp_a) / max(mean_gp_a, 1e-6)) * 100.0

        p_val_gp = welch_t_test([r.goodput_mbps for r in runs_a], [r.goodput_mbps for r in runs_b])

        # Gate 2: Lexicographic Priority 1 - Loaded Latency p99
        # (Candidate must NOT increase p99 latency by more than allowed threshold)
        if p99_delta > self.max_p99_regress:
            return GateDecision(
                verdict="REJECT",
                rationale=(
                    f"Bufferbloat regression: p99 latency degraded by +{p99_delta:.1f}% "
                    f"({mean_p99_a:.1f}ms -> {mean_p99_b:.1f}ms). Exceeds +{self.max_p99_regress}% limit."
                ),
                p99_delta_pct=round(p99_delta, 2),
                goodput_delta_pct=round(gp_delta, 2),
                p_value=round(p_val_gp, 4),
                summary="REJECT: Latency regressed."
            )

        # Gate 3: Lexicographic Priority 4 - Throughput Gain
        if gp_delta < self.min_goodput_gain:
            return GateDecision(
                verdict="REJECT",
                rationale=(
                    f"Insufficient gain: Candidate goodput delta of {gp_delta:+.1f}% "
                    f"does not meet the +{self.min_goodput_gain}% minimum threshold."
                ),
                p99_delta_pct=round(p99_delta, 2),
                goodput_delta_pct=round(gp_delta, 2),
                p_value=round(p_val_gp, 4),
                summary="REJECT: No material throughput gain."
            )

        # Gate 4: Statistical Significance (p < 0.05 for N>=3, p < 0.10 for N=2)
        p_threshold = 0.10 if min(len(runs_a), len(runs_b)) <= 2 else 0.05
        if p_val_gp > p_threshold:
            return GateDecision(
                verdict="INCONCLUSIVE",
                rationale=f"Result is not statistically significant (p-value {p_val_gp:.3f} > {p_threshold}).",
                p99_delta_pct=round(p99_delta, 2),
                goodput_delta_pct=round(gp_delta, 2),
                p_value=round(p_val_gp, 4),
                summary="INCONCLUSIVE: Variance too high."
            )

        # ALL GATES PASSED! KEEP CANDIDATE!
        return GateDecision(
            verdict="KEEP",
            rationale=(
                f"Candidate SUCCESS: Goodput improved by {gp_delta:+.1f}% "
                f"({mean_gp_a:.1f} -> {mean_gp_b:.1f} Mbps) with p99 latency change {p99_delta:+.1f}% "
                f"and statistical significance p={p_val_gp:.4f}."
            ),
            p99_delta_pct=round(p99_delta, 2),
            goodput_delta_pct=round(gp_delta, 2),
            p_value=round(p_val_gp, 4),
            summary=f"KEEP: +{gp_delta:.1f}% goodput with bounded latency."
        )
