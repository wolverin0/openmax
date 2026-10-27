"""Scoped conditional Stage13 audit; no cross-radio or packet pseudoreplication."""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import argparse
import hashlib
import json
import math
import platform
import numpy as np
import scipy
from orchestration.autoresearch import fmx_stage13_sync as data

ROUNDS=tuple(f'R{n}'for n in range(147,195))
METRICS=('goodput_mbps','p50_ms','p95_ms','p99_ms','ul_goodput_mbps','jain_fairness','wds_retry_fraction')
LOWER={'p50_ms','p95_ms','p99_ms','wds_retry_fraction'}
FAMILY_SIZE=336


def dependency_bindings():
    from orchestration.autoresearch import fmx_statistical_audit as engine
    modules=[Path(engine.__file__),Path(__file__),Path(data.__file__),data.ROOT/'orchestration/autoresearch/fmx_offline_data.py',
        Path(data.full.__file__),Path(data.full.live.__file__)]
    modules.extend(data.ROOT/f'analysis/statistics/{name}.py'for name in (
        'fmx_r10_to_r14_causal_and_power_analysis','fmx_r15_and_crossover_statistical_audit',
        'fmx_r16_to_r21_real_crossover_audit','fmx_r22_to_r26_crossover_audit',
        'fmx_r27_to_r32_certified_wds_audit','fmx_r33_to_r42_exact_holm500_audit',
        'fmx_r43_to_r47_dyadic_zero_loss_audit','fmx_r48_to_r56_distance_goodput_dyadic_audit',
        'fmx_r57_to_r60_retry64_goodput_parity_audit'))
    return [data.binding(p)for p in modules]


def metric_value(row,metric):
    if metric not in METRICS:raise ValueError('Metric outside fixed family')
    if metric=='wds_retry_fraction':
        if row.get('counter_interface')!='phy0-ap0.sta1':raise ValueError('Exact saved station-counter declaration required')
        denominator=row.get('mac_tx_packets_delta');numerator=row.get('mac_tx_retries_delta')
        data.integer(denominator,'retry denominator',1);data.integer(numerator,'retry events')
        return numerator/denominator
    value=row.get('ul_goodput_mbps')if metric=='ul_goodput_mbps'else row.get('observation',{}).get(
        'goodput_rx_mbps'if metric=='goodput_mbps'else metric)
    return data.finite(value,'paired '+metric)


def pair_rows(rows,control,target,metric):
    if not isinstance(rows,list)or len(rows)!=32 or not isinstance(control,str)or not isinstance(target,str)or control==target:
        raise ValueError('Exactly two saved sixteen-block arms and distinct IDs required')
    seen=set();rounds=set();groups={}
    for row in rows:
        if row.get('round_id')not in ROUNDS:raise ValueError('Owned Stage13 round only')
        rounds.add(row['round_id']);index=data.integer(row.get('block_index'),'paired block index',0,16)
        step=data.integer(row.get('crossover_step'),'paired source step',0,1)
        if row.get('treatment_id')not in (control,target):raise ValueError('Unexpected treatment')
        key=(row['round_id'],index,step)
        if key in seen:raise ValueError('Duplicate source block/step identity')
        seen.add(key);groups.setdefault(index,[]).append(row)
    if len(rounds)!=1 or len(groups)!=16:raise ValueError('No mixed-round or incomplete pair inference')
    pairs=[]
    for index,group in sorted(groups.items()):
        a=[r for r in group if r['treatment_id']==control];b=[r for r in group if r['treatment_id']==target]
        if len(a)!=1 or len(b)!=1 or {r['crossover_step']for r in group}!={0,1}:raise ValueError('One control/target at distinct genuine periods required')
        x=metric_value(a[0],metric);y=metric_value(b[0],metric)
        pairs.append(dict(round_id=a[0]['round_id'],block_index=index,control_value=x,target_value=y,difference=y-x,
            control_step=a[0]['crossover_step'],target_step=b[0]['crossover_step'],sequence='AB'if a[0]['crossover_step']==0 else'BA'))
    return pairs


def alias_audit(arms,rows):
    direction=arms[0]['bidirectional']
    if any(r['bidirectional']is not direction for r in arms):raise ValueError('Mixed direction in one source comparison')
    if direction:return dict(status='BIDIRECTIONAL_NO_ACTIVE_DIRECTION_ALIAS',inapplicable_metrics=[])
    if any(r['workload_regime']!='unidir_ul_8flow_hammer'for r in arms):raise ValueError('Unknown unidirectional schema')
    if any(r['dl_goodput_mbps']!=0 or r['ul_goodput_mbps']!=r['goodput_mbps']for r in arms):raise ValueError('Arm active/inactive alias not identified')
    if any(r['dl_goodput_mbps']!=0 or r['ul_goodput_mbps']!=r['observation']['goodput_rx_mbps']for r in rows):raise ValueError('Block active/inactive alias not identified')
    return dict(status='SOURCE_PROVEN_GP_EQUALS_ACTIVE_UL_WITH_INACTIVE_DL_ZERO',alias_of='goodput_mbps',active_metric='ul_goodput_mbps',
        arms_verified=2,blocks_verified=32,inapplicable_metrics=['ul_goodput_mbps','jain_fairness'],
        raw_inactive_throughput_and_jain_retained=True,no_duplicate_hypothesis=True)


def descriptive(values):
    x=np.asarray(values,dtype=float)
    if len(x)!=16 or not np.isfinite(x).all():raise ValueError('Sixteen finite saved block values required')
    return dict(n=16,mean=float(x.mean()),median=float(np.median(x)),sample_sd=float(x.std(ddof=1)),
        minimum=float(x.min()),maximum=float(x.max()),values=x.tolist(),constant=bool(np.ptp(x)==0))


def restricted_period(pairs):
    groups={s:[p for p in pairs if p['sequence']==s]for s in ('AB','BA')}
    if not all(groups.values()):return dict(status='UNIDENTIFIED_SINGLE_SEQUENCE',causal_acceptance=False)
    means={s:sum((Fraction(str(p['target_value']))-Fraction(str(p['control_value']))for p in v),Fraction())/len(v)for s,v in groups.items()}
    direct=(means['AB']+means['BA'])/2;period=(means['AB']-means['BA'])/2
    return dict(status='RESTRICTED_POINT_ESTIMATE_ONLY',model='BLOCK+PERIOD+CURRENT_TREATMENT_WITH_NO_DIFFERENTIAL_CARRYOVER',
        direct_exact_fraction=str(direct),period_exact_fraction=str(period),direct=float(direct),period=float(period),
        AB=len(groups['AB']),BA=len(groups['BA']),assumptions=['No differential carryover','Meaningful paired units and additive period effect'],
        separated_current_and_lag_causal_effect_identified=False,adjusted_inference_p_value=None)


def analyze_pairs(pairs,*,resample_indices):
    from orchestration.autoresearch import fmx_statistical_audit as engine
    differences=[p['difference']for p in pairs]
    effect=engine.exact_effect_bj(differences);flips=engine.exact_sign_flips(differences)
    if any(effect['exact_'+k]['p_value']!=flips[k]['p_value']for k in ('rank','sign')):
        raise ValueError('Exact independent numerical engines disagree')
    return dict(**effect,exact_sign_flips=flips,restricted_period=restricted_period(pairs),
        paired_bca_HL=engine.paired_bca_hl(differences,resample_indices=resample_indices,resamples=10000,seed=20261025),
        conditional_only=True,promotion_input=False)


def _frozen_inputs(*,records_path,blocks_path,manifest_path,expected_manifest_sha256,dependency_freeze_path):
    paths={key:data.full._safe_path(path)for key,path in [('records',records_path),('blocks',blocks_path),('manifest',manifest_path),('freeze',dependency_freeze_path)]}
    if any(p.parent!=data.BASE for k,p in paths.items()):raise ValueError('Explicit owned Stage13 artifact files only')
    if paths['freeze'].name!='statistics_dependency_freeze.json':raise ValueError('Explicit Stage13 pre-inference dependency freeze required')
    manifest,refs,contents,prefix,mapping,family,manifest_pin=data.authenticate(manifest_path=paths['manifest'],expected_manifest_sha256=expected_manifest_sha256)
    freeze=data.full._json(paths['freeze'].read_bytes());pins={k:data.binding(p)for k,p in paths.items()if k!='freeze'}
    if freeze.get('source_inputs')!=pins or freeze.get('source_bindings')!=dependency_bindings()or freeze.get('family_recipe')!=manifest['statistical_family_recipe']:
        raise ValueError('Stage13 current source/input/family freeze differs before inference')
    records=data.full._json(paths['records'].read_bytes());blocks=data.full._json(paths['blocks'].read_bytes())
    # Compare the exact current source-bound normalized cohort, not status flags.
    expected=data._build(manifest_path=paths['manifest'],expected_manifest_sha256=expected_manifest_sha256)
    cohort=expected[2];new=expected[3];observations=[b for r in cohort for b in r['repetition_blocks']]
    if records.get('multiradio_packages')!=expected[7]:raise ValueError('Normalized MultiRadio values/provenance/missingness differ from authenticated saved evidence')
    if (records.get('source_refs')!=prefix['records']['source_refs']+expected[5]
            or blocks.get('source_refs')!=prefix['blocks']['source_refs']+expected[5]):raise ValueError('Normalized source references differ from exact authenticated prefix+append')
    if records['bench_cohort']!=cohort or blocks['bench_cohort_crossed']!=observations:raise ValueError('Normalized source values/identities differ from authenticated saved evidence')
    if records['records']!=prefix['records']['records']+new:raise ValueError('Cumulative bench records differ from exact prefix+append')
    if blocks['crossed']!=prefix['blocks']['crossed']+expected[4]or blocks['sequential']!=prefix['blocks']['sequential']:raise ValueError('Cumulative block prefix/append drift')
    if family.get('family_size')!=336 or family.get('metric_slots')!=list(METRICS)or family.get('bootstrap_seed')!=20261025:
        raise ValueError('Exact computational family recipe required')
    return records,blocks,pins,freeze,paths,family


def build_stage13_statistical_audit(*,records_path,blocks_path,manifest_path,expected_manifest_sha256,dependency_freeze_path):
    from orchestration.autoresearch import fmx_statistical_audit as engine
    records,blocks,pins,freeze,paths,family=_frozen_inputs(records_path=records_path,blocks_path=blocks_path,manifest_path=manifest_path,
        expected_manifest_sha256=expected_manifest_sha256,dependency_freeze_path=dependency_freeze_path)
    indices=engine.bootstrap_indices(16,10000,20261025)
    slots=[];descriptives=[];designs=[];aliases=[];prepared=[]
    # All raw descriptives/missingness are built before the first inferential call.
    for round_id in ROUNDS:
        arms=sorted([r for r in records['bench_cohort']if r['round_id']==round_id],key=lambda r:r['source_position'])
        if len(arms)!=2 or [r['source_position']for r in arms]!=['/iterations/0','/iterations/1']:raise ValueError('Explicit source arm order required')
        rows=[r for r in blocks['bench_cohort_crossed']if r['round_id']==round_id]
        alias=alias_audit(arms,rows);aliases.append(dict(round_id=round_id,**alias))
        designs.append(dict(round_id=round_id,**engine.multilevel_design_diagnostics(rows)))
        for metric in METRICS:
            slot=dict(source_hypothesis_id=json.dumps(['STAGE13_SYNC',round_id,arms[0]['iteration'],arms[1]['iteration'],metric],separators=(',',':')),
                round_id=round_id,metric=metric,control=arms[0]['iteration'],target=arms[1]['iteration'],
                control_policy_key=arms[0]['stage13_policy_key'],target_policy_key=arms[1]['stage13_policy_key'],
                raw_p_value=None,correction_p_value=1,mean_raw_p_value=None,mean_correction_p_value=1,promotion_input=False)
            if metric in alias['inapplicable_metrics']:
                slot.update(status='INAPPLICABLE_ALIAS_OR_DIRECTIONAL_JAIN',reason='Raw values retained; active throughput aliases the GP hypothesis or Jain is not a directional effect.')
            else:
                try:pairs=pair_rows(rows,slot['control'],slot['target'],metric)
                except ValueError as error:slot.update(status='UNAVAILABLE',reason=str(error))
                else:
                    slot.update(status='PENDING_CONDITIONAL_INFERENCE',pairs=pairs,paired_unit_ids=[dict(round_id=p['round_id'],block_index=p['block_index'])for p in pairs])
                    descriptives.append(dict(source_hypothesis_id=slot['source_hypothesis_id'],control=descriptive([p['control_value']for p in pairs]),
                        target=descriptive([p['target_value']for p in pairs]),differences=descriptive([p['difference']for p in pairs])))
            prepared.append(slot)
    for slot in prepared:
        if slot['status']=='PENDING_CONDITIONAL_INFERENCE':
            analysis=analyze_pairs(slot['pairs'],resample_indices=indices);slot.update(status='CONDITIONAL_PAIRED_ANALYSIS',analysis=analysis,
                raw_p_value=analysis['exact_rank']['p_value'],mean_raw_p_value=analysis['exact_sign_flips']['mean']['p_value'])
            slot['correction_p_value']=slot['raw_p_value'];slot['mean_correction_p_value']=slot['mean_raw_p_value']
        slot['bonferroni336_rank_bound']=min(1.,FAMILY_SIZE*slot['correction_p_value'])
        slot['bonferroni336_mean_bound']=min(1.,FAMILY_SIZE*slot['mean_correction_p_value'])
        slots.append(slot)
    if len(slots)!=336 or len({r['source_hypothesis_id']for r in slots})!=336:raise ValueError('Exact distinct336-slot computational family required')
    for key,p in paths.items():
        if key!='freeze'and data.binding(p)!=pins[key]:raise ValueError('Statistical input drift during inference')
    if dependency_bindings()!=freeze['source_bindings']:raise ValueError('Numerical source drift during inference')
    multi=[dict(round_id=p['round_id'],inference_status=p['inference_status'],phase_count=len(p['phases']),
        phases=p['phases'],source=p['source'],source_pointer=p['source_pointer'],independent_sampling_units_identified=False)
        for p in records['multiradio_packages']]
    return dict(schema_version='STAGE13_STATISTICS_V1',status='CONDITIONAL_SAVED_EVIDENCE_AUDIT_NOT_PHYSICAL_OR_SELECTOR_ACCEPTANCE',
        source_inputs=pins,numerical_dependencies=freeze['source_bindings'],dependency_freeze=data.binding(paths['freeze']),
        family_recipe=family,family_size=336,slots=slots,slot_status_counts=dict(Counter(s['status']for s in slots)),
        rank_and_mean_families_separate=True,sign_diagnostic_is_not_an_extra_independent_test=True,
        missing_raw_p_stays_null=True,missing_or_inapplicable_p1_is_conservative_bound_only=True,
        prior_historical_project_family_claimed=False,preinference_descriptives=descriptives,design_diagnostics=designs,
        directional_aliases=aliases,multiradio_descriptive_packages=multi,
        bootstrap_common_indices_sha256=hashlib.sha256(indices.astype('<i8').tobytes()).hexdigest(),
        software_versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        limits=['Round-scoped paired blocks are not packet RTT trials or independent radio replications.',
            'Exact tests/intervals are conditional on unqualified paired-unit independence, sign exchangeability and shift/symmetry assumptions.',
            'Restricted period estimates assume no differential carryover; aliased current/lag effects are not separated causal effects.',
            'MultiRadio four-phase aggregates are descriptive; no reconstructed distributions or cross-radio inference.',
            'No effective actuator, physical range, voice-service qualification or selector promotion follows from these results.'],
        physical_acceptance=False,automatic_execution_allowed=False,selector_promotion_allowed=False)


def main(argv=None):
    parser=argparse.ArgumentParser(description='STAGE13_SYNC saved-source conditional audit only')
    parser.add_argument('--campaign',choices=['STAGE13_SYNC'],required=True)
    for name in ('records','blocks','manifest','dependency-freeze','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--expected-manifest-sha256',required=True)
    args=parser.parse_args(argv)
    path=data.full._safe_path(args.output)
    if path.parent!=data.BASE or path.suffix!='.json':raise ValueError('Only exclusive new Stage13 JSON output')
    if path.exists():raise FileExistsError(path)
    result=build_stage13_statistical_audit(records_path=args.records,blocks_path=args.blocks,manifest_path=args.manifest,
        expected_manifest_sha256=args.expected_manifest_sha256,dependency_freeze_path=args.dependency_freeze)
    with path.open('x',encoding='utf-8',newline='\n')as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=result['status'],family_size=336,slot_status_counts=result['slot_status_counts'])))
