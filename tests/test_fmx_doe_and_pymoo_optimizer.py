"""Pure offline numerical contracts, plus mandatory native pymoo integration checks."""

from copy import deepcopy
from dataclasses import replace
import importlib.util
import json

import numpy as np
import pytest

from orchestration.autoresearch.fmx_offline_data import (
    DEFAULT_RECEIPTS, ROOT, load_measurements, local_json, finite_number, write_json,
)
from orchestration.autoresearch.fmx_doe_and_pymoo_optimizer import (
    FACTORS, INPUTS_CATALOG, Factor, KernelSurrogate, build_dataset, candidate_grid,
    catalog_coverage, d_optimal_design, fractional_factorial, grouped_validation,
    model_matrix, nondominated_indices, optimize_pareto, policy_from_levels,
)


def test_saved_data_counts_and_receiver_aggregation():
    records, refs = load_measurements()
    assert len(records) == 13 and len(refs) == 2
    assert sum(row.round_id == 'R1' for row in records) == 8
    assert sum(row.round_id == 'R2' for row in records) == 5
    assert all(len(row.goodputs_mbps) == 2 and len(row.rtts_ms) == 6 for row in records)
    assert all(row.goodput_mbps == pytest.approx(np.mean(row.goodputs_mbps)) for row in records)


@pytest.mark.parametrize('value', [True, float('nan'), float('inf'), -float('inf'), '28', 10**1000])
def test_nonfinite_and_boolean_numbers_rejected(value):
    with pytest.raises(ValueError):
        finite_number(value, 'example')


def test_bad_receiver_aggregate_is_not_silently_repaired(tmp_path):
    payload = local_json(DEFAULT_RECEIPTS[0])
    payload['iterations'][0]['observation']['goodput_rx_mbps'] += 1
    path = tmp_path/'bad.json'
    path.write_text(json.dumps(payload), encoding='utf-8')
    with pytest.raises(ValueError, match='disagrees'):
        load_measurements([path])


@pytest.mark.parametrize('path',[
    ROOT/'artifacts/autoresearch/lap120_loco195_live_autoresearch_20261024.json',
    DEFAULT_RECEIPTS[0], ROOT/'artifacts/autoresearch/waves_abcd_20261024/NUL',
    ROOT/'artifacts/autoresearch/waves_abcd_20261024/file.json:stream',
])
def test_generated_outputs_cannot_overwrite_inputs_or_devices(path):
    with pytest.raises(ValueError):write_json(path,{'should_not_write':True})


def test_catalog_coverage_never_enables_unmodeled_controls():
    catalog = local_json(INPUTS_CATALOG)
    coverage = catalog_coverage(catalog)
    assert len(coverage) == 248
    by_id = {entry['id']:entry for entry in coverage}
    assert by_id['ct_special_6']['disposition'] == 'excluded_by_source_or_scope'
    assert by_id['ct_special_7']['disposition'] == 'measured_model_domain_only'
    assert any(entry['disposition'] == 'unmodeled_no_empirical_response' for entry in coverage)
    assert all(entry['automatic_execution_allowed'] is False for entry in coverage)
    for mutation in ('root', 'entry'):
        broken = deepcopy(catalog)
        if mutation == 'root':
            broken['actuation'] = 'live'
        else:
            broken['knobs'][0]['enabled'] = True
        with pytest.raises(ValueError):
            catalog_coverage(broken)


def test_coupled_aql_and_discrete_domain():
    assert policy_from_levels((2000,28,0,300,3,64))[:3] == (2000,4000,8000)
    assert policy_from_levels((5000,50,0,300,3,64))[:3] == (5000,12000,24000)
    with pytest.raises(ValueError):
        policy_from_levels((999,28,0,300,3,64))


def test_half_fraction_balance_rank_alias_and_seed():
    factors = tuple(Factor(name, (0,1), ()) for name in ('A','B','C'))
    design = fractional_factorial(factors, seed=7)
    assert design == fractional_factorial(factors, seed=7)
    assert len(design['rows']) == 4
    assert design['main_effect_rank'] == design['main_effect_columns'] == 4
    assert design['resolution'] == 3
    assert len(design['main_and_two_way_aliases']) == 3
    assert np.all(np.sum(design['rows'], axis=0) == 2)
    assert set(map(tuple,design['rows'])) == set(map(tuple,fractional_factorial(factors,seed=8)['rows']))


def test_d_optimal_rank_unique_seed_and_information_gain():
    design = d_optimal_design(n_runs=12, seed=9)
    assert design == d_optimal_design(n_runs=12, seed=9)
    rows = np.array(design['rows'])
    matrix, terms = model_matrix(rows)
    assert len(np.unique(rows,axis=0)) == 12
    assert design['model_rank'] == len(terms) == len(FACTORS)+1
    assert np.linalg.slogdet(matrix.T@matrix)[1] == pytest.approx(design['log_determinant'])
    assert np.all(np.diff(design['regularized_selection_logdet_history']) >= -1e-5)
    assert design['optimality_certificate'] is False


@pytest.mark.parametrize('n', [0, 3, 10000])
def test_d_design_rejects_unestimable_or_excessive_budget(n):
    with pytest.raises(ValueError):
        d_optimal_design(n_runs=n)


def test_surrogate_validation_removes_whole_policy_groups():
    records, _ = load_measurements()
    validation = grouped_validation(records)
    assert len(validation['rows']) == len(records)
    assert np.isfinite(validation['rmse']).all()
    for row in validation['rows']:
        assert row['held_out_policy'] not in row['train_policies']
    estimate = KernelSurrogate(records).predict(records[0].knobs)
    assert 0 <= estimate['p95_ms'] <= estimate['p99_ms']
    assert estimate['prediction_kind'].startswith('exploratory')


def test_surrogate_rejects_unknown_round_and_nonfinite_training():
    records, _ = load_measurements()
    for bad in (replace(records[0], round_id='R3'), replace(records[0],goodput_mbps=float('inf'))):
        with pytest.raises(ValueError):
            KernelSurrogate([bad,*records[1:]])


def test_dominance_signs_and_ties():
    assert nondominated_indices([[-100,10],[-80,20],[-70,5],[-100,10]]) == [0,2,3]
    with pytest.raises(ValueError):
        nondominated_indices([[1,float('nan')]])


def test_missing_native_library_preserves_design_and_explicit_block(monkeypatch):
    def unavailable(*args,**kwargs):
        raise RuntimeError('missing offline dependency') from ImportError('pymoo')
    monkeypatch.setattr('orchestration.autoresearch.fmx_doe_and_pymoo_optimizer.optimize_pareto',unavailable)
    dataset = build_dataset()
    assert dataset['d_optimal']['model_rank'] == len(FACTORS)+1
    assert dataset['native_integration_status'] == 'BLOCKED_OFFLINE_PYMOO_DEPENDENCY'
    assert dataset['optimizations'] == [] and len(dataset['required_pending_algorithms']) == 2


@pytest.mark.parametrize('algorithm', ['nsga2','nsga3'])
@pytest.mark.skipif(importlib.util.find_spec('pymoo') is None,
                    reason='MANDATORY native pymoo integration BLOCKED: offline library unavailable')
def test_native_pymoo_discrete_pareto_and_reproducibility(algorithm):
    records, _ = load_measurements()
    result = optimize_pareto(records,algorithm,seed=4,population=20,generations=4)
    repeat = optimize_pareto(records,algorithm,seed=4,population=20,generations=4)
    assert result == repeat and result['pareto']
    assert result['evaluations'] <= 20*4
    objectives=[]
    for candidate in result['pareto']:
        assert not candidate['automatic_execution_allowed'] and not candidate['physical_safety_qualified']
        assert candidate['prediction']['distance_to_training'] <= 0.75+1e-8
        objectives.append([-candidate['prediction']['goodput_mbps'],candidate['prediction']['p95_ms'],candidate['prediction']['p99_ms']])
    assert nondominated_indices(objectives) == list(range(len(objectives)))
