"""
Autonomous A/B/A/B Regression Gatekeeper and Lexicographic Evaluator.
Implements Decision D-0009, AGENTS.md Section 7-8, and Phase 0 Workstream D.

Evaluation Rules:
1. Hard validity check (watchdog / firmware reset / excessive packet loss).
2. Temporal drift check across baseline (A) sentinel/sequential blocks.
3. Full lexicographic hierarchy:
   - Priority 1: Loaded latency p99 (must not regress beyond max_p99_regression_pct)
   - Priority 2: Loaded latency p95 (must not regress beyond max_p95_regression_pct)
   - Priority 3: Jain fairness index & worst-peer service (must not drop beyond max_fairness_drop_pct)
   - Priority 4: Spectral efficiency goodput_per_mhz (must gain at least min_goodput_gain_pct)
4. Paired block statistical inference (exact sign-flip permutation test + paired bootstrap 95% CI)
   with Holm-Sidak alpha-spending control for repeated autonomous experiments.
5. Four-stage promotion discipline:
   REJECT | INCONCLUSIVE | KEEP_FOR_REPLICATION | PROMOTE
   (plus legacy 'KEEP' alias in evaluate() when use_four_state_verdicts=False).
"""

from __future__ import annotations

import itertools
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from analysis.metrics.schema import validate_channel_width_mhz


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
    channel_width_mhz: int = 20
    goodput_per_mhz: Optional[float] = None
    block_index: Optional[int] = None
    is_sentinel: bool = False
    worst_peer_goodput_mbps: Optional[float] = None

    def __post_init__(self) -> None:
        validate_channel_width_mhz(self.channel_width_mhz)
        if self.goodput_per_mhz is None:
            self.goodput_per_mhz = round(self.goodput_mbps / float(self.channel_width_mhz), 4)


@dataclass
class PairedBlockDiff:
    block_index: int
    run_a: RunMetrics
    run_b: RunMetrics
    goodput_per_mhz_delta_pct: float
    goodput_mbps_delta_pct: float
    p99_delta_pct: float
    p95_delta_pct: float
    fairness_delta_pct: float
    worst_peer_delta_pct: float


@dataclass
class GateDecision:
    verdict: str  # 'REJECT', 'INCONCLUSIVE', 'KEEP_FOR_REPLICATION', 'PROMOTE' (or legacy 'KEEP')
    rationale: str
    p99_delta_pct: float
    goodput_delta_pct: float
    p_value: float
    summary: str
    promotion_stage: str = "INCONCLUSIVE"
    p95_delta_pct: float = 0.0
    fairness_delta_pct: float = 0.0
    goodput_per_mhz_delta_pct: float = 0.0
    paired_permutation_p_value: float = 1.0
    ci_95_goodput_per_mhz_delta_pct: Tuple[float, float] = (0.0, 0.0)
    ci_95_p99_delta_pct: Tuple[float, float] = (0.0, 0.0)
    drift_detected: bool = False
    drift_pct: float = 0.0
    paired_blocks_count: int = 0
    adjusted_alpha: float = 0.05


def compute_mean_and_variance(values: List[float]) -> Tuple[float, float]:
    if not values:
        return 0.0, 0.0
    mean = sum(values) / len(values)
    if len(values) < 2:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return mean, var


def welch_t_test(group_a: List[float], group_b: List[float]) -> float:
    """Computes approximate two-sided p-value using Welch's t-test."""
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

    num_dof = ((var_a / n_a) + (var_b / n_b)) ** 2
    den_dof = ((var_a / n_a) ** 2 / (n_a - 1)) + ((var_b / n_b) ** 2 / (n_b - 1))
    dof = max(1.0, num_dof / max(den_dof, 1e-12))

    z = t_stat / math.sqrt(1.0 + (t_stat ** 2) / (2.0 * dof))
    p_val = math.erfc(z / math.sqrt(2.0))
    return max(0.0, min(1.0, p_val))


def paired_sign_flip_p_value(
    paired_diffs: List[float],
    max_exact_blocks: int = 14,
    n_permutations: int = 4096,
    seed: int = 42,
) -> float:
    """Computes two-sided paired sign-flip permutation p-value on block differences d_k = B_k - A_k."""
    n = len(paired_diffs)
    if n < 2:
        return 1.0
    observed = abs(sum(paired_diffs) / n)
    if observed < 1e-12:
        return 1.0

    if n <= max_exact_blocks:
        total = 1 << n
        extreme = 0
        for signs in itertools.product((-1.0, 1.0), repeat=n):
            perm_mean = abs(sum(s * d for s, d in zip(signs, paired_diffs)) / n)
            if perm_mean >= observed - 1e-12:
                extreme += 1
        return max(0.0, min(1.0, extreme / float(total)))

    rng = random.Random(seed)
    extreme = 1
    for _ in range(n_permutations):
        perm_mean = abs(sum((1.0 if rng.random() < 0.5 else -1.0) * d for d in paired_diffs) / n)
        if perm_mean >= observed - 1e-12:
            extreme += 1
    return max(0.0, min(1.0, extreme / float(n_permutations + 1)))


def paired_bootstrap_ci_95(
    paired_diffs: List[float],
    n_boot: int = 2000,
    seed: int = 42,
) -> Tuple[float, float]:
    """Computes 95% bootstrap confidence interval for the mean paired block difference."""
    n = len(paired_diffs)
    if n == 0:
        return (0.0, 0.0)
    if n == 1:
        val = round(paired_diffs[0], 4)
        return (val, val)
    if all(abs(d - paired_diffs[0]) < 1e-12 for d in paired_diffs):
        val = round(paired_diffs[0], 4)
        return (val, val)

    rng = random.Random(seed)
    means: List[float] = []
    for _ in range(n_boot):
        sample = [paired_diffs[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo_idx = max(0, min(n_boot - 1, int(0.025 * n_boot)))
    hi_idx = max(0, min(n_boot - 1, int(0.975 * n_boot)))
    return (round(means[lo_idx], 4), round(means[hi_idx], 4))


def compute_adjusted_alpha(alpha: float = 0.05, num_hypotheses: int = 1) -> float:
    """Computes Šidák / family-wise adjusted alpha for repeated autonomous candidate trials."""
    m = max(1, int(num_hypotheses))
    if m == 1:
        return alpha
    return round(1.0 - (1.0 - alpha) ** (1.0 / m), 6)


def build_paired_blocks(runs: List[RunMetrics]) -> List[PairedBlockDiff]:
    """Pairs baseline (A) and candidate (B) runs by explicit block_index or sequential order."""
    runs_a = [r for r in runs if r.arm.upper() == "A" and not r.is_sentinel]
    runs_b = [r for r in runs if r.arm.upper() == "B" and not r.is_sentinel]

    by_index_a = {r.block_index: r for r in runs_a if r.block_index is not None}
    by_index_b = {r.block_index: r for r in runs_b if r.block_index is not None}

    pairs: List[Tuple[int, RunMetrics, RunMetrics]] = []
    common_indices = sorted(set(by_index_a.keys()) & set(by_index_b.keys()))
    if common_indices and len(common_indices) == min(len(runs_a), len(runs_b)):
        for idx in common_indices:
            pairs.append((int(idx), by_index_a[idx], by_index_b[idx]))
    else:
        n_pairs = min(len(runs_a), len(runs_b))
        for idx in range(n_pairs):
            pairs.append((idx, runs_a[idx], runs_b[idx]))

    diffs: List[PairedBlockDiff] = []
    for idx, ra, rb in pairs:
        if ra.channel_width_mhz != rb.channel_width_mhz:
            raise ValueError(
                f"Block {idx} channel_width_mhz mismatch: arm A has {ra.channel_width_mhz} MHz "
                f"while arm B has {rb.channel_width_mhz} MHz."
            )
        gpm_a = float(ra.goodput_per_mhz or (ra.goodput_mbps / ra.channel_width_mhz))
        gpm_b = float(rb.goodput_per_mhz or (rb.goodput_mbps / rb.channel_width_mhz))
        gpm_delta = ((gpm_b - gpm_a) / max(gpm_a, 1e-6)) * 100.0
        gp_delta = ((rb.goodput_mbps - ra.goodput_mbps) / max(ra.goodput_mbps, 1e-6)) * 100.0
        p99_delta = ((rb.p99_lat_ms - ra.p99_lat_ms) / max(ra.p99_lat_ms, 1e-6)) * 100.0
        p95_delta = ((rb.p95_lat_ms - ra.p95_lat_ms) / max(ra.p95_lat_ms, 1e-6)) * 100.0
        fair_delta = ((rb.jain_fairness - ra.jain_fairness) / max(ra.jain_fairness, 1e-6)) * 100.0
        if ra.worst_peer_goodput_mbps is not None and rb.worst_peer_goodput_mbps is not None:
            wp_delta = (
                (rb.worst_peer_goodput_mbps - ra.worst_peer_goodput_mbps)
                / max(ra.worst_peer_goodput_mbps, 1e-6)
            ) * 100.0
        else:
            wp_delta = 0.0
        diffs.append(
            PairedBlockDiff(
                block_index=idx,
                run_a=ra,
                run_b=rb,
                goodput_per_mhz_delta_pct=gpm_delta,
                goodput_mbps_delta_pct=gp_delta,
                p99_delta_pct=p99_delta,
                p95_delta_pct=p95_delta,
                fairness_delta_pct=fair_delta,
                worst_peer_delta_pct=wp_delta,
            )
        )
    return diffs


def detect_baseline_drift(
    runs: List[RunMetrics],
    max_drift_pct: float = 20.0,
) -> Tuple[bool, float, str]:
    """Detects non-stationary RF/environment drift across baseline (A) and sentinel blocks."""
    baseline_all = [r for r in runs if r.arm.upper() == "A"]
    if len(baseline_all) < 2:
        return False, 0.0, "Insufficient baseline runs for drift check."

    sentinels = [r for r in baseline_all if r.is_sentinel]
    reference_pool = sentinels if len(sentinels) >= 2 else baseline_all

    first = reference_pool[0]
    last = reference_pool[-1]
    gpm_first = float(first.goodput_per_mhz or (first.goodput_mbps / first.channel_width_mhz))
    gpm_last = float(last.goodput_per_mhz or (last.goodput_mbps / last.channel_width_mhz))
    gpm_drift_pct = abs(gpm_last - gpm_first) / max(gpm_first, 1e-6) * 100.0
    p99_drift_pct = abs(last.p99_lat_ms - first.p99_lat_ms) / max(first.p99_lat_ms, 1e-6) * 100.0

    worst_drift = max(gpm_drift_pct, p99_drift_pct)
    if worst_drift > max_drift_pct:
        return (
            True,
            round(worst_drift, 2),
            f"Temporal baseline drift of {worst_drift:.1f}% exceeds {max_drift_pct:.1f}% threshold "
            f"(gpm drift={gpm_drift_pct:.1f}%, p99 drift={p99_drift_pct:.1f}%).",
        )
    return False, round(worst_drift, 2), "Baseline stationary within drift bounds."


class RegressionGatekeeper:
    """Evaluates A/B/A/B experimental trial blocks against the openMAX lexicographic objective."""

    def __init__(
        self,
        max_p99_regression_pct: float = 10.0,
        min_goodput_gain_pct: float = 5.0,
        max_p95_regression_pct: float = 10.0,
        max_fairness_drop_pct: float = 5.0,
        max_worst_peer_drop_pct: float = 15.0,
        max_loss_pct: float = 10.0,
        max_drift_pct: float = 25.0,
        alpha: float = 0.05,
        num_hypotheses_tested: int = 1,
        min_blocks_for_keep: int = 4,
        min_blocks_for_promote: int = 6,
    ):
        self.max_p99_regress = max_p99_regression_pct
        self.min_goodput_gain = min_goodput_gain_pct
        self.max_p95_regress = max_p95_regression_pct
        self.max_fairness_drop = max_fairness_drop_pct
        self.max_worst_peer_drop = max_worst_peer_drop_pct
        self.max_loss_pct = max_loss_pct
        self.max_drift_pct = max_drift_pct
        self.alpha = alpha
        self.num_hypotheses_tested = num_hypotheses_tested
        self.min_blocks_for_keep = min_blocks_for_keep
        self.min_blocks_for_promote = min_blocks_for_promote

    def evaluate_paired(
        self,
        runs: List[RunMetrics],
        holdout_replicated: bool = False,
    ) -> GateDecision:
        """Strict Phase 0 Workstream D evaluator emitting REJECT | INCONCLUSIVE | KEEP_FOR_REPLICATION | PROMOTE."""
        return self._evaluate_core(
            runs=runs,
            use_four_state_verdicts=True,
            holdout_replicated=holdout_replicated,
        )

    def evaluate(
        self,
        runs: List[RunMetrics],
        use_four_state_verdicts: bool = False,
        holdout_replicated: bool = False,
    ) -> GateDecision:
        """Evaluates A/B/A/B runs. Preserves legacy verdict='KEEP' unless use_four_state_verdicts=True."""
        return self._evaluate_core(
            runs=runs,
            use_four_state_verdicts=use_four_state_verdicts,
            holdout_replicated=holdout_replicated,
        )

    def _evaluate_core(
        self,
        runs: List[RunMetrics],
        use_four_state_verdicts: bool,
        holdout_replicated: bool,
    ) -> GateDecision:
        runs_a = [r for r in runs if r.arm.upper() == "A" and not r.is_sentinel]
        runs_b = [r for r in runs if r.arm.upper() == "B" and not r.is_sentinel]
        adjusted_alpha = compute_adjusted_alpha(self.alpha, self.num_hypotheses_tested)

        # Gate 1: Hard Safety Checks on Candidate (Arm B) — checked first regardless of sample count
        for r in runs_b:
            if r.firmware_resets > 0:
                return GateDecision(
                    verdict="REJECT",
                    promotion_stage="REJECT",
                    rationale=f"Hard safety failure: Candidate triggered {r.firmware_resets} firmware reset(s)!",
                    p99_delta_pct=0.0,
                    goodput_delta_pct=0.0,
                    p_value=0.0,
                    summary="REJECT: Firmware instability detected.",
                    adjusted_alpha=adjusted_alpha,
                )
            if r.loss_pct > self.max_loss_pct:
                return GateDecision(
                    verdict="REJECT",
                    promotion_stage="REJECT",
                    rationale=(
                        f"Hard safety failure: Candidate incurred unacceptable packet loss "
                        f"({r.loss_pct:.1f}% > {self.max_loss_pct:.1f}%)!"
                    ),
                    p99_delta_pct=0.0,
                    goodput_delta_pct=0.0,
                    p_value=0.0,
                    summary="REJECT: Excessive packet loss.",
                    adjusted_alpha=adjusted_alpha,
                )

        if len(runs_a) < 2 or len(runs_b) < 2:
            return GateDecision(
                verdict="INCONCLUSIVE",
                promotion_stage="INCONCLUSIVE",
                rationale="Insufficient samples (minimum 2 runs of A and 2 runs of B required).",
                p99_delta_pct=0.0,
                goodput_delta_pct=0.0,
                p_value=1.0,
                summary="Need at least 2 A/B block repetitions.",
                adjusted_alpha=adjusted_alpha,
            )

        # Build paired temporal blocks (verifies channel_width_mhz consistency per block)
        pairs = build_paired_blocks(runs)
        n_pairs = len(pairs)

        # Temporal drift sentinel check
        drift_detected, drift_pct, drift_msg = detect_baseline_drift(runs, max_drift_pct=self.max_drift_pct)

        # Paired block differences and aggregate means
        mean_p99_a, _ = compute_mean_and_variance([p.run_a.p99_lat_ms for p in pairs])
        mean_p99_b, _ = compute_mean_and_variance([p.run_b.p99_lat_ms for p in pairs])
        mean_p95_a, _ = compute_mean_and_variance([p.run_a.p95_lat_ms for p in pairs])
        mean_p95_b, _ = compute_mean_and_variance([p.run_b.p95_lat_ms for p in pairs])
        mean_fair_a, _ = compute_mean_and_variance([p.run_a.jain_fairness for p in pairs])
        mean_fair_b, _ = compute_mean_and_variance([p.run_b.jain_fairness for p in pairs])
        mean_gp_a, _ = compute_mean_and_variance([p.run_a.goodput_mbps for p in pairs])
        mean_gp_b, _ = compute_mean_and_variance([p.run_b.goodput_mbps for p in pairs])
        mean_gpm_a, _ = compute_mean_and_variance([float(p.run_a.goodput_per_mhz or 0.0) for p in pairs])
        mean_gpm_b, _ = compute_mean_and_variance([float(p.run_b.goodput_per_mhz or 0.0) for p in pairs])

        p99_delta = ((mean_p99_b - mean_p99_a) / max(mean_p99_a, 1e-6)) * 100.0
        p95_delta = ((mean_p95_b - mean_p95_a) / max(mean_p95_a, 1e-6)) * 100.0
        fair_delta = ((mean_fair_b - mean_fair_a) / max(mean_fair_a, 1e-6)) * 100.0
        gp_delta = ((mean_gp_b - mean_gp_a) / max(mean_gp_a, 1e-6)) * 100.0
        gpm_delta = ((mean_gpm_b - mean_gpm_a) / max(mean_gpm_a, 1e-6)) * 100.0

        gpm_pair_diffs = [p.goodput_per_mhz_delta_pct for p in pairs]
        p99_pair_diffs = [p.p99_delta_pct for p in pairs]
        wp_pair_diffs = [p.worst_peer_delta_pct for p in pairs]
        mean_wp_delta = sum(wp_pair_diffs) / max(1, len(wp_pair_diffs))

        p_val_welch = welch_t_test(
            [float(p.run_a.goodput_per_mhz or 0.0) for p in pairs],
            [float(p.run_b.goodput_per_mhz or 0.0) for p in pairs],
        )
        p_val_perm = paired_sign_flip_p_value(gpm_pair_diffs)
        ci_gpm = paired_bootstrap_ci_95(gpm_pair_diffs)
        ci_p99 = paired_bootstrap_ci_95(p99_pair_diffs)

        if drift_detected:
            return GateDecision(
                verdict="INCONCLUSIVE",
                promotion_stage="INCONCLUSIVE",
                rationale=f"Environment drift invalidated paired comparison: {drift_msg}",
                p99_delta_pct=round(p99_delta, 2),
                goodput_delta_pct=round(gp_delta, 2),
                p_value=round(p_val_perm, 4),
                summary="INCONCLUSIVE: Baseline temporal drift detected.",
                p95_delta_pct=round(p95_delta, 2),
                fairness_delta_pct=round(fair_delta, 2),
                goodput_per_mhz_delta_pct=round(gpm_delta, 2),
                paired_permutation_p_value=round(p_val_perm, 4),
                ci_95_goodput_per_mhz_delta_pct=ci_gpm,
                ci_95_p99_delta_pct=ci_p99,
                drift_detected=True,
                drift_pct=drift_pct,
                paired_blocks_count=n_pairs,
                adjusted_alpha=adjusted_alpha,
            )

        # Gate 2: Lexicographic Priority 1 - Loaded Latency p99
        if p99_delta > self.max_p99_regress:
            return GateDecision(
                verdict="REJECT",
                promotion_stage="REJECT",
                rationale=(
                    f"Bufferbloat regression: p99 latency degraded by +{p99_delta:.1f}% "
                    f"({mean_p99_a:.1f}ms -> {mean_p99_b:.1f}ms). Exceeds +{self.max_p99_regress}% limit."
                ),
                p99_delta_pct=round(p99_delta, 2),
                goodput_delta_pct=round(gp_delta, 2),
                p_value=round(p_val_welch, 4),
                summary="REJECT: Latency p99 regressed.",
                p95_delta_pct=round(p95_delta, 2),
                fairness_delta_pct=round(fair_delta, 2),
                goodput_per_mhz_delta_pct=round(gpm_delta, 2),
                paired_permutation_p_value=round(p_val_perm, 4),
                ci_95_goodput_per_mhz_delta_pct=ci_gpm,
                ci_95_p99_delta_pct=ci_p99,
                drift_detected=False,
                drift_pct=drift_pct,
                paired_blocks_count=n_pairs,
                adjusted_alpha=adjusted_alpha,
            )

        # Gate 3: Lexicographic Priority 2 - Loaded Latency p95
        if p95_delta > self.max_p95_regress:
            return GateDecision(
                verdict="REJECT",
                promotion_stage="REJECT",
                rationale=(
                    f"Loaded p95 latency degraded by +{p95_delta:.1f}% "
                    f"({mean_p95_a:.1f}ms -> {mean_p95_b:.1f}ms). Exceeds +{self.max_p95_regress}% limit."
                ),
                p99_delta_pct=round(p99_delta, 2),
                goodput_delta_pct=round(gp_delta, 2),
                p_value=round(p_val_welch, 4),
                summary="REJECT: Latency p95 regressed.",
                p95_delta_pct=round(p95_delta, 2),
                fairness_delta_pct=round(fair_delta, 2),
                goodput_per_mhz_delta_pct=round(gpm_delta, 2),
                paired_permutation_p_value=round(p_val_perm, 4),
                ci_95_goodput_per_mhz_delta_pct=ci_gpm,
                ci_95_p99_delta_pct=ci_p99,
                drift_detected=False,
                drift_pct=drift_pct,
                paired_blocks_count=n_pairs,
                adjusted_alpha=adjusted_alpha,
            )

        # Gate 4: Lexicographic Priority 3 - Jain Fairness & Worst-Peer Protection
        if fair_delta < -self.max_fairness_drop or mean_wp_delta < -self.max_worst_peer_drop:
            return GateDecision(
                verdict="REJECT",
                promotion_stage="REJECT",
                rationale=(
                    f"Fairness/starvation regression: Jain fairness delta {fair_delta:+.1f}% "
                    f"(limit -{self.max_fairness_drop:.1f}%), worst-peer delta {mean_wp_delta:+.1f}% "
                    f"(limit -{self.max_worst_peer_drop:.1f}%)."
                ),
                p99_delta_pct=round(p99_delta, 2),
                goodput_delta_pct=round(gp_delta, 2),
                p_value=round(p_val_welch, 4),
                summary="REJECT: Fairness or worst-peer service regressed.",
                p95_delta_pct=round(p95_delta, 2),
                fairness_delta_pct=round(fair_delta, 2),
                goodput_per_mhz_delta_pct=round(gpm_delta, 2),
                paired_permutation_p_value=round(p_val_perm, 4),
                ci_95_goodput_per_mhz_delta_pct=ci_gpm,
                ci_95_p99_delta_pct=ci_p99,
                drift_detected=False,
                drift_pct=drift_pct,
                paired_blocks_count=n_pairs,
                adjusted_alpha=adjusted_alpha,
            )

        # Gate 5: Lexicographic Priority 4 - Spectral Efficiency (goodput_per_mhz) Gain
        if gpm_delta < self.min_goodput_gain:
            return GateDecision(
                verdict="REJECT",
                promotion_stage="REJECT",
                rationale=(
                    f"Insufficient gain: Candidate goodput/MHz delta of {gpm_delta:+.1f}% "
                    f"does not meet the +{self.min_goodput_gain}% minimum threshold."
                ),
                p99_delta_pct=round(p99_delta, 2),
                goodput_delta_pct=round(gp_delta, 2),
                p_value=round(p_val_welch, 4),
                summary="REJECT: No material throughput gain.",
                p95_delta_pct=round(p95_delta, 2),
                fairness_delta_pct=round(fair_delta, 2),
                goodput_per_mhz_delta_pct=round(gpm_delta, 2),
                paired_permutation_p_value=round(p_val_perm, 4),
                ci_95_goodput_per_mhz_delta_pct=ci_gpm,
                ci_95_p99_delta_pct=ci_p99,
                drift_detected=False,
                drift_pct=drift_pct,
                paired_blocks_count=n_pairs,
                adjusted_alpha=adjusted_alpha,
            )

        # Gate 6: Sample Size, Paired Inference, and Promotion Stage Discipline
        if use_four_state_verdicts:
            if n_pairs < self.min_blocks_for_keep:
                return GateDecision(
                    verdict="INCONCLUSIVE",
                    promotion_stage="INCONCLUSIVE",
                    rationale=(
                        f"Insufficient paired blocks ({n_pairs} < {self.min_blocks_for_keep} required "
                        f"for KEEP_FOR_REPLICATION). N=2 is never sufficient for promotion."
                    ),
                    p99_delta_pct=round(p99_delta, 2),
                    goodput_delta_pct=round(gp_delta, 2),
                    p_value=round(p_val_perm, 4),
                    summary="INCONCLUSIVE: Need more paired A/B blocks.",
                    p95_delta_pct=round(p95_delta, 2),
                    fairness_delta_pct=round(fair_delta, 2),
                    goodput_per_mhz_delta_pct=round(gpm_delta, 2),
                    paired_permutation_p_value=round(p_val_perm, 4),
                    ci_95_goodput_per_mhz_delta_pct=ci_gpm,
                    ci_95_p99_delta_pct=ci_p99,
                    drift_detected=False,
                    drift_pct=drift_pct,
                    paired_blocks_count=n_pairs,
                    adjusted_alpha=adjusted_alpha,
                )

            if p_val_perm > adjusted_alpha or ci_gpm[0] <= 0.0:
                return GateDecision(
                    verdict="INCONCLUSIVE",
                    promotion_stage="INCONCLUSIVE",
                    rationale=(
                        f"Paired inference not statistically significant under alpha control "
                        f"(paired_p={p_val_perm:.4f} vs adjusted_alpha={adjusted_alpha:.4f}, "
                        f"95% CI={ci_gpm})."
                    ),
                    p99_delta_pct=round(p99_delta, 2),
                    goodput_delta_pct=round(gp_delta, 2),
                    p_value=round(p_val_perm, 4),
                    summary="INCONCLUSIVE: Variance too high under paired permutation test.",
                    p95_delta_pct=round(p95_delta, 2),
                    fairness_delta_pct=round(fair_delta, 2),
                    goodput_per_mhz_delta_pct=round(gpm_delta, 2),
                    paired_permutation_p_value=round(p_val_perm, 4),
                    ci_95_goodput_per_mhz_delta_pct=ci_gpm,
                    ci_95_p99_delta_pct=ci_p99,
                    drift_detected=False,
                    drift_pct=drift_pct,
                    paired_blocks_count=n_pairs,
                    adjusted_alpha=adjusted_alpha,
                )

            if holdout_replicated and n_pairs >= self.min_blocks_for_promote:
                stage = "PROMOTE"
            else:
                stage = "KEEP_FOR_REPLICATION"

            return GateDecision(
                verdict=stage,
                promotion_stage=stage,
                rationale=(
                    f"Candidate {stage}: goodput/MHz improved by {gpm_delta:+.1f}% "
                    f"(95% CI {ci_gpm[0]:+.1f}%..{ci_gpm[1]:+.1f}%, paired_p={p_val_perm:.4f} <= {adjusted_alpha:.4f}) "
                    f"with p99={p99_delta:+.1f}%, p95={p95_delta:+.1f}%, fairness={fair_delta:+.1f}%."
                ),
                p99_delta_pct=round(p99_delta, 2),
                goodput_delta_pct=round(gp_delta, 2),
                p_value=round(p_val_perm, 4),
                summary=f"{stage}: +{gpm_delta:.1f}% goodput/MHz with bounded latency and fairness.",
                p95_delta_pct=round(p95_delta, 2),
                fairness_delta_pct=round(fair_delta, 2),
                goodput_per_mhz_delta_pct=round(gpm_delta, 2),
                paired_permutation_p_value=round(p_val_perm, 4),
                ci_95_goodput_per_mhz_delta_pct=ci_gpm,
                ci_95_p99_delta_pct=ci_p99,
                drift_detected=False,
                drift_pct=drift_pct,
                paired_blocks_count=n_pairs,
                adjusted_alpha=adjusted_alpha,
            )

        # Legacy evaluate() mode: preserves 'KEEP' string for backward compatibility while
        # setting promotion_stage accurately ('KEEP_FOR_REPLICATION' vs 'PROMOTE').
        if p_val_welch > adjusted_alpha:
            return GateDecision(
                verdict="INCONCLUSIVE",
                promotion_stage="INCONCLUSIVE",
                rationale=f"Result is not statistically significant (p-value {p_val_welch:.3f} > {adjusted_alpha:.3f}).",
                p99_delta_pct=round(p99_delta, 2),
                goodput_delta_pct=round(gp_delta, 2),
                p_value=round(p_val_welch, 4),
                summary="INCONCLUSIVE: Variance too high.",
                p95_delta_pct=round(p95_delta, 2),
                fairness_delta_pct=round(fair_delta, 2),
                goodput_per_mhz_delta_pct=round(gpm_delta, 2),
                paired_permutation_p_value=round(p_val_perm, 4),
                ci_95_goodput_per_mhz_delta_pct=ci_gpm,
                ci_95_p99_delta_pct=ci_p99,
                drift_detected=False,
                drift_pct=drift_pct,
                paired_blocks_count=n_pairs,
                adjusted_alpha=adjusted_alpha,
            )

        stage = "PROMOTE" if (holdout_replicated and n_pairs >= self.min_blocks_for_promote) else "KEEP_FOR_REPLICATION"
        return GateDecision(
            verdict="KEEP",
            promotion_stage=stage,
            rationale=(
                f"Candidate SUCCESS ({stage}): Goodput improved by {gp_delta:+.1f}% "
                f"({mean_gp_a:.1f} -> {mean_gp_b:.1f} Mbps) with p99 latency change {p99_delta:+.1f}% "
                f"and statistical significance p={p_val_welch:.4f}."
            ),
            p99_delta_pct=round(p99_delta, 2),
            goodput_delta_pct=round(gp_delta, 2),
            p_value=round(p_val_welch, 4),
            summary=f"KEEP: +{gp_delta:.1f}% goodput with bounded latency.",
            p95_delta_pct=round(p95_delta, 2),
            fairness_delta_pct=round(fair_delta, 2),
            goodput_per_mhz_delta_pct=round(gpm_delta, 2),
            paired_permutation_p_value=round(p_val_perm, 4),
            ci_95_goodput_per_mhz_delta_pct=ci_gpm,
            ci_95_p99_delta_pct=ci_p99,
            drift_detected=False,
            drift_pct=drift_pct,
            paired_blocks_count=n_pairs,
            adjusted_alpha=adjusted_alpha,
        )


def run_aa_null_replay_validation(
    baseline_pool: List[RunMetrics],
    gatekeeper: Optional[RegressionGatekeeper] = None,
    pairs_per_trial: int = 6,
    num_trials: int = 300,
    seed: int = 20261024,
) -> Dict[str, Any]:
    """Replays baseline-only (A/A) logs under random A/B block assignment to measure false-positive rate."""
    if len(baseline_pool) < 4:
        raise ValueError("baseline_pool must contain at least 4 baseline RunMetrics samples for A/A replay.")

    gk = gatekeeper or RegressionGatekeeper()
    rng = random.Random(seed)
    verdict_counts: Dict[str, int] = {
        "REJECT": 0,
        "INCONCLUSIVE": 0,
        "KEEP_FOR_REPLICATION": 0,
        "PROMOTE": 0,
    }

    for trial_idx in range(num_trials):
        trial_runs: List[RunMetrics] = []
        for block_idx in range(pairs_per_trial):
            sample_a = rng.choice(baseline_pool)
            sample_b = rng.choice(baseline_pool)
            trial_runs.append(
                RunMetrics(
                    run_id=f"aa_t{trial_idx}_b{block_idx}_A",
                    arm="A",
                    goodput_mbps=sample_a.goodput_mbps,
                    p95_lat_ms=sample_a.p95_lat_ms,
                    p99_lat_ms=sample_a.p99_lat_ms,
                    loss_pct=sample_a.loss_pct,
                    jain_fairness=sample_a.jain_fairness,
                    firmware_resets=0,
                    channel_width_mhz=sample_a.channel_width_mhz,
                    block_index=block_idx,
                    worst_peer_goodput_mbps=sample_a.worst_peer_goodput_mbps,
                )
            )
            trial_runs.append(
                RunMetrics(
                    run_id=f"aa_t{trial_idx}_b{block_idx}_B",
                    arm="B",
                    goodput_mbps=sample_b.goodput_mbps,
                    p95_lat_ms=sample_b.p95_lat_ms,
                    p99_lat_ms=sample_b.p99_lat_ms,
                    loss_pct=sample_b.loss_pct,
                    jain_fairness=sample_b.jain_fairness,
                    firmware_resets=0,
                    channel_width_mhz=sample_b.channel_width_mhz,
                    block_index=block_idx,
                    worst_peer_goodput_mbps=sample_b.worst_peer_goodput_mbps,
                )
            )
        decision = gk.evaluate_paired(trial_runs, holdout_replicated=True)
        verdict_counts[decision.verdict] = verdict_counts.get(decision.verdict, 0) + 1

    false_positives = verdict_counts["KEEP_FOR_REPLICATION"] + verdict_counts["PROMOTE"]
    fp_rate = false_positives / float(num_trials)
    return {
        "num_trials": num_trials,
        "pairs_per_trial": pairs_per_trial,
        "verdict_counts": verdict_counts,
        "false_positives": false_positives,
        "false_positive_rate": round(fp_rate, 4),
        "target_alpha": gk.alpha,
        "passes_null_calibration": fp_rate <= max(gk.alpha, 0.05),
    }
