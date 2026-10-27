import math
import pytest
from tools.sim import build_stage355a_airselect_hopping_evasion_pareto as m
from tools.re import ground_up_release_common as c


def test_seeded_conservation_and_determinism():
    args=(m.Policy(),'MIXED','rotating_interference',355)
    a=m.simulate(*args,horizon_ms=400);assert a==m.simulate(*args,horizon_ms=400)
    assert math.isclose(a['offered_bits'],a['delivered_expected_bits']+a['overflow_dropped_bits']+a['outstanding_bits'],rel_tol=1e-9)
    assert a['event_steps']<a['event_cap']


def test_quiet_control_avoids_gratuitous_hopping():
    a=m.simulate(m.Policy(),'WA','quiet',355,horizon_ms=400)
    b=m.simulate(m.Policy('static'),'WA','quiet',355,horizon_ms=400)
    assert a['hops']==b['hops']==0 and a['goodput_mbps']==b['goodput_mbps']


def test_missing_announcements_and_skew_have_explicit_costs():
    p=m.Policy('coordinated',100,2,20)
    a=m.simulate(p,'MIXED','rotating_interference',355,announcement_loss=1,horizon_ms=600)
    assert a['missed_announcements']==a['announcements'] and sum(a['blackout_link_ms'])>0
    b=m.simulate(m.Policy('static'),'WA','quiet',355,clock_skew_ms=3,horizon_ms=400)
    assert sum(b['tdd_mismatch_link_ms'])>0


def test_channel_eligibility_is_a_restriction_not_regulatory_override():
    a=m.simulate(m.Policy(),'XW','rotating_interference',355,horizon_ms=300,eligible_channels=('C0',))
    assert a['hops']==0


def test_handoff_exact_control_and_retune_boundaries():
    assert m.handoff_schedule('reactive',100,20,5,18)=={'ap_switch_at_ms':100,'peer_retune_start_ms':105,'peer_ready_ms':123}
    assert m.handoff_schedule('coordinated',100,20,5,18)=={'ap_switch_at_ms':120,'peer_retune_start_ms':120,'peer_ready_ms':138}
    assert m.handoff_schedule('coordinated',100,20,25,18)=={'ap_switch_at_ms':120,'peer_retune_start_ms':125,'peer_ready_ms':143}


def test_missed_hop_has_one_scan_wait_one_retune_and_no_service_overlap():
    r=m.simulate(m.Policy('reactive'),'XW','rotating_interference',355,announcement_loss=1,horizon_ms=400)
    rows=[e for e in r['coordination_events'] if e['kind']=='scan_retune']
    assert rows and r['service_hop_boundary_guard']
    for e in rows:
        assert e['retune_start_ms']-e['mismatch_start_ms']==60
        assert e['ready_ms']-e['retune_start_ms']==18


@pytest.mark.parametrize('kwargs',[{'announcement_loss':float('nan')},{'horizon_ms':True},{'horizon_ms':0},
                                  {'clock_skew_ms':4},{'eligible_channels':('C0','C0')},{'eligible_channels':('DFS_DISABLED',)}])
def test_invalid_simulation_inputs(kwargs):
    with pytest.raises(ValueError):m.simulate(m.Policy(),'WA','quiet',355,**kwargs)


@pytest.mark.parametrize('kwargs',[{'dwell_ms':20},{'lead_ms':40,'dwell_ms':40},{'kind':'native_airselect'},{'guard_ms':True}])
def test_invalid_policy(kwargs):
    with pytest.raises(ValueError):m.Policy(**kwargs)


def test_saved_finite_fronts_recomputed_independently():
    r=c.load(m.ROOT/m.OUT)
    assert r['summary']['replications']==240 and not r['boundary']['physical_acceptance']
    for group in r['groups']:
        rows=group['policies']
        for row in rows:
            f=row['objectives']
            dominated=any(all(x<=y for x,y in zip(other['objectives'],f)) and any(x<y for x,y in zip(other['objectives'],f)) for other in rows)
            assert (row['pareto_rank']==0)==(not dominated)


def test_doc_budget():
    text=(m.ROOT/m.DOC).read_text();assert len(text.splitlines())<220
    assert text.count('<!-- doc-head:')==text.count('<!-- /doc-head -->')==1
