"""Pure offline frozen R76-R80 exact paired audit and approximate BCa sensitivity.

No acquisition, actuator, recipe execution, or unobserved context interpolation.
"""
from __future__ import annotations
import argparse
import ast
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import numpy as np
import scipy
from scipy.special import ndtr, ndtri
from analysis.statistics.fmx_r43_to_r47_dyadic_zero_loss_audit import enumerate_fraction_flips, exact_sign_flips, literal_metric
from analysis.statistics.fmx_r48_to_r56_distance_goodput_dyadic_audit import source_arm_audit, observed_utility, record_dict
from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import multilevel_design_diagnostics, schedule_agreement
from analysis.statistics.fmx_r22_to_r26_crossover_audit import METRICS as ORDINARY_METRICS, _metric as ordinary_metric, _quality
from analysis.statistics.fmx_r27_to_r32_certified_wds_audit import binding, padded_family
from analysis.statistics.fmx_r33_to_r42_exact_holm500_audit import exact_effect, parse_source
from analysis.statistics.fmx_r57_to_r60_retry64_goodput_parity_audit import changed_coordinates

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/autoresearch/waves_be_to_bh_20261024'
ROUNDS=(76,77,78,79,80)
METRICS=(*ORDINARY_METRICS,'wds_mac_retry_rate')
QOE=ORDINARY_METRICS[1:]
LOWER=(*ORDINARY_METRICS[1:4],'wds_mac_retry_rate')
MANIFEST_SHA='98a66e5a52a7e952e02843bf3b0d2a80b78491df1cafd633db517fc346f6beef'
FAMILY_SHA='58e5ee1b88817501782091871a7e9623d121a1cfa47db03e5c9ab830bd4ce903'
RANK_FAMILY='new_rank35_bound500'
MEAN_FAMILY='new_meanflip35_bound500'
TIMING={76:(1500,3,18,36),77:(7500,16,57,114),78:(10500,23,78,156),79:(13500,30,99,198),80:(7500,16,57,114)}

def retry_fraction(row):
    """Saved station-counter rate, not PER and not independent device identity."""
    n=row.get('mac_tx_packets_delta');r=row.get('mac_tx_retries_delta')
    if type(n) is not int or n<=0 or type(r) is not int or r<0:
        raise ValueError('Missing/invalid typed positive station TX denominator or retry counter')
    if row.get('counter_interface')!='phy0-ap0.sta1':
        raise ValueError('Exact declared WDS station interface required')
    return Fraction(r,n)

def _metric(row,metric):
    if metric=='wds_mac_retry_rate':return float(retry_fraction(row))
    return ordinary_metric(row,metric)

def source_metric(row,metric):
    if metric=='wds_mac_retry_rate':
        n=row.get('mac_tx_packets_delta');r=row.get('mac_tx_retries_delta')
        if type(n) is not int or n<=0 or type(r) is not int or r<0:raise ValueError('Literal station counters unavailable')
        return Fraction(r,n)
    return literal_metric(row,metric)


def frozen_inputs():
    manifest=BASE/'inputs_manifest.json'
    if binding(manifest)['sha256']!=MANIFEST_SHA:raise ValueError('Frozen manifest changed')
    if binding(BASE/'wave_bf_family_and_bootstrap_recipe.json')['sha256']!=FAMILY_SHA:raise ValueError('Family definition changed')
    entries=json.loads(manifest.read_text(encoding='utf-8'))['entries']
    if len(entries)!=15:raise ValueError('Require15 frozen inputs')
    receipts,literals,refs,recipes={},{},[],{}
    seen=set()
    for ref in entries:
        path=(ROOT/ref['path']).resolve()
        if type(ref.get('round')) is not int or ref['round'] not in ROUNDS or path.parent!=(BASE/'inputs').resolve():raise ValueError('Owned frozen R76-R80 direct inputs only')
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


def recipe_coverage_commands(text):
    """Literal shell fragments in source are declarations, never execution proof."""
    result=[]
    for node in ast.walk(ast.parse(text)):
        if isinstance(node,ast.Constant) and isinstance(node.value,str):
            for match in re.finditer(r'\biw\s+phy\s+phy0\s+set\s+coverage\s+(\d+)\b([^\n]*)',node.value):
                result.append(dict(line=node.lineno,coverage_class_literal=int(match.group(1)),
                    ignored_error_declared='|| true' in match.group(2),
                    source_text_only_not_execution_or_readback=True))
    return result


def recorded_context(record):
    """Presence-first fallback only; never impute a timing value from class."""
    def declared(key):
        if key in record:return record[key]
        nested=record.get('certified_wds_evidence')
        return nested.get(key) if isinstance(nested,dict) else None
    return {k:declared(k) for k in ('workload_regime','active_flow_count','distance_meters','coverage_class','slot_time_us','ack_timeout_us')}


def pair_rows(rows,control,target,metric):
    """Explicit R76..R80 validator; no global edits or relabeled old IDs."""
    if not isinstance(rows,list) or not rows:raise ValueError('Explicit crossed rows required')
    seen=set();rounds=set();groups=defaultdict(list)
    for row in rows:
        if row.get('round_id') not in {f'R{n}' for n in ROUNDS}:raise ValueError('Owned frozen R76..R80 only')
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


def validated_differences(values):
    if not isinstance(values,(list,tuple,np.ndarray)) or len(values)<3:
        raise ValueError('At least three paired numeric differences required')
    if any(isinstance(v,(bool,np.bool_)) or not isinstance(v,(int,float,np.integer,np.floating)) for v in values):
        raise ValueError('Finite numeric paired differences required')
    result=np.asarray(values,dtype=float)
    if result.ndim!=1 or not np.isfinite(result).all():raise ValueError('Finite one-dimensional differences required')
    return result


def bootstrap_indices(n,resamples=10000,seed=20261024):
    if type(n) is not int or n<3 or type(resamples) is not int or resamples<2 or type(seed) is not int or seed<0:
        raise ValueError('Explicit positive sample/resample counts and integer seed required')
    return np.random.default_rng(seed).integers(0,n,size=(resamples,n),dtype=np.int64)


def walsh_hl(values):
    values=validated_differences(values)
    i,j=np.triu_indices(len(values))
    return float(np.median(values[i]/2+values[j]/2))


def paired_bca_hl(values,*,resample_indices=None,resamples=10000,seed=20261024,confidence=.95):
    """Paired bootstrap HL sensitivity; no independent resampling of arms.

    BCa is approximate, conditional on independent paired units and a suitable
    shift interpretation. Degeneracy is unavailable, never an invented CI.
    """
    x=validated_differences(values);n=len(x)
    if isinstance(confidence,bool) or not isinstance(confidence,(int,float)) or not 0<confidence<1:
        raise ValueError('Confidence must be strictly between zero and one')
    indices=bootstrap_indices(n,resamples,seed) if resample_indices is None else np.asarray(resample_indices)
    if indices.shape!=(resamples,n) or indices.dtype.kind not in 'iu' or np.any(indices<0) or np.any(indices>=n):
        raise ValueError('Paired resample index matrix has wrong shape/type/bounds')
    i,j=np.triu_indices(n);samples=x[indices]
    distribution=np.median(samples[:,i]/2+samples[:,j]/2,axis=1)
    theta=walsh_hl(x)
    # n-1 can equal two for small generic fixtures; the actual audit uses n=16.
    def reduced_hl(z):
        a,b=np.triu_indices(len(z));return float(np.median(z[a]/2+z[b]/2))
    jack=np.array([reduced_hl(np.delete(x,k)) for k in range(n)])
    result=dict(status='UNAVAILABLE',interval=None,observed_HL=theta,confidence=confidence,
        resamples=resamples,seed=seed,bit_generator='PCG64',unit='PAIRED_BLOCK_DIFFERENCE',
        resample_indices_sha256=hashlib.sha256(indices.astype('<i8').tobytes()).hexdigest(),
        quantile_method='linear',z0_tie_rule='MIDRANK',jackknife_estimates=jack.tolist(),
        bootstrap_min=float(distribution.min()),bootstrap_max=float(distribution.max()),
        exact_interval=False,promotion_input=False)
    def unavailable(reason):return result|dict(reason=reason)
    if not np.isfinite(distribution).all() or not np.isfinite(jack).all():return unavailable('NONFINITE_BOOTSTRAP_OR_JACKKNIFE')
    if np.ptp(distribution)==0:return unavailable('CONSTANT_BOOTSTRAP_DISTRIBUTION')
    centered=jack.mean()-jack;scale=float(np.max(np.abs(centered)))
    if scale==0:return unavailable('ZERO_JACKKNIFE_VARIATION')
    scaled=centered/scale
    acceleration=float(np.sum(scaled**3)/(6*np.sum(scaled**2)**1.5))
    less=int(np.sum(distribution<theta));equal=int(np.sum(distribution==theta))
    proportion=(less+equal/2)/resamples
    result.update(bias_less=less,bias_equal=equal,bias_midrank_proportion=proportion,acceleration=acceleration)
    if not 0<proportion<1:return unavailable('BIAS_CORRECTION_BOUNDARY')
    z0=float(ndtri(proportion));za=ndtri([(1-confidence)/2,(1+confidence)/2]);den=1-acceleration*(z0+za)
    result['z0']=z0
    if not np.isfinite(den).all() or np.any(den<=0):return unavailable('INVALID_BCA_DENOMINATOR')
    probabilities=ndtr(z0+(z0+za)/den)
    result['adjusted_probabilities']=probabilities.tolist()
    if not np.isfinite(probabilities).all() or not 0<probabilities[0]<probabilities[1]<1:
        return unavailable('INVALID_OR_BOUNDARY_ADJUSTED_PROBABILITIES')
    interval=np.quantile(distribution,probabilities,method='linear')
    if not np.isfinite(interval).all() or interval[0]>interval[1]:return unavailable('INVALID_INTERVAL')
    return result|dict(status='APPROXIMATE_PAIRED_BCA_SENSITIVITY',reason=None,interval=interval.tolist(),
        adjusted_tail_expected_counts=[float(resamples*probabilities[0]),float(resamples*(1-probabilities[1]))],
        monte_carlo_tail_resolution_limited=bool(min(probabilities[0],1-probabilities[1])*resamples<10))


def profile_conditions(contrasts,utilities):
    result=[]
    for number in ROUNDS:
        group=[c for c in contrasts if c['scope']==f'R{number}' and c['metric'] in QOE]
        if len(group)!=5:raise ValueError('Five QoE metrics required; retry is separate')
        u=next(u for u in utilities if u['round_id']==f'R{number}')
        unanimous=all(c['favorable_blocks']==16 for c in group)
        significant=all(c['family_adjusted_p'][RANK_FAMILY]<=.05 and (c['HL_estimate']<0 if c['direction']=='lower' else c['HL_estimate']>0) for c in group)
        result.append(dict(round_id=f'R{number}',all_five_16of16=unanimous,five_direct_rank_HL_Holm500=significant,
            strict_observed_GP_loss_below2=Fraction(u['loss_percent_exact'])<2,
            requested_strict_necessary_conditions_met=unanimous and significant and Fraction(u['loss_percent_exact'])<2,
            target_retry_lower=u['target_retry_lower'],failed_unanimity_metrics=[c['metric']for c in group if c['favorable_blocks']!=16],
            no_health_or_controller_promotion_inferred=True))
    return result


def claim_audits(descriptions,contrasts,utilities):
    """Specified display precision remains separate from full-precision source."""
    out=[]
    def display(n,name,actual,claimed,places):
        out.append(dict(round_id=f'R{n}',claim=name,claimed_literal=claimed,actual=float(actual),
            actual_exact_fraction=str(Fraction(actual)),format_places=places,
            canonical_display=format(float(actual),f'.{places}f'),matches=format(float(actual),f'.{places}f')==claimed))
    gp={76:('108.916016','107.405273'),78:('85.142578','84.433594'),79:('74.355469','74.943359'),80:('90.556641','86.743164')}
    delta={76:('-1.387071',6),77:('-2.0248',4),78:('-0.832702',6),79:('0.790648',6),80:('-4.211',3)}
    latency={76:('6.8415','21.7318','31.5208'),78:('5.7650','15.7771','23.7261'),79:('5.1585','14.2464','18.9780'),80:('6.0665','18.3825','27.8459')}
    jain={76:'0.77062988',77:'0.79644775',78:'0.80072021',79:'0.76855469',80:'0.70526123'}
    ul_gain={76:'50.8',77:'41.4',78:'44.8',79:'58.7',80:'35.1'}
    loss={76:('0.754236','0.386001','48.8'),77:('0.924380','0.362316','60.8'),78:('0.835910','0.281530','66.3'),79:('0.897392','0.236443','73.6'),80:('0.776391','0.351923','54.7')}
    for n in ROUNDS:
        a,b=[d for d in descriptions if d['round_id']==f'R{n}'];u=next(u for u in utilities if u['round_id']==f'R{n}')
        if n in gp:
            for k,r in enumerate((a,b)):display(n,('control'if k==0 else'target')+'_GP',Fraction(str(r['summary']['goodput_mbps'])),gp[n][k],6)
        display(n,'signed_GP_change_percent',-Fraction(u['loss_percent_exact']),*delta[n])
        if n in latency:
            for m,c in zip(('p50_ms','p95_ms','p99_ms'),latency[n]):display(n,'target_'+m,Fraction(str(b['summary'][m])),c,4)
        display(n,'target_Jain',Fraction(str(b['summary']['jain_fairness'])),jain[n],8)
        au,bu=[Fraction(str(d['summary']['ul_goodput_mbps']))for d in (a,b)]
        display(n,'UL_gain_percent',(bu-au)*100/au,ul_gain[n],1)
        fa,fb=[Fraction(str(d['evaluation']['fmx_loss']))for d in (a,b)]
        display(n,'control_fmx_objective',fa,loss[n][0],6);display(n,'target_fmx_objective',fb,loss[n][1],6)
        display(n,'fmx_objective_reduction_percent',(fa-fb)*100/fa,loss[n][2],1)
        expected={m:16 for m in QOE}
        if n in (77,80):expected.update(ul_goodput_mbps=15,jain_fairness=15)
        if n==79:expected.update(p95_rtt_ms=15,p99_rtt_ms=15)
        if n in (78,79):expected['goodput_rx_mbps']={78:6,79:7}[n]
        for m,count in expected.items():
            c=next(c for c in contrasts if c['scope']==f'R{n}' and c['metric']==m)
            out.append(dict(round_id=f'R{n}',claim='favorable_blocks:'+m,claimed_count=count,actual_count=c['favorable_blocks'],matches=count==c['favorable_blocks']))
    for n,side,value in ((76,0,'0.188018'),(76,1,'0.179643'),(79,0,'0.439473'),(79,1,'0.321434')):
        d=[d for d in descriptions if d['round_id']==f'R{n}'][side]
        display(n,('control'if side==0 else'target')+'_retry_percent',Fraction(d['retry_fraction_exact'])*100,value,6)
    for n,metric,claimed in ((77,'goodput_mbps','89.922852'),(77,'ul_goodput_mbps','22.309570'),(80,'ul_goodput_mbps','15.325195')):
        b=[d for d in descriptions if d['round_id']==f'R{n}'][1];display(n,'target_'+metric,Fraction(str(b['summary'][metric])),claimed,6)
    a,b=[d for d in descriptions if d['round_id']=='R80']
    display(80,'control_UL',Fraction(str(a['summary']['ul_goodput_mbps'])),'11.344727',6)
    display(80,'control_Jain',Fraction(str(a['summary']['jain_fairness'])),'0.64044189',8)
    u=next(u for u in utilities if u['round_id']=='R78');display(78,'preserved_GP_percent',100-Fraction(u['loss_percent_exact']),'99.1673',4)
    a,b=[d for d in descriptions if d['round_id']=='R79'];ra,rb=[Fraction(d['retry_fraction_exact'])for d in(a,b)]
    display(79,'relative_retry_rate_reduction_percent',(ra-rb)*100/ra,'26.9',1)
    return out


def ablation_description(records,contrasts):
    arms={n:sorted([r for r in records if r['round_id']==f'R{n}'],key=lambda r:r['iteration']) for n in(77,80)}
    if any(len(x)!=2 for x in arms.values()):raise ValueError('Separate two-arm R77/R80 required')
    outcomes=('goodput_mbps','ul_goodput_mbps','p50_ms','p95_ms','p99_ms','jain_fairness')
    values={}
    for m in outcomes:
        a,b=[Fraction(str(r[m]))for r in arms[77]];c,d=[Fraction(str(r[m]))for r in arms[80]]
        values[m]=dict(target77_minus_target80_exact=str(b-d),target77_minus_target80=float(b-d),
            within77_exact=str(b-a),within80_exact=str(d-c),descriptive_difference_in_differences_exact=str((b-a)-(d-c)))
    changes={label:changed_coordinates(json.loads(arms[77][i]['policy_key']),json.loads(arms[80][i]['policy_key']))for i,label in enumerate(('stock','target'))}
    return dict(status='NOT_AN_ISOLATED_AF_ABLATION',rounds=['R77','R80'],full_policy_coordinate_differences=changes,
        contexts=[recorded_context(arms[n][1])for n in(77,80)],observed_differences=values,
        crossround_paired_test=None,crossround_unit_identity_demonstrated=False,
        claimed_mechanism='AIRTIME_RX_DOUBLE_CHARGE_AND_UNIVERSAL_AT_LEAST_6000M_AF1_RULE',mechanism_status='NOT_DEMONSTRATED',
        target_GP_advantage_display_2f=format(values['goodput_mbps']['target77_minus_target80'],'.2f'),
        target_UL_advantage_display_2f=format(values['ul_goodput_mbps']['target77_minus_target80'],'.2f'),
        limits=['Different round-specific controls, time and full endpoint packages. No shared randomization or block pairing.',
            'Difference in differences is descriptive only, not a parallel-trends or af causal estimate.'])


def loo_diagnostics(contrasts):
    result=[]
    for c in contrasts:
        if c['scope']!='R77':continue
        d=[p['difference']for p in c['pairs']]
        result.append(dict(metric=c['metric'],primary_all16=True,primary_rank_p=c['exact_rank']['p_value'],
            leave_one_out=[dict(omitted_block_index=p['block_index'],explicit_block14=p['block_index']==14,
                rank_p=exact_sign_flips(d[:k]+d[k+1:])['rank']['p_value'],HL=walsh_hl(d[:k]+d[k+1:])) for k,p in enumerate(c['pairs'])],
            replaces_primary=False,RF_spike_cause_demonstrated=False))
    return result


def declared_distance_grid(records,contrasts,prior_views):
    all_contrasts=[c for v in prior_views for c in v['contrasts']]+contrasts
    points=[]
    for n in (60,76,61,70,62,77,80,69,78,73,79,75):
        arms=sorted([r for r in records if r['round_id']==f'R{n}'],key=lambda r:r['iteration'])
        if len(arms)!=2:raise ValueError('Exactly two arms for each observed grid round')
        a,b=arms;group=[c for c in all_contrasts if c['scope']==f'R{n}'and c['metric']in QOE]
        if len(group)!=5:raise ValueError('All five source-bound QoE contrasts required for grid')
        def adjusted(c):return next(v for k,v in c['family_adjusted_p'].items()if k.startswith('new_rank')and k.endswith('bound500'))
        u=observed_utility(a['goodput_mbps'],b['goodput_mbps'])
        points.append(dict(round_id=f'R{n}',context=recorded_context(b),full_control_policy_id=a['policy_key'],full_target_policy_id=b['policy_key'],
            control_metrics={k:a[k]for k in('goodput_mbps','ul_goodput_mbps','p50_ms','p95_ms','p99_ms','jain_fairness')},
            target_metrics={k:b[k]for k in('goodput_mbps','ul_goodput_mbps','p50_ms','p95_ms','p99_ms','jain_fairness')},
            utility=u,favorable_blocks={c['metric']:c['favorable_blocks']for c in group},
            all_five_unanimous=all(c['favorable_blocks']==16 for c in group),
            five_direct_rank_HL_Holm500=all(adjusted(c)<=.05 and(c['HL_estimate']<0 if c['direction']=='lower'else c['HL_estimate']>0)for c in group),
            paired_crossround_p=None,physical_range_verified=False))
    contexts={p['context']['distance_meters']for p in points}
    if len(contexts)!=11:raise ValueError('Eleven distinct observed declared distances required')
    observed_cells=sorted({(r['active_flow_count'],r['distance_meters'])for r in records if r['window_kind']=='primary'and r.get('distance_meters')in contexts},key=lambda x:(x[0],x[1]))
    return dict(status='OBSERVED_PACKAGE_CONTEXT_GRID_NOT_COMMON_POLICY_CURVE',points=points,distinct_declared_distances=len(contexts),
        separate_7500m_packages=['R77','R80'],different_target_package_count=len({p['full_target_policy_id']for p in points}),
        observed_flow_distance_cells=[dict(active_flow_count=f,distance_meters=d)for f,d in observed_cells],
        all_44_cells_qualified=False,interpolation_permitted=False,crossround_causal_or_RF_range_proof=False)


def build_analysis():
    from orchestration.autoresearch.fmx_live_dataset import load_all80_measurements,load_all80_block_observations
    module_names=('fmx_r71_to_r75_seven_distance_and_flow_audit','fmx_r43_to_r47_dyadic_zero_loss_audit',
        'fmx_r48_to_r56_distance_goodput_dyadic_audit','fmx_r33_to_r42_exact_holm500_audit',
        'fmx_r27_to_r32_certified_wds_audit','fmx_r22_to_r26_crossover_audit','fmx_r16_to_r21_real_crossover_audit',
        'fmx_r15_and_crossover_statistical_audit','fmx_r10_to_r14_causal_and_power_analysis','fmx_r57_to_r60_retry64_goodput_parity_audit')
    dependencies=[Path(__file__),ROOT/'orchestration/autoresearch/fmx_live_dataset.py',ROOT/'orchestration/autoresearch/fmx_offline_data.py']+[ROOT/f'analysis/statistics/{n}.py'for n in module_names]
    before=[binding(p)for p in dependencies]
    implementation=BASE/'wave_bf_implementation_freeze.json'
    frozen=json.loads(implementation.read_text(encoding='utf-8'))
    if frozen['source']!=binding(Path(__file__)) or frozen['family_recipe']['sha256']!=FAMILY_SHA:
        raise ValueError('Implementation and bootstrap recipe must be frozen before inference')
    receipts,literals,refs,recipes=frozen_inputs()
    typed,_=load_all80_measurements();blocks=load_all80_block_observations()
    records=[record_dict(r)for r in typed];by_id={(r['round_id'],r['iteration']):r for r in records}
    new=[b for b in blocks['crossed']if int(b['round_id'][1:])in ROUNDS]
    counts=dict(records=len(records),new_arms=sum(len(r['iterations'])for r in receipts.values()),crossed_rows=len(blocks['crossed']),
        new_crossed_rows=len(new),matched_ids=len({(b['round_id'],b['block_index'])for b in blocks['crossed']}),
        new_matched_ids=len({(b['round_id'],b['block_index'])for b in new}),sequential_R17=len(blocks['sequential']))
    if counts!=dict(records=260,new_arms=10,crossed_rows=1756,new_crossed_rows=160,matched_ids=790,new_matched_ids=80,sequential_R17=16):
        raise ValueError('Actual260/1756/790+16 corpus required; spec161 is not source truth')
    indices=bootstrap_indices(16)
    descriptions=[];utilities=[];designs=[];contrasts=[]
    # Source-bound descriptives are built and plotted BEFORE inferential results.
    descriptive=[]
    for n in ROUNDS:
        arms=receipts[n]['iterations']
        if len(arms)!=2:raise ValueError('Exactly two source arms required')
        control,target=[a['commit']for a in arms];group=[b for b in new if b['round_id']==f'R{n}']
        for metric in METRICS:
            pairs=pair_rows(group,control,target,metric)
            if len(pairs)!=16:raise ValueError('Exactly16 genuine pairs required')
            descriptive.append(dict(round_id=f'R{n}',metric=metric,pairs=pairs))
        for k,arm in enumerate(arms):
            saved=by_id[(f'R{n}',arm['commit'])]
            audit=source_arm_audit(n,arm,literals[n]['iterations'][k],saved)
            audit['declared_timing_context']=declared_context(n,receipts[n],arm,saved)
            audit['recipe_distance_calls']=recipe_distance_calls(recipes[n]);audit['recipe_coverage_commands']=recipe_coverage_commands(recipes[n])
            audit['counter_identity']=dict(interface='phy0-ap0.sta1',evidence='NAMED_IN_FROZEN_RECIPE_NOT_INDEPENDENT_DEVICE_READBACK',peer_MAC=None,
                per_block_counter_records=[dict(block_index=b['block_index'],packets=b['mac_tx_packets_delta'],retries=b['mac_tx_retries_delta'],rate_exact=str(retry_fraction(b)))for b in group if b['treatment_id']==arm['commit']])
            descriptions.append(audit)
        a,b=[by_id[(f'R{n}',t)]for t in(control,target)]
        u=observed_utility(a['goodput_mbps'],b['goodput_mbps'])
        utilities.append(dict(round_id=f'R{n}',**u,control_retry_exact=str(Fraction(a['mac_tx_retries'],a['mac_tx_packets'])),
            target_retry_exact=str(Fraction(b['mac_tx_retries'],b['mac_tx_packets'])),
            target_retry_lower=Fraction(b['mac_tx_retries'],b['mac_tx_packets'])<Fraction(a['mac_tx_retries'],a['mac_tx_packets'])))
        diagnostic=multilevel_design_diagnostics(group)|dict(round_id=f'R{n}')
        diagnostic['schedule_agreement']=schedule_agreement(group,receipts[n]['crossover_schedule'],{'A':control,'B':target})
        diagnostic['interpretation']='Full current/period/lag alias remains; restricted point model assumes no differential carryover.'
        designs.append(diagnostic)
    plot_path=BASE/'wave_bf_paired_descriptives.png'
    if plot_path.exists():raise FileExistsError(plot_path)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(7,5,figsize=(18,20))
    for row in descriptive:
        ax=axes[METRICS.index(row['metric']),ROUNDS.index(int(row['round_id'][1:]))]
        p=row['pairs'];ax.plot([x['block_index']for x in p],[x['control_mean']for x in p],'.-',label='Stock')
        ax.plot([x['block_index']for x in p],[x['treatment_mean']for x in p],'.-',label='Target')
        if row['round_id']=='R77':ax.axvline(14,color='gray',linestyle=':')
        ax.set_title(row['round_id']+' '+row['metric'],fontsize=8);ax.tick_params(labelsize=6)
    axes[0,0].legend();fig.suptitle('Saved block outcomes; declared contexts only; R77 block14 retained')
    fig.tight_layout();fig.savefig(plot_path,dpi=120);plt.close(fig)
    with (BASE/'wave_bf_preinference_descriptives.json').open('x',encoding='utf-8',newline='\n')as f:
        json.dump(dict(status='CREATED_BEFORE_INFERENCE',source_inputs=refs,pairs=descriptive,plot=binding(plot_path),assumptions=frozen['assumptions']),f,indent=2,allow_nan=False);f.write('\n')
    for n in ROUNDS:
        arms=receipts[n]['iterations'];control,target=[a['commit']for a in arms]
        group=[b for b in new if b['round_id']==f'R{n}'];literal_by={(a['commit'],b['block_index']):b for a in literals[n]['iterations']for b in a['repetition_blocks']}
        for metric in METRICS:
            pairs=next(x['pairs']for x in descriptive if x['round_id']==f'R{n}'and x['metric']==metric)
            d=[p['difference']for p in pairs];effect=exact_effect(d);flips=exact_sign_flips(d)
            if any(flips[k]['p_value']!=effect['exact_'+k]['p_value']for k in('rank','sign')):raise ValueError('Exact enumeration and DP disagree')
            decimal=[source_metric(literal_by[(target,p['block_index'])],metric)-source_metric(literal_by[(control,p['block_index'])],metric)for p in pairs]
            sensitivity=enumerate_fraction_flips(decimal);a,b=[by_id[(f'R{n}',t)]for t in(control,target)]
            contrasts.append(dict(source_hypothesis_id=json.dumps([f'R{n}',control,target,metric],separators=(',',':')),scope=f'R{n}',
                control=control,target=target,control_policy_id=a['policy_key'],target_policy_id=b['policy_key'],regime=b['workload_regime'],metric=metric,
                direction='lower'if metric in LOWER else'higher',paired_unit_ids=[dict(round_id=p['round_id'],block_index=p['block_index'])for p in pairs],pairs=pairs,
                favorable_blocks=sum(x<0 if metric in LOWER else x>0 for x in d),equal_blocks=sum(x==0 for x in d),quality=_quality(group),
                exact_sign_flips=flips,source_decimal_sensitivity=dict(literal_differences=[str(x)for x in decimal],exact_flips=sensitivity,
                    rank_p_changed=sensitivity['rank']['p_value']!=flips['rank']['p_value'],mean_p_changed=sensitivity['mean']['p_value']!=flips['mean']['p_value']),
                period_adjusted=period_adjusted_estimation(group,control,target,metric),paired_bca_HL=paired_bca_hl(d,resample_indices=indices),**effect))
    prior_path=ROOT/'artifacts/autoresearch/waves_ba_to_bd_20261024/wave_bb_seven_distance_and_flow_analysis.json'
    if binding(prior_path)['sha256']!='df37b3be5a0d897dca4675b3307d4135a50f2f58084071ba6bf4836613dc0f68':raise ValueError('Accepted prior BB changed')
    prior=json.loads(prior_path.read_text(encoding='utf-8'))['families']['complete_known_rank945_bound945']['known_hypotheses']
    if len(prior)!=945 or len(contrasts)!=35:raise ValueError('Known945+35 required')
    families={RANK_FAMILY:padded_family(contrasts,500,RANK_FAMILY),
        'complete_known_rank980_bound980':padded_family([dict(source_hypothesis_id=k,exact_rank=dict(p_value=p))for k,p in prior.items()]+contrasts,980,'complete_known_rank980_bound980')}
    families[MEAN_FAMILY]=padded_family([dict(source_hypothesis_id='MEANFLIP:'+c['source_hypothesis_id'],exact_rank=dict(p_value=c['exact_sign_flips']['mean']['p_value']))for c in contrasts],500,MEAN_FAMILY)
    for c in contrasts:
        c['family_adjusted_p']={k:v['adjusted_p'][c['source_hypothesis_id']]for k,v in families.items()if c['source_hypothesis_id']in v['adjusted_p']}
        c['mean_flip_holm500_adjusted_p']=families[MEAN_FAMILY]['adjusted_p']['MEANFLIP:'+c['source_hypothesis_id']]
    inputs={k:binding(BASE/name)for k,name in dict(records='normalized_r1_to_r80_measurements_20261024.json',blocks='normalized_r16_to_r80_block_observations_20261024.json',manifest='inputs_manifest.json').items()}
    projection=[dict(source_hypothesis_id=c['source_hypothesis_id'],regime=c['regime'],target_policy_id=c['target_policy_id'],control_policy_id=c['control_policy_id'],
        round_ids=[c['scope']],paired_unit_ids=c['paired_unit_ids'],metric=c['metric'],direction=c['direction'],effect_hl=c['HL_estimate'],p_exact_rank=c['exact_rank']['p_value'],
        holm500_adjusted_p=c['family_adjusted_p'][RANK_FAMILY],family500_key=RANK_FAMILY,comparability_status='WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON',statistic='PRIMARY_EXACT_SIGNED_RANK_NOT_MEAN_FLIP_OR_BOOTSTRAP')for c in contrasts]
    prior_paths=[ROOT/'artifacts/autoresearch'/folder/file for folder,file in (
        ('waves_ao_to_ar_20261024','wave_ap_retry64_goodput_parity_analysis.json'),
        ('waves_as_to_av_20261024','wave_at_strict_distance_and_flow_analysis.json'),
        ('waves_aw_to_az_20261024','wave_ax_five_distance_and_flow_analysis.json'))]+[prior_path]
    prior_bindings=[binding(p)for p in prior_paths]
    grids=declared_distance_grid(records,contrasts,[json.loads(p.read_text(encoding='utf-8'))for p in prior_paths])
    if [binding(p)for p in dependencies]!=before:raise ValueError('Numerical dependency changed during calculation')
    return dict(schema_version=1,status='OFFLINE_ELEVEN_CONTEXT_AND_AF_PACKAGE_AUDIT_PENDING_INDEPENDENT_ACCEPTANCE',counts=counts,
        software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
        sources=refs,source_inputs=inputs,numerical_dependencies=before,family_plan=binding(BASE/'wave_bf_family_and_bootstrap_recipe.json'),implementation_freeze=binding(implementation),
        prior_unchanged_analysis=binding(prior_path),preinference_descriptives=binding(BASE/'wave_bf_preinference_descriptives.json'),paired_plot=binding(plot_path),
        contrasts=contrasts,families=families,source_claim_audits=descriptions,observed_utility=utilities,design_diagnostics=designs,
        numeric_and_win_claims=claim_audits(descriptions,contrasts,utilities),strict_source_profile_conditions=profile_conditions(contrasts,utilities),
        R77_block14_leave_one_out_diagnostics=loo_diagnostics(contrasts),af_package_comparison=ablation_description(records,contrasts),
        eleven_declared_context_grid=grids,prior_grid_evidence=prior_bindings,
        catalog_scope=dict(primary_new_known=35,primary_prior_known=945,complete_primary_known=980,complete_primary_Holm500='INAPPLICABLE_KNOWN980_EXCEEDS500',mean_flip_family_separate=True,not_all_project_tests=True),
        promotion_evidence=dict(source_inputs={k+'_sha256':v['sha256']for k,v in inputs.items()},contrasts=projection,
            families={k:v for k,v in families.items()if k!=MEAN_FAMILY},evidence_only_not_promotion=True),
        bootstrap_common_indices_sha256=hashlib.sha256(indices.astype('<i8').tobytes()).hexdigest(),automatic_execution_allowed=False,physical_or_causal_acceptance=False,
        limits=['80 genuine paired block IDs are not1600 independent physical trials. Randomization, independence, washout and symmetric shift assumptions remain unproven.',
            'Exact conditional float differences and source rational sensitivity are distinct when rounding/ties differ. Retry ratios are event counts/packet counts, not PER.',
            'BCa is approximate paired Monte Carlo sensitivity; degeneracy remains unavailable and does not replace exact acceptance sets or rank-only promotion.',
            'Declared timing contexts and recipe text are not effective runtime or outdoor RF-range proof. R75class33 remains a source-only label.',
            'Full carryover model aliases current/lag; restricted estimates require no differential carryover and do not establish causality.',
            'Eleven observed contexts across differing workload/policy packages do not fill44Cartesian cells or demonstrate universal af rules.',
            'All R77block14 pairs remain in primary outcomes; LOO is diagnostic only. R77/R80block IDs are never crossround paired.'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=BASE/'wave_bf_eleven_distance_and_af_ablation_analysis.json')
    path=p.parse_args().output.resolve()
    if path.parent!=BASE.resolve()or not path.name.startswith('wave_bf_')or path.suffix!='.json':raise ValueError('Owned exclusive BF output only')
    if path.exists():raise FileExistsError(path)
    result=build_analysis()
    with path.open('x',encoding='utf-8',newline='\n')as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=result['status'],contrasts=len(result['contrasts']),arms=len(result['source_claim_audits']))))



# Additive BJ entry points. Historical BF constants/functions remain unchanged.
BJ_BASE=ROOT/'artifacts/autoresearch/waves_bi_to_bl_20261024'
BJ_ROUNDS=(81,82,83,84,85,86)
BJ_TIMING={81:(100,0,9,18),82:(100,0,9,18),83:(3000,6,27,54),84:(6000,13,48,96),85:(7500,16,57,114),86:(9000,20,69,138)}
BJ_REGIMES={81:('unidir_dl_2flow',2,False),82:('unidir_ul_2flow',2,False),83:('bidir_4flow',4,True),84:('bidir_4flow',4,True),85:('bidir_6flow',6,True),86:('bidir_4flow',4,True)}
BJ_MANIFEST_SHA='529168c4a6a8070ae29b0984c73ee8fef44a9e6583f9517594a121a9479a7778'
BJ_FAMILY_SHA='e6c83216bade988b1b42cecd0c89db2d131305dbd2c3bfb299164a6bf7572cd3'
BJ_RANK_FAMILY='new_rank38_bound500'
BJ_MEAN_FAMILY='new_meanflip38_bound500'

def metrics_bj(number):
    if type(number)is not int or number not in BJ_ROUNDS:raise ValueError('Explicit owned R81..R86 required')
    return (*METRICS[:4],METRICS[-1])if number in(81,82)else METRICS

def frozen_inputs_bj():
    if binding(BJ_BASE/'inputs_manifest.json')['sha256']!=BJ_MANIFEST_SHA:raise ValueError('Frozen BJ manifest changed')
    if binding(BJ_BASE/'wave_bj_family_and_bootstrap_recipe.json')['sha256']!=BJ_FAMILY_SHA:raise ValueError('Frozen BJ family changed')
    entries=json.loads((BJ_BASE/'inputs_manifest.json').read_text(encoding='utf-8'))['entries']
    if len(entries)!=18:raise ValueError('Require18frozen copies')
    receipts={};literals={};recipes={};refs=[];seen=set()
    for entry in entries:
        n=entry.get('round');original=Path(entry.get('path',''));path=(ROOT/entry.get('copy','')).resolve()
        if type(n)is not int or n not in BJ_ROUNDS or original.is_absolute()or'..'in original.parts:
            raise ValueError('Only explicit current frozen identities')
        if path!=(BJ_BASE/'inputs'/original).resolve()or not path.is_relative_to((BJ_BASE/'inputs').resolve())or path in seen:
            raise ValueError('Only exact owned frozen copies may be read')
        if not re.search(r'(?i)(?:^|_)r'+str(n)+r'_',path.name):raise ValueError('Filename round mismatch')
        seen.add(path);actual=binding(path)
        if any(actual[k]!=entry[k]for k in('sha256','bytes')):raise ValueError('Frozen copy drift')
        refs.append(actual|dict(round=n,original_path=entry['path']))
        if path.suffix=='.json':
            if n in receipts:raise ValueError('Duplicate receipt')
            raw=path.read_text(encoding='utf-8');receipts[n]=parse_source(raw);literals[n]=parse_source(raw,True)
        elif path.suffix=='.py':
            if n in recipes:raise ValueError('Duplicate recipe')
            recipes[n]=path.read_text(encoding='utf-8')
        elif path.suffix!='.tsv':raise ValueError('Unexpected frozen input type')
    if set(receipts)!=set(BJ_ROUNDS)or set(recipes)!=set(BJ_ROUNDS)or any(sum(e['round']==n for e in refs)!=3 for n in BJ_ROUNDS):raise ValueError('Incomplete receipt/TSV/recipe triples')
    return receipts,literals,refs,recipes

def declared_context_bj(number,payload,arm,saved=None):
    if type(number)is not int or number not in BJ_ROUNDS:raise ValueError('Explicit current round required')
    d,c,s,a=BJ_TIMING[number];regime,flows,bidir=BJ_REGIMES[number]
    expected=dict(distance_m=d,coverage_class=c,slot_time_us=s,ack_timeout_us=a)
    knobs=arm.get('candidate_knobs')
    for obj in(payload,arm,knobs):
        if not isinstance(obj,dict):raise ValueError('Three source declaration objects required')
        for k,v in expected.items():
            if type(obj.get(k))is not int or obj[k]!=v:raise ValueError('Shared timing missing/conflicting/untyped')
        if obj.get('traffic_regime')!=regime or type(obj.get('active_flow_count'))is not int or obj['active_flow_count']!=flows or type(obj.get('bidirectional'))is not bool or obj['bidirectional']!=bidir:
            raise ValueError('Shared direction/flow/regime mismatch')
    for side in('ap','cpe'):
        state=knobs.get(side+'_state')
        if not isinstance(state,dict):raise ValueError('Endpoint states required')
        for k,v in expected.items():
            if k in state and(type(state[k])is not int or state[k]!=v):raise ValueError('Conflicting endpoint timing')
        if 'distance_meters'in state and(type(state['distance_meters'])is not int or state['distance_meters']!=d):raise ValueError('Conflicting endpoint distance')
    if saved is not None:
        if(saved['workload_regime'],saved['active_flow_count'],saved['bidirectional'],saved['distance_meters'],saved['coverage_class'])!=(regime,flows,bidir,d,c):raise ValueError('Normalized context differs')
        evidence=saved['certified_wds_evidence']
        if evidence.get('slot_time_us')!=s or evidence.get('ack_timeout_us')!=a or evidence.get('slot_ack_source')!='SHARED_PAYLOAD_TREATMENT_KNOBS':raise ValueError('Normalized slot/ACK provenance differs')
    return dict(**expected,workload_regime=regime,active_flow_count=flows,bidirectional=bidir,
        provenance='SHARED_PAYLOAD_TREATMENT_KNOBS',physical_distance_verified=False,effective_timing_independently_verified=False)

def unidirectional_alias_audit(number,payload):
    if type(number)is not int or number not in(81,82):raise ValueError('Only identified unidirectional current rounds')
    active='dl_goodput_mbps'if number==81 else'ul_goodput_mbps';inactive='ul_goodput_mbps'if number==81 else'dl_goodput_mbps'
    arms=payload.get('iterations')
    if not isinstance(arms,list)or len(arms)!=2:raise ValueError('Two identified arms required')
    checks=[]
    for arm in arms:
        declared_context_bj(number,payload,arm)
        rows=arm.get('repetition_blocks')
        if not isinstance(rows,list)or len(rows)!=16:raise ValueError('All16source blocks required')
        for label,obj,gp in [('arm',arm,arm.get('total_bidir_goodput_mbps'))]+[(f'block:{b.get("block_index")}',b,b.get('total_goodput_mbps'))for b in rows]:
            values=[obj.get(active),obj.get(inactive),gp]
            if any(type(v)not in(int,float)or not math.isfinite(v)for v in values):raise ValueError('Explicit finite typed directional throughput required')
            if values[0]!=gp or values[1]!=0:raise ValueError('Unidirectional activeGP identity/inactivezero failed')
            if 'observation'in obj:
                observation=obj['observation']
                if not isinstance(observation,dict)or type(observation.get('goodput_rx_mbps'))not in(int,float)or observation['goodput_rx_mbps']!=gp:
                    raise ValueError('Recorded duplicate observation GP conflicts')
            checks.append(dict(iteration=arm['commit'],source_unit=label,active_value=values[0],inactive_value=values[1],totalGP=gp,
                raw_directional_Jain=obj.get('bidir_jain_fairness'),raw_observation_present='observation'in obj,Jain_not_a_promoted_metric=True))
    return dict(status='EXACT_ACTIVE_DIRECTION_TOTAL_GP_ALIAS_VERIFIED',round_id=f'R{number}',active_metric=active,inactive_metric=inactive,
        semantic_alias_of='goodput_rx_mbps',same_hypothesis_not_duplicate=True,arms_checked=2,blocks_checked=32,source_units=checks,
        inapplicable_inference=['jain_fairness',inactive],selector_contract='Exact both-arm and every-block active=GP/inactive0 as _alias_valid')

def direction_recipe_audit_bj(number,text):
    tree=ast.parse(text);segments=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.JoinedStr):
            literal=''.join(v.value if isinstance(v,ast.Constant)and isinstance(v.value,str)else'{EXPR}'for v in node.values)
            for line in literal.splitlines():
                if line.strip().startswith('iperf3 -c')and' -t {EXPR}'in line:
                    segments.append(dict(line=node.lineno,parallel2=bool(re.search(r'-P\s+2\b',line)),parallel3=bool(re.search(r'-P\s+3\b',line)),reverse=bool(re.search(r'(?:^|\s)-R(?:\s|$)',line)),bidir='--bidir'in line))
    if number in(81,82):
        if len(segments)!=1 or not segments[0]['parallel2']or segments[0]['bidir']or segments[0]['reverse']!=(number==82):raise ValueError('Literal unidirectional iperf direction inconsistent')
    helpers=sorted({getattr(n.func,'id',getattr(n.func,'attr',''))for n in ast.walk(tree)if isinstance(n,ast.Call)and'bidir'in getattr(n.func,'id',getattr(n.func,'attr',''))})
    return dict(source_text_and_AST_only=True,direct_window_command_flags=segments,named_bidir_window_helpers=helpers,
        expected_workload=BJ_REGIMES[number][0],executed_or_effectively_read_back=False,
        limits='Imported helper implementation not executed; literal/named-call evidence is declaration, not current device behavior')


def pair_rows_bj(rows,control,target,metric):
    """Explicit R81..R86 validator; no global edits or relabeled old IDs."""
    if not isinstance(rows,list) or not rows:raise ValueError('Explicit crossed rows required')
    seen=set();rounds=set();groups=defaultdict(list)
    for row in rows:
        if row.get('round_id') not in {f'R{n}' for n in BJ_ROUNDS}:raise ValueError('Owned frozen R81..R86 only')
        rounds.add(row['round_id'])
        if any(type(row.get(k)) is not int or row[k]<0 for k in ('block_index','crossover_step')):raise ValueError('Genuine integer block/step IDs required')
        if not isinstance(row.get('treatment_id'),str) or not row['treatment_id']:raise ValueError('Treatment identity required')
        identity=(row['round_id'],row['block_index'],row['crossover_step'])
        if identity in seen:raise ValueError('Duplicate source identity')
        seen.add(identity);groups[row['block_index']].append(row)
    if len(rounds)!=1:raise ValueError('No mixed-round inference or pooling')
    number=int(next(iter(rounds))[1:])
    if metric not in metrics_bj(number):raise ValueError('Outcome is inapplicable to this direction; no duplicate or Jain inference')
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


def period_adjusted_estimation_bj(rows,control,target,metric):
    """Only the explicitly restricted no-differential-carryover point model."""
    pairs=pair_rows_bj(rows,control,target,metric)
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


def profile_conditions_bj(contrasts,utilities,aliases):
    result=[]
    for n in BJ_ROUNDS:
        required=(*METRICS[1:4],METRICS[0])if n in(81,82)else QOE
        own=[c for c in contrasts if c['scope']==f'R{n}'and c['metric']in required]
        if len(own)!=len(required):raise ValueError('All applicable distinct outcomes required')
        u=next(u for u in utilities if u['round_id']==f'R{n}')
        unanimous=all(c['favorable_blocks']==16 for c in own)
        stats=all(c['family_adjusted_p'][BJ_RANK_FAMILY]<=.05 and(c['HL_estimate']<0 if c['direction']=='lower'else c['HL_estimate']>0)for c in own)
        result.append(dict(round_id=f'R{n}',required_primary_metrics=list(required),
            semantic_GP_alias=next((a for a in aliases if a['round_id']==f'R{n}'),None),
            all_applicable_16of16=unanimous,applicable_direct_rank_HL_Holm500=stats,
            strict_observed_GP_loss_below2=Fraction(u['loss_percent_exact'])<2,
            necessary_observed_strict_conditions_met=unanimous and stats and Fraction(u['loss_percent_exact'])<2,
            failed_unanimity_metrics=[c['metric']for c in own if c['favorable_blocks']!=16],
            target_retry_lower=u['target_retry_lower'],controller_or_physical_acceptance=False))
    return result


def exact_effect_bj(differences):
    """BJ-specific facade; legacy exact engines remain immutable."""
    effect=exact_effect(differences)
    values=validated_differences(differences);nonzero=[v for v in values if v!=0]
    n=len(nonzero);positive=sum(v>0 for v in nonzero);k=min(positive,n-positive)
    tail=min(Fraction(1),Fraction(2*sum(math.comb(n,i)for i in range(k+1)),2**n))
    old=effect['exact_sign']['p_value']
    effect['exact_sign']={**effect['exact_sign'],'p_value':float(tail),'exact_binomial_fraction':str(tail),
        'legacy_float_p_value':old,'legacy_float_rounding_delta':old-float(tail),
        'method':'INTEGER_COMBINATORIAL_TWO_SIDED_SIGN_TAIL_ZEROS_EXCLUDED'}
    return effect


def raw_step_roundtrip_bj(number,arm,canonical_rows):
    """Source1/2 is not a new/guessed unit; only explicit81/82 map to0/1."""
    if type(number)is not int or number not in BJ_ROUNDS:raise ValueError('Explicit current source round required')
    checked=[];seen=set()
    for block in arm['repetition_blocks']:
        index=block.get('block_index')
        if type(index)is not int or index<0 or index in seen:raise ValueError('Genuine unique block identity required')
        seen.add(index)
        if number in(81,82):
            if 'crossover_step'in block or type(block.get('step_in_block'))is not int or block['step_in_block']not in(1,2):
                raise ValueError('Exclusive literal unidirectional source step1/2 required')
            original=block['step_in_block'];step=original-1;field='step_in_block'
        else:
            if 'step_in_block'in block or type(block.get('crossover_step'))is not int or block['crossover_step']not in(0,1):
                raise ValueError('Exclusive literal bidirectional source step0/1 required')
            original=step=block['crossover_step'];field='crossover_step'
        own=[r for r in canonical_rows if r.get('round_id')==f'R{number}'and r.get('treatment_id')==arm['commit']and r.get('block_index')==index]
        if len(own)!=1 or type(own[0].get('crossover_step'))is not int or own[0]['crossover_step']!=step:
            raise ValueError('Canonical source identity/period mapping differs')
        if number in(81,82)and(type(own[0].get('source_step_in_block'))is not int or own[0]['source_step_in_block']!=original
                or own[0].get('source_step_field')!='step_in_block'or own[0].get('crossover_step_mapping')!='EXPLICIT_ONE_BASED_SOURCE_MINUS_ONE'):
            raise ValueError('Original source step provenance missing')
        checked.append(dict(block_index=index,source_step_field=field,source_step_literal=original,crossover_step=step,
            exact_roundtrip=step+1==original if number in(81,82)else step==original))
    if len(checked)!=16:raise ValueError('All16source blocks required')
    return dict(status='EXACT_SOURCE_STEP_ROUNDTRIP',units=checked,source_unit_ids_not_generated=True)


def contextual_descriptions_bj(records):
    result=[]
    for label,numbers in(('four_flow_declared_distance_points',(64,83,84,86)),('six_flow_7500m_distinct_packages',(77,80,85))):
        points=[]
        for n in numbers:
            arms=sorted([r for r in records if r['round_id']==f'R{n}'],key=lambda r:r['iteration'])
            if len(arms)!=2:raise ValueError('Two explicit recorded contextual arms required')
            a,b=arms
            points.append(dict(round_id=f'R{n}',context=recorded_context(b),control_policy_id=a['policy_key'],target_policy_id=b['policy_key'],
                control_summary={k:a[k]for k in('goodput_mbps','dl_goodput_mbps','ul_goodput_mbps','p50_ms','p95_ms','p99_ms','jain_fairness')},
                target_summary={k:b[k]for k in('goodput_mbps','dl_goodput_mbps','ul_goodput_mbps','p50_ms','p95_ms','p99_ms','jain_fairness')},
                observed_utility=observed_utility(a['goodput_mbps'],b['goodput_mbps']),crossround_paired_units=False))
        anchor=points[0]
        for point in points[1:]:
            point['target_coordinates_different_from_first']=changed_coordinates(json.loads(anchor['target_policy_id']),json.loads(point['target_policy_id']))
            point['control_coordinates_different_from_first']=changed_coordinates(json.loads(anchor['control_policy_id']),json.loads(point['control_policy_id']))
        result.append(dict(label=label,points=points,interpretation='DESCRIPTIVE_HISTORICAL_CONTEXTS_NOT_COMMON_POLICY_CAUSAL_CURVE',
            no_crossround_pairing=True,no_physical_distance_or_interpolation_proof=True))
    return result


def _build_analysis_bj():
    from orchestration.autoresearch.fmx_live_dataset import load_all86_measurements,load_all86_block_observations
    names=('fmx_r43_to_r47_dyadic_zero_loss_audit','fmx_r48_to_r56_distance_goodput_dyadic_audit','fmx_r33_to_r42_exact_holm500_audit',
        'fmx_r27_to_r32_certified_wds_audit','fmx_r22_to_r26_crossover_audit','fmx_r16_to_r21_real_crossover_audit',
        'fmx_r15_and_crossover_statistical_audit','fmx_r10_to_r14_causal_and_power_analysis','fmx_r57_to_r60_retry64_goodput_parity_audit')
    dependencies=[Path(__file__),ROOT/'orchestration/autoresearch/fmx_live_dataset.py',ROOT/'orchestration/autoresearch/fmx_offline_data.py']+[ROOT/f'analysis/statistics/{n}.py'for n in names]
    deps=[binding(p)for p in dependencies]
    implementation=BJ_BASE/'wave_bj_implementation_freeze_2.json'
    frozen=json.loads(implementation.read_text(encoding='utf-8'))
    if frozen['source']!=binding(Path(__file__))or frozen['family_recipe']['sha256']!=BJ_FAMILY_SHA:raise ValueError('BJ implementation freeze must precede inference')
    receipts,literals,refs,recipes=frozen_inputs_bj();typed,_=load_all86_measurements();blocks=load_all86_block_observations()
    records=[record_dict(r)for r in typed];by_id={(r['round_id'],r['iteration']):r for r in records}
    new=[r for r in blocks['crossed']if int(r['round_id'][1:])in BJ_ROUNDS]
    counts=dict(records=len(records),primary=sum(r['window_kind']=='primary'for r in records),auxiliary=sum(r['window_kind']!='primary'for r in records),
        crossed=len(blocks['crossed']),matched=len({(r['round_id'],r['block_index'])for r in blocks['crossed']}),
        sequential=len(blocks['sequential']),new_arms=sum(len(r['iterations'])for r in receipts.values()),new_crossed=len(new),new_matched=len({(r['round_id'],r['block_index'])for r in new}))
    if counts!=dict(records=272,primary=270,auxiliary=2,crossed=1948,matched=886,sequential=16,new_arms=12,new_crossed=192,new_matched=96):raise ValueError('Actual272/1948/886+16 corpus required, not spec173')
    aliases=[unidirectional_alias_audit(n,receipts[n])for n in(81,82)]
    for alias in aliases:
        n=int(alias['round_id'][1:]);active=alias['active_metric'];inactive=alias['inactive_metric']
        arms=[r for r in records if r['round_id']==f'R{n}'];own=[b for b in new if b['round_id']==f'R{n}']
        if len(arms)!=2 or len(own)!=32 or not all(r[active]==r['goodput_mbps']and r[inactive]==0 for r in arms)or not all(b[active]==b['observation']['goodput_rx_mbps']and b[inactive]==0 for b in own):
            raise ValueError('Normalized unidirectional alias differs from frozen source identity')
        alias['normalized_arm_and_all_block_identity_verified']=True
    descriptions=[];utilities=[];designs=[];raw_pairs=[];contrasts=[]
    for n in BJ_ROUNDS:
        arms=receipts[n]['iterations']
        if len(arms)!=2:raise ValueError('Two current arms required')
        control,target=[a['commit']for a in arms];group=[r for r in new if r['round_id']==f'R{n}']
        for metric in metrics_bj(n):
            pairs=pair_rows_bj(group,control,target,metric)
            if len(pairs)!=16:raise ValueError('Exactly16identified matched pairs required')
            raw_pairs.append(dict(round_id=f'R{n}',metric=metric,pairs=pairs))
        for index,arm in enumerate(arms):
            saved=by_id[(f'R{n}',arm['commit'])];audit=source_arm_audit(n,arm,literals[n]['iterations'][index],saved)
            audit['declared_timing_context']=declared_context_bj(n,receipts[n],arm,saved)
            audit['recipe_direction']=direction_recipe_audit_bj(n,recipes[n]);audit['recipe_coverage_commands']=recipe_coverage_commands(recipes[n])
            audit['source_step_roundtrip']=raw_step_roundtrip_bj(n,arm,group)
            audit['per_block_station_counters']=[dict(block_index=b['block_index'],counter_interface=b['counter_interface'],packets=b['mac_tx_packets_delta'],retries=b['mac_tx_retries_delta'],rate_exact=str(retry_fraction(b)),independent_AP_or_peer_identity_verified=False)for b in group if b['treatment_id']==arm['commit']]
            descriptions.append(audit)
        a,b=[by_id[(f'R{n}',t)]for t in(control,target)];u=observed_utility(a['goodput_mbps'],b['goodput_mbps'])
        utilities.append(dict(round_id=f'R{n}',**u,control_retry_exact=str(Fraction(a['mac_tx_retries'],a['mac_tx_packets'])),target_retry_exact=str(Fraction(b['mac_tx_retries'],b['mac_tx_packets'])),
            target_retry_lower=Fraction(b['mac_tx_retries'],b['mac_tx_packets'])<Fraction(a['mac_tx_retries'],a['mac_tx_packets'])))
        d=multilevel_design_diagnostics(group)|dict(round_id=f'R{n}')
        d['schedule_agreement']=schedule_agreement(group,receipts[n]['crossover_schedule'],{'A':control,'B':target})
        d['interpretation']='Full current/period/lag alias retained; restricted model assumes no differential carryover, not separated causal effects.'
        designs.append(d)
    # Plot/raw descriptions precede the first exact/bootstrap result calculation.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(7,6,figsize=(20,20))
    for n in BJ_ROUNDS:
        for metric in METRICS:
            ax=axes[METRICS.index(metric),BJ_ROUNDS.index(n)]
            row=next((p for p in raw_pairs if p['round_id']==f'R{n}'and p['metric']==metric),None)
            if row is None:ax.text(.1,.5,'INAPPLICABLE; raw retained',fontsize=7);ax.set_axis_off();continue
            p=row['pairs'];ax.plot([x['block_index']for x in p],[x['control_mean']for x in p],'.-',label='Stock')
            ax.plot([x['block_index']for x in p],[x['treatment_mean']for x in p],'.-',label='Target')
            ax.set_title(f'R{n} '+metric,fontsize=7);ax.tick_params(labelsize=6)
    axes[0,0].legend();fig.suptitle('Frozen R81-R86 paired blocks; unidirectional aliases are one GP test')
    fig.tight_layout();plot=BJ_BASE/'wave_bj_paired_descriptives_2.png'
    if plot.exists():raise FileExistsError(plot)
    fig.savefig(plot,dpi=120);plt.close(fig)
    descpath=BJ_BASE/'wave_bj_preinference_descriptives_2.json'
    with descpath.open('x',encoding='utf-8',newline='\n')as f:json.dump(dict(status='CREATED_BEFORE_INFERENCE',source_inputs=refs,paired_values=raw_pairs,source_audits=descriptions,semantic_aliases=aliases,plot=binding(plot),assumptions=frozen['assumptions']),f,indent=2,allow_nan=False);f.write('\n')
    indices=bootstrap_indices(16)
    for n in BJ_ROUNDS:
        arms=receipts[n]['iterations'];control,target=[a['commit']for a in arms]
        group=[r for r in new if r['round_id']==f'R{n}'];literal_by={(a['commit'],b['block_index']):b for a in literals[n]['iterations']for b in a['repetition_blocks']}
        for metric in metrics_bj(n):
            pairs=next(x['pairs']for x in raw_pairs if x['round_id']==f'R{n}'and x['metric']==metric)
            differences=[p['difference']for p in pairs];effect=exact_effect_bj(differences);flips=exact_sign_flips(differences)
            if any(flips[k]['p_value']!=effect['exact_'+k]['p_value']for k in('rank','sign')):raise ValueError('Graycode and exactrankDP/binomial disagree')
            exact_source=[source_metric(literal_by[(target,p['block_index'])],metric)-source_metric(literal_by[(control,p['block_index'])],metric)for p in pairs]
            sensitivity=enumerate_fraction_flips(exact_source);a,b=[by_id[(f'R{n}',t)]for t in(control,target)]
            alias=next((x for x in aliases if x['round_id']==f'R{n}'),None)if metric=='goodput_rx_mbps'else None
            contrasts.append(dict(source_hypothesis_id=json.dumps([f'R{n}',control,target,metric],separators=(',',':')),scope=f'R{n}',control=control,target=target,
                control_policy_id=a['policy_key'],target_policy_id=b['policy_key'],regime=b['workload_regime'],metric=metric,direction='lower'if metric in LOWER else'higher',
                semantic_alias=None if alias is None else dict(active_metric=alias['active_metric'],alias_of='goodput_rx_mbps',same_hypothesis_not_duplicate=True,source_audit_round=f'R{n}'),
                paired_unit_ids=[dict(round_id=p['round_id'],block_index=p['block_index'])for p in pairs],pairs=pairs,
                favorable_blocks=sum(d<0 if metric in LOWER else d>0 for d in differences),equal_blocks=sum(d==0 for d in differences),quality=_quality(group),
                exact_sign_flips=flips,source_decimal_sensitivity=dict(literal_differences=[str(x)for x in exact_source],exact_flips=sensitivity,
                    rank_p_changed=sensitivity['rank']['p_value']!=flips['rank']['p_value'],mean_p_changed=sensitivity['mean']['p_value']!=flips['mean']['p_value']),
                period_adjusted=period_adjusted_estimation_bj(group,control,target,metric),paired_bca_HL=paired_bca_hl(differences,resample_indices=indices),**effect))
    priorpath=BASE/'wave_bf_eleven_distance_and_af_ablation_analysis.json'
    if binding(priorpath)['sha256']!='5dc0f81a9b3d734ebd3ef2ee0a33e6b8aca3ceedb89950716e25a3b2f61a4e63':raise ValueError('Prior accepted BF changed')
    prior=json.loads(priorpath.read_text(encoding='utf-8'))['families']['complete_known_rank980_bound980']['known_hypotheses']
    if len(prior)!=980 or len(contrasts)!=38:raise ValueError('Known980+38required')
    families={BJ_RANK_FAMILY:padded_family(contrasts,500,BJ_RANK_FAMILY),
        'complete_known_rank1018_bound1018':padded_family([dict(source_hypothesis_id=k,exact_rank=dict(p_value=p))for k,p in prior.items()]+contrasts,1018,'complete_known_rank1018_bound1018')}
    families[BJ_MEAN_FAMILY]=padded_family([dict(source_hypothesis_id='MEANFLIP:'+c['source_hypothesis_id'],exact_rank=dict(p_value=c['exact_sign_flips']['mean']['p_value']))for c in contrasts],500,BJ_MEAN_FAMILY)
    for c in contrasts:
        c['family_adjusted_p']={k:v['adjusted_p'][c['source_hypothesis_id']]for k,v in families.items()if c['source_hypothesis_id']in v['adjusted_p']}
        c['mean_flip_holm500_adjusted_p']=families[BJ_MEAN_FAMILY]['adjusted_p']['MEANFLIP:'+c['source_hypothesis_id']]
    inputs={k:binding(BJ_BASE/name)for k,name in dict(records='normalized_r1_to_r86_measurements_20261024.json',blocks='normalized_r16_to_r86_block_observations_20261024.json',manifest='inputs_manifest.json').items()}
    projection=[dict(source_hypothesis_id=c['source_hypothesis_id'],regime=c['regime'],target_policy_id=c['target_policy_id'],control_policy_id=c['control_policy_id'],
        round_ids=[c['scope']],paired_unit_ids=c['paired_unit_ids'],metric=c['metric'],direction=c['direction'],effect_hl=c['HL_estimate'],p_exact_rank=c['exact_rank']['p_value'],
        semantic_alias=c['semantic_alias'],holm500_adjusted_p=c['family_adjusted_p'][BJ_RANK_FAMILY],family500_key=BJ_RANK_FAMILY,
        comparability_status='WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON',statistic='PRIMARY_EXACT_SIGNED_RANK_NOT_MEAN_FLIP_OR_BCA')for c in contrasts]
    profiles=profile_conditions_bj(contrasts,utilities,aliases)
    claims=dict(spec173_total_refuted_by_actual=272,source_arms=12,source_block_windows=192,saved_RTTs=sum(d['received_pings']for d in descriptions),
        all48_fraction_means_exact=all(d['literal_mean_audit']['all_literal_equal']for d in descriptions),all48_zero_ULP=all(d['dyadic_audit']['all_zero_ulp']for d in descriptions),
        both_arm_saved_zero_loss_every_round=all(d['saved_loss_pct']==0 for d in descriptions),all12arms160received=all(d['complete_160_pings']for d in descriptions),
        all12chronological_RTT_pools=all(d['chronology_matches']for d in descriptions),all12MAC_pools_match=all(d['mac_sums_match']for d in descriptions),
        R85_requested_strict_claim=next(c for c in profiles if c['round_id']=='R85'),unidirectional_no_Jain_or_inactive_tests=True)
    if [binding(p)for p in dependencies]!=deps:raise ValueError('BJ numerical dependency drift')
    return dict(schema_version=2,status='OFFLINE_UNIDIRECTIONAL_AND_4FLOW_DISTANCE_AUDIT_PENDING_INDEPENDENT_ACCEPTANCE',counts=counts,
        software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
        sources=refs,source_inputs=inputs,numerical_dependencies=deps,family_plan=binding(BJ_BASE/'wave_bj_family_and_bootstrap_recipe.json'),implementation_freeze=binding(implementation),prior_unchanged_analysis=binding(priorpath),
        preinference_descriptives=binding(descpath),paired_plot=binding(plot),contrasts=contrasts,families=families,source_claim_audits=descriptions,observed_utility=utilities,
        unidirectional_semantic_aliases=aliases,source_claims=claims,applicable_strict_source_conditions=profiles,design_diagnostics=designs,
        contextual_descriptions=contextual_descriptions_bj(records),
        bootstrap_common_indices_sha256=hashlib.sha256(indices.astype('<i8').tobytes()).hexdigest(),
        catalog_scope=dict(primary_new_known=38,primary_prior_known=980,complete_primary_known=1018,complete_primary_Holm500='INAPPLICABLE_KNOWN1018_EXCEEDS500',mean_flip_family_separate=True,not_all_project_tests=True),
        promotion_evidence=dict(source_inputs={k+'_sha256':v['sha256']for k,v in inputs.items()},contrasts=projection,
            families={k:v for k,v in families.items()if k!=BJ_MEAN_FAMILY},unidirectional_aliases=aliases,evidence_only_not_promotion=True),
        automatic_execution_allowed=False,physical_or_causal_acceptance=False,
        limits=['96genuine paired block IDs are not1920independent physical trials; no crossround pairing.',
            'Unidirectional totalGP is one active-direction hypothesis only after exact arm/block identity and inactive0 proof. Jain/inactive raw values are retained, not inferred as QoE.',
            'All exact tests/sets are conditional on sign exchangeability and suitable symmetry/shift assumptions; no causal certification.',
            'BCa is approximate paired Monte Carlo sensitivity with explicit degeneracy, not a primary promotion gate.',
            'Declared slot/ACK/distance and recipe AST are not effective firmware timing or physical/outdoor range.',
            'Full current/period/lag alias remains; restricted period point estimates assume no differential carryover.',
            'Different round/workload/full AP+CPE packages do not establish isolated-knob superiority, noninferiority or an interpolated Cartesian curve.'])


def build_analysis_bj():
    """Explicit new-campaign builder; legacy BF entry point is preserved."""
    return _build_analysis_bj()


def main_campaign():
    """Require an explicit new campaign; retain historical default CLI scope."""
    import sys
    if '--campaign'not in sys.argv[1:]:return main()
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--campaign',choices=('BJ',),required=True)
    parser.add_argument('--output',type=Path,default=BJ_BASE/'wave_bj_unidir_and_multidistance_4flow_analysis.json')
    path=parser.parse_args().output.resolve()
    if path.parent!=BJ_BASE.resolve()or not path.name.startswith('wave_bj_')or path.suffix!='.json':raise ValueError('Owned BJ exclusive output only')
    if path.exists():raise FileExistsError(path)
    result=build_analysis_bj()
    with path.open('x',encoding='utf-8',newline='\n')as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=result['status'],contrasts=len(result['contrasts']),arms=len(result['source_claim_audits']))))


# Additive BN campaign. All preceding BF/BJ functions and historical defaults stay intact.
BN_BASE=ROOT/'artifacts/autoresearch/waves_bm_to_bp_20261024'
BN_ROUNDS=(87,88,89,90,91,92)
BN_TIMING={87:(100,0,9,18),88:(12000,27,90,180),89:(14000,31,102,204),90:(14000,31,102,204),91:(3000,6,27,54),92:(6000,13,48,96)}
BN_REGIMES={87:('unidir_dl_2flow',2,False),88:('bidir_4flow',4,True),89:('bidir_4flow',4,True),90:('bidir_6flow',6,True),91:('bidir_2flow',2,True),92:('bidir_2flow',2,True)}
BN_MANIFEST_SHA='c6ad60ddfdaf33cb0cf885fb28a46c63013dad06057ebcb37b385e1c5f9a0fb6'
BN_FAMILY_SHA='e4e18f7b5fb6583ccbc8ac21a31bb89f4bf9fe5b25134091bcfe6ba33ca20899'
BN_RANK_FAMILY='new_rank40_bound500'
BN_MEAN_FAMILY='new_meanflip40_bound500'


def metrics_bn(number):
    if type(number)is not int or number not in BN_ROUNDS:raise ValueError('Explicit owned R87..R92 required')
    return (*METRICS[:4],METRICS[-1])if number in(87,)else METRICS

def frozen_inputs_bn():
    if binding(BN_BASE/'inputs_manifest.json')['sha256']!=BN_MANIFEST_SHA:raise ValueError('Frozen BN manifest changed')
    if binding(BN_BASE/'wave_bn_family_and_bootstrap_recipe.json')['sha256']!=BN_FAMILY_SHA:raise ValueError('Frozen BN family changed')
    entries=json.loads((BN_BASE/'inputs_manifest.json').read_text(encoding='utf-8'))['entries']
    if len(entries)!=18:raise ValueError('Require18frozen copies')
    receipts={};literals={};recipes={};refs=[];seen=set()
    for entry in entries:
        n=entry.get('round');original=Path(entry.get('path',''));path=(ROOT/entry.get('copy','')).resolve()
        if type(n)is not int or n not in BN_ROUNDS or original.is_absolute()or'..'in original.parts:
            raise ValueError('Only explicit current frozen identities')
        if path!=(BN_BASE/'inputs'/original).resolve()or not path.is_relative_to((BN_BASE/'inputs').resolve())or path in seen:
            raise ValueError('Only exact owned frozen copies may be read')
        if not re.search(r'(?i)(?:^|_)r'+str(n)+r'_',path.name):raise ValueError('Filename round mismatch')
        seen.add(path);actual=binding(path)
        if any(actual[k]!=entry[k]for k in('sha256','bytes')):raise ValueError('Frozen copy drift')
        refs.append(actual|dict(round=n,original_path=entry['path']))
        if path.suffix=='.json':
            if n in receipts:raise ValueError('Duplicate receipt')
            raw=path.read_text(encoding='utf-8');receipts[n]=parse_source(raw);literals[n]=parse_source(raw,True)
        elif path.suffix=='.py':
            if n in recipes:raise ValueError('Duplicate recipe')
            recipes[n]=path.read_text(encoding='utf-8')
        elif path.suffix!='.tsv':raise ValueError('Unexpected frozen input type')
    if set(receipts)!=set(BN_ROUNDS)or set(recipes)!=set(BN_ROUNDS)or any(sum(e['round']==n for e in refs)!=3 for n in BN_ROUNDS):raise ValueError('Incomplete receipt/TSV/recipe triples')
    return receipts,literals,refs,recipes

def declared_context_bn(number,payload,arm,saved=None):
    if type(number)is not int or number not in BN_ROUNDS:raise ValueError('Explicit current round required')
    d,c,s,a=BN_TIMING[number];regime,flows,bidir=BN_REGIMES[number]
    expected=dict(distance_m=d,coverage_class=c,slot_time_us=s,ack_timeout_us=a)
    knobs=arm.get('candidate_knobs')
    for obj in(payload,arm,knobs):
        if not isinstance(obj,dict):raise ValueError('Three source declaration objects required')
        for k,v in expected.items():
            if type(obj.get(k))is not int or obj[k]!=v:raise ValueError('Shared timing missing/conflicting/untyped')
        if obj.get('traffic_regime')!=regime or type(obj.get('active_flow_count'))is not int or obj['active_flow_count']!=flows or type(obj.get('bidirectional'))is not bool or obj['bidirectional']!=bidir:
            raise ValueError('Shared direction/flow/regime mismatch')
    for side in('ap','cpe'):
        state=knobs.get(side+'_state')
        if not isinstance(state,dict):raise ValueError('Endpoint states required')
        for k,v in expected.items():
            if k in state and(type(state[k])is not int or state[k]!=v):raise ValueError('Conflicting endpoint timing')
        if 'distance_meters'in state and(type(state['distance_meters'])is not int or state['distance_meters']!=d):raise ValueError('Conflicting endpoint distance')
    if saved is not None:
        if(saved['workload_regime'],saved['active_flow_count'],saved['bidirectional'],saved['distance_meters'],saved['coverage_class'])!=(regime,flows,bidir,d,c):raise ValueError('Normalized context differs')
        evidence=saved['certified_wds_evidence']
        if evidence.get('slot_time_us')!=s or evidence.get('ack_timeout_us')!=a or evidence.get('slot_ack_source')!='SHARED_PAYLOAD_TREATMENT_KNOBS':raise ValueError('Normalized slot/ACK provenance differs')
    return dict(**expected,workload_regime=regime,active_flow_count=flows,bidirectional=bidir,
        provenance='SHARED_PAYLOAD_TREATMENT_KNOBS',physical_distance_verified=False,effective_timing_independently_verified=False)

def unidirectional_alias_audit_bn(number,payload):
    if type(number)is not int or number not in(87,):raise ValueError('Only identified unidirectional current rounds')
    active='dl_goodput_mbps'if number==87 else'ul_goodput_mbps';inactive='ul_goodput_mbps'if number==87 else'dl_goodput_mbps'
    arms=payload.get('iterations')
    if not isinstance(arms,list)or len(arms)!=2:raise ValueError('Two identified arms required')
    checks=[]
    for arm in arms:
        declared_context_bn(number,payload,arm)
        rows=arm.get('repetition_blocks')
        if not isinstance(rows,list)or len(rows)!=16:raise ValueError('All16source blocks required')
        for label,obj,gp in [('arm',arm,arm.get('total_bidir_goodput_mbps'))]+[(f'block:{b.get("block_index")}',b,b.get('total_goodput_mbps'))for b in rows]:
            values=[obj.get(active),obj.get(inactive),gp]
            if any(type(v)not in(int,float)or not math.isfinite(v)for v in values):raise ValueError('Explicit finite typed directional throughput required')
            if values[0]!=gp or values[1]!=0:raise ValueError('Unidirectional activeGP identity/inactivezero failed')
            if 'observation'in obj:
                observation=obj['observation']
                if not isinstance(observation,dict)or type(observation.get('goodput_rx_mbps'))not in(int,float)or observation['goodput_rx_mbps']!=gp:
                    raise ValueError('Recorded duplicate observation GP conflicts')
            checks.append(dict(iteration=arm['commit'],source_unit=label,active_value=values[0],inactive_value=values[1],totalGP=gp,
                raw_directional_Jain=obj.get('bidir_jain_fairness'),raw_observation_present='observation'in obj,Jain_not_a_promoted_metric=True))
    return dict(status='EXACT_ACTIVE_DIRECTION_TOTAL_GP_ALIAS_VERIFIED',round_id=f'R{number}',active_metric=active,inactive_metric=inactive,
        semantic_alias_of='goodput_rx_mbps',same_hypothesis_not_duplicate=True,arms_checked=2,blocks_checked=32,source_units=checks,
        inapplicable_inference=['jain_fairness',inactive],selector_contract='Exact both-arm and every-block active=GP/inactive0 as _alias_valid')

def direction_recipe_audit_bn(number,text):
    if type(number)is not int or number not in BN_ROUNDS:raise ValueError('Explicit owned round required')
    tree=ast.parse(text)
    if number!=87:
        helpers=sorted({getattr(n.func,'id',getattr(n.func,'attr',''))for n in ast.walk(tree)if isinstance(n,ast.Call)and'bidir'in getattr(n.func,'id',getattr(n.func,'attr',''))})
        return dict(source_text_and_AST_only=True,direct_window_command_flags=[],named_bidir_window_helpers=helpers,
            expected_workload=BN_REGIMES[number][0],executed_or_effectively_read_back=False,
            limits='Named helper/recipe declarations only; no executed direction or hardware proof')
    # R87 delegates its actual window to the unchanged, authenticated R81 copy.
    name='run_single_5s_unidir_dl_2flow_dyadic'
    manifest=json.loads((BJ_BASE/'inputs_manifest.json').read_text(encoding='utf-8'))
    if binding(BJ_BASE/'inputs_manifest.json')['sha256']!=BJ_MANIFEST_SHA:raise ValueError('Prior frozen helper manifest changed')
    entry=next(e for e in manifest['entries']if e['round']==81 and Path(e['path']).suffix=='.py')
    module=entry['path'].removesuffix('.py').replace('/','.')
    imports=[n for n in ast.walk(tree)if isinstance(n,ast.ImportFrom)and n.module==module and any(x.name==name and x.asname in(None,name)for x in n.names)]
    calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id==name]
    if len(imports)!=1 or len(calls)!=1:raise ValueError('Exact frozen R81 import and one window call required')
    duration=[x.value for x in calls[0].keywords if x.arg=='duration_sec']
    if len(duration)!=1 or not isinstance(duration[0],ast.Constant)or type(duration[0].value)is not int or duration[0].value!=5:
        raise ValueError('Explicit five-second source window required')
    frozen=(ROOT/entry['copy']).resolve()
    if frozen!=(BJ_BASE/'inputs'/entry['path']).resolve()or not frozen.is_relative_to((BJ_BASE/'inputs').resolve()):raise ValueError('Only frozen prior helper copy')
    actual=binding(frozen)
    if any(actual[k]!=entry[k]for k in('sha256','bytes')):raise ValueError('Frozen prior helper drift')
    prior=direction_recipe_audit_bj(81,frozen.read_text(encoding='utf-8'))
    return prior|dict(direction_evidence='EXACT_NAMED_CALL_TO_PRIOR_FROZEN_R81_WINDOW',frozen_helper_source=actual,
        current_import_line=imports[0].lineno,current_call_line=calls[0].lineno,declared_duration_seconds=5,
        expected_workload=BN_REGIMES[number][0],executed_or_effectively_read_back=False,
        limits='Exact imported/called source and frozen prior command AST only; no recipe import/execution or current firmware behavior proof')

def pair_rows_bn(rows,control,target,metric):
    """Explicit R87..R92 validator; no global edits or relabeled old IDs."""
    if not isinstance(rows,list) or not rows:raise ValueError('Explicit crossed rows required')
    seen=set();rounds=set();groups=defaultdict(list)
    for row in rows:
        if row.get('round_id') not in {f'R{n}' for n in BN_ROUNDS}:raise ValueError('Owned frozen R87..R92 only')
        rounds.add(row['round_id'])
        if any(type(row.get(k)) is not int or row[k]<0 for k in ('block_index','crossover_step')):raise ValueError('Genuine integer block/step IDs required')
        if not isinstance(row.get('treatment_id'),str) or not row['treatment_id']:raise ValueError('Treatment identity required')
        identity=(row['round_id'],row['block_index'],row['crossover_step'])
        if identity in seen:raise ValueError('Duplicate source identity')
        seen.add(identity);groups[row['block_index']].append(row)
    if len(rounds)!=1:raise ValueError('No mixed-round inference or pooling')
    number=int(next(iter(rounds))[1:])
    if metric not in metrics_bn(number):raise ValueError('Outcome is inapplicable to this direction; no duplicate or Jain inference')
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

def period_adjusted_estimation_bn(rows,control,target,metric):
    """Only the explicitly restricted no-differential-carryover point model."""
    pairs=pair_rows_bn(rows,control,target,metric)
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

def profile_conditions_bn(contrasts,utilities,aliases):
    result=[]
    for n in BN_ROUNDS:
        required=(*METRICS[1:4],METRICS[0])if n in(87,)else QOE
        own=[c for c in contrasts if c['scope']==f'R{n}'and c['metric']in required]
        if len(own)!=len(required):raise ValueError('All applicable distinct outcomes required')
        u=next(u for u in utilities if u['round_id']==f'R{n}')
        unanimous=all(c['favorable_blocks']==16 for c in own)
        stats=all(c['family_adjusted_p'][BN_RANK_FAMILY]<=.05 and(c['HL_estimate']<0 if c['direction']=='lower'else c['HL_estimate']>0)for c in own)
        result.append(dict(round_id=f'R{n}',required_primary_metrics=list(required),
            semantic_GP_alias=next((a for a in aliases if a['round_id']==f'R{n}'),None),
            all_applicable_16of16=unanimous,applicable_direct_rank_HL_Holm500=stats,
            strict_observed_GP_loss_below2=Fraction(u['loss_percent_exact'])<2,
            necessary_observed_strict_conditions_met=unanimous and stats and Fraction(u['loss_percent_exact'])<2,
            failed_unanimity_metrics=[c['metric']for c in own if c['favorable_blocks']!=16],
            target_retry_lower=u['target_retry_lower'],controller_or_physical_acceptance=False))
    return result

def raw_step_roundtrip_bn(number,arm,canonical_rows):
    """Source1/2 is not a new/guessed unit; only explicit81/82 map to0/1."""
    if type(number)is not int or number not in BN_ROUNDS:raise ValueError('Explicit current source round required')
    checked=[];seen=set()
    for block in arm['repetition_blocks']:
        index=block.get('block_index')
        if type(index)is not int or index<0 or index in seen:raise ValueError('Genuine unique block identity required')
        seen.add(index)
        if number in(87,):
            if 'crossover_step'in block or type(block.get('step_in_block'))is not int or block['step_in_block']not in(1,2):
                raise ValueError('Exclusive literal unidirectional source step1/2 required')
            original=block['step_in_block'];step=original-1;field='step_in_block'
        else:
            if 'step_in_block'in block or type(block.get('crossover_step'))is not int or block['crossover_step']not in(0,1):
                raise ValueError('Exclusive literal bidirectional source step0/1 required')
            original=step=block['crossover_step'];field='crossover_step'
        own=[r for r in canonical_rows if r.get('round_id')==f'R{number}'and r.get('treatment_id')==arm['commit']and r.get('block_index')==index]
        if len(own)!=1 or type(own[0].get('crossover_step'))is not int or own[0]['crossover_step']!=step:
            raise ValueError('Canonical source identity/period mapping differs')
        if number in(87,)and(type(own[0].get('source_step_in_block'))is not int or own[0]['source_step_in_block']!=original
                or own[0].get('source_step_field')!='step_in_block'or own[0].get('crossover_step_mapping')!='EXPLICIT_ONE_BASED_SOURCE_MINUS_ONE'):
            raise ValueError('Original source step provenance missing')
        checked.append(dict(block_index=index,source_step_field=field,source_step_literal=original,crossover_step=step,
            exact_roundtrip=step+1==original if number in(87,)else step==original))
    if len(checked)!=16:raise ValueError('All16source blocks required')
    return dict(status='EXACT_SOURCE_STEP_ROUNDTRIP',units=checked,source_unit_ids_not_generated=True)

def contextual_descriptions_bn(records):
    result=[]
    groups=(('pureDL_observed_packages',(81,87)),('four_flow_declared_distance_points',(64,83,84,86,88,89)),
        ('six_flow_declared_distance_points',(60,61,70,62,69,73,75,85,90)),('two_flow_bidir_declared_points',(66,71,91,92)))
    for label,numbers in groups:
        points=[]
        for n in numbers:
            arms=sorted([r for r in records if r['round_id']==f'R{n}'],key=lambda r:r['iteration'])
            if len(arms)!=2:raise ValueError('Two exact historical/current arms required')
            a,b=arms
            points.append(dict(round_id=f'R{n}',context=recorded_context(b),control_policy_id=a['policy_key'],target_policy_id=b['policy_key'],
                control_summary={k:a[k]for k in('goodput_mbps','dl_goodput_mbps','ul_goodput_mbps','p50_ms','p95_ms','p99_ms','jain_fairness')},
                target_summary={k:b[k]for k in('goodput_mbps','dl_goodput_mbps','ul_goodput_mbps','p50_ms','p95_ms','p99_ms','jain_fairness')},
                observed_utility=observed_utility(a['goodput_mbps'],b['goodput_mbps']),crossround_paired_units=False))
        for point in points[1:]:
            point['target_coordinates_different_from_first']=changed_coordinates(json.loads(points[0]['target_policy_id']),json.loads(point['target_policy_id']))
            point['control_coordinates_different_from_first']=changed_coordinates(json.loads(points[0]['control_policy_id']),json.loads(point['control_policy_id']))
        result.append(dict(label=label,points=points,interpretation='DESCRIPTIVE_DECLARED_CONTEXTS_NOT_COMMON_POLICY_CAUSAL_CURVE',
            no_crossround_pairing=True,no_physical_distance_or_interpolation_proof=True))
    return result


def coverage_policy_audit_bn(number,context):
    if type(number)is not int or number not in BN_ROUNDS:raise ValueError('Explicit owned round required')
    expected=BN_TIMING[number]
    values=tuple(context.get(k)for k in('distance_m','coverage_class','slot_time_us','ack_timeout_us'))
    if any(type(v)is not int for v in values)or values!=expected:raise ValueError('Exact declared context required, no signed coercion')
    if context.get('physical_distance_verified')is not False or context.get('effective_timing_independently_verified')is not False:raise ValueError('Declared source is not qualified physical/readback proof')
    return dict(round_id=f'R{number}',declared_context=context,requested_advice_policy_max=31,
        inside_requested_advice_policy=0<=values[1]<=31,silicon_or_installed_build_ceiling_verified=False,
        policy_not_hardware_limit=True,source_evidence=binding(BN_BASE/'timing_policy_source_evidence.json'))


def _build_analysis_bn():
    from orchestration.autoresearch.fmx_live_dataset import load_all92_measurements,load_all92_block_observations
    names=('fmx_r43_to_r47_dyadic_zero_loss_audit','fmx_r48_to_r56_distance_goodput_dyadic_audit','fmx_r33_to_r42_exact_holm500_audit',
        'fmx_r27_to_r32_certified_wds_audit','fmx_r22_to_r26_crossover_audit','fmx_r16_to_r21_real_crossover_audit',
        'fmx_r15_and_crossover_statistical_audit','fmx_r10_to_r14_causal_and_power_analysis','fmx_r57_to_r60_retry64_goodput_parity_audit')
    dependencies=[Path(__file__),ROOT/'orchestration/autoresearch/fmx_live_dataset.py',ROOT/'orchestration/autoresearch/fmx_offline_data.py']+[ROOT/f'analysis/statistics/{n}.py'for n in names]
    deps=[binding(p)for p in dependencies]
    implementation=BN_BASE/'wave_bn_implementation_freeze_3.json'
    frozen=json.loads(implementation.read_text(encoding='utf-8'))
    if frozen['source']!=binding(Path(__file__))or frozen['family_recipe']['sha256']!=BN_FAMILY_SHA:raise ValueError('BJ implementation freeze must precede inference')
    receipts,literals,refs,recipes=frozen_inputs_bn();typed,_=load_all92_measurements();blocks=load_all92_block_observations()
    records=[record_dict(r)for r in typed];by_id={(r['round_id'],r['iteration']):r for r in records}
    new=[r for r in blocks['crossed']if int(r['round_id'][1:])in BN_ROUNDS]
    counts=dict(records=len(records),primary=sum(r['window_kind']=='primary'for r in records),auxiliary=sum(r['window_kind']!='primary'for r in records),
        crossed=len(blocks['crossed']),matched=len({(r['round_id'],r['block_index'])for r in blocks['crossed']}),
        sequential=len(blocks['sequential']),new_arms=sum(len(r['iterations'])for r in receipts.values()),new_crossed=len(new),new_matched=len({(r['round_id'],r['block_index'])for r in new}))
    if counts!=dict(records=284,primary=282,auxiliary=2,crossed=2140,matched=982,sequential=16,new_arms=12,new_crossed=192,new_matched=96):raise ValueError('Actual284/2140/982+16 corpus required, not spec185')
    aliases=[unidirectional_alias_audit_bn(n,receipts[n])for n in(87,)]
    for alias in aliases:
        n=int(alias['round_id'][1:]);active=alias['active_metric'];inactive=alias['inactive_metric']
        arms=[r for r in records if r['round_id']==f'R{n}'];own=[b for b in new if b['round_id']==f'R{n}']
        if len(arms)!=2 or len(own)!=32 or not all(r[active]==r['goodput_mbps']and r[inactive]==0 for r in arms)or not all(b[active]==b['observation']['goodput_rx_mbps']and b[inactive]==0 for b in own):
            raise ValueError('Normalized unidirectional alias differs from frozen source identity')
        alias['normalized_arm_and_all_block_identity_verified']=True
    descriptions=[];utilities=[];designs=[];raw_pairs=[];contrasts=[]
    for n in BN_ROUNDS:
        arms=receipts[n]['iterations']
        if len(arms)!=2:raise ValueError('Two current arms required')
        control,target=[a['commit']for a in arms];group=[r for r in new if r['round_id']==f'R{n}']
        for metric in metrics_bn(n):
            pairs=pair_rows_bn(group,control,target,metric)
            if len(pairs)!=16:raise ValueError('Exactly16identified matched pairs required')
            raw_pairs.append(dict(round_id=f'R{n}',metric=metric,pairs=pairs))
        for index,arm in enumerate(arms):
            saved=by_id[(f'R{n}',arm['commit'])];audit=source_arm_audit(n,arm,literals[n]['iterations'][index],saved)
            audit['declared_timing_context']=declared_context_bn(n,receipts[n],arm,saved)
            audit['recipe_direction']=direction_recipe_audit_bn(n,recipes[n]);audit['recipe_coverage_commands']=recipe_coverage_commands(recipes[n])
            audit['source_step_roundtrip']=raw_step_roundtrip_bn(n,arm,group)
            audit['per_block_station_counters']=[dict(block_index=b['block_index'],counter_interface=b['counter_interface'],packets=b['mac_tx_packets_delta'],retries=b['mac_tx_retries_delta'],rate_exact=str(retry_fraction(b)),independent_AP_or_peer_identity_verified=False)for b in group if b['treatment_id']==arm['commit']]
            descriptions.append(audit)
        a,b=[by_id[(f'R{n}',t)]for t in(control,target)];u=observed_utility(a['goodput_mbps'],b['goodput_mbps'])
        utilities.append(dict(round_id=f'R{n}',**u,control_retry_exact=str(Fraction(a['mac_tx_retries'],a['mac_tx_packets'])),target_retry_exact=str(Fraction(b['mac_tx_retries'],b['mac_tx_packets'])),
            target_retry_lower=Fraction(b['mac_tx_retries'],b['mac_tx_packets'])<Fraction(a['mac_tx_retries'],a['mac_tx_packets'])))
        d=multilevel_design_diagnostics(group)|dict(round_id=f'R{n}')
        d['schedule_agreement']=schedule_agreement(group,receipts[n]['crossover_schedule'],{'A':control,'B':target})
        d['interpretation']='Full current/period/lag alias retained; restricted model assumes no differential carryover, not separated causal effects.'
        designs.append(d)
    # Plot/raw descriptions precede the first exact/bootstrap result calculation.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(7,6,figsize=(20,20))
    for n in BN_ROUNDS:
        for metric in METRICS:
            ax=axes[METRICS.index(metric),BN_ROUNDS.index(n)]
            row=next((p for p in raw_pairs if p['round_id']==f'R{n}'and p['metric']==metric),None)
            if row is None:ax.text(.1,.5,'INAPPLICABLE; raw retained',fontsize=7);ax.set_axis_off();continue
            p=row['pairs'];ax.plot([x['block_index']for x in p],[x['control_mean']for x in p],'.-',label='Stock')
            ax.plot([x['block_index']for x in p],[x['treatment_mean']for x in p],'.-',label='Target')
            ax.set_title(f'R{n} '+metric,fontsize=7);ax.tick_params(labelsize=6)
    axes[0,0].legend();fig.suptitle('Frozen R87-R92 paired blocks; unidirectional aliases are one GP test')
    fig.tight_layout();plot=BN_BASE/'wave_bn_paired_descriptives_3.png'
    if plot.exists():raise FileExistsError(plot)
    fig.savefig(plot,dpi=120);plt.close(fig)
    descpath=BN_BASE/'wave_bn_preinference_descriptives_3.json'
    with descpath.open('x',encoding='utf-8',newline='\n')as f:json.dump(dict(status='CREATED_BEFORE_INFERENCE',source_inputs=refs,paired_values=raw_pairs,source_audits=descriptions,semantic_aliases=aliases,plot=binding(plot),assumptions=frozen['assumptions']),f,indent=2,allow_nan=False);f.write('\n')
    indices=bootstrap_indices(16)
    for n in BN_ROUNDS:
        arms=receipts[n]['iterations'];control,target=[a['commit']for a in arms]
        group=[r for r in new if r['round_id']==f'R{n}'];literal_by={(a['commit'],b['block_index']):b for a in literals[n]['iterations']for b in a['repetition_blocks']}
        for metric in metrics_bn(n):
            pairs=next(x['pairs']for x in raw_pairs if x['round_id']==f'R{n}'and x['metric']==metric)
            differences=[p['difference']for p in pairs];effect=exact_effect_bj(differences);flips=exact_sign_flips(differences)
            if any(flips[k]['p_value']!=effect['exact_'+k]['p_value']for k in('rank','sign')):raise ValueError('Graycode and exactrankDP/binomial disagree')
            exact_source=[source_metric(literal_by[(target,p['block_index'])],metric)-source_metric(literal_by[(control,p['block_index'])],metric)for p in pairs]
            sensitivity=enumerate_fraction_flips(exact_source);a,b=[by_id[(f'R{n}',t)]for t in(control,target)]
            alias=next((x for x in aliases if x['round_id']==f'R{n}'),None)if metric=='goodput_rx_mbps'else None
            contrasts.append(dict(source_hypothesis_id=json.dumps([f'R{n}',control,target,metric],separators=(',',':')),scope=f'R{n}',control=control,target=target,
                control_policy_id=a['policy_key'],target_policy_id=b['policy_key'],regime=b['workload_regime'],metric=metric,direction='lower'if metric in LOWER else'higher',
                semantic_alias=None if alias is None else dict(active_metric=alias['active_metric'],alias_of='goodput_rx_mbps',same_hypothesis_not_duplicate=True,source_audit_round=f'R{n}'),
                paired_unit_ids=[dict(round_id=p['round_id'],block_index=p['block_index'])for p in pairs],pairs=pairs,
                favorable_blocks=sum(d<0 if metric in LOWER else d>0 for d in differences),equal_blocks=sum(d==0 for d in differences),quality=_quality(group),
                exact_sign_flips=flips,source_decimal_sensitivity=dict(literal_differences=[str(x)for x in exact_source],exact_flips=sensitivity,
                    rank_p_changed=sensitivity['rank']['p_value']!=flips['rank']['p_value'],mean_p_changed=sensitivity['mean']['p_value']!=flips['mean']['p_value']),
                period_adjusted=period_adjusted_estimation_bn(group,control,target,metric),paired_bca_HL=paired_bca_hl(differences,resample_indices=indices),**effect))
    priorpath=BJ_BASE/'wave_bj_unidir_and_multidistance_4flow_analysis.json'
    if binding(priorpath)['sha256']!='ab315b959b0e75e1fca88b3abc096df0a73afc50082215f3b0ef347ff37da4df':raise ValueError('Prior accepted BJ changed')
    prior=json.loads(priorpath.read_text(encoding='utf-8'))['families']['complete_known_rank1018_bound1018']['known_hypotheses']
    if len(prior)!=1018 or len(contrasts)!=40:raise ValueError('Known1018+40required')
    families={BN_RANK_FAMILY:padded_family(contrasts,500,BN_RANK_FAMILY),
        'complete_known_rank1058_bound1058':padded_family([dict(source_hypothesis_id=k,exact_rank=dict(p_value=p))for k,p in prior.items()]+contrasts,1058,'complete_known_rank1058_bound1058')}
    families[BN_MEAN_FAMILY]=padded_family([dict(source_hypothesis_id='MEANFLIP:'+c['source_hypothesis_id'],exact_rank=dict(p_value=c['exact_sign_flips']['mean']['p_value']))for c in contrasts],500,BN_MEAN_FAMILY)
    for c in contrasts:
        c['family_adjusted_p']={k:v['adjusted_p'][c['source_hypothesis_id']]for k,v in families.items()if c['source_hypothesis_id']in v['adjusted_p']}
        c['mean_flip_holm500_adjusted_p']=families[BN_MEAN_FAMILY]['adjusted_p']['MEANFLIP:'+c['source_hypothesis_id']]
    inputs={k:binding(BN_BASE/name)for k,name in dict(records='normalized_r1_to_r92_measurements_20261024.json',blocks='normalized_r16_to_r92_block_observations_20261024.json',manifest='inputs_manifest.json').items()}
    projection=[dict(source_hypothesis_id=c['source_hypothesis_id'],regime=c['regime'],target_policy_id=c['target_policy_id'],control_policy_id=c['control_policy_id'],
        round_ids=[c['scope']],paired_unit_ids=c['paired_unit_ids'],metric=c['metric'],direction=c['direction'],effect_hl=c['HL_estimate'],p_exact_rank=c['exact_rank']['p_value'],
        semantic_alias=c['semantic_alias'],holm500_adjusted_p=c['family_adjusted_p'][BN_RANK_FAMILY],family500_key=BN_RANK_FAMILY,
        comparability_status='WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON',statistic='PRIMARY_EXACT_SIGNED_RANK_NOT_MEAN_FLIP_OR_BCA')for c in contrasts]
    profiles=profile_conditions_bn(contrasts,utilities,aliases)
    claims=dict(spec185_total_refuted_by_actual=284,source_arms=12,source_block_windows=192,saved_RTTs=sum(d['received_pings']for d in descriptions),
        all48_fraction_means_exact=all(d['literal_mean_audit']['all_literal_equal']for d in descriptions),all48_zero_ULP=all(d['dyadic_audit']['all_zero_ulp']for d in descriptions),
        both_arm_saved_zero_loss_every_round=all(d['saved_loss_pct']==0 for d in descriptions),all12arms160received=all(d['complete_160_pings']for d in descriptions),
        all12chronological_RTT_pools=all(d['chronology_matches']for d in descriptions),all12MAC_pools_match=all(d['mac_sums_match']for d in descriptions),
        requested_strict_conditions=profiles,unidirectional_no_Jain_or_inactive_tests=True)
    if [binding(p)for p in dependencies]!=deps:raise ValueError('BJ numerical dependency drift')
    return dict(schema_version=2,status='OFFLINE_PURE_DL_COVCLASS31_AND_CONTEXT_MATRIX_AUDIT_PENDING_INDEPENDENT_ACCEPTANCE',counts=counts,
        software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
        sources=refs,source_inputs=inputs,numerical_dependencies=deps,family_plan=binding(BN_BASE/'wave_bn_family_and_bootstrap_recipe.json'),implementation_freeze=binding(implementation),prior_unchanged_analysis=binding(priorpath),
        preinference_descriptives=binding(descpath),paired_plot=binding(plot),contrasts=contrasts,families=families,source_claim_audits=descriptions,observed_utility=utilities,
        unidirectional_semantic_aliases=aliases,source_claims=claims,applicable_strict_source_conditions=profiles,design_diagnostics=designs,
        contextual_descriptions=contextual_descriptions_bn(records),coverage_policy_audits=[coverage_policy_audit_bn(n,declared_context_bn(n,receipts[n],receipts[n]['iterations'][0]))for n in BN_ROUNDS],
        bootstrap_common_indices_sha256=hashlib.sha256(indices.astype('<i8').tobytes()).hexdigest(),
        catalog_scope=dict(primary_new_known=40,primary_prior_known=1018,complete_primary_known=1058,complete_primary_Holm500='INAPPLICABLE_KNOWN1058_EXCEEDS500',mean_flip_family_separate=True,not_all_project_tests=True),
        promotion_evidence=dict(source_inputs={k+'_sha256':v['sha256']for k,v in inputs.items()},contrasts=projection,
            families={k:v for k,v in families.items()if k!=BN_MEAN_FAMILY},unidirectional_aliases=aliases,evidence_only_not_promotion=True),
        automatic_execution_allowed=False,physical_or_causal_acceptance=False,
        limits=['96genuine paired block IDs are not1920independent physical trials; no crossround pairing.',
            'Unidirectional totalGP is one active-direction hypothesis only after exact arm/block identity and inactive0 proof. Jain/inactive raw values are retained, not inferred as QoE.',
            'All exact tests/sets are conditional on sign exchangeability and suitable symmetry/shift assumptions; no causal certification.',
            'BCa is approximate paired Monte Carlo sensitivity with explicit degeneracy, not a primary promotion gate.',
            'Declared slot/ACK/distance and recipe AST are not effective firmware timing or physical/outdoor range.',
            'Full current/period/lag alias remains; restricted period point estimates assume no differential carryover.',
            'Different round/workload/full AP+CPE packages do not establish isolated-knob superiority, noninferiority or an interpolated Cartesian curve.'])

def build_analysis_bn():
    return _build_analysis_bn()


def main_bn():
    import sys
    if '--campaign'not in sys.argv[1:]or sys.argv[sys.argv.index('--campaign')+1]!='BN':return main_campaign()
    parser=argparse.ArgumentParser(description='Explicit frozen BN exact paired audit; no actuator')
    parser.add_argument('--campaign',choices=('BN',),required=True)
    parser.add_argument('--output',type=Path,default=BN_BASE/'wave_bn_covclass31_and_full_matrix_analysis.json')
    path=parser.parse_args().output.resolve()
    if path.parent!=BN_BASE.resolve()or not path.name.startswith('wave_bn_')or path.suffix!='.json':raise ValueError('Owned BN exclusive output only')
    if path.exists():raise FileExistsError(path)
    result=build_analysis_bn()
    with path.open('x',encoding='utf-8',newline='\n')as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=result['status'],contrasts=len(result['contrasts']),arms=len(result['source_claim_audits']))))


# Additive BQ-CF campaign. Legacy functions and the default BN dispatch are intact.
BQCF_BASE=ROOT/'artifacts/autoresearch/waves_bq_to_cf_20261024'
BQCF_ROUNDS=tuple(range(93,110))+tuple(range(114,135))
BQCF_MISSING=(110,111,112,113)
BQCF_MANIFEST_SHA='f81036628828869df84ebb7887093ce1fff17e185ba8ddbf05d1a1701bc42d1d'
BQCF_FAMILY_SHA='b36d41838b64557838a9c64c0e31429df3e60e1c0e2f85aea2ed796304fd8502'
BQCF_GROUPS=(('waves_bq_to_bt_20261024',93,96),('waves_bu_to_bx_20261024',97,102),
             ('waves_by_to_cb_20261024',103,107),('waves_cc_to_cf_20261024',108,134))
BQCF_RANK_FAMILY='new_rank_bound500'
BQCF_MEAN_FAMILY='new_meanflip_bound500'


def metrics_bqcf(number):
    """Fixed before outcomes; absent receipt rounds never become tests."""
    if type(number) is not int or number not in BQCF_ROUNDS:
        raise ValueError('Only explicit available frozen R93-R134 rounds')
    return METRICS if number<=102 else (*METRICS[:4],METRICS[-1])


def frozen_inputs_bqcf(manifest_path=None):
    """Verify logical identity and path boundary before reading any source copy."""
    path=(BQCF_BASE/'inputs_manifest.json') if manifest_path is None else Path(manifest_path)
    if path.resolve()!=(BQCF_BASE/'inputs_manifest.json').resolve():
        raise ValueError('Only the explicit frozen umbrella manifest')
    if binding(path)['sha256']!=BQCF_MANIFEST_SHA:
        raise ValueError('Frozen umbrella manifest drift')
    if binding(BQCF_BASE/'stats_family_and_bootstrap_recipe.json')['sha256']!=BQCF_FAMILY_SHA:
        raise ValueError('Frozen joint hypothesis/bootstrap recipe drift')
    entries=json.loads(path.read_text(encoding='utf-8'))['entries']
    if len(entries)!=114:
        raise ValueError('Exactly114 frozen measurement/TSV/recipe copies')
    refs=[];receipts={};literals={};recipes={};seen=set();kinds=defaultdict(set)
    # Preflight ALL identities first. A future/path substitution is rejected before content.
    for e in entries:
        n=e.get('round');logical=Path(e.get('path',''))
        if type(n) is not int or n not in BQCF_ROUNDS or logical.is_absolute() or '..' in logical.parts:
            raise ValueError('Only available explicit round identities, never missing/future rounds')
        copy=(ROOT/e.get('copy','')).resolve();expected=(BQCF_BASE/'inputs'/logical).resolve()
        if copy!=expected or not copy.is_relative_to((BQCF_BASE/'inputs').resolve()) or copy in seen:
            raise ValueError('Only exact owned frozen copy paths')
        if logical.suffix not in ('.json','.tsv','.py') or logical.suffix in kinds[n]:
            raise ValueError('Unique receipt/TSV/recipe triple required')
        if not re.search(r'(?i)(?:^|_)r'+str(n)+r'_',logical.name):
            raise ValueError('Frozen filename round identity mismatch')
        seen.add(copy);kinds[n].add(logical.suffix)
    if set(kinds)!=set(BQCF_ROUNDS) or any(v!={'.json','.tsv','.py'} for v in kinds.values()):
        raise ValueError('Missing or duplicate source triples')
    for e in entries:
        n=e['round'];copy=(ROOT/e['copy']).resolve();actual=binding(copy)
        if any(actual[k]!=e[k] for k in ('sha256','bytes')):
            raise ValueError('Frozen input bytes differ')
        refs.append(actual|dict(round=n,original_path=e['path']))
        if copy.suffix=='.json':
            text=copy.read_text(encoding='utf-8');receipts[n]=parse_source(text);literals[n]=parse_source(text,True)
        elif copy.suffix=='.py':recipes[n]=copy.read_text(encoding='utf-8')
    return receipts,literals,refs,recipes


def declared_context_bqcf(number,payload,arm,saved=None):
    metrics_bqcf(number)
    expected={k:payload.get(k) for k in ('distance_m','coverage_class','slot_time_us','ack_timeout_us')}
    if any(type(v) is not int or v<0 for v in expected.values()):
        raise ValueError('Explicit typed shared timing declarations required')
    if not 0<=expected['coverage_class']<=31:
        raise ValueError('Current requested advice policy is0..31, not silicon proof')
    regime=payload.get('traffic_regime');flows=payload.get('active_flow_count');bidir=payload.get('bidirectional')
    if type(flows) is not int or flows not in (2,4,6,8) or type(bidir) is not bool:
        raise ValueError('Explicit typed workload context required')
    valid=(f'bidir_{flows}flow' if bidir else f'unidir_dl_{flows}flow' if number<=107 else
           f'unidir_ul_{flows}flow'+('_hammer' if flows==8 else ''))
    if regime!=valid or bidir!=(number<=102):
        raise ValueError('Frozen planned direction and literal source regime conflict')
    for obj in (payload,arm,arm.get('candidate_knobs')):
        if not isinstance(obj,dict):raise ValueError('Three declaration objects required')
        for key,value in expected.items():
            if type(obj.get(key)) is not int or obj[key]!=value:
                raise ValueError('Shared timing missing/conflicting/untyped')
        if obj.get('traffic_regime')!=regime or type(obj.get('active_flow_count')) is not int or obj['active_flow_count']!=flows or type(obj.get('bidirectional')) is not bool or obj['bidirectional']!=bidir:
            raise ValueError('Three shared flow/direction declarations must agree')
    for endpoint in ('ap','cpe'):
        state=arm['candidate_knobs'].get(endpoint+'_state')
        if not isinstance(state,dict):raise ValueError('Both full endpoint packages required')
        for key,value in expected.items():
            if key in state and(type(state[key]) is not int or state[key]!=value):
                raise ValueError('Conflicting endpoint timing')
        if 'distance_meters' in state and(type(state['distance_meters']) is not int or state['distance_meters']!=expected['distance_m']):
            raise ValueError('Conflicting endpoint distance')
    if saved is not None:
        if (saved['workload_regime'],saved['active_flow_count'],saved['bidirectional'],saved['distance_meters'],saved['coverage_class'])!=(regime,flows,bidir,expected['distance_m'],expected['coverage_class']):
            raise ValueError('Normalized shared context differs')
        ev=saved['certified_wds_evidence']
        for key in ('slot_time_us','ack_timeout_us'):
            value=saved[key] if key in saved else ev.get(key)
            if type(value) is not int or value!=expected[key]:raise ValueError('Normalized slot/ACK differs')
    return dict(**expected,workload_regime=regime,active_flow_count=flows,bidirectional=bidir,
                provenance='SHARED_PAYLOAD_TREATMENT_KNOBS',physical_distance_verified=False,effective_timing_independently_verified=False)


def unidirectional_alias_bqcf(number,payload):
    if len(metrics_bqcf(number))!=5:raise ValueError('Only source-declared unidirectional contexts')
    active='dl_goodput_mbps' if number<=107 else 'ul_goodput_mbps'
    inactive='ul_goodput_mbps' if active=='dl_goodput_mbps' else 'dl_goodput_mbps'
    arms=payload.get('iterations')
    if not isinstance(arms,list) or len(arms)!=2:raise ValueError('Two actual arms required')
    checks=[]
    for arm in arms:
        declared_context_bqcf(number,payload,arm)
        blocks=arm.get('repetition_blocks')
        if not isinstance(blocks,list) or len(blocks)!=16:raise ValueError('16actual source blocks required')
        for label,obj,total in [('arm',arm,arm.get('total_bidir_goodput_mbps'))]+[
            (f'block:{r.get("block_index")}',r,r.get('total_goodput_mbps')) for r in blocks]:
            values=[obj.get(active),obj.get(inactive),total]
            if any(type(v) not in (int,float) or not math.isfinite(v) for v in values):
                raise ValueError('Explicit finite typed directional outcomes required')
            if values[0]!=total or values[1]!=0:raise ValueError('ActiveGP alias or inactivezero fails')
            if 'observation' in obj:
                obs=obj['observation']
                if not isinstance(obs,dict) or type(obs.get('goodput_rx_mbps')) not in (int,float) or obs['goodput_rx_mbps']!=total:
                    raise ValueError('Duplicate recorded GP conflicts')
            checks.append(dict(iteration=arm['commit'],source_unit=label,active_value=values[0],inactive_value=values[1],totalGP=total,
                               raw_directional_Jain=obj.get('bidir_jain_fairness'),Jain_not_a_promoted_metric=True))
    return dict(status='EXACT_ACTIVE_DIRECTION_TOTAL_GP_ALIAS_VERIFIED',round_id=f'R{number}',active_metric=active,inactive_metric=inactive,
                semantic_alias_of='goodput_rx_mbps',same_hypothesis_not_duplicate=True,arms_checked=2,blocks_checked=32,source_units=checks,
                inapplicable_inference=['jain_fairness',inactive],selector_contract='Exact both-arm and every-block active=GP/inactive0 as _alias_valid')


def pair_rows_bqcf(rows,control,target,metric):
    if not isinstance(rows,list) or not rows or not isinstance(control,str) or not isinstance(target,str) or not control or not target or control==target:
        raise ValueError('Explicit distinct arms and source rows required')
    seen=set();groups=defaultdict(list);rounds=set()
    for row in rows:
        rid=row.get('round_id')
        if rid not in {f'R{n}' for n in BQCF_ROUNDS}:raise ValueError('Only frozen available current rounds')
        rounds.add(rid)
        if any(type(row.get(k)) is not int or row[k]<0 for k in ('block_index','crossover_step')):
            raise ValueError('Genuine integer IDs/steps required')
        key=(rid,row['block_index'],row['crossover_step'])
        if key in seen:raise ValueError('Duplicate genuine source identity')
        seen.add(key);groups[row['block_index']].append(row)
    if len(rounds)!=1:raise ValueError('No crossround pairing')
    number=int(next(iter(rounds))[1:])
    if metric not in metrics_bqcf(number):raise ValueError('Inapplicable directional/Jain or duplicate hypothesis')
    pairs=[]
    for index,group in sorted(groups.items()):
        a=[r for r in group if r.get('treatment_id')==control];b=[r for r in group if r.get('treatment_id')==target]
        if len(group)!=2 or len(a)!=1 or len(b)!=1 or {r['crossover_step'] for r in group}!={0,1}:
            raise ValueError('One source control and target in source periods0/1 required')
        x,y=_metric(a[0],metric),_metric(b[0],metric)
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in (x,y)):
            raise ValueError('Missing/bad metric cannot disappear or become zero')
        pairs.append(dict(round_id=a[0]['round_id'],block_index=index,control_mean=x,treatment_mean=y,difference=y-x,
                          control_step=a[0]['crossover_step'],target_step=b[0]['crossover_step'],sequence='AB' if a[0]['crossover_step']==0 else 'BA'))
    if len(pairs)!=16:raise ValueError('Exactly16round-scoped genuine block pairs required')
    return pairs


def raw_step_roundtrip_bqcf(number,arm,canonical_rows):
    metrics_bqcf(number);seen=set();checked=[]
    for raw in arm['repetition_blocks']:
        index=raw.get('block_index')
        if type(index) is not int or index<0 or index in seen:raise ValueError('Genuine unique source block IDs')
        seen.add(index);one='step_in_block' in raw;zero='crossover_step' in raw
        if one==zero:raise ValueError('One exclusive source step schema required')
        field='step_in_block' if one else 'crossover_step';original=raw[field]
        if type(original) is not int or original not in ((1,2) if one else (0,1)):
            raise ValueError('Exact source step type/domain required')
        step=original-1 if one else original
        matches=[r for r in canonical_rows if r.get('round_id')==f'R{number}' and r.get('treatment_id')==arm['commit'] and r.get('block_index')==index]
        if len(matches)!=1 or type(matches[0].get('crossover_step')) is not int or matches[0]['crossover_step']!=step:
            raise ValueError('Canonical step/identity differs from literal source')
        if one and any(matches[0].get(k)!=v or type(matches[0].get(k)) is not type(v) for k,v in
                       {'source_step_in_block':original,'source_step_field':field,'crossover_step_mapping':'EXPLICIT_ONE_BASED_SOURCE_MINUS_ONE'}.items()):
            raise ValueError('One-based step provenance is not preserved')
        checked.append(dict(block_index=index,source_step_field=field,source_step_literal=original,crossover_step=step,exact_roundtrip=True))
    if len(checked)!=16:raise ValueError('All16source blocks required')
    return dict(status='EXACT_SOURCE_STEP_ROUNDTRIP',units=checked,source_unit_ids_not_generated=True)


def period_adjusted_bqcf(rows,control,target,metric):
    pairs=pair_rows_bqcf(rows,control,target,metric)
    ab=[p for p in pairs if p['sequence']=='AB'];ba=[p for p in pairs if p['sequence']=='BA']
    if not ab or not ba:return dict(status='NOT_IDENTIFIED_SINGLE_SEQUENCE',assumption='No causal claim')
    def average(group):
        return sum((Fraction(str(p['treatment_mean']))-Fraction(str(p['control_mean'])) for p in group),Fraction())/len(group)
    direct=(average(ab)+average(ba))/2;period=(average(ab)-average(ba))/2
    ids=sorted({r['block_index'] for r in rows})
    x=np.asarray([[1]+[int(r['block_index']==b) for b in ids[1:]]+[r['crossover_step'],int(r['treatment_id']==target)] for r in rows],float)
    beta=np.linalg.lstsq(x,np.asarray([_metric(r,metric) for r in rows]),rcond=None)[0];rank=int(np.linalg.matrix_rank(x))
    if rank!=x.shape[1] or not all(math.isclose(float(a),float(b),abs_tol=1e-9,rel_tol=1e-11) for a,b in ((direct,beta[-1]),(period,beta[-2]))):
        raise ValueError('Restricted exact and numeric period estimates disagree or rank deficient')
    return dict(status='IDENTIFIED_RESTRICTED_MODEL_NOT_CAUSAL_CERTIFICATION',model='BLOCK_FIXED_EFFECTS+PERIOD+CURRENT_TREATMENT_NO_DIFFERENTIAL_CARRYOVER',
                assumptions=['No differential carryover or block-by-period response','Counterbalance does not establish randomization or independence','No separated current/lag causal effect'],
                AB_blocks=len(ab),BA_blocks=len(ba),columns=x.shape[1],rank=rank,direct_estimate=float(direct),period_estimate=float(period),
                direct_exact_fraction=str(direct),period_exact_fraction=str(period),numeric_direct_estimate=float(beta[-1]),numeric_period_estimate=float(beta[-2]),
                no_period_adjusted_inference_p_value='Raw sign flips are not a nuisance-adjusted test')


def joint_families_bqcf(contrasts,prior):
    if len(prior)!=1058 or len({c['source_hypothesis_id'] for c in contrasts})!=len(contrasts) or len(contrasts)>210:
        raise ValueError('Exact prior1058 and unique planned new hypotheses required')
    planned={(f'R{n}',m) for n in BQCF_ROUNDS for m in metrics_bqcf(n)}
    if any((c['scope'],c['metric']) not in planned for c in contrasts):raise ValueError('Unplanned hypothesis')
    if len({(c['scope'],c['metric']) for c in contrasts})!=len(contrasts):
        raise ValueError('One distinct current contrast per planned round/outcome')
    complete=len(prior)+len(contrasts);key=f'complete_known_rank{complete}_bound{complete}'
    families={BQCF_RANK_FAMILY:padded_family(contrasts,500,BQCF_RANK_FAMILY),key:padded_family(
        [dict(source_hypothesis_id=k,exact_rank=dict(p_value=p)) for k,p in prior.items()]+contrasts,complete,key)}
    families[BQCF_MEAN_FAMILY]=padded_family([dict(source_hypothesis_id='MEANFLIP:'+c['source_hypothesis_id'],
        exact_rank=dict(p_value=c['exact_sign_flips']['mean']['p_value'])) for c in contrasts],500,BQCF_MEAN_FAMILY)
    return families


def source_recipe_audit_bqcf(number,text,context):
    """Parse current text, never import/execute live helpers. Keep delegation explicit."""
    metrics_bqcf(number);tree=ast.parse(text);calls=[];warmup=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id.startswith('run_single_'):
            keywords={k.arg:ast.literal_eval(k.value) for k in node.keywords if k.arg in ('duration_sec','flows_per_dir') and isinstance(k.value,ast.Constant)}
            calls.append(dict(name=node.func.id,line=node.lineno,literal_keywords=keywords))
        if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value.startswith('iperf3 -c ') and '-t 1 ' in node.value:
            command=node.value;parallel=re.search(r'(?:^| )-P (\d+)(?: |$)',command)
            warmup.append(dict(line=node.lineno,parallel_streams=int(parallel.group(1)) if parallel else None,
                               reverse=bool(re.search(r'(?:^| )-R(?: |$)',command)),bidir='--bidir' in command,source_role='WARMUP_NOT_MEASUREMENT_WINDOW'))
    if len(calls)!=1:raise ValueError('One explicit source measurement helper call required')
    if calls[0]['literal_keywords'].get('duration_sec')!=5:raise ValueError('Explicit five-second window call required')
    if not warmup:raise ValueError('Current recipe direction/flow warmup text unavailable')
    expected_streams=context['active_flow_count']//2 if context['bidirectional'] else context['active_flow_count']
    expected_reverse=context['workload_regime'].startswith('unidir_ul_')
    if any((w['parallel_streams'],w['reverse'],w['bidir'])!=(expected_streams,expected_reverse,context['bidirectional']) for w in warmup):
        raise ValueError('Recipe literal direction/streams disagree with saved workload')
    expected_word='bidir' if context['bidirectional'] else 'unidir_ul' if expected_reverse else 'unidir_dl'
    if expected_word not in calls[0]['name']:raise ValueError('Explicit helper call direction differs')
    helper_flows=calls[0]['literal_keywords'].get('flows_per_dir')
    if context['bidirectional'] and helper_flows!=expected_streams:raise ValueError('Bidir per-direction call flow count differs')
    return dict(status='SOURCE_AST_DIRECTION_AND_CALL_DECLARATIONS_ONLY',measurement_calls=calls,warmup_direction_checks=warmup,
                recipe_coverage_commands=recipe_coverage_commands(text),source_text_and_AST_only=True,recipe_imported_or_executed=False,
                limits='Current literal warmup and measurement helper call are source declarations, not execution/readback proof. Delegated helper bodies are not implied by their names.')


def statistics_inputs_bqcf(records_path,blocks_path,manifest_path):
    """Only explicit frozen umbrella paths, authenticated by a pre-inference pin."""
    expected={'records':BQCF_BASE/'normalized_r1_to_r134_measurements_20261024.json',
              'blocks':BQCF_BASE/'normalized_r16_to_r134_block_observations_20261024.json',
              'manifest':BQCF_BASE/'inputs_manifest.json'}
    supplied={'records':Path(records_path),'blocks':Path(blocks_path),'manifest':Path(manifest_path)}
    for key,path in supplied.items():
        if path.resolve()!=expected[key].resolve():raise ValueError('Only explicit canonical134 paths; no future-content reads')
    freeze_path=BQCF_BASE/'stats_dependency_freeze.json'
    freeze=json.loads(freeze_path.read_text(encoding='utf-8'))
    if freeze['source']!=binding(Path(__file__)) or freeze['family_recipe']!=binding(BQCF_BASE/'stats_family_and_bootstrap_recipe.json'):
        raise ValueError('Current implementation/family freeze required before inference')
    pins={key:binding(path) for key,path in supplied.items()}
    if freeze['source_inputs']!=pins:raise ValueError('Canonical statistical input pins differ from dependency freeze')
    records=json.loads(supplied['records'].read_text(encoding='utf-8'))['records']
    blocks=json.loads(supplied['blocks'].read_text(encoding='utf-8'))
    return records,blocks,pins,freeze,freeze_path


def applicable_profiles_bqcf(contrasts,utilities,aliases):
    result=[]
    for n in BQCF_ROUNDS:
        own=[c for c in contrasts if c['scope']==f'R{n}']
        required=QOE if n<=102 else (*METRICS[1:4],METRICS[0])
        applicable=[c for c in own if c['metric'] in required]
        if len(applicable)!=len(required):
            result.append(dict(round_id=f'R{n}',status='UNAVAILABLE_SOURCE_OR_OUTCOME_INVALID',controller_or_physical_acceptance=False));continue
        utility=next(u for u in utilities if u['round_id']==f'R{n}')
        unanimous=all(c['favorable_blocks']==16 for c in applicable)
        stats=all(c['family_adjusted_p'][BQCF_RANK_FAMILY]<=.05 and
                  (c['HL_estimate']<0 if c['direction']=='lower' else c['HL_estimate']>0) for c in applicable)
        loss=Fraction(utility['loss_percent_exact'])
        result.append(dict(round_id=f'R{n}',status='SOURCE_CONDITIONS_ONLY_NOT_PROMOTION',required_primary_metrics=list(required),
            semantic_GP_alias=next((a for a in aliases if a['round_id']==f'R{n}'),None),all_applicable_16of16=unanimous,
            applicable_direct_rank_HL_Holm500=stats,strict_observed_GP_loss_below2=loss<2,operator_observed_GP_loss_at_most2=loss<=2,
            necessary_observed_strict_conditions_met=unanimous and stats and loss<2,
            failed_unanimity_metrics=[c['metric'] for c in applicable if c['favorable_blocks']!=16],target_retry_lower=utility['target_retry_lower'],
            controller_or_physical_acceptance=False,health_history_provenance_gates_not_replaced=True))
    return result


def revalidate_input_pins_bqcf(pins):
    """Bindings store repo-relative names; rehash their explicit absolute paths."""
    current={}
    for key,pin in pins.items():
        logical=Path(pin['path'])
        if logical.is_absolute() or '..' in logical.parts:
            raise ValueError('Only repo-relative canonical input bindings')
        current[key]=binding(ROOT/logical)
    if current!=pins:raise ValueError('Canonical input drift during inference')


def build_analysis_bqcf(records_path,blocks_path,manifest_path):
    """One prespecified union family; group outputs are views, never re-tests."""
    names=('fmx_r43_to_r47_dyadic_zero_loss_audit','fmx_r48_to_r56_distance_goodput_dyadic_audit',
           'fmx_r33_to_r42_exact_holm500_audit','fmx_r27_to_r32_certified_wds_audit','fmx_r22_to_r26_crossover_audit',
           'fmx_r16_to_r21_real_crossover_audit','fmx_r15_and_crossover_statistical_audit',
           'fmx_r10_to_r14_causal_and_power_analysis','fmx_r57_to_r60_retry64_goodput_parity_audit')
    dependencies=[Path(__file__),ROOT/'orchestration/autoresearch/fmx_live_dataset.py',ROOT/'orchestration/autoresearch/fmx_offline_data.py']+[
        ROOT/f'analysis/statistics/{name}.py' for name in names]
    deps=[binding(p) for p in dependencies]
    records,blocks,pins,freeze,freeze_path=statistics_inputs_bqcf(records_path,blocks_path,manifest_path)
    if freeze['numerical_dependencies']!=deps:raise ValueError('Frozen dependency bytes differ before inference')
    receipts,literals,refs,recipes=frozen_inputs_bqcf(manifest_path)
    by_id={(r['round_id'],r['iteration']):r for r in records}
    if len(by_id)!=len(records):raise ValueError('Duplicate normalized arm identity')
    new=[r for r in blocks['crossed'] if r.get('round_id') in {f'R{n}' for n in BQCF_ROUNDS}]
    counts=dict(records=len(records),primary=sum(r['window_kind']=='primary' for r in records),auxiliary=sum(r['window_kind']!='primary' for r in records),
                crossed=len(blocks['crossed']),matched=len({(r['round_id'],r['block_index']) for r in blocks['crossed']}),sequential=len(blocks['sequential']),
                available_new_rounds=len(receipts),new_arms=sum(len(r['iterations']) for r in receipts.values()),new_crossed=len(new),
                new_matched=len({(r['round_id'],r['block_index']) for r in new}))
    if counts!=dict(records=360,primary=358,auxiliary=2,crossed=3356,matched=1590,sequential=16,available_new_rounds=38,new_arms=76,new_crossed=1216,new_matched=608):
        raise ValueError('Actual canonical360/3356/1590+16 and76/1216/608 expected')
    aliases=[];descriptions=[];utilities=[];designs=[];raw_pairs=[];excluded=[];valid=[]
    for n in BQCF_ROUNDS:
        # Do not silently omit a failed source: retain a bounded diagnostic, leave
        # its planned hypotheses unavailable, and keep the family size500.
        try:
            arms=receipts[n]['iterations']
            if len(arms)!=2:raise ValueError('Two actual source arms required')
            control,target=[a['commit'] for a in arms]
            group=[r for r in new if r['round_id']==f'R{n}']
            own_pairs=[dict(round_id=f'R{n}',metric=m,pairs=pair_rows_bqcf(group,control,target,m)) for m in metrics_bqcf(n)]
            audits=[]
            for index,arm in enumerate(arms):
                saved=by_id[(f'R{n}',arm['commit'])]
                audit=source_arm_audit(n,arm,literals[n]['iterations'][index],saved)
                context=declared_context_bqcf(n,receipts[n],arm,saved)
                audit.update(declared_timing_context=context,recipe_direction=source_recipe_audit_bqcf(n,recipes[n],context),
                             source_step_roundtrip=raw_step_roundtrip_bqcf(n,arm,group),
                             per_block_station_counters=[dict(block_index=r['block_index'],counter_interface=r['counter_interface'],
                                packets=r['mac_tx_packets_delta'],retries=r['mac_tx_retries_delta'],rate_exact=str(retry_fraction(r)),
                                independent_AP_or_peer_identity_verified=False) for r in group if r['treatment_id']==arm['commit']])
                audits.append(audit)
            alias=None
            if n>102:
                alias=unidirectional_alias_bqcf(n,receipts[n]);active=alias['active_metric'];inactive=alias['inactive_metric']
                saved_arms=[by_id[(f'R{n}',t)] for t in (control,target)]
                if not all(a[active]==a['goodput_mbps'] and a[inactive]==0 for a in saved_arms) or not all(
                        r[active]==r['observation']['goodput_rx_mbps'] and r[inactive]==0 for r in group):
                    raise ValueError('Normalized alias differs from actual source')
                alias['normalized_arm_and_all_block_identity_verified']=True
            a,b=[by_id[(f'R{n}',t)] for t in (control,target)]
            utility=dict(round_id=f'R{n}',**observed_utility(a['goodput_mbps'],b['goodput_mbps']),
                         control_retry_exact=str(Fraction(a['mac_tx_retries'],a['mac_tx_packets'])),
                         target_retry_exact=str(Fraction(b['mac_tx_retries'],b['mac_tx_packets'])),
                         target_retry_lower=Fraction(b['mac_tx_retries'],b['mac_tx_packets'])<Fraction(a['mac_tx_retries'],a['mac_tx_packets']))
            design=multilevel_design_diagnostics(group)|dict(round_id=f'R{n}')
            design['schedule_agreement']=schedule_agreement(group,receipts[n]['crossover_schedule'],{'A':control,'B':target})
            design['interpretation']='Full current/period/lag alias retained. Restricted model assumes no differential carryover, not separated causal effects.'
        except (ValueError,KeyError,TypeError,ZeroDivisionError) as error:
            excluded.append(dict(round_id=f'R{n}',status='INVALID_SOURCE_OR_OUTCOME_NO_INFERENCE',reason=type(error).__name__+': '+str(error),
                                 planned_hypotheses=len(metrics_bqcf(n)),family_declared_size_unchanged=500));continue
        raw_pairs+=own_pairs;descriptions+=audits;utilities.append(utility);designs.append(design);valid.append(n)
        if alias is not None:aliases.append(alias)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(7,4,figsize=(22,20))
    for column,(groupname,first,last) in enumerate(BQCF_GROUPS):
        for mi,metric in enumerate(METRICS):
            own=[r for r in raw_pairs if first<=int(r['round_id'][1:])<=last and r['metric']==metric]
            ax=axes[mi,column]
            if own:
                ax.boxplot([[p['difference'] for p in row['pairs']] for row in own],tick_labels=[r['round_id'] for r in own],showfliers=True)
                ax.axhline(0,color='gray',linewidth=.5);ax.tick_params(axis='x',rotation=90,labelsize=6)
            else:ax.text(.1,.5,'INAPPLICABLE: raw Jain/inactive retained',fontsize=7)
            ax.set_title(groupname.replace('_20261024','')+' '+metric,fontsize=7)
    fig.suptitle('Frozen paired target-minus-control descriptives before inference; no crossround pairing')
    fig.tight_layout();plot=BQCF_BASE/'stats_paired_descriptives.png'
    if plot.exists():raise FileExistsError(plot)
    fig.savefig(plot,dpi=110);plt.close(fig)
    descpath=BQCF_BASE/'stats_preinference_descriptives.json'
    with descpath.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(dict(status='CREATED_BEFORE_INFERENCE',source_inputs=pins,sources=refs,paired_values=raw_pairs,source_audits=descriptions,
                       semantic_aliases=aliases,excluded_rounds=excluded,plot=binding(plot),assumptions=freeze['assumptions']),f,indent=2,allow_nan=False);f.write('\n')
    indices=bootstrap_indices(16);contrasts=[]
    for n in valid:
        control,target=[a['commit'] for a in receipts[n]['iterations']]
        group=[r for r in new if r['round_id']==f'R{n}']
        literal_by={(a['commit'],r['block_index']):r for a in literals[n]['iterations'] for r in a['repetition_blocks']}
        a,b=[by_id[(f'R{n}',t)] for t in (control,target)]
        for metric in metrics_bqcf(n):
            pairs=next(x['pairs'] for x in raw_pairs if x['round_id']==f'R{n}' and x['metric']==metric)
            differences=[p['difference'] for p in pairs];effect=exact_effect_bj(differences);flips=exact_sign_flips(differences)
            if any(flips[k]['p_value']!=effect['exact_'+k]['p_value'] for k in ('rank','sign')):
                raise ValueError('Exact enumeration and independent rank/sign algorithms disagree')
            decimal_differences=[source_metric(literal_by[(target,p['block_index'])],metric)-source_metric(literal_by[(control,p['block_index'])],metric) for p in pairs]
            sensitivity=enumerate_fraction_flips(decimal_differences)
            alias=next((v for v in aliases if v['round_id']==f'R{n}'),None) if metric=='goodput_rx_mbps' else None
            contrasts.append(dict(source_hypothesis_id=json.dumps([f'R{n}',control,target,metric],separators=(',',':')),scope=f'R{n}',control=control,target=target,
                control_policy_id=a['policy_key'],target_policy_id=b['policy_key'],regime=b['workload_regime'],metric=metric,direction='lower' if metric in LOWER else 'higher',
                semantic_alias=None if alias is None else dict(active_metric=alias['active_metric'],alias_of='goodput_rx_mbps',same_hypothesis_not_duplicate=True,source_audit_round=f'R{n}'),
                paired_unit_ids=[dict(round_id=p['round_id'],block_index=p['block_index']) for p in pairs],pairs=pairs,
                favorable_blocks=sum(d<0 if metric in LOWER else d>0 for d in differences),equal_blocks=sum(d==0 for d in differences),quality=_quality(group),
                exact_sign_flips=flips,source_decimal_sensitivity=dict(literal_differences=[str(v) for v in decimal_differences],exact_flips=sensitivity,
                    rank_p_changed=sensitivity['rank']['p_value']!=flips['rank']['p_value'],mean_p_changed=sensitivity['mean']['p_value']!=flips['mean']['p_value']),
                period_adjusted=period_adjusted_bqcf(group,control,target,metric),paired_bca_HL=paired_bca_hl(differences,resample_indices=indices),**effect))
    priorpath=BN_BASE/'wave_bn_covclass31_and_full_matrix_analysis.json'
    if binding(priorpath)['sha256']!='26dfde9204725b373bb59375dd4b10309361b19c1578f282ffdf62e49794088d':raise ValueError('Accepted prior BN bytes changed')
    prior=json.loads(priorpath.read_text(encoding='utf-8'))['families']['complete_known_rank1058_bound1058']['known_hypotheses']
    families=joint_families_bqcf(contrasts,prior)
    for c in contrasts:
        c['family_adjusted_p']={k:v['adjusted_p'][c['source_hypothesis_id']] for k,v in families.items() if c['source_hypothesis_id'] in v['adjusted_p']}
        c['mean_flip_holm500_adjusted_p']=families[BQCF_MEAN_FAMILY]['adjusted_p']['MEANFLIP:'+c['source_hypothesis_id']]
    projection=[dict(source_hypothesis_id=c['source_hypothesis_id'],regime=c['regime'],target_policy_id=c['target_policy_id'],control_policy_id=c['control_policy_id'],
        round_ids=[c['scope']],paired_unit_ids=c['paired_unit_ids'],metric=c['metric'],direction=c['direction'],effect_hl=c['HL_estimate'],p_exact_rank=c['exact_rank']['p_value'],
        semantic_alias=c['semantic_alias'],holm500_adjusted_p=c['family_adjusted_p'][BQCF_RANK_FAMILY],family500_key=BQCF_RANK_FAMILY,
        comparability_status='WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON',statistic='PRIMARY_EXACT_SIGNED_RANK_NOT_MEAN_FLIP_OR_BCA') for c in contrasts]
    if [binding(p) for p in dependencies]!=deps:raise ValueError('Numerical dependency drift during inference')
    revalidate_input_pins_bqcf(pins)
    profiles=applicable_profiles_bqcf(contrasts,utilities,aliases)
    return dict(schema_version=3,status='OFFLINE_BQ_CF_UNION_AUDIT_PENDING_INDEPENDENT_ACCEPTANCE',counts=counts,
        software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
        source_inputs=pins,sources=refs,numerical_dependencies=deps,implementation_freeze=binding(freeze_path),family_plan=binding(BQCF_BASE/'stats_family_and_bootstrap_recipe.json'),
        prior_unchanged_analysis=binding(priorpath),preinference_descriptives=binding(descpath),paired_plot=binding(plot),contrasts=contrasts,families=families,
        source_claim_audits=descriptions,observed_utility=utilities,design_diagnostics=designs,excluded_rounds=excluded,
        missing_measurements=[dict(round_id=f'R{n}',status='UNKNOWN_LOCAL_ARTIFACT_ABSENT',check_complete=True,measurement_or_test_invented=False) for n in BQCF_MISSING],
        unidirectional_semantic_aliases=aliases,applicable_strict_source_conditions=profiles,
        source_claims=dict(actual_source_arms=len(descriptions),saved_RTTs=sum(d['received_pings'] for d in descriptions),
            all_literal_means_exact=all(d['literal_mean_audit']['all_literal_equal'] for d in descriptions),all_zero_ULP=all(d['dyadic_audit']['all_zero_ulp'] for d in descriptions),
            all_source_arms160received=all(d['complete_160_pings'] for d in descriptions),all_chronological_RTT_pools=all(d['chronology_matches'] for d in descriptions),
            all_MAC_pools_match=all(d['mac_sums_match'] for d in descriptions),seven_point_pureDL_certification='NOT_ASSUMED: priorR81failsGP andR83is_bidir4flow3km'),
        bootstrap_common_indices_sha256=hashlib.sha256(indices.astype('<i8').tobytes()).hexdigest(),
        catalog_scope=dict(primary_new_known=len(contrasts),primary_new_planned=210,primary_prior_known=1058,complete_primary_known=1058+len(contrasts),
            complete_primary_Holm500='INAPPLICABLE_KNOWN_EXCEEDS500',mean_flip_family_separate=True,group_outputs_same_union_adjustment=True,not_all_project_tests=True),
        promotion_evidence=dict(source_inputs={k+'_sha256':v['sha256'] for k,v in pins.items()},contrasts=projection,
            families={k:v for k,v in families.items() if k!=BQCF_MEAN_FAMILY},unidirectional_aliases=aliases,evidence_only_not_promotion=True),
        automatic_execution_allowed=False,physical_or_causal_acceptance=False,
        limits=['608round-scoped pairs are not12160independent trials; missing110-113 are not invented.',
            'Unidirectional GP aliases its explicit active direction only after both-arm/every-block identity; raw Jain/inactive retained but inapplicable.',
            'One joint210-primary/500 family is shared by all four groups; mean flips are a separate sensitivity family.',
            'Exact rank/sign/mean tests and Walsh sets remain conditional on sign exchangeability/symmetry/shift assumptions.',
            'Paired seeded BCa is approximate sensitivity, explicit unavailable if degenerate, never promotion evidence.',
            'Full block/period/current/lag alias is retained; restricted point model assumes no differential carryover.',
            'Declared timing/class/recipe text is not effective readback, silicon maximum, outdoor range or wireless causal acceptance.',
            'UL8hammer/RTS/VO/TSQ/full endpoint packages are not interchangeable with UL2 or isolated-knob effects.'])


def main_bqcf():
    import sys
    if '--campaign' not in sys.argv[1:] or sys.argv[sys.argv.index('--campaign')+1]!='BQCF':return main_bn()
    parser=argparse.ArgumentParser(description='Frozen BQ-CF union exact paired audit; no actuator')
    parser.add_argument('--campaign',choices=('BQCF',),required=True)
    parser.add_argument('--records',type=Path,default=BQCF_BASE/'normalized_r1_to_r134_measurements_20261024.json')
    parser.add_argument('--blocks',type=Path,default=BQCF_BASE/'normalized_r16_to_r134_block_observations_20261024.json')
    parser.add_argument('--manifest',type=Path,default=BQCF_BASE/'inputs_manifest.json')
    parser.add_argument('--output',type=Path,default=BQCF_BASE/'stats_crossover_analysis.json')
    args=parser.parse_args();path=args.output.resolve()
    if path.parent!=BQCF_BASE.resolve() or not path.name.startswith('stats_') or path.suffix!='.json':raise ValueError('Owned exclusive stats output only')
    if path.exists():raise FileExistsError(path)
    result=build_analysis_bqcf(args.records,args.blocks,args.manifest)
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=result['status'],contrasts=len(result['contrasts']),arms=len(result['source_claim_audits']))))


def stage13_statistics_dependency_bindings():
    """Actual current implementation pins for the separate Stage13 freeze."""
    from orchestration.autoresearch.fmx_stage13_statistics import dependency_bindings
    return dependency_bindings()


def build_analysis_stage13_sync(*,records_path,blocks_path,manifest_path,expected_manifest_sha256,dependency_freeze_path):
    from orchestration.autoresearch.fmx_stage13_statistics import build_stage13_statistical_audit
    return build_stage13_statistical_audit(records_path=records_path,blocks_path=blocks_path,manifest_path=manifest_path,
        expected_manifest_sha256=expected_manifest_sha256,dependency_freeze_path=dependency_freeze_path)


def main_stage13_sync(argv=None):
    from orchestration.autoresearch.fmx_stage13_statistics import main
    return main(argv)


if __name__=='__main__':
    import sys
    if '--campaign'in sys.argv[1:]and sys.argv.index('--campaign')+1<len(sys.argv)and sys.argv[sys.argv.index('--campaign')+1]=='STAGE13_SYNC':
        main_stage13_sync()
    else:main_bqcf()



