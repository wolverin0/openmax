"""Offline R15 ping sensitivity and exact identified-block crossover analysis.

No acquisition, live-file discovery, recipe execution, or policy actuation.
Exact paired inference assumes independent blocks and sign-exchangeable,
symmetric treatment differences. Neither IDs nor rank diagnostics prove this.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
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

from analysis.statistics.fmx_r10_to_r14_causal_and_power_analysis import (
    conditional_tail_bootstrap, holm_adjust, mwu_contrast, probability, sample,
)
from analysis.statistics.fmx_autoresearch_statistical_audit import required_sample_size

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts/autoresearch/waves_mnop_20261024"


def _differences(values):
    result = sample(values, minimum=1)
    if len(result) > 60:
        raise ValueError("Exact sign-rank API bounded to60 independent blocks")
    return result


@lru_cache(maxsize=256)
def _rank_sum_counts(weights):
    counts = [1] + [0]*sum(weights)
    reachable = 0
    for weight in weights:
        for total in range(reachable, -1, -1):
            counts[total+weight] += counts[total]
        reachable += weight
    return tuple(counts)


def exact_signed_rank(differences):
    """Exact conditional sign enumeration, including tied absolute ranks/zeros.

    Wilcox zero rule: remove exact zeros, then midrank absolute nonzero values.
    Doubled ranks are integers; subset DP counts all2**m sign assignments exactly.
    No asymptotic normal approximation or scipy exact-with-ties shortcut.
    """
    data = _differences(differences)
    nonzero = data[data != 0]
    if not len(nonzero):
        return dict(p_value=1.0, positive_rank_sum=0.0, negative_rank_sum=0.0,
                    nonzero_blocks=0, zero_blocks=len(data), sign_assignments=1,
                    method="EXACT_CONDITIONAL_SIGN_RANK_DP_WILCOX_ZEROS")
    doubled = np.rint(2*stats.rankdata(np.abs(nonzero), method="average")).astype(int)
    weights = tuple(sorted(int(x) for x in doubled))
    counts = _rank_sum_counts(weights)
    observed = int(doubled[nonzero > 0].sum())
    total = sum(weights)
    distance = abs(2*observed-total)
    extreme = sum(count for value, count in enumerate(counts) if abs(2*value-total) >= distance)
    return dict(p_value=extreme/(2**len(nonzero)), positive_rank_sum=observed/2,
                negative_rank_sum=(total-observed)/2, nonzero_blocks=len(nonzero),
                zero_blocks=len(data)-len(nonzero), sign_assignments=2**len(nonzero),
                minimum_possible_two_sided_p=2**(1-len(nonzero)),
                method="EXACT_CONDITIONAL_SIGN_RANK_DP_WILCOX_ZEROS")


def exact_sign_test(differences):
    data = _differences(differences)
    positive, negative = int((data > 0).sum()), int((data < 0).sum())
    n = positive+negative
    p = float(stats.binomtest(positive, n, 0.5, alternative="two-sided").pvalue) if n else 1.0
    return dict(p_value=p, positive=positive, negative=negative, zeros=len(data)-n,
                method="EXACT_BINOMIAL_CONDITIONAL_NONZERO_SIGNS",
                assumptions="Independent blocks; under null nonzero signs equally likely. Discarded zeros disclosed; arbitrary asymmetric point masses are not a median-only null.")


def paired_hl_interval(differences, alpha=0.05):
    """Walsh pseudomedian and conservative hull of exact test-inversion set.

    Signed-rank statistic/tie distribution changes only at Walsh averages,
    including diagonal averages (zero crossings). Evaluate every breakpoint and
    open cell, plus both unbounded tails. This handles ties/zeros using the SAME
    exact test. Convex hull may include rejected gaps, so never understates set.
    Coverage is conditional on independent symmetric location-shift differences;
    Walsh averages are NOT counted as independent replication.
    """
    alpha = probability(alpha)
    data = _differences(differences)
    walsh = np.sort(np.array([a/2+b/2 for i, a in enumerate(data) for b in data[i:]]))
    if not np.isfinite(walsh).all():
        raise ValueError("Nonfinite Walsh arithmetic")
    # Stable median avoids summing two near-maximum finite floats.
    estimate = float(walsh[(len(walsh)-1)//2]/2 + walsh[len(walsh)//2]/2)
    points = np.unique(walsh)
    accepted = []
    for point in points:
        shifted = data-point
        if not np.isfinite(shifted).all():
            raise ValueError("Nonfinite shift arithmetic")
        if exact_signed_rank(shifted)["p_value"] > alpha:
            accepted.append((float(point), float(point)))
    for left, right in zip(points, points[1:]):
        midpoint = float(left/2+right/2)
        if exact_signed_rank(data-midpoint)["p_value"] > alpha:
            accepted.append((float(left), float(right)))
    # Outside every Walsh point all differences have one sign, no zeros/ties
    # affecting the extreme-tail probability2/2**n.
    tails_accepted = 2**(1-len(data)) > alpha
    if tails_accepted:
        interval = [None, None]
    elif accepted:
        interval = [min(v[0] for v in accepted), max(v[1] for v in accepted)]
    else:
        # Discrete sign tests can have an empty inverted set at unusual alpha.
        interval = None
    return dict(estimate=estimate, confidence=1-alpha, interval=interval,
                method="WALSH_PSEUDOMEDIAN_EXACT_SIGN_RANK_INVERSION_CONSERVATIVE_HULL",
                independent_blocks=len(data), derived_Walsh_count=len(walsh),
                breakpoints_evaluated=len(points), accepted_cells=len(accepted),
                null_endpoint_convention="None endpoint=-/+infinity; intervalNone=empty acceptance set",
                assumptions="Independent identically distributed symmetric block differences around a common shift; no physical randomization certified")


def _identifier(value, name):
    if type(value) is not int or not 0 <= value <= 10**9:
        raise ValueError(name+" must be a genuine nonnegative integer ID")
    return value


def _validate_rows(rows):
    if not isinstance(rows, list) or len(rows) > 512:
        raise ValueError("Bounded list of normalized identified block rows required")
    seen, result = set(), []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Block row object required")
        block = _identifier(row.get("block_index"), "block_index")
        step = _identifier(row.get("crossover_step"), "crossover_step")
        if (block, step) in seen:
            raise ValueError("Duplicate(block,step) identity")
        seen.add((block, step))
        treatment = row.get("treatment_id")
        if not isinstance(treatment, str) or not treatment.strip() or treatment.strip() != treatment:
            raise ValueError("Explicit treatment identity required")
        obs = row.get("observation")
        if not isinstance(obs, dict):
            raise ValueError("Explicit observation object required")
        if "period_index" in row and row["period_index"] is not None:
            _identifier(row["period_index"], "period_index")
        result.append(row)
    return sorted(result, key=lambda row: (row["block_index"], row["crossover_step"]))


def _metric(row, name):
    value = row["observation"].get(name)
    if value is None:
        return None
    result = float(sample([value], minimum=1)[0])
    if result < 0:
        raise ValueError("Physical outcome must be nonnegative")
    return result


def _quality_summary(rows):
    counts = Counter()
    for row in rows:
        obs = row["observation"]
        value = obs.get("packet_loss_pct")
        if value is None:
            counts["loss_unknown_rows"] += 1
        else:
            value = float(sample([value], minimum=1)[0])
            if not 0 <= value <= 100:
                raise ValueError("Invalid supplied loss percentage")
            counts["lossful_rows"] += value > 0
        drops = obs.get("station_drops")
        if drops is None:
            counts["station_drop_unknown_rows"] += 1
        else:
            _identifier(drops, "station_drops")
            counts["station_drop_rows"] += drops > 0
        restored = obs.get("restoration_verified")
        if restored is None:
            counts["restoration_unknown_rows"] += 1
        elif type(restored) is not bool:
            raise ValueError("Invalid supplied restoration boolean")
        else:
            counts["restoration_false_rows"] += not restored
    return dict(counts)


def crossover_design_diagnostics(rows, control_id, treatment_id, metric):
    """Read-only descriptive design checks, no carryover/causal certification."""
    by_block = defaultdict(list)
    for row in rows:
        by_block[row["block_index"]].append(row)
    periods, sequences, model_rows, gaps = defaultdict(list), Counter(), [], []
    for block, group in sorted(by_block.items()):
        sequence = "".join("A" if row["treatment_id"] == control_id else "B" if row["treatment_id"] == treatment_id else "?" for row in group)
        sequences[sequence] += 1
        previous = None
        for row in group:
            if previous and row["crossover_step"] != previous["crossover_step"]+1:
                gaps.append(dict(block_index=block, before=previous["crossover_step"], after=row["crossover_step"]))
            period = row.get("period_index")
            if period is None:
                period = row["crossover_step"]
            value = _metric(row, metric)
            if value is not None:
                periods[period].append(value)
                contiguous = previous is not None and row["crossover_step"] == previous["crossover_step"]+1
                model_rows.append((block, period, row["treatment_id"] == treatment_id,
                                   previous["treatment_id"] == treatment_id if contiguous else False))
            previous = row
    block_ids = sorted({row[0] for row in model_rows})
    period_ids = sorted({row[1] for row in model_rows})
    names = ["intercept"]+[f"block_{b}" for b in block_ids[1:]]+[f"period_{p}" for p in period_ids[1:]]+["current_B", "previous_observed_B_if_contiguous"]
    matrix = np.array([[1]+[int(b == value) for value in block_ids[1:]]+[int(p == value) for value in period_ids[1:]]+[int(t), int(lag)] for b,p,t,lag in model_rows], dtype=float)
    rank = int(np.linalg.matrix_rank(matrix)) if len(matrix) else 0
    estimable = {}
    for label, column in (("current_treatment", len(names)-2), ("previous_treatment_proxy", len(names)-1)):
        estimable[label] = bool(len(matrix) and rank > np.linalg.matrix_rank(np.delete(matrix, column, axis=1)))
    return dict(sequences=dict(sequences), period_metric_means=[dict(period_index=p, observed_rows=len(v), mean=math.fsum(v)/len(v)) for p,v in sorted(periods.items())],
                step_gaps=gaps, design=dict(columns=names, rows=len(model_rows), rank=rank, full_column_rank=rank == len(names), conditional_column_estimability=estimable),
                interpretation="Block+period+current-treatment+previous-B design rank; no p-value or causal carryover estimate. First/gap lag encoded0, not known washout; arbitrary unobserved carryover remains UNKNOWN.")


def audit_blocked_crossover(rows, control_id, treatment_id, *, metric="p95_rtt_ms", alpha=0.05, evidence_kind="provided_identified_rows"):
    """Aggregate equal-weight means per treatment/block before paired inference.

    Repeated policies such as ABBA are allowed with balanced A/B counts. Missing
    metric, missing arm, other treatment or unequal counts exclude the block and
    remain reported. Lossful observations are NOT silently discarded here;
    analysis/quality and physical acceptance are separate.
    """
    alpha = probability(alpha)
    if (any(not isinstance(v, str) or not v or v.strip() != v for v in (control_id,treatment_id))
            or control_id == treatment_id):
        raise ValueError("Distinct explicit control/treatment IDs required")
    if metric not in {"goodput_rx_mbps", "p50_rtt_ms", "p95_rtt_ms", "p99_rtt_ms"}:
        raise ValueError("Unsupported declared outcome")
    rows = _validate_rows(rows)
    if not rows:
        return dict(status="NOT_AVAILABLE_NO_IDENTIFIED_BLOCKS", paired_results=None,
                    evidence_kind=evidence_kind, automatic_execution_allowed=False)
    by_block = defaultdict(list)
    for row in rows:
        by_block[row["block_index"]].append(row)
    pairs, excluded, sequence_deltas = [], [], defaultdict(list)
    for block, group in sorted(by_block.items()):
        a = [row for row in group if row["treatment_id"] == control_id]
        b = [row for row in group if row["treatment_id"] == treatment_id]
        values_a, values_b = [_metric(r, metric) for r in a], [_metric(r, metric) for r in b]
        reason = ("OTHER_TREATMENT_IN_BLOCK" if len(a)+len(b) != len(group) else
                  "MISSING_ARM" if not a or not b else "UNBALANCED_WITHIN_BLOCK_COUNTS" if len(a) != len(b) else
                  "MISSING_OUTCOME" if None in values_a+values_b else None)
        if reason:
            excluded.append(dict(block_index=block, reason=reason, control_rows=len(a), treatment_rows=len(b)))
            continue
        ma, mb = math.fsum(values_a)/len(a), math.fsum(values_b)/len(b)
        delta = mb-ma
        sequence = "".join("A" if r["treatment_id"] == control_id else "B" for r in group)
        sequence_deltas[sequence].append(delta)
        pairs.append(dict(block_index=block, control_mean=ma, treatment_mean=mb, difference=delta,
                          control_steps=[r["crossover_step"] for r in a], treatment_steps=[r["crossover_step"] for r in b], sequence=sequence))
    differences = [row["difference"] for row in pairs]
    return dict(status="CALCULATED_CONDITIONAL_IDENTIFIED_BLOCK_MODEL" if pairs else "NO_COMPLETE_BALANCED_BLOCKS", evidence_kind=evidence_kind,
                metric=metric, unit="One genuine independent block; average repeated treatment measurements within block first",
                aggregation="Equal-weight arithmetic means of window outcomes within each treatment/block; mean windowp95 is NOT pooled-pingp95; no ping-position pairing",
                complete_blocks=len(pairs), excluded_blocks=excluded, pairs=pairs,
                quality_observations=_quality_summary(rows),
                wholly_missing_blocks="UNKNOWN_WITHOUT_EXPLICIT_EXPECTED_SCHEDULE",
                primary_paired_test="EXACT_SIGNED_RANK", sign_test_role="SENSITIVITY_NOT_ADDITIONAL_UNADJUSTED_CONFIRMATORY_CLAIM",
                paired_results=dict(wilcoxon=exact_signed_rank(differences), sign_test=exact_sign_test(differences), hl=paired_hl_interval(differences, alpha)) if pairs else None,
                sequence_differences=[dict(sequence=k, blocks=len(v), mean_difference=math.fsum(v)/len(v), median_difference=float(np.median(v))) for k,v in sorted(sequence_deltas.items())],
                design_diagnostics=crossover_design_diagnostics(rows, control_id, treatment_id, metric),
                automatic_execution_allowed=False, physical_or_causal_acceptance=False,
                limits="Pairing/independence/randomization/washout are not proved by IDs; exclusions disclosed, no dropout imputation. Sign-rank/HL assume symmetric independent block differences; different sequences/periods may confound the aggregate.")


def _frozen_inputs():
    manifest = json.loads((ARTIFACTS/"inputs_manifest.json").read_text(encoding="utf-8"))
    needed = {"lap120_loco195_r15_wpa2_asym_n40_20261024.json", "lap120_loco195_r15_wpa2_asym_n40_results.tsv", "run_live_autoresearch_r15_wpa2_asym_n40_20261024.py", "normalized_r1_to_r14_measurements_20261024.json"}
    sources, raw_by_name = [], {}
    for ref in manifest:
        name = Path(ref["path"]).name
        if name not in needed:
            continue  # No discovery/following other live measurement sources.
        path = (ROOT/ref["path"]).resolve()
        if not path.is_relative_to((ARTIFACTS/"inputs").resolve()):
            raise ValueError("Frozen input escapes input directory")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != ref["sha256"]:
            raise ValueError("Frozen source mismatch: "+name)
        sources.append(dict(path=ref["path"], sha256=ref["sha256"], bytes=len(raw)))
        raw_by_name[name] = raw
    if set(raw_by_name) != needed:
        raise ValueError("Frozen currentR15 sources/prior normalized output missing")
    return raw_by_name, sources


def build_audit(*, resamples=1999):
    from orchestration.autoresearch.fmx_offline_data import load_blocked_crossover_blocks
    raw, sources = _frozen_inputs()
    data = json.loads(raw["lap120_loco195_r15_wpa2_asym_n40_20261024.json"])
    prior = json.loads(raw["normalized_r1_to_r14_measurements_20261024.json"])
    recipe_text = raw["run_live_autoresearch_r15_wpa2_asym_n40_20261024.py"].decode("utf-8")
    tsv = list(csv.DictReader(raw["lap120_loco195_r15_wpa2_asym_n40_results.tsv"].decode("utf-8").splitlines(), delimiter="\t"))
    rows = data["iterations"]
    if len(rows) != len(tsv) or {r["commit"] for r in rows} != {r["commit"] for r in tsv}:
        raise ValueError("JSON/TSV window identities disagree")
    descriptions = []
    for row in rows:
        rtts, obs = row["rtts_ms"], row["observation"]
        if len(rtts) != row["rtt_sample_count"] or len(rtts) != 40 or obs["repetitions"] != 4:
            raise ValueError("R15N40/fourreported-rep contract mismatch")
        line = next(r for r in tsv if r["commit"] == row["commit"])
        if not math.isclose(float(line["p95_rtt_ms"]), obs["p95_rtt_ms"], abs_tol=.0051):
            raise ValueError("JSON/TSV quantiles differ beyond display precision")
        descriptions.append(dict(iteration=row["commit"], received_RTT=40, declared_repetitions=4, packet_loss_pct=obs["packet_loss_pct"],
                                 restoration_reported=obs["restoration_verified"], station_drops_reported=obs["station_drops"],
                                 per_rep_arrays_retained=False, raw_block_IDs_retained=bool(row.get("repetition_blocks")),
                                 total_goodput_mbps=row["total_bidir_goodput_mbps"], dl_goodput_mbps=row["dl_goodput_mbps"], ul_goodput_mbps=row["ul_goodput_mbps"],
                                 tail_intervals=[conditional_tail_bootstrap(rtts, quantile=q, resamples=resamples) for q in (.95,.99)]))
    contrasts = [dict(control=a["commit"], treatment=b["commit"], **mwu_contrast(a["rtts_ms"], b["rtts_ms"])) for a,b in combinations(rows, 2)]
    for row,p in zip(contrasts,holm_adjust([r["p_value"] for r in contrasts])):
        row.update(holm_p_value=p, family_size=len(contrasts), inference="CONDITIONAL_IID_RECEIVED_PINGS_NOT_INDEPENDENT_PHYSICAL_TRIALS")
    blocks = load_blocked_crossover_blocks(data)
    actual_pairs = audit_blocked_crossover(blocks, rows[0]["commit"], rows[1]["commit"], evidence_kind="FROZEN_R15_ONLY_NO_OTHER_LIVE_ROUND_READ")
    planned = [required_sample_size(d, design=design, family_size=family, dropout=.1) for d in (.2,.5,.8) for design in ("paired","independent") for family in (1,6)]
    return dict(schema_version=1, status="OFFLINE_R15_CONDITIONAL_AND_CROSSOVER_API_AUDIT", sources=sources,
                software_versions=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                observed_R15_windows=len(rows), observed_TSV_rows=len(tsv), prior_records=len(prior["records"]), combined_records=len(prior["records"])+len(rows),
                requested_count=90, actual_count=len(prior["records"])+len(rows), missing_fifth_R15="NOT_IN_FROZEN_DATA_NOT_INVENTED",
                descriptions=descriptions, R15_contrasts=contrasts, multiplicity="All6within-R15 unordered MWU contrasts; Holm; offline family not preregistered physical design; marginal intervals not simultaneous",
                actual_crossover=actual_pairs, independent_physical_repetition_identified=False,
                recipe_read_as_text_only=True, recipe_contains_WPA2_declaration="psk2" in recipe_text or "WPA2" in recipe_text,
                prospective_power_sensitivity=planned, small_n_detectability=[dict(nonzero_blocks=n, minimum_exact_two_sided_p=2**(1-n)) for n in range(1,9)],
                numerical_reuse_sources=[dict(path=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [ROOT/"analysis/statistics/fmx_r10_to_r14_causal_and_power_analysis.py",ROOT/"analysis/statistics/fmx_autoresearch_statistical_audit.py"]],
                automatic_execution_allowed=False, physical_or_causal_acceptance=False,
                limits=["R15fourreported reps lack raw repetition arrays or pairing IDs;40pings are subsamples, not40independent physical experiments",
                        "R15actual crossover is unavailable, not synthesized from sortedRTTs; exact API demonstration uses explicitly labeled synthetic fixtures only",
                        "Balanced within-block means permit ABBA; unbalanced/missing blocks disclosed, quality failures not silently filtered",
                        "Exact signedrank and WalshCI conditional on independent symmetric block differences, not proven by IDs/design rank; carryover remains possible",
                        "Power is prospective assumed-effect sensitivity for independent blocks/windows, never observed power or a scheduled physical trial"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ARTIFACTS/"wave_o_analysis.json")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.parent != ARTIFACTS.resolve() or not output.name.startswith("wave_o_") or output.suffix != ".json":
        raise ValueError("Only new WaveOowned artifact outputs allowed")
    result = build_audit()
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, allow_nan=False);handle.write("\n")
    print(json.dumps(dict(status=result["status"], windows=result["observed_R15_windows"], actual_crossover=result["actual_crossover"]["status"])))


if __name__ == "__main__":
    main()
