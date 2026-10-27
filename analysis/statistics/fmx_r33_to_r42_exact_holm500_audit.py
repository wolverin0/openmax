"""Pure offline R33-R42 audit, exact DP through94 identified block units.

Full known-family bounds, source precision and policy mixtures stay explicit.
No device/recipe execution, actuator or implicit physical certification.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from decimal import Decimal
from fractions import Fraction
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
from analysis.statistics.fmx_r10_to_r14_causal_and_power_analysis import sample,probability
from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import _merge_atoms,multilevel_design_diagnostics,schedule_agreement
from analysis.statistics.fmx_r22_to_r26_crossover_audit import METRICS,_metric,_quality
from analysis.statistics.fmx_r27_to_r32_certified_wds_audit import binding,literal_mean_audit,padded_family,pool_comparability
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/autoresearch/waves_ac_to_af_20261024'
ROUNDS=tuple(range(33,43))
ALLOWED_ROUNDS=tuple(range(27,43))
FOCUSED=METRICS[1:]
POOL={27:2,28:1,29:1,32:1,40:1,41:1,42:1}


@lru_cache(maxsize=256)
def rank_polynomial(weights):
    """Exact subset-count DP packed in base2**bits, with no coefficient carries.

    Every coefficient and every subset sum of coefficients is at most2**n.
    Radix uses at least n+1 bits. Thus polynomial multiplication by (1+x**w)
    is one shift/add; low-digit coefficient sums are exact modulo radix-1.
    This is polynomial rank-sum DP, not enumeration of sign assignments.
    """
    n=len(weights)
    if not 1<=n<=128 or any(type(w) is not int or not 1<=w<=2*n for w in weights):raise ValueError('Bounded integer doubled-rank weights required')
    bits=8*((n+8)//8);packed=1
    for w in weights:packed+=packed<<(w*bits)
    return packed,bits


def exact_rank(differences):
    """Same Wilcox-zero conditional DP as prior accepted API; raised owned bound."""
    data=sample(differences,minimum=1)
    if len(data)>128:raise ValueError('Bounded128 supplied independent units')
    nz=data[data!=0]
    if not len(nz):return dict(p_value=1.,positive_rank_sum=0.,negative_rank_sum=0.,nonzero_blocks=0,zero_blocks=len(data),sign_assignments=1,method='EXACT_CONDITIONAL_SIGN_RANK_DP_WILCOX_ZEROS')
    doubled=np.rint(2*stats.rankdata(np.abs(nz),method='average')).astype(int)
    weights=tuple(sorted(int(x) for x in doubled));packed,bits=rank_polynomial(weights)
    observed=int(doubled[nz>0].sum());total=sum(weights);distance=abs(2*observed-total)
    if not distance:extreme=2**len(nz)
    else:
        low_max=(total-distance)//2
        low_digits=packed&((1<<((low_max+1)*bits))-1)
        extreme=2*(low_digits%((1<<bits)-1))
    return dict(p_value=extreme/(2**len(nz)),positive_rank_sum=observed/2,negative_rank_sum=(total-observed)/2,
        nonzero_blocks=len(nz),zero_blocks=len(data)-len(nz),sign_assignments=2**len(nz),
        minimum_possible_two_sided_p=2**(1-len(nz)),method='EXACT_CONDITIONAL_SIGN_RANK_DP_WILCOX_ZEROS')


def confidence_set(differences,alpha=.05):
    """Full exact acceptance union, not an asymptotic or convex-hull interval."""
    alpha=probability(alpha);data=sample(differences,minimum=1)
    if len(data)>128:raise ValueError('Bounded128 supplied independent units')
    if 2**(1-len(data))>alpha:return dict(components=[dict(lower=None,upper=None,lower_closed=False,upper_closed=False)],confidence=1-alpha,whole_real_line=True,independent_blocks=len(data),reason='SMALL_N_EXACT_P_FLOOR_EXCEEDS_ALPHA')
    points=sorted(set(float(a/2+b/2) for i,a in enumerate(data) for b in data[i:]))
    if not all(math.isfinite(v) for v in points):raise ValueError('Nonfinite Walsh arithmetic')
    atoms=[]
    for i,left in enumerate(points):
        delta=data-left
        if not np.isfinite(delta).all():raise ValueError('Nonfinite shifted differences')
        if exact_rank(delta)['p_value']>alpha:atoms.append(dict(lower=left,upper=left,lower_closed=True,upper_closed=True))
        if i+1<len(points):
            right=points[i+1];middle=left/2+right/2
            if exact_rank(data-middle)['p_value']>alpha:atoms.append(dict(lower=left,upper=right,lower_closed=False,upper_closed=False))
    return dict(components=_merge_atoms(atoms),confidence=1-alpha,whole_real_line=False,independent_blocks=len(data),tested_breakpoints=len(points),reason='EXACT_SIGNED_RANK_ACCEPTANCE_SET_NOT_HULL',endpoint_convention='None=-/+infinity; emptycomponents=emptyset')


def exact_effect(differences):
    values=sample(differences,minimum=1)
    rank=exact_rank(values);positive=int((values>0).sum());negative=int((values<0).sum());n=positive+negative
    sign=dict(p_value=float(stats.binomtest(positive,n,.5).pvalue) if n else 1.,positive=positive,negative=negative,zeros=len(values)-n,method='EXACT_BINOMIAL_CONDITIONAL_NONZERO_SIGNS')
    walsh=sorted(float(a/2+b/2) for i,a in enumerate(values) for b in values[i:])
    hl=walsh[(len(walsh)-1)//2]/2+walsh[len(walsh)//2]/2
    return dict(exact_rank=rank,exact_sign=sign,HL_estimate=hl,derived_Walsh_terms=len(walsh),independent_units_assumed=len(values),confidence_sets={'95':confidence_set(values,.05),'99.9':confidence_set(values,.001)},assumptions='Conditional on supplied finite float differences and independent symmetric sign-exchangeable block units; IDs do not prove independence, invariant shift or washout.')


def parse_source(text,decimal=False):
    """Only explicit CRASH/disqualified evaluation Infinity may be metadata."""
    marker=object();data=json.loads(text,parse_float=Decimal if decimal else float,parse_constant=lambda x:marker if x=='Infinity' else (_ for _ in ()).throw(ValueError('Unsupported nonfinite token')))
    def walk(value,path=()):
        if value is marker:
            if len(path)!=4 or path[0]!='iterations' or type(path[1]) is not int or path[2:]!=('evaluation','fmx_loss'):raise ValueError('Nonfinite outside evaluation loss')
            evaluation=data['iterations'][path[1]]['evaluation']
            if evaluation.get('decision')!='crash' or evaluation.get('disqualified') is not True:raise ValueError('Nonfinite without explicit disqualified crash')
            evaluation['fmx_loss']={'nonfinite':'Infinity'}
        elif isinstance(value,dict):
            for k,v in list(value.items()):walk(v,path+(k,))
        elif isinstance(value,list):
            for i,v in enumerate(value):walk(v,path+(i,))
    walk(data);return data


def frozen_inputs():
    manifest=json.loads((BASE/'inputs_manifest.json').read_text(encoding='utf-8'))['entries']
    if len(manifest)!=30:raise ValueError('Require30 frozen inputs')
    receipts,literals,refs={},{},[]
    for ref in manifest:
        path=(ROOT/ref['path']).resolve()
        if not path.is_relative_to((BASE/'inputs').resolve()) or ref['round'] not in ROUNDS:raise ValueError('Only owned frozen inputs')
        actual=binding(path)
        if any(actual[k]!=ref[k] for k in ('bytes','sha256')):raise ValueError('Frozen input changed')
        refs.append(actual|dict(round=ref['round']))
        if path.suffix=='.json':
            text=path.read_text(encoding='utf-8');receipts[ref['round']]=parse_source(text);literals[ref['round']]=parse_source(text,True)
    if set(receipts)!=set(ROUNDS):raise ValueError('Missing current round')
    return receipts,literals,refs


def validate_rows(rows):
    if not isinstance(rows,list) or not rows:raise ValueError("Explicit crossed rows required")
    seen = set()
    for r in rows:
        if r.get("round_id") not in {f"R{n}" for n in ALLOWED_ROUNDS}:raise ValueError("Frozen crossed round required")
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



def _comparability(selected):
    result=pool_comparability(selected)
    coverage=[dict(round_id=f'R{n}',control=getattr(a,'coverage_class',None),target=getattr(b,'coverage_class',None)) for n,a,b in selected]
    coverage_match=all(r['control']==coverage[0]['control'] and r['target']==coverage[0]['target'] and r['control']==r['target'] for r in coverage)
    result['coverage_class_context']=coverage
    if not coverage_match:
        result['recorded_packages_and_contexts_match']=False
        result['status']='MIXTURE_ONLY_EXPLICIT_DECLARED_DIFFERENCES'
    return result


def _source_audit(number,arm,literal,saved):
    blocks=arm['repetition_blocks'];raw=arm['raw_rtts_ms']
    q={name:float(np.quantile(raw,prob)) for name,prob in (('p50_rtt_ms',.5),('p95_rtt_ms',.95),('p99_rtt_ms',.99))}
    quantile_deltas={name:arm['observation'][name]-v for name,v in q.items()}
    return dict(round_id=f'R{number}',iteration=arm['commit'],policy_id=saved.policy_key,
        literal_mean_audit=literal_mean_audit(literal),
        AC_literal_consistency=saved.block_mean_consistent,
        python_float_consistency=saved.certified_wds_evidence.get('block_mean_float_consistent'),
        numpy_float_consistency=saved.certified_wds_evidence.get('block_mean_numpy_consistent'),
        exact_numpy_quantiles=all(v==0 for v in quantile_deltas.values()),numpy_quantile_deltas=quantile_deltas,
        chronology_matches=raw==[x for b in blocks for x in b['rtts_ms']],
        attempted_pings=sum(b['pings_sent'] for b in blocks),received_pings=sum(b['pings_rcvd'] for b in blocks),
        saved_loss_pct=arm['observation']['packet_loss_pct'],saved_goodput_mbps=arm['observation']['goodput_rx_mbps'],
        mac_tx_packets=arm['mac_tx_packets_delta'],mac_tx_retries=arm['mac_tx_retries_delta'],
        mac_retry_rate_from_counters=arm['mac_tx_retries_delta']/arm['mac_tx_packets_delta'] if arm['mac_tx_packets_delta'] else None,
        mac_sums_match=all(sum(b[k] for b in blocks)==arm[k] for k in ('mac_tx_packets_delta','mac_tx_retries_delta')),
        evaluation=arm.get('evaluation'),source_failure_metadata=saved.source_failure_metadata,
        window_restoration_reported=saved.restoration_verified,window_station_drops=saved.station_drops,
        coverage_class=saved.coverage_class,timing_distance_meters=saved.distance_meters,
        limits='Exact decimal, Python float, NumPy mean and quantile equality are separate contracts. A label/readback is not independent physical acceptance. Timing distance does not prove physical range.')


def build_analysis():
    from orchestration.autoresearch.fmx_offline_data import load_all42_measurements,load_all42_block_observations
    paths=[Path(__file__),ROOT/'orchestration/autoresearch/fmx_offline_data.py',
        ROOT/'analysis/statistics/fmx_r27_to_r32_certified_wds_audit.py',ROOT/'analysis/statistics/fmx_r22_to_r26_crossover_audit.py',
        ROOT/'analysis/statistics/fmx_r16_to_r21_real_crossover_audit.py',ROOT/'analysis/statistics/fmx_r15_and_crossover_statistical_audit.py',
        ROOT/'analysis/statistics/fmx_r10_to_r14_causal_and_power_analysis.py']
    dep_refs=[binding(x) for x in paths]
    receipts,literals,refs=frozen_inputs();records,_=load_all42_measurements();blocks=load_all42_block_observations()
    by_id={(r.round_id,r.iteration):r for r in records};rows=[r for r in blocks['crossed'] if int(r['round_id'][1:]) in ROUNDS]
    counts=dict(records=len(records),new_windows=sum(len(x['iterations']) for x in receipts.values()),crossed_rows=len(blocks['crossed']),new_rows=len(rows),matched=len({(r['round_id'],r['block_index']) for r in blocks['crossed']}),new_matched=len({(r['round_id'],r['block_index']) for r in rows}),sequential_R17=len(blocks['sequential']))
    if counts!=dict(records=184,new_windows=34,crossed_rows=540,new_rows=208,matched=182,new_matched=76,sequential_R17=16):raise ValueError('Unexpected actual frozen counts')
    contrasts,descriptions,designs,local=[],[],[],{}
    for number,receipt in receipts.items():
        arms=receipt['iterations'];group=[r for r in rows if r['round_id']==f'R{number}']
        for a,b in combinations(arms,2):
            for metric in METRICS:
                r=audit_pair(group,a['commit'],b['commit'],metric)
                saved=by_id[(f'R{number}',b['commit'])]
                r.update(regime=saved.workload_regime,target_policy_id=saved.policy_key,control_policy_id=by_id[(f'R{number}',a['commit'])].policy_key,coverage_class=saved.coverage_class,timing_distance_meters=saved.distance_meters)
                contrasts.append(r)
        for target in arms[1:]:
            key=f'local_R{number}_{target["commit"]}_bound10'
            local[key]=[r for r in contrasts if r['scope']==f'R{number}' and r['control']==arms[0]['commit'] and r['target']==target['commit'] and r['metric'] in FOCUSED]
        diag=multilevel_design_diagnostics(group)|dict(round_id=f'R{number}')
        diag['schedule_agreement']=schedule_agreement(group,receipt['crossover_schedule'],{chr(65+i):a['commit'] for i,a in enumerate(arms)})
        designs.append(diag)
        for i,arm in enumerate(arms):descriptions.append(_source_audit(number,arm,literals[number]['iterations'][i],by_id[(f'R{number}',arm['commit'])]))
    if len(contrasts)!=270:raise ValueError('Require all270 within-round comparisons')
    # Prior frozen normalized blocks supply old rounds; no original sources read.
    pool_groups={};pool_comparison={};pooled=[]
    for scope,rounds,n in [('MIXTURE94',tuple(POOL),94),('COMMON_PACKAGE78',tuple(x for x in POOL if x!=41),78)]:
        selected=[];pool_rows=[]
        for number in rounds:
            all_rows=[r for r in blocks['crossed'] if r['round_id']==f'R{number}']
            candidates=sorted({r['treatment_id'] for r in all_rows})
            # Explicit input commit prefixes identify preselected source arm positions, never outcome ranking.
            a=next(x for x in candidates if x.startswith(f'r{number}_iter0_'))
            b=next(x for x in candidates if x.startswith(f'r{number}_iter{POOL[number]}_'))
            selected.append((number,by_id[(f'R{number}',a)],by_id[(f'R{number}',b)]))
            pool_rows.extend(r|dict(analysis_role='A' if r['treatment_id']==a else 'T') for r in all_rows if r['treatment_id'] in (a,b))
        comparison=_comparability(selected);pool_comparison[scope]=comparison
        if scope=='MIXTURE94' and comparison['recorded_packages_and_contexts_match']:raise ValueError('Retry53 mixture incorrectly collapsed')
        for metric in FOCUSED:
            r=audit_pair(pool_rows,'A','T',metric,role_field='analysis_role',scope=scope)
            if len(r['pairs'])!=n:raise ValueError('Pool genuine unit count mismatch')
            r.update(regime='bidir_6flow',round_ids=[f'R{x}' for x in rounds],comparability_status=comparison['status'],
                target_policy_id=selected[0][2].policy_key if comparison['recorded_packages_and_contexts_match'] else None,
                control_policy_id=selected[0][1].policy_key if comparison['recorded_packages_and_contexts_match'] else None,
                interpretation='Conditional pooled mixture only, not a single treatment effect' if scope=='MIXTURE94' else 'Recorded package/common context only; independence, effective state and invariant causal shift unproven',
                round_strata=[dict(round_id=f'R{number}',control=a.iteration,target=b.iteration,target_policy_id=b.policy_key,control_policy_id=a.policy_key) for number,a,b in selected])
            pooled.append(r)
        pool_groups[scope]=pool_rows
    new=contrasts+pooled
    families={k:padded_family(v,10,k) for k,v in local.items()}
    for size in (324,500):families[f'new_known280_bound{size}']=padded_family(new,size,f'new_known280_bound{size}')
    oldpath=ROOT/'artifacts/autoresearch/waves_yzab_20261024/wave_z_certified_wds_analysis.json';old=json.loads(oldpath.read_text(encoding='utf-8'))['families']['complete_known467_bound467']['known_hypotheses']
    previous=[dict(source_hypothesis_id=i,exact_rank=dict(p_value=p)) for i,p in old.items()]
    if len(previous)!=467:raise ValueError('Prior known467 required unchanged')
    families['complete_known747_bound747']=padded_family(previous+new,747,'complete_known747_bound747')
    for r in new:r['family_adjusted_p']={key:value['adjusted_p'][r['source_hypothesis_id']] for key,value in families.items() if r['source_hypothesis_id'] in value['adjusted_p']}
    requested=[]
    for r in contrasts:
        if r['scope'] in ('R40','R41','R42') and r['metric'] in FOCUSED:
            expected=15 if r['scope']=='R40' and r['metric']=='p99_rtt_ms' else 16
            requested.append(dict(source_hypothesis_id=r['source_hypothesis_id'],round_id=r['scope'],metric=r['metric'],claimed_favorable=expected,actual_favorable=r['favorable_blocks'],equal_blocks=r['equal_blocks'],matches=r['favorable_blocks']==expected,p_rank=r['exact_rank']['p_value'],p_sign=r['exact_sign']['p_value'],claimed_unanimous_floor=2**-15,actual_p_equals_unanimous_floor=r['exact_rank']['p_value']==2**-15))
    source_inputs={k:binding(BASE/v) for k,v in {'records':'normalized_r1_to_r42_measurements_20261024.json','blocks':'normalized_r16_to_r42_block_observations_20261024.json','manifest':'inputs_manifest.json'}.items()}
    projection=[]
    for r in new:
        projection.append(dict(source_hypothesis_id=r['source_hypothesis_id'],regime=r['regime'],target_policy_id=r['target_policy_id'],control_policy_id=r['control_policy_id'],round_ids=sorted({p['round_id'] for p in r['pairs']}),paired_unit_ids=r['paired_unit_ids'],metric=r['metric'],direction=r['direction'],effect_hl=r['HL_estimate'],p_exact_rank=r['exact_rank']['p_value'],holm324_adjusted_p=r['family_adjusted_p']['new_known280_bound324'],holm500_adjusted_p=r['family_adjusted_p']['new_known280_bound500'],family324_key='new_known280_bound324',family500_key='new_known280_bound500',comparability_status=r.get('comparability_status','WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON'),coverage_class=r.get('coverage_class'),timing_distance_meters=r.get('timing_distance_meters')))
    if [binding(x) for x in paths]!=dep_refs:raise ValueError('Dependency changed during analysis')
    return dict(schema_version=1,status='OFFLINE_EXACT_ANALYSIS_PENDING_INDEPENDENT_ACCEPTANCE',software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),counts=counts,sources=refs,source_inputs=source_inputs,numerical_dependencies=dep_refs,prior_unchanged_analysis=binding(oldpath),frozen_spec=binding(BASE/'inputs/waves_ac_to_af_20261024_spec.md'),family_plan=binding(BASE/'wave_ad_family_recipe.json'),within_round_contrasts=contrasts,pooled_contrasts=pooled,pool_comparability=pool_comparison,families=families,source_claim_audits=descriptions,requested_win_claims=requested,design_diagnostics=designs,catalog_scope=dict(new_known=280,prior_known=467,complete_known=747,Holm500_complete747='INAPPLICABLE_KNOWN_SCOPE_EXCEEDS_BOUND',not_all_project_tests=True),promotion_evidence=dict(source_inputs={k+'_sha256':v['sha256'] for k,v in source_inputs.items()},contrasts=projection,families=families,evidence_only_not_promotion_or_actuation=True),automatic_execution_allowed=False,physical_or_causal_acceptance=False,limits=['Exact rank and confidence sets conditional on supplied float differences; source-decimal tie sensitivity is a separate diagnostic, not silently repaired.','Marginal95 and99.9 exact inversion, not simultaneous intervals. n4 p-floor0.125 means unbounded sets at both levels.','94-unit pool mixes retry53 and retry74;78-unit pool requires recorded full-package/context match and still no proof of independent invariant block effects.','All4 R36 crash/disqualified failures remain, including source station-drop1; OOM physical narrative is not independently certified.','Coverage_class/timing distance is not proof of physical3km/6km. Source exactrational/Pythonfloat/NumPy summaries remain separate.','No original/newer/live files, target execution, networking or actuator.'])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=BASE/'wave_ad_exact_holm500_analysis.json');path=parser.parse_args().output.resolve()
    if path.parent!=BASE.resolve() or not path.name.startswith('wave_ad_') or path.suffix!='.json':raise ValueError('Only new owned WaveAD output')
    result=build_analysis()
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=result['status'],within=len(result['within_round_contrasts']),pooled=len(result['pooled_contrasts']))))


if __name__=='__main__':main()
