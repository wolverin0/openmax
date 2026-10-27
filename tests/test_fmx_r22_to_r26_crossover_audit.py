"""Host-only synthetic numerical oracles and manifest-frozen evidence."""
from copy import deepcopy
from itertools import product

import numpy as np
import pytest

from analysis.statistics.fmx_r15_and_crossover_statistical_audit import exact_signed_rank
from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import exact_walsh_confidence_set
from analysis.statistics.fmx_r22_to_r26_crossover_audit import (
    CROSSED_ROUNDS, METRICS, _window_description, assign_families, build_analysis,
    factorial_boundaries, frozen_new_receipts, package_changes, paired_contrast,
    unanimity_checks, validate_crossed_rows,
)


def brute_force_p(values):
    nz = [v for v in values if v != 0]
    ranks = [1 + sum(abs(y) < abs(x) for y in nz) + (sum(abs(y) == abs(x) for y in nz) - 1) / 2 for x in nz]
    center = sum(ranks) / 2
    observed = sum(r for r,v in zip(ranks,nz) if v > 0)
    scores = [sum(r for r,s in zip(ranks,signs) if s > 0) for signs in product((-1,1),repeat=len(nz))]
    return sum(abs(v-center) >= abs(observed-center) for v in scores) / len(scores)


def contains(result, point):
    return any((c['lower'] is None or point > c['lower'] or (point == c['lower'] and c['lower_closed']))
               and (c['upper'] is None or point < c['upper'] or (point == c['upper'] and c['upper_closed']))
               for c in result['components'])


@pytest.mark.parametrize('values', [list(range(1,13)), [1,1,2,2,3,3,4,5,6,8,9,10], [0,-1,1,-2,2,-3,3,-4,4,-5,5,6]])
def test_n12_exact_distribution_against_independent4096_or_fewer_sign_enumeration(values):
    result = exact_signed_rank(values)
    assert result['p_value'] == brute_force_p(values)
    assert result['sign_assignments'] == 2 ** sum(v != 0 for v in values)
    if all(v > 0 for v in values):
        assert result['p_value'] == 2 / 4096


@pytest.mark.parametrize('alpha', [.05, .005, .05/162, .05/324])
def test_n12_exact_confidence_membership_with_ties_not_independent_Walsh_units(alpha):
    values = np.array([1,1,2,2,3,3,4,5,6,8,9,10],dtype=float)
    result = exact_walsh_confidence_set(values,alpha)
    for point in [0,1,1.25,2,4,4.5,5,6,8,10,11]:
        assert contains(result,point) == (brute_force_p(values-point) > alpha)
    if alpha in (.05,.005):
        assert not result['whole_real_line']
        assert all(c['lower'] is not None and c['upper'] is not None for c in result['components'])
    else:
        assert result['whole_real_line']


def rows(number=25, arms=3, blocks=12):
    result = []
    for block in range(blocks):
        for step in range(arms):
            arm = (step + block) % arms
            result.append(dict(round_id=f'R{number}',block_index=block,crossover_step=step,
                treatment_id=f'arm{arm}',ul_goodput_mbps=40 + arm + block/100,
                observation=dict(goodput_rx_mbps=100 + arm,p50_rtt_ms=20-arm,
                    p95_rtt_ms=30-arm,p99_rtt_ms=40-arm,jain_fairness=.8+arm/100,
                    packet_loss_pct=10 if (block,arm)==(0,0) else 0)))
    return result


def test_six_metrics_are_actual_block_values_and_loss_is_not_silently_dropped():
    data = rows()
    for metric in METRICS:
        r = paired_contrast(data,'arm0','arm1',metric)
        assert r['complete_blocks'] == 12 and not r['excluded_blocks']
        assert r['quality_observations']['lossful_rows'] == 1
        assert r['quality_observations']['restoration_verified_unknown_rows'] == 24
        assert r['wilcoxon']['sign_assignments'] == 4096
    assert paired_contrast(data,'arm0','arm1','ul_goodput_mbps')['pairs'][0]['difference'] == 1
    assert paired_contrast(data,'arm0','arm1','jain_fairness')['pairs'][0]['difference'] == pytest.approx(.01)


@pytest.mark.parametrize('problem', ['absent_arm','missing_metric','unequal_repeats'])
def test_incomplete_block_is_disclosed_without_imputation_or_ping_pairing(problem):
    data = rows()
    if problem == 'absent_arm':
        data = [r for r in data if not (r['block_index']==0 and r['treatment_id']=='arm1')]
    elif problem == 'missing_metric':
        next(r for r in data if r['block_index']==0 and r['treatment_id']=='arm1')['ul_goodput_mbps'] = None
    else:
        extra = deepcopy(next(r for r in data if r['block_index']==0 and r['treatment_id']=='arm1'))
        extra['crossover_step'] = 7;data.append(extra)
    r = paired_contrast(data,'arm0','arm1','ul_goodput_mbps')
    assert r['complete_blocks']==11 and r['excluded_blocks'][0]['block_index']==0


@pytest.mark.parametrize('problem', ['R17','bool','duplicate','missing_step'])
def test_only_genuine_crossed_ids_accepted(problem):
    data = rows()
    if problem == 'R17':data[0]['round_id']='R17'
    elif problem == 'bool':data[0]['block_index']=False
    elif problem == 'duplicate':data.append(deepcopy(data[0]))
    else:data[0].pop('crossover_step')
    with pytest.raises(ValueError):validate_crossed_rows(data)


def test_round_scope_separates_equal_numeric_block_ids():
    assert len(validate_crossed_rows(rows(24,4,4)+rows())) == 52


def test_complete_families_can_disagree_without_selection_or_significance_shopping():
    all_contrasts = []
    for number in CROSSED_ROUNDS:
        arms = 3 if number in (16,25) else 4
        count = 8 if number==16 else 12 if number==25 else 4
        data = rows(number,arms,count)
        for a in range(arms):
            for b in range(a+1,arms):
                all_contrasts.extend(paired_contrast(data,f'arm{a}',f'arm{b}',m) for m in METRICS)
    families, focused = assign_families(all_contrasts,['arm0','arm1','arm2'])
    assert {k:v['tests'] for k,v in families.items()} == {'Holm324':324,'Holm162':162,'Holm10':10}
    assert families['Holm10']['rejected_05']==10
    assert families['Holm162']['rejected_05']==families['Holm324']['rejected_05']==0
    assert all(r['Bonferroni162_confidence_set']['whole_real_line'] and r['Bonferroni324_confidence_set']['whole_real_line'] for r in focused)
    assert all(not r['Bonferroni10_confidence_set']['whole_real_line'] for r in focused)
    assert all(r['claim_matches'] for r in unanimity_checks(focused))
    with pytest.raises(ValueError):assign_families(all_contrasts[:-1],['arm0','arm1','arm2'])


def test_factorial_nominal_rank_does_not_resolve_queue_and_retry_aliasing():
    receipts,_=frozen_new_receipts()
    result=factorial_boundaries(receipts[24],receipts[26])
    r24=result['R24']
    assert r24['nominal']['rank']==4 and r24['nominal']['full_column_rank']
    assert r24['nuisance_adjusted']['rank']==4 and len(r24['nuisance_adjusted']['columns'])==6
    for name in ('AF1','FQ2048','AF1xFQ2048'):
        assert not r24['nuisance_adjusted']['conditional_column_estimability'][name]
    assert r24['nuisance_aliases']['nonstock_queue_package']['nominal_basis_coefficients']==pytest.approx([0,1,1,-1])
    assert r24['nuisance_aliases']['retry_changed']['nominal_basis_coefficients']==pytest.approx([0,0,0,1])
    assert not r24['isolated_factor_effects_identified']
    r26=result['R26']
    assert r26['hybrid_factor_matrix']['rank']==3 and len(r26['hybrid_factor_matrix']['columns'])==4
    assert r26['missing_FTX0_retry_changed']==[0,1] and not r26['interaction_identified']
    assert r26['C_vs_B']['declared_single_FTX_change']
    assert r26['D_vs_C']['declared_only_retry_pair_change']


def test_declared_clean_package_check_rejects_extra_endpoint_change():
    receipts,_=frozen_new_receipts();changed=deepcopy(receipts[26])
    changed['iterations'][2]['candidate_knobs']['ap_state']['fq_quantum_bytes'] += 1
    assert not factorial_boundaries(receipts[24],changed)['R26']['C_vs_B']['declared_single_FTX_change']
    a,b=deepcopy(receipts[26]['iterations'][:2])
    a['candidate_knobs']['new_unknown']=None
    assert package_changes(a,b)['new_unknown']==[None,{'state':'ABSENT'}]


def test_hook_boolean_candidate_does_not_satisfy_exact_integer_declaration():
    receipts,_=frozen_new_receipts();row=deepcopy(receipts[22]['iterations'][0])
    row['candidate_knobs']['force_tx_status']=False
    with pytest.raises(ValueError,match='hook'):_window_description('R22',row)


@pytest.fixture(scope='module')
def actual():
    from orchestration.autoresearch import fmx_offline_data
    if not hasattr(fmx_offline_data,'load_all26_block_observations'):
        pytest.skip('U API not yet frozen; final review must execute this fixture')
    return build_analysis()


def test_actual_complete_units_families_and_preexisting_rows_preserved(actual):
    assert (actual['crossed_rows'],actual['matched_round_block_units'],actual['new_crossed_rows'],actual['new_matched_units'])==(188,52,100,28)
    assert actual['R17_sequential_rows']==16 and len(actual['new_window_descriptions'])==19
    assert len(actual['contrasts'])==324
    assert {k:v['tests'] for k,v in actual['families'].items()}=={'Holm324':324,'Holm162':162,'Holm10':10}
    assert not actual['automatic_execution_allowed'] and not actual['causal_or_physical_acceptance']


def test_actual_R25_claims_checked_against_raw_identified_blocks_not_sorted_pings(actual):
    receipts,_=frozen_new_receipts();a,b,c=receipts[25]['iterations']
    for claim in actual['R25_unanimity_checks']:
        treatment=b if claim['treatment']==b['commit'] else c
        control={r['block_index']:r for r in a['repetition_blocks']}
        key={'ul_goodput_mbps':'ul_goodput_mbps','jain_fairness':'bidir_jain_fairness'}.get(claim['metric'],claim['metric'])
        lower=claim['metric'].startswith('p')
        improved=sum((r[key]<control[r['block_index']][key]) if lower else (r[key]>control[r['block_index']][key]) for r in treatment['repetition_blocks'])
        assert claim['observed_improved_blocks']==improved
        assert claim['claim_matches']==(improved==12)
    diag=next(r for r in actual['full_design_diagnostics'] if r['round_id']=='R25')
    assert all(r['rows']==4 for r in diag['period_counts'])
    assert len(diag['sequence_counts'])==6 and all(r['blocks']==2 for r in diag['sequence_counts'])
    assert diag['saved_schedule_agreement']['matches']
    assert diag['design']['rank']==18 and diag['transition_balance']['all_distinct_ordered_pairs_equal']


def test_actual_attempted_vs_received_sorted_multisets_and_summary_drift(actual):
    losses=[r for r in actual['new_window_descriptions'] if r['reported_window_loss_pct']>0]
    assert {r['round_id']:r['received_pings'] for r in losses}=={'R22':37,'R23':39,'R25':117,'R26':38}
    assert all(r['interpretable_mac_retry_fraction'] is None for r in actual['new_window_descriptions'])
    assert all(max([abs(v) for v in r['reported_minus_block_means'].values()]+[abs(r['reported_total_minus_directional_sum'])])>.021 for r in actual['new_window_descriptions'])
    sorted_rows=[r for r in actual['new_window_descriptions'] if r['round_id'] in ('R24','R25','R26')]
    assert all(r['pooled_RTT_is_sorted'] and r['pooled_RTT_multiset_matches_blocks'] for r in sorted_rows)
    assert all(not r['pooled_order_matches_block_concatenation'] for r in sorted_rows)


def test_actual_user_unanimity_claim_has_one_counterexample_without_changing_family(actual):
    claims=actual['R25_unanimity_checks']
    failed=[c for c in claims if not c['claim_matches']]
    assert len(failed)==1
    claim=failed[0]
    assert claim['treatment'].startswith('r25_iter1_') and claim['metric']=='p99_rtt_ms'
    assert (claim['observed_improved_blocks'],claim['observed_worse_blocks'],claim['observed_equal_blocks'])==(11,1,0)
    assert claim['sign_assignments']==4096 and claim['raw_exact_signed_rank_p']==.0009765625
    assert claim['raw_exact_sign_p']==26/4096
    assert actual['families']['Holm10']['rejected_05']==10
    assert actual['families']['Holm162']['rejected_05']==actual['families']['Holm324']['rejected_05']==0
    assert all(c['sign_assignments']==4096 for c in claims)
