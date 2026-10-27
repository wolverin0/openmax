import copy
import math
import pytest
from tools.sim import run_stage790a_panel1_guarida_84_20h_zero_drop_reliability_model as m


def test_exact_zero_poisson_reference_identity():
    r=m.zero_event_bound(math.log(20),future_hours=1)
    assert r['outage_rate_upper_per_hour']==pytest.approx(1)
    assert r['mtbf_lower_hours']==pytest.approx(1)
    assert r['survival_lower']==pytest.approx(math.exp(-1))
    assert not r['empirical_eligibility']


def test_exposure_and_detection_sensitivity():
    a=m.zero_event_bound(20);b=m.zero_event_bound(40);q=m.zero_event_bound(20,detection_probability=.5)
    assert b['outage_rate_upper_per_hour']==a['outage_rate_upper_per_hour']/2
    assert q['outage_rate_upper_per_hour']==a['outage_rate_upper_per_hour']*2
    assert b['survival_lower']>a['survival_lower']>q['survival_lower']


def test_undetected_events_are_unidentifiable_not_zero_risk():
    r=m.zero_event_bound(20,detection_probability=0)
    assert r['outage_rate_upper_per_hour'] is None and r['mtbf_lower_hours'] is None
    assert not r['identifiable_under_assumptions'] and r['survival_lower']==0
    assert m.zero_event_bound(20,detection_probability=0,future_hours=0)['survival_lower']==1


@pytest.mark.parametrize('kwargs',[{'hours':0},{'hours':True},{'hours':math.inf},{'hours':20,'confidence':1},
                                    {'hours':20,'confidence':0},{'hours':20,'detection_probability':1.1},
                                    {'hours':20,'future_hours':-1}])
def test_invalid_probability_time_and_types(kwargs):
    with pytest.raises(ValueError):m.zero_event_bound(**kwargs)


def test_actual_dump_counters_and_distinct_tid_cohort():
    payloads,_=m.h.freeze(m.ROOT,790,m.SOURCES);s=m.h.json_source(payloads[m.SNAP]);t=m.h.json_source(payloads[m.COUNTERS])
    raw=m.station_dump(s['live_3cpe_20h_uptime_and_station_audit']['raw_3cpe_station_dump'])
    assert raw['totals']==dict(tx_packets=40482795,tx_retries=500366,tx_failed=2473,rx_drop_misc=32586)
    tid=m.tid_counts(t['stations_per_tid'])
    assert tid['tx_packets']==39405365 and tid['rows']==24 and tid['tid0_codel_drops']==1412
    assert tid['non_tid0_codel_drops']==0 and tid['marks']==30
    assert tid['packet_trial_denominator_for_WDS'] is None
    assert m.literal_stations(payloads[m.CP].decode('utf-8'))==t['stations_per_tid']


def test_missing_or_duplicate_counter_never_defaults_zero():
    block='Station 00:11:22:33:44:55 (on sta1)\n\ttx packets: 10\n'
    with pytest.raises(ValueError):m.station_dump(block)
    payloads,_=m.h.freeze(m.ROOT,790,m.SOURCES);r=m.h.json_source(payloads[m.COUNTERS])
    stations=copy.deepcopy(r['stations_per_tid']);first=next(iter(stations.values()));first['tids'][1]['tid']=0
    with pytest.raises(ValueError):m.tid_counts(stations)


def test_snapshot_membership_is_not_event_surveillance():
    payloads,_=m.h.freeze(m.ROOT,790,m.SOURCES);r=m.h.json_source(payloads[m.SNAP]);s=m.snapshot_membership(r)
    assert s['same_mac_set'] and s['station_count']==3
    assert sorted(x['delta_s']for x in s['rows'])==[2,3,3]
    assert s['saved_execution_elapsed_s']==3.869 and not s['continuous_zero_WDS_events_proven']


def test_saved_qualified_model_and_current_owned_bindings():
    r=m.h.json_source(m.h.snapshot(m.ROOT,m.OUT)[0])
    assert len(r['conditional_sensitivity'])==9 and r['actual_detection_probability'] is None
    assert r['empirical_outage_rate_bound'] is None and not r['cohorts_joined']
    assert r['raw678']['max_connected_hours']>20.07 and r['raw678']['min_connected_hours']<20.07
    assert not any(r['boundary'].values())
    for pin in [r['implementation'],*r['analysis_dependencies'],r['outputs'][m.DOC]]:assert m.h.snapshot(m.ROOT,pin['path'])[1]==pin
