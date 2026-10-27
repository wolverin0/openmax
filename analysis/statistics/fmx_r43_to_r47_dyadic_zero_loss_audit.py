"""Wholly offline exact16-block rank/sign/mean and restricted period audit.

No actuator, live discovery, network, target or recipe execution. All families
are fixed in the owned precomputation recipe before new outcome computation.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from decimal import Decimal
from fractions import Fraction
import hashlib,json,math,platform
from pathlib import Path
import numpy as np
import scipy
from analysis.statistics.fmx_r10_to_r14_causal_and_power_analysis import sample
from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import multilevel_design_diagnostics,schedule_agreement
from analysis.statistics.fmx_r22_to_r26_crossover_audit import METRICS,_metric,_quality
from analysis.statistics.fmx_r27_to_r32_certified_wds_audit import binding,literal_mean_audit,padded_family
from analysis.statistics.fmx_r33_to_r42_exact_holm500_audit import exact_effect,parse_source
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/autoresearch/waves_ag_to_aj_20261024'
ROUNDS=tuple(range(43,48))


def fraction_rank_weights(values):
    """Signed doubled midranks from exact absolute Fraction values; zeros0."""
    groups=defaultdict(list)
    for i,value in enumerate(values):
        if value:groups[abs(value)].append(i)
    result=[0]*len(values);position=1
    for value,indices in sorted(groups.items()):
        doubled=2*position+len(indices)-1
        for i in indices:result[i]=doubled if values[i]>0 else -doubled
        position+=len(indices)
    return result


def enumerate_fraction_flips(values):
    """Enumerate EVERY assigned sign; mean uses integer sums, no epsilon tail.

    The assignment space includes zero coefficients, so degeneracy is repeated
    exactly rather than being mistaken for extra independent information.
    """
    if not isinstance(values,(list,tuple)) or not 1<=len(values)<=20 or any(type(v) is not Fraction for v in values):raise ValueError('Explicit1..20 Fraction block differences required')
    n=len(values);denominator=math.lcm(*(v.denominator for v in values))
    mean=[v.numerator*(denominator//v.denominator) for v in values]
    rank=fraction_rank_weights(values);sign=[int(v>0)-int(v<0) for v in values]
    coefficients=(rank,sign,mean);observed=[abs(sum(w)) for w in coefficients]
    sums=[-sum(w) for w in coefficients];extreme=[int(abs(x)>=cutoff) for x,cutoff in zip(sums,observed)]
    previous=0;assignments=1<<n
    for number in range(1,assignments):
        gray=number^(number>>1);changed=gray^previous;bit=changed.bit_length()-1
        direction=2 if gray&changed else -2
        for k,w in enumerate(coefficients):
            sums[k]+=direction*w[bit]
            extreme[k]+=int(abs(sums[k])>=observed[k])
        previous=gray
    mean_observed=sum(values,Fraction(0))/n
    return dict(assignments=assignments,independent_units_assumed=n,
        rank=dict(extreme_assignments=extreme[0],p_value=extreme[0]/assignments,statistic='ABS_SIGNED_DOUBLED_MIDRANK_SUM'),
        sign=dict(extreme_assignments=extreme[1],p_value=extreme[1]/assignments,statistic='ABS_POSITIVE_MINUS_NEGATIVE_NONZERO_SIGN_COUNT'),
        mean=dict(extreme_assignments=extreme[2],p_value=extreme[2]/assignments,statistic='ABS_ARITHMETIC_MEAN_OF_SIGNED_DIFFERENCES',observed_exact_numerator=str(mean_observed.numerator),observed_exact_denominator=str(mean_observed.denominator),common_integer_denominator=str(denominator)),
        zero_differences=sum(not v for v in values),method='ALL_SIGN_ASSIGNMENTS_INTEGER_GRAY_CODE_EXACT_TAILS_NO_TOLERANCE',
        limits='Conditional symmetry/sign exchangeability of actual blocks required. Rank,sign andmean are distinct statistics on the same observations, not three independent experiments.')


def exact_sign_flips(differences):
    data=sample(differences,minimum=1)
    return enumerate_fraction_flips([Fraction.from_float(float(x)) for x in data])


def validate_rows(rows):
    if not isinstance(rows,list) or not rows:raise ValueError('Explicit crossed source rows required')
    seen=set();rounds=set()
    for r in rows:
        if r.get('round_id') not in {f'R{n}' for n in ROUNDS}:raise ValueError('Owned new frozen round required')
        rounds.add(r['round_id'])
        for key in ('block_index','crossover_step'):
            if type(r.get(key)) is not int or r[key]<0:raise ValueError('Genuine nonnegative integer block/step IDs required')
        identity=(r['round_id'],r['block_index'],r['crossover_step'])
        if identity in seen:raise ValueError('Duplicate source identity')
        seen.add(identity)
        if not isinstance(r.get('treatment_id'),str) or not r['treatment_id']:raise ValueError('Treatment identity required')
    if len(rounds)!=1:raise ValueError('No mixed-round inference or pooling')


def pair_rows(rows,control,target,metric):
    validate_rows(rows);groups=defaultdict(list)
    for r in rows:groups[r['block_index']].append(r)
    pairs=[]
    for block,group in sorted(groups.items()):
        a=[r for r in group if r['treatment_id']==control];b=[r for r in group if r['treatment_id']==target]
        if len(group)!=2 or len(a)!=1 or len(b)!=1:raise ValueError('Exactlyone source control+target per genuine block required')
        if {r['crossover_step'] for r in group}!={0,1}:raise ValueError('Exact two-period source steps0/1 required')
        x,y=_metric(a[0],metric),_metric(b[0],metric)
        if x is None or y is None:raise ValueError('Missing block outcome cannot silently disappear')
        pairs.append(dict(round_id=a[0]['round_id'],block_index=block,control_mean=x,treatment_mean=y,difference=y-x,
            control_step=a[0]['crossover_step'],target_step=b[0]['crossover_step'],sequence='AB' if a[0]['crossover_step']==0 else 'BA'))
    return pairs


def period_adjusted_estimation(rows,control,target,metric):
    """Named identifiable NO_DIFFERENTIAL_CARRYOVER submodel, not a full fit."""
    pairs=pair_rows(rows,control,target,metric)
    ab=[p for p in pairs if p['sequence']=='AB'];ba=[p for p in pairs if p['sequence']=='BA']
    if not ab or not ba:return dict(status='NOT_IDENTIFIED_SINGLE_SEQUENCE',assumption='No causal claim')
    mean=lambda group:sum((Fraction(str(p['treatment_mean']))-Fraction(str(p['control_mean'])) for p in group),Fraction(0))/len(group)
    direct=(mean(ab)+mean(ba))/2;period=(mean(ab)-mean(ba))/2
    blocks=sorted({r['block_index'] for r in rows});matrix=[];outcomes=[]
    for r in rows:
        matrix.append([1]+[int(r['block_index']==b) for b in blocks[1:]]+[r['crossover_step'],int(r['treatment_id']==target)])
        outcomes.append(_metric(r,metric))
    x=np.array(matrix,dtype=float);y=np.array(outcomes,dtype=float);fit=np.linalg.lstsq(x,y,rcond=None)[0];rank=int(np.linalg.matrix_rank(x))
    if rank!=x.shape[1]:raise ValueError('Named restricted submodel must be full rank')
    if not math.isclose(float(direct),float(fit[-1]),abs_tol=1e-9,rel_tol=1e-11) or not math.isclose(float(period),float(fit[-2]),abs_tol=1e-9,rel_tol=1e-11):raise ValueError('Closed-form exact source-decimal coefficients disagree with least squares')
    return dict(status='IDENTIFIED_RESTRICTED_MODEL_NOT_CAUSAL_CERTIFICATION',model='BLOCK_FIXED_EFFECTS+PERIOD+CURRENT_TREATMENT_NO_DIFFERENTIAL_CARRYOVER',assumptions=['No differential carryover or unmodeled block-by-period response','Recorded order is not proof of randomization','Coefficients are conditional estimands, not separated direct/lag causal effects'],AB_blocks=len(ab),BA_blocks=len(ba),columns=x.shape[1],rank=rank,
        direct_estimate=float(direct),period_estimate=float(period),direct_exact_fraction=str(direct),period_exact_fraction=str(period),numeric_direct_estimate=float(fit[-1]),numeric_period_estimate=float(fit[-2]),
        source_precision='Exact arithmetic on canonical source-number decimal values; float least-squares cross-check',
        no_period_adjusted_inference_p_value='Raw difference sign flips do not automatically test a direct effect with a nonzero period nuisance')


def frozen_inputs():
    entries=json.loads((BASE/'inputs_manifest.json').read_text(encoding='utf-8'))['entries']
    if len(entries)!=15:raise ValueError('Require15 owned frozen inputs')
    receipts,literals,refs={},{},[]
    for ref in entries:
        path=(ROOT/ref['path']).resolve()
        if ref['round'] not in ROUNDS or not path.is_relative_to((BASE/'inputs').resolve()):raise ValueError('Owned frozen input only')
        actual=binding(path)
        if any(actual[k]!=ref[k] for k in ('sha256','bytes')):raise ValueError('Frozen file changed')
        refs.append(actual|dict(round=ref['round']))
        if path.suffix=='.json':
            text=path.read_text(encoding='utf-8');receipts[ref['round']]=parse_source(text);literals[ref['round']]=parse_source(text,True)
    if set(receipts)!=set(ROUNDS):raise ValueError('Missing current frozen round')
    return receipts,literals,refs


def literal_metric(block,metric):
    key={'goodput_rx_mbps':'total_goodput_mbps','jain_fairness':'bidir_jain_fairness'}.get(metric,metric)
    return Fraction(block[key])


def dyadic_mean_audit(arm,literal):
    """Independent source-literal versus NumPy audit, no epsilon/rounding repair."""
    fields={};all_dyadic=True
    for name,reported,source in [('goodput_mbps',literal['observation']['goodput_rx_mbps'],'total_goodput_mbps'),('dl_goodput_mbps',literal['dl_goodput_mbps'],'dl_goodput_mbps'),('ul_goodput_mbps',literal['ul_goodput_mbps'],'ul_goodput_mbps'),('jain_fairness',literal['bidir_jain_fairness'],'bidir_jain_fairness')]:
        values=[Fraction(b[source]) for b in literal['repetition_blocks']];expected=Fraction(reported);mean=sum(values,Fraction(0))/len(values)
        floats=[float(b[source]) for b in arm['repetition_blocks']];given=float(reported);nmean=float(np.mean(np.array(floats,dtype=np.float64)))
        if not all(math.isfinite(v) and v>=0 for v in floats+[given,nmean]):raise ValueError('Nonnegative finite source mean required')
        normalize=lambda v:0. if v==0 else v
        ulp=abs(int(np.float64(normalize(given)).view(np.uint64))-int(np.float64(normalize(nmean)).view(np.uint64)))
        binary_delta=Fraction.from_float(given)-sum((Fraction.from_float(v) for v in floats),Fraction(0))/len(floats)
        dyadic=all(v.denominator&(v.denominator-1)==0 for v in [expected,*values]);all_dyadic &= dyadic
        fields[name]=dict(fraction_delta=str(expected-mean),numpy_float_delta=given-nmean,ulp_error=ulp,binary_rational_delta=str(binary_delta),source_decimal_inputs_dyadic=dyadic,all_source_values_binary64_representable=all(Fraction.from_float(float(v))==v for v in [expected,*values]))
    exact=all(v['fraction_delta']=='0' and v['numpy_float_delta']==0 and v['ulp_error']==0 for v in fields.values())
    return dict(status=('DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP' if all_dyadic else 'FLOAT_AND_RATIONAL_EXACT_ZERO_ULP_NON_DYADIC_INPUTS') if exact else 'NOT_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP',fields=fields,all_fraction_zero=all(v['fraction_delta']=='0' for v in fields.values()),all_numpy_float_zero=all(v['numpy_float_delta']==0 for v in fields.values()),all_zero_ulp=all(v['ulp_error']==0 for v in fields.values()),all_source_inputs_dyadic=bool(all_dyadic),physical_certification=False)


def source_audit(number,arm,literal,saved):
    blocks=arm['repetition_blocks'];q=dyadic_mean_audit(arm,literal)
    return dict(round_id=f'R{number}',iteration=arm['commit'],policy_id=saved.policy_key,
        literal_mean_audit=literal_mean_audit(literal),dyadic_audit=q,AG_dyadic_audit=saved.dyadic_mean_audit,
        attempted_pings=sum(b['pings_sent'] for b in blocks),received_pings=sum(b['pings_rcvd'] for b in blocks),saved_loss_pct=arm['observation']['packet_loss_pct'],
        chronology_matches=arm['raw_rtts_ms']==[v for b in blocks for v in b['rtts_ms']],
        mac_tx_packets=arm['mac_tx_packets_delta'],mac_tx_retries=arm['mac_tx_retries_delta'],
        retry_events_per_packet=arm['mac_tx_retries_delta']/arm['mac_tx_packets_delta'] if arm['mac_tx_packets_delta'] else None,
        mac_sums_match=all(sum(b[k] for b in blocks)==arm[k] for k in ('mac_tx_packets_delta','mac_tx_retries_delta')),
        summary_goodput_mbps=saved.goodput_mbps,summary_dl_mbps=saved.dl_goodput_mbps,summary_ul_mbps=saved.ul_goodput_mbps,summary_p50_ms=saved.p50_ms,summary_p95_ms=saved.p95_ms,summary_p99_ms=saved.p99_ms,summary_jain=saved.jain_fairness,
        directional_GP_identity=(saved.ul_goodput_mbps==0 and saved.dl_goodput_mbps==saved.goodput_mbps) if saved.workload_regime=='unidir_dl_2flow' else (saved.dl_goodput_mbps==0 and saved.ul_goodput_mbps==saved.goodput_mbps) if saved.workload_regime=='unidir_ul_2flow' else None,
        saved_station_drops=saved.station_drops,saved_restoration_verified=saved.restoration_verified,evaluation=arm['evaluation'])


def _change(target,control):return (target/control-1)*100 if control else None


def build_analysis():
    from orchestration.autoresearch.fmx_offline_data import load_all47_measurements,load_all47_block_observations
    dependencies=[Path(__file__),ROOT/'orchestration/autoresearch/fmx_offline_data.py',ROOT/'analysis/statistics/fmx_r33_to_r42_exact_holm500_audit.py',ROOT/'analysis/statistics/fmx_r27_to_r32_certified_wds_audit.py',ROOT/'analysis/statistics/fmx_r22_to_r26_crossover_audit.py',ROOT/'analysis/statistics/fmx_r16_to_r21_real_crossover_audit.py',ROOT/'analysis/statistics/fmx_r15_and_crossover_statistical_audit.py',ROOT/'analysis/statistics/fmx_r10_to_r14_causal_and_power_analysis.py']
    dep_refs=[binding(p) for p in dependencies]
    receipts,literals,refs=frozen_inputs();records,_=load_all47_measurements();blocks=load_all47_block_observations();by_id={(r.round_id,r.iteration):r for r in records}
    new=[r for r in blocks['crossed'] if int(r['round_id'][1:]) in ROUNDS]
    counts=dict(records=len(records),new_arms=sum(len(a['iterations']) for a in receipts.values()),crossed_rows=len(blocks['crossed']),new_crossed_rows=len(new),matched_ids=len({(r['round_id'],r['block_index']) for r in blocks['crossed']}),new_matched_ids=len({(r['round_id'],r['block_index']) for r in new}),sequential_R17=len(blocks['sequential']))
    if counts!=dict(records=194,new_arms=10,crossed_rows=700,new_crossed_rows=160,matched_ids=262,new_matched_ids=80,sequential_R17=16):raise ValueError('Unexpected actual194/700/262 corpus')
    contrasts,descriptions,designs=[],[],[]
    for number in ROUNDS:
        arms=receipts[number]['iterations'];control,target=[a['commit'] for a in arms];group=[r for r in new if r['round_id']==f'R{number}']
        if len(arms)!=2 or len(group)!=32:raise ValueError('Exactly2arms/32 source rows required')
        literal_by={(arm['commit'],b['block_index']):b for arm in literals[number]['iterations'] for b in arm['repetition_blocks']}
        for metric in METRICS:
            pairs=pair_rows(group,control,target,metric)
            if len(pairs)!=16:raise ValueError('Exactly16 genuine paired units required')
            d=[p['difference'] for p in pairs];effect=exact_effect(d);flips=exact_sign_flips(d)
            if flips['rank']['p_value']!=effect['exact_rank']['p_value'] or flips['sign']['p_value']!=effect['exact_sign']['p_value']:raise ValueError('All65536 enumeration disagrees with accepted rank/sign DP')
            decimal_d=[literal_metric(literal_by[(target,p['block_index'])],metric)-literal_metric(literal_by[(control,p['block_index'])],metric) for p in pairs]
            decimal_flips=enumerate_fraction_flips(decimal_d)
            saved=by_id[(f'R{number}',target)];cid=json.dumps([f'R{number}',control,target,metric],separators=(',',':'))
            r=dict(source_hypothesis_id=cid,scope=f'R{number}',control=control,target=target,regime=saved.workload_regime,
                control_policy_id=by_id[(f'R{number}',control)].policy_key,target_policy_id=saved.policy_key,metric=metric,
                direction='lower' if metric in ('p50_rtt_ms','p95_rtt_ms','p99_rtt_ms') else 'higher',
                paired_unit_ids=[dict(round_id=p['round_id'],block_index=p['block_index']) for p in pairs],pairs=pairs,
                favorable_blocks=sum(x<0 if metric in ('p50_rtt_ms','p95_rtt_ms','p99_rtt_ms') else x>0 for x in d),equal_blocks=sum(x==0 for x in d),quality=_quality(group),
                exact_sign_flips=flips,source_decimal_sensitivity=dict(exact_flips=decimal_flips,literal_differences=[str(x) for x in decimal_d],rank_p_changed=decimal_flips['rank']['p_value']!=flips['rank']['p_value'],mean_p_changed=decimal_flips['mean']['p_value']!=flips['mean']['p_value']),
                period_adjusted=period_adjusted_estimation(group,control,target,metric),**effect)
            contrasts.append(r)
        diag=multilevel_design_diagnostics(group)|dict(round_id=f'R{number}')
        diag['schedule_agreement']=schedule_agreement(group,receipts[number]['crossover_schedule'],{'A':control,'B':target})
        diag['full_model_interpretation']='Fullblock+period+current+lag: rank/alias diagnostic, never silently drop lag and call the restricted effect separatedcausal'
        designs.append(diag)
        for i,arm in enumerate(arms):descriptions.append(source_audit(number,arm,literals[number]['iterations'][i],by_id[(f'R{number}',arm['commit'])]))
    if len(contrasts)!=30:raise ValueError('Complete30 primary contrasts required')
    families={'new_rank30_bound500':padded_family(contrasts,500,'new_rank30_bound500')}
    oldpath=ROOT/'artifacts/autoresearch/waves_ac_to_af_20261024/wave_ad_exact_holm500_analysis.json';prior=json.loads(oldpath.read_text(encoding='utf-8'))['families']['complete_known747_bound747']['known_hypotheses']
    if len(prior)!=747:raise ValueError('Prior exact known747 required unchanged')
    families['complete_known_rank777_bound777']=padded_family([dict(source_hypothesis_id=k,exact_rank=dict(p_value=p)) for k,p in prior.items()]+contrasts,777,'complete_known_rank777_bound777')
    mean_members=[dict(source_hypothesis_id='MEANFLIP:'+r['source_hypothesis_id'],exact_rank=dict(p_value=r['exact_sign_flips']['mean']['p_value'])) for r in contrasts]
    families['new_meanflip30_bound500']=padded_family(mean_members,500,'new_meanflip30_bound500')|dict(statistic='EXACT_TWO_SIDED_INTEGER_ARITHMETIC_MEAN_FLIP_SECONDARY_FAMILY_NOT_RANK')
    for r in contrasts:
        r['family_adjusted_p']={k:v['adjusted_p'][r['source_hypothesis_id']] for k,v in families.items() if r['source_hypothesis_id'] in v['adjusted_p']}
        r['mean_flip_holm500_adjusted_p']=families['new_meanflip30_bound500']['adjusted_p']['MEANFLIP:'+r['source_hypothesis_id']]
    claimed={43:{'p50_rtt_ms':16,'p95_rtt_ms':14},44:{'p50_rtt_ms':16,'p95_rtt_ms':16,'p99_rtt_ms':14},45:{m:16 for m in METRICS[1:]},46:{'p95_rtt_ms':15,'p99_rtt_ms':15},47:{m:16 for m in METRICS[1:]}}
    claims=[dict(source_hypothesis_id=r['source_hypothesis_id'],round_id=r['scope'],metric=r['metric'],claimed_favorable=claimed[int(r['scope'][1:])][r['metric']],actual_favorable=r['favorable_blocks'],matches=r['favorable_blocks']==claimed[int(r['scope'][1:])][r['metric']],rank_p=r['exact_rank']['p_value'],sign_p=r['exact_sign']['p_value'],mean_flip_p=r['exact_sign_flips']['mean']['p_value'],R46_claimed34of65536_statistic='SIGN_COUNT_NOT_AUTOMATICALLY_RANK_OR_MEAN' if r['scope']=='R46' else None) for r in contrasts if r['metric'] in claimed[int(r['scope'][1:])]]
    r39=next(r for r in records if r.round_id=='R39' and r.iteration.startswith('r39_iter1_'));r46=[by_id[('R46',arm['commit'])] for arm in receipts[46]['iterations']]
    describe=lambda r:dict(round_id=r.round_id,iteration=r.iteration,policy_id=r.policy_key,goodput_mbps=r.goodput_mbps,ul_goodput_mbps=r.ul_goodput_mbps,p50_ms=r.p50_ms,p95_ms=r.p95_ms,p99_ms=r.p99_ms,mac_retry_rate=r.mac_retry_rate,mac_tx_packets=r.mac_tx_packets,mac_tx_retries=r.mac_tx_retries,regime=r.workload_regime,restoration_reported=r.restoration_verified,packet_loss_pct=r.packet_loss_pct)
    loss=[arm['evaluation']['fmx_loss'] for arm in receipts[46]['iterations']]
    tradeoff=dict(status='DESCRIPTIVE_CROSSROUND_NOT_GENUINE_PAIRED_CONTRAST',R39_target=describe(r39),R46_control=describe(r46[0]),R46_target=describe(r46[1]),R46_p95_change_pct=_change(r46[1].p95_ms,r46[0].p95_ms),R46_p99_change_pct=_change(r46[1].p99_ms,r46[0].p99_ms),R46_UL_change_pct=_change(r46[1].ul_goodput_mbps,r46[0].ul_goodput_mbps),R46_target_vs_R39_target_UL_change_pct=_change(r46[1].ul_goodput_mbps,r39.ul_goodput_mbps),FMX_objective_loss_change_pct=_change(loss[1],loss[0]),objective_is_not_packet_loss=True,packet_loss_change_pct_points=r46[1].packet_loss_pct-r46[0].packet_loss_pct,full_recorded_package_equal_R39_R46_target=r39.policy_key==r46[1].policy_key,paired_p_value=None,limits='Differentrounds/packages/samplecounts; no shared actual matchedblockidentities or randomized crossround causal effect. Do not call objective loss43.3percent reduction a packetloss reduction.')
    inputs={k:binding(BASE/v) for k,v in {'records':'normalized_r1_to_r47_measurements_20261024.json','blocks':'normalized_r16_to_r47_block_observations_20261024.json','manifest':'inputs_manifest.json'}.items()}
    projection=[dict(source_hypothesis_id=r['source_hypothesis_id'],regime=r['regime'],target_policy_id=r['target_policy_id'],control_policy_id=r['control_policy_id'],round_ids=[r['scope']],paired_unit_ids=r['paired_unit_ids'],metric=r['metric'],direction=r['direction'],effect_hl=r['HL_estimate'],p_exact_rank=r['exact_rank']['p_value'],holm500_adjusted_p=r['family_adjusted_p']['new_rank30_bound500'],family500_key='new_rank30_bound500',comparability_status='WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON',statistic='PRIMARY_EXACT_SIGNED_RANK_NOT_MEAN_FLIP') for r in contrasts]
    if [binding(p) for p in dependencies]!=dep_refs:raise ValueError('Dependency changed during computation')
    return dict(schema_version=1,status='OFFLINE_EXACT_DYADIC_AUDIT_PENDING_INDEPENDENT_ACCEPTANCE',software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),counts=counts,sources=refs,source_inputs=inputs,numerical_dependencies=dep_refs,family_plan=binding(BASE/'wave_ah_family_recipe.json'),prior_unchanged_analysis=binding(oldpath),frozen_spec=binding(BASE/'inputs/waves_ag_to_aj_20261024_spec.md'),contrasts=contrasts,families=families,source_claim_audits=descriptions,requested_win_claims=claims,design_diagnostics=designs,R46_vs_R39_tradeoff=tradeoff,catalog_scope=dict(primary_new_known=30,primary_prior_known=747,complete_primary_known=777,complete_primary_Holm500='INAPPLICABLE_KNOWN777_EXCEEDS500',mean_flip_family_separate=True,not_all_project_tests=True),promotion_evidence=dict(source_inputs={k+'_sha256':v['sha256'] for k,v in inputs.items()},contrasts=projection,families={k:v for k,v in families.items() if k!='new_meanflip30_bound500'},evidence_only_not_promotion=True),automatic_execution_allowed=False,physical_or_causal_acceptance=False,limits=['All16-pair sign flips exact over supplied float differences as binary rationals; sourceDecimal sensitivities separate. Rank,sign,mean are distinct statistics on the same80actualblocks.','No new/old policy pooling. Changed R45 AQL is not the old selected package.','Named no-differential-carryover submodel estimates only; fullcurrent+lag rank aliases remain, no causal separation claimed.','All reported restoration/cipher/counter/sourcecertification is not independent device/sector acceptance.','Only frozen new inputs and prior accepted offline data/source; no original/newer/live data or processes touched, no network/target/recipe execution.'])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=BASE/'wave_ah_dyadic_zero_loss_analysis.json');path=parser.parse_args().output.resolve()
    if path.parent!=BASE.resolve() or not path.name.startswith('wave_ah_') or path.suffix!='.json':raise ValueError('Exclusive owned WaveAH output only')
    result=build_analysis()
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=result['status'],contrasts=len(result['contrasts']),source_windows=len(result['source_claim_audits']))))


if __name__=='__main__':main()
