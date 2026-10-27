"""Host-only statistical regressions: synthetic samples and frozen JSON, no bench."""
from itertools import combinations
import math
import json
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from analysis.statistics.fmx_r10_to_r14_causal_and_power_analysis import (
    _u_counts, build_analysis, conditional_tail_bootstrap, hodges_lehmann,
    holm_adjust, load_frozen_rounds, mwu_contrast, paired_wilcoxon,
    planning_power, required_sample_size,
)
import analysis.statistics.fmx_r10_to_r14_causal_and_power_analysis as module


@pytest.mark.parametrize("n,m", [(2, 2), (3, 4), (20, 40)])
def test_exact_U_integer_distribution_mass_symmetry(n, m):
    counts = _u_counts(n, m)
    assert sum(counts) == math.comb(n+m, n)
    assert counts == counts[::-1]
    assert len(counts) == n*m+1


def test_rank_inversion_CI_actual_finite_sample_null_coverage():
    # All70 random allocations under iid exchangeability, no Monte Carlo.
    # This checks coverage, not just a formula repeated from implementation.
    population = np.arange(8, dtype=float)
    covered = 0
    for chosen in combinations(range(8), 4):
        mask = np.array([i in chosen for i in range(8)])
        ci = hodges_lehmann(population[mask], population[~mask], alpha=0.2, continuous_shift=True)["interval_ms"]
        covered += ci[0] <= 0 <= ci[1]
    assert covered/70 == pytest.approx(0.8)


def test_HL_shift_sign_and_no_false_nm_independent_precision():
    a = hodges_lehmann([0,1,2], [5,6,7], alpha=0.2, continuous_shift=True)
    b = hodges_lehmann([5,6,7], [0,1,2], alpha=0.2, continuous_shift=True)
    assert a['estimate_ms'] == 5 and b['estimate_ms'] == -5
    # n=m=3 gives P(U<=1)=2/20=.1, hence criticalU1 at alpha=.2.
    assert a['critical_U'] == 1
    assert a['interval_ms'] == [4, 6]
    assert b['interval_ms'] == [-6, -4]
    assert hodges_lehmann([0,1], [5,6], continuous_shift=True)['interval_ms'] == [None, None]


def test_DKW_CI_ties_noninformative_small_n_and_conservative_large_n():
    tied = hodges_lehmann([1]*20, [2]*20, continuous_shift=True)
    assert tied['method'] == 'CONSERVATIVE_MARGINAL_DKW_QUANTILE_INVERSION'
    assert tied['interval_ms'] == [None, None]
    result = hodges_lehmann([1]*40, [2]*40)
    assert result['interval_ms'] == [1, 1]
    assert result['cdf_error_bound'] < 0.5
    assert result['ties'] is True


def test_mwu_real_tie_corrected_values_direction_and_zeros():
    x, y = [1,1,3,5], [2,2,4,6]
    result = mwu_contrast(x, y)
    direct = stats.mannwhitneyu(y, x, method='asymptotic', use_continuity=True)
    assert result['U_treatment'] == direct.statistic == 11
    assert result['p_value'] == pytest.approx(direct.pvalue)
    reverse = mwu_contrast(y, x)
    assert reverse['U_treatment'] + result['U_treatment'] == 16
    assert reverse['p_value'] == pytest.approx(result['p_value'])
    assert mwu_contrast([1,1], [1,1])['p_value'] == 1


def test_pairing_absent_not_inferred_from_equal_length_sorted_arrays():
    assert paired_wilcoxon([1,2,3], [4,5,6]) == dict(status='UNIDENTIFIED_PAIRING', p_value=None, pairs=None)


def test_wilcoxon_aligns_explicit_ids_not_position_and_all_zero_case():
    x, y = [1,4,7,8,11,13], [18,2,14,5,9,10]
    ids_x = ['a','b','c','d','e','f']
    ids_y = ['f','a','e','b','d','c']
    result = paired_wilcoxon(x, y, control_ids=ids_x, treatment_ids=ids_y)
    differences = np.array([1,1,3,1,3,5])
    assert result['p_value'] == stats.wilcoxon(differences).pvalue
    assert result['pairs'] == 6 and result['median_difference'] == 2
    assert paired_wilcoxon([1,2], [2,1], control_ids=['a','b'], treatment_ids=['b','a'])['p_value'] == 1


@pytest.mark.parametrize('left,right', [(['a','a'],['a','b']), (['a','b'],['a','c']), (['a'],['a','b']), ([1,2],[1,2])])
def test_bad_pair_identifiers_refused(left, right):
    with pytest.raises(ValueError):
        paired_wilcoxon([1,2], [3,4], control_ids=left, treatment_ids=right)


@pytest.mark.parametrize('bad', [True, float('nan'), float('inf'), -0.1, 0, 1])
def test_alpha_fail_closed(bad):
    with pytest.raises(ValueError):mwu_contrast([1,2], [3,4], alpha=bad)
    with pytest.raises(ValueError):hodges_lehmann([1,2], [3,4], alpha=bad)
    with pytest.raises(ValueError):conditional_tail_bootstrap([1,2], alpha=bad)


@pytest.mark.parametrize('bad', [[1,float('nan')], [1,float('inf')], [True,1], [], [[1],[2]]])
def test_bad_samples_refused(bad):
    with pytest.raises(ValueError):mwu_contrast(bad, [1,2])


def test_nonfinite_pair_arithmetic_fails_closed():
    with pytest.raises(ValueError, match='finite arithmetic'):
        hodges_lehmann([-1e308,-1e308], [1e308,1e308])


def test_bootstrap_reproducible_tails_bounded_by_observations_not_physical_CI():
    x = list(range(20))
    a = conditional_tail_bootstrap(x, seed=17, resamples=199)
    b = conditional_tail_bootstrap(x, seed=17, resamples=199)
    assert a == b
    assert a['estimate_ms'] == pytest.approx(18.05)
    low, high = a['percentile_interval_ms']
    assert 0 <= low <= high <= 19
    assert a['probability_max_exceeds_true_quantile_under_iid'] == pytest.approx(1-.95**20)
    assert 'serial/rep dependence' in a['limits']
    assert conditional_tail_bootstrap([5]*40, resamples=99)['percentile_interval_ms'] == [5,5]


def test_complete_Holm_family_does_not_drop_missing_R14():
    assert holm_adjust([None, .01, .04, .03]) == [None, .04, .09, .09]
    assert holm_adjust([.01, .04, .03])[0] == .03


@pytest.fixture(scope='module')
def actual_analysis():
    # Small Monte Carlo count for structural fixtures; delivered CLI uses1999.
    return build_analysis(resamples=99)


def test_actual_frozen_counts_loss_and_no_pairing_or_repetition_fabrication(actual_analysis):
    a = actual_analysis
    assert len(a['sources']) == 11
    assert len(a['descriptions']) == 25
    assert a['R12']['raw_received_counts'] == [40,40,39,40]
    assert a['R12']['lossful_iterations'] == ['r12_iter2_r10_max_tput_winner_n40']
    assert a['R12']['independent_physical_repetitions_identified'] is False
    assert len(a['contrasts']) == 52 and a['multiplicity']['missing_tests'] == 6
    assert all(c['family_size_including_missing'] == 52 for c in a['contrasts'])
    assert all(d['wilcoxon_status'] == 'UNIDENTIFIED_PAIRING' for d in a['descriptions'])
    assert all(d['raw_per_rep_arrays_available'] is False for d in a['descriptions'])
    assert sum(d['lossful'] for d in a['descriptions']) == 2  # R11stock +R12iter2
    assert all(c['paired_wilcoxon']['status'] == 'UNIDENTIFIED_PAIRING' and c['paired_wilcoxon']['p_value'] is None for c in a['contrasts'] if c['p_value'] is not None)


def test_missing_historical_recipe_is_unknown_complete_not_gate(tmp_path, monkeypatch):
    original_root = module.ROOT
    manifest = json.loads((module.ARTIFACTS/'inputs_manifest.json').read_text(encoding='utf-8'))
    chosen = [r for r in manifest if (r['kind']=='receipt' and any(f'_r{i}_' in Path(r['path']).name for i in range(10,15))) or (r['kind']=='recipe' and '_r7_' in Path(r['path']).name)]
    inputs = tmp_path/'inputs'; inputs.mkdir()
    for entry in chosen:
        old = original_root/entry['path']
        entry['path'] = 'inputs/'+old.name
        if entry['kind']=='receipt':(tmp_path/entry['path']).write_bytes(old.read_bytes())
    (tmp_path/'inputs_manifest.json').write_text(json.dumps(chosen),encoding='utf-8')
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    rounds, refs = load_frozen_rounds(tmp_path)
    assert set(rounds)=={'R10','R11','R12','R13','R14'}
    absent = [r for r in refs if r.get('status')=='UNKNOWN_LOCAL_ARTIFACT_ABSENT']
    assert len(absent)==1 and absent[0]['check_complete'] is True
    # Even missing historical manifest entries do not invent a dependency gate.
    (tmp_path/'inputs_manifest.json').write_text(json.dumps([r for r in chosen if r['kind']!='recipe']),encoding='utf-8')
    _, refs = load_frozen_rounds(tmp_path)
    assert any(r.get('status')=='UNKNOWN_LOCAL_ARTIFACT_ABSENT' and r['check_complete'] for r in refs)


def test_actual_timing_BE_and_crypto_boundaries(actual_analysis):
    a = actual_analysis
    timing = a['R13']['contrasts']
    assert timing[0]['changed_declared_fields'] == {'distance_meters':[0,1500]}
    assert timing[1]['changed_declared_fields'] == {'distance_meters':[1500,3000]}
    assert timing[2]['changed_declared_fields'] == {'be_low_us':[1800,1900], 'be_high_us':[3600,3800], 'aql_threshold_us':[7200,7600]}
    assert a['R14']['associated_CPE_labels'] == ['Loco195']
    assert a['R14']['measured_three_CPE_claim'] is False
    assert a['R14']['raw_RTT_available'] is False
    assert a['R14']['encryption_status'].startswith('DECLARED_')
    assert a['R14']['prior_encryption_status'].startswith('INFERRED_')
    for row in a['R14']['matched_declared_policy_cross_round']:
        assert row['reported_numeric_knobs_equal'] and row['p_value'] is None
    for row in (d for d in a['descriptions'] if d['round_id']=='R14'):
        assert row['conditional_tail_intervals'] is None and row['raw_received_RTT'] == 0


def test_prospective_power_golden_sensitivity_not_observed_power(actual_analysis):
    assert required_sample_size(.5, design='paired')['analyzed_units'] == 34
    assert required_sample_size(.5, design='independent')['analyzed_units'] == 64
    assert planning_power(4,.2) < planning_power(4,.8) < planning_power(40,.8)
    assert actual_analysis['planning']['kind'].startswith('PROSPECTIVE_')
    assert actual_analysis['automatic_execution_allowed'] is False
