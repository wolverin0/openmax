import math
import pytest
from tools.sim import run_stage788a_guarida_backbone_5210_to_5220_shift_pareto as m


def test_no_reflection_matches_analytical_awgn_density():
    for delta in (0,10):
        r=m.channel(delta,0,25,math.pi,20)
        assert r['capacity_density_bps_hz']==pytest.approx(math.log2(101))
        assert r['numerical_mean_power']==r['analytical_mean_power']==1


@pytest.mark.parametrize('tau',[0,25,50,100])
@pytest.mark.parametrize('rho',[0,.5,.9])
def test_numerical_power_integration_matches_exact_identity(tau,rho):
    r=m.channel(10,rho,tau,.7,20)
    assert r['numerical_mean_power']==pytest.approx(r['analytical_mean_power'],abs=1e-7)


def test_shift_can_improve_worsen_or_be_neutral():
    better=m.compare(.9,25,math.pi,20,0)['rows']
    worse=m.compare(.9,25,0,20,0)['rows']
    same=m.compare(.9,0,0,20,0)['rows']
    assert better[1]['effective_density_bps_hz']>better[0]['effective_density_bps_hz']
    assert worse[1]['effective_density_bps_hz']<worse[0]['effective_density_bps_hz']
    assert same[1]['effective_density_bps_hz']==same[0]['effective_density_bps_hz']


def test_pause_cost_reduces_effective_density_and_stay_dominates_neutral_shift():
    a=m.compare(.5,0,.5,20,0);b=m.compare(.5,0,.5,20,5)
    assert b['rows'][1]['effective_density_bps_hz']==pytest.approx(a['rows'][1]['effective_density_bps_hz']*595/600)
    assert b['frontier_indices']==[0]
    assert b['rows'][0]['pause_s']==0


@pytest.mark.parametrize('args',[(11,.5,25,0,20),(0,1,25,0,20),(0,.5,-1,0,20),
                                  (0,.5,25,-1,20),(0,.5,25,0,math.nan),(True,.5,25,0,20)])
def test_invalid_channel_inputs(args):
    with pytest.raises(ValueError):m.channel(*args)


def test_quadrature_and_horizon_caps():
    with pytest.raises(ValueError):m.channel(0,.5,25,0,20,points=200)
    with pytest.raises(ValueError):m.channel(0,.5,25,0,20,points=2003)
    with pytest.raises(ValueError):m.compare(.5,25,0,20,601)
    assert m.compare(.5,25,0,20,600)['rows'][1]['effective_density_bps_hz']==0


def test_saved_missing_counter_and_physical_qualifications_are_preserved():
    r=m.h.json_source(m.h.snapshot(m.ROOT,m.OUT)[0])
    assert len(r['cells'])==216 and r['model']['modelled_shift_can_improve'] and r['model']['modelled_shift_can_worsen']
    assert r['evidence']['native_subframe_pointer'] is None
    assert r['evidence']['subframe_provenance']=='UNLINKED_OPERATOR_PREMISE'
    assert r['evidence']['held457_documented_baseline_mhz']==5705
    assert not any(r['boundary'].values()) and r['new_hardware_results']==0
    for source in r['static_sources']:assert m.h.snapshot(m.ROOT,source['frozen']['path'])[1]==source['frozen']
    for p in [r['implementation'],*r['analysis_dependencies'],r['outputs'][m.DOC]]:assert m.h.snapshot(m.ROOT,p['path'])[1]==p
