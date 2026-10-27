"""Frozen R16-R21 statistical audit, wholly offline and non-actuating.

Primary family: all27 within-round treatment pairs in the five identified
crossover rounds times3 block outcomes =81 exact signed-rank tests, Holm81.
Secondary family per outcome:27. Conditional ping family:33within-round MWUs.
These are retrospective analysis choices, not physical preregistration.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy

from analysis.statistics.fmx_r15_and_crossover_statistical_audit import (
    audit_blocked_crossover, exact_signed_rank,
)
from analysis.statistics.fmx_r10_to_r14_causal_and_power_analysis import (
    conditional_tail_bootstrap, holm_adjust, mwu_contrast, probability, sample,
)

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/"artifacts/autoresearch/waves_qrst_20261024"
CROSSED_ROUNDS = (16,18,19,20,21)
METRICS = ("goodput_rx_mbps","p95_rtt_ms","p99_rtt_ms")


def _merge_atoms(atoms):
    result = []
    for atom in atoms:
        if result:
            previous = result[-1]
            touching = previous["upper"] == atom["lower"]
            if touching and (previous["upper_closed"] or atom["lower_closed"]):
                previous.update(upper=atom["upper"],upper_closed=atom["upper_closed"])
                continue
        result.append(dict(atom))
    return result


def exact_walsh_confidence_set(differences, alpha=.05):
    """Exact acceptance union, retaining rejected singleton holes/open endpoints.

    Invert the accepted M-P exact tie/zero-aware signed-rank test. Unlike its
    conservative hull, this representation exposes all accepted components.
    None lower/upper is -/+infinity. Discrete-test inversion assumes independent
    symmetric location-shift block differences, never independent Walsh terms.
    """
    alpha = probability(alpha)
    data = sample(differences, minimum=1)
    if len(data)>60:
        raise ValueError("Exact CI bounded to60 independent blocks")
    if 2**(1-len(data)) > alpha:
        return dict(components=[dict(lower=None,upper=None,lower_closed=False,upper_closed=False)],
                    confidence=1-alpha,whole_real_line=True,
                    reason="SMALL_N_EXACT_P_FLOOR_EXCEEDS_ALPHA",independent_blocks=len(data))
    walsh = sorted(set(float(a/2+b/2) for i,a in enumerate(data) for b in data[i:]))
    if not all(math.isfinite(v) for v in walsh):
        raise ValueError("Nonfinite Walsh arithmetic")
    atoms = []
    for i,point in enumerate(walsh):
        delta = data-point
        if not np.isfinite(delta).all():raise ValueError("Nonfinite shifted differences")
        if exact_signed_rank(delta)["p_value"] > alpha:
            atoms.append(dict(lower=point,upper=point,lower_closed=True,upper_closed=True))
        if i+1<len(walsh):
            right = walsh[i+1]
            midpoint = point/2+right/2
            if exact_signed_rank(data-midpoint)["p_value"] > alpha:
                atoms.append(dict(lower=point,upper=right,lower_closed=False,upper_closed=False))
    return dict(components=_merge_atoms(atoms),confidence=1-alpha,whole_real_line=False,
                reason="EXACT_SIGNED_RANK_ACCEPTANCE_SET_NOT_HULL",independent_blocks=len(data),
                tested_breakpoints=len(walsh),endpoint_convention="None=-/+infinity; emptycomponents=emptyset")


def _rows(rows, round_number):
    if round_number not in CROSSED_ROUNDS:
        raise ValueError("R17/sequential rows are not identified crossovers")
    if not isinstance(rows,list) or not rows:raise ValueError("Explicit identified rows required")
    seen = set()
    for row in rows:
        if not isinstance(row,dict):raise ValueError("Block row object required")
        for name in ("block_index","crossover_step"):
            if type(row.get(name)) is not int or row[name]<0:raise ValueError("Genuine nonnegative integer IDs required")
        identity = (row["block_index"],row["crossover_step"])
        if identity in seen:raise ValueError("Duplicate block/step")
        seen.add(identity)
        if not isinstance(row.get("treatment_id"),str) or not row["treatment_id"]:raise ValueError("Treatment identity required")
        if not isinstance(row.get("observation"),dict):raise ValueError("Observation required")
    return sorted(rows,key=lambda r:(r["block_index"],r["crossover_step"]))


def multilevel_design_diagnostics(rows):
    """Keep all3/4arms in period/sequence/lag diagnostics, not C/D=>A."""
    by_block = defaultdict(list)
    for row in rows:by_block[row["block_index"]].append(row)
    treatments = sorted({r["treatment_id"] for r in rows})
    blocks = sorted(by_block)
    periods = sorted({r["crossover_step"] for r in rows})
    sequence_counts, period_counts, transitions = Counter(), Counter(), Counter()
    sequences, design_rows, gaps = [], [], []
    for block,group in sorted(by_block.items()):
        ordered = sorted(group,key=lambda r:r["crossover_step"])
        sequence = tuple(r["treatment_id"] for r in ordered)
        sequence_counts[sequence] += 1
        sequences.append(dict(block_index=block,treatments=list(sequence),steps=[r["crossover_step"] for r in ordered]))
        previous = None
        for row in ordered:
            period_counts[(row["crossover_step"],row["treatment_id"])] += 1
            contiguous = previous is not None and row["crossover_step"]==previous["crossover_step"]+1
            lag = previous["treatment_id"] if contiguous else None
            if contiguous:transitions[(lag,row["treatment_id"])] += 1
            elif previous is not None:
                gaps.append(dict(block_index=block,previous_step=previous["crossover_step"],current_step=row["crossover_step"]))
            design_rows.append([1]+[int(block==b) for b in blocks[1:]]+
                               [int(row["crossover_step"]==p) for p in periods[1:]]+
                               [int(row["treatment_id"]==t) for t in treatments[1:]]+
                               [int(lag==t) for t in treatments[1:]])
            previous = row
    names = (["intercept"]+[f"block:{b}" for b in blocks[1:]]+[f"period:{p}" for p in periods[1:]]+
             [f"current:{t}" for t in treatments[1:]]+[f"lag:{t}" for t in treatments[1:]])
    matrix = np.asarray(design_rows,dtype=float)
    rank = int(np.linalg.matrix_rank(matrix))
    current_lag_start = 1+len(blocks)-1+len(periods)-1
    estimability = {names[i]:bool(rank>np.linalg.matrix_rank(np.delete(matrix,i,axis=1))) for i in range(current_lag_start,len(names))}
    return dict(blocks=len(blocks),treatment_by_block_rows=len(rows),treatment_ids=treatments,
                sequences=sequences,sequence_counts=[dict(treatments=list(k),blocks=v) for k,v in sequence_counts.items()],
                period_counts=[dict(crossover_step=p,treatment_id=t,rows=period_counts[(p,t)]) for p in periods for t in treatments],
                period_balance=dict(equal_treatment_counts_within_every_period=all(
                    len({period_counts[(p,t)] for t in treatments})==1 for p in periods),
                    interpretation="Count balance only, not randomized allocation or causal balance"),
                directed_transition_counts=[dict(previous=a,current=b,rows=transitions[(a,b)]) for a in treatments for b in treatments],
                transition_balance=dict(contiguous_transitions=sum(transitions.values()),
                    all_distinct_ordered_pairs_equal=len({transitions[(a,b)] for a in treatments for b in treatments if a!=b})<=1,
                    every_pair_forward_reverse_equal=all(transitions[(a,b)]==transitions[(b,a)] for a,b in combinations(treatments,2)),
                    interpretation="Within-block contiguous first-order counts only; equality does not prove absent carryover"),
                step_gaps=gaps,
                period_outcome_means=[dict(crossover_step=p,metric=m,rows=len(v),mean=math.fsum(v)/len(v))
                    for p in periods for m in METRICS
                    if (v:=[r["observation"][m] for r in rows if r["crossover_step"]==p and r["observation"].get(m) is not None])],
                design=dict(rows=len(matrix),columns=names,rank=rank,full_column_rank=rank==len(names),conditional_column_estimability=estimability),
                randomization="UNKNOWN_NOT_ESTABLISHED_BY_IDS_OR_WILLIAMS_LABEL",
                carryover="UNKNOWN: categorical lag/period rank is diagnostic, not a washout or causal test; first/gap lag reference is not proven no-carryover")


def schedule_agreement(rows, schedule, label_to_treatment):
    """Compare explicit saved positions; labels must have a supplied provenance."""
    if not isinstance(schedule,list) or not schedule or not isinstance(label_to_treatment,dict):
        raise ValueError("Explicit schedule and label mapping required")
    if len(set(label_to_treatment.values()))!=len(label_to_treatment):
        raise ValueError("Schedule labels must map one-to-one")
    expected={}
    for block,sequence in enumerate(schedule):
        if not isinstance(sequence,list) or not sequence:raise ValueError("Nonempty scheduled sequence required")
        for step,label in enumerate(sequence):
            if not isinstance(label,str) or label not in label_to_treatment:raise ValueError("Unknown schedule label")
            expected[(block,step)]=label_to_treatment[label]
    actual={}
    for row in rows:
        key=(row["block_index"],row["crossover_step"])
        if any(type(v) is not int or v<0 for v in key) or key in actual:raise ValueError("Invalid/duplicate actual schedule position")
        actual[key]=row["treatment_id"]
    mismatches=[dict(block_index=b,crossover_step=s,planned=expected.get((b,s)),actual=actual.get((b,s)))
                for b,s in sorted(set(expected)|set(actual)) if expected.get((b,s))!=actual.get((b,s))]
    return dict(matches=not mismatches,planned_positions=len(expected),actual_positions=len(actual),
                label_to_treatment=dict(label_to_treatment),mismatches=mismatches,
                interpretation="Schedule conformity only; neither randomization nor washout proof")


def analyze_identified_round(rows, round_number):
    rows = _rows(rows,round_number)
    treatments = sorted({r["treatment_id"] for r in rows})
    results = []
    for control,treatment in combinations(treatments,2):
        subset = [r for r in rows if r["treatment_id"] in (control,treatment)]
        for metric in METRICS:
            audit = audit_blocked_crossover(subset,control,treatment,metric=metric,evidence_kind=f"FROZEN_R{round_number}_GENUINE_PROVIDED_BLOCK_IDS")
            if not audit["pairs"]:raise ValueError("No complete blocks for planned paired contrast")
            differences = [r["difference"] for r in audit["pairs"]]
            n = len(differences)
            results.append(dict(round_id=f"R{round_number}",control=control,treatment=treatment,metric=metric,
                                complete_blocks=n,excluded_blocks=audit["excluded_blocks"],pairs=audit["pairs"],
                                quality_observations=audit["quality_observations"],
                                pair_sequence_differences=audit["sequence_differences"],
                                wilcoxon=audit["paired_results"]["wilcoxon"],sign_test=audit["paired_results"]["sign_test"],
                                paired_HL=audit["paired_results"]["hl"],
                                exact_marginal_confidence_set=exact_walsh_confidence_set(differences),
                                exact_Bonferroni81_confidence_set=exact_walsh_confidence_set(differences,.05/81),
                                p_floor_if_nozeros=2**(1-n),causal_acceptance=False))
    return dict(round_id=f"R{round_number}",diagnostics=multilevel_design_diagnostics(rows),contrasts=results)


def frozen_receipts():
    manifest = json.loads((BASE/"inputs_manifest.json").read_text(encoding="utf-8"))
    receipts,sources = {},[]
    if len(manifest)!=18:raise ValueError("Require18frozen Q-R-S-Tinputs")
    for ref in manifest:
        path = (ROOT/ref["path"]).resolve()
        if not path.is_relative_to((BASE/"inputs").resolve()):raise ValueError("Input escape")
        if ref["round"] not in range(16,22):raise ValueError("Outside authorized frozen rounds")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=ref["sha256"] or len(raw)!=ref["bytes"]:raise ValueError("Frozen input mismatch")
        sources.append(dict(path=ref["path"],sha256=ref["sha256"],bytes=len(raw),round=ref["round"]))
        if path.suffix==".json":receipts[ref["round"]]=json.loads(raw)
        else:raw.decode("utf-8") # TSV/recipe TEXTonly; never import/execute.
    if set(receipts)!=set(range(16,22)):raise ValueError("Missing current frozen round")
    return receipts,sources


def _summary_consistency(row):
    blocks = row["repetition_blocks"]
    reported = dict(total_mbps=row["observation"]["goodput_rx_mbps"],dl_mbps=row["dl_goodput_mbps"],ul_mbps=row["ul_goodput_mbps"])
    means = {name:math.fsum(b[key] for b in blocks)/len(blocks) for name,key in [("total_mbps","total_goodput_mbps"),("dl_mbps","dl_goodput_mbps"),("ul_mbps","ul_goodput_mbps")]}
    return dict(reported=reported,block_means=means,reported_minus_block_mean={k:reported[k]-means[k] for k in reported},
                reported_total_minus_reported_dl_plus_ul=reported["total_mbps"]-reported["dl_mbps"]-reported["ul_mbps"],
                interpretation="Retain all saved values, no overwrite/forced reconciliation; paired outcome uses genuine blocks")


def sequential_CPU_description(receipt):
    output=[]
    for row in receipt["iterations"]:
        blocks=row["repetition_blocks"]
        if any("crossover_step" in b for b in blocks):raise ValueError("R17 unexpectedly contains crossover step")
        item=dict(iteration=row["commit"],cipher_declared=row["encryption_mode"],sequential_rows=len(blocks),
                  reported_cpu_busy_median=row["ap_cpu_busy_pct_median"],reported_cpu_softirq_median=row["ap_cpu_softirq_pct_median"],
                  block_cpu_busy=[b["ap_cpu_busy_pct"] for b in blocks],block_cpu_softirq=[b["ap_cpu_softirq_pct"] for b in blocks],
                  block_total_goodput=[b["total_goodput_mbps"] for b in blocks])
        item.update(block_cpu_busy_median=float(np.median(item["block_cpu_busy"])),block_cpu_softirq_median=float(np.median(item["block_cpu_softirq"])))
        output.append(item)
    secure,opened=output[1],output[3]
    return dict(status="SEQUENTIAL_DESCRIPTIVE_NOT_CROSSOVER",rows=output,
                same_symmetric_package_secure_vs_open=dict(control=secure["iteration"],treatment=opened["iteration"],
                    busy_median_delta=opened["block_cpu_busy_median"]-secure["block_cpu_busy_median"],
                    softirq_median_delta=opened["block_cpu_softirq_median"]-secure["block_cpu_softirq_median"],paired_p_value=None),
                limits="16sequential rows with no stepIDs; block_index0..3 reuse is not pairing. CPUbusy/softirq are observed load fractions, not isolated cipher cycles/offload; time/load/adaptation remain confounders.")


def build_analysis(*,resamples=1999):
    from orchestration.autoresearch.fmx_offline_data import load_all21_block_observations
    receipts,sources=frozen_receipts()
    normalized=load_all21_block_observations()
    crossed=normalized["crossed"]
    paired=[];diagnostics=[];block_keys=set()
    for number in CROSSED_ROUNDS:
        rows=[r for r in crossed if r["round_id"]==f"R{number}"]
        result=analyze_identified_round(rows,number);paired.extend(result["contrasts"]);diagnostics.append(result["diagnostics"]|dict(round_id=f"R{number}"))
        # Frozen recipe text emits detailed_runs in explicit A/B/C[/D] order.
        # Verified at R16:383,R18:271,R19:280,R20:302,R21:240; never executed.
        mapping={chr(65+i):r["commit"] for i,r in enumerate(receipts[number]["iterations"])}
        diagnostics[-1]["saved_schedule_agreement"]=schedule_agreement(rows,receipts[number]["crossover_schedule"],mapping)
        diagnostics[-1]["schedule_label_mapping_evidence"]="Frozen recipe TEXT explicit iteration loop A,B,C[/D], aligned with saved iterations; recipe hashes in sources"
        block_keys.update((f"R{number}",r["block_index"]) for r in rows)
    if len(paired)!=81:raise ValueError("Planned81pairedtests incomplete")
    for row,p in zip(paired,holm_adjust([r["wilcoxon"]["p_value"] for r in paired])):row["Holm81_p_value"]=p
    for metric in METRICS:
        members=[r for r in paired if r["metric"]==metric]
        for row,p in zip(members,holm_adjust([r["wilcoxon"]["p_value"] for r in members])):row["secondary_outcome_Holm27_p_value"]=p
    descriptions=[];ping=[]
    for number,receipt in sorted(receipts.items()):
        for row in receipt["iterations"]:
            raw=row["raw_rtts_ms"];concat=[v for b in row["repetition_blocks"] for v in b["rtts_ms"]]
            if raw!=concat:raise ValueError("Raw RTT differs from retained block concatenation")
            descriptions.append(dict(round_id=f"R{number}",iteration=row["commit"],raw_received_RTT=len(raw),reported_received_RTT=row["rtt_sample_count"],
                                     block_attempted_pings=sum(b["pings_sent"] for b in row["repetition_blocks"]),
                                     block_received_pings=sum(b["pings_rcvd"] for b in row["repetition_blocks"]),
                                     reported_loss_pct=row["observation"]["packet_loss_pct"],summary_consistency=_summary_consistency(row),
                                     reported_mac_retry_rate=row.get("mac_retry_rate"),mac_tx_packet_delta=row.get("mac_tx_packets_delta"),
                                     interpretable_mac_retry_rate=(row.get("mac_tx_retries_delta",0)/row["mac_tx_packets_delta"] if row.get("mac_tx_packets_delta",0)>0 else None),
                                     tail_intervals=[conditional_tail_bootstrap(raw,quantile=q,resamples=resamples) for q in (.95,.99)],
                                     received_ping_scope="Conditional IID resampling; not independent block/physical-trial tail interval"))
        for a,b in combinations(receipt["iterations"],2):
            ping.append(dict(round_id=f"R{number}",control=a["commit"],treatment=b["commit"],**mwu_contrast(a["raw_rtts_ms"],b["raw_rtts_ms"])))
    if len(descriptions)!=23 or len(ping)!=33:raise ValueError("Planned23windows/33pingcontrasts incomplete")
    for row,p in zip(ping,holm_adjust([r["p_value"] for r in ping])):row["Holm33_p_value"]=p
    r18=receipts[18]["iterations"];a,b=r18[1:3];changes={}
    for endpoint in ("ap_state","cpe_state"):
        x,y=a["candidate_knobs"][endpoint],b["candidate_knobs"][endpoint]
        for k in sorted(set(x)|set(y)):
            if k not in {"name","description","complexity_cost"} and x.get(k)!=y.get(k):changes[endpoint+"."+k]=[x.get(k),y.get(k)]
    return dict(schema_version=1,status="OFFLINE_REAL_IDENTIFIED_BLOCK_CONDITIONAL_AUDIT",sources=sources,
                software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
                treatment_by_block_rows=len(crossed),matched_round_block_units=len(block_keys),matched_keys=[dict(round_id=r,block_index=b) for r,b in sorted(block_keys)],
                R17_sequential_rows=len(normalized["sequential"]),window_count=len(descriptions),descriptions=descriptions,
                paired_contrasts=paired,full_multilevel_design_diagnostics=diagnostics,ping_contrasts=ping,
                families=dict(primary="81exact block signedrank tests=27pairs x3outcomes, Holm81",secondary="27tests peroutcome, named exploratory secondary",conditional_ping="33withinround MWUs,Holm33",CI="Marginal95% exactsets and conservative simultaneous Bonferroni81sets; sign-test sensitivity only",retrospective_not_physical_preregistered=True),
                exact_detectability=dict(n4_minimum_two_sided_p=.125,n8_minimum_two_sided_p=.0078125,
                    smallest_n_for_marginal_05=6,smallest_n_for_first_Holm81_05=12,
                    interpretation="Attainability bounds without zeros, not observed power or adequate sample-size assurance; ties/zeros can reduce information"),
                R18_fixed_threshold_comparison=dict(control=a["commit"],treatment=b["commit"],declared_distance_m=[a["distance_meters"],b["distance_meters"]],
                    AP_threshold_us=[a["candidate_knobs"]["ap_state"]["aql_threshold_us"],b["candidate_knobs"]["ap_state"]["aql_threshold_us"]],
                    CPE_threshold_us=[a["candidate_knobs"]["cpe_state"]["aql_threshold_us"],b["candidate_knobs"]["cpe_state"]["aql_threshold_us"]],changed_endpoint_fields=changes,
                    inference="Genuine n4blockcontrast includedall3outcomes; programmed3000m is not physical3km; no independent threshold change"),
                R17_CPU=sequential_CPU_description(receipts[17]),automatic_execution_allowed=False,causal_or_physical_acceptance=False,
                numerical_reuse=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [ROOT/"analysis/statistics/fmx_r15_and_crossover_statistical_audit.py",ROOT/"analysis/statistics/fmx_r10_to_r14_causal_and_power_analysis.py",ROOT/"orchestration/autoresearch/fmx_offline_data.py"]],
                limits=["88treatment-by-block rows are24round-scoped blockIDs, not88independent paired units; R17sequential16rows neverpaired",
                        "n8minimum exact two-sidedp=.0078125,n4=.125 beforezero removal; Holm81cannotcertify.05at thosefloors",
                        "IDs/counterbalancing do not establish randomization, inter-block independence, washout, symmetry or no carryover",
                        "All lossful blocks retained; received-ping tails exclude lost packets and do not substitute physical replication",
                        "Summary means contradict retained blockmeans in places; both preserved, paired outcomes useblock values only",
                        "Frozen18files only; recipes readtextnotexecuted; no original receipts, future rounds or network/device access"])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",type=Path,default=BASE/"wave_r_real_crossover_analysis.json");args=parser.parse_args()
    path=args.output.resolve()
    if path.parent!=BASE.resolve() or not path.name.startswith("wave_r_") or path.suffix!=".json":raise ValueError("Only new ownedWaveRoutputs")
    result=build_analysis()
    with path.open("x",encoding="utf-8",newline="\n") as f:json.dump(result,f,indent=2,allow_nan=False);f.write("\n")
    print(json.dumps(dict(status=result["status"],windows=result["window_count"],blocks=result["matched_round_block_units"])))


if __name__=="__main__":main()
