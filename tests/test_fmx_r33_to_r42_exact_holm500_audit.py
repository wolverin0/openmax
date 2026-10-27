"""Pure host numerical/schema fixtures; no live recipes or target imports."""
from itertools import product
import json
import math
import numpy as np
import pytest
from scipy import stats
from analysis.statistics.fmx_r33_to_r42_exact_holm500_audit import exact_rank,confidence_set,exact_effect,parse_source,audit_pair,frozen_inputs
from analysis.statistics.fmx_r15_and_crossover_statistical_audit import exact_signed_rank,_rank_sum_counts


def exhaustive(values):
    data=np.array(values,dtype=float);data=data[data!=0]
    if not len(data):return 1.
    weights=stats.rankdata(abs(data),method='average');obs=abs(sum(w*(1 if x>0 else -1) for w,x in zip(weights,data)))
    return sum(abs(sum(w*s for w,s in zip(weights,signs)))>=obs for signs in product((-1,1),repeat=len(data)))/2**len(data)


def member(result,x):
    return any((r['lower'] is None or x>r['lower'] or (x==r['lower'] and r['lower_closed'])) and (r['upper'] is None or x<r['upper'] or (x==r['upper'] and r['upper_closed'])) for r in result['components'])


@pytest.mark.parametrize('values',[[0,0,0],[1,-1,2,-2,0],[1,1,1,-1,4],[1,-3,2,2,-4,0],[.1,.2,-.3,.4,0],[-1,-2,-3,-4,-5]])
def test_ties_zeros_exact_probabilities_match_independent_enumeration_and_old(values):
    r=exact_rank(values)
    assert r['p_value']==exhaustive(values)==exact_signed_rank(values)['p_value']
    assert r['nonzero_blocks']+r['zero_blocks']==len(values)


def test_94_true_sign_space_is_counted_not_enumerated():
    r=exact_rank(list(range(1,95)))
    assert r['sign_assignments']==2**94 and r['p_value']==2**-93
    c=_rank_sum_counts(tuple(range(2,189,2)))
    assert len(c)==8931 and sum(c)==2**94
    assert exact_rank([-x for x in range(1,95)])['p_value']==r['p_value']


def test_n4_unbounded_95_and999_truth_and_94_tied_singleton():
    for alpha in (.05,.001):
        assert confidence_set([1,2,3,4],alpha)['whole_real_line']
        c=confidence_set([3]*94,alpha)
        assert c['components']==[dict(lower=3.,upper=3.,lower_closed=True,upper_closed=True)]


def test_94_finite_sets_and_monotonic_coverage_membership():
    d=np.arange(1.,95.)
    a,b=confidence_set(d,.05),confidence_set(d,.001)
    assert not a['whole_real_line'] and not b['whole_real_line']
    for theta in np.arange(0,95,.5):
        assert member(a,theta)==(exact_rank(d-theta)['p_value']>.05)
        assert member(b,theta)==(exact_rank(d-theta)['p_value']>.001)
        assert not member(a,theta) or member(b,theta)
    assert exact_effect(d)['HL_estimate']==47.5


def test_small_set_all_breakpoints_cells_against_exhaustive_oracle():
    d=np.array([1.,1.,2.,-3.,4.,5.,7.,8.])
    points=sorted(set((a+b)/2 for i,a in enumerate(d) for b in d[i:]));grid=points+[(a+b)/2 for a,b in zip(points,points[1:])]+[-100,100]
    for alpha in (.05,.001):
        c=confidence_set(d,alpha)
        for theta in grid:assert member(c,theta)==(exhaustive(d-theta)>alpha)


@pytest.mark.parametrize('values',[[True],[float('nan')],[float('inf')],[],list(range(129))])
def test_invalid_values_and_compute_bound_rejected(values):
    with pytest.raises(ValueError):exact_rank(values)


@pytest.mark.parametrize('payload',[{'observation':float('inf')},{'iterations':[{'evaluation':{'fmx_loss':float('inf'),'decision':'keep','disqualified':True}}]},{'iterations':[{'evaluation':{'fmx_loss':float('nan'),'decision':'crash','disqualified':True}}]}])
def test_nonfinite_only_explicit_crash_metadata(payload):
    with pytest.raises(ValueError):parse_source(json.dumps(payload))


def test_valid_disqualified_crash_sentinel_preserved_not_numeric():
    a=parse_source('{"iterations":[{"evaluation":{"fmx_loss":Infinity,"decision":"crash","disqualified":true}}]}')
    assert a['iterations'][0]['evaluation']['fmx_loss']=={'nonfinite':'Infinity'}


def test_all_frozen_30_verified_and_all4_crashes_retained():
    receipts,literals,refs=frozen_inputs()
    assert len(refs)==30 and sum(len(a['iterations']) for a in receipts.values())==34
    assert len(receipts[36]['iterations'])==4
    for r in receipts[36]['iterations']:
        assert r['evaluation']['fmx_loss']=={'nonfinite':'Infinity'} and r['evaluation']['disqualified'] is True
        assert r['observation']['station_drops']==1
        assert len(r['repetition_blocks'])==4
    assert all(len(a['iterations'])==2 for n,a in receipts.items() if n>=40)


from types import SimpleNamespace
from analysis.statistics.fmx_r33_to_r42_exact_holm500_audit import _comparability,build_analysis


def recorded(policy,coverage=None):
    return SimpleNamespace(policy_key=policy,workload_regime='bidir_6flow',active_flow_count=6,bidirectional=True,encryption_mode='psk2',distance_meters=100,associated_cpes=('Loco195',),coverage_class=coverage)


def test_full_package_retry_and_coverage_context_never_collapse_to_recipe_alias():
    same=[(40,recorded('stock'),recorded('retry74')),(42,recorded('stock'),recorded('retry74'))]
    assert _comparability(same)['recorded_packages_and_contexts_match']
    mix=same+[(41,recorded('stock'),recorded('retry53'))]
    assert _comparability(mix)['status']=='MIXTURE_ONLY_EXPLICIT_DECLARED_DIFFERENCES'
    same[1]=(42,recorded('stock',6),recorded('retry74',6))
    assert not _comparability(same)['recorded_packages_and_contexts_match']


@pytest.fixture(scope='module')
def actual():return build_analysis()


def test_actual_all34_arms_208_rows_and_all45pairs_retained(actual):
    assert actual['counts']==dict(records=184,new_windows=34,crossed_rows=540,new_rows=208,matched=182,new_matched=76,sequential_R17=16)
    assert len(actual['within_round_contrasts'])==270 and len(actual['pooled_contrasts'])==10
    crashes=[x for x in actual['source_claim_audits'] if x['round_id']=='R36']
    assert len(crashes)==4 and all(x['evaluation']['disqualified'] is True and x['window_station_drops']==1 for x in crashes)
    assert len([r for r in actual['within_round_contrasts'] if r['scope']=='R36'])==36
    assert all(len(r['pairs'])==4 for r in actual['within_round_contrasts'] if r['scope']=='R36')
    assert not actual['automatic_execution_allowed'] and not actual['physical_or_causal_acceptance']


def test_actual_pool94_mixture_and78_common_with_source_ids(actual):
    assert not actual['pool_comparability']['MIXTURE94']['recorded_packages_and_contexts_match']
    assert actual['pool_comparability']['COMMON_PACKAGE78']['recorded_packages_and_contexts_match']
    for r in actual['pooled_contrasts']:
        n=94 if r['scope']=='MIXTURE94' else 78
        assert len(r['pairs'])==n and len({(u['round_id'],u['block_index']) for u in r['paired_unit_ids']})==n
        assert ('R41' in {u['round_id'] for u in r['paired_unit_ids']})==(n==94)
        assert (r['target_policy_id'] is None)==(n==94)
        for c in r['confidence_sets'].values():
            assert c['components'] and not c['whole_real_line']


def test_actual_families_no_hidden_complete500_claim(actual):
    f=actual['families']
    assert f['new_known280_bound324']['unknown_padding_count']==44
    assert f['new_known280_bound500']['unknown_padding_count']==220
    assert f['complete_known747_bound747']['known_count']==747
    assert actual['catalog_scope']['Holm500_complete747'].startswith('INAPPLICABLE')
    assert len([x for x in f if x.startswith('local_')])==24
    assert all(x['known_count']==5 and x['unknown_padding_count']==5 for k,x in f.items() if k.startswith('local_'))
    assert all(x['literal_mean_audit']['all_literal_equal']==x['AC_literal_consistency'] for x in actual['source_claim_audits'])
    assert len(actual['requested_win_claims'])==15


def test_actual_projected_statistics_are_same_hypotheses_and_units(actual):
    allrows={r['source_hypothesis_id']:r for r in actual['within_round_contrasts']+actual['pooled_contrasts']}
    assert len(actual['promotion_evidence']['contrasts'])==280
    for p in actual['promotion_evidence']['contrasts']:
        r=allrows[p['source_hypothesis_id']]
        assert p['paired_unit_ids']==r['paired_unit_ids'] and p['effect_hl']==r['HL_estimate']
        for size in (324,500):
            family=actual['families'][p[f'family{size}_key']]
            assert family['known_hypotheses'][p['source_hypothesis_id']]==p['p_exact_rank']
            assert family['adjusted_p'][p['source_hypothesis_id']]==p[f'holm{size}_adjusted_p']


from analysis.statistics.fmx_r33_to_r42_exact_holm500_audit import rank_polynomial


@pytest.mark.parametrize('weights',[(2,4,6),(3,3,6),(4,4,4),(2,5,5,8),(5,5,5,5),tuple(range(2,189,2))])
def test_packed_all_coefficients_identical_to_independent_scalar_integer_DP(weights):
    packed,bits=rank_polynomial(weights);mask=(1<<bits)-1
    actual=tuple((packed>>(i*bits))&mask for i in range(sum(weights)+1))
    assert actual==_rank_sum_counts(weights)
    assert sum(actual)==2**len(weights) and max(actual)<2**bits
    for cutoff in (0,sum(weights)//4,sum(weights)//2,sum(weights)):
        low=packed&((1<<((cutoff+1)*bits))-1)
        assert low%mask==sum(actual[:cutoff+1])
