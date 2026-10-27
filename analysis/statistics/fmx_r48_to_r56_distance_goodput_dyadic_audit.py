"""Frozen R48..R56 block audit, strictly offline and nonactuating.

Rank, sign and mean sign-flips are different conditional tests. The externally
reviewed AH numerical engine is reused, not copied or silently modified.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from dataclasses import asdict, is_dataclass
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy

from analysis.statistics.fmx_r43_to_r47_dyadic_zero_loss_audit import (
    dyadic_mean_audit, enumerate_fraction_flips, exact_sign_flips, literal_metric)
from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import (
    multilevel_design_diagnostics, schedule_agreement)
from analysis.statistics.fmx_r22_to_r26_crossover_audit import METRICS, _metric, _quality
from analysis.statistics.fmx_r27_to_r32_certified_wds_audit import binding, literal_mean_audit, padded_family
from analysis.statistics.fmx_r33_to_r42_exact_holm500_audit import exact_effect, parse_source

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/autoresearch/waves_ak_to_an_20261024'
ROUNDS=tuple(range(48,57))
MANIFEST_SHA='88c7b54b781e53b9747d704ea75a880f85984aa4a335fe36c06f8042bb5c9bef'
FAMILY_SHA='256b31a78331b4a30f07c678a20a795855dff6192a2e506b057c5c0c76dc533e'
RANK_FAMILY='new_rank54_bound500'
MEAN_FAMILY='new_meanflip54_bound500'


def pair_rows(rows,control,target,metric):
    """AH's two-period contract with this campaign's explicit round boundary."""
    if not isinstance(rows,list) or not rows:raise ValueError('Explicit crossed rows required')
    seen=set();rounds=set();groups=defaultdict(list)
    for row in rows:
        if row.get('round_id') not in {f'R{n}' for n in ROUNDS}:raise ValueError('Owned frozen R48..R56 only')
        rounds.add(row['round_id'])
        if any(type(row.get(k)) is not int or row[k]<0 for k in ('block_index','crossover_step')):raise ValueError('Genuine nonnegative integer block/step IDs required')
        if not isinstance(row.get('treatment_id'),str) or not row['treatment_id']:raise ValueError('Explicit treatment ID required')
        identity=(row['round_id'],row['block_index'],row['crossover_step'])
        if identity in seen:raise ValueError('Duplicate source identity')
        seen.add(identity);groups[row['block_index']].append(row)
    if len(rounds)!=1:raise ValueError('No mixed-round inference or pooling')
    pairs=[]
    for block,group in sorted(groups.items()):
        a=[r for r in group if r['treatment_id']==control];b=[r for r in group if r['treatment_id']==target]
        if len(group)!=2 or len(a)!=1 or len(b)!=1:raise ValueError('Exactlyone control+target per genuine block required')
        if {r['crossover_step'] for r in group}!={0,1}:raise ValueError('Exactlytwo source periods0/1 required')
        x,y=_metric(a[0],metric),_metric(b[0],metric)
        if x is None or y is None:raise ValueError('Missing block outcome cannot disappear')
        pairs.append(dict(round_id=a[0]['round_id'],block_index=block,control_mean=x,treatment_mean=y,
            difference=y-x,control_step=a[0]['crossover_step'],target_step=b[0]['crossover_step'],
            sequence='AB' if a[0]['crossover_step']==0 else 'BA'))
    return pairs


def period_adjusted_estimation(rows,control,target,metric):
    """Explicit NO_DIFFERENTIAL_CARRYOVER restriction, never a full causal fit."""
    pairs=pair_rows(rows,control,target,metric)
    ab=[p for p in pairs if p['sequence']=='AB'];ba=[p for p in pairs if p['sequence']=='BA']
    if not ab or not ba:return dict(status='NOT_IDENTIFIED_SINGLE_SEQUENCE',assumption='No causal claim')
    def mean(group):return sum((Fraction(str(p['treatment_mean']))-Fraction(str(p['control_mean'])) for p in group),Fraction())/len(group)
    direct=(mean(ab)+mean(ba))/2;period=(mean(ab)-mean(ba))/2
    blocks=sorted({r['block_index'] for r in rows});matrix=[];outcomes=[]
    for r in rows:
        matrix.append([1]+[int(r['block_index']==b) for b in blocks[1:]]+[r['crossover_step'],int(r['treatment_id']==target)])
        outcomes.append(_metric(r,metric))
    x=np.asarray(matrix,dtype=float);fit=np.linalg.lstsq(x,np.asarray(outcomes,dtype=float),rcond=None)[0]
    rank=int(np.linalg.matrix_rank(x))
    if rank!=x.shape[1]:raise ValueError('Named restricted submodel must be full rank')
    if not all(math.isclose(float(a),float(b),abs_tol=1e-9,rel_tol=1e-11) for a,b in ((direct,fit[-1]),(period,fit[-2]))):raise ValueError('Exact closed-form and least-squares coefficients disagree')
    return dict(status='IDENTIFIED_RESTRICTED_MODEL_NOT_CAUSAL_CERTIFICATION',model='BLOCK_FIXED_EFFECTS+PERIOD+CURRENT_TREATMENT_NO_DIFFERENTIAL_CARRYOVER',
        assumptions=['No differential carryover or unmodeled block-by-period response','Recorded order is not proof of randomization','Not separated current/lag causal effects'],
        AB_blocks=len(ab),BA_blocks=len(ba),columns=x.shape[1],rank=rank,direct_estimate=float(direct),period_estimate=float(period),
        direct_exact_fraction=str(direct),period_exact_fraction=str(period),numeric_direct_estimate=float(fit[-1]),numeric_period_estimate=float(fit[-2]),
        no_period_adjusted_inference_p_value='Raw sign flips do not automatically test direct treatment effects under period nuisance')


def frozen_inputs():
    manifest=BASE/'inputs_manifest.json'
    if binding(manifest)['sha256']!=MANIFEST_SHA:raise ValueError('Frozen manifest changed')
    if binding(BASE/'wave_al_family_recipe.json')['sha256']!=FAMILY_SHA:raise ValueError('Prespecified family changed')
    entries=json.loads(manifest.read_text(encoding='utf-8'))['entries']
    if len(entries)!=27:raise ValueError('Require27 owned frozen inputs')
    receipts,literals,refs={},{},[]
    for ref in entries:
        path=(ROOT/ref['path']).resolve()
        if ref['round'] not in ROUNDS or not path.is_relative_to((BASE/'inputs').resolve()):raise ValueError('Owned frozen inputs only')
        actual=binding(path)
        if any(actual[k]!=ref[k] for k in ('sha256','bytes')):raise ValueError('Frozen input drift')
        refs.append(actual|dict(round=ref['round']))
        if path.suffix=='.json':
            text=path.read_text(encoding='utf-8');receipts[ref['round']]=parse_source(text);literals[ref['round']]=parse_source(text,True)
    if set(receipts)!=set(ROUNDS):raise ValueError('Missing frozen current round')
    return receipts,literals,refs


def source_arm_audit(number,arm,literal,saved):
    """Retain adverse/missing health, exact counters and source claims, not filter."""
    blocks=arm['repetition_blocks'];obs=arm['observation']
    if len(blocks)!=16:raise ValueError('Exactly16 actual blocks per arm required')
    sent=sum(b['pings_sent'] for b in blocks);received=sum(b['pings_rcvd'] for b in blocks)
    packets=arm['mac_tx_packets_delta'];retries=arm['mac_tx_retries_delta']
    if type(packets) is not int or packets<=0 or type(retries) is not int or retries<0:raise ValueError('Positive typed MAC denominator required')
    health=[dict(block_index=b['block_index'],packet_loss_pct=b.get('observation',{}).get('packet_loss_pct'),
        station_drops=b.get('observation',{}).get('station_drops'),restoration_verified=b.get('observation',{}).get('restoration_verified')) for b in blocks]
    return dict(round_id=f'R{number}',iteration=arm['commit'],policy_id=saved['policy_key'],
        literal_mean_audit=literal_mean_audit(literal),dyadic_audit=dyadic_mean_audit(arm,literal),
        normalizer_dyadic_audit=saved.get('dyadic_mean_audit'),attempted_pings=sent,received_pings=received,
        complete_160_pings=(sent==received==160 and all(b['pings_sent']==b['pings_rcvd']==len(b['rtts_ms']) for b in blocks)),
        saved_loss_pct=obs['packet_loss_pct'],saved_station_drops=obs['station_drops'],
        saved_restoration_verified=obs['restoration_verified'],block_health=health,
        independent_device_health_verified=False,
        chronology_matches=arm['raw_rtts_ms']==[v for b in blocks for v in b['rtts_ms']],
        mac_tx_packets=packets,mac_tx_retries=retries,retry_events_per_packet=retries/packets,
        retry_fraction_exact=str(Fraction(retries,packets)),
        mac_sums_match=all(sum(b[k] for b in blocks)==arm[k] for k in ('mac_tx_packets_delta','mac_tx_retries_delta')),
        reported_mac_retry_rate=arm.get('mac_retry_rate'),
        context=observed_context(saved),summary={k:saved[k] for k in ('goodput_mbps','dl_goodput_mbps','ul_goodput_mbps','p50_ms','p95_ms','p99_ms','jain_fairness')},
        evaluation=arm['evaluation'])


def observed_context(record):
    """Comparison boundary excludes policy coordinates, includes RF timing/context."""
    keys=('workload_regime','active_flow_count','bidirectional','coverage_class','distance_meters',
          'encryption_mode','associated_cpes')
    return {k:record.get(k) for k in keys}


def record_dict(record):
    value=asdict(record) if is_dataclass(record) else dict(record)
    if hasattr(record,'policy_key'):value['policy_key']=record.policy_key
    return value


def observed_utility(control,target):
    a,b=Fraction(str(control)),Fraction(str(target))
    if a<=0 or b<0:raise ValueError('Positive control and nonnegative target required')
    loss=(a-b)*100/a
    return dict(control_goodput_mbps=float(a),target_goodput_mbps=float(b),loss_percent=float(loss),
        loss_percent_exact=str(loss),passes_strict_less_than_2_percent=loss<2,
        passes_observed_at_most_2_percent=loss<=2,noninferiority_test=False)


def descriptive_pareto(points):
    """Observed GP/UL/Jain higher +3RTT lower; never causal cross-round inference."""
    groups={}
    for point in points:
        context=json.dumps(point['context'],sort_keys=True,separators=(',',':'))
        groups.setdefault(context,[]).append(point)
    out=[]
    objectives=('goodput_mbps','ul_goodput_mbps','jain_fairness','p50_ms','p95_ms','p99_ms')
    for context,items in sorted(groups.items()):
        def dominates(a,b):
            signs=(1,1,1,-1,-1,-1)
            deltas=[s*(a['summary'][k]-b['summary'][k]) for s,k in zip(signs,objectives)]
            return all(v>=0 for v in deltas) and any(v>0 for v in deltas)
        nodes=[]
        for item in items:
            blockers=[x['id'] for x in items if x['id']!=item['id'] and dominates(x,item)]
            nodes.append(item|dict(nondominated=not blockers,dominated_by=blockers))
        out.append(dict(context=json.loads(context),points=nodes))
    return dict(status='DESCRIPTIVE_SAME_DECLARED_CONTEXT_ONLY',groups=out,paired_p_value=None,
        limitations=['Different rounds/controls/policies are not randomized shared experimental units.',
            'No causal package or individual-knob superiority, physical distance or sector accuracy is inferred.',
            'Nondominance is an observed summary tradeoff, not safety, significance or promotion.'])


def claimed_win_profiles(contrasts):
    five=METRICS[1:]
    claims={48:{m:16 for m in five},49:{m:16 for m in five},50:{m:16 for m in five},
        51:{'p50_rtt_ms':16,'p95_rtt_ms':15,'ul_goodput_mbps':16,'jain_fairness':16},
        52:{m:(15 if m=='p99_rtt_ms' else 16) for m in five},53:{m:16 for m in five},
        54:{'p50_rtt_ms':16,'p95_rtt_ms':15,'jain_fairness':15},
        55:{m:(15 if m in ('p95_rtt_ms','p99_rtt_ms') else 16) for m in five},
        56:{m:15 if m=='p99_rtt_ms' else 14 if m=='ul_goodput_mbps' else 16 for m in five}}
    return [dict(round_id=r['scope'],metric=r['metric'],claimed_favorable=claims[int(r['scope'][1:])].get(r['metric']),
        actual_favorable=r['favorable_blocks'],equal=r['equal_blocks'],
        matches=(r['favorable_blocks']==claims[int(r['scope'][1:])][r['metric']]) if r['metric'] in claims[int(r['scope'][1:])] else None,
        rank_p=r['exact_rank']['p_value'],sign_p=r['exact_sign']['p_value'],mean_flip_p=r['exact_sign_flips']['mean']['p_value'],
        rank_holm500=r['family_adjusted_p'][RANK_FAMILY]) for r in contrasts if r['metric'] in five]


def numeric_spec_claims(descriptions):
    """Literal full-precision GP values in spec; do not widen epsilon to pass."""
    declared={48:('104.072265625','90.3056640625'),49:('94.158203125','81.8125'),
        50:('109.046875','107.6826171875'),51:(None,'102.6669921875'),
        52:('103.3564453125','97.826171875'),53:('94.9599609375','89.90625'),
        54:(None,'103.513671875'),55:(None,'104.1044921875'),56:(None,'102.98828125')}
    out=[]
    for row in descriptions:
        number=int(row['round_id'][1:]);index=0 if '_iter0_' in row['iteration'] else 1
        claimed=declared[number][index]
        if claimed is None:continue
        actual=Fraction(str(row['summary']['goodput_mbps']));expected=Fraction(claimed)
        out.append(dict(round_id=row['round_id'],iteration=row['iteration'],metric='goodput_mbps',
            claimed_literal=claimed,actual=row['summary']['goodput_mbps'],exact_difference=str(actual-expected),
            matches=actual==expected,source_priority='FROZEN_RECEIPT_NOT_SPEC_NARRATIVE'))
    return out


def build_analysis():
    from orchestration.autoresearch.fmx_live_dataset import load_all56_measurements,load_all56_block_observations
    dependencies=[Path(__file__),ROOT/'orchestration/autoresearch/fmx_live_dataset.py']+[
        ROOT/f'analysis/statistics/{name}.py' for name in ('fmx_r43_to_r47_dyadic_zero_loss_audit',
            'fmx_r33_to_r42_exact_holm500_audit','fmx_r27_to_r32_certified_wds_audit',
            'fmx_r22_to_r26_crossover_audit','fmx_r16_to_r21_real_crossover_audit',
            'fmx_r15_and_crossover_statistical_audit','fmx_r10_to_r14_causal_and_power_analysis')]
    dep_refs=[binding(p) for p in dependencies]
    receipts,literals,refs=frozen_inputs();raw_records,_=load_all56_measurements();blocks=load_all56_block_observations()
    records=[record_dict(r) for r in raw_records]
    by_id={(r['round_id'],r['iteration']):r for r in records}
    new=[b for b in blocks['crossed'] if int(b['round_id'][1:]) in ROUNDS]
    counts=dict(records=len(records),new_arms=sum(len(x['iterations']) for x in receipts.values()),
        crossed_rows=len(blocks['crossed']),new_crossed_rows=len(new),matched_ids=len({(b['round_id'],b['block_index']) for b in blocks['crossed']}),
        new_matched_ids=len({(b['round_id'],b['block_index']) for b in new}),sequential_R17=len(blocks['sequential']))
    if counts!=dict(records=212,new_arms=18,crossed_rows=988,new_crossed_rows=288,matched_ids=406,new_matched_ids=144,sequential_R17=16):raise ValueError('Actual212/988/406 corpus required')
    contrasts,descriptions,designs,utilities=[],[],[],[]
    for number in ROUNDS:
        arms=receipts[number]['iterations']
        if len(arms)!=2:raise ValueError('Exactly2 source arms required')
        control,target=[a['commit'] for a in arms];group=[b for b in new if b['round_id']==f'R{number}']
        if len(group)!=32:raise ValueError('Exactly32 source windows per round required')
        literal_by={(a['commit'],b['block_index']):b for a in literals[number]['iterations'] for b in a['repetition_blocks']}
        for metric in METRICS:
            pairs=pair_rows(group,control,target,metric)
            if len(pairs)!=16:raise ValueError('Exactly16 genuine source pairs required')
            d=[p['difference'] for p in pairs];effect=exact_effect(d);flips=exact_sign_flips(d)
            if any(flips[k]['p_value']!=effect['exact_'+k]['p_value'] for k in ('rank','sign')):raise ValueError('65536 enumeration disagrees with accepted DP')
            dd=[literal_metric(literal_by[(target,p['block_index'])],metric)-literal_metric(literal_by[(control,p['block_index'])],metric) for p in pairs]
            sensitivity=enumerate_fraction_flips(dd);saved=by_id[(f'R{number}',target)]
            contrasts.append(dict(source_hypothesis_id=json.dumps([f'R{number}',control,target,metric],separators=(',',':')),
                scope=f'R{number}',control=control,target=target,regime=saved['workload_regime'],
                control_policy_id=by_id[(f'R{number}',control)]['policy_key'],target_policy_id=saved['policy_key'],metric=metric,
                direction='lower' if metric in METRICS[1:4] else 'higher',paired_unit_ids=[dict(round_id=p['round_id'],block_index=p['block_index']) for p in pairs],pairs=pairs,
                favorable_blocks=sum(x<0 if metric in METRICS[1:4] else x>0 for x in d),equal_blocks=sum(x==0 for x in d),quality=_quality(group),
                exact_sign_flips=flips,source_decimal_sensitivity=dict(exact_flips=sensitivity,literal_differences=[str(v) for v in dd],
                    rank_p_changed=sensitivity['rank']['p_value']!=flips['rank']['p_value'],mean_p_changed=sensitivity['mean']['p_value']!=flips['mean']['p_value']),
                period_adjusted=period_adjusted_estimation(group,control,target,metric),**effect))
        design=multilevel_design_diagnostics(group)|dict(round_id=f'R{number}')
        design['schedule_agreement']=schedule_agreement(group,receipts[number]['crossover_schedule'],{'A':control,'B':target})
        design['interpretation']='Fullblock+period+current+lag alias retained; restricted point estimate is conditional on no differential carryover, not separated causal effect.'
        designs.append(design)
        for i,arm in enumerate(arms):descriptions.append(source_arm_audit(number,arm,literals[number]['iterations'][i],by_id[(f'R{number}',arm['commit'])]))
        a,b=(by_id[(f'R{number}',k)] for k in (control,target))
        utilities.append(dict(round_id=f'R{number}',**observed_utility(a['goodput_mbps'],b['goodput_mbps']),
            target_retry_lower=Fraction(b['mac_tx_retries'],b['mac_tx_packets'])<Fraction(a['mac_tx_retries'],a['mac_tx_packets']),
            control_retry_exact=str(Fraction(a['mac_tx_retries'],a['mac_tx_packets'])),target_retry_exact=str(Fraction(b['mac_tx_retries'],b['mac_tx_packets'])),
            context_equal=observed_context(a)==observed_context(b),physical_distance_verified=False))
    if len(contrasts)!=54:raise ValueError('Complete54 primary contrasts required')
    priorpath=ROOT/'artifacts/autoresearch/waves_ag_to_aj_20261024/wave_ah_dyadic_zero_loss_analysis.json'
    prior=json.loads(priorpath.read_text(encoding='utf-8'))['families']['complete_known_rank777_bound777']['known_hypotheses']
    if len(prior)!=777:raise ValueError('Prior accepted777 required unchanged')
    families={RANK_FAMILY:padded_family(contrasts,500,RANK_FAMILY),
        'complete_known_rank831_bound831':padded_family([dict(source_hypothesis_id=k,exact_rank=dict(p_value=p)) for k,p in prior.items()]+contrasts,831,'complete_known_rank831_bound831')}
    members=[dict(source_hypothesis_id='MEANFLIP:'+r['source_hypothesis_id'],exact_rank=dict(p_value=r['exact_sign_flips']['mean']['p_value'])) for r in contrasts]
    families[MEAN_FAMILY]=padded_family(members,500,MEAN_FAMILY)|dict(statistic='SECONDARY_EXACT_MEAN_FLIP_NOT_RANK')
    for r in contrasts:
        r['family_adjusted_p']={k:v['adjusted_p'][r['source_hypothesis_id']] for k,v in families.items() if r['source_hypothesis_id'] in v['adjusted_p']}
        r['mean_flip_holm500_adjusted_p']=families[MEAN_FAMILY]['adjusted_p']['MEANFLIP:'+r['source_hypothesis_id']]
    points=[]
    for number in (45,48,49,50,51,52,53,55,56):
        candidates=[r for r in records if r['round_id']==f'R{number}' and r['iteration'].startswith(f'r{number}_iter1_')]
        if len(candidates)!=1:raise ValueError('Unique requested descriptive target required')
        r=candidates[0];points.append(dict(id=r['round_id'],policy_id=r['policy_key'],context=observed_context(r),
            summary={k:r[k] for k in ('goodput_mbps','ul_goodput_mbps','jain_fairness','p50_ms','p95_ms','p99_ms')}))
    inputs={k:binding(BASE/v) for k,v in dict(records='normalized_r1_to_r56_measurements_20261024.json',blocks='normalized_r16_to_r56_block_observations_20261024.json',manifest='inputs_manifest.json').items()}
    projection=[dict(source_hypothesis_id=r['source_hypothesis_id'],regime=r['regime'],target_policy_id=r['target_policy_id'],control_policy_id=r['control_policy_id'],
        round_ids=[r['scope']],paired_unit_ids=r['paired_unit_ids'],metric=r['metric'],direction=r['direction'],effect_hl=r['HL_estimate'],p_exact_rank=r['exact_rank']['p_value'],
        holm500_adjusted_p=r['family_adjusted_p'][RANK_FAMILY],family500_key=RANK_FAMILY,
        comparability_status='WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON',statistic='PRIMARY_EXACT_SIGNED_RANK_NOT_MEAN_FLIP') for r in contrasts]
    if [binding(p) for p in dependencies]!=dep_refs:raise ValueError('Dependency changed during calculation')
    return dict(schema_version=1,status='OFFLINE_DISTANCE_GOODPUT_AUDIT_PENDING_INDEPENDENT_ACCEPTANCE',
        software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),counts=counts,
        sources=refs,source_inputs=inputs,numerical_dependencies=dep_refs,family_plan=binding(BASE/'wave_al_family_recipe.json'),prior_unchanged_analysis=binding(priorpath),
        contrasts=contrasts,families=families,source_claim_audits=descriptions,requested_win_claims=claimed_win_profiles(contrasts),
        numeric_spec_claims=numeric_spec_claims(descriptions),
        observed_utility=utilities,descriptive_pareto=descriptive_pareto(points),design_diagnostics=designs,
        catalog_scope=dict(primary_new_known=54,primary_prior_known=777,complete_primary_known=831,complete_primary_Holm500='INAPPLICABLE_KNOWN831_EXCEEDS500',mean_flip_family_separate=True,not_all_project_tests=True),
        promotion_evidence=dict(source_inputs={k+'_sha256':v['sha256'] for k,v in inputs.items()},contrasts=projection,
            families={k:v for k,v in families.items() if k!=MEAN_FAMILY},evidence_only_not_promotion=True),
        automatic_execution_allowed=False,physical_or_causal_acceptance=False,
        limits=['144 actual matched blocks, not2880 independent physical experiments. Conditional sign symmetry/exchangeability is assumed, not established by counterbalancing.',
            'Programmed coverage/timing3000/6000m does not prove geographic range. No RF authority or external-sector replication follows.',
            'Rank,sign andmean-flip are distinct conditional statistics; exact integer tails do not prove carryover absent.',
            'No matched-policy pooling or causal crossround package gain. Observed2% floor is not statistical noninferiority.',
            'Health/restoration are saved reports, not independent target readbacks. Missing health remains unknown.',
            'Only owned frozen inputs and accepted prior offline data/source; no network, target, recipe or bench-process operations.'])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=BASE/'wave_al_distance_goodput_dyadic_analysis.json')
    path=parser.parse_args().output.resolve()
    if path.parent!=BASE.resolve() or not path.name.startswith('wave_al_') or path.suffix!='.json':raise ValueError('Owned exclusive AL output required')
    if path.exists():raise FileExistsError(path)
    result=build_analysis()
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=result['status'],contrasts=len(result['contrasts']),source_windows=len(result['source_claim_audits']))))


if __name__=='__main__':main()
