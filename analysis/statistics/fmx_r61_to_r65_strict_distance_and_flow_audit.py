"""Offline frozen R61-R65 exact distance/flow package audit; no actuator.

Recorded timing contexts do not demonstrate effective settings or physical range.
R63 cannot satisfy five-outcome unanimity by relabeling a15/16 p50 result.
"""
from __future__ import annotations
import argparse
import ast
from collections import defaultdict
from fractions import Fraction
import json
import math
from pathlib import Path
import platform
import re
import numpy as np
import scipy
from analysis.statistics.fmx_r43_to_r47_dyadic_zero_loss_audit import enumerate_fraction_flips,exact_sign_flips,literal_metric
from analysis.statistics.fmx_r48_to_r56_distance_goodput_dyadic_audit import source_arm_audit,observed_utility,record_dict
from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import multilevel_design_diagnostics,schedule_agreement
from analysis.statistics.fmx_r22_to_r26_crossover_audit import METRICS,_metric,_quality
from analysis.statistics.fmx_r27_to_r32_certified_wds_audit import binding,padded_family
from analysis.statistics.fmx_r33_to_r42_exact_holm500_audit import exact_effect,parse_source
from analysis.statistics.fmx_r57_to_r60_retry64_goodput_parity_audit import changed_coordinates

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/autoresearch/waves_as_to_av_20261024'
ROUNDS=(61,62,63,64,65)
MANIFEST_SHA='902990cb6d38ca0ae66b0b78f375e16fb1bb6fecb22b4ae364b28aedd8a30ee4'
FAMILY_SHA='33eb919640f3823c1035a62b0be44cce8aeed600bab8a1ef05e50a10730d3257'
RANK_FAMILY='new_rank30_bound500'
MEAN_FAMILY='new_meanflip30_bound500'
PRIOR_ANALYSIS_SHA='9ece477e12e30db25e4e04265e8042ed2ebd822caf67e666dc73bfea20b3eb32'
TIMING={61:(3000,6,27,54),62:(6000,13,48,96),63:(100,0,9,18),64:(100,0,9,18),65:(100,0,9,18)}


def frozen_inputs():
    manifest=BASE/'inputs_manifest.json'
    if binding(manifest)['sha256']!=MANIFEST_SHA:raise ValueError('Frozen manifest changed')
    if binding(BASE/'wave_at_family_recipe.json')['sha256']!=FAMILY_SHA:raise ValueError('Family definition changed')
    entries=json.loads(manifest.read_text(encoding='utf-8'))['entries']
    if len(entries)!=15:raise ValueError('Require15 frozen inputs')
    receipts,literals,refs,recipes={},{},[],{}
    seen=set()
    for ref in entries:
        path=(ROOT/ref['path']).resolve()
        if type(ref.get('round')) is not int or ref['round'] not in ROUNDS or path.parent!=(BASE/'inputs').resolve():raise ValueError('Owned frozen R61-R65 direct inputs only')
        if path in seen:raise ValueError('Duplicate frozen input identity')
        seen.add(path)
        actual=binding(path)
        if any(actual[k]!=ref[k] for k in ('sha256','bytes')):raise ValueError('Frozen input drift')
        refs.append(actual|dict(round=ref['round']))
        if path.suffix=='.json':
            if ref['round'] in receipts:raise ValueError('Duplicate receipt round')
            text=path.read_text(encoding='utf-8');receipts[ref['round']]=parse_source(text);literals[ref['round']]=parse_source(text,True)
        elif path.suffix=='.py':recipes[ref['round']]=path.read_text(encoding='utf-8')
        elif path.suffix!='.tsv':raise ValueError('Unexpected input suffix')
    if set(receipts)!=set(ROUNDS) or set(recipes)!=set(ROUNDS) or any(sum(r['round']==n for r in refs)!=3 for n in ROUNDS):raise ValueError('Missing current frozen receipt/TSV/recipe provenance')
    return receipts,literals,refs,recipes


def declared_context(number,payload,arm,saved=None):
    if type(number) is not int or number not in TIMING:raise ValueError('Explicit current round required')
    distance,coverage,slot,ack=TIMING[number]
    expected=dict(distance_m=distance,coverage_class=coverage,slot_time_us=slot,ack_timeout_us=ack)
    knobs=arm.get('candidate_knobs')
    for declaration in (payload,arm,knobs):
        if not isinstance(declaration,dict):raise ValueError('Three shared timing declaration objects required')
        for key,value in expected.items():
            if type(declaration.get(key)) is not int or declaration[key]!=value:raise ValueError('Shared typed distance/class/slot/ACK declaration differs')
    states=[knobs.get(side+'_state') for side in ('ap','cpe')]
    if any(not isinstance(x,dict) for x in states):raise ValueError('Endpoint state objects required')
    for state in states:
        for key,value in expected.items():
            if key in state and (type(state[key]) is not int or state[key]!=value):raise ValueError('Endpoint timing conflicts')
        if 'distance_meters' in state and (type(state['distance_meters']) is not int or state['distance_meters']!=distance):raise ValueError('Endpoint distance conflicts')
    if saved is not None:
        if (saved['coverage_class'],saved['distance_meters'])!=(coverage,distance):raise ValueError('Normalized declaration differs')
        evidence=saved['certified_wds_evidence']
        if evidence.get('slot_time_us')!=slot or evidence.get('ack_timeout_us')!=ack or evidence.get('slot_ack_source')!='SHARED_PAYLOAD_TREATMENT_KNOBS':raise ValueError('Normalizer timing provenance differs')
    return dict(**expected,provenance='EXPLICIT_SHARED_PAYLOAD_TREATMENT_KNOBS',slot_ack_provenance='SHARED_PAYLOAD_TREATMENT_KNOBS',
        physical_distance_verified=False,effective_runtime_application_verified=False,
        endpoint_states_originally_omit_timing=all(not any(k in state for k in (*expected,'distance_meters')) for state in states))


def profile_claims(contrasts):
    claims=[]
    for row in contrasts:
        number=int(row['scope'][1:]);metric=row['metric']
        claimed={62:5,63:9,64:5,65:7}.get(number) if metric==METRICS[0] else (15 if number==63 and metric==METRICS[1] else 16)
        claims.append(dict(round_id=row['scope'],metric=metric,claimed_favorable=claimed,actual_favorable=row['favorable_blocks'],equal=row['equal_blocks'],
            matches=None if claimed is None else claimed==row['favorable_blocks'],rank_p=row['exact_rank']['p_value'],sign_p=row['exact_sign']['p_value'],
            mean_flip_p=row['exact_sign_flips']['mean']['p_value'],rank_holm500=row['family_adjusted_p'][RANK_FAMILY]))
    return claims


def numerical_claims(descriptions,utilities):
    gp={61:('104.548828125','103.2314453125'),62:('95.08203125','94.294921875'),63:('104.9736328125','105.02734375'),64:('106.5322265625','105.8955078125'),65:('105.2451171875','104.05078125')}
    display={61:'-1.260065',62:'-0.827821',63:'0.051166',64:'-0.597677',65:'-1.134814'}
    claims=[]
    for number in ROUNDS:
        arms=[a for a in descriptions if a['round_id']==f'R{number}']
        for arm,literal in zip(arms,gp[number]):
            actual=Fraction(str(arm['summary']['goodput_mbps']));claimed=Fraction(literal)
            claims.append(dict(round_id=f'R{number}',iteration=arm['iteration'],metric='goodput_mbps',claimed_literal=literal,actual=float(actual),exact_difference=str(actual-claimed),matches=actual==claimed))
        u=next(u for u in utilities if u['round_id']==f'R{number}');actual=-Fraction(u['loss_percent_exact']);claimed=Fraction(display[number])
        claims.append(dict(round_id=f'R{number}',metric='signed_GP_change_percent',claimed_display_literal=display[number],actual=float(actual),actual_exact=str(actual),difference_from_display=str(actual-claimed),
            display_precision=6,rounded_matches=format(float(actual),'.6f')==format(float(claimed),'.6f'),claim_is_rounded_not_exact_source=True))
    return claims


def stated_latency_displays(descriptions):
    values={61:(('27.7365','46.2777','51.0350'),('6.9425','17.7264','27.8940')),
        62:(('27.2965','47.3927','58.2518'),('6.2745','14.2683','23.7384')),
        63:(('12.0400','54.3759','64.4340'),('7.1230','26.1690','33.7415')),
        64:(('19.5050','37.3292','52.7258'),('7.6600','19.9715','23.0616')),
        65:(('24.3945','45.4724','51.4304'),('7.3315','19.2464','29.0071'))}
    claims=[]
    for number in ROUNDS:
        arms=[r for r in descriptions if r['round_id']==f'R{number}']
        for arm,literals in zip(arms,values[number]):
            for metric,literal in zip(('p50_ms','p95_ms','p99_ms'),literals):
                actual=arm['summary'][metric]
                claims.append(dict(round_id=f'R{number}',iteration=arm['iteration'],metric=metric,
                    claimed_display=literal,actual=actual,canonical_python_4f=format(actual,'.4f'),
                    rounded_matches=format(actual,'.4f')==literal,
                    rounding_discrepancy_not_silently_repaired=True))
    return claims


def recipe_distance_calls(text):
    """Read AST only; no recipe import or execution and no inferred RF action."""
    calls=[]
    for node in ast.walk(ast.parse(text)):
        if not isinstance(node,ast.Call):continue
        name=node.func.id if isinstance(node.func,ast.Name) else getattr(node.func,'attr',None)
        if name!='apply_r33_state_with_distance':continue
        for kw in node.keywords:
            if kw.arg=='distance_m':
                value=kw.value.value if isinstance(kw.value,ast.Constant) and type(kw.value.value) is int else None
                calls.append(dict(line=node.lineno,declared_distance_m_literal=value,
                    source_text_only_not_execution_or_readback=True))
    return calls


def profile_conditions(contrasts,utilities):
    results=[]
    for number in ROUNDS:
        rid=f'R{number}';group=[c for c in contrasts if c['scope']==rid and c['metric'] in METRICS[1:]]
        utility=next(u for u in utilities if u['round_id']==rid)
        unanimity=all(c['favorable_blocks']==16 for c in group)
        stats=all(c['family_adjusted_p'][RANK_FAMILY]<=.05 and (c['HL_estimate']<0 if c['direction']=='lower' else c['HL_estimate']>0) for c in group)
        results.append(dict(round_id=rid,strict_observed_GP_loss_below2=Fraction(utility['loss_percent_exact'])<2,all_five_16of16=unanimity,
            five_direct_rank_HL_Holm500=stats,failed_unanimity_metrics=[c['metric'] for c in group if c['favorable_blocks']!=16],
            requested_strict_claim_necessary_conditions_met=unanimity and stats and Fraction(utility['loss_percent_exact'])<2,
            status='NECESSARY_OBSERVED_CONDITIONS_ONLY_NOT_AU_PROMOTION',spec_R63_qualification_conflict_confirmed=number==63 and not unanimity))
    return results


def historical_comparisons(records):
    def declared(record,key):
        # Typed-asdict omits extra top-level fields; use only saved provenance.
        # A present None remains unknown. Never derive timing from a class.
        if key in record:return record[key]
        nested=record.get('certified_wds_evidence')
        return nested.get(key) if isinstance(nested,dict) else None
    comparisons=[]
    for old,new in ((52,61),(53,62),(57,63),(55,64),(60,65)):
        a=next(r for r in records if r['round_id']==f'R{old}' and '_iter1_' in r['iteration'])
        b=next(r for r in records if r['round_id']==f'R{new}' and '_iter1_' in r['iteration'])
        comparisons.append(dict(control_round=f'R{old}',target_round=f'R{new}',full_policy_changed_coordinates=changed_coordinates(json.loads(a['policy_key']),json.loads(b['policy_key'])),
            recorded_contexts=[{k:declared(r,k) for k in ('workload_regime','active_flow_count','distance_meters','coverage_class','slot_time_us','ack_timeout_us')} for r in (a,b)],
            observed_metrics=[{k:r[k] for k in ('goodput_mbps','ul_goodput_mbps','p95_ms','p99_ms','jain_fairness')} for r in (a,b)],
            paired_crossround_p_value=None,causal_acceptance=False,interpretation='DESCRIPTIVE_DIFFERENT_ROUND_PACKAGES_NO_CAUSAL_POOL_OR_PHYSICAL_RANGE_PROOF'))
    return comparisons


def pair_rows(rows,control,target,metric):
    """Explicit R61..R65 validator; no global edits or relabeled old IDs."""
    if not isinstance(rows,list) or not rows:raise ValueError('Explicit crossed rows required')
    seen=set();rounds=set();groups=defaultdict(list)
    for row in rows:
        if row.get('round_id') not in {f'R{n}' for n in ROUNDS}:raise ValueError('Owned frozen R61..R65 only')
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

def build_analysis():
    from orchestration.autoresearch.fmx_live_dataset import load_all65_measurements,load_all65_block_observations
    names=('fmx_r57_to_r60_retry64_goodput_parity_audit','fmx_r43_to_r47_dyadic_zero_loss_audit','fmx_r48_to_r56_distance_goodput_dyadic_audit',
        'fmx_r33_to_r42_exact_holm500_audit','fmx_r27_to_r32_certified_wds_audit','fmx_r22_to_r26_crossover_audit',
        'fmx_r16_to_r21_real_crossover_audit','fmx_r15_and_crossover_statistical_audit','fmx_r10_to_r14_causal_and_power_analysis')
    dependencies=[Path(__file__),ROOT/'orchestration/autoresearch/fmx_live_dataset.py']+[ROOT/f'analysis/statistics/{n}.py' for n in names]
    dep_refs=[binding(p) for p in dependencies]
    receipts,literals,refs,recipes=frozen_inputs();typed,_=load_all65_measurements();blocks=load_all65_block_observations()
    records=[record_dict(r) for r in typed];by_id={(r['round_id'],r['iteration']):r for r in records}
    new=[b for b in blocks['crossed'] if int(b['round_id'][1:]) in ROUNDS]
    counts=dict(records=len(records),new_arms=sum(len(x['iterations']) for x in receipts.values()),crossed_rows=len(blocks['crossed']),
        new_crossed_rows=len(new),matched_ids=len({(b['round_id'],b['block_index']) for b in blocks['crossed']}),
        new_matched_ids=len({(b['round_id'],b['block_index']) for b in new}),sequential_R17=len(blocks['sequential']))
    if counts!=dict(records=230,new_arms=10,crossed_rows=1276,new_crossed_rows=160,matched_ids=550,new_matched_ids=80,sequential_R17=16):raise ValueError('Actual230/1276/550corpus required')
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
            audit['declared_timing_context']=declared_context(number,receipts[number],arm,saved)
            audit['recipe_distance_calls']=recipe_distance_calls(recipes[number])
            audit['recipe_distance_application_call_present']=bool(audit['recipe_distance_calls'])
            descriptions.append(audit)
        a,b=(by_id[(f'R{number}',k)] for k in (control,target));utility=observed_utility(a['goodput_mbps'],b['goodput_mbps'])
        loss=Fraction(utility['loss_percent_exact'])
        utilities.append(dict(round_id=f'R{number}',**utility,
            preserved_GP_percent=float(100-loss),preserved_GP_percent_exact=str(100-loss),
            control_retry_exact=str(Fraction(a['mac_tx_retries'],a['mac_tx_packets'])),target_retry_exact=str(Fraction(b['mac_tx_retries'],b['mac_tx_packets'])),
            target_retry_lower=Fraction(b['mac_tx_retries'],b['mac_tx_packets'])<Fraction(a['mac_tx_retries'],a['mac_tx_packets']),
            observed_GP_block_wins=next(c['favorable_blocks'] for c in contrasts if c['scope']==f'R{number}' and c['metric']=='goodput_rx_mbps'),
            statistical_equivalence_or_noninferiority=False))
    if len(contrasts)!=30:raise ValueError('Complete30 primary contrasts required')
    priorpath=ROOT/'artifacts/autoresearch/waves_ao_to_ar_20261024/wave_ap_retry64_goodput_parity_analysis.json'
    if binding(priorpath)['sha256']!=PRIOR_ANALYSIS_SHA:raise ValueError('Prior accepted AP artifact changed')
    prior=json.loads(priorpath.read_text(encoding='utf-8'))['families']['complete_known_rank855_bound855']['known_hypotheses']
    if len(prior)!=855:raise ValueError('Prior accepted855required unchanged')
    families={RANK_FAMILY:padded_family(contrasts,500,RANK_FAMILY),
        'complete_known_rank885_bound885':padded_family([dict(source_hypothesis_id=k,exact_rank=dict(p_value=p)) for k,p in prior.items()]+contrasts,885,'complete_known_rank885_bound885')}
    members=[dict(source_hypothesis_id='MEANFLIP:'+r['source_hypothesis_id'],exact_rank=dict(p_value=r['exact_sign_flips']['mean']['p_value'])) for r in contrasts]
    families[MEAN_FAMILY]=padded_family(members,500,MEAN_FAMILY)|dict(statistic='SECONDARY_INTEGER_EXACT_MEAN_FLIP_NOT_RANK')
    for row in contrasts:
        row['family_adjusted_p']={k:v['adjusted_p'][row['source_hypothesis_id']] for k,v in families.items() if row['source_hypothesis_id'] in v['adjusted_p']}
        row['mean_flip_holm500_adjusted_p']=families[MEAN_FAMILY]['adjusted_p']['MEANFLIP:'+row['source_hypothesis_id']]
    inputs={k:binding(BASE/v) for k,v in dict(records='normalized_r1_to_r65_measurements_20261024.json',blocks='normalized_r16_to_r65_block_observations_20261024.json',manifest='inputs_manifest.json').items()}
    projection=[dict(source_hypothesis_id=r['source_hypothesis_id'],regime=r['regime'],target_policy_id=r['target_policy_id'],control_policy_id=r['control_policy_id'],
        round_ids=[r['scope']],paired_unit_ids=r['paired_unit_ids'],metric=r['metric'],direction=r['direction'],effect_hl=r['HL_estimate'],
        p_exact_rank=r['exact_rank']['p_value'],holm500_adjusted_p=r['family_adjusted_p'][RANK_FAMILY],family500_key=RANK_FAMILY,
        comparability_status='WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON',statistic='PRIMARY_EXACT_SIGNED_RANK_NOT_MEAN_FLIP') for r in contrasts]
    if [binding(p) for p in dependencies]!=dep_refs:raise ValueError('Dependency changed during calculation')
    return dict(schema_version=1,status='OFFLINE_STRICT_DISTANCE_FLOW_AUDIT_PENDING_INDEPENDENT_ACCEPTANCE',counts=counts,
        software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),sources=refs,source_inputs=inputs,numerical_dependencies=dep_refs,
        family_plan=binding(BASE/'wave_at_family_recipe.json'),prespecified_contract=binding(BASE/'prespecified_contract.json'),prior_unchanged_analysis=binding(priorpath),
        contrasts=contrasts,families=families,source_claim_audits=descriptions,observed_utility=utilities,
        requested_win_claims=profile_claims(contrasts),numerical_source_claims=numerical_claims(descriptions,utilities),
        stated_latency_display_claims=stated_latency_displays(descriptions),design_diagnostics=designs,
        strict_source_profile_conditions=profile_conditions(contrasts,utilities),historical_descriptive_comparisons=historical_comparisons(records),
        catalog_scope=dict(primary_new_known=30,primary_prior_known=855,complete_primary_known=885,complete_primary_Holm500='INAPPLICABLE_KNOWN885_EXCEEDS500',mean_flip_family_separate=True,not_all_project_tests=True),
        promotion_evidence=dict(source_inputs={k+'_sha256':v['sha256'] for k,v in inputs.items()},contrasts=projection,
            families={k:v for k,v in families.items() if k!=MEAN_FAMILY},evidence_only_not_promotion=True),
        automatic_execution_allowed=False,physical_or_causal_acceptance=False,
        limits=['80actual matched block IDs, not1600independent physical experiments. Conditional symmetric/sign-exchangeable block assumptions not proven.',
            'Explicitdistance100/3000/6000,class0/6/13 and sharedslot/ACK are saved declarations, not verified recipe application, geographic separation or effective RF authority.',
            'Rank/sign/meanflip are distinct tests;60marginal95/99.9sets are not simultaneous885-test intervals.',
            'Observed mean GP and favorable block counts do not prove equivalence/noninferiority; all adverse block outcomes remain.',
            'Fullcarryover alias retained; restricted point estimates assume no differential carryover; no causalperiod p-values.',
            'No target/network/recipe/process operations; only owned frozen new files and accepted prior offline data/source.'])

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=BASE/'wave_at_strict_distance_and_flow_analysis.json')
    path=parser.parse_args().output.resolve()
    if path.parent!=BASE.resolve() or not path.name.startswith('wave_at_') or path.suffix!='.json':raise ValueError('Owned exclusive AT output required')
    if path.exists():raise FileExistsError(path)
    result=build_analysis()
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=result['status'],contrasts=len(result['contrasts']),arms=len(result['source_claim_audits']))))

if __name__=='__main__':main()
