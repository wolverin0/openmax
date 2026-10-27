"""Pure host numerical oracles and manifest-pinned R16-R21 snapshots only."""
from copy import deepcopy
from itertools import combinations, product
import math

import numpy as np
import pytest

from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import (
    analyze_identified_round, build_analysis, exact_walsh_confidence_set,
    frozen_receipts, multilevel_design_diagnostics, sequential_CPU_description,
)


def oracle_p(values):
    nonzero=[v for v in values if v!=0]
    ranks=[1+sum(abs(x)<abs(v) for x in nonzero)+(sum(abs(x)==abs(v) for x in nonzero)-1)/2 for v in nonzero]
    score=sum(r for r,v in zip(ranks,nonzero) if v>0)
    center=sum(ranks)/2
    scores=[sum(r for r,s in zip(ranks,signs) if s>0) for signs in product((-1,1),repeat=len(nonzero))]
    return sum(abs(s-center)>=abs(score-center) for s in scores)/len(scores)


def contains(result,point):
    return any((c['lower'] is None or point>c['lower'] or (point==c['lower'] and c['lower_closed'])) and
               (c['upper'] is None or point<c['upper'] or (point==c['upper'] and c['upper_closed']))
               for c in result['components'])


@pytest.mark.parametrize('values,alpha', [([0,0,1,1,2,3],.1), ([-3,-1,0,1,3,3],.2), ([1,2,3,4,5,6,7,8],.05), ([1,1,2,2],.25)])
def test_confidence_union_inverts_independent_sign_enumeration_at_every_cell(values,alpha):
    result=exact_walsh_confidence_set(values,alpha)
    points=sorted(set((a+b)/2 for i,a in enumerate(values) for b in values[i:]))
    probes=[points[0]-10,points[-1]+10]+points+[(a+b)/2 for a,b in zip(points,points[1:])]
    for value in probes:
        assert contains(result,value)==(oracle_p([v-value for v in values])>alpha)


def test_confidence_set_exact_conditional_sign_coverage_with_ties_zeros():
    # Independent exhaustive null sign distribution, not Walsh terms as units.
    magnitudes=[0,1,1,2,3,5]
    accepted=0
    for signs in product((-1,1),repeat=5):
        values=[0]+[m*s for m,s in zip(magnitudes[1:],signs)]
        accepted+=contains(exact_walsh_confidence_set(values,.1),0)
    assert accepted/32>=.9


def test_exact_small_n_and_multiplicity_are_not_finite_precision_claims():
    assert exact_walsh_confidence_set([1,2,3,4])['whole_real_line']
    assert not exact_walsh_confidence_set(range(1,9))['whole_real_line']
    assert exact_walsh_confidence_set(range(1,9),.05/81)['whole_real_line']


@pytest.mark.parametrize('alpha', [0,1,False,float('nan'),float('inf')])
def test_confidence_invalid_alpha_fails_closed(alpha):
    with pytest.raises(ValueError):exact_walsh_confidence_set([1,2],alpha)


def synthetic_rows():
    rows=[]
    for block,sequence in enumerate(('ABC','BCA','CAB')):
        for step,treatment in enumerate(sequence):
            value=block+ord(treatment)-64
            rows.append(dict(block_index=block,crossover_step=step,treatment_id=treatment,
                observation=dict(goodput_rx_mbps=value,p95_rtt_ms=value,p99_rtt_ms=value+1,
                                 packet_loss_pct=10 if (block,treatment)==(0,'A') else 0)))
    return rows


def test_three_arms_not_collapsed_and_pair_filter_does_not_exclude_third_arm_blocks():
    result=analyze_identified_round(synthetic_rows(),16)
    assert result['diagnostics']['treatment_ids']==['A','B','C']
    assert len(result['contrasts'])==9
    assert all(c['complete_blocks']==3 and not c['excluded_blocks'] for c in result['contrasts'])
    pair=next(c for c in result['contrasts'] if c['control']=='A' and c['treatment']=='B')
    assert pair['quality_observations']['lossful_rows']==1
    assert pair['quality_observations']['restoration_unknown_rows']==6
    assert pair['pairs'][0]['control_mean']==1  # Actual block, not sorted ping pairing.


def test_missing_arm_disclosed_not_imputed():
    rows=[r for r in synthetic_rows() if not (r['block_index']==0 and r['treatment_id']=='B')]
    result=analyze_identified_round(rows,16)
    pair=next(c for c in result['contrasts'] if c['control']=='A' and c['treatment']=='B')
    assert pair['complete_blocks']==2
    assert pair['excluded_blocks']==[dict(block_index=0,reason='MISSING_ARM',control_rows=1,treatment_rows=0)]


@pytest.mark.parametrize('change', ['missing_step','bool_id','duplicate','R17'])
def test_genuine_ids_required(change):
    rows=synthetic_rows()
    if change=='missing_step':rows[0].pop('crossover_step')
    if change=='bool_id':rows[0]['block_index']=False
    if change=='duplicate':rows.append(deepcopy(rows[0]))
    with pytest.raises(ValueError):analyze_identified_round(rows,17 if change=='R17' else 16)


def test_period_and_lag_diagnostics_retain_all_treatment_labels():
    result=multilevel_design_diagnostics(synthetic_rows())
    assert 'current:C' in result['design']['columns'] and 'lag:C' in result['design']['columns']
    assert len(result['period_counts'])==9
    assert sum(r['rows'] for r in result['period_counts'])==9
    assert result['randomization'].startswith('UNKNOWN')


def test_directed_previous_current_transitions_do_not_collapse_reference_arm():
    result=multilevel_design_diagnostics(synthetic_rows())
    transition={(r['previous'],r['current']):r['rows'] for r in result['directed_transition_counts']}
    assert sum(transition.values())==6
    assert transition[('A','B')]==transition[('B','C')]==transition[('C','A')]==2
    assert transition[('B','A')]==transition[('C','B')]==transition[('A','C')]==0
    assert result['period_balance']['equal_treatment_counts_within_every_period'] is True
    assert result['transition_balance']['all_distinct_ordered_pairs_equal'] is False


def test_schedule_agreement_uses_explicit_label_mapping_not_just_design_name():
    import analysis.statistics.fmx_r16_to_r21_real_crossover_audit as module
    rows=synthetic_rows();schedule=[list(s) for s in ('ABC','BCA','CAB')]
    assert module.schedule_agreement(rows,schedule,dict(A='A',B='B',C='C'))['matches']
    changed=deepcopy(rows);changed[0]['crossover_step'],changed[1]['crossover_step']=1,0
    result=module.schedule_agreement(changed,schedule,dict(A='A',B='B',C='C'))
    assert not result['matches'] and len(result['mismatches'])==2
    assert not module.schedule_agreement(rows[:-1],schedule,dict(A='A',B='B',C='C'))['matches']


@pytest.fixture(scope='module')
def actual():
    return build_analysis(resamples=99)


def test_actual_predeclared_complete_families_and_true_units(actual):
    assert (actual['treatment_by_block_rows'],actual['matched_round_block_units'],actual['R17_sequential_rows'])==(88,24,16)
    assert actual['window_count']==23 and len(actual['paired_contrasts'])==81 and len(actual['ping_contrasts'])==33
    assert {r['round_id'] for r in actual['paired_contrasts']}=={'R16','R18','R19','R20','R21'}
    assert all(r['complete_blocks']==(8 if r['round_id']=='R16' else 4) for r in actual['paired_contrasts'])
    assert all(r['Holm81_p_value']>=.05 for r in actual['paired_contrasts'])
    assert all(r['exact_Bonferroni81_confidence_set']['whole_real_line'] for r in actual['paired_contrasts'])


def test_actual_losses_summary_disagreement_and_received_tail_scope_preserved(actual):
    losses=[r for r in actual['descriptions'] if r['reported_loss_pct']>0]
    assert len(losses)==2 and all(r['raw_received_RTT']==39 for r in losses)
    assert any(c['quality_observations'].get('lossful_rows',0)>0 for c in actual['paired_contrasts'])
    stock=next(r for r in actual['descriptions'] if r['round_id']=='R16' and 'stock' in r['iteration'])
    assert stock['summary_consistency']['reported']['total_mbps']==105.85
    assert stock['summary_consistency']['block_means']['total_mbps']==pytest.approx(105.6875)
    assert not actual['automatic_execution_allowed'] and not actual['causal_or_physical_acceptance']
    assert all(r['interpretable_mac_retry_rate'] is None for r in actual['descriptions'] if r['mac_tx_packet_delta']==0)
    assert all(r['block_received_pings']==r['raw_received_RTT'] for r in actual['descriptions'])
    assert actual['exact_detectability']['smallest_n_for_first_Holm81_05']==12


def test_R18_comparison_changes_BE_not_threshold_and_distance_is_declared(actual):
    result=actual['R18_fixed_threshold_comparison']
    assert result['declared_distance_m']==[3000,3000]
    assert result['AP_threshold_us']==result['CPE_threshold_us']==[7200,7200]
    assert result['changed_endpoint_fields']['ap_state.be_low_us']==[1800,1900]
    assert not any(k.endswith('aql_threshold_us') for k in result['changed_endpoint_fields'])


def test_R17_CPU_is_raw_block_description_never_crossover(actual):
    result=actual['R17_CPU']
    assert result['status']=='SEQUENTIAL_DESCRIPTIVE_NOT_CROSSOVER'
    assert sum(r['sequential_rows'] for r in result['rows'])==16
    assert result['same_symmetric_package_secure_vs_open']['paired_p_value'] is None
    receipts,_=frozen_receipts()
    broken=deepcopy(receipts[17]);broken['iterations'][0]['repetition_blocks'][0]['crossover_step']=0
    with pytest.raises(ValueError):sequential_CPU_description(broken)
