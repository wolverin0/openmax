"""Disposable synthetic contracts only; no bench, target or acquisition imports."""
from copy import deepcopy
import hashlib
import json

import pytest

from controller.optimizer.wmm_regime_policy import select_regime_policy
from orchestration.autoresearch.fmx_structural_promotion_gate import (
    load_bound_evidence,evaluate_promotion,REGIMES,REQUIRED_METRICS,
)


def dump(path,value):
    path.write_text(json.dumps(value,sort_keys=True,allow_nan=False)+'\n')
    return {'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def fixture_bundle(tmp_path,*,regime='bidir_6flow',count=16,mutate=None,retry=7,after_pins=None):
    inputs=tmp_path/'inputs';inputs.mkdir()
    source=dump(inputs/'saved_receipt.json',{'synthetic_disposable':True})
    recipe=dump(inputs/'saved_recipe.txt',{'synthetic_text_not_executed':True})
    ap=dict(aql_by_ac=[[300,600],[600,1200],[1500,3000],[600,1200]],aql_threshold_us=7200,
            fq_quantum_bytes=256,rc_per_thresh=50,rts_threshold=None,ct_baseband_rifs=None,
            ct_pshack=None,htt_max_amsdu=None,htt_max_ampdu=None,dscp_micro_vo_steering=True,
            fq_target_us=10000,fq_interval_us=50000,tcp_limit_output_bytes=262144,
            tcp_notsent_lowat=131072,distance_meters=None,encryption_mode='psk2')
    cpe=deepcopy(ap);cpe['aql_by_ac'][2]=[2100,4200]
    if regime=='unidir_dl_2flow':
        ap['aql_by_ac'][2]=[1800,3600];cpe=deepcopy(ap)
    hook=dict(short_retry_limit=retry,long_retry_limit=4 if retry==7 else 3,
              force_tx_status=1,ani_enable=None,airtime_flags=1,fq_limit=2048)
    def row(name,control=False):
        a,b=deepcopy(ap),deepcopy(cpe);h={**hook,'force_tx_status':0 if control else 1}
        endpoints=[]
        for p in (a,b):endpoints.append({**p,'ack_pps':None,'tcp_ack_vi':None,'ack_burst':None,**h})
        return dict(round_id='R32',iteration=name,workload_regime=regime,
            active_flow_count=REGIMES[regime][0],bidirectional=REGIMES[regime][1],
            ap_policy=a,cpe_policy=b,policy_key=json.dumps(endpoints,sort_keys=True,separators=(',',':')),
            ap_ack_pps=None,cpe_ack_pps=None,ap_tcp_ack_vi=None,cpe_tcp_ack_vi=None,ap_ack_burst=None,cpe_ack_burst=None,
            **h,goodput_mbps=100,dl_goodput_mbps=80,ul_goodput_mbps=20,jain_fairness=.8,
            p50_ms=4 if control else 2,p95_ms=4 if control else 2,p99_ms=4 if control else 2,
            packet_loss_pct=0,station_drops=0,restoration_verified=True,
            mac_tx_packets=count*100,mac_tx_retries=count,mac_retry_rate=.01,
            rtts_ms=[4 if control else 2]*(count*2),distance_meters=None,encryption_mode='psk2',
            associated_cpes=['Loco195'],window_kind='primary',block_mean_consistent=True,raw_rtts_matches_blocks=True,
            certified_wds_evidence={'counter_interface':'phy0-ap0.sta1','mac_counters_valid':True,
                'mac_block_sums_match_window':True,'source_receipt':source,'source_recipe':recipe})
    target,control=row('target'),row('control',True)
    control['dl_goodput_mbps']=90;control['ul_goodput_mbps']=10;control['jain_fairness']=.6
    if regime=='unidir_dl_2flow':
        target['dl_goodput_mbps']=100
        for r in (target,control):r['goodput_mbps']=r['dl_goodput_mbps'];r['ul_goodput_mbps']=0;r['jain_fairness']=1
    records={'records':[target,control]}
    blocks={'crossed':[], 'sequential':[]}
    for r in records['records']:
        for i in range(count):
            blocks['crossed'].append(dict(round_id='R32',treatment_id=r['iteration'],block_index=i,
                crossover_step=0 if r['iteration']=='target' else 1,
                observation={'goodput_rx_mbps':r['goodput_mbps'],'jain_fairness':r['jain_fairness'],
                             'p50_rtt_ms':r['p50_ms'],'p95_rtt_ms':r['p95_ms'],'p99_rtt_ms':r['p99_ms']},
                dl_goodput_mbps=r['dl_goodput_mbps'],ul_goodput_mbps=r['ul_goodput_mbps'],
                rtts_ms=[r['p50_ms']]*2,pings_sent=2,pings_rcvd=2,mac_tx_packets_delta=100,
                mac_tx_retries_delta=1,counter_interface='phy0-ap0.sta1'))
    projection={'source_inputs':{},'contrasts':[],'families':{}}
    for metric in REQUIRED_METRICS[regime]:
        projection['contrasts'].append(dict(regime=regime,target_policy_id=target['policy_key'],control_policy_id=control['policy_key'],
            round_ids=['R32'],paired_unit_ids=[{'round_id':'R32','block_index':i} for i in range(count)],metric=metric,
            direction='lower' if metric.startswith('p') else 'higher',effect_hl=-2 if metric.startswith('p') else .2 if metric=='jain_fairness' else 10,
            p_exact_rank=2**(1-count),holm324_adjusted_p=min(1,324*2**(1-count)),
            holm500_adjusted_p=min(1,500*2**(1-count)),comparability_status='COMPARABLE',
            source_hypothesis_id='h_'+metric,family324_key='new_padded324',family500_key='new_padded500'))
    known={'h_'+metric:2**(1-count) for metric in REQUIRED_METRICS[regime]}
    for size in (324,500):
        projection['families']['new_padded'+str(size)]={'declared_size':size,'known_hypotheses':known,
            'unknown_padding_count':size-len(known)}
    stats={'promotion_evidence':projection}
    if mutate:mutate(records,blocks,stats)
    paths={name:tmp_path/(name+'.json') for name in ['records','blocks','stats','manifest']}
    bindings=[dump(paths['records'],records),dump(paths['blocks'],blocks),dump(paths['manifest'],[source,recipe])]
    projection['source_inputs']={name+'_sha256':hashlib.sha256(paths[name].read_bytes()).hexdigest() for name in ['records','blocks','manifest']}
    if after_pins:after_pins(stats)
    bindings.append(dump(paths['stats'],stats))
    receipt_path=tmp_path/'accepted_stats_receipt.json'
    receipt=dump(receipt_path,{'bindings':bindings,'status':'SYNTHETIC_DISPOSABLE_NOT_PHYSICAL_PROOF'})
    args={name+'_path':path for name,path in paths.items()}
    args.update(receipt_path=receipt_path,expected_receipt_sha256=receipt['sha256'])
    return load_bound_evidence(**args),target['policy_key'],args


def test_all_explicit_gates_positive_only_then_canary_is_nonactuating(tmp_path):
    evidence,key,_=fixture_bundle(tmp_path)
    gate=evaluate_promotion(evidence,policy_id=key,regime='bidir_6flow')
    assert gate['status']=='PROMOTED_CERTIFIED_CANARY' and gate['reasons']==[]
    result=select_regime_policy(evidence,regime='bidir_6flow')
    assert result['status']=='PROMOTED_CERTIFIED_CANARY' and result['policy_id']==key
    assert result['automatic_execution_allowed'] is result['physical_safety_qualified'] is False
    assert result['ap_policy']!=result['cpe_policy']


def test_bound_statistics_cannot_claim_effect_absent_from_matched_source_pairs(tmp_path):
    def mutate(r,b,s):
        t,c=r['records'];c['dl_goodput_mbps']=t['dl_goodput_mbps'];c['ul_goodput_mbps']=t['ul_goodput_mbps'];c['jain_fairness']=t['jain_fairness']
        for row in b['crossed']:
            if row['treatment_id']=='control':
                row['dl_goodput_mbps']=t['dl_goodput_mbps'];row['ul_goodput_mbps']=t['ul_goodput_mbps'];row['observation']['jain_fairness']=t['jain_fairness']
    e,key,_=fixture_bundle(tmp_path,mutate=mutate)
    r=evaluate_promotion(e,policy_id=key,regime='bidir_6flow')
    assert r['status']=='BLOCKED'


@pytest.mark.parametrize('field,value',[
    ('block_mean_consistent',False),('block_mean_consistent',1),('raw_rtts_matches_blocks',False),
    ('restoration_verified',False),('restoration_verified',1),('packet_loss_pct',1),
    ('station_drops',1),('mac_tx_packets',0),('mac_tx_packets',True),('force_tx_status',None),('mac_retry_rate',.2),
    ('goodput_mbps',100.000000001),('jain_fairness',.8002),('p95_ms',True),
])
def test_source_quality_and_literal_rounding_cannot_be_overridden_by_stats(tmp_path,field,value):
    def mutate(r,b,s):r['records'][0][field]=value
    e,key,_=fixture_bundle(tmp_path,mutate=mutate)
    assert evaluate_promotion(e,policy_id=key,regime='bidir_6flow')['status']=='BLOCKED'


@pytest.mark.parametrize('what',['rtt_order','counter_sum','wrong_interface','unknown_wmm','stats_regime',
                                'stats_policy','units','bool_unit','duplicate_source_block','p_bool','n4_fake_significance','scope','missing_metric','ambiguous_context'])
def test_false_scope_and_metadata_cannot_promote(tmp_path,what):
    def mutate(r,b,s):
        t=r['records'][0];c=s['promotion_evidence']['contrasts'][0]
        if what=='rtt_order':t['rtts_ms'][0]=9
        elif what=='counter_sum':b['crossed'][0]['mac_tx_packets_delta']=101
        elif what=='wrong_interface':b['crossed'][0]['counter_interface']='wifi0'
        elif what=='stats_regime':c['regime']='bidir_2flow'
        elif what=='stats_policy':c['target_policy_id']='label_not_exact_policy'
        elif what=='units':c['paired_unit_ids'][0]={'round_id':'R29','block_index':0}
        elif what=='bool_unit':c['paired_unit_ids'][1]['block_index']=True
        elif what=='duplicate_source_block':b['crossed'].append(deepcopy(b['crossed'][0]))
        elif what=='p_bool':c['p_exact_rank']=False
        elif what=='n4_fake_significance':
            for c in s['promotion_evidence']['contrasts']:c['p_exact_rank']=1e-9;c['holm324_adjusted_p']=1e-8;c['holm500_adjusted_p']=1e-8
        elif what=='missing_metric':s['promotion_evidence']['contrasts'].pop()
        elif what=='ambiguous_context':
            other=deepcopy(t);other['round_id']='R29';other['associated_cpes']=['Other'];r['records'].append(other)
    def scope(s):s['promotion_evidence']['source_inputs']['records_sha256']='0'*64
    e,key,args=fixture_bundle(tmp_path,count=4 if what=='n4_fake_significance' else 16,
                            mutate=mutate,after_pins=scope if what=='scope' else None)
    request={'AP':{'BE':[3600,2,3,7]},'CPE':{'BE':[1800,3,5,7]}} if what=='unknown_wmm' else None
    assert evaluate_promotion(e,policy_id=key,regime='bidir_6flow',requested_wmm=request)['status']=='BLOCKED'


def test_n4_does_not_inherit_another_regime_significance(tmp_path):
    e,key,_=fixture_bundle(tmp_path,regime='bidir_2flow',count=4)
    r=select_regime_policy(e,regime='bidir_2flow')
    assert r['status']=='BLOCKED'
    assert any('HOLM' in reason for reason in r['candidates'][0]['reasons'])
    assert evaluate_promotion(e,policy_id=key,regime='bidir_6flow')['status']=='BLOCKED'


def test_unidir_total_GP_contrast_is_DL_only_when_source_algebra_exact(tmp_path):
    def mutate(r,b,s):
        for c in s['promotion_evidence']['contrasts']:
            if c['metric']=='dl_goodput_mbps':c['metric']='goodput_rx_mbps'
    e,key,_=fixture_bundle(tmp_path,regime='unidir_dl_2flow',mutate=mutate)
    gate=evaluate_promotion(e,policy_id=key,regime='unidir_dl_2flow')
    assert gate['status']=='PROMOTED_CERTIFIED_CANARY'
    support=next(x for x in gate['statistical_support'] if x['required_metric']=='dl_goodput_mbps')
    assert support['source_metric']=='goodput_rx_mbps' and support['DL_equals_total_GP_verified'] is True
    assert select_regime_policy(e,regime='unidir_dl_2flow')['ap_policy']['fq_quantum_bytes']==256


def test_unidir_GP_alias_never_bypasses_nonzero_UL_or_claims_n4_significance(tmp_path):
    def mutate(r,b,s):
        for c in s['promotion_evidence']['contrasts']:
            if c['metric']=='dl_goodput_mbps':c['metric']='goodput_rx_mbps'
    e,key,_=fixture_bundle(tmp_path,count=4,regime='unidir_dl_2flow',mutate=mutate)
    assert evaluate_promotion(e,policy_id=key,regime='unidir_dl_2flow')['status']=='BLOCKED'


def test_unidir_cannot_relabel_real_bidir_total_GP_as_DL(tmp_path):
    def mutate(r,b,s):
        for c in s['promotion_evidence']['contrasts']:
            if c['metric']=='dl_goodput_mbps':c['metric']='goodput_rx_mbps'
        r['records'][1]['ul_goodput_mbps']=1
        b['crossed'][-1]['ul_goodput_mbps']=1
    e,key,_=fixture_bundle(tmp_path,regime='unidir_dl_2flow',mutate=mutate)
    assert evaluate_promotion(e,policy_id=key,regime='unidir_dl_2flow')['status']=='BLOCKED'


def test_prior_uncertified_source_issue_is_not_a_wireless_failure_but_true_negative_quarantines(tmp_path):
    def mutate(r,b,s):
        old=deepcopy(r['records'][0]);old['round_id']='R26'
        del old['block_mean_consistent'];old['summary_consistency']={'consistent':False}
        r['records'].append(old)
    e,key,_=fixture_bundle(tmp_path,mutate=mutate)
    r=evaluate_promotion(e,policy_id=key,regime='bidir_6flow')
    assert r['status']=='PROMOTED_CERTIFIED_CANARY'
    assert len(r['prior_uncertified_observations_not_used_for_certification'])==1


@pytest.mark.parametrize('change',[{'packet_loss_pct':5},{'station_drops':1},{'restoration_verified':False}])
def test_known_prior_negative_same_package_never_reenters_via_new_certification(tmp_path,change):
    def mutate(r,b,s):
        old=deepcopy(r['records'][0]);old['round_id']='R26';del old['block_mean_consistent'];old.update(change)
        r['records'].append(old)
    e,key,_=fixture_bundle(tmp_path,mutate=mutate)
    r=evaluate_promotion(e,policy_id=key,regime='bidir_6flow')
    assert r['status']=='BLOCKED' and 'KNOWN_NEGATIVE_WHOLE_PACKAGE_IN_CONTEXT' in r['reasons']


def test_optional_retry53_never_autoenrolled_by_name_and_alias_is_not_wmm(tmp_path):
    e,key,_=fixture_bundle(tmp_path,retry=5)
    assert select_regime_policy(e,regime='bidir_6flow')['status']=='ABSTAIN'
    explicit=select_regime_policy(e,regime='bidir_6flow',policy_id=key,requested_alias='tail_retry53')
    assert explicit['status']=='PROMOTED_CERTIFIED_CANARY'
    assert 'NOT_EVIDENCE' in explicit['alias_diagnostic']


def test_tampered_stats_or_receipt_rejected_without_flag_trust(tmp_path):
    _,_,args=fixture_bundle(tmp_path)
    args['stats_path'].write_text('{"all_pass":true}')
    with pytest.raises(ValueError,match='binding'):load_bound_evidence(**args)
    args['receipt_path'].write_text('{"status":"PASS"}')
    with pytest.raises(ValueError,match='pin'):load_bound_evidence(**args)


def test_source_manifest_is_hashed_and_only_frozen_paths_may_be_read(tmp_path):
    _,_,args=fixture_bundle(tmp_path)
    (tmp_path/'inputs'/'saved_recipe.txt').write_text('mutated')
    with pytest.raises(ValueError,match='Frozen source'):load_bound_evidence(**args)


@pytest.mark.parametrize('mutation',['wrong_size','missing_member','wrong_padding','forged_adjusted'])
def test_catalog_multiplicity_is_recomputed_not_trusted_flag_or_scalar(tmp_path,mutation):
    def mutate(r,b,s):
        p=s['promotion_evidence']
        f=p['families']['new_padded500']
        if mutation=='wrong_size':f['declared_size']=10
        elif mutation=='missing_member':del f['known_hypotheses']['h_p50_rtt_ms']
        elif mutation=='wrong_padding':f['unknown_padding_count']=0
        else:p['contrasts'][0]['holm500_adjusted_p']=p['contrasts'][0]['p_exact_rank']
    e,key,_=fixture_bundle(tmp_path,mutate=mutate)
    assert evaluate_promotion(e,policy_id=key,regime='bidir_6flow')['status']=='BLOCKED'


def test_remote_path_rejected_before_read_and_unsupported_regime_abstains(tmp_path):
    e,key,args=fixture_bundle(tmp_path)
    assert select_regime_policy(e,regime='unknown')['status']=='ABSTAIN'
    args['stats_path']='https://example.invalid/data'
    with pytest.raises(ValueError,match='offline'):load_bound_evidence(**args)


# Wave AE: local disposable contracts, never recorded physical outcomes.
def campaign_bundle(tmp_path, *, regime='bidir_8flow', mutate=None, count=16):
    base = 'unidir_dl_2flow' if regime == 'unidir_ul_2flow' else 'bidir_6flow'
    def adapt(records, blocks, stats):
        rows=records['records']; contrasts=stats['promotion_evidence']['contrasts']
        distance, coverage = (3000,6) if regime=='covclass6_3km' else (6000,13) if regime=='covclass13_6km' else (None,None)
        for row in rows:
            row['workload_regime']='bidir_6flow' if coverage is not None else regime
            row['active_flow_count']=8 if regime=='bidir_8flow' else 2 if regime=='unidir_ul_2flow' else 6
            row['distance_meters']=distance
            row['coverage_class']=coverage
            row['source_failure_metadata']={'crash':False,'disqualified':False}
            row['certified_wds_evidence'].update(coverage_class=coverage,physical_distance_verified=False)
            row['jain_fairness']=1 if regime=='unidir_ul_2flow' else .75 if row['iteration']=='target' else .5
            if regime=='unidir_ul_2flow':
                row['ul_goodput_mbps']=row['goodput_mbps'];row['dl_goodput_mbps']=0
            pair=json.loads(row['policy_key'])
            for end, policy in zip(('ap_policy','cpe_policy'),pair):
                row[end]['distance_meters']=distance;policy['distance_meters']=distance
            row['policy_key']=json.dumps(pair,sort_keys=True,separators=(',',':'))
        for block in blocks['crossed']:
            block['observation']['jain_fairness']=1 if regime=='unidir_ul_2flow' else .75 if block['treatment_id']=='target' else .5
            if regime=='unidir_ul_2flow':
                block['ul_goodput_mbps']=block['observation']['goodput_rx_mbps'];block['dl_goodput_mbps']=0
        for contrast in contrasts:
            contrast.update(regime=rows[0]['workload_regime'],target_policy_id=rows[0]['policy_key'],control_policy_id=rows[1]['policy_key'])
            if contrast['metric']=='jain_fairness':contrast['effect_hl']=.25
            if regime=='unidir_ul_2flow' and contrast['metric']=='dl_goodput_mbps':contrast['metric']='ul_goodput_mbps'
        if mutate:mutate(records,blocks,stats)
    return fixture_bundle(tmp_path,regime=base,count=count,mutate=adapt)


@pytest.mark.parametrize('regime',['covclass6_3km','covclass13_6km','bidir_8flow','unidir_ul_2flow'])
def test_ae_new_exact_regimes_have_a_real_source_bound_positive_path(tmp_path,regime):
    e,key,_=campaign_bundle(tmp_path,regime=regime)
    gate=evaluate_promotion(e,policy_id=key,regime=regime)
    assert gate['status']=='PROMOTED_CERTIFIED_CANARY',gate
    assert select_regime_policy(e,regime=regime,policy_id=key)['status']=='PROMOTED_CERTIFIED_CANARY'
    assert gate['automatic_execution_allowed'] is False


@pytest.mark.parametrize('mutation',['class_missing','class_wrong','class_bool','distance_wrong','endpoint_unknown'])
def test_ae_coverage_alias_never_substitutes_for_exact_timing_context(tmp_path,mutation):
    def mutate(r,b,s):
        row=r['records'][0]
        if mutation=='class_missing':row['coverage_class']=None
        elif mutation=='class_wrong':row['coverage_class']=13
        elif mutation=='class_bool':row['coverage_class']=True
        elif mutation=='distance_wrong':row['distance_meters']=6000
        else:row['ap_policy']['distance_meters']=None
    e,key,_=campaign_bundle(tmp_path,regime='covclass6_3km',mutate=mutate)
    assert evaluate_promotion(e,policy_id=key,regime='covclass6_3km')['status']=='BLOCKED'


def test_ae_ul_total_alias_requires_exact_zero_DL_not_label(tmp_path):
    def mutate(r,b,s):
        for c in s['promotion_evidence']['contrasts']:
            if c['metric']=='ul_goodput_mbps':c['metric']='goodput_rx_mbps'
    e,key,_=campaign_bundle(tmp_path,regime='unidir_ul_2flow',mutate=mutate)
    gate=evaluate_promotion(e,policy_id=key,regime='unidir_ul_2flow')
    assert gate['status']=='PROMOTED_CERTIFIED_CANARY',gate
    support=next(c for c in gate['statistical_support'] if c['required_metric']=='ul_goodput_mbps')
    assert support['UL_equals_total_GP_verified'] is True


@pytest.mark.parametrize('regime',['bidir_12flow','unmeasured_PtMP'])
def test_ae_unsafe_or_unobserved_regimes_cannot_autoenroll(tmp_path,regime):
    e,key,_=fixture_bundle(tmp_path)
    assert select_regime_policy(e,regime=regime)['status']=='ABSTAIN'
    assert evaluate_promotion(e,policy_id=key,regime=regime)['status']=='BLOCKED'


@pytest.mark.parametrize('reason',['crash','disqualified'])
def test_ae_source_crash_cannot_be_overridden_by_good_ping_or_stats(tmp_path,reason):
    def mutate(r,b,s):r['records'][0]['source_failure_metadata'][reason]=True
    e,key,_=campaign_bundle(tmp_path,mutate=mutate)
    gate=evaluate_promotion(e,policy_id=key,regime='bidir_8flow')
    assert 'SOURCE_CRASH_OR_DISQUALIFICATION' in gate['reasons']


@pytest.mark.parametrize('scope',[[],['R32','R32'],['r32'],[True],'R32',['R31'],['R32','R31']])
def test_ae_round_scope_is_exact_and_cannot_invent_or_shrink_source_rounds(tmp_path,scope):
    e,key,_=fixture_bundle(tmp_path)
    assert evaluate_promotion(e,policy_id=key,regime='bidir_6flow',round_ids=scope)['status']=='BLOCKED'
    assert select_regime_policy(e,regime='bidir_6flow',policy_id=key,round_ids=scope)['status']!='PROMOTED_CERTIFIED_CANARY'


def test_ae_explicit_direct_scope_discloses_prior_source_failure_without_repair(tmp_path):
    def mutate(r,b,s):
        old=deepcopy(r['records'][0]);old.update(round_id='R28',block_mean_consistent=False)
        r['records'].append(old)
    e,key,_=fixture_bundle(tmp_path,mutate=mutate)
    assert evaluate_promotion(e,policy_id=key,regime='bidir_6flow')['status']=='BLOCKED'
    gate=evaluate_promotion(e,policy_id=key,regime='bidir_6flow',round_ids=['R32'])
    assert gate['status']=='PROMOTED_CERTIFIED_CANARY',gate
    assert gate['older_source_certifications_outside_requested_scope']==[{'round_id':'R28','iteration':'target','block_mean_consistent':False}]
    assert 'within_link_repetitions_not_independent_sector_trials' in gate['eligibility_limits']


@pytest.mark.parametrize('change',[{'packet_loss_pct':5},{'station_drops':1},{'restoration_verified':False},
                                   {'source_failure_metadata':{'crash':True,'disqualified':True}}])
def test_ae_direct_round_scope_cannot_hide_real_historical_negative(tmp_path,change):
    def mutate(r,b,s):
        old=deepcopy(r['records'][0]);old.update(round_id='R28',block_mean_consistent=False,**change)
        r['records'].append(old)
    e,key,_=fixture_bundle(tmp_path,mutate=mutate)
    gate=evaluate_promotion(e,policy_id=key,regime='bidir_6flow',round_ids=['R32'])
    assert gate['status']=='BLOCKED' and 'KNOWN_NEGATIVE_WHOLE_PACKAGE_IN_CONTEXT' in gate['reasons']


def test_ae_scoped_stats_may_not_borrow_other_round_or_retry_profile(tmp_path):
    def mutate(r,b,s):
        for c in s['promotion_evidence']['contrasts']:c['round_ids']=['R28','R32']
    e,key,_=fixture_bundle(tmp_path,mutate=mutate)
    assert evaluate_promotion(e,policy_id=key,regime='bidir_6flow',round_ids=['R32'])['status']=='BLOCKED'


def test_ae_new_manifest_envelope_still_verifies_only_its_frozen_paths(tmp_path):
    e,key,args=fixture_bundle(tmp_path)
    manifest=json.loads(args['manifest_path'].read_text())
    dump(args['manifest_path'],{'schema_version':1,'entries':manifest})
    stats=json.loads(args['stats_path'].read_text())
    stats['promotion_evidence']['source_inputs']['manifest_sha256']=hashlib.sha256(args['manifest_path'].read_bytes()).hexdigest()
    dump(args['stats_path'],stats)
    receipt=json.loads(args['receipt_path'].read_text())
    receipt['bindings']=[dump(path,json.loads(path.read_text())) for path in (args['records_path'],args['blocks_path'],args['stats_path'],args['manifest_path'])]
    args['expected_receipt_sha256']=dump(args['receipt_path'],receipt)['sha256']
    bound=load_bound_evidence(**args)
    assert evaluate_promotion(bound,policy_id=key,regime='bidir_6flow')['status']=='PROMOTED_CERTIFIED_CANARY'
    (tmp_path/'inputs'/'saved_recipe.txt').write_text('altered')
    with pytest.raises(ValueError,match='Frozen source'):load_bound_evidence(**args)


def test_ae_ul_GP_alias_cannot_hide_nonzero_downlink_or_nonmatching_direction(tmp_path):
    def mutate(r,b,s):
        r['records'][1]['dl_goodput_mbps']=1
        for c in s['promotion_evidence']['contrasts']:
            if c['metric']=='ul_goodput_mbps':c['metric']='goodput_rx_mbps'
    e,key,_=campaign_bundle(tmp_path,regime='unidir_ul_2flow',mutate=mutate)
    assert evaluate_promotion(e,policy_id=key,regime='unidir_ul_2flow')['status']=='BLOCKED'



def test_ae_new_campaign_python_sum_mean_is_exact_not_epsilon_or_numpy_mean(tmp_path):
    def mutate(r,b,s):
        target=r['records'][0]
        target['goodput_mbps']=.15
        target['certified_wds_evidence']['block_mean_float_consistent']=True
        for i,block in enumerate(x for x in b['crossed'] if x['treatment_id']=='target'):
            block['observation']['goodput_rx_mbps']=.1 if i%2==0 else .2
    e,key,_=campaign_bundle(tmp_path,mutate=mutate)
    gate=evaluate_promotion(e,policy_id=key,regime='bidir_8flow')
    assert 'LITERAL_PYTHON_FLOAT_MEAN_MISMATCH_goodput_mbps' in gate['reasons']
    assert 'LITERAL_MEAN_MISMATCH_goodput_mbps' not in gate['reasons']



@pytest.mark.parametrize('regime',['covclass6_3km','covclass13_6km','bidir_8flow'])
def test_ae_new_mappings_include_observed_asymmetric_AF3_without_changing_legacy_preset(tmp_path,regime):
    def mutate(r,b,s):
        for row in r['records']:
            row['airtime_flags']=3
            pair=json.loads(row['policy_key'])
            for p in pair:p['airtime_flags']=3
            row['policy_key']=json.dumps(pair,sort_keys=True,separators=(',',':'))
        for c in s['promotion_evidence']['contrasts']:
            c['target_policy_id']=r['records'][0]['policy_key'];c['control_policy_id']=r['records'][1]['policy_key']
    e,key,_=campaign_bundle(tmp_path,regime=regime,mutate=mutate)
    assert select_regime_policy(e,regime=regime)['status']=='PROMOTED_CERTIFIED_CANARY'
    if regime.startswith('covclass'):
        assert select_regime_policy(e,regime='bidir_6flow')['status']=='ABSTAIN'


@pytest.mark.parametrize('field,value',[('restoration_verified',False),('restoration_verified',1),
                                         ('station_drops',1),('station_drops',True)])
def test_ae_recorded_block_health_cannot_be_masked_by_positive_window_summary(tmp_path,field,value):
    def mutate(r,b,s):b['crossed'][0]['observation'][field]=value
    e,key,_=campaign_bundle(tmp_path,mutate=mutate)
    assert evaluate_promotion(e,policy_id=key,regime='bidir_8flow')['status']=='BLOCKED'
