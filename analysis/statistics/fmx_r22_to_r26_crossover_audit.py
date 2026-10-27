"""Pure offline exact crossover audit; no actuator or live-source discovery.

Families were frozen before new outcome inspection: new162, combined324,
and the explicitly requested R25 ten. None substitutes for another.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy

from analysis.statistics.fmx_r10_to_r14_causal_and_power_analysis import holm_adjust, sample
from analysis.statistics.fmx_r15_and_crossover_statistical_audit import (
    exact_sign_test, exact_signed_rank, paired_hl_interval,
)
from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import (
    exact_walsh_confidence_set, multilevel_design_diagnostics, schedule_agreement,
)

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "artifacts/autoresearch/waves_uvwx_20261024"
NEW_ROUNDS = (22, 23, 24, 25, 26)
CROSSED_ROUNDS = (16, 18, 19, 20, 21, *NEW_ROUNDS)
METRICS = ("goodput_rx_mbps", "p50_rtt_ms", "p95_rtt_ms", "p99_rtt_ms", "ul_goodput_mbps", "jain_fairness")
FOCUSED_METRICS = METRICS[1:]
HOOKS = ("short_retry_limit", "long_retry_limit", "force_tx_status", "ani_enable", "airtime_flags", "fq_limit")
ANNOTATIONS = {"name", "description", "complexity_cost"}


def _binding(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def frozen_new_receipts():
    """Do not follow the manifest's original source pointers."""
    manifest = json.loads((BASE / "inputs_manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, list) or len(manifest) != 15:
        raise ValueError("Expected15 frozen U-V-W-X files")
    receipts, refs = {}, []
    for ref in manifest:
        path = (ROOT / ref["path"]).resolve()
        if not path.is_relative_to((BASE / "inputs").resolve()) or ref["round"] not in NEW_ROUNDS:
            raise ValueError("Only owned frozen new inputs allowed")
        bound = _binding(path)
        if bound["sha256"] != ref["sha256"] or bound["bytes"] != ref["bytes"]:
            raise ValueError("Frozen source bytes changed")
        refs.append(bound | dict(round=ref["round"]))
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            if ref["round"] in receipts:
                raise ValueError("Duplicate receipt round")
            receipts[ref["round"]] = json.loads(text)
        # Other files are validated text only, never imported or executed.
    if set(receipts) != set(NEW_ROUNDS):
        raise ValueError("Missing new frozen receipt")
    return receipts, refs


def validate_crossed_rows(rows):
    if not isinstance(rows, list) or not 1 <= len(rows) <= 5000:
        raise ValueError("Bounded explicit block rows required")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or row.get("round_id") not in {f"R{n}" for n in CROSSED_ROUNDS}:
            raise ValueError("Identified crossed round required; R17 is sequential")
        for key in ("block_index", "crossover_step"):
            if type(row.get(key)) is not int or row[key] < 0:
                raise ValueError("Genuine nonnegative block/step IDs required")
        identity = (row["round_id"], row["block_index"], row["crossover_step"])
        if identity in seen:
            raise ValueError("Duplicate round/block/step")
        seen.add(identity)
        if not isinstance(row.get("treatment_id"), str) or not row["treatment_id"].strip():
            raise ValueError("Explicit treatment required")
        if not isinstance(row.get("observation"), dict):
            raise ValueError("Observation object required")
    return rows


def _metric(row, metric):
    if metric not in METRICS:
        raise ValueError("Unknown declared outcome")
    value = row.get(metric) if metric == "ul_goodput_mbps" else row["observation"].get(metric)
    if value is None:
        return None
    value = float(sample([value], minimum=1)[0])
    if value < 0 or (metric == "jain_fairness" and value > 1):
        raise ValueError("Invalid physical metric")
    return value


def _quality(rows):
    counts = Counter()
    for row in rows:
        obs = row["observation"]
        loss = obs.get("packet_loss_pct")
        if loss is None:
            counts["loss_unknown_rows"] += 1
        else:
            loss = float(sample([loss], minimum=1)[0])
            if not 0 <= loss <= 100:
                raise ValueError("Invalid loss percentage")
            counts["lossful_rows"] += loss > 0
        for key in ("restoration_verified", "station_drops"):
            if key not in obs or obs[key] is None:
                counts[key + "_unknown_rows"] += 1
            elif key == "restoration_verified":
                if type(obs[key]) is not bool:
                    raise ValueError("Invalid restoration flag")
                counts["restoration_false_rows"] += not obs[key]
            else:
                if type(obs[key]) is not int or obs[key] < 0:
                    raise ValueError("Invalid station drops")
                counts["station_drop_rows"] += obs[key] > 0
    return dict(counts)


def paired_contrast(rows, control, treatment, metric):
    """Equal-weight within-arm/block means, never pair ping positions."""
    validate_crossed_rows(rows)
    if control == treatment:
        raise ValueError("Distinct arms required")
    rounds = {r["round_id"] for r in rows}
    if len(rounds) != 1:
        raise ValueError("One round per contrast")
    subset = [r for r in rows if r["treatment_id"] in (control, treatment)]
    groups = defaultdict(list)
    for row in rows:
        groups[row["block_index"]]  # Retain a wholly missing pair within known block.
    for row in subset:
        groups[row["block_index"]].append(row)
    pairs, excluded = [], []
    for block, group in sorted(groups.items()):
        a = [r for r in group if r["treatment_id"] == control]
        b = [r for r in group if r["treatment_id"] == treatment]
        va, vb = [_metric(r, metric) for r in a], [_metric(r, metric) for r in b]
        reason = ("MISSING_ARM" if not a or not b else "UNBALANCED_WITHIN_BLOCK_COUNTS" if len(a) != len(b)
                  else "MISSING_OUTCOME" if None in va + vb else None)
        if reason:
            excluded.append(dict(block_index=block, reason=reason, control_rows=len(a), treatment_rows=len(b)))
            continue
        ma, mb = math.fsum(va) / len(va), math.fsum(vb) / len(vb)
        difference = mb - ma
        if not math.isfinite(difference):
            raise ValueError("Nonfinite block difference")
        pairs.append(dict(block_index=block, control_mean=ma, treatment_mean=mb, difference=difference,
                          control_steps=[r["crossover_step"] for r in a], treatment_steps=[r["crossover_step"] for r in b]))
    differences = [p["difference"] for p in pairs]
    result = dict(round_id=next(iter(rounds)), control=control, treatment=treatment, metric=metric,
        contrast_id=json.dumps([next(iter(rounds)), control, treatment, metric], separators=(",", ":")),
        complete_blocks=len(pairs), pairs=pairs, excluded_blocks=excluded, quality_observations=_quality(subset),
        unit="One supplied round-scoped matched block; mean repeated arm outcomes within block first",
        causal_or_physical_acceptance=False)
    if not differences:
        return result | dict(status="NO_COMPLETE_BALANCED_BLOCKS", wilcoxon=None, sign_test=None,
                             paired_HL=None, marginal95_confidence_set=None)
    return result | dict(status="CONDITIONAL_EXACT_BLOCK_ANALYSIS", wilcoxon=exact_signed_rank(differences),
        sign_test=exact_sign_test(differences), paired_HL=paired_hl_interval(differences),
        marginal95_confidence_set=exact_walsh_confidence_set(differences),
        Bonferroni324_confidence_set=exact_walsh_confidence_set(differences, .05 / 324))


def assign_families(contrasts, focused_treatments):
    """Complete predeclared families; missing p values remain in denominators."""
    new = [r for r in contrasts if int(r["round_id"][1:]) in NEW_ROUNDS]
    a, b, c = focused_treatments
    focused = [r for r in contrasts if r["round_id"] == "R25" and r["control"] == a
               and r["treatment"] in (b, c) and r["metric"] in FOCUSED_METRICS]
    if (len(contrasts), len(new), len(focused)) != (324, 162, 10):
        raise ValueError("Incomplete predeclared324/162/10 families")
    summaries = {}
    for label, members in (("Holm324", contrasts), ("Holm162", new), ("Holm10", focused)):
        p_values = [r["wilcoxon"]["p_value"] if r["wilcoxon"] else None for r in members]
        adjusted = holm_adjust(p_values)
        for row, p in zip(members, adjusted):
            row[label + "_p_value"] = p
            if members is not contrasts and row["pairs"]:
                row["Bonferroni" + str(len(members)) + "_confidence_set"] = exact_walsh_confidence_set(
                    [r["difference"] for r in row["pairs"]], .05 / len(members))
        summaries[label] = dict(tests=len(members), contrast_ids=[r["contrast_id"] for r in members],
                                rejected_05=sum(p is not None and p < .05 for p in adjusted),
                                minimum_adjusted_p=min((p for p in adjusted if p is not None), default=None))
    return summaries, focused


def unanimity_checks(focused):
    results = []
    for row in focused:
        values = [r["difference"] for r in row["pairs"]]
        lower_better = row["metric"] in ("p50_rtt_ms", "p95_rtt_ms", "p99_rtt_ms")
        improved = sum(v < 0 if lower_better else v > 0 for v in values)
        results.append(dict(contrast_id=row["contrast_id"], treatment=row["treatment"], metric=row["metric"],
            claimed_improved_blocks=12, observed_improved_blocks=improved,
            observed_equal_blocks=sum(v == 0 for v in values), observed_worse_blocks=len(values)-improved-sum(v == 0 for v in values),
            complete_blocks=len(values), claim_matches=improved == len(values) == 12,
            sign_assignments=row["wilcoxon"]["sign_assignments"] if row["wilcoxon"] else None,
            theoretical_n12_minimum_p=2 / 4096,
            raw_exact_signed_rank_p=row["wilcoxon"]["p_value"] if row["wilcoxon"] else None,
            raw_exact_sign_p=row["sign_test"]["p_value"] if row["sign_test"] else None,
            adjusted_p_values={k:row.get(k+"_p_value") for k in ("Holm10","Holm162","Holm324")},
            surviving_families={k:row.get(k + "_p_value") is not None and row[k + "_p_value"] < .05 for k in ("Holm10", "Holm162", "Holm324")},
            conditional_on_received_pings_and_block_assumptions=True))
    return results


def _canonical(value):
    if isinstance(value, dict):
        return {k:_canonical(v) for k,v in value.items() if k not in ANNOTATIONS}
    if isinstance(value, list):
        return [_canonical(v) for v in value]
    return value


def package_changes(a, b):
    """Declared coordinates only; absence and explicit None stay distinct."""
    changes = {}
    def walk(x, y, prefix):
        for key in sorted(set(x) | set(y)):
            path = prefix + key
            if key not in x or key not in y:
                changes[path] = [x[key] if key in x else {"state":"ABSENT"}, y[key] if key in y else {"state":"ABSENT"}]
            elif isinstance(x[key], dict) and isinstance(y[key], dict):
                walk(x[key], y[key], path + ".")
            elif x[key] != y[key]:
                changes[path] = [x[key], y[key]]
    walk(_canonical(a["candidate_knobs"]), _canonical(b["candidate_knobs"]), "")
    return changes


def _matrix_audit(matrix, columns):
    matrix = np.asarray(matrix, dtype=float)
    rank = int(np.linalg.matrix_rank(matrix))
    return dict(matrix=matrix.tolist(), columns=columns, rows=len(matrix), rank=rank,
                full_column_rank=rank == len(columns),
                conditional_column_estimability={name:bool(rank > np.linalg.matrix_rank(np.delete(matrix,i,axis=1))) for i,name in enumerate(columns)})


def factorial_boundaries(r24, r26):
    """Expose nuisance aliasing, never infer isolated effects from four arms."""
    aa, bb = r24["iterations"], r26["iterations"]
    if len(aa) != 4 or len(bb) != 4:
        raise ValueError("Four explicit arms required")
    nominal, full = [], []
    base_retry = (aa[0]["short_retry_limit"], aa[0]["long_retry_limit"])
    base_endpoints = _canonical({k:aa[0]["candidate_knobs"][k] for k in ("ap_state", "cpe_state")})
    for arm in aa:
        af, fq = int(arm["airtime_flags"] == 1), int(arm["fq_limit"] == 2048)
        queue_changed = _canonical({k:arm["candidate_knobs"][k] for k in ("ap_state", "cpe_state")}) != base_endpoints
        retry_changed = (arm["short_retry_limit"], arm["long_retry_limit"]) != base_retry
        nominal.append([1, af, fq, af*fq])
        full.append([1, af, fq, af*fq, int(queue_changed), int(retry_changed)])
    nominal_names = ["intercept", "AF1", "FQ2048", "AF1xFQ2048"]
    x = np.asarray(nominal, dtype=float)
    aliases = {}
    for column, name in ((4,"nonstock_queue_package"), (5,"retry_changed")):
        coef, *_ = np.linalg.lstsq(x, np.asarray(full)[:,column], rcond=None)
        aliases[name] = dict(nominal_basis_coefficients=coef.tolist(), max_residual=float(np.max(np.abs(x@coef-np.asarray(full)[:,column]))))
    missing_cell = (0, 1)
    rows26 = [[1, arm["force_tx_status"], int((arm["short_retry_limit"],arm["long_retry_limit"]) != (7,4))]
              for arm in bb[1:]]
    rows26 = [row + [row[1]*row[2]] for row in rows26]
    present = {(r[1], r[2]) for r in rows26}
    return dict(R24=dict(nominal=_matrix_audit(nominal,nominal_names),
        nuisance_adjusted=_matrix_audit(full,nominal_names+["nonstock_queue_package","retry_changed"]), nuisance_aliases=aliases,
        A_vs_B_declared_changes=package_changes(aa[0],aa[1]), B_vs_C_declared_changes=package_changes(aa[1],aa[2]), C_vs_D_declared_changes=package_changes(aa[2],aa[3]),
        isolated_factor_effects_identified=False,
        interpretation="Nominal2x2 rank is not causal isolation: stockA has different endpoint queue package; D interaction aliases changed retry; all pair contrasts remain package contrasts"),
        R26=dict(hybrid_factor_matrix=_matrix_audit(rows26,["intercept","FTX1","retry_changed","FTX1xretry_changed"]),
            observed_hybrid_cells=[list(v) for v in sorted(present)], missing_FTX0_retry_changed=list(missing_cell),
            interaction_identified=False,
            C_vs_B=dict(declared_changes=package_changes(bb[1],bb[2]),declared_single_FTX_change=set(package_changes(bb[1],bb[2]))=={"force_tx_status"}),
            D_vs_C=dict(declared_changes=package_changes(bb[2],bb[3]),declared_only_retry_pair_change=set(package_changes(bb[2],bb[3]))=={"short_retry_limit","long_retry_limit"}),
            effective_hardware_isolation_verified=False,
            interpretation="Clean declared conditional package comparisons, not effective control readback or fullFTXxretry2x2; stockA cannot supply missing hybrid cell"))


def _window_description(round_id, row):
    blocks = row["repetition_blocks"]
    raw, concat = row["raw_rtts_ms"], [v for b in blocks for v in b["rtts_ms"]]
    if sorted(raw) != sorted(concat):
        raise ValueError("Pooled RTT multiset differs from saved blocks")
    sent, received = sum(b["pings_sent"] for b in blocks), sum(b["pings_rcvd"] for b in blocks)
    if received != len(raw):
        raise ValueError("Received block RTT count mismatch")
    hooks = {}
    for name in HOOKS:
        top, candidate = name in row, name in row["candidate_knobs"]
        if top != candidate or (top and (type(row[name]) is not int
                or type(row["candidate_knobs"][name]) is not int or row[name] != row["candidate_knobs"][name])):
            raise ValueError("Conflicting hook declaration")
        hooks[name] = row[name] if top else None
    means = {key:math.fsum(b[source] for b in blocks)/len(blocks) for key,source in
             (("total_mbps","total_goodput_mbps"),("dl_mbps","dl_goodput_mbps"),("ul_mbps","ul_goodput_mbps"))}
    reported = dict(total_mbps=row["observation"]["goodput_rx_mbps"],dl_mbps=row["dl_goodput_mbps"],ul_mbps=row["ul_goodput_mbps"])
    return dict(round_id=round_id,iteration=row["commit"],supplied_blocks=len(blocks),attempted_pings=sent,received_pings=received,
        reported_window_loss_pct=row["observation"]["packet_loss_pct"],block_loss_pct=100*(sent-received)/sent,
        pooled_RTT_multiset_matches_blocks=True,pooled_order_matches_block_concatenation=raw==concat,
        pooled_RTT_is_sorted=raw==sorted(raw),chronology="Only supplied block arrays preserve their within-block order; pooled order must not be treated as chronological",
        hooks_declared=hooks,effective_hook_readback_verified=False,
        reported_summaries=reported,actual_block_means=means,reported_minus_block_means={k:reported[k]-means[k] for k in reported},
        reported_total_minus_directional_sum=reported["total_mbps"]-reported["dl_mbps"]-reported["ul_mbps"],
        mac_packets_delta=row.get("mac_tx_packets_delta"),interpretable_mac_retry_fraction=(row.get("mac_tx_retries_delta",0)/row["mac_tx_packets_delta"] if row.get("mac_tx_packets_delta",0)>0 else None))


def build_analysis():
    from orchestration.autoresearch.fmx_offline_data import load_all26_block_observations
    dependency_paths = [Path(__file__), ROOT/"orchestration/autoresearch/fmx_offline_data.py",
                        ROOT/"analysis/statistics/fmx_r16_to_r21_real_crossover_audit.py",
                        ROOT/"analysis/statistics/fmx_r15_and_crossover_statistical_audit.py",
                        ROOT/"analysis/statistics/fmx_r10_to_r14_causal_and_power_analysis.py"]
    dependencies = [_binding(p) for p in dependency_paths]
    receipts, sources = frozen_new_receipts()
    normalized = load_all26_block_observations()
    rows = validate_crossed_rows(normalized["crossed"])
    if len(rows) != 188 or len(normalized["sequential"]) != 16:
        raise ValueError("Expected188 crossed and16 sequential rows")
    # Reuse only Q-T normalized measurement output, never original/live old inputs.
    old_path = ROOT/"artifacts/autoresearch/waves_qrst_20261024/normalized_r16_to_r21_block_observations_20261024.json"
    old = json.loads(old_path.read_text(encoding="utf-8"))
    old_rows = [r for r in rows if int(r["round_id"][1:]) < 22]
    if old_rows != old["crossed"]:
        raise ValueError("Previously accepted Q-T block rows changed")
    contrasts, designs = [], []
    for number in CROSSED_ROUNDS:
        group = [r for r in rows if r["round_id"] == f"R{number}"]
        treatment_ids = sorted({r["treatment_id"] for r in group})
        for a,b in combinations(treatment_ids,2):
            contrasts.extend(paired_contrast(group,a,b,m) for m in METRICS)
        diag = multilevel_design_diagnostics(group) | dict(round_id=f"R{number}")
        if number in NEW_ROUNDS:
            receipt = receipts[number]
            mapping = {chr(65+i):r["commit"] for i,r in enumerate(receipt["iterations"])}
            diag["saved_schedule_agreement"] = schedule_agreement(group,receipt["crossover_schedule"],mapping)
            diag["mapping_evidence"] = "Frozen recipe TEXT emits iteration loop A/B/C[/D]; recipe hashes retained"
        designs.append(diag)
    r25 = receipts[25]["iterations"]
    families, focused = assign_families(contrasts,[r["commit"] for r in r25])
    keys = {(r["round_id"],r["block_index"]) for r in rows}
    new_keys = {k for k in keys if int(k[0][1:]) in NEW_ROUNDS}
    descriptions = [_window_description(f"R{number}",row) for number,receipt in sorted(receipts.items()) for row in receipt["iterations"]]
    if [_binding(p) for p in dependency_paths] != dependencies:
        raise ValueError("Dependency bytes changed during computation; preserve failure and rebind")
    return dict(schema_version=1,status="OFFLINE_EXACT_CROSSOVER_AUDIT_PENDING_INDEPENDENT_REVIEW",
        software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        family_plan=_binding(BASE/"wave_v_families_precomputation.json"),sources=sources,numerical_dependencies=dependencies,
        old_block_output=_binding(old_path),U_source_refs=normalized["source_refs"],
        crossed_rows=len(rows),matched_round_block_units=len(keys),new_crossed_rows=len(rows)-len(old_rows),new_matched_units=len(new_keys),R17_sequential_rows=16,
        contrasts=contrasts,families=families,R25_unanimity_checks=unanimity_checks(focused),new_window_descriptions=descriptions,
        full_design_diagnostics=designs,factorial_boundaries=factorial_boundaries(receipts[24],receipts[26]),
        quality=_quality(rows),automatic_execution_allowed=False,causal_or_physical_acceptance=False,
        limits=["All families retrospective and frozen before new outcome inspection, not experiment preregistration",
                "Independent symmetric block differences required for signed-rank location interpretation; sign test has its own nonzero-sign null",
                "52round-scoped matched blocks are not52 independent sectors; all observed on one bench link; period balance/rank not washout proof",
                "12block sign permutations are4096, not120ping trials; missing/lossful outcomes retained and received-tail censoring remains",
                "Marginal/focused significance must be shown beside broad162/324, not substituted for global claims",
                "All declared hooks/packages are source context, not proof of effective hardware state or safe RAM range",
                "StockA versus hybrid changes whole queue package; no causal AFxFQ or FTXxretry interaction accepted",
                "No rawAssembly/target execution/live sources/R27/network access; no controller enrollment or actuation"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=BASE/"wave_v_r22_to_r26_crossover_analysis.json")
    path = parser.parse_args().output.resolve()
    if path.parent != BASE.resolve() or not path.name.startswith("wave_v_") or path.suffix != ".json":
        raise ValueError("Only new owned Wave V JSON output allowed")
    result = build_analysis()
    with path.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(result,f,indent=2,allow_nan=False);f.write("\n")
    print(json.dumps({"status":result["status"],"contrasts":len(result["contrasts"]),"families":{k:v["tests"] for k,v in result["families"].items()}}))


if __name__ == "__main__":
    main()
