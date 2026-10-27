"""Disposable offline source views; these fixtures are not physical evidence."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import (
    EvidenceViewPaths, SUPPORTED_REGIMES, dyadic_mean_audit, evaluate_policy,
    load_multi_regime_evidence, select_policy, load_operator_evidence,
    evaluate_operator_policy, select_operator_policy, OPERATOR_MODES,
)


def dump(path, value):
    path.write_bytes((json.dumps(value, sort_keys=True, allow_nan=False)+'\n').encode())
    return dict(path=str(path), bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def make_view(tmp_path, *, name='AH', round_id='R45', regime='bidir_6flow',
              gp_loss=0, count=16, mutate=None, prior=None):
    base=tmp_path/name; base.mkdir(); inputs=base/'inputs';inputs.mkdir()
    receipt=dump(inputs/'saved_receipt.json',{'disposable_source':True})
    recipe=dump(inputs/'saved_recipe.txt',{'disposable_recipe_not_executable':True})
    distance,coverage=(3000,6) if regime=='covclass6_3km' else (6000,13) if regime=='covclass13_6km' else (None,None)
    unidir=regime in ('unidir_dl_2flow','unidir_ul_2flow','unidir_ul_8flow_hammer')
    workload='bidir_6flow' if coverage else regime
    def row(target):
        endpoint=dict(aql_by_ac=[[300,600],[600,1200],[1100,2200] if target else [5000,12000],[600,1200]],
            aql_threshold_us=7200,fq_quantum_bytes=256,rc_per_thresh=50,rts_threshold=None,
            ct_baseband_rifs=None,ct_pshack=None,htt_max_amsdu=None,htt_max_ampdu=None,
            dscp_micro_vo_steering=True,fq_target_us=10000,fq_interval_us=50000,
            tcp_limit_output_bytes=262144,tcp_notsent_lowat=131072,distance_meters=distance,encryption_mode='psk2')
        ap=deepcopy(endpoint);cpe=deepcopy(endpoint)
        if target and not unidir:cpe['aql_by_ac'][2]=[2200,4400]
        hooks=dict(short_retry_limit=7,long_retry_limit=4,force_tx_status=int(target),
                   ani_enable=None,airtime_flags=1,fq_limit=2048 if target else 8192)
        pair=[{**p,'ack_pps':None,'tcp_ack_vi':None,'ack_burst':None,**hooks} for p in (ap,cpe)]
        gp=(100 if target else 96) if unidir else (100-gp_loss if target else 100)
        ul=(gp if regime in ('unidir_ul_2flow','unidir_ul_8flow_hammer') else 0) if unidir else (30 if target else 20)
        dl=(gp if regime=='unidir_dl_2flow' else 0) if unidir else gp-ul
        return dict(round_id=round_id,iteration='target' if target else 'control',workload_regime=workload,
            active_flow_count=8 if regime=='unidir_ul_8flow_hammer' else 2 if unidir else 8 if regime=='bidir_8flow' else 6,bidirectional=not unidir,
            policy_key=json.dumps(pair,sort_keys=True,separators=(',',':')),ap_policy=ap,cpe_policy=cpe,
            **hooks,ap_ack_pps=None,cpe_ack_pps=None,ap_tcp_ack_vi=None,cpe_tcp_ack_vi=None,
            ap_ack_burst=None,cpe_ack_burst=None,associated_cpes=['Loco195'],distance_meters=distance,
            encryption_mode='psk2',coverage_class=coverage,window_kind='primary',
            source_failure_metadata={'crash':False,'disqualified':False},
            goodput_mbps=gp,dl_goodput_mbps=dl,ul_goodput_mbps=ul,jain_fairness=1 if unidir else .75 if target else .5,
            p50_ms=2 if target else 4,p95_ms=2 if target else 4,p99_ms=2 if target else 4,
            packet_loss_pct=0,station_drops=0,restoration_verified=True,
            mac_tx_packets=100*count,mac_tx_retries=count*(1 if target else 4),
            mac_retry_rate=.01 if target else .04,rtts_ms=[2 if target else 4]*(2*count),
            certified_wds_evidence={'counter_interface':'phy0-ap0.sta1','source_receipt':receipt,'source_recipe':recipe,
                                    'coverage_class':coverage,'physical_distance_verified':False})
    target,control=row(True),row(False)
    records={'records':[target,control]};blocks={'crossed':[],'sequential':[]}
    for r in records['records']:
        for i in range(count):
            blocks['crossed'].append(dict(round_id=round_id,treatment_id=r['iteration'],block_index=i,
                crossover_step=0 if r['iteration']=='target' else 1,dl_goodput_mbps=r['dl_goodput_mbps'],
                ul_goodput_mbps=r['ul_goodput_mbps'],rtts_ms=[r['p50_ms']]*2,pings_sent=2,pings_rcvd=2,
                mac_tx_packets_delta=100,mac_tx_retries_delta=1 if r['iteration']=='target' else 4,
                counter_interface='phy0-ap0.sta1',observation=dict(goodput_rx_mbps=r['goodput_mbps'],
                    jain_fairness=r['jain_fairness'],p50_rtt_ms=r['p50_ms'],p95_rtt_ms=r['p95_ms'],p99_rtt_ms=r['p99_ms'],
                    station_drops=0,restoration_verified=True,packet_loss_pct=0)))
    metrics=['p50_rtt_ms','p95_rtt_ms','p99_rtt_ms']+(['goodput_rx_mbps'] if unidir else ['ul_goodput_mbps','jain_fairness'])
    contrasts=[];p=2**(1-count)
    for metric in metrics:
        hl=-2 if metric.startswith('p') else 4 if metric=='goodput_rx_mbps' else 10 if metric=='ul_goodput_mbps' else .25
        contrasts.append(dict(source_hypothesis_id='h_'+metric,regime=workload,
            target_policy_id=target['policy_key'],control_policy_id=control['policy_key'],round_ids=[round_id],
            paired_unit_ids=[dict(round_id=round_id,block_index=i) for i in range(count)],metric=metric,
            direction='lower' if metric.startswith('p') else 'higher',effect_hl=hl,p_exact_rank=p,
            holm500_adjusted_p=min(1,500*p),family500_key='scoped500',comparability_status='WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON'))
    stats={'promotion_evidence':dict(source_inputs={},contrasts=contrasts,families={
        'scoped500':dict(declared_size=500,known_hypotheses={c['source_hypothesis_id']:p for c in contrasts},unknown_padding_count=500-len(contrasts))})}
    if prior:
        saved=json.loads(prior.records_path.read_text());sb=json.loads(prior.blocks_path.read_text())
        records['records']+=saved['records'];blocks['crossed']+=sb['crossed']
    if mutate:mutate(records,blocks,stats)
    paths={k:base/(k+'.json') for k in ('records','blocks','stats','manifest')}
    bindings=[dump(paths['records'],records),dump(paths['blocks'],blocks),dump(paths['manifest'],[receipt,recipe])]
    stats['promotion_evidence']['source_inputs']={k+'_sha256':hashlib.sha256(paths[k].read_bytes()).hexdigest() for k in ('records','blocks','manifest')}
    bindings.append(dump(paths['stats'],stats))
    path=base/'accepted_fixture_receipt.json';pin=dump(path,{'bindings':bindings})
    config=EvidenceViewPaths(name,**{k+'_path':v for k,v in paths.items()},receipt_path=path,expected_receipt_sha256=pin['sha256'])
    return config,target['policy_key'],control['policy_key']


def evaluate(tmp_path, *, mode='STRICT', regime='bidir_6flow', **kwargs):
    config,target,control=make_view(tmp_path,regime=regime,**kwargs)
    evidence=load_multi_regime_evidence(current=config)
    return evaluate_policy(evidence,regime=regime,round_id='R45',policy_id=target,control_policy_id=control,mode=mode)


def make_operator_view(tmp_path, *, regime='bidir_6flow', distance=None, mutate=None, coverage_class=None, **kwargs):
    """160-sample disposable source, never an invented physical measurement."""
    def prepare(records,blocks,stats):
        replacements={}
        for row in records['records']:
            old=row['policy_key']
            row['active_flow_count']={'bidir_2flow':2,'bidir_4flow':4}.get(regime,row['active_flow_count'])
            row['rtts_ms']=[row['p50_ms']]*160
            if distance is not None:
                row['distance_meters']=distance
                row['coverage_class']=coverage_class if coverage_class is not None else {100:0,1000:2,1500:3,3000:6,4500:10,6000:13,7500:16,9000:20,10500:23,12000:27,13500:30,14000:31,15000:33}[distance]
                row['certified_wds_evidence']['coverage_class']=row['coverage_class']
                if distance==100:
                    row['certified_wds_evidence'].update(slot_time_us=9,ack_timeout_us=18,
                        effective_timing_independently_verified=False)
                for end in ('ap_policy','cpe_policy'):row[end]['distance_meters']=distance
                pair=json.loads(old)
                for end in pair:end['distance_meters']=distance
                row['policy_key']=json.dumps(pair,sort_keys=True,separators=(',',':'))
                replacements[old]=row['policy_key']
        for block in blocks['crossed']:
            block['rtts_ms']*=5;block['pings_sent']=block['pings_rcvd']=10
            block['crossover_step']=(block['block_index']+(block['treatment_id']=='control'))%2
        for contrast in stats['promotion_evidence']['contrasts']:
            for key in ('target_policy_id','control_policy_id'):
                contrast[key]=replacements.get(contrast[key],contrast[key])
        if mutate:mutate(records,blocks,stats)
    cfg,_,_=make_view(tmp_path,regime=regime,mutate=prepare,**kwargs)
    rows=json.loads(cfg.records_path.read_text())['records']
    return cfg,rows[0]['policy_key'],rows[1]['policy_key']


def make_as_operator_view(tmp_path, *, round_id='R61', regime='bidir_6flow', distance=3000,
                          p50_reversal=False, mutate=None, coverage_class=None, **kwargs):
    """Shared saved timing declarations on disposable R61-R75 fixtures only."""
    def prepare(records, blocks, stats):
        coverage = coverage_class if coverage_class is not None else {100:0,1000:2,1500:3,3000:6,4500:10,6000:13,7500:16,9000:20,10500:23,12000:27,13500:30,14000:31,15000:33}[distance]
        slot, ack = {0:(9,18),2:(15,30),3:(18,36),6:(27,54),10:(39,78),13:(48,96),16:(57,114),20:(69,138),23:(78,156),26:(87,174),27:(90,180),30:(99,198),31:(102,204),33:(108,216)}[coverage]
        for row in records['records']:
            row.update(slot_time_us=slot, ack_timeout_us=ack)
            row['certified_wds_evidence'].update(slot_time_us=slot, ack_timeout_us=ack,
                slot_ack_source='SHARED_PAYLOAD_TREATMENT_KNOBS', saved_context_credited=True,
                effective_timing_independently_verified=False)
        if p50_reversal:
            import numpy as np
            for block in blocks['crossed']:
                control = block['treatment_id'] == 'control'
                block['rtts_ms'] = ([4]*6+[10]*4 if control else
                    [5]*6+[6]*4 if block['block_index'] == 15 else [2]*10)
                for metric, value in zip(('p50_rtt_ms','p95_rtt_ms','p99_rtt_ms'), np.percentile(block['rtts_ms'], [50,95,99])):
                    block['observation'][metric] = float(value)
            for row in records['records']:
                row['rtts_ms'] = [r for b in blocks['crossed'] if b['treatment_id']==row['iteration'] for r in b['rtts_ms']]
                for metric, value in zip(('p50_ms','p95_ms','p99_ms'), np.percentile(row['rtts_ms'],[50,95,99])):
                    row[metric] = float(value)
            projection = stats['promotion_evidence']
            family = projection['families']['scoped500']
            for contrast in projection['contrasts']:
                metric = contrast['metric']
                if metric.startswith('p'):
                    contrast['effect_hl'] = -2 if metric == 'p50_rtt_ms' else -8
                contrast['p_exact_rank'] = 4/65536 if metric == 'p50_rtt_ms' else 2/65536
                family['known_hypotheses'][contrast['source_hypothesis_id']] = contrast['p_exact_rank']
            adjusted = {}
            running = 0
            for i, (hypothesis, p) in enumerate(sorted(family['known_hypotheses'].items(), key=lambda x:(x[1],x[0]))):
                running = max(running, min(1,(500-i)*p)); adjusted[hypothesis] = running
            for contrast in projection['contrasts']:
                contrast['holm500_adjusted_p'] = adjusted[contrast['source_hypothesis_id']]
        if mutate:
            mutate(records, blocks, stats)
    return make_operator_view(tmp_path, round_id=round_id, regime=regime, distance=distance, mutate=prepare, coverage_class=coverage_class, **kwargs)


@pytest.mark.parametrize('round_id,regime,distance', [
    ('R61','bidir_6flow',3000), ('R62','bidir_6flow',6000), ('R63','bidir_8flow',100),
    ('R64','bidir_4flow',100), ('R65','bidir_6flow',100)])
def test_au_five_new_round_identities_have_strict_positive_fixture_path(tmp_path, round_id, regime, distance):
    cfg, target, control = make_as_operator_view(tmp_path, round_id=round_id, regime=regime, distance=distance, gp_loss=1.25)
    result = evaluate_operator_policy(load_operator_evidence(current=cfg), regime=regime, round_id=round_id,
        policy_id=target, control_policy_id=control, distance_meters=distance)
    assert result['status'] == 'ELIGIBLE_OFFLINE_strict_goodput_preservation', result
    assert len(result['paired_block_wins']) == 5
    assert all(x == dict(wins=16,pairs=16) for x in result['paired_block_wins'].values())
    assert not result['automatic_execution_allowed'] and not result['physical_acceptance']


def test_au_r63_p50_exception_never_becomes_strict_five_outcome_qualification(tmp_path):
    cfg, target, control = make_as_operator_view(tmp_path, round_id='R63', regime='bidir_8flow',
        distance=100, p50_reversal=True, gp_loss=-.125)
    evidence = load_operator_evidence(current=cfg)
    result = evaluate_operator_policy(evidence, regime='bidir_8flow', round_id='R63',
        policy_id=target, control_policy_id=control, distance_meters=100)
    assert result['status'] == 'BLOCKED'
    assert 'NOT_16_OF_16_FAVORABLE_p50_rtt_ms' in result['reasons']
    assert result['paired_block_wins']['p50_rtt_ms'] == dict(wins=15,pairs=16)
    assert all(x['wins']==16 for m,x in result['paired_block_wins'].items() if m!='p50_rtt_ms')
    assert result['utility']['observed_total_goodput_loss_pct'] < 0
    selected = select_operator_policy(evidence, regime='bidir_8flow', distance_meters=100)
    assert selected['status'] == 'BLOCKED' and selected['selected'] is None
    assert any(p['round_id']=='R63' for p in selected['observed_points'])


@pytest.mark.parametrize('round_id,distance', [('R61',3000),('R62',6000)])
@pytest.mark.parametrize('defect', ['wrong_slot','missing_ack','unproved_effective_claim','wrong_shared_source'])
def test_au_long_distance_new_rounds_require_shared_saved_timing_without_effective_proof(tmp_path, round_id, distance, defect):
    def mutate(records, blocks, stats):
        e = records['records'][0]['certified_wds_evidence']
        if defect == 'wrong_slot': e['slot_time_us'] += 1
        elif defect == 'missing_ack': e.pop('ack_timeout_us')
        elif defect == 'unproved_effective_claim': e['effective_timing_independently_verified'] = True
        else: e['slot_ack_source'] = 'ROOT_RECEIPT_ONLY'
    cfg, target, control = make_as_operator_view(tmp_path, round_id=round_id, distance=distance, mutate=mutate)
    result = evaluate_operator_policy(load_operator_evidence(current=cfg), regime='bidir_6flow',
        round_id=round_id, policy_id=target, control_policy_id=control, distance_meters=distance)
    assert result['status'] == 'BLOCKED', result


@pytest.mark.parametrize('distance',[100,3000,6000])
@pytest.mark.parametrize('mode',OPERATOR_MODES)
def test_operator_distance_classes_and_utilities_have_true_positive_path(tmp_path,distance,mode):
    cfg,t,c=make_operator_view(tmp_path,round_id='R50',distance=distance,gp_loss=1.25)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),regime='bidir_6flow',
        round_id='R50',policy_id=t,control_policy_id=c,mode=mode,distance_meters=distance)
    assert result['status']=='ELIGIBLE_OFFLINE_'+mode,result
    assert all(v=={'wins':16,'pairs':16} for v in result['paired_block_wins'].values())
    assert not result['automatic_execution_allowed'] and not result['physical_acceptance']


@pytest.mark.parametrize('regime',['bidir_2flow','bidir_4flow'])
def test_operator_additional_workloads_are_typed_and_context_scoped(tmp_path,regime):
    cfg,t,c=make_operator_view(tmp_path,regime=regime,round_id='R55')
    evidence=load_operator_evidence(current=cfg)
    result=select_operator_policy(evidence,regime=regime)
    assert result['selected']['round_id']=='R55',result
    assert result['observed_points'] and result['pareto_frontier']
    assert result['selected']['policy_id']==t
    assert select_policy(evidence,regime=regime)['selected'] is None


@pytest.mark.parametrize('distance',[100,3000,6000])
def test_unknown_distance_never_satisfies_a_requested_class(tmp_path,distance):
    cfg,t,c=make_operator_view(tmp_path,round_id='R50')
    result=select_operator_policy(load_operator_evidence(current=cfg),regime='bidir_6flow',distance_meters=distance)
    assert result['selected'] is None and not result['observed_points']
    assert 'REQUESTED_DISTANCE_CONTEXT_NOT_RECORDED' in result['evaluations'][0]['reasons']


@pytest.mark.parametrize('loss,strict,directional',[(2,True,True),(2.0001,False,True),(15,False,True),(15.0001,False,False)])
def test_operator_goodput_limits_use_exact_inclusive_arithmetic(tmp_path,loss,strict,directional):
    cfg,t,c=make_operator_view(tmp_path,round_id='R50',gp_loss=loss)
    evidence=load_operator_evidence(current=cfg)
    for mode,expected in zip(OPERATOR_MODES,(strict,directional)):
        result=evaluate_operator_policy(evidence,regime='bidir_6flow',round_id='R50',policy_id=t,control_policy_id=c,mode=mode)
        assert result['status'].startswith('ELIGIBLE_') is expected,result


@pytest.mark.parametrize('what',['retry_raised','win_missing','sample_missing','loss','restore','forged_hl','bad_history'])
def test_operator_cannot_bypass_source_or_joint_statistical_gates(tmp_path,what):
    def mutate(records,blocks,stats):
        row=records['records'][0]
        own=[b for b in blocks['crossed'] if b['treatment_id']=='target']
        if what=='retry_raised':
            row['mac_tx_retries']=80;row['mac_retry_rate']=.05
            for b in own:b['mac_tx_retries_delta']=5
        elif what=='win_missing':own[0]['observation']['p99_rtt_ms']=5
        elif what=='sample_missing':own[0]['pings_sent']=own[0]['pings_rcvd']=9;own[0]['rtts_ms'].pop();row['rtts_ms'].pop()
        elif what=='loss':row['packet_loss_pct']=1
        elif what=='restore':row['restoration_verified']=False
        elif what=='forged_hl':stats['promotion_evidence']['contrasts'][0]['effect_hl']=-100
        else:
            past=deepcopy(row);past['round_id']='R49';past['restoration_verified']=False;records['records'].append(past)
    cfg,t,c=make_operator_view(tmp_path,round_id='R50',mutate=mutate)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),regime='bidir_6flow',round_id='R50',policy_id=t,control_policy_id=c)
    assert result['status'].startswith('ELIGIBLE_') is (what=='retry_raised'),result
    if what=='retry_raised':assert not result['retry_fraction']['target_strictly_lower']


def test_operator_round_extension_does_not_widen_legacy_loader(tmp_path):
    cfg,_,_=make_operator_view(tmp_path,round_id='R56')
    with pytest.raises(ValueError,match='R1..R47'):load_multi_regime_evidence(current=cfg)
    assert load_operator_evidence(current=cfg)


@pytest.mark.parametrize('mode',OPERATOR_MODES)
@pytest.mark.parametrize('difference',['distance','topology'])
def test_operator_abstains_across_eligible_contexts_and_round_scope_resolves(tmp_path,mode,difference):
    prior,_,_=make_operator_view(tmp_path,name='prior_operator',round_id='R48',distance=3000)
    def topology(records,blocks,stats):
        if difference=='topology':
            for row in records['records']:row['associated_cpes']=['OTHER_RECORDED_PEER']
    cfg,_,_=make_operator_view(tmp_path,name='current_operator',round_id='R49',
        distance=6000 if difference=='distance' else 3000,mutate=topology)
    records=json.loads(cfg.records_path.read_text());blocks=json.loads(cfg.blocks_path.read_text())
    records['records']+=json.loads(prior.records_path.read_text())['records']
    blocks['crossed']+=json.loads(prior.blocks_path.read_text())['crossed']
    dump(cfg.records_path,records);dump(cfg.blocks_path,blocks)
    stats=json.loads(cfg.stats_path.read_text())
    stats['promotion_evidence']['source_inputs']={k+'_sha256':hashlib.sha256(getattr(cfg,k+'_path').read_bytes()).hexdigest()
        for k in ('records','blocks','manifest')}
    dump(cfg.stats_path,stats)
    pins=[dict(path=str(getattr(cfg,k+'_path')),bytes=getattr(cfg,k+'_path').stat().st_size,
        sha256=hashlib.sha256(getattr(cfg,k+'_path').read_bytes()).hexdigest()) for k in ('records','blocks','stats','manifest')]
    receipt=dump(cfg.receipt_path,{'bindings':pins})
    cfg=EvidenceViewPaths(**{**vars(cfg),'expected_receipt_sha256':receipt['sha256']})
    evidence=load_operator_evidence(current=cfg,prior_views=(prior,))
    result=select_operator_policy(evidence,regime='bidir_6flow',mode=mode)
    assert result['status']=='BLOCKED' and result['selected'] is None,result
    assert result['reason']=='AMBIGUOUS_ELIGIBLE_CONTEXTS'
    assert len(result['eligible_contexts'])==2 and len(result['evaluations'])==2
    assert result['pareto_frontier'] and result['observed_points']
    scoped=select_operator_policy(evidence,regime='bidir_6flow',mode=mode,round_ids=['R48'])
    assert scoped['selected']['round_id']=='R48',scoped


def test_operator_balanced_order_is_required_independently_of_favorable_wins(tmp_path):
    def mutate(records,blocks,stats):
        for b in blocks['crossed']:b['crossover_step']=int(b['treatment_id']=='control')
    cfg,t,c=make_operator_view(tmp_path,round_id='R50',mutate=mutate)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),regime='bidir_6flow',
        round_id='R50',policy_id=t,control_policy_id=c)
    assert result['status']=='BLOCKED' and 'BALANCED_8AB_8BA_DESIGN_REQUIRED' in result['reasons']


def make_retry_preserving_view(tmp_path, *, mutate=None, **kwargs):
    """One real synthetic tail loss:9x2ms+5ms vs control10x4ms in one block."""
    import numpy as np
    def prepare(records,blocks,stats):
        row=records['records'][0]
        own=[b for b in blocks['crossed'] if b['treatment_id']=='target']
        own[0]['rtts_ms']=[2]*9+[5]
        for name,value in zip(('p50_rtt_ms','p95_rtt_ms','p99_rtt_ms'),np.percentile(own[0]['rtts_ms'],[50,95,99])):
            own[0]['observation'][name]=float(value)
        row['rtts_ms']=[v for b in own for v in b['rtts_ms']]
        assert row['p99_ms']==float(np.percentile(row['rtts_ms'],99))
        if mutate:mutate(records,blocks,stats)
    return make_operator_view(tmp_path,round_id='R59',distance=100,mutate=prepare,**kwargs)


def test_retry_preserving_profile_is_four_outcomes_and_never_silently_qualifies_all_five(tmp_path):
    cfg,t,c=make_retry_preserving_view(tmp_path,gp_loss=1.25)
    evidence=load_operator_evidence(current=cfg)
    result=evaluate_operator_policy(evidence,regime='bidir_6flow',round_id='R59',policy_id=t,control_policy_id=c,
        mode='strict_goodput_AND_lower_retry',distance_meters=100)
    assert result['status']=='ELIGIBLE_OFFLINE_strict_goodput_AND_lower_retry',result
    assert result['paired_block_wins']['p99_rtt_ms']==dict(wins=15,pairs=16)
    assert result['profile_contrast_scope']['complete_five_outcome_qualification'] is False
    assert result['retry_fraction']['target_strictly_lower'] is True
    assert result['utility']['retry_cost_is_diagnostic'] is False
    diagnostic=result['diagnostic_statistics']['p99_rtt_ms']
    assert diagnostic['status']=='SOURCE_CHECKED_DIAGNOSTIC' and diagnostic['wins']==15
    assert diagnostic['HL']==-2 and diagnostic['holm500_adjusted_p'] is not None
    assert diagnostic['used_for_primary_profile_eligibility'] is False
    strict=evaluate_operator_policy(evidence,regime='bidir_6flow',round_id='R59',policy_id=t,control_policy_id=c,
        mode='strict_goodput_preservation',distance_meters=100)
    assert strict['status']=='BLOCKED' and 'NOT_16_OF_16_FAVORABLE_p99_rtt_ms' in strict['reasons']


@pytest.mark.parametrize('what',['equal_retry','worse_retry','missing_primary','slot','ack','effective_claim','packet_loss'])
def test_retry_preserving_named_profile_cannot_bypass_any_required_boundary(tmp_path,what):
    def mutate(records,blocks,stats):
        row=records['records'][0]
        if what in ('equal_retry','worse_retry'):
            retry=4 if what=='equal_retry' else 5
            row['mac_tx_retries']=16*retry;row['mac_retry_rate']=retry/100
            for b in blocks['crossed']:
                if b['treatment_id']=='target':b['mac_tx_retries_delta']=retry
        elif what=='missing_primary':
            stats['promotion_evidence']['contrasts']=[c for c in stats['promotion_evidence']['contrasts'] if c['metric']!='jain_fairness']
        elif what=='slot':row['certified_wds_evidence']['slot_time_us']=10
        elif what=='ack':row['certified_wds_evidence']['ack_timeout_us']=19
        elif what=='effective_claim':row['certified_wds_evidence']['effective_timing_independently_verified']=True
        else:row['packet_loss_pct']=1
    cfg,t,c=make_retry_preserving_view(tmp_path,mutate=mutate)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),regime='bidir_6flow',round_id='R59',
        policy_id=t,control_policy_id=c,mode='strict_goodput_AND_lower_retry',distance_meters=100)
    assert result['status']=='BLOCKED',result


@pytest.mark.parametrize('loss,expected',[(2,True),(2.0001,False),(10,False)])
def test_retry_preserving_profile_keeps_the_strict_two_percent_budget(tmp_path,loss,expected):
    cfg,t,c=make_retry_preserving_view(tmp_path,gp_loss=loss)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),regime='bidir_6flow',round_id='R59',
        policy_id=t,control_policy_id=c,mode='strict_goodput_AND_lower_retry',distance_meters=100)
    assert result['status'].startswith('ELIGIBLE_') is expected,result


def test_future_operator_round_rejected_before_any_evidence_access():
    class NoRead:
        def parse(self):raise AssertionError('Future round must not cause any evidence read')
    result=evaluate_operator_policy(NoRead(),regime='bidir_6flow',round_id='R135',policy_id='x',control_policy_id='y')
    assert result['status']=='BLOCKED'
    assert select_operator_policy(NoRead(),regime='bidir_6flow',round_ids=['R135'])['status']=='BLOCKED'


@pytest.mark.parametrize('what',['absent','tampered'])
def test_optional_p99_statistic_is_explicitly_unknown_without_a_false_or_new_primary_gate(tmp_path,what):
    def mutate(records,blocks,stats):
        contrasts=stats['promotion_evidence']['contrasts']
        if what=='absent':stats['promotion_evidence']['contrasts']=[c for c in contrasts if c['metric']!='p99_rtt_ms']
        else:next(c for c in contrasts if c['metric']=='p99_rtt_ms')['effect_hl']=-100
    cfg,t,c=make_retry_preserving_view(tmp_path,mutate=mutate)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),regime='bidir_6flow',round_id='R59',
        policy_id=t,control_policy_id=c,mode='strict_goodput_AND_lower_retry',distance_meters=100)
    assert result['status']=='ELIGIBLE_OFFLINE_strict_goodput_AND_lower_retry',result
    diagnostic=result['diagnostic_statistics']['p99_rtt_ms']
    assert diagnostic['status']=='UNKNOWN' and diagnostic['HL'] is diagnostic['holm500_adjusted_p'] is None
    assert diagnostic['wins']==15 and diagnostic['used_for_primary_profile_eligibility'] is False


@pytest.mark.parametrize('ul_gain',[39.9,40,80,81])
def test_directional_expected_gain_band_never_vetoes_a_larger_benefit(tmp_path,ul_gain):
    def mutate(records,blocks,stats):
        row=records['records'][0];row['ul_goodput_mbps']=20*(1+ul_gain/100)
        row['dl_goodput_mbps']=row['goodput_mbps']-row['ul_goodput_mbps']
        for block in blocks['crossed']:
            if block['treatment_id']=='target':
                block['ul_goodput_mbps']=row['ul_goodput_mbps'];block['dl_goodput_mbps']=row['dl_goodput_mbps']
        for contrast in stats['promotion_evidence']['contrasts']:
            if contrast['metric']=='ul_goodput_mbps':contrast['effect_hl']=row['ul_goodput_mbps']-20
    # Decimal dyadic means must be exact too; 39.9/81 can fail that independent guard.
    cfg,t,c=make_operator_view(tmp_path,round_id='R50',mutate=mutate)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),regime='bidir_6flow',round_id='R50',policy_id=t,control_policy_id=c,mode=OPERATOR_MODES[1])
    if ul_gain==39.9:assert 'DIRECTIONAL_UL_GAIN_BELOW_40PCT' in result['reasons']
    if ul_gain in (40,80):assert not any('UL_GAIN' in reason for reason in result['reasons'])
    if ul_gain==81:assert not any('UL_GAIN' in reason for reason in result['reasons'])


@pytest.mark.parametrize('regime',SUPPORTED_REGIMES)
def test_all_six_regimes_have_real_positive_contract_path_without_actuation(tmp_path,regime):
    result=evaluate(tmp_path,regime=regime)
    assert result['status']=='ELIGIBLE_OFFLINE_STRICT',result
    assert not result['automatic_execution_allowed'] and not result['physical_acceptance']
    assert result['total_goodput_noninferiority_claim'] is False


@pytest.mark.parametrize('loss,strict',[ (0,True),(2,True),(2.0001,False),(10,False)])
def test_prespecified_observed_2percent_boundary_is_not_a_fitted_threshold(tmp_path,loss,strict):
    cfg,t,c=make_view(tmp_path,gp_loss=loss)
    evidence=load_multi_regime_evidence(current=cfg)
    result=evaluate_policy(evidence,regime='bidir_6flow',round_id='R45',policy_id=t,control_policy_id=c)
    assert result['utility']['passes_observed_2pct_floor'] is strict
    assert result['status'].startswith('ELIGIBLE_') is strict
    directional=evaluate_policy(evidence,regime='bidir_6flow',round_id='R45',policy_id=t,control_policy_id=c,mode='DIRECTIONAL')
    assert directional['status']=='ELIGIBLE_OFFLINE_DIRECTIONAL'
    assert directional['utility']['permits_total_goodput_cost'] and not directional['total_goodput_noninferiority_claim']


@pytest.mark.parametrize('arm',[0,1])
@pytest.mark.parametrize('field,value',[('packet_loss_pct',1),('restoration_verified',False),
    ('restoration_verified',1),('station_drops',1),('station_drops',True),('mac_tx_packets',False)])
def test_both_current_arms_health_and_types_are_conjunctive(tmp_path,arm,field,value):
    def mutate(r,b,s):r['records'][arm][field]=value
    assert evaluate(tmp_path,mutate=mutate)['status']=='BLOCKED'


@pytest.mark.parametrize('what',['rtt_order','fraction','np_only','bool_counter','block_loss','block_restore',
    'counter_sum','wrong_wds','missing_source','wrong_coverage','unknown_hook','forged_HL','wrong_round',
    'bool_unit','missing_unit','different_control','forged_p','bad_padding','wrong_adjusted','missing_outcome'])
def test_no_flag_or_label_can_override_saved_scope_quality_or_statistics(tmp_path,what):
    def mutate(r,b,s):
        t=r['records'][0];projection=s['promotion_evidence'];c=projection['contrasts'][0]
        if what=='rtt_order':t['rtts_ms'][0]=3
        elif what=='fraction':t['jain_fairness']=.7500000000001
        elif what=='np_only':
            t['jain_fairness']=.1
            for block in b['crossed']:
                if block['treatment_id']=='target':block['observation']['jain_fairness']=.1
        elif what=='bool_counter':b['crossed'][0]['mac_tx_packets_delta']=True
        elif what=='block_loss':b['crossed'][0]['pings_rcvd']=1
        elif what=='block_restore':b['crossed'][0]['observation']['restoration_verified']=False
        elif what=='counter_sum':b['crossed'][0]['mac_tx_packets_delta']=101
        elif what=='wrong_wds':b['crossed'][0]['counter_interface']='phy0'
        elif what=='missing_source':t['certified_wds_evidence']['source_receipt']={**t['certified_wds_evidence']['source_receipt'],'sha256':'0'*64}
        elif what=='wrong_coverage':t['distance_meters']=3000
        elif what=='unknown_hook':t['force_tx_status']=None
        elif what=='forged_HL':c['effect_hl']=-10
        elif what=='wrong_round':c['round_ids']=['R44']
        elif what=='bool_unit':c['paired_unit_ids'][1]['block_index']=True
        elif what=='missing_unit':c['paired_unit_ids'].pop()
        elif what=='different_control':c['control_policy_id']='a different package'
        elif what=='forged_p':c['p_exact_rank']=0
        elif what=='bad_padding':projection['families']['scoped500']['unknown_padding_count']=0
        elif what=='wrong_adjusted':c['holm500_adjusted_p']=c['p_exact_rank']
        else:projection['contrasts'].pop()
    assert evaluate(tmp_path,mutate=mutate)['status']=='BLOCKED'


@pytest.mark.parametrize('target_retries',[4,5])
def test_retry_gate_uses_counts_not_a_rounded_lower_rate_claim(tmp_path,target_retries):
    def mutate(r,b,s):
        t=r['records'][0];t['mac_tx_retries']=16*target_retries;t['mac_retry_rate']=target_retries/100
        for block in b['crossed']:
            if block['treatment_id']=='target':block['mac_tx_retries_delta']=target_retries
    result=evaluate(tmp_path,mutate=mutate)
    assert result['status']=='BLOCKED' and 'TARGET_MAC_RETRY_FRACTION_NOT_LOWER' in result['reasons']


def test_n4_cannot_borrow_16pair_holm_evidence(tmp_path):
    assert evaluate(tmp_path,count=4)['status']=='BLOCKED'


def test_directional_does_not_bypass_missing_fairness_or_latency(tmp_path):
    def mutate(r,b,s):s['promotion_evidence']['contrasts'].pop()
    assert evaluate(tmp_path,mode='DIRECTIONAL',mutate=mutate)['status']=='BLOCKED'


def test_union_of_explicit_accepted_manifests_resolves_real_prior_source_refs(tmp_path):
    prior,t,c=make_view(tmp_path,name='prior',round_id='R32')
    current,_,_=make_view(tmp_path,name='current',prior=prior)
    one=load_multi_regime_evidence(current=current)
    no_prior=evaluate_policy(one,regime='bidir_6flow',round_id='R32',policy_id=t,control_policy_id=c)
    assert no_prior['status']=='BLOCKED'
    both=load_multi_regime_evidence(current=current,prior_views=(prior,))
    result=evaluate_policy(both,regime='bidir_6flow',round_id='R32',policy_id=t,control_policy_id=c)
    assert result['status']=='ELIGIBLE_OFFLINE_STRICT',result
    (tmp_path/'prior'/'inputs'/'saved_recipe.txt').write_text('tampered')
    with pytest.raises(ValueError,match='Frozen source'):load_multi_regime_evidence(current=current,prior_views=(prior,))


@pytest.mark.parametrize('which',['target','control'])
def test_true_historical_target_negative_quarantines_but_old_stock_failure_is_not_blanket(tmp_path,which):
    def mutate(r,b,s):
        row=deepcopy(r['records'][0 if which=='target' else 1]);row.update(round_id='R28',packet_loss_pct=5)
        r['records'].append(row)
    result=evaluate(tmp_path,mutate=mutate)
    assert result['status']==('BLOCKED' if which=='target' else 'ELIGIBLE_OFFLINE_STRICT')
    assert bool(result['historical_target_negatives']) is (which=='target')


def test_new_comparison_does_not_inherit_old_policy_or_regime_stats(tmp_path):
    def mutate(r,b,s):
        for c in s['promotion_evidence']['contrasts']:c['target_policy_id']='old AP1500/CPE2100 not new AP1100/CPE2200'
    assert evaluate(tmp_path,mutate=mutate)['status']=='BLOCKED'


def test_deterministic_selection_is_observed_package_only(tmp_path):
    cfg,t,c=make_view(tmp_path)
    evidence=load_multi_regime_evidence(current=cfg)
    a=select_policy(evidence,regime='bidir_6flow');b=select_policy(evidence,regime='bidir_6flow')
    assert a==b and a['selected']['policy_id']==t
    assert not a['automatic_execution_allowed']
    assert select_policy(evidence,regime='bidir_12flow')['status']=='ABSTAIN'
    assert select_policy(evidence,regime='bidir_6flow',round_ids=['R48'])['status']=='BLOCKED'
    assert select_policy(evidence,regime='bidir_6flow',mode='magic')['status']=='ABSTAIN'


def test_pin_mismatch_current_history_tamper_and_projection_scope_fail_at_load(tmp_path):
    prior,_,_=make_view(tmp_path,name='prior',round_id='R32')
    def mutate(r,b,s):r['records'][-1]['goodput_mbps']=99
    current,_,_=make_view(tmp_path,name='current',prior=prior,mutate=mutate)
    with pytest.raises(ValueError,match='prior record'):load_multi_regime_evidence(current=current,prior_views=(prior,))
    wrong=EvidenceViewPaths(**{**vars(prior),'expected_receipt_sha256':'0'*64})
    with pytest.raises(ValueError,match='pin'):load_multi_regime_evidence(current=wrong)



def test_zero_ulp_audit_is_not_just_fraction_or_float_flag(tmp_path):
    def mutate(r,b,s):
        r['records'][0]['jain_fairness']=.15
        for i,block in enumerate(x for x in b['crossed'] if x['treatment_id']=='target'):
            block['observation']['jain_fairness']=.1 if i%2==0 else .2
    cfg,t,c=make_view(tmp_path,mutate=mutate)
    evidence=load_multi_regime_evidence(current=cfg);data=evidence.parse()[cfg.name]
    row=data['records']['records'][0]
    audit=dyadic_mean_audit(row,data['blocks']['crossed'])['jain_fairness']
    assert audit['fraction_delta']=='0' and audit['ulp_error']>0 and audit['exact'] is False
    result=evaluate_policy(evidence,regime='bidir_6flow',round_id='R45',policy_id=t,control_policy_id=c)
    assert 'TARGET_FRACTION_OR_NUMPY_MEAN_NOT_ZERO_ULP' in result['reasons']


@pytest.mark.parametrize('negative',['packet_loss','station_drop','restoration'])
def test_historical_target_block_failure_cannot_hide_behind_healthy_window(tmp_path,negative):
    def mutate(r,b,s):
        old=deepcopy(r['records'][0]);old['round_id']='R28';r['records'].append(old)
        oldblocks=deepcopy([x for x in b['crossed'] if x['treatment_id']=='target'])
        for block in oldblocks:block['round_id']='R28'
        if negative=='packet_loss':oldblocks[0]['pings_rcvd']=1
        elif negative=='station_drop':oldblocks[0]['observation']['station_drops']=1
        else:oldblocks[0]['observation']['restoration_verified']=False
        b['crossed']+=oldblocks
    result=evaluate(tmp_path,mutate=mutate)
    assert result['status']=='BLOCKED' and result['historical_target_negatives']


@pytest.mark.parametrize('what',['boolean_metric','overflowing_numpy_reduction'])
def test_invalid_or_overflowing_metrics_fail_closed_without_nonfinite_output(tmp_path,what):
    def mutate(r,b,s):
        if what=='boolean_metric':r['records'][0]['goodput_mbps']=True
        else:
            r['records'][0]['goodput_mbps']=1e308
            for block in b['crossed']:
                if block['treatment_id']=='target':block['observation']['goodput_rx_mbps']=1e308
    result=evaluate(tmp_path,mutate=mutate)
    assert result['status']=='BLOCKED'
    json.dumps(result,allow_nan=False)


def coverage_mutation(kind):
    def mutate(records,blocks,stats):
        target,control=records['records']
        if kind=='control_wrong_class':
            control['coverage_class']=13
            control['certified_wds_evidence']['coverage_class']=13
        elif kind=='control_unknown':
            control['coverage_class']=None
            control['certified_wds_evidence']['coverage_class']=None
        elif kind=='target_class_bool':target['coverage_class']=True
        elif kind=='target_class_float':target['coverage_class']=6.0
        elif kind=='unsupported_class':target['coverage_class']=7
        elif kind=='wrong_timing':
            for row in records['records']:
                row['distance_meters']=6000
                pair=json.loads(row['policy_key'])
                for end,p in zip(('ap_policy','cpe_policy'),pair):
                    row[end]['distance_meters']=6000;p['distance_meters']=6000
                row['policy_key']=json.dumps(pair,sort_keys=True,separators=(',',':'))
            for c in stats['promotion_evidence']['contrasts']:
                c['target_policy_id']=target['policy_key'];c['control_policy_id']=control['policy_key']
        elif kind=='provenance_mismatch':target['certified_wds_evidence']['coverage_class']=13
        elif kind=='provenance_float':target['certified_wds_evidence']['coverage_class']=6.0
        elif kind=='physical_not_false':target['certified_wds_evidence']['physical_distance_verified']=0
        elif kind=='unknown_with_known_provenance':target['coverage_class']=None
    return mutate


@pytest.mark.parametrize('mode',['STRICT','DIRECTIONAL'])
@pytest.mark.parametrize('requested',['bidir_6flow','covclass6_3km'])
@pytest.mark.parametrize('kind',['control_wrong_class','control_unknown','target_class_bool','target_class_float',
    'unsupported_class','wrong_timing','provenance_mismatch','provenance_float','physical_not_false',
    'unknown_with_known_provenance'])
def test_generic_declared_coverage_cannot_bypass_alias_guard(tmp_path,mode,requested,kind):
    cfg,t,c=make_view(tmp_path,regime='covclass6_3km',mutate=coverage_mutation(kind))
    evidence=load_multi_regime_evidence(current=cfg)
    result=evaluate_policy(evidence,regime=requested,round_id='R45',policy_id=t,control_policy_id=c,mode=mode)
    assert result['status']=='BLOCKED',result
    assert select_policy(evidence,regime=requested,mode=mode)['status']!='ELIGIBLE_OFFLINE_'+mode


@pytest.mark.parametrize('mode',['STRICT','DIRECTIONAL'])
@pytest.mark.parametrize('coverage_regime',['covclass6_3km','covclass13_6km'])
@pytest.mark.parametrize('generic',[True,False])
def test_matching_known_coverage_is_valid_in_generic_and_alias_routes(tmp_path,mode,coverage_regime,generic):
    cfg,t,c=make_view(tmp_path,regime=coverage_regime)
    evidence=load_multi_regime_evidence(current=cfg)
    result=evaluate_policy(evidence,regime='bidir_6flow' if generic else coverage_regime,
                           round_id='R45',policy_id=t,control_policy_id=c,mode=mode)
    assert result['status']=='ELIGIBLE_OFFLINE_'+mode,result


@pytest.mark.parametrize('mode',['STRICT','DIRECTIONAL'])
@pytest.mark.parametrize('distance',[None,3000])
def test_both_unknown_coverage_legacy_context_is_not_inferred_from_distance(tmp_path,mode,distance):
    def mutate(records,blocks,stats):
        for row in records['records']:
            row['distance_meters']=distance
            pair=json.loads(row['policy_key'])
            for end,p in zip(('ap_policy','cpe_policy'),pair):
                row[end]['distance_meters']=distance;p['distance_meters']=distance
            row['policy_key']=json.dumps(pair,sort_keys=True,separators=(',',':'))
        for c in stats['promotion_evidence']['contrasts']:
            c['target_policy_id']=records['records'][0]['policy_key'];c['control_policy_id']=records['records'][1]['policy_key']
    assert evaluate(tmp_path,mode=mode,mutate=mutate)['status']=='ELIGIBLE_OFFLINE_'+mode


@pytest.mark.parametrize('mode',['STRICT','DIRECTIONAL'])
@pytest.mark.parametrize('requested',['bidir_6flow','covclass6_3km'])
def test_known_coverage_history_still_quarantines_the_same_context(tmp_path,mode,requested):
    def mutate(records,blocks,stats):
        old=deepcopy(records['records'][0]);old.update(round_id='R28',packet_loss_pct=5)
        records['records'].append(old)
    cfg,t,c=make_view(tmp_path,regime='covclass6_3km',mutate=mutate)
    result=evaluate_policy(load_multi_regime_evidence(current=cfg),regime=requested,
                           round_id='R45',policy_id=t,control_policy_id=c,mode=mode)
    assert result['status']=='BLOCKED' and result['historical_target_negatives']


@pytest.mark.parametrize('mode',['STRICT','DIRECTIONAL'])
@pytest.mark.parametrize('change',[
    {'restoration_verified':0},{'restoration_verified':1},{'restoration_verified':'false'},
    {'source_failure_metadata':{'crash':1,'disqualified':False}},
    {'source_failure_metadata':{'crash':'false','disqualified':False}},
    {'source_failure_metadata':{'crash':False,'disqualified':0}},
    {'source_failure_metadata':'false'},
])
def test_malformed_historical_metadata_is_not_silently_a_healthy_boolean(tmp_path,mode,change):
    def mutate(records,blocks,stats):
        old=deepcopy(records['records'][0]);old.update(round_id='R28',**change)
        records['records'].append(old)
    result=evaluate(tmp_path,mode=mode,mutate=mutate)
    assert result['status']=='BLOCKED',result


@pytest.mark.parametrize('mode',['STRICT','DIRECTIONAL'])
@pytest.mark.parametrize('restoration',[True,False,None,'ABSENT'])
def test_historical_real_bool_and_unknown_legacy_restoration_are_distinct(tmp_path,mode,restoration):
    def mutate(records,blocks,stats):
        old=deepcopy(records['records'][0]);old['round_id']='R28'
        if restoration=='ABSENT':
            del old['restoration_verified'];del old['source_failure_metadata']
        else:
            old['restoration_verified']=restoration
            if restoration is None:old['source_failure_metadata']=None
        records['records'].append(old)
    result=evaluate(tmp_path,mode=mode,mutate=mutate)
    if restoration is False:
        assert result['status']=='BLOCKED' and result['historical_target_negatives']
    else:
        assert result['status']=='ELIGIBLE_OFFLINE_'+mode,result
        assert not result['historical_target_negatives']
        assert bool(result['historical_target_unknown_metadata']) is (restoration is None or restoration=='ABSENT')


@pytest.mark.parametrize('round_id,regime,distance',[
    ('R66','bidir_2flow',100),('R67','bidir_8flow',100),('R68','bidir_6flow',4500),
    ('R69','bidir_6flow',9000),('R70','bidir_6flow',4500)])
def test_ay_new_rounds_and_declared_classes_have_guarded_synthetic_positive_path(tmp_path,round_id,regime,distance):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,regime=regime,distance=distance,gp_loss=1.25)
    evidence=load_operator_evidence(current=cfg)
    result=evaluate_operator_policy(evidence,round_id=round_id,regime=regime,policy_id=t,control_policy_id=c,distance_meters=distance)
    assert result['status']=='ELIGIBLE_OFFLINE_strict_goodput_preservation',result
    assert all(w==dict(wins=16,pairs=16) for w in result['paired_block_wins'].values())
    assert not result['automatic_execution_allowed'] and not result['physical_acceptance']


@pytest.mark.parametrize('round_id,distance',[('R68',4500),('R69',9000),('R70',4500)])
@pytest.mark.parametrize('defect',['wrong_class','wrong_slot','missing_ack','wrong_root_slot','effective_claim','wrong_provenance'])
def test_ay_new_declared_contexts_cannot_be_guessed_or_downgraded(tmp_path,round_id,distance,defect):
    def mutate(records,blocks,stats):
        row=records['records'][0]
        e=row['certified_wds_evidence']
        if defect=='wrong_class':row['coverage_class']=6
        elif defect=='wrong_slot':e['slot_time_us']+=1
        elif defect=='missing_ack':e.pop('ack_timeout_us')
        elif defect=='wrong_root_slot':row['slot_time_us']+=1
        elif defect=='effective_claim':e['effective_timing_independently_verified']=True
        else:e['slot_ack_source']='ROOT_RECEIPT_ONLY'
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,distance=distance,mutate=mutate)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),round_id=round_id,regime='bidir_6flow',policy_id=t,control_policy_id=c,distance_meters=distance)
    assert result['status']=='BLOCKED',result


@pytest.mark.parametrize('round_id,regime,distance,loss',[
    ('R67','bidir_8flow',100,2.388110),('R68','bidir_6flow',4500,2.139503)])
def test_ay_observed_gp_failures_remain_visible_and_block_strict(tmp_path,round_id,regime,distance,loss):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,regime=regime,distance=distance,gp_loss=loss)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),round_id=round_id,regime=regime,policy_id=t,control_policy_id=c,distance_meters=distance)
    assert result['status']=='BLOCKED'
    assert 'OPERATOR_GOODPUT_DROP_LIMIT_EXCEEDED' in result['reasons']
    assert result['utility']['observed_total_goodput_loss_pct']>2


def test_ay_two_flow_lower_retry_observation_does_not_redefine_six_flow_only_profile(tmp_path):
    cfg,t,c=make_as_operator_view(tmp_path,round_id='R66',regime='bidir_2flow',distance=100)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),round_id='R66',regime='bidir_2flow',policy_id=t,control_policy_id=c,distance_meters=100,mode='strict_goodput_AND_lower_retry')
    assert result['status']=='BLOCKED'
    assert result['reasons']==['RETRY_PRESERVING_PROFILE_REQUIRES_BIDIR_6FLOW']


@pytest.mark.parametrize('distance',[4500,9000])
def test_ay_new_operator_contexts_do_not_widen_revision_fixed_legacy_gate(tmp_path,distance):
    cfg,t,c=make_as_operator_view(tmp_path,round_id='R45',distance=distance)
    result=evaluate_policy(load_multi_regime_evidence(current=cfg),round_id='R45',regime='bidir_6flow',policy_id=t,control_policy_id=c)
    assert result['status']=='BLOCKED'


@pytest.mark.parametrize('round_id,regime,distance',[
    ('R71','bidir_2flow',100),('R72','bidir_8flow',100),('R73','bidir_6flow',12000),
    ('R74','bidir_8flow',100),('R75','bidir_6flow',15000)])
def test_bc_new_contexts_have_synthetic_guarded_positive_path(tmp_path,round_id,regime,distance):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,regime=regime,distance=distance,gp_loss=1.25)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),round_id=round_id,
        regime=regime,policy_id=t,control_policy_id=c,distance_meters=distance)
    if distance==15000:
        assert result['status']=='BLOCKED',result
        assert 'COVERAGE_CLASS_EXCEEDS_SUPPORTED_POLICY_MAX31' in result['reasons']
    else:
        assert result['status']=='ELIGIBLE_OFFLINE_strict_goodput_preservation',result
    assert all(w==dict(wins=16,pairs=16) for w in result['paired_block_wins'].values())
    assert result['automatic_execution_allowed'] is result['physical_acceptance'] is False


@pytest.mark.parametrize('round_id,distance',[('R73',12000),('R75',15000)])
@pytest.mark.parametrize('defect',['wrong_class','fractional_class','wrong_slot','missing_ack',
    'wrong_root_slot','effective_claim','physical_claim','wrong_provenance'])
def test_bc_new_contexts_keep_all_explicit_timing_provenance_gates(tmp_path,round_id,distance,defect):
    def mutate(records,blocks,stats):
        row=records['records'][0];e=row['certified_wds_evidence']
        if defect=='wrong_class':row['coverage_class']=32
        elif defect=='fractional_class':row['coverage_class']=float(row['coverage_class'])
        elif defect=='wrong_slot':e['slot_time_us']+=1
        elif defect=='missing_ack':e.pop('ack_timeout_us')
        elif defect=='wrong_root_slot':row['slot_time_us']+=1
        elif defect=='effective_claim':e['effective_timing_independently_verified']=True
        elif defect=='physical_claim':e['physical_distance_verified']=True
        else:e['slot_ack_source']='ROOT_RECEIPT_ONLY'
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,distance=distance,mutate=mutate)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),round_id=round_id,
        regime='bidir_6flow',policy_id=t,control_policy_id=c,distance_meters=distance)
    assert result['status']=='BLOCKED',result


@pytest.mark.parametrize('distance',[12000,15000])
def test_bc_new_operator_classes_do_not_widen_legacy_revision_contract(tmp_path,distance):
    cfg,t,c=make_as_operator_view(tmp_path,round_id='R45',distance=distance)
    result=evaluate_policy(load_multi_regime_evidence(current=cfg),round_id='R45',
        regime='bidir_6flow',policy_id=t,control_policy_id=c)
    assert result['status']=='BLOCKED'


@pytest.mark.parametrize('round_id',['R72','R74'])
def test_bc_eight_flow_positive_gp_cannot_rescue_p50_nonunanimity(tmp_path,round_id):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,regime='bidir_8flow',distance=100,
        gp_loss=-.25,p50_reversal=True)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),round_id=round_id,
        regime='bidir_8flow',policy_id=t,control_policy_id=c,distance_meters=100)
    assert result['status']=='BLOCKED',result
    assert 'NOT_16_OF_16_FAVORABLE_p50_rtt_ms' in result['reasons']
    assert result['utility']['observed_total_goodput_loss_pct']<0


@pytest.mark.parametrize('round_id,distance', [('R76',1500),('R77',7500),('R78',10500),('R79',13500),('R80',7500)])
def test_bg_new_rounds_and_declared_classes_have_guarded_positive_path(tmp_path,round_id,distance):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,distance=distance,gp_loss=1.25)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),round_id=round_id,regime='bidir_6flow',policy_id=t,control_policy_id=c,distance_meters=distance)
    assert result['status']=='ELIGIBLE_OFFLINE_strict_goodput_preservation',result
    assert all(v=={'wins':16,'pairs':16} for v in result['paired_block_wins'].values())
    assert result['automatic_execution_allowed'] is result['physical_acceptance'] is False


@pytest.mark.parametrize('round_id,distance', [('R76',1500),('R77',7500),('R78',10500),('R79',13500)])
@pytest.mark.parametrize('defect', ['missing_root_slot','wrong_ack','provenance_not_shared','effective_timing_claim'])
def test_bg_new_classes_keep_shared_timing_evidence_mandatory(tmp_path,round_id,distance,defect):
    def mutate(records,blocks,stats):
        row=records['records'][0];e=row['certified_wds_evidence']
        if defect=='missing_root_slot':row.pop('slot_time_us')
        elif defect=='wrong_ack':e['ack_timeout_us']+=1
        elif defect=='provenance_not_shared':e['slot_ack_source']='INFERRED_FROM_CLASS'
        else:e['effective_timing_independently_verified']=True
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,distance=distance,gp_loss=1.25,mutate=mutate)
    result=evaluate_operator_policy(load_operator_evidence(current=cfg),round_id=round_id,regime='bidir_6flow',policy_id=t,control_policy_id=c,distance_meters=distance)
    assert result['status']=='BLOCKED',result


@pytest.mark.parametrize('distance',[1500,7500,10500,13500])
def test_bg_operator_classes_do_not_widen_legacy_coverage_routes(tmp_path,distance):
    cfg,t,c=make_as_operator_view(tmp_path,round_id='R45',distance=distance,gp_loss=1.25)
    result=evaluate_policy(load_multi_regime_evidence(current=cfg),round_id='R45',regime='bidir_6flow',policy_id=t,control_policy_id=c)
    assert result['status']=='BLOCKED',result


@pytest.mark.parametrize('round_id,regime,distance',[('R81','unidir_dl_2flow',100),('R82','unidir_ul_2flow',100),('R83','bidir_4flow',3000),('R84','bidir_4flow',6000),('R85','bidir_6flow',7500),('R86','bidir_4flow',9000)])
def test_bk_new_direction_workload_contexts_have_source_bound_positive_path(tmp_path,round_id,regime,distance):
    cfg,target,control=make_as_operator_view(tmp_path,round_id=round_id,regime=regime,distance=distance,gp_loss=1.25)
    out=evaluate_operator_policy(load_operator_evidence(current=cfg),regime=regime,round_id=round_id,
        policy_id=target,control_policy_id=control,distance_meters=distance)
    assert out['status']=='ELIGIBLE_OFFLINE_strict_goodput_preservation',out
    expected=4 if regime.startswith('unidir') else 5
    assert len(out['paired_block_wins'])==expected
    assert all(v=={'wins':16,'pairs':16} for v in out['paired_block_wins'].values())
    assert out['automatic_execution_allowed'] is out['physical_acceptance'] is False


@pytest.mark.parametrize('round_id,regime,distance',[('R81','unidir_dl_2flow',100),('R82','unidir_ul_2flow',100),('R83','bidir_4flow',3000),('R84','bidir_4flow',6000),('R85','bidir_6flow',7500),('R86','bidir_4flow',9000)])
@pytest.mark.parametrize('fault',['slot','ack','source','proof'])
def test_bk_every_new_context_retains_shared_timing_provenance(tmp_path,round_id,regime,distance,fault):
    def mutate(records,blocks,stats):
        row=records['records'][0]
        if fault=='slot':row.pop('slot_time_us')
        elif fault=='ack':row['certified_wds_evidence']['ack_timeout_us']+=1
        elif fault=='source':row['certified_wds_evidence'].pop('slot_ack_source')
        else:row['certified_wds_evidence']['effective_timing_independently_verified']=True
    cfg,target,control=make_as_operator_view(tmp_path,round_id=round_id,regime=regime,distance=distance,mutate=mutate)
    out=evaluate_operator_policy(load_operator_evidence(current=cfg),regime=regime,round_id=round_id,
        policy_id=target,control_policy_id=control,distance_meters=distance)
    assert out['status']=='BLOCKED'


@pytest.mark.parametrize('round_id',[f'R{n}' for n in range(81,87)])
def test_bk_operator_extension_keeps_revision47_api_no_read_boundary(round_id):
    class NoRead:
        def parse(self):raise AssertionError('Legacy API must reject new scope before reading')
    out=evaluate_policy(NoRead(),regime='bidir_6flow',round_id=round_id,policy_id='x',control_policy_id='y')
    assert out['status']=='BLOCKED'


@pytest.mark.parametrize('regime',['unidir_dl_2flow','unidir_ul_2flow'])
def test_bk_directional_ranking_never_uses_inactive_or_directional_jain_coordinates(regime):
    from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import _operator_cost_vector
    from fractions import Fraction
    row=dict(goodput_mbps=100,ul_goodput_mbps=object(),jain_fairness=object(),p95_ms=2,p99_ms=3,
        mac_tx_retries=2,mac_tx_packets=100)
    assert _operator_cost_vector(row,regime)==(Fraction(100),Fraction(-2),Fraction(-3),Fraction(-2,100))


@pytest.mark.parametrize('round_id,regime,distance', [('R87','unidir_dl_2flow',100),('R88','bidir_4flow',12000),('R89','bidir_4flow',14000),('R90','bidir_6flow',14000),('R91','bidir_2flow',3000),('R92','bidir_2flow',6000)])
def test_bo_new_round_context_has_source_bound_positive_path(tmp_path,round_id,regime,distance):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,regime=regime,distance=distance,gp_loss=1.25)
    out=evaluate_operator_policy(load_operator_evidence(current=cfg),regime=regime,round_id=round_id,
        policy_id=t,control_policy_id=c,distance_meters=distance)
    assert out['status']=='ELIGIBLE_OFFLINE_strict_goodput_preservation',out
    assert out['recorded_context']['coverage_class']=={100:0,12000:27,14000:31,3000:6,6000:13}[distance]
    assert out['automatic_execution_allowed'] is out['physical_acceptance'] is False


def test_bo_historical_class33_stays_loaded_but_cannot_emit_current_advice(tmp_path):
    cfg,t,c=make_as_operator_view(tmp_path,round_id='R75',distance=15000,gp_loss=1.25)
    evidence=load_operator_evidence(current=cfg)
    assert evidence.parse()[cfg.name]['records']['records'][0]['coverage_class']==33
    out=evaluate_operator_policy(evidence,round_id='R75',regime='bidir_6flow',policy_id=t,control_policy_id=c,distance_meters=15000)
    assert out['status']=='BLOCKED'
    assert 'COVERAGE_CLASS_EXCEEDS_SUPPORTED_POLICY_MAX31' in out['reasons']
    assert out['source_checks']['target']['dyadic_means']
    assert out['utility']['passes_operator_goodput_floor'] is True
    assert out['coverage_policy']['hardware_ceiling_verified'] is False


@pytest.mark.parametrize('defect',['wrong_slot','missing_ack','fractional_class','wrong_provenance','effective_claim','wrong_distance'])
def test_bo_class31_keeps_exact_timing_and_provenance_gates(tmp_path,defect):
    def mutate(records,blocks,stats):
        r=records['records'][0];e=r['certified_wds_evidence']
        if defect=='wrong_slot':r['slot_time_us']=108
        elif defect=='missing_ack':e.pop('ack_timeout_us')
        elif defect=='fractional_class':r['coverage_class']=31.0
        elif defect=='wrong_provenance':e['slot_ack_source']='INFERRED_FROM_DISTANCE'
        elif defect=='effective_claim':e['effective_timing_independently_verified']=True
        else:r['distance_meters']=15000
    cfg,t,c=make_as_operator_view(tmp_path,round_id='R90',distance=14000,mutate=mutate)
    out=evaluate_operator_policy(load_operator_evidence(current=cfg),regime='bidir_6flow',round_id='R90',policy_id=t,control_policy_id=c,distance_meters=14000)
    assert out['status']=='BLOCKED',out


@pytest.mark.parametrize('round_id,regime,distance,coverage', [
    ('R93','bidir_6flow',14000,31), ('R96','bidir_2flow',14000,31),
    ('R102','bidir_8flow',14000,31), ('R107','unidir_dl_2flow',14000,31),
    ('R108','unidir_ul_2flow',1000,2), ('R120','unidir_ul_2flow',12000,26),
    ('R134','unidir_ul_2flow',1000,2)])
def test_bqcf_new_source_contexts_have_guarded_positive_path(tmp_path,round_id,regime,distance,coverage):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,regime=regime,distance=distance,
                                coverage_class=coverage,gp_loss=1.25)
    out=evaluate_operator_policy(load_operator_evidence(current=cfg),regime=regime,round_id=round_id,
        policy_id=t,control_policy_id=c,distance_meters=distance,coverage_class=coverage)
    assert out['status']=='ELIGIBLE_OFFLINE_strict_goodput_preservation',out
    assert out['recorded_context']['coverage_class']==coverage
    assert out['automatic_execution_allowed'] is out['physical_acceptance'] is False


def test_bqcf_recipe_only_round_does_not_create_measurement_or_read_future_scope():
    class NoRead:
        def parse(self):raise AssertionError('Out-of-scope evidence must not be opened')
    out=evaluate_operator_policy(NoRead(),regime='bidir_6flow',round_id='R135',policy_id='x',control_policy_id='y')
    assert out['status']=='BLOCKED'


def source_package_mutation(fault=None):
    def mutate(records,blocks,stats):
        ids={}
        for row in records['records']:
            target=row['iteration']=='target'
            old=row['policy_key']
            controls=dict(rts_threshold='256' if target else 'off',ap_ack_clocking=target)
            row['new_source_controls']=controls
            pair=json.loads(old)
            for end,p in zip(('ap','cpe'),pair):
                row[end+'_policy']['rts_threshold']=256 if target else None
                p['rts_threshold']=row[end+'_policy']['rts_threshold']
                p['new_source_controls']=controls.copy() if end=='ap' else {'rts_threshold':controls['rts_threshold']}
            if target:
                if fault=='unknown':controls['guessed_control']=1
                elif fault=='bool':controls['ap_ack_clocking']=1
                elif fault=='leading_zero':controls['rts_threshold']='0256'
                elif fault=='rts_mismatch':row['cpe_policy']['rts_threshold']=None
                elif fault=='missing_ap':pair[0].pop('new_source_controls')
                elif fault=='cpe_ack':pair[1]['new_source_controls']['ap_ack_clocking']=True
            row['policy_key']=json.dumps(pair,sort_keys=True,separators=(',',':'))
            ids[old]=row['policy_key']
        for contrast in stats['promotion_evidence']['contrasts']:
            for key in ('target_policy_id','control_policy_id'):
                contrast[key]=ids[contrast[key]]
    return mutate


def test_bqcf_ul8_package_controls_and_active_alias_have_positive_path(tmp_path):
    cfg,t,c=make_as_operator_view(tmp_path,round_id='R134',regime='unidir_ul_8flow_hammer',distance=1000,
                                mutate=source_package_mutation())
    out=evaluate_operator_policy(load_operator_evidence(current=cfg),regime='unidir_ul_8flow_hammer',round_id='R134',
                                 policy_id=t,control_policy_id=c,distance_meters=1000,coverage_class=2)
    assert out['status']=='ELIGIBLE_OFFLINE_strict_goodput_preservation',out
    assert set(out['paired_block_wins'])=={'p50_rtt_ms','p95_rtt_ms','p99_rtt_ms','ul_goodput_mbps'}
    assert len(out['statistical_support'])==4


@pytest.mark.parametrize('fault',['unknown','bool','leading_zero','rts_mismatch','missing_ap','cpe_ack'])
def test_bqcf_package_controls_fail_closed_on_identity_mutation(tmp_path,fault):
    cfg,t,c=make_as_operator_view(tmp_path,round_id='R134',regime='unidir_ul_8flow_hammer',distance=1000,
                                mutate=source_package_mutation(fault))
    out=evaluate_operator_policy(load_operator_evidence(current=cfg),regime='unidir_ul_8flow_hammer',round_id='R134',
                                 policy_id=t,control_policy_id=c,distance_meters=1000)
    assert out['status']=='BLOCKED',out


def test_bqcf_class26_does_not_silently_match_default_class27_query(tmp_path):
    cfg,t,c=make_as_operator_view(tmp_path,round_id='R120',regime='unidir_ul_2flow',distance=12000,coverage_class=26)
    evidence=load_operator_evidence(current=cfg)
    out=evaluate_operator_policy(evidence,regime='unidir_ul_2flow',round_id='R120',policy_id=t,control_policy_id=c,distance_meters=12000)
    assert 'REQUESTED_DISTANCE_CONTEXT_NOT_RECORDED' in out['reasons']
    assert out['recorded_context']['coverage_class']==26
