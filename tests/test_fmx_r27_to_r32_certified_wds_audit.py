"""Host-only independent exact oracles; frozen snapshots, no live recipes."""
from copy import deepcopy
from decimal import Decimal
from itertools import product
from types import SimpleNamespace

import pytest

from analysis.statistics.fmx_r15_and_crossover_statistical_audit import exact_signed_rank, _rank_sum_counts
from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import exact_walsh_confidence_set
from analysis.statistics.fmx_r27_to_r32_certified_wds_audit import (
    audit_pair, build_analysis, exact_effect, frozen_inputs, literal_mean_audit,
    padded_family, pool_comparability,
)


def oracle(values):
    nz = [v for v in values if v!=0]
    ranks = [1+sum(abs(y)<abs(v) for y in nz)+(sum(abs(y)==abs(v) for y in nz)-1)/2 for v in nz]
    center = sum(ranks)/2
    actual = sum(r for r,v in zip(ranks,nz) if v>0)
    scores = [sum(r for r,s in zip(ranks,signs) if s>0) for signs in product((-1,1),repeat=len(nz))]
    return sum(abs(s-center)>=abs(actual-center) for s in scores)/len(scores)


@pytest.mark.parametrize('values', [[0],[0,1,-1,2,-2],[1,1,-1,2,3,-5],[1,2,3,4,5,6],[0,0,-1,-2,-3]])
def test_exact_tie_zero_DP_matches_independent_small_n_sign_exhaustion(values):
    assert exact_signed_rank(values)['p_value']==oracle(values)


def test_n46_known_positive_case_uses_polynomial_rank_sum_DP_not_2power46_enumeration():
    result = exact_signed_rank(list(range(1,47)))
    assert result['p_value']==2/2**46
    assert result['sign_assignments']==2**46
    counts = _rank_sum_counts(tuple(range(2,93,2)))
    assert len(counts)==2163 and sum(counts)==2**46
    assert counts[0]==counts[-1]==1


def contains(ci,x):
    return any((c['lower'] is None or x>c['lower'] or (x==c['lower'] and c['lower_closed']))
        and (c['upper'] is None or x<c['upper'] or (x==c['upper'] and c['upper_closed'])) for c in ci['components'])


def test_exact_coverage_levels_monotone_tied_zero_membership_and_n4_unbounded_truth():
    values = [0,1,1,2,3,5,8,13]
    a,b = exact_walsh_confidence_set(values,.05),exact_walsh_confidence_set(values,.001)
    for point in [-2,0,.5,1,1.5,2,4,8,20]:
        assert contains(a,point)==(oracle([v-point for v in values])>.05)
        assert contains(b,point)==(oracle([v-point for v in values])>.001)
        assert not contains(a,point) or contains(b,point)
    r=exact_effect([1,2,3,4])
    assert r['confidence_sets']['95']['whole_real_line']
    assert r['confidence_sets']['99.9']['whole_real_line']


def test_n46_confidence_sets_are_finite_and_higher_coverage_contains_lower():
    r=exact_effect(list(range(1,47)))
    assert r['HL_estimate']==23.5 and r['derived_Walsh_terms']==1081
    for ci in r['confidence_sets'].values():
        assert not ci['whole_real_line'] and ci['components']
        assert all(c['lower'] is not None and c['upper'] is not None for c in ci['components'])
    for x in range(0,48):
        assert not contains(r['confidence_sets']['95'],x) or contains(r['confidence_sets']['99.9'],x)


def member(name,p):
    return dict(source_hypothesis_id=name,exact_rank=dict(p_value=p))


def test_p1_holm_completion_exact_padding_and_Bonf_bound_without_fake_catalog():
    members=[member('a',.001),member('b',.004)]
    r=padded_family(members,10,'fixture')
    assert r['known_count']==2 and r['unknown_padding_count']==8
    assert r['adjusted_p']==pytest.approx({'a':.01,'b':.036})
    assert r['Bonferroni_upper_bound']=={'a':.01,'b':.04}
    assert r['known_hypotheses']=={'a':.001,'b':.004}
    assert len(r['known_hypotheses'])==2 # No eight invented measured hypotheses.
    with pytest.raises(ValueError):padded_family(members,1,'too_small')
    with pytest.raises(ValueError):padded_family(members+[members[0]],10,'duplicate')


@pytest.mark.parametrize('bad',[True,float('nan'),float('inf'),-.1,1.1])
def test_malformed_p_does_not_generate_acceptance(bad):
    with pytest.raises(ValueError):padded_family([member('x',bad)],324,'bad')


def rows(number=27):
    result=[]
    for block in range(4):
        for step,arm in enumerate(('A','B')):
            result.append(dict(round_id=f'R{number}',block_index=block,crossover_step=step,treatment_id=arm,
                ul_goodput_mbps=20+step,observation=dict(goodput_rx_mbps=100+step,p50_rtt_ms=10-step,
                    p95_rtt_ms=15-step,p99_rtt_ms=20-step,jain_fairness=.8+.01*step,
                    packet_loss_pct=10 if block==0 and step==0 else 0)))
    return result


def test_round_block_pairing_retains_loss_and_missing_arm_without_ping_position_pairs():
    data=rows();r=audit_pair(data,'A','B','p95_rtt_ms')
    assert len(r['pairs'])==4 and r['quality']['lossful_rows']==1
    assert r['paired_unit_ids'][0]=={'round_id':'R27','block_index':0}
    missing=[r for r in data if not(r['block_index']==0 and r['treatment_id']=='B')]
    result=audit_pair(missing,'A','B','p95_rtt_ms')
    assert len(result['pairs'])==3 and result['excluded_blocks'][0]['reason']=='MISSING_ARM'


def test_unlabelled_cross_round_mix_cannot_pretend_one_round():
    with pytest.raises(ValueError,match='scope'):audit_pair(rows()+rows(28),'A','B','p95_rtt_ms')


def literal_row(value_type):
    q=value_type
    return {'observation':{'goodput_rx_mbps':q('.15')},'dl_goodput_mbps':q('.10'),
        'ul_goodput_mbps':q('.05'),'bidir_jain_fairness':q('.8'),
        'repetition_blocks':[{'total_goodput_mbps':q(v),'dl_goodput_mbps':q('.10'),
            'ul_goodput_mbps':q('.05'),'bidir_jain_fairness':q('.8')} for v in ('.1','.2')]}


def test_exact_decimal_mean_does_not_invent_binary_roundoff_failure_or_widen_literal_difference():
    assert literal_mean_audit(literal_row(Decimal))['all_literal_equal']
    assert literal_mean_audit(literal_row(float))['all_literal_equal']
    changed=literal_row(Decimal);changed['observation']['goodput_rx_mbps']=Decimal('.1500000001')
    r=literal_mean_audit(changed)
    assert not r['all_literal_equal'] and r['fields']['goodput_mbps']['reported_minus_mean']!=0


def policy_row(policy='observed_package',regime='bidir_6flow'):
    return SimpleNamespace(policy_key=policy,workload_regime=regime,active_flow_count=6,bidirectional=True,
        encryption_mode='psk2',distance_meters=None,associated_cpes=('Loco195',))


def test_pool_checks_complete_policy_and_context_not_merely_alias_names():
    selected=[(27,policy_row('stock'),policy_row('target')),(28,policy_row('stock'),policy_row('target'))]
    r=pool_comparability(selected)
    assert r['recorded_packages_and_contexts_match'] and not r['homogeneous_causal_effect_accepted']
    selected[1]=(28,policy_row('stock'),policy_row('target_extra_retry_change'))
    assert pool_comparability(selected)['status'].startswith('MIXTURE_ONLY')
    selected[1]=(28,policy_row('stock'),policy_row('target','bidir_2flow'))
    assert not pool_comparability(selected)['recorded_packages_and_contexts_match']


@pytest.fixture(scope='module')
def actual():
    return build_analysis()


def test_actual_counts_full_scopes_and_padding_are_honest(actual):
    assert actual['counts']==dict(new_windows=19,records=150,new_rows=144,new_matched=54,crossed_rows=332,matched=106,sequential_R17=16,pooled=46)
    assert len(actual['within_round_contrasts'])==138 and len(actual['pooled_contrasts'])==5
    assert actual['families']['new_known143_bound324']['unknown_padding_count']==181
    assert actual['families']['new_known143_bound500']['unknown_padding_count']==357
    assert actual['families']['complete_known467_bound467']['unknown_padding_count']==0
    assert actual['families']['complete_known467_bound500']['unknown_padding_count']==33
    assert actual['catalog_scope']['Holm324_for_complete467'].startswith('INAPPLICABLE')


def test_actual_spec_literal_mean_refuted_without_dropping_block_statistics(actual):
    audits=actual['source_claim_audits']
    assert sum(a['literal_mean_audit']['all_literal_equal'] for a in audits)==4
    assert all(a['literal_mean_audit']['all_literal_equal']==a['Y_literal_consistency'] for a in audits)
    assert all(a['chronological_RTT_claim'] and a['mac_tx_packets_delta']>0 and a['mac_block_sums_match_window'] for a in audits)
    assert not actual['claim_status']['exact_mean_all19']
    assert not actual['automatic_execution_allowed'] and not actual['physical_or_causal_acceptance']


def test_actual_pool_keeps_round_ids_and_strata_policy_and_n46_DP(actual):
    assert len(actual['pool_comparability']['strata'])==4
    for r in actual['pooled_contrasts']:
        assert len(r['pairs'])==46 and len({(p['round_id'],p['block_index']) for p in r['pairs']})==46
        assert {p['round_id'] for p in r['pairs']}=={'R27','R28','R29','R32'}
        assert len(r['round_stratified_results'])==4
        assert r['exact_rank']['method'].endswith('DP_WILCOX_ZEROS')
        assert r['confidence_sets']['99.9']['components']


def test_actual_projection_is_recomputable_from_true_family_members_not_flags(actual):
    projection=actual['promotion_evidence']
    assert len(projection['contrasts'])==143
    by_id={r['source_hypothesis_id']:r for r in actual['within_round_contrasts']+actual['pooled_contrasts']}
    for r in projection['contrasts']:
        assert r['paired_unit_ids']==by_id[r['source_hypothesis_id']]['paired_unit_ids']
        for bound in (324,500):
            family=projection['families'][r[f'family{bound}_key']]
            assert r[f'holm{bound}_adjusted_p']==family['adjusted_p'][r['source_hypothesis_id']]
            assert r['p_exact_rank']==family['known_hypotheses'][r['source_hypothesis_id']]
