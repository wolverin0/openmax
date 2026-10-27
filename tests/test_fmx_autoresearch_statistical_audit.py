import math

import pytest

from analysis.statistics.fmx_autoresearch_statistical_audit import (
    build_audit, describe, holm_adjust, planning_power, required_sample_size,
    tail_sample_requirement, welch_contrast,
)


def test_receiver_descriptive_t_interval_known_example():
    result=describe([1,2,3])
    assert result['mean']==2 and result['sd']==1 and result['n']==3
    assert result['conditional_t_interval']==pytest.approx([-0.4841377117,4.4841377117])


def test_welch_direction_symmetry_and_degenerate_samples():
    a=welch_contrast([3,4],[1,2])
    b=welch_contrast([1,2],[3,4])
    assert a['delta_mbps']==-b['delta_mbps']==2
    assert a['t_stat']==-b['t_stat']
    assert a['p_value']==b['p_value']
    result=welch_contrast([2,2],[1,1])
    assert result['p_value'] is None and result['conditional_interval'] is None


@pytest.mark.parametrize('alpha',[-0.1,True,float('nan'),1])
def test_alpha_validation_precedes_adjustments_and_tails(alpha):
    with pytest.raises(ValueError):welch_contrast([1,2],[3,4],alpha=alpha)
    with pytest.raises(ValueError):required_sample_size(0.5,alpha=alpha,family_size=3)


def test_holm_known_values_missing_and_original_order():
    assert holm_adjust([0.04,0.01,0.03])==pytest.approx([0.06,0.03,0.06])
    assert holm_adjust([None,0.01])==[None,0.02]
    with pytest.raises(ValueError):holm_adjust([float('nan')])


def test_sparse_tail_resolution_analytic_coverage():
    assert tail_sample_requirement(0.99,0.95)==299
    assert tail_sample_requirement(0.95,0.95)==59
    assert tail_sample_requirement(0.5,0.75)==2
    assert 1-0.99**6<0.06


@pytest.mark.parametrize('design,n',[('paired',34),('independent',64)])
def test_noncentral_t_known_sample_sizes_and_integer_rounding(design,n):
    result=required_sample_size(0.5,design=design)
    assert result['analyzed_units']==n
    assert planning_power(n,0.5,design=design)>=0.8
    assert planning_power(n-1,0.5,design=design)<0.8


def test_power_sensitivity_monotonic_and_adjustments():
    assert planning_power(30,0.5)<planning_power(60,0.5)
    assert planning_power(30,0.2)<planning_power(30,0.8)
    simple=required_sample_size(0.5)
    adjusted=required_sample_size(0.5,family_size=3,dropout=0.2)
    assert adjusted['analyzed_units']>simple['analyzed_units']
    assert adjusted['enrolled_units']==math.ceil(adjusted['analyzed_units']/0.8)


@pytest.mark.parametrize('design',['paired','independent'])
def test_large_noncentral_t_tail_regression_is_finite(design):
    for n in [1000,5000,10000]:
        power=planning_power(n,0.5,design=design)
        assert math.isfinite(power) and 0.99<power<=1


@pytest.mark.parametrize('kwargs',[{'effect_d':0},{'effect_d':float('inf')},{'effect_d':True},
    {'effect_d':0.5,'family_size':0},{'effect_d':0.5,'dropout':1},{'effect_d':0.5,'design':'unregistered'}])
def test_invalid_power_plans_rejected(kwargs):
    with pytest.raises(ValueError):required_sample_size(**kwargs)


def test_causal_audit_retains_negative_and_missing_evidence():
    audit=build_audit()
    assert audit['treatment_windows']==13 and audit['independent_links']==1
    assert len(audit['contrasts'])==11
    assert not audit['observed_power_computed'] and not audit['causal_effects_identified']
    assert all(row['causal_conclusion']=='NOT_IDENTIFIED' for row in audit['contrasts'])
    assert audit['design_diagnostics']['rank']<audit['design_diagnostics']['columns']
    assert any(abs(row['difference_mbps'])>30 for row in audit['same_policy_cross_round_changes'])
    assert len(audit['prospective_power_sensitivity'])==12
    assert all(row['rtt_count']==6 for row in audit['descriptives'])
