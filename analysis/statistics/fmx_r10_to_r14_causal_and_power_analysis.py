"""Offline exploratory inference on frozen R10-R14 receipts; never an actuator.

Ping-level calculations are conditional sensitivity analyses, not independent
physical repetitions. Recipes are hashed/read as text, never imported/executed.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy import stats

from analysis.statistics.fmx_autoresearch_statistical_audit import (
    holm_adjust, planning_power, required_sample_size,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts/autoresearch/waves_ijkl_20261024"
SEED = 20261024


def probability(value, name="alpha"):
    if isinstance(value, (bool, str)) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite probability")
    if not math.isfinite(value) or not 0 < value < 1:
        raise ValueError(f"{name} must lie strictly between zero and one")
    return float(value)


def sample(values, minimum=2):
    items = list(values)
    if not minimum <= len(items) <= 1000:
        raise ValueError("Bounded one-dimensional sample required")
    if any(isinstance(v, (bool, str)) or not isinstance(v, (int, float, np.number)) for v in items):
        raise ValueError("Finite numeric scalars required")
    result = np.asarray(items, dtype=float)
    if result.ndim != 1 or not np.isfinite(result).all():
        raise ValueError("Finite one-dimensional sample required")
    return result


@lru_cache(maxsize=32)
def _u_counts(n, m):
    """Exact no-tie rank-sum distribution, integer subset-count recurrence."""
    if not (1 <= n <= 50 and 1 <= m <= 50):
        raise ValueError("Exact rank inversion limited to 50 observations per arm")
    previous = [[1] for _ in range(m + 1)]
    for i in range(1, n + 1):
        current = [[1]]
        for j in range(1, m + 1):
            a, b = previous[j], current[j - 1]
            counts = [0] * (i * j + 1)
            for k, value in enumerate(a):
                counts[k + j] += value
            for k, value in enumerate(b):
                counts[k] += value
            current.append(counts)
        previous = current
    return tuple(previous[m])


def hodges_lehmann(control, treatment, alpha=0.05, *, continuous_shift=False):
    """Median of treatment-control pair differences with honest CI assumptions.

    Default CI uses simultaneous DKW bounds on the two marginal empirical CDFs.
    Their convolution CDF error is <= eps_control+eps_treatment (union bound).
    Quantile inversion gives a conservative distribution-free interval for the
    population median of Y-X under independent iid samples, including ties.
    None endpoints mean -/+ infinity, not missing zero. No nm-iid assumption.

    An explicitly requested continuous common-shape location-shift model, with
    no observed ties, permits the classical exact U rank-inversion interval.
    Shape equality/independence cannot be established from these bench arrays.
    """
    alpha = probability(alpha)
    if type(continuous_shift) is not bool:
        raise ValueError("continuous_shift must be explicit boolean")
    x, y = sample(control), sample(treatment)
    with np.errstate(over="ignore", invalid="ignore"):
        differences = np.sort((y[:, None] - x[None, :]).ravel())
    if not np.isfinite(differences).all():
        raise ValueError("Pair differences exceed finite arithmetic")
    estimate = float(np.median(differences))
    tied = len(np.unique(np.concatenate((x, y)))) != len(x) + len(y)
    if continuous_shift and not tied:
        counts = _u_counts(len(x), len(y))
        total, cumulative, critical = sum(counts), 0, -1
        for u, count in enumerate(counts):
            cumulative += count
            if cumulative / total <= alpha / 2:
                critical = u
            else:
                break
        ci = [float(differences[critical]), float(differences[-critical - 1])] if critical >= 0 else [None, None]
        return dict(estimate_ms=estimate, interval_ms=ci, confidence=1-alpha,
                    method="EXACT_U_RANK_INVERSION_CONTINUOUS_COMMON_SHAPE_SHIFT",
                    critical_U=critical, ties=False,
                    estimand="Common location shift, conditional on the stated shift model")
    epsilon = math.sqrt(math.log(4/alpha)/(2*len(x))) + math.sqrt(math.log(4/alpha)/(2*len(y)))
    lower, upper = 0.5-epsilon, 0.5+epsilon
    # Inverse empirical CDF, not interpolated pseudo-independent differences.
    def inverse(p):
        return float(differences[max(0, math.ceil(p*len(differences))-1)])
    return dict(estimate_ms=estimate,
                interval_ms=[inverse(lower) if lower > 0 else None, inverse(upper) if upper < 1 else None],
                confidence=1-alpha, method="CONSERVATIVE_MARGINAL_DKW_QUANTILE_INVERSION",
                cdf_error_bound=epsilon, ties=tied, shift_model_requested=continuous_shift,
                estimand="Population median of independent treatment-control differences, not difference of medians",
                assumptions="iid within each arm and independent arms; not verified for serial pooled pings")


def mwu_contrast(control, treatment, alpha=0.05):
    alpha = probability(alpha)
    x, y = sample(control), sample(treatment)
    # Explicit asymptotic test corrects ties; exact no-tie method is inappropriate
    # for rounded RTT arrays. Continuity correction is retained explicitly.
    result = stats.mannwhitneyu(y, x, alternative="two-sided", method="asymptotic", use_continuity=True)
    return dict(n_control=len(x), n_treatment=len(y), U_treatment=float(result.statistic),
                p_value=float(result.pvalue), superiority_treatment_gt_control_with_half_ties=float(result.statistic/(len(x)*len(y))),
                hl=hodges_lehmann(x, y, alpha),
                interpretation="Distribution/rank contrast, not a median-only test; CONDITIONAL_IID_PING_MODEL_NOT_PHYSICAL_TRIAL_INFERENCE")


def paired_wilcoxon(control, treatment, *, control_ids=None, treatment_ids=None):
    """Align by genuine supplied unit IDs; never zip sorted arrays by position."""
    x, y = sample(control), sample(treatment)
    if control_ids is None or treatment_ids is None:
        return dict(status="UNIDENTIFIED_PAIRING", p_value=None, pairs=None)
    ids_x, ids_y = list(control_ids), list(treatment_ids)
    if (len(ids_x) != len(x) or len(ids_y) != len(y)
            or any(not isinstance(v, str) or not v for v in ids_x + ids_y)
            or len(set(ids_x)) != len(ids_x) or len(set(ids_y)) != len(ids_y)
            or set(ids_x) != set(ids_y)):
        raise ValueError("Unique matching genuine pair identifiers required")
    lookup = dict(zip(ids_y, y))
    differences = np.array([lookup[i]-v for i, v in zip(ids_x, x)])
    if np.all(differences == 0):
        statistic, p_value = 0.0, 1.0
    else:
        result = stats.wilcoxon(differences, alternative="two-sided", zero_method="wilcox", method="auto")
        statistic, p_value = float(result.statistic), float(result.pvalue)
    return dict(status="CALCULATED_WITH_EXPLICIT_PAIR_IDS", statistic=statistic, p_value=p_value,
                pairs=len(differences), median_difference=float(np.median(differences)),
                assumptions="Independent identified pairs and symmetric difference distribution; caller must establish physical design")


def conditional_tail_bootstrap(values, *, quantile=0.95, alpha=0.05, resamples=1999, seed=SEED):
    data = sample(values)
    quantile, alpha = probability(quantile, "quantile"), probability(alpha)
    if type(resamples) is not int or not 99 <= resamples <= 20000:
        raise ValueError("99..20000 bootstrap replicates required")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("Bounded integer seed required")
    rng = np.random.default_rng(seed)
    estimates = []
    for first in range(0, resamples, 128):
        draws = rng.choice(data, size=(min(128, resamples-first), len(data)), replace=True)
        estimates.extend(np.quantile(draws, quantile, axis=1, method="linear").tolist())
    return dict(quantile=quantile, estimate_ms=float(np.quantile(data, quantile, method="linear")),
                percentile_interval_ms=np.quantile(estimates, [alpha/2, 1-alpha/2]).tolist(),
                confidence=1-alpha, resamples=resamples, seed=seed, received_count=len(data),
                probability_max_exceeds_true_quantile_under_iid=1-quantile**len(data),
                status="CONDITIONAL_EMPIRICAL_IID_BOOTSTRAP_ONLY",
                limits="Pooled received pings; unknown serial/rep dependence and loss censoring; sparse tail/percentile coverage uncalibrated; no physical-trial CI")


def load_frozen_rounds(base=ARTIFACTS):
    """Verify frozen manifest bytes before JSON parsing; recipes remain text."""
    base = Path(base)
    manifest_path = base / "inputs_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    provenance, rounds = [], {}
    for entry in manifest:
        name = Path(entry["path"]).name
        relevant_round = any(f"_r{i}_" in name for i in range(10, 15))
        probe_dependency = entry["kind"] == "recipe" and name == "run_live_autoresearch_r7_multiflow_shootout_20261024.py"
        if not (relevant_round or probe_dependency):
            continue
        path = (ROOT / entry["path"]).resolve()
        if not path.is_relative_to((base / "inputs").resolve()):
            raise ValueError("Frozen input escapes input directory")
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            if entry["kind"] != "recipe":
                raise ValueError("Required current round receipt absent: " + name) from None
            provenance.append(dict(path=entry["path"], expected_sha256=entry["sha256"],
                                   status="UNKNOWN_LOCAL_ARTIFACT_ABSENT", check_complete=True, kind="recipe"))
            continue
        digest = hashlib.sha256(raw).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError("Frozen input SHA mismatch: " + name)
        provenance.append(dict(path=entry["path"], sha256=digest, bytes=len(raw), kind=entry["kind"]))
        if entry["kind"] == "receipt":
            r = next(f"R{i}" for i in range(10, 15) if f"_r{i}_" in name)
            rounds[r] = json.loads(raw)
        elif entry["kind"] == "recipe":
            raw.decode("utf-8")  # validation only; never exec/import recipe
    if set(rounds) != {f"R{i}" for i in range(10, 15)}:
        raise ValueError("All five current frozen round receipts required")
    if not any(Path(r["path"]).name == "run_live_autoresearch_r7_multiflow_shootout_20261024.py" for r in provenance):
        provenance.append(dict(path="shared_R7_probe_recipe_not_in_manifest", status="UNKNOWN_LOCAL_ARTIFACT_ABSENT",
                               check_complete=True, kind="recipe"))
    return rounds, provenance


def _descriptive(row, round_id, *, resamples):
    obs, knobs = row["observation"], row["candidate_knobs"]
    rtts = row.get("rtts_ms", [])
    expected_attempts = 40 if round_id == "R12" else 20
    retained = len(rtts)
    reported = row.get("rtt_sample_count")
    if rtts and (retained != reported or not np.isfinite(sample(rtts)).all()):
        raise ValueError("RTT count/content inconsistent")
    if rtts and not math.isclose(100*(expected_attempts-retained)/expected_attempts, obs["packet_loss_pct"], abs_tol=0.001):
        raise ValueError("RTT loss inconsistent with frozen recipe attempts")
    dl, ul = row["dl_goodput_mbps"], row["ul_goodput_mbps"]
    return dict(round_id=round_id, iteration=row["commit"], declared_repetitions=obs["repetitions"],
                raw_per_rep_arrays_available=False, identified_pair_ids_available=False,
                attempted_RTT_per_recipe=expected_attempts, reported_received_RTT=reported, raw_received_RTT=retained,
                packet_loss_pct=obs["packet_loss_pct"], lossful=obs["packet_loss_pct"] > 0,
                restoration_reported=obs["restoration_verified"],
                dl_goodput_mbps=dl, ul_goodput_mbps=ul, total_goodput_mbps=row["total_bidir_goodput_mbps"],
                ul_dl_ratio=ul/dl if dl > 0 else None, ul_fraction=ul/(ul+dl) if ul+dl > 0 else None,
                programmed_distance_m=knobs.get("distance_meters"),
                be_aql_us=[knobs["be_low_us"], knobs["be_high_us"]], aql_threshold_us=knobs["aql_threshold_us"],
                reported_p95_ms=obs["p95_rtt_ms"], reported_p99_ms=obs["p99_rtt_ms"],
                conditional_tail_intervals=[conditional_tail_bootstrap(rtts, quantile=q, resamples=resamples) for q in (0.95, 0.99)] if rtts else None,
                raw_RTT_sorted=all(a <= b for a, b in zip(rtts, rtts[1:])) if rtts else None,
                tail_status="RAW_RTT_ABSENT_NOT_RECONSTRUCTED" if not rtts else "CONDITIONAL_RECEIVED_PINGS_ONLY",
                wilcoxon_status="UNIDENTIFIED_PAIRING")


def build_analysis(*, resamples=1999):
    rounds, provenance = load_frozen_rounds()
    descriptions, contrasts = [], []
    # Family chosen without p-value selection: ALL unordered within-round pairs
    # across R10-R14. Missing R14 raw-data tests stay in the Holm denominator.
    for round_id, data in rounds.items():
        rows = data["iterations"]
        descriptions.extend(_descriptive(row, round_id, resamples=resamples) for row in rows)
        for a, b in combinations(rows, 2):
            available = bool(a.get("rtts_ms")) and bool(b.get("rtts_ms"))
            result = mwu_contrast(a["rtts_ms"], b["rtts_ms"]) if available else dict(p_value=None, status="RAW_RTT_ABSENT")
            contrasts.append(dict(round_id=round_id, control=a["commit"], treatment=b["commit"],
                                  causal_effect="NOT_IDENTIFIED",
                                  paired_wilcoxon=paired_wilcoxon(a["rtts_ms"], b["rtts_ms"]) if available else dict(status="RAW_RTT_ABSENT", p_value=None),
                                  **result))
    for row, p in zip(contrasts, holm_adjust([c["p_value"] for c in contrasts])):
        row["holm_p_value"] = p
        row["family_size_including_missing"] = len(contrasts)
    round_families = []
    for round_id in rounds:
        members = [c for c in contrasts if c["round_id"] == round_id]
        for row, p in zip(members, holm_adjust([c["p_value"] for c in members])):
            row["within_round_holm_p_value"] = p
        round_families.append(dict(round_id=round_id, planned_contrasts=len(members),
                                   missing=sum(c["p_value"] is None for c in members)))
    r12 = [r for r in descriptions if r["round_id"] == "R12"]
    r13 = rounds["R13"]["iterations"]
    # Recorded policy deltas; never interpret programmed distance as a measured
    # physical link length, or a one-window sequential contrast as randomized.
    timing = []
    for ai, bi, label in [(1, 2, "TIMING_0_TO_1500"), (2, 3, "TIMING_1500_TO_3000"), (3, 4, "BE_AND_THRESHOLD_SCALING_AT_3000")]:
        a, b = r13[ai], r13[bi]
        changed = {k: [a["candidate_knobs"].get(k), b["candidate_knobs"].get(k)] for k in sorted(set(a["candidate_knobs"]) | set(b["candidate_knobs"]))
                   if k not in ("name", "description") and a["candidate_knobs"].get(k) != b["candidate_knobs"].get(k)}
        timing.append(dict(label=label, control=a["commit"], treatment=b["commit"], changed_declared_fields=changed,
                           total_goodput_delta_mbps=b["total_bidir_goodput_mbps"]-a["total_bidir_goodput_mbps"],
                           reported_p95_delta_ms=b["observation"]["p95_rtt_ms"]-a["observation"]["p95_rtt_ms"],
                           interpretation="Sequential within-bench association; time/order and other context unresolved, no outdoor propagation or gain proof"))
    cross_crypto = []
    for ar, ai, bi in [("R11", 4, 1), ("R12", 3, 2)]:
        a, b = rounds[ar]["iterations"][ai], rounds["R14"]["iterations"][bi]
        fields = set(a["candidate_knobs"]) | set(b["candidate_knobs"])
        equal = all(a["candidate_knobs"].get(k) == b["candidate_knobs"].get(k) for k in fields-{"name", "description"})
        cross_crypto.append(dict(control=a["commit"], treatment=b["commit"], reported_numeric_knobs_equal=equal,
                                 control_dl_ul_mbps=[a["dl_goodput_mbps"], a["ul_goodput_mbps"]],
                                 R14_dl_ul_mbps=[b["dl_goodput_mbps"], b["ul_goodput_mbps"]],
                                 p_value=None, causal_crypto_effect="NOT_IDENTIFIED_CROSS_ROUND_CONFOUNDING_AND_NO_CIPHER_READBACK"))
    power = [required_sample_size(d, design=design, family_size=family, dropout=0.1)
             for design in ("paired", "independent") for family in (1, 3, len(contrasts)) for d in (0.2, 0.5, 0.8)]
    shared_probe_available = any(r["path"].endswith("run_live_autoresearch_r7_multiflow_shootout_20261024.py") and "sha256" in r for r in provenance)
    return dict(schema_version=1, status="OFFLINE_EXPLORATORY_CONDITIONAL_ANALYSIS", automatic_execution_allowed=False,
                sources=provenance, software_versions=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                descriptions=descriptions, contrasts=contrasts,
                multiplicity=dict(family="All unordered within-round RTT distribution contrasts R10-R14, including missing tests", size=len(contrasts), method="Holm", missing_tests=sum(c["p_value"] is None for c in contrasts),
                                  complete_within_round_families=round_families, primary_correction="Global52, secondary per-round values explicitly named",
                                  CI_scope="Marginal 95% HL/tail intervals are NOT simultaneous familywise intervals"),
                R12=dict(windows=len(r12), attempted_each=40, declared_reps_each=4, raw_received_counts=[r["raw_received_RTT"] for r in r12],
                         lossful_iterations=[r["iteration"] for r in r12 if r["lossful"]], independent_physical_repetitions_identified=False,
                         attempted_count_provenance="NEW_RECIPE_N40_AND_SHARED_PROBE_4x10" if shared_probe_available else "DECLARED_NEW_ROUND_N40_SHARED_PROBE_UNKNOWN_LOCAL_ARTIFACT_ABSENT",
                         shared_probe_verified=shared_probe_available,
                         recipe_comment_discrepancy="Opening comment says 5x8; actual call repetitions=4 and receipt reports4; per-rep received counts are NOT retained. Shared R7 probe loops10 pings (lines63/71) only if shared_probe_verified=true"),
                R13=dict(contrasts=timing, distance_interpretation="Programmed coverage timing, not measured physical distance"),
                R14=dict(associated_CPE_labels=list(rounds["R14"].get("cpes_associated", {})), measured_three_CPE_claim=False,
                         raw_RTT_available=False, encryption="none", encryption_status="DECLARED_BY_FROZEN_RECIPE_NOT_EFFECTIVE_READBACK",
                         prior_R10_R13_encryption="psk2", prior_encryption_status="INFERRED_PRIOR_WPA2_CONTEXT_NOT_PER_WINDOW_READBACK",
                         recipe_source_evidence="R14 precondition WPA2-PSK comment then encryption none and restoration_verified_wpa2_loco195; not a cipher measurement",
                         matched_declared_policy_cross_round=cross_crypto),
                planning=dict(kind="PROSPECTIVE_STANDARDIZED_EFFECT_SENSITIVITY_NOT_OBSERVED_POWER", calculations=power,
                              n4_independent_units_sensitivity=[dict(assumed_d=d, paired_power=planning_power(4, d), independent_per_arm_power=planning_power(4, d, design="independent")) for d in (0.2,0.5,0.8)],
                              limits="Illustrative normal paired/independent t models; d_z vs d differs; n counts independently randomized windows/pairs, NOT pings or declared unretained reps; no physical power certified"),
                limitations=["Adaptive sequential one-link observations: causal effects and independent experimental replication not identified",
                             "Sorted rounded pooled RTTs have no time/rep/pair IDs; Wilcoxon is not run on production arrays",
                             "MWU/HL/bootstrap assume iid independent pings only as a conditional sensitivity model, not verified here",
                             "Lossful windows remain; bootstrap/HL for received pings do not identify unconditional lost-packet latency",
                             "p99 with20/39/40 responses is sparse; bootstrap cannot invent unseen tails or physical replication",
                             "R14 direction balance changes are descriptive; no three-CPE, cipher-effect or crypto-offload claim"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ARTIFACTS / "wave_j_analysis.json")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.parent != ARTIFACTS.resolve() or not output.name.startswith("wave_j_") or output.suffix != ".json":
        raise ValueError("Only new Wave J artifacts allowed")
    result = build_analysis()
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps(dict(status=result["status"], windows=len(result["descriptions"]), contrasts=len(result["contrasts"]), output=str(output))))


if __name__ == "__main__":
    main()
