"""Synthetic exhaustive statistical oracles and frozen R15 data; host-only."""
from collections import Counter
from itertools import product
import math

import numpy as np
import pytest
from scipy import stats

from analysis.statistics.fmx_r15_and_crossover_statistical_audit import (
    audit_blocked_crossover, build_audit, exact_sign_test, exact_signed_rank,
    paired_hl_interval,
)


def oracle_p_value(values):
    """Brute force signed-rank oracle, deriving ranks without scipy/DP."""
    nz = [x for x in values if x != 0]
    if not nz:return 1.0
    ranks = [1+sum(abs(y)<abs(x) for y in nz)+(sum(abs(y)==abs(x) for y in nz)-1)/2 for x in nz]
    observed = sum(rank for rank,value in zip(ranks,nz) if value > 0)
    total = sum(ranks)
    all_scores = [sum(rank for rank,sign in zip(ranks,signs) if sign > 0) for signs in product((-1,1),repeat=len(nz))]
    return sum(abs(score-total/2)>=abs(observed-total/2) for score in all_scores)/len(all_scores)


@pytest.mark.parametrize('values', [[0], [0,0,0], [0,1,-1,2,-2], [1,2,3,4,5,6], [1,1,-1,2,2,-3], [3,-1,1,-3,0,4]])
def test_exact_signrank_DP_against_all_sign_assignments_with_ties_and_zeros(values):
    r = exact_signed_rank(values)
    assert r['p_value'] == oracle_p_value(values)
    assert exact_signed_rank([-x for x in values])['p_value']==r['p_value']
    assert r['nonzero_blocks']+r['zero_blocks']==len(values)
    assert r['sign_assignments']==2**r['nonzero_blocks']


def test_signrank_all_sign_patterns_not_just_one_statistic():
    for signs in product((-1,1),repeat=5):
        values = [a*s for a,s in zip([1,1,2,3,5],signs)]+[0]
        assert exact_signed_rank(values)['p_value']==oracle_p_value(values)


def test_exact_binomial_sign_test_zeros_and_detectability():
    r = exact_sign_test([0,0,1,2,3,4])
    assert r['p_value']==.125 and r['zeros']==2 and r['positive']==4
    assert exact_sign_test([0,0])['p_value']==1
    assert exact_sign_test([1,-1,2,-2])['p_value']==1
    assert exact_signed_rank([1,2,3,4])['minimum_possible_two_sided_p']==.125


def test_small_n_tie_counterexample_normal_approximation_would_falsely_cross_threshold():
    # Four tied positive differences: uncorrected normal z=2 gives p<.05,
    # while the exact attainable two-sided significance is only2/16=.125.
    assert 2*stats.norm.sf(2)<.05
    assert exact_signed_rank([1,1,1,1])['p_value']==.125


def test_Walsh_not_sample_median_or_independent_pair_count_and_small_n_unbounded():
    r = paired_hl_interval([0,1,10],alpha=.05)
    assert r['estimate']==3  # Walsh0,.5,1,5,5.5,10; samplemedian1
    assert r['independent_blocks']==3 and r['derived_Walsh_count']==6
    assert r['interval']==[None,None]
    a = paired_hl_interval([1,2,3,4,5,6])
    assert a['estimate']==3.5 and a['interval']==[1,6]
    b = paired_hl_interval([-1,-2,-3,-4,-5,-6])
    assert b['estimate']==-3.5 and b['interval']==[-6,-1]


def test_exact_HL_inversion_coverage_all_sign_allocations_ties_zeros():
    covered = 0; trials = 0
    for signs in product((-1,1),repeat=6):
        differences = [a*s for a,s in zip([1,1,2,3,5,8],signs)]+[0]
        ci = paired_hl_interval(differences,alpha=.1)['interval']
        includes_zero = ci is not None and (ci[0] is None or ci[0]<=0) and (ci[1] is None or ci[1]>=0)
        # A hull may be conservative, but it must contain every non-rejected0.
        if oracle_p_value(differences)>.1:assert includes_zero
        covered += includes_zero; trials += 1
    assert covered/trials >= .9


def make_rows(sequences=('AB','BA'),values=None):
    rows=[]
    for block,sequence in enumerate(sequences):
        for step,treatment in enumerate(sequence):
            value=values[block][step] if values else 10+step+(treatment=='B')
            rows.append(dict(block_index=block,crossover_step=step,treatment_id=treatment,
                             observation=dict(p95_rtt_ms=value,packet_loss_pct=0),rtts_ms=[]))
    return rows


def test_ABBA_mean_aggregation_true_blocks_not_four_pseudo_pairs():
    rows=make_rows(('ABBA','BAAB'),((1,5,7,3),(8,2,4,10)))
    result=audit_blocked_crossover(rows,'A','B',evidence_kind='SYNTHETIC_FIXTURE_ONLY')
    assert result['complete_blocks']==2
    assert [p['difference'] for p in result['pairs']]==[4,6]
    assert result['paired_results']['wilcoxon']['nonzero_blocks']==2
    assert result['paired_results']['hl']['independent_blocks']==2
    assert result['physical_or_causal_acceptance'] is False


def test_missing_unbalanced_other_arm_outcome_and_quality_disclosed_without_imputation():
    rows=make_rows(('AB','A','ABB','AB','AC'))
    rows[6]['observation'].pop('p95_rtt_ms')  # block3A has missing metric
    rows[0]['observation']['packet_loss_pct']=5 # retain lossful metric, no selectionbias
    r=audit_blocked_crossover(rows,'A','B')
    assert r['complete_blocks']==1 and r['pairs'][0]['block_index']==0
    assert Counter(x['reason'] for x in r['excluded_blocks'])==Counter({'MISSING_ARM':1,'UNBALANCED_WITHIN_BLOCK_COUNTS':1,'MISSING_OUTCOME':1,'OTHER_TREATMENT_IN_BLOCK':1})
    assert len(r['excluded_blocks'])==4
    assert r['quality_observations']['lossful_rows']==1
    assert r['quality_observations']['restoration_unknown_rows']==len(rows)


def test_period_sequence_drift_is_observable_but_not_causal_carryover_proof():
    rows=make_rows(('AB','BA'),((10,30),(10,30))) # period+20, no treatment effect
    r=audit_blocked_crossover(rows,'A','B')
    assert [p['difference'] for p in r['pairs']]==[20,-20]
    assert {p['sequence']:p['mean_difference'] for p in r['sequence_differences']}=={'AB':20,'BA':-20}
    assert [p['mean'] for p in r['design_diagnostics']['period_metric_means']]==[10,30]
    assert r['design_diagnostics']['design']['full_column_rank'] is False
    all_AB=audit_blocked_crossover(make_rows(('AB','AB')),'A','B')
    assert all_AB['design_diagnostics']['design']['conditional_column_estimability']['current_treatment'] is False


def test_explicit_period_and_step_gap_retained_not_reenumerated():
    rows=make_rows(('AB',));rows[0]['crossover_step']=7;rows[1]['crossover_step']=10
    rows[0]['period_index']=20;rows[1]['period_index']=21
    r=audit_blocked_crossover(rows,'A','B')
    assert r['pairs'][0]['control_steps']==[7] and r['pairs'][0]['treatment_steps']==[10]
    assert r['design_diagnostics']['step_gaps']==[dict(block_index=0,before=7,after=10)]
    assert [x['period_index'] for x in r['design_diagnostics']['period_metric_means']]==[20,21]


@pytest.mark.parametrize('mutation',['missing_block','missing_step','bool_block','string_step','duplicate','missing_treatment','bad_observation','bad_period'])
def test_genuine_pair_IDs_and_schema_required_not_ping_position(mutation):
    rows=make_rows(('AB',))
    if mutation=='missing_block':rows[0].pop('block_index')
    if mutation=='missing_step':rows[0].pop('crossover_step')
    if mutation=='bool_block':rows[0]['block_index']=True
    if mutation=='string_step':rows[0]['crossover_step']='0'
    if mutation=='duplicate':rows.append(dict(rows[0]))
    if mutation=='missing_treatment':rows[0].pop('treatment_id')
    if mutation=='bad_observation':rows[0]['observation']=[]
    if mutation=='bad_period':rows[0]['period_index']=False
    with pytest.raises(ValueError):audit_blocked_crossover(rows,'A','B')


@pytest.mark.parametrize('bad', [True,float('nan'),float('inf'),0,1,-.1])
def test_alpha_rejects_nonprobabilities(bad):
    with pytest.raises(ValueError):paired_hl_interval([1,2],bad)
    with pytest.raises(ValueError):audit_blocked_crossover([], 'A','B',alpha=bad)


def test_nonfinite_bad_samples_and_invalid_treatment_ids_rejected():
    for values in ([],[True],[1,float('nan')],[float('inf')]):
        with pytest.raises(ValueError):exact_signed_rank(values)
        with pytest.raises(ValueError):paired_hl_interval(values)
    for a,b in [('A','A'),('A',''),(' ','B')]:
        with pytest.raises(ValueError):audit_blocked_crossover([],a,b)
    assert audit_blocked_crossover([],'A','B')['paired_results'] is None


def test_root_loader_normalized_synthetic_IDs_integrate_without_guessing():
    from orchestration.autoresearch.fmx_offline_data import load_blocked_crossover_blocks
    rows=load_blocked_crossover_blocks(dict(repetition_blocks=make_rows(('ABBA','BAAB'))))
    r=audit_blocked_crossover(rows,'A','B',evidence_kind='SYNTHETIC_FIXTURE_ONLY')
    assert r['complete_blocks']==2
    assert r['evidence_kind']=='SYNTHETIC_FIXTURE_ONLY'


def test_real_frozen_R15_remains_unpaired_and_all_six_contrasts_retained():
    r=build_audit(resamples=99)
    assert r['observed_R15_windows']==r['observed_TSV_rows']==4
    assert r['combined_records']==r['actual_count']==89 and r['requested_count']==90
    assert len(r['R15_contrasts'])==6
    assert all(c['family_size']==6 for c in r['R15_contrasts'])
    assert r['actual_crossover']['status']=='NOT_AVAILABLE_NO_IDENTIFIED_BLOCKS'
    assert r['actual_crossover']['paired_results'] is None
    assert r['independent_physical_repetition_identified'] is False
    assert all(d['received_RTT']==40 and d['declared_repetitions']==4 and not d['per_rep_arrays_retained'] for d in r['descriptions'])
    assert r['automatic_execution_allowed'] is r['physical_or_causal_acceptance'] is False
