"""Frozen offline WDS crossover audit; certification labels are not acceptance.

Exact rank probabilities use integer rank-sum dynamic programming, not2**46
enumeration. Families and requested targets were fixed before new outcomes.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy

from analysis.statistics.fmx_r10_to_r14_causal_and_power_analysis import holm_adjust, sample
from analysis.statistics.fmx_r15_and_crossover_statistical_audit import exact_signed_rank, exact_sign_test
from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import (
    exact_walsh_confidence_set, multilevel_design_diagnostics, schedule_agreement,
)
from analysis.statistics.fmx_r22_to_r26_crossover_audit import METRICS, _metric, _quality

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "artifacts/autoresearch/waves_yzab_20261024"
ROUNDS = tuple(range(27,33))
FOCUSED = METRICS[1:]
TARGETS = {27:(2,),28:(1,2),29:(1,),30:(2,),31:(1,),32:(1,)}
POOL = {27:2,28:1,29:1,32:1}


def binding(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def frozen_inputs():
    manifest = json.loads((BASE/"inputs_manifest.json").read_text(encoding="utf-8"))
    if len(manifest)!=18:raise ValueError("Require18 frozen data/recipe/TSV files")
    receipts,literal,refs = {},{},[]
    for ref in manifest:
        path = (ROOT/ref["path"]).resolve()
        if not path.is_relative_to((BASE/"inputs").resolve()) or ref["round"] not in ROUNDS:
            raise ValueError("Only frozen new inputs, no original/live paths")
        actual = binding(path)
        if actual["sha256"]!=ref["sha256"] or actual["bytes"]!=ref["bytes"]:
            raise ValueError("Frozen input changed")
        refs.append(actual|dict(round=ref["round"]))
        text = path.read_text(encoding="utf-8")
        if path.suffix==".json":
            if ref["round"] in receipts:raise ValueError("Duplicate round")
            receipts[ref["round"]] = json.loads(text)
            literal[ref["round"]] = json.loads(text,parse_float=Decimal)
    if set(receipts)!=set(ROUNDS):raise ValueError("Missing current frozen round")
    return receipts,literal,refs


def exact_effect(differences):
    values = sample(differences,minimum=1)
    if len(values)>60:raise ValueError("At most60 supplied blocks")
    walsh = sorted(float(a/2+b/2) for i,a in enumerate(values) for b in values[i:])
    estimate = walsh[(len(walsh)-1)//2]/2+walsh[len(walsh)//2]/2
    if not math.isfinite(estimate):raise ValueError("Nonfinite Walsh location")
    return dict(exact_rank=exact_signed_rank(values),exact_sign=exact_sign_test(values),
        HL_estimate=estimate,derived_Walsh_terms=len(walsh),independent_units_assumed=len(values),
        confidence_sets={"95":exact_walsh_confidence_set(values,.05),
                         "99.9":exact_walsh_confidence_set(values,.001)},
        method="EXACT_CONDITIONAL_TIED_RANK_SUBSET_SUM_DP_AND_TEST_INVERSION",
        assumptions="Independent sign-exchangeable symmetric block differences; common-shift interpretation also needs invariant location model. IDs do not prove these.")


def validate_rows(rows):
    if not isinstance(rows,list) or not rows:raise ValueError("Explicit crossed rows required")
    seen = set()
    for r in rows:
        if r.get("round_id") not in {f"R{n}" for n in ROUNDS}:raise ValueError("New frozen round required")
        for key in ("block_index","crossover_step"):
            if type(r.get(key)) is not int or r[key]<0:raise ValueError("Genuine block/step required")
        key = (r["round_id"],r["block_index"],r["crossover_step"])
        if key in seen:raise ValueError("Duplicate supplied unit")
        seen.add(key)
        if not isinstance(r.get("observation"),dict) or not isinstance(r.get("treatment_id"),str):
            raise ValueError("Explicit treatment and observation required")
    return rows


def audit_pair(rows,control,treatment,metric,*,role_field="treatment_id",scope=None):
    """Preserve original round/block keys even in the derived pooled diagnostic."""
    validate_rows(rows)
    if scope is None and len({r["round_id"] for r in rows}) != 1:
        raise ValueError("Explicit scope required for cross-round pooling")
    groups = defaultdict(list)
    for r in rows:groups[(r["round_id"],r["block_index"])]
    subset = [r for r in rows if r.get(role_field) in (control,treatment)]
    for r in subset:groups[(r["round_id"],r["block_index"])].append(r)
    pairs,excluded = [],[]
    for (rid,block),group in sorted(groups.items()):
        a = [r for r in group if r[role_field]==control]
        b = [r for r in group if r[role_field]==treatment]
        va,vb = [_metric(r,metric) for r in a],[_metric(r,metric) for r in b]
        reason = ("MISSING_ARM" if not a or not b else "UNBALANCED_ARM_REPEATS" if len(a)!=len(b)
                  else "MISSING_OUTCOME" if None in va+vb else None)
        if reason:
            excluded.append(dict(round_id=rid,block_index=block,reason=reason));continue
        ma,mb = math.fsum(va)/len(va),math.fsum(vb)/len(vb)
        pairs.append(dict(round_id=rid,block_index=block,control_mean=ma,treatment_mean=mb,difference=mb-ma,
            source_control_ids=sorted({r["treatment_id"] for r in a}),source_target_ids=sorted({r["treatment_id"] for r in b})))
    if not pairs:raise ValueError("No complete identified pair")
    d = [r["difference"] for r in pairs]
    rid = scope or next(iter({r["round_id"] for r in rows}))
    return dict(source_hypothesis_id=json.dumps([rid,control,treatment,metric],separators=(",",":")),
        scope=rid,control=control,target=treatment,metric=metric,
        direction="lower" if metric in ("p50_rtt_ms","p95_rtt_ms","p99_rtt_ms") else "higher",
        paired_unit_ids=[dict(round_id=r["round_id"],block_index=r["block_index"]) for r in pairs],
        pairs=pairs,excluded_blocks=excluded,quality=_quality(subset),
        favorable_blocks=sum(x<0 if metric in ("p50_rtt_ms","p95_rtt_ms","p99_rtt_ms") else x>0 for x in d),
        equal_blocks=sum(x==0 for x in d),**exact_effect(d),physical_or_causal_acceptance=False)


def padded_family(members,declared_size,key):
    """Actual Holm on a stated p=1 completion; never an invented full catalog."""
    if type(declared_size) is not int or declared_size<len(members) or not members:
        raise ValueError("Declared bound cannot be smaller than known scope")
    ids = [r["source_hypothesis_id"] for r in members]
    if len(set(ids))!=len(ids):raise ValueError("Duplicate hypothesis")
    values = [r["exact_rank"]["p_value"] for r in members]
    for p in values:
        if type(p) not in (int,float) or not math.isfinite(p) or not 0<=p<=1:raise ValueError("Invalid exact p")
    padding = declared_size-len(values)
    adjusted = holm_adjust(values+[1.0]*padding)[:len(values)]
    return dict(key=key,declared_size=declared_size,known_count=len(values),unknown_padding_count=padding,
        unknown_padding_p_value=1.0,known_hypotheses={i:p for i,p in zip(ids,values)},
        adjusted_p={i:p for i,p in zip(ids,adjusted)},
        Bonferroni_upper_bound={i:min(1.,declared_size*p) for i,p in zip(ids,values)},
        rejections_05=sum(p<.05 for p in adjusted),
        interpretation="Exact Holm for specified known hypotheses plus constant1 never-tested placeholders. Valid conservative procedure, not measured unknown p-values or a complete project catalog. BonferroniMp separately shown.")


def literal_mean_audit(row):
    """Rational arithmetic on canonical literal decimals, no tolerance repair."""
    refs = (("goodput_mbps",row["observation"]["goodput_rx_mbps"],"total_goodput_mbps"),
            ("dl_mbps",row["dl_goodput_mbps"],"dl_goodput_mbps"),
            ("ul_mbps",row["ul_goodput_mbps"],"ul_goodput_mbps"),
            ("jain_index",row["bidir_jain_fairness"],"bidir_jain_fairness"))
    def canonical_fraction(value):
        return Fraction(str(value)) if type(value) is float else Fraction(value)
    fields = {}
    for name,reported,source in refs:
        mean = sum(canonical_fraction(b[source]) for b in row["repetition_blocks"])/len(row["repetition_blocks"])
        delta = canonical_fraction(reported)-mean
        fields[name] = dict(exact=delta==0,reported_canonical=str(reported),block_mean_numerator=str(mean.numerator),
                            block_mean_denominator=str(mean.denominator),reported_minus_mean=float(delta))
    return dict(all_literal_equal=all(x["exact"] for x in fields.values()),fields=fields,
                no_tolerance_widening=True,binary_float_noise_excluded_by_exact_rational_source_decimals=True)


def pool_comparability(selected):
    """All observed endpoint fields and recorded contexts, not just recipe names."""
    contexts = ("workload_regime","active_flow_count","bidirectional","encryption_mode","distance_meters","associated_cpes")
    data = []
    for number,control,target in selected:
        def context(row):
            return {k:list(getattr(row,k)) if isinstance(getattr(row,k,None),tuple) else getattr(row,k,None) for k in contexts}
        data.append(dict(round_id=f"R{number}",control_policy_id=control.policy_key,target_policy_id=target.policy_key,
                         control_context=context(control),target_context=context(target)))
    baseline = data[0]
    differences = [dict(round_id=r["round_id"],field=k) for r in data[1:]
                   for k in ("control_policy_id","target_policy_id","control_context","target_context") if r[k]!=baseline[k]]
    known_context_matches = all(r["target_context"]==r["control_context"] for r in data)
    match = not differences and known_context_matches
    return dict(recorded_packages_and_contexts_match=match,strata=data,differences=differences,
        status="MATCHED_RECORDED_PACKAGE_CONTEXT_LATENT_STATE_UNVERIFIED" if match else "MIXTURE_ONLY_EXPLICIT_DECLARED_DIFFERENCES",
        unknown_context_fields=[k for k,v in baseline["control_context"].items() if v is None],
        homogeneous_causal_effect_accepted=False,
        limits="Recorded equality does not establish effective radio/cipher state, block independence, round invariance or washout. Pooled result is conditional, with separate round effects retained.")


def requested_claims(contrasts):
    claims = []
    for r in contrasts:
        if r["scope"] not in ("R28","R29","R32") or r["metric"] not in FOCUSED or "iter0_" not in r["control"]:
            continue
        number = int(r["scope"][1:])
        if number==28 and not any(r["target"].startswith(f"r28_iter{i}_") for i in (1,2)):continue
        n = {28:12,29:14,32:16}[number]
        expected = n - int((number==29 and r["metric"]=="p99_rtt_ms") or
                           (number==32 and r["metric"] in ("p95_rtt_ms","p99_rtt_ms")))
        claims.append(dict(source_hypothesis_id=r["source_hypothesis_id"],round_id=r["scope"],target=r["target"],metric=r["metric"],
            claimed_favorable_blocks=expected,observed_favorable_blocks=r["favorable_blocks"],observed_equal_blocks=r["equal_blocks"],
            favorable_count_claim_matches=r["favorable_blocks"]==expected,independent_blocks_assumed=len(r["pairs"]),
            exact_rank_p=r["exact_rank"]["p_value"],exact_sign_p=r["exact_sign"]["p_value"],
            rank_sign_assignments=r["exact_rank"]["sign_assignments"],p_floor_if_no_zeros=2**(1-n)))
    return claims


def build_analysis():
    from orchestration.autoresearch.fmx_offline_data import load_all32_measurements,load_all32_block_observations
    dependencies = [Path(__file__),ROOT/"orchestration/autoresearch/fmx_offline_data.py",
        ROOT/"analysis/statistics/fmx_r22_to_r26_crossover_audit.py",ROOT/"analysis/statistics/fmx_r16_to_r21_real_crossover_audit.py",
        ROOT/"analysis/statistics/fmx_r15_and_crossover_statistical_audit.py",ROOT/"analysis/statistics/fmx_r10_to_r14_causal_and_power_analysis.py"]
    dep_refs = [binding(p) for p in dependencies]
    receipts,literal,sources = frozen_inputs()
    records,_ = load_all32_measurements();blocks = load_all32_block_observations()
    rows = [r for r in blocks["crossed"] if int(r["round_id"][1:]) in ROUNDS]
    validate_rows(rows)
    record_by_id = {(r.round_id,r.iteration):r for r in records}
    if (len(records),len(blocks["crossed"]),len(rows),len({(r["round_id"],r["block_index"]) for r in rows}))!=(150,332,144,54):
        raise ValueError("Actual frozen count differs from150/332/144/54")
    results,local,designs,descriptions,selected = [],{},[],[],[]
    for number in ROUNDS:
        receipt = receipts[number];arms = receipt["iterations"];group = [r for r in rows if r["round_id"]==f"R{number}"]
        for a,b in combinations(arms,2):
            for metric in METRICS:
                result = audit_pair(group,a["commit"],b["commit"],metric)
                result.update(control_policy_id=record_by_id[(f"R{number}",a["commit"])].policy_key,
                    target_policy_id=record_by_id[(f"R{number}",b["commit"])].policy_key,
                    regime=record_by_id[(f"R{number}",b["commit"])].workload_regime)
                results.append(result)
        targets = {arms[i]["commit"] for i in TARGETS[number]}
        local[f"R{number}"] = [r for r in results if r["scope"]==f"R{number}" and r["control"]==arms[0]["commit"] and r["target"] in targets and r["metric"] in FOCUSED]
        diag = multilevel_design_diagnostics(group)|dict(round_id=f"R{number}")
        diag["schedule_agreement"] = schedule_agreement(group,receipt["crossover_schedule"],{chr(65+i):r["commit"] for i,r in enumerate(arms)})
        designs.append(diag)
        for i,arm in enumerate(arms):
            saved = record_by_id[(f"R{number}",arm["commit"])];bs = arm["repetition_blocks"]
            descriptions.append(dict(round_id=f"R{number}",iteration=arm["commit"],policy_id=saved.policy_key,
                literal_mean_audit=literal_mean_audit(literal[number]["iterations"][i]),
                Y_literal_consistency=getattr(saved,"block_mean_consistent",None),
                chronological_RTT_claim=arm["raw_rtts_ms"]==[v for b in bs for v in b["rtts_ms"]],
                attempted_pings=sum(b["pings_sent"] for b in bs),received_pings=sum(b["pings_rcvd"] for b in bs),
                mac_tx_packets_delta=arm["mac_tx_packets_delta"],mac_tx_retries_delta=arm["mac_tx_retries_delta"],
                mac_block_sums_match_window=all(sum(b[k] for b in bs)==arm[k] for k in ("mac_tx_packets_delta","mac_tx_retries_delta")),
                certified_wds_evidence=deepcopy(getattr(saved,"certified_wds_evidence",{})),
                source_classification="Frozen source reports counters/recipe interface, not an independent device-side control qualification"))
        if number in POOL:selected.append((number,record_by_id[(f"R{number}",arms[0]["commit"])],record_by_id[(f"R{number}",arms[POOL[number]]["commit"])]))
    if len(results)!=138:raise ValueError("Complete new138 hypotheses required")
    comparability = pool_comparability(selected)
    pooled_rows = []
    for number in POOL:
        arms = receipts[number]["iterations"]
        for r in rows:
            if r["round_id"]==f"R{number}" and r["treatment_id"] in (arms[0]["commit"],arms[POOL[number]]["commit"]):
                pooled_rows.append(r|dict(analysis_role="A" if r["treatment_id"]==arms[0]["commit"] else "T"))
    pooled = [audit_pair(pooled_rows,"A","T",m,role_field="analysis_role",scope="POOLED_R27_R28_R29_R32") for m in FOCUSED]
    for r in pooled:
        r.update(comparability_status=comparability["status"],round_ids=list(POOL),regime="bidir_6flow",
                 target_policy_id=selected[0][2].policy_key if comparability["recorded_packages_and_contexts_match"] else None,
                 control_policy_id=selected[0][1].policy_key if comparability["recorded_packages_and_contexts_match"] else None,
                 round_stratified_results=[x["source_hypothesis_id"] for x in results if int(x["scope"][1:]) in POOL and x["metric"]==r["metric"] and x["control"]==receipts[int(x["scope"][1:])]["iterations"][0]["commit"] and x["target"]==receipts[int(x["scope"][1:])]["iterations"][POOL[int(x["scope"][1:])]]["commit"]])
        if len(r["pairs"])!=46:raise ValueError("Pooled genuine IDs must total46")
    local["POOLED_R27_R28_R29_R32"] = pooled
    families = {"local_"+k+"_bound10":padded_family(v,10,"local_"+k+"_bound10") for k,v in local.items()}
    new = results+pooled
    for size in (324,500):families[f"new_known143_bound{size}"] = padded_family(new,size,f"new_known143_bound{size}")
    old_path = ROOT/"artifacts/autoresearch/waves_uvwx_20261024/wave_v_r22_to_r26_crossover_analysis.json"
    old = json.loads(old_path.read_text(encoding="utf-8"))["contrasts"]
    previous = [dict(source_hypothesis_id=r["contrast_id"],exact_rank=dict(p_value=r["wilcoxon"]["p_value"])) for r in old]
    if len(previous)!=324:raise ValueError("Prior known324 required unchanged")
    for size in (467,500):families[f"complete_known467_bound{size}"] = padded_family(previous+new,size,f"complete_known467_bound{size}")
    for r in new:
        r["family_adjusted_p"] = {k:v["adjusted_p"][r["source_hypothesis_id"]] for k,v in families.items() if r["source_hypothesis_id"] in v["adjusted_p"]}
    source_inputs = {"manifest":binding(BASE/"inputs_manifest.json"),
        "records":binding(BASE/"normalized_r1_to_r32_measurements_20261024.json"),
        "blocks":binding(BASE/"normalized_r16_to_r32_block_observations_20261024.json")}
    projections = []
    for r in new:
        projections.append(dict(source_hypothesis_id=r["source_hypothesis_id"],regime=r["regime"],round_ids=sorted({p["round_id"] for p in r["pairs"]}),
            target_policy_id=r["target_policy_id"],control_policy_id=r["control_policy_id"],paired_unit_ids=r["paired_unit_ids"],
            metric=r["metric"],direction=r["direction"],effect_hl=r["HL_estimate"],p_exact_rank=r["exact_rank"]["p_value"],
            holm324_adjusted_p=r["family_adjusted_p"]["new_known143_bound324"],holm500_adjusted_p=r["family_adjusted_p"]["new_known143_bound500"],
            family324_key="new_known143_bound324",family500_key="new_known143_bound500",
            comparability_status=r.get("comparability_status","WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON")))
    if [binding(p) for p in dependencies]!=dep_refs:raise ValueError("Dependencies changed during computation")
    return dict(schema_version=1,status="OFFLINE_EXACT_WDS_AUDIT_PENDING_INDEPENDENT_REVIEW",sources=sources,
        software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        source_inputs=source_inputs,numerical_dependencies=dep_refs,family_plan=binding(BASE/"wave_z_families_precomputation.json"),
        frozen_spec=binding(BASE/"inputs/waves_yzab_20261024_spec.md"),prior_unchanged_analysis=binding(old_path),
        counts=dict(new_windows=len(descriptions),records=150,new_rows=144,new_matched=54,crossed_rows=332,matched=106,sequential_R17=16,pooled=46),
        within_round_contrasts=results,pooled_contrasts=pooled,pool_comparability=comparability,families=families,
        requested_spec_claims=requested_claims(results),
        catalog_scope=dict(known_new=143,known_combined=467,Holm324_for_complete467="INAPPLICABLE_SCOPE_EXCEEDS_BOUND",not_all_project_research_tests=True),
        promotion_evidence=dict(source_inputs={k+"_sha256":v["sha256"] for k,v in source_inputs.items()},contrasts=projections,families=families,
            evidence_only_not_promotion_or_actuation=True),
        source_claim_audits=descriptions,design_diagnostics=designs,
        claim_status=dict(spec_counts="REFUTED_19_NOT20_ARMS_150_NOT151_RECORDS_332_NOT328_ROWS_106_NOT108_MATCHED_IDS",
            exact_mean_all19=all(r["literal_mean_audit"]["all_literal_equal"] for r in descriptions),
            finite_all_n4_95_and999="MATHEMATICALLY_IMPOSSIBLE_P_FLOOR_0.125_ABOVE_ALPHA",
            WMM_EDCA_TXOP="NOT_IDENTIFIED_BY_AQL1800_3600_OR_FQ256_FIELDS"),
        automatic_execution_allowed=False,physical_or_causal_acceptance=False,
        limits=["Frozen source certification labels, policy KEEP and nonzero WDS denominators do not certify independent restoration or physical control",
                "Pooled46 conditional exact DP is not2**46 enumeration; recorded package matching does not establish round invariance or independence",
                "Placeholders p1 are never-tested hypotheses in declared scoped completions, not invented complete project catalogs",
                "Source exact-mean contradictions remain; no rounding tolerance widened or summaries rewritten",
                "No original/livefiles, newerrounds, device/network/target execution, rawassembly/hex, credentials or installation"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=BASE/"wave_z_certified_wds_analysis.json")
    path = parser.parse_args().output.resolve()
    if path.parent!=BASE.resolve() or not path.name.startswith("wave_z_") or path.suffix!=".json":raise ValueError("Only new ownedWaveZoutput")
    result = build_analysis()
    with path.open("x",encoding="utf-8",newline="\n") as f:json.dump(result,f,indent=2,allow_nan=False);f.write("\n")
    print(json.dumps(dict(status=result["status"],contrasts=len(result["within_round_contrasts"]),pooled=len(result["pooled_contrasts"]))))


if __name__=="__main__":main()
