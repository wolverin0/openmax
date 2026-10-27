"""Offline exact R57..R60 audit. Saved package effects are not a retry mechanism.

Only frozen owned inputs and accepted prior outputs are read. No recipe,
target, network, actuator or process-control executor is imported or called.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from fractions import Fraction
import json
import math
from pathlib import Path
import platform
import re

import numpy as np
import scipy

from analysis.statistics.fmx_r43_to_r47_dyadic_zero_loss_audit import (
    enumerate_fraction_flips,exact_sign_flips,literal_metric)
from analysis.statistics.fmx_r48_to_r56_distance_goodput_dyadic_audit import (
    source_arm_audit,observed_utility,record_dict)
from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import multilevel_design_diagnostics,schedule_agreement
from analysis.statistics.fmx_r22_to_r26_crossover_audit import METRICS,_metric,_quality
from analysis.statistics.fmx_r27_to_r32_certified_wds_audit import binding,padded_family
from analysis.statistics.fmx_r33_to_r42_exact_holm500_audit import exact_effect,parse_source

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/autoresearch/waves_ao_to_ar_20261024'
ROUNDS=(57,58,59,60)
MANIFEST_SHA='5844355bb99e2dbc41c83cfb34c7c03ff5d6992679d19367470e3c761ab448d8'
FAMILY_SHA='306d39b5b2d99461b98d39e713eda2aabc3f69e982728f8574b187c901e13e8c'
RANK_FAMILY='new_rank24_bound500'
MEAN_FAMILY='new_meanflip24_bound500'


def pair_rows(rows,control,target,metric):
    """Explicit R57..R60 validator; no global edits or relabeled old IDs."""
    if not isinstance(rows,list) or not rows:raise ValueError('Explicit crossed rows required')
    seen=set();rounds=set();groups=defaultdict(list)
    for row in rows:
        if row.get('round_id') not in {f'R{n}' for n in ROUNDS}:raise ValueError('Owned frozen R57..R60 only')
        rounds.add(row['round_id'])
        if any(type(row.get(k)) is not int or row[k]<0 for k in ('block_index','crossover_step')):raise ValueError('Genuine integer block/step IDs required')
        if not isinstance(row.get('treatment_id'),str) or not row['treatment_id']:raise ValueError('Treatment identity required')
        identity=(row['round_id'],row['block_index'],row['crossover_step'])
        if identity in seen:raise ValueError('Duplicate source identity')
        seen.add(identity);groups[row['block_index']].append(row)
    if len(rounds)!=1:raise ValueError('No mixed-round inference or pooling')
    pairs=[]
    for block,group in sorted(groups.items()):
        a=[r for r in group if r['treatment_id']==control];b=[r for r in group if r['treatment_id']==target]
        if len(group)!=2 or len(a)!=1 or len(b)!=1:raise ValueError('One control and target per genuine block required')
        if {r['crossover_step'] for r in group}!={0,1}:raise ValueError('Exactlytwo source periods0/1 required')
        x,y=_metric(a[0],metric),_metric(b[0],metric)
        if x is None or y is None:raise ValueError('Missing block outcome cannot disappear')
        pairs.append(dict(round_id=a[0]['round_id'],block_index=block,control_mean=x,treatment_mean=y,
            difference=y-x,control_step=a[0]['crossover_step'],target_step=b[0]['crossover_step'],
            sequence='AB' if a[0]['crossover_step']==0 else 'BA'))
    return pairs


def period_adjusted_estimation(rows,control,target,metric):
    """Only the explicitly restricted no-differential-carryover point model."""
    pairs=pair_rows(rows,control,target,metric)
    ab=[p for p in pairs if p['sequence']=='AB'];ba=[p for p in pairs if p['sequence']=='BA']
    if not ab or not ba:return dict(status='NOT_IDENTIFIED_SINGLE_SEQUENCE',assumption='No causal claim')
    def mean(group):return sum((Fraction(str(p['treatment_mean']))-Fraction(str(p['control_mean'])) for p in group),Fraction())/len(group)
    direct=(mean(ab)+mean(ba))/2;period=(mean(ab)-mean(ba))/2
    blocks=sorted({r['block_index'] for r in rows});matrix=[];outcomes=[]
    for row in rows:
        matrix.append([1]+[int(row['block_index']==b) for b in blocks[1:]]+[row['crossover_step'],int(row['treatment_id']==target)])
        outcomes.append(_metric(row,metric))
    x=np.asarray(matrix,dtype=float);beta=np.linalg.lstsq(x,np.asarray(outcomes,dtype=float),rcond=None)[0]
    rank=int(np.linalg.matrix_rank(x))
    if rank!=x.shape[1]:raise ValueError('Restricted named model must be full rank')
    if not all(math.isclose(float(a),float(b),abs_tol=1e-9,rel_tol=1e-11) for a,b in ((direct,beta[-1]),(period,beta[-2]))):raise ValueError('Exact source-decimal coefficients disagree with least squares')
    return dict(status='IDENTIFIED_RESTRICTED_MODEL_NOT_CAUSAL_CERTIFICATION',
        model='BLOCK_FIXED_EFFECTS+PERIOD+CURRENT_TREATMENT_NO_DIFFERENTIAL_CARRYOVER',
        assumptions=['No differential carryover or unmodeled block-by-period response','Counterbalance is not randomization or independence','No separated current/lag causal effect'],
        AB_blocks=len(ab),BA_blocks=len(ba),columns=x.shape[1],rank=rank,direct_estimate=float(direct),period_estimate=float(period),
        direct_exact_fraction=str(direct),period_exact_fraction=str(period),numeric_direct_estimate=float(beta[-1]),numeric_period_estimate=float(beta[-2]),
        no_period_adjusted_inference_p_value='Raw difference sign flips are not an automatically valid nuisance-adjusted test')


def frozen_inputs():
    manifest=BASE/'inputs_manifest.json'
    if binding(manifest)['sha256']!=MANIFEST_SHA:raise ValueError('Frozen manifest changed')
    if binding(BASE/'wave_ap_family_recipe.json')['sha256']!=FAMILY_SHA:raise ValueError('Family definition changed')
    entries=json.loads(manifest.read_text(encoding='utf-8'))['entries']
    if len(entries)!=12:raise ValueError('Require12 frozen inputs')
    receipts,literals,refs,recipes={},{},[],{}
    for ref in entries:
        path=(ROOT/ref['path']).resolve()
        if ref['round'] not in ROUNDS or not path.is_relative_to((BASE/'inputs').resolve()):raise ValueError('Owned frozen R57..R60 inputs only')
        actual=binding(path)
        if any(actual[k]!=ref[k] for k in ('sha256','bytes')):raise ValueError('Frozen input drift')
        refs.append(actual|dict(round=ref['round']))
        if path.suffix=='.json':
            text=path.read_text(encoding='utf-8');receipts[ref['round']]=parse_source(text);literals[ref['round']]=parse_source(text,True)
        if path.suffix=='.py':recipes[ref['round']]=path.read_text(encoding='utf-8')
    if set(receipts)!=set(ROUNDS) or set(recipes)!=set(ROUNDS):raise ValueError('Missing current frozen receipt or recipe provenance')
    return receipts,literals,refs,recipes


def declared_context(payload,arm,saved=None):
    """Credit explicit declarations, never invent recipe application or RF range."""
    expected=dict(coverage_class=0,distance_m=100,slot_time_us=9,ack_timeout_us=18)
    for key,value in expected.items():
        if type(payload.get(key)) is not int or payload[key]!=value:raise ValueError('Exact payload timing declaration required')
    for declaration in (arm,arm.get('candidate_knobs')):
        if not isinstance(declaration,dict):raise ValueError('Treatment/knob declarations required')
        for key,value in expected.items():
            if key in ('coverage_class','distance_m') or key in declaration:
                if type(declaration.get(key)) is not int or declaration[key]!=value:raise ValueError('Conflicting treatment/knob timing declaration')
    if saved is not None and (saved['coverage_class']!=0 or saved['distance_meters']!=100):raise ValueError('Normalized declaration differs')
    return dict(**expected,provenance='EXPLICIT_SAVED_PAYLOAD_TREATMENT_KNOBS_DECLARATIONS',
        slot_ack_provenance='PAYLOAD_ONLY_WHEN_NOT_RECORDED_IN_TREATMENT_OR_KNOBS',
        physical_distance_verified=False,effective_runtime_application_verified=False,
        endpoint_states_originally_omit_distance=all('distance_meters' not in arm['candidate_knobs'][side+'_state'] for side in ('ap','cpe')))


def profile_claims(contrasts):
    five=METRICS[1:]
    claimed={57:{m:15 if m in METRICS[1:4] else 16 for m in five},58:{m:16 for m in five},
        59:{**{m:15 if m=='p99_rtt_ms' else 16 for m in five},'goodput_rx_mbps':9},
        60:{**{m:16 for m in five},'goodput_rx_mbps':11}}
    out=[]
    for row in contrasts:
        value=claimed[int(row['scope'][1:])].get(row['metric'])
        out.append(dict(round_id=row['scope'],metric=row['metric'],claimed_favorable=value,
            actual_favorable=row['favorable_blocks'],equal=row['equal_blocks'],matches=row['favorable_blocks']==value if value is not None else None,
            rank_p=row['exact_rank']['p_value'],sign_p=row['exact_sign']['p_value'],mean_flip_p=row['exact_sign_flips']['mean']['p_value'],
            rank_holm500=row['family_adjusted_p'][RANK_FAMILY]))
    return out


def numerical_claims(descriptions,utilities):
    gp={57:('105.0244140625','99.201171875'),58:(None,'94.4130859375'),
        59:('104.8505859375','104.830078125'),60:('105.3564453125','105.294921875')}
    out=[]
    for row in descriptions:
        n=int(row['round_id'][1:]);index=0 if '_iter0_' in row['iteration'] else 1;expected=gp[n][index]
        if expected is not None:
            delta=Fraction(str(row['summary']['goodput_mbps']))-Fraction(expected)
            out.append(dict(round_id=row['round_id'],iteration=row['iteration'],metric='goodput_mbps',
                claimed_literal=expected,actual=row['summary']['goodput_mbps'],exact_difference=str(delta),matches=not delta))
    for row in utilities:
        if row['round_id'] in ('R59','R60'):
            expected='0.019559' if row['round_id']=='R59' else '0.058395'
            loss=Fraction(row['loss_percent_exact'])
            out.append(dict(round_id=row['round_id'],metric='GP_loss_percent',claimed_display_literal=expected,
                actual=float(loss),actual_exact=str(loss),difference_from_display=str(loss-Fraction(expected)),
                claim_is_rounded_narrative_not_exact_source=True))
    return out


def telemetry_paths(value,path='$'):
    result=[]
    if isinstance(value,dict):
        for key,item in value.items():
            here=path+'.'+key
            if re.search(r'ampdu|a_mpdu|subframe|cwnd|cubic|tcp_info|ssthresh|retry_exhaust|mpdu_drop',key,re.I):result.append(here)
            result.extend(telemetry_paths(item,here))
    elif isinstance(value,list):
        for index,item in enumerate(value):result.extend(telemetry_paths(item,f'{path}[{index}]'))
    return result


def changed_coordinates(a,b,path=''):
    """Compare complete public policy declarations, not outcome-selected knobs."""
    if isinstance(a,dict) and isinstance(b,dict):
        result=[]
        for key in sorted(set(a)|set(b)):
            if key not in a or key not in b:result.append(path+'.'+key)
            else:result.extend(changed_coordinates(a[key],b[key],path+'.'+key))
        return result
    if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        return [p for i,(x,y) in enumerate(zip(a,b)) for p in changed_coordinates(x,y,f'{path}[{i}]')]
    return [] if a==b else [path]


def mechanism_assessment(receipts,records):
    target=lambda n:next(r for r in records if r['round_id']==f'R{n}' and r['iteration'].startswith(f'r{n}_iter1_'))
    rows=[target(n) for n in (50,51,58)];comparisons=[]
    for a,b in ((rows[0],rows[1]),(rows[0],rows[2]),(rows[1],rows[2])):
        comparisons.append(dict(control_round=a['round_id'],target_round=b['round_id'],
            full_policy_changed_coordinates=changed_coordinates(json.loads(a['policy_key']),json.loads(b['policy_key'])),
            declared_context_changed=[k for k in ('workload_regime','active_flow_count','bidirectional','coverage_class','distance_meters','encryption_mode','associated_cpes') if a.get(k)!=b.get(k)],
            control_GP=a['goodput_mbps'],target_GP=b['goodput_mbps'],control_DL=a['dl_goodput_mbps'],target_DL=b['dl_goodput_mbps'],
            paired_crossround_p_value=None,isolated_long_retry_control=False))
    return dict(status='HYPOTHESIS_NOT_DEMONSTRATED',claim='long_retry4to3 causes earlier A-MPDU subframe drops then AP CUBICcwndbackoff',
        direct_telemetry_named_fields_in_R58=telemetry_paths(receipts[58]),
        field_search_is_not_proof_of_complete_instrumentation=True,
        available_aggregate_telemetry=['GP/DL/UL','RTT arrays','MACtx/retry counters','aggregate retransmits','source health'],
        crossround_comparisons=comparisons,
        limits=['Crossround package/context changes are not an isolated long-retry intervention.',
            'Aggregate retry/retransmit/GP alone cannot identify early A-MPDU subframe loss, CUBIC attribution or cwnd trajectory.',
            'Even a named field would require validated semantics/chronology and controlled mechanism evidence; no new capture is requested by this offline audit.'],
        mechanism_causal_acceptance=False)


def build_analysis():
    from orchestration.autoresearch.fmx_live_dataset import load_all60_measurements,load_all60_block_observations
    names=('fmx_r43_to_r47_dyadic_zero_loss_audit','fmx_r48_to_r56_distance_goodput_dyadic_audit',
        'fmx_r33_to_r42_exact_holm500_audit','fmx_r27_to_r32_certified_wds_audit','fmx_r22_to_r26_crossover_audit',
        'fmx_r16_to_r21_real_crossover_audit','fmx_r15_and_crossover_statistical_audit','fmx_r10_to_r14_causal_and_power_analysis')
    dependencies=[Path(__file__),ROOT/'orchestration/autoresearch/fmx_live_dataset.py']+[ROOT/f'analysis/statistics/{n}.py' for n in names]
    dep_refs=[binding(p) for p in dependencies]
    receipts,literals,refs,recipes=frozen_inputs();typed,_=load_all60_measurements();blocks=load_all60_block_observations()
    records=[record_dict(r) for r in typed];by_id={(r['round_id'],r['iteration']):r for r in records}
    new=[b for b in blocks['crossed'] if int(b['round_id'][1:]) in ROUNDS]
    counts=dict(records=len(records),new_arms=sum(len(x['iterations']) for x in receipts.values()),crossed_rows=len(blocks['crossed']),
        new_crossed_rows=len(new),matched_ids=len({(b['round_id'],b['block_index']) for b in blocks['crossed']}),
        new_matched_ids=len({(b['round_id'],b['block_index']) for b in new}),sequential_R17=len(blocks['sequential']))
    if counts!=dict(records=220,new_arms=8,crossed_rows=1116,new_crossed_rows=128,matched_ids=470,new_matched_ids=64,sequential_R17=16):raise ValueError('Actual220/1116/470corpus required')
    contrasts,descriptions,utilities,designs=[],[],[],[]
    for number in ROUNDS:
        arms=receipts[number]['iterations']
        if len(arms)!=2:raise ValueError('Exactlytwo source arms required')
        control,target=[a['commit'] for a in arms];group=[b for b in new if b['round_id']==f'R{number}']
        if len(group)!=32:raise ValueError('Exactly32 source rows per round required')
        literal_by={(a['commit'],b['block_index']):b for a in literals[number]['iterations'] for b in a['repetition_blocks']}
        for metric in METRICS:
            pairs=pair_rows(group,control,target,metric)
            if len(pairs)!=16:raise ValueError('Exactly16 genuine paired units required')
            d=[p['difference'] for p in pairs];effect=exact_effect(d);flips=exact_sign_flips(d)
            if any(flips[k]['p_value']!=effect['exact_'+k]['p_value'] for k in ('rank','sign')):raise ValueError('65536enumeration differs from accepted DP')
            decimal=[literal_metric(literal_by[(target,p['block_index'])],metric)-literal_metric(literal_by[(control,p['block_index'])],metric) for p in pairs]
            sensitivity=enumerate_fraction_flips(decimal);saved=by_id[(f'R{number}',target)]
            contrasts.append(dict(source_hypothesis_id=json.dumps([f'R{number}',control,target,metric],separators=(',',':')),scope=f'R{number}',
                control=control,target=target,regime=saved['workload_regime'],control_policy_id=by_id[(f'R{number}',control)]['policy_key'],target_policy_id=saved['policy_key'],
                metric=metric,direction='lower' if metric in METRICS[1:4] else 'higher',
                paired_unit_ids=[dict(round_id=p['round_id'],block_index=p['block_index']) for p in pairs],pairs=pairs,
                favorable_blocks=sum(x<0 if metric in METRICS[1:4] else x>0 for x in d),equal_blocks=sum(x==0 for x in d),
                quality=_quality(group),exact_sign_flips=flips,
                source_decimal_sensitivity=dict(exact_flips=sensitivity,literal_differences=[str(v) for v in decimal],
                    rank_p_changed=sensitivity['rank']['p_value']!=flips['rank']['p_value'],mean_p_changed=sensitivity['mean']['p_value']!=flips['mean']['p_value']),
                period_adjusted=period_adjusted_estimation(group,control,target,metric),**effect))
        diagnostic=multilevel_design_diagnostics(group)|dict(round_id=f'R{number}')
        diagnostic['schedule_agreement']=schedule_agreement(group,receipts[number]['crossover_schedule'],{'A':control,'B':target})
        diagnostic['interpretation']='Fullperiod/current/lag alias retained; restricted current point estimate assumes no differential carryover, not separated causality.'
        designs.append(diagnostic)
        for index,arm in enumerate(arms):
            saved=by_id[(f'R{number}',arm['commit'])];audit=source_arm_audit(number,arm,literals[number]['iterations'][index],saved)
            audit['declared_timing_context']=declared_context(receipts[number],arm,saved)
            audit['recipe_distance_application_call_present']=bool(re.search(r'\bapply_r33_state_with_distance\s*\(',recipes[number]))
            descriptions.append(audit)
        a,b=(by_id[(f'R{number}',k)] for k in (control,target));utility=observed_utility(a['goodput_mbps'],b['goodput_mbps'])
        loss=Fraction(utility['loss_percent_exact'])
        utilities.append(dict(round_id=f'R{number}',**utility,passes_observed_less_than_0_02_percent=loss<Fraction(1,50),
            preserved_GP_percent=float(100-loss),preserved_GP_percent_exact=str(100-loss),
            control_retry_exact=str(Fraction(a['mac_tx_retries'],a['mac_tx_packets'])),target_retry_exact=str(Fraction(b['mac_tx_retries'],b['mac_tx_packets'])),
            target_retry_lower=Fraction(b['mac_tx_retries'],b['mac_tx_packets'])<Fraction(a['mac_tx_retries'],a['mac_tx_packets']),
            observed_GP_block_wins=next(c['favorable_blocks'] for c in contrasts if c['scope']==f'R{number}' and c['metric']=='goodput_rx_mbps'),
            statistical_equivalence_or_noninferiority=False))
    if len(contrasts)!=24:raise ValueError('Complete24 primary contrasts required')
    priorpath=ROOT/'artifacts/autoresearch/waves_ak_to_an_20261024/wave_al_distance_goodput_dyadic_analysis.json'
    prior=json.loads(priorpath.read_text(encoding='utf-8'))['families']['complete_known_rank831_bound831']['known_hypotheses']
    if len(prior)!=831:raise ValueError('Prior accepted831required unchanged')
    families={RANK_FAMILY:padded_family(contrasts,500,RANK_FAMILY),
        'complete_known_rank855_bound855':padded_family([dict(source_hypothesis_id=k,exact_rank=dict(p_value=p)) for k,p in prior.items()]+contrasts,855,'complete_known_rank855_bound855')}
    members=[dict(source_hypothesis_id='MEANFLIP:'+r['source_hypothesis_id'],exact_rank=dict(p_value=r['exact_sign_flips']['mean']['p_value'])) for r in contrasts]
    families[MEAN_FAMILY]=padded_family(members,500,MEAN_FAMILY)|dict(statistic='SECONDARY_INTEGER_EXACT_MEAN_FLIP_NOT_RANK')
    for row in contrasts:
        row['family_adjusted_p']={k:v['adjusted_p'][row['source_hypothesis_id']] for k,v in families.items() if row['source_hypothesis_id'] in v['adjusted_p']}
        row['mean_flip_holm500_adjusted_p']=families[MEAN_FAMILY]['adjusted_p']['MEANFLIP:'+row['source_hypothesis_id']]
    inputs={k:binding(BASE/v) for k,v in dict(records='normalized_r1_to_r60_measurements_20261024.json',blocks='normalized_r16_to_r60_block_observations_20261024.json',manifest='inputs_manifest.json').items()}
    projection=[dict(source_hypothesis_id=r['source_hypothesis_id'],regime=r['regime'],target_policy_id=r['target_policy_id'],control_policy_id=r['control_policy_id'],
        round_ids=[r['scope']],paired_unit_ids=r['paired_unit_ids'],metric=r['metric'],direction=r['direction'],effect_hl=r['HL_estimate'],
        p_exact_rank=r['exact_rank']['p_value'],holm500_adjusted_p=r['family_adjusted_p'][RANK_FAMILY],family500_key=RANK_FAMILY,
        comparability_status='WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON',statistic='PRIMARY_EXACT_SIGNED_RANK_NOT_MEAN_FLIP') for r in contrasts]
    if [binding(p) for p in dependencies]!=dep_refs:raise ValueError('Dependency changed during calculation')
    return dict(schema_version=1,status='OFFLINE_RETRY64_PARITY_AUDIT_PENDING_INDEPENDENT_ACCEPTANCE',counts=counts,
        software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),sources=refs,source_inputs=inputs,numerical_dependencies=dep_refs,
        family_plan=binding(BASE/'wave_ap_family_recipe.json'),prespecified_contract=binding(BASE/'prespecified_contract.json'),prior_unchanged_analysis=binding(priorpath),
        contrasts=contrasts,families=families,source_claim_audits=descriptions,observed_utility=utilities,
        requested_win_claims=profile_claims(contrasts),numerical_source_claims=numerical_claims(descriptions,utilities),design_diagnostics=designs,
        R58_mechanism_assessment=mechanism_assessment(receipts,records),
        catalog_scope=dict(primary_new_known=24,primary_prior_known=831,complete_primary_known=855,complete_primary_Holm500='INAPPLICABLE_KNOWN855_EXCEEDS500',mean_flip_family_separate=True,not_all_project_tests=True),
        promotion_evidence=dict(source_inputs={k+'_sha256':v['sha256'] for k,v in inputs.items()},contrasts=projection,
            families={k:v for k,v in families.items() if k!=MEAN_FAMILY},evidence_only_not_promotion=True),
        automatic_execution_allowed=False,physical_or_causal_acceptance=False,
        limits=['64actual matched block IDs, not1280independent physical experiments. Conditional symmetric/sign-exchangeable block assumptions not proven.',
            'Explicit100/class0/slot9/ack18 are saved declarations, not verified recipe application, geographic separation or effective RF authority.',
            'Rank/sign/meanflip are distinct tests;48marginal95/99.9sets are not simultaneous855-test intervals.',
            'Observed near-equal mean GP and9/16 or11/16 wins do not prove equivalence/noninferiority; all adverse block outcomes remain.',
            'Fullcarryover alias retained; restricted point estimates assume no differential carryover; no causalperiod p-values.',
            'No target/network/recipe/process operations; only owned frozen new files and accepted prior offline data/source.'])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=BASE/'wave_ap_retry64_goodput_parity_analysis.json')
    path=parser.parse_args().output.resolve()
    if path.parent!=BASE.resolve() or not path.name.startswith('wave_ap_') or path.suffix!='.json':raise ValueError('Owned exclusive AP output required')
    if path.exists():raise FileExistsError(path)
    result=build_analysis()
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=result['status'],contrasts=len(result['contrasts']),arms=len(result['source_claim_audits']))))

if __name__=='__main__':main()
