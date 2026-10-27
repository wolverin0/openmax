"""Regime, leakage and native multi-objective proposal contracts for Waves E/F."""
from dataclasses import replace

import numpy as np
import pytest

from orchestration.autoresearch.fmx_offline_data import EndpointPolicy, REGIMES, load_all_measurements
from orchestration.autoresearch.fmx_doe_and_pymoo_optimizer import (
    RegimeSurrogate, _core_policy_key, _regime_candidate, endpoint_features,
    nondominated_indices, optimize_regime_pareto, regime_features,
    regime_search_space, regime_validation,
)


@pytest.fixture(scope='module')
def rows():return load_all_measurements()[0]


def test_unknown_controls_masks_and_endpoints_are_preserved(rows):
    assert endpoint_features(None).shape==(23,)
    assert regime_features(rows[0]).shape==(46,)
    assert np.isfinite(np.array([regime_features(r) for r in rows])).all()
    policy=rows[-1].ap_policy
    assert not np.array_equal(endpoint_features(policy),endpoint_features(replace(policy,ct_baseband_rifs=0)))
    assert not np.array_equal(endpoint_features(policy),endpoint_features(replace(policy,dscp_micro_vo_steering=False)))


def test_outcomes_are_never_surrogate_features(rows):
    row=rows[-1]
    changed=replace(row,mac_retry_rate=.8,goodput_mbps=1,dl_goodput_mbps=1,
                    ul_goodput_mbps=100,p95_ms=500,p99_ms=1000,jain_fairness=.1)
    np.testing.assert_array_equal(regime_features(row),regime_features(changed))


def test_unseen_cpe_dscp_treatment_is_reported_even_when_ap_is_observed(rows):
    row=next(r for r in rows if r.workload_regime==REGIMES[1])
    model=RegimeSurrogate(rows)
    query=replace(row.cpe_policy,dscp_micro_vo_steering=True)
    prediction=model.predict(row.ap_policy,query,row.workload_regime)
    assert prediction['unseen_DSCP_treatment'] is True
    assert prediction['unseen_DSCP_endpoints']==['CPE']


def test_unknown_baseline_fields_cannot_create_holdout_leakage(rows):
    row=rows[0]
    other=replace(row,ap_policy=replace(row.ap_policy,ct_pshack=3,htt_max_ampdu=None),round_id='R9')
    assert row.policy_key!=other.policy_key
    assert _core_policy_key(row)==_core_policy_key(other)


def test_regimes_never_pool_each_others_outcomes(rows):
    model=RegimeSurrogate(rows)
    changed=[replace(r,goodput_mbps=999,p95_ms=999,p99_ms=1000) if r.workload_regime==REGIMES[0] else r for r in rows]
    row=next(r for r in rows if r.workload_regime==REGIMES[2])
    assert model.predict(row.ap_policy,row.cpe_policy,row.workload_regime)==RegimeSurrogate(changed).predict(row.ap_policy,row.cpe_policy,row.workload_regime)
    with pytest.raises(ValueError):model.predict(row.ap_policy,None,row.workload_regime)
    with pytest.raises(ValueError):model.predict(row.ap_policy,row.cpe_policy,REGIMES[0])


@pytest.mark.parametrize('method',['leave_core_policy_out','leave_round_out'])
def test_holdouts_cover_all_windows_with_train_only_context(rows,method):
    audit=regime_validation(rows,method)
    assert len(audit['rows'])==58
    by_name={r.iteration:r for r in rows}
    for item in audit['rows']:
        row=by_name[item['iteration']]
        train=[by_name[name] for name in item['training_windows']]
        assert row.iteration not in item['training_windows']
        if method=='leave_core_policy_out':
            assert all(_core_policy_key(r)!=_core_policy_key(row) for r in train)
        else:
            assert all(r.round_id!=row.round_id for r in train)
            assert item['prediction']['round_context_seen'] is False
        # Independent train-only replay proves held-out target means do not leak.
        replay=RegimeSurrogate(train).predict(row.ap_policy,row.cpe_policy,row.workload_regime,row.round_id)
        assert replay==item['prediction']
    assert {k:v['windows'] for k,v in audit['per_regime'].items()}==dict(zip(REGIMES,[27,13,18]))


def test_search_packages_keep_per_ac_and_symmetric_or_asymmetric_choices(rows):
    for regime,n_var in [(REGIMES[0],4),(REGIMES[1],8),(REGIMES[2],8)]:
        space=regime_search_space(rows,regime)
        assert len(space)==n_var
        ap,cpe=_regime_candidate(space,[0]*n_var)
        assert isinstance(ap,EndpointPolicy)
        assert (cpe is None)==(regime==REGIMES[0])
        for policy in (ap,cpe):
            if policy:
                assert len(policy.aql_by_ac)==4
                assert all(low<=high for low,high in policy.aql_by_ac)
        with pytest.raises(ValueError):_regime_candidate(space,[-1]*n_var)


@pytest.mark.parametrize('regime',REGIMES)
@pytest.mark.parametrize('algorithm',['nsga2','nsga3'])
def test_native_regime_frontier_is_supported_nondominated_and_nonactuating(rows,regime,algorithm):
    result=optimize_regime_pareto(rows,regime,algorithm,population=32,generations=12)
    assert result['evaluations']>0 and result['pareto']
    objectives=[]
    bad={(r.ap_policy,r.cpe_policy) for r in rows if r.workload_regime==regime and
         (r.packet_loss_pct or r.station_drops or not r.restoration_verified)}
    for proposal in result['pareto']:
        ap=EndpointPolicy(**proposal['ap_policy'])
        cpe=EndpointPolicy(**proposal['cpe_policy']) if proposal['cpe_policy'] else None
        assert (ap,cpe) not in bad
        assert proposal['stable_reference_distance']<=result['model_support_radius']+1e-8
        assert proposal['automatic_execution_allowed'] is False
        assert proposal['physical_safety_qualified'] is False
        p=proposal['prediction'];assert 0<=p['p95_ms']<=p['p99_ms']
        objectives.append([-p['goodput_mbps'],p['p95_ms'],p['p99_ms']])
    assert nondominated_indices(objectives)==list(range(len(objectives)))


def test_native_seed_reproducibility(rows):
    kwargs=dict(regime=REGIMES[2],algorithm='nsga3',population=24,generations=10)
    assert optimize_regime_pareto(rows,**kwargs)==optimize_regime_pareto(rows,**kwargs)
