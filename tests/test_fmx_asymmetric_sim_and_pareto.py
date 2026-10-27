"""Host-only model/optimizer tests. No device or acquisition recipe import."""
from dataclasses import replace
import math

import numpy as np
import pytest

from analysis.simulation.fmx_asymmetric_ap_cpe_sim import (
    Endpoint,Scenario,SimulationBudgetExceeded,seed_manifest,simulate,
)
from controller.optimizer.fmx_asymmetric_pareto_optimizer import (
    CaseBank,decode,model_assessment,nondominated,optimize,repaired,
)


SHORT=Scenario(horizon_s=.04,warmup_s=.01,drain_s=.01)


def test_native_simpy_deterministic_separate_endpoint_queues_and_conservation():
    first=simulate(scenario=SHORT,seed=5)
    assert first==simulate(scenario=SHORT,seed=5)
    assert first['status']=='MODEL_ONLY_SIMPY_EXECUTED'
    assert first['events_processed']>0
    for snap in (first['horizon'],first['after_drain']):
        assert snap['offered']==snap['backpressured']+snap['admitted']
        assert snap['admitted']==snap['states']['completed']+snap['states']['codel_drop']+snap['pending']
        assert snap['offered_bytes']==snap['backpressured_bytes']+snap['completed_bytes']+snap['codel_dropped_bytes']+snap['pending_bytes']
        assert snap['packet_and_byte_conservation'] is True
    assert first['horizon']['pending']>0
    assert first['after_drain']['pending']<=first['horizon']['pending']
    assert first['automatic_execution_allowed'] is False


def test_endpoint_swap_changes_actual_event_outcomes_not_just_labels():
    tight=Endpoint(500,1000,2000,240,1000,5000,24000,12000)
    wide=Endpoint(3000,6000,12000,300,15000,75000,300000,150000)
    a=simulate(tight,wide,SHORT,seed=19)
    b=simulate(wide,tight,SHORT,seed=19)
    assert a['endpoints']['AP']==b['endpoints']['CPE']
    assert a['DL']!=b['DL'] and a['UL']!=b['UL']
    assert a['peak_driver_airtime_us'][0]<b['peak_driver_airtime_us'][0]


def test_warmup_and_horizon_metrics_do_not_include_drain_completions():
    a=simulate(scenario=replace(SHORT,drain_s=0),seed=7)
    b=simulate(scenario=replace(SHORT,drain_s=.1),seed=7)
    assert a['DL']==b['DL'] and a['UL']==b['UL']
    assert a['horizon']==b['horizon']
    assert b['after_drain']['states']['completed']>a['after_drain']['states']['completed']
    assert a['horizon']['right_censored_measurement_cohort']>0


def test_tsq_notsent_backpressure_and_valid_stock_independent_limits():
    stock=Endpoint(5000,12000,24000,300,20000,100000,1048576,4294967295)
    stock.validate() # NOTSENT is independently valid above TSQ.
    tight=replace(Endpoint(),tcp_limit_output_bytes=1500,tcp_notsent_lowat=1500)
    a=simulate(tight,tight,SHORT,seed=5);b=simulate(stock,stock,SHORT,seed=5)
    assert a['horizon']['backpressured']>b['horizon']['backpressured']
    assert a['horizon']['pending_bytes']<=6*1500


def test_persistent_codel_state_drops_and_declared_crypto_cost_has_directional_role():
    p=replace(Endpoint(),fq_target_us=1,fq_interval_us=10)
    a=simulate(p,p,SHORT,seed=9)
    assert a['horizon']['states']['codel_drop']>0
    plain=simulate(scenario=replace(SHORT,ccmp_ul_preparation_us=2000,encryption_mode='none'),seed=9)
    crypto=simulate(scenario=replace(SHORT,ccmp_ul_preparation_us=2000),seed=9)
    assert crypto['UL']['goodput_mbps']<plain['UL']['goodput_mbps']
    assert crypto['status'].startswith('MODEL_ONLY')


@pytest.mark.parametrize('change',[
    {'horizon_s':True},{'warmup_s':.12},{'horizon_s':float('nan')},
    {'capacity_mbps':0},{'flows_per_endpoint':1.0},{'flows_per_endpoint':9},
    {'packet_bytes':True},{'ccmp_ul_preparation_us':float('inf')},
    {'encryption_mode':'WPA3'},{'max_events':0},
])
def test_invalid_scenarios_fail_without_unbounded_run(change):
    with pytest.raises(ValueError):simulate(scenario=replace(Scenario(),**change))


@pytest.mark.parametrize('change',[
    {'be_low_us':True},{'be_low_us':1000.0},{'be_high_us':1},
    {'fq_target_us':60000},{'tcp_notsent_lowat':-1},
])
def test_endpoint_domains_are_not_silently_coerced(change):
    with pytest.raises(ValueError):simulate(ap=replace(Endpoint(),**change),scenario=SHORT)


def test_event_and_entity_budget_exhaustion_not_reported_as_success():
    with pytest.raises(SimulationBudgetExceeded):simulate(scenario=replace(SHORT,max_events=2))
    with pytest.raises(SimulationBudgetExceeded):simulate(scenario=replace(SHORT,max_packets=2))


def test_rng_blocks_are_disjoint_within_bounded_domain_and_roles():
    for seed in (0,1,20261024,2**31-2):
        a=seed_manifest(seed,8);b=seed_manifest(seed+1,8)
        streams=a['arrivals']+a['backoff']+a['service']
        assert len(streams)==len(set(streams))==20
        assert not set(streams)&set(b['arrivals']+b['backoff']+b['service'])
    with pytest.raises(ValueError):seed_manifest(True,3)


def test_repair_and_original_integer_feasibility_recheck():
    x=repaired([1234.6,211.1,15000.4,50000.2,100.5,255.9]*2)
    assert all(type(i)is int for i in x)
    ap,cpe=decode(x)
    assert ap.be_low_us==1235 and ap.be_high_us==2470
    assert ap.tcp_notsent_lowat<=ap.tcp_limit_output_bytes
    assert ap==cpe
    with pytest.raises(ValueError):decode([1234.0]*12)
    with pytest.raises(ValueError):decode([1000,200,10000,50000,96,256]*2)
    with pytest.raises(ValueError):repaired([float('nan')]*12)


def test_native_both_algorithms_finite_nondominated_disabled_and_common_streams():
    bank=CaseBank(max_cases=30,seed=19,scenario=SHORT)
    runs=optimize(bank,120,population=10,generations=1)
    assert [r['algorithm'] for r in runs]==['NSGA-II','NSGA-III']
    assert len(bank.cache)<=20
    for run in runs:
        assert run['evaluations']==10 and run['candidates']
        f=[c['objectives'] for c in run['candidates']]
        assert nondominated(f)==list(range(len(f)))
        for c in run['candidates']:
            assert c['enabled'] is False and c['automatic_execution_allowed'] is False
            assert c['physical_safety_qualified'] is False
            assert all(math.isfinite(v) for v in c['objectives'])
            decode(c['vector'])
    manifests=[tuple(r['seeds']['arrivals']) for case in bank.cache.values() for r in case['runs']]
    assert len(set(manifests))==3
    assert runs==optimize(CaseBank(max_cases=30,seed=19,scenario=SHORT),120,population=10,generations=1)


def test_global_case_budget_and_nondominance_validation():
    bank=CaseBank(max_cases=1,scenario=SHORT)
    bank.evaluate(Endpoint(),Endpoint())
    with pytest.raises(RuntimeError,match='budget'):bank.evaluate(replace(Endpoint(),be_low_us=1700),Endpoint())
    assert nondominated([[1,2,3,4],[2,3,4,5],[0,3,3,4]])==[0,2]
    with pytest.raises(ValueError):nondominated([[float('nan')]*4])


def test_frozen_four_training_and_whole_policy_out_validation_no_r14_projection():
    bank=CaseBank()
    capacity,report,refs=model_assessment(bank)
    assert capacity in (90,120,150) and len(refs)==4
    assert report['training_windows']==4 and len(report['calibration_window_ids'])==4
    assert report['heldout_windows']>0
    assert all(not r['training_policy_overlap'] for r in report['heldout'])
    assert all(r['round_id']!='R14' for r in report['heldout'])
    assert sum(r['round_id']=='R14' and r['reason']=='OUTSIDE_DECLARED_WPA2_MODEL_DOMAIN'
               for r in report['excluded_prior'])==4
    assert report['physical_predictive_accuracy_accepted'] is False


def test_mixed_boolean_encoding_never_becomes_integer_coordinate():
    with pytest.raises(ValueError):repaired([True]+[1500]*11)


def test_absent_completed_latency_cohort_remains_unavailable_not_favorable():
    stock=Endpoint(5000,12000,24000,300,20000,100000,1048576,4294967295)
    with pytest.raises(ValueError,match='No completed delay cohort'):
        CaseBank(scenario=SHORT).evaluate(stock,stock,capacity=90)


def test_other_host_backlog_never_selects_local_low_aql_window():
    ap=Endpoint(1000,4000,4000,256,10000,50000,262144,131072)
    cpe=Endpoint(5000,12000,24000,300,20000,100000,1048576,4294967295)
    r=simulate(ap,cpe,SHORT,seed=5)
    assert all(a['low_below_local_threshold']==0 for a in r['aql_decision_audit'])
    assert r['aql_decision_audit'][0]['high_window']>0
