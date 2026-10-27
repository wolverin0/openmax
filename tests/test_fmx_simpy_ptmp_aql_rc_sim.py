from dataclasses import replace
import importlib.util

import numpy as np
import pytest

from orchestration.autoresearch.fmx_offline_data import load_measurements
from tools.sim.fmx_simpy_ptmp_aql_rc_sim import (
    Scenario, calibrate, replication_interval, response_for_policy, simulate,
)


def test_calibration_keeps_both_rounds_and_drift_separate():
    records,_=load_measurements()
    calibration=calibrate(records)
    assert len(calibration['training'])==13
    assert not calibration['physical_validation']
    r1=response_for_policy(calibration,Scenario(calibration_round='R1',aql_low_us=5000,aql_high_us=12000,aql_threshold_us=24000,rc_per=50))
    r2=response_for_policy(calibration,Scenario(calibration_round='R2',aql_low_us=5000,aql_high_us=12000,aql_threshold_us=24000,rc_per=50))
    assert r2['goodput_mbps']>r1['goodput_mbps']
    assert r2['distance_to_calibration']==pytest.approx(0)
    with pytest.raises(ValueError,match='EACH'):
        calibrate([row for row in records if row.round_id=='R2'])


@pytest.mark.parametrize('field,value',[
    ('vendors',()),('vendors',('WA',)*17),('vendors',('invalid',)),
    ('horizon_s',float('inf')),('warmup_s',0.5),('offered_mbps',-1),
    ('dynamic_bw_rts',1),('txop_us',4001),('aql_low_us',0),('rc_per',28.5),
    ('max_events',0),('max_packets',True),('legacy_efficiency',0),('calibration_round','R3'),
])
def test_unsafe_or_unbounded_model_inputs_rejected(field,value):
    with pytest.raises(ValueError):
        replace(Scenario(),**{field:value}).validate()


def test_replication_intervals_are_not_packet_level_intervals():
    result=replication_interval([1,2,3])
    assert result['mean']==2 and result['lower']<2<result['upper']
    assert 'conditional' in result['scope']
    with pytest.raises(ValueError):
        replication_interval([1])


native_simpy=pytest.mark.skipif(importlib.util.find_spec('simpy') is None,
    reason='MANDATORY native SimPy integration BLOCKED: offline library unavailable')


@native_simpy
@pytest.mark.parametrize('cpes',[1,4,16])
def test_native_simpy_conservation_bounds_and_repeatable_seeds(cpes):
    records,_=load_measurements()
    calibration=calibrate(records)
    scenario=Scenario(vendors=tuple(('WA','XC','SXT','LBM5')[i%4] for i in range(cpes)),horizon_s=0.05,warmup_s=0.01)
    result=simulate(scenario,calibration)
    assert result==simulate(scenario,calibration)
    counts=result['counts']
    assert counts['arrivals']==sum(counts[key] for key in ('rejected','delivered','collision_lost'))+result['unfinished_at_horizon']
    assert result['max_pending_airtime_us']<=cpes*scenario.aql_high_us+1e-6
    assert result['events']<=scenario.max_events
    assert 0<=result['goodput_mbps']<=scenario.offered_mbps*1.5
    assert 1/cpes-1e-8<=result['jain_fairness']<=1+1e-8
    assert result['p50_ms']<=result['p95_ms']<=result['p99_ms']
    assert result['automatic_execution_allowed'] is False


@native_simpy
def test_native_zero_load_and_runtime_caps_fail_closed():
    records,_=load_measurements()
    calibration=calibrate(records)
    empty=simulate(Scenario(offered_mbps=0),calibration)
    assert empty['goodput_mbps']==0 and empty['unfinished_at_horizon']==0 and empty['p99_ms'] is None
    for scenario in (Scenario(max_packets=1),Scenario(max_events=1)):
        with pytest.raises(RuntimeError,match='cap'):
            simulate(scenario,calibration)


# Wave G uses a separate API; the legacy tests above remain unchanged.
from types import SimpleNamespace
import json
from tools.sim.fmx_simpy_ptmp_aql_rc_sim import (
    QueuePolicy,FlowSpec,PerACScenario,classify_micro,simulate_per_ac,
    multiflow_response,scenario_flows,wave_g_heldout,
)


def endpoint(low=2000,steering=False):
    return SimpleNamespace(aql_by_ac=((low,low*2),)*4,aql_threshold_us=low*4,
                           fq_quantum_bytes=300,rc_per_thresh=28,rts_threshold=None,
                           ct_baseband_rifs=None,ct_pshack=None,htt_max_amsdu=None,
                           htt_max_ampdu=None,dscp_micro_vo_steering=steering)


def regime_row(index,policy=None,round_id='R7'):
    p=policy or endpoint(1000+index*250)
    return SimpleNamespace(round_id=round_id,iteration=f'window{index}',workload_regime='bidir_6flow',
                           active_flow_count=6,bidirectional=True,ap_policy=p,cpe_policy=p,
                           policy_key=json.dumps([vars(p),vars(p)],sort_keys=True),goodput_mbps=80+index*5,
                           p50_ms=10+index,p95_ms=20+index,p99_ms=22+index,
                           packet_loss_pct=5 if index==1 else 0,restoration_verified=True)


@pytest.mark.parametrize('protocol,size,dscp,steering,expected',[
    ('UDP',255,0,True,('VO',46)),('ICMP',64,0,True,('VO',46)),
    ('UDP',256,0,True,('BE',0)),('TCP',64,0,True,('BE',0)),
    ('UDP',128,0,False,('BE',0)),('ICMP',128,46,False,('VO',46)),
])
def test_g_micro_classifier_is_explicit_assumption(protocol,size,dscp,steering,expected):
    f=FlowSpec('x',0,'DL',protocol,size,.1,dscp=dscp)
    assert classify_micro(f,QueuePolicy(dscp_micro_vo_steering=steering))==expected


@pytest.mark.parametrize('cpes',[1,4,16])
@native_simpy
def test_g_native_flow_conservation_inflight_and_seeds(cpes):
    policy=QueuePolicy(((500,1000),(1000,2000),(2000,4000),(5000,12000)),8000,300,True)
    s=PerACScenario(tuple(('WA','XC','SXT','LBM5')[i%4] for i in range(cpes)),policy,policy,horizon_s=.05,warmup_s=.01)
    flows=scenario_flows(cpes)
    r=simulate_per_ac(s,flows,{'goodput_mbps':80,'p50_ms':10})
    assert r==simulate_per_ac(s,flows,{'goodput_mbps':80,'p50_ms':10})
    assert r['counts']['arrivals']==sum(r['counts'][k] for k in ('rejected','delivered','collision_lost','unfinished'))
    assert sum(f['unfinished'] for f in r['flows'])==r['counts']['unfinished']
    assert r['pending_airtime_us']<=r['max_pending_airtime_us']+1e-6
    assert r['events']<=s.max_events and r['p50_ms']<=r['p95_ms']<=r['p99_ms']
    assert any(f['admission_ac']=='VO' and f['flow']['direction']=='UL' for f in r['flows'])
    assert any(f['admission_ac']=='BE' and f['flow']['direction']=='DL' for f in r['flows'])
    assert r['EF46_to_AC_VO']=='MODEL_ASSUMPTION_UNVERIFIED' and not r['physical_measurement']


@native_simpy
def test_g_sender_aql_and_uniform_baseline_are_different_models():
    ap=QueuePolicy(((100,200),(100,200),(100,200),(100,200)),1000,300,True)
    cpe=QueuePolicy(((5000,10000),)*4,20000,300,False)
    flows=[FlowSpec('down',0,'DL','TCP',1500,100),FlowSpec('up',0,'UL','TCP',1500,100)]
    r=simulate_per_ac(PerACScenario(ap_policy=ap,cpe_policy=cpe,horizon_s=.05,warmup_s=.01),flows,{'goodput_mbps':20,'p50_ms':10})
    assert r['flows'][0]['counts']['rejected']>r['flows'][1]['counts']['rejected']
    mixed=scenario_flows(1)
    q=simulate_per_ac(PerACScenario(ap_policy=ap,cpe_policy=cpe,horizon_s=.05,warmup_s=.01),mixed,{'goodput_mbps':20,'p50_ms':10},'pooled_uniform')
    assert {f['admission_ac'] for f in q['flows']}=={'BE'}


@native_simpy
def test_g_weighted_server_keeps_each_ac_alive():
    p=QueuePolicy(((25000,50000),)*4,200000,300)
    flows=[FlowSpec(ac,0,'DL','TCP',100,2,base_ac=ac) for ac in ('VO','VI','BE','BK')]
    r=simulate_per_ac(PerACScenario(ap_policy=p,horizon_s=.05,warmup_s=0,collision_probability=0),flows,{'goodput_mbps':1,'p50_ms':0})
    delivered=[f['counts']['delivered'] for f in r['flows']]
    assert delivered[0]>delivered[1]>delivered[2]>delivered[3]>0


@native_simpy
def test_g_empty_probe_population_is_not_bulk_latency_or_zero():
    flows=[FlowSpec('tcp',0,'DL','TCP',1500,10),FlowSpec('probe',0,'DL','ICMP',64,0)]
    r=simulate_per_ac(PerACScenario(horizon_s=.05,warmup_s=0),flows,{'goodput_mbps':20,'p50_ms':0})
    assert r['goodput_mbps']>0 and r['p99_ms'] is None and r['micro_latency_samples']==0


@pytest.mark.parametrize('field,value',[
    ('max_packets',True),('max_events',0),('ac_weights',(4,3,2,0)),('horizon_s',float('nan')),
    ('collision_probability',True),('legacy_efficiency',0),
    ('seed',-1),('seed',True),('seed',2**53+1),
])
def test_g_invalid_model_inputs_fail_closed(field,value):
    with pytest.raises(ValueError):replace(PerACScenario(),**{field:value}).validate(scenario_flows(1))


@native_simpy
def test_g_caps_and_unrecorded_ul_fail_closed():
    with pytest.raises(ValueError,match='UL'):
        simulate_per_ac(PerACScenario(cpe_policy=None),scenario_flows(1),{'goodput_mbps':80,'p50_ms':10})
    for change in ({'max_packets':1},{'max_events':1}):
        with pytest.raises(RuntimeError,match='cap'):
            simulate_per_ac(replace(PerACScenario(),**change),scenario_flows(1),{'goodput_mbps':80,'p50_ms':10})


@native_simpy
def test_g_heldout_is_matched_across_variants_and_has_no_target_response_leak():
    rows=[regime_row(i) for i in range(5)]
    a=wave_g_heldout(rows,2,horizon=.05)
    for per,baseline in zip(a['comparisons'][::2],a['comparisons'][1::2]):
        assert per['training_ids']==baseline['training_ids']
        assert per['held_policy_key'] not in per['training_policy_keys']
        assert per['runs'][0]['seed_manifest']==baseline['runs'][0]['seed_manifest']
    target=[x['prediction'] for x in a['comparisons'] if x['iteration']=='window0']
    rows[0].goodput_mbps=999;rows[0].p95_ms=999;rows[0].p99_ms=1000
    b=wave_g_heldout(rows,2,horizon=.05)
    assert target==[x['prediction'] for x in b['comparisons'] if x['iteration']=='window0']
    assert any(x['observed_packet_loss_pct']==5 for x in b['comparisons'])
    assert set(b['rmse_goodput_p95_p99'])=={'per_ac','pooled_uniform'} and not b['physical_accuracy_accepted']


def test_g_response_refuses_empty_training_and_unknown_variant():
    with pytest.raises(ValueError):multiflow_response([],regime_row(0),'per_ac')
    with pytest.raises(ValueError):multiflow_response([regime_row(1)],regime_row(0),'invented')


@native_simpy
def test_g_replication_stream_roles_do_not_reuse_any_seed():
    sets=[]
    for seed in (20261024,20261024+1009,20261024+2018):
        s=PerACScenario(vendors=('WA','XC'),horizon_s=.01,warmup_s=0,seed=seed)
        manifest=simulate_per_ac(s,scenario_flows(2),{'goodput_mbps':80,'p50_ms':10})['seed_manifest']
        values=set(manifest['arrivals'].values())|{manifest['collisions']}
        assert len(values)==len(manifest['arrivals'])+1
        sets.append(values)
    assert all(not a&b for i,a in enumerate(sets) for b in sets[i+1:])


@native_simpy
def test_g_seed_blocks_cover_maximum_total_flow_and_seed_domains():
    flows=[FlowSpec(str(i),i%16,'DL','TCP',1500,0) for i in range(256)]
    sets=[]
    for seed in (2**53-1,2**53):
        r=simulate_per_ac(PerACScenario(vendors=('WA',)*16,seed=seed),flows,{'goodput_mbps':80,'p50_ms':10})
        m=r['seed_manifest'];values=set(m['arrivals'].values())|{m['collisions']}
        assert len(values)==257 and all(type(v)is int and seed*10000<=v<(seed+1)*10000 for v in values)
        sets.append(values)
    assert not sets[0]&sets[1]
