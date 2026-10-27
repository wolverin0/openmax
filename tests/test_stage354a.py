"""Contract tests for the synthetic model; no radio or native runner imports."""
import ast
from dataclasses import replace
import json
import math
from pathlib import Path

import pytest

from tools.sim import build_stage354a_wmi_4series_retry_fallback_pareto as m


def test_four_series_stbc_and_separate_cdd_assumption():
    p = m.make_policy()
    assert [s.nss for s in p.series] == [2, 2, 1, 1]
    assert p.series[2].chain_mask == 3 and p.series[2].stbc is True
    assert p.series[3].chain_mask == 1 and p.series[3].stbc is False
    with pytest.raises(ValueError, match='CDD'):
        m.make_policy(final_branch='cdd_hypothesis')
    cdd = m.make_policy(final_branch='cdd_hypothesis', cdd_model_assumption=True)
    assert cdd.series[3].chain_mask == 3 and cdd.series[3].stbc is False
    assert not cdd.as_dict()['cdd_configuration_encoded_by_stbc_bit']
    for plan in (p, cdd):
        with pytest.raises(m.NativeWmiAbiUnqualified):
            plan.native_payload()


@pytest.mark.parametrize('change', [dict(ldpc=False), dict(stbc=False), dict(sgi=False),
                                  dict(max_nss=1), dict(tx_chain_mask=1), dict(max_vht_mcs=3)])
def test_required_declared_capability_guard(change):
    with pytest.raises(ValueError):
        m.make_policy(capabilities=m.PeerCapabilities(**change))


@pytest.mark.parametrize('kwargs', [dict(initial_mcs=True), dict(initial_mcs=9),
                                   dict(attempts=(0, 1, 1, 1)), dict(attempts=(True, 1, 1, 1)),
                                   dict(attempts=(4, 4, 4, 4)), dict(final_branch='STBC_ONE_CHAIN')])
def test_invalid_policy(kwargs):
    with pytest.raises(ValueError):
        m.make_policy(**kwargs)


def test_direct_policy_invariants_cannot_bypass_builder():
    p = m.make_policy()
    bad = replace(p.series[2], stbc=False)
    with pytest.raises(ValueError):
        replace(p, series=(p.series[0], p.series[1], bad, p.series[3]))


@pytest.mark.parametrize('values', [dict(rate=9, nss=3, chain_mask=7),
                                   dict(rate=6, nss=3, chain_mask=7),
                                   dict(rate=6, nss=2, chain_mask=7),
                                   dict(rate=0, nss=1, chain_mask=1, preamble_type=0, ldpc=0),
                                   dict(rate=6, nss=2, chain_mask=3, preamble_type=2),
                                   dict(rate=6, nss=2, chain_mask=3, sgi=1),
                                   dict(rate=6, nss=2, chain_mask=3, sgi=2),
                                   dict(rate=6, nss=2, chain_mask=3, ldpc=3),
                                   dict(rate=6, nss=2, chain_mask=3, txbf=True)])
def test_baseline_constructor_rejects_unmodeled_series(values):
    baseline = next(p for p in m.policies() if p.kind == 'MODELED_BASELINE_PROXY')
    descriptor = m.SeriesBwDescriptor(**values)  # Valid shared hardware domain, not this model domain.
    with pytest.raises(ValueError):
        replace(baseline, series=(descriptor,) * 4)


def assert_conservation(r):
    assert r['generated'] == r['delivered'] + r['retry_exhausted'] + r['queue_dropped']
    assert r['outstanding'] == 0
    assert r['offered_bytes'] == r['delivered_bytes'] + r['dropped_bytes']
    assert r['attempts_total'] == sum(r['attempts_by_series'])
    assert 0 <= r['busy_ms'] <= r['elapsed_ms'] + 1e-8
    assert r['event_steps'] < r['event_cap'] and r['elapsed_ms'] <= r['horizon_cap_ms']
    assert 0 <= r['loss_ratio'] <= 1
    if r['elapsed_ms']:
        assert math.isclose(r['goodput_mbps'], r['delivered_bytes'] * 8 / (r['elapsed_ms'] * 1000))
    json.dumps(r, allow_nan=False)


def test_no_error_single_packet_analytical_accounting():
    r = m.simulate(m.make_policy(), 'balanced_control', 354, packets=1, success_override=1.)
    assert r['delivered'] == 1 and r['attempts_total'] == 1 and r['loss_ratio'] == 0
    assert r['attempts_by_series'] == [1, 0, 0, 0]
    assert r['delivered_delay_p50_ms'] == r['busy_ms'] == r['terminal_delay_p99_ms']
    assert_conservation(r)


def test_total_loss_consumes_every_allowed_retry_and_never_counts_payload():
    p = m.make_policy()
    r = m.simulate(p, 'multipath_bursts', 7, packets=12, queue_limit=128, success_override=0.)
    assert r['retry_exhausted'] == 12 and r['queue_dropped'] == 0
    assert r['attempts_total'] == 12 * sum(p.attempts)
    assert r['delivered_bytes'] == 0 and r['goodput_mbps'] == 0 and r['loss_ratio'] == 1
    assert r['delivered_delay_p99_ms'] is None
    assert_conservation(r)


def test_empty_and_queue_overflow_are_explicit_terminal_outcomes():
    empty = m.simulate(m.make_policy(), 'balanced_control', 1, packets=0)
    assert empty['generated'] == empty['elapsed_ms'] == empty['goodput_mbps'] == 0
    assert empty['terminal_delay_p99_ms'] is None
    assert_conservation(empty)
    r = m.simulate(m.make_policy(), 'balanced_control', 1, packets=32, queue_limit=0,
                   arrival_interval_ms=.00001, success_override=1.)
    assert r['queue_dropped'] > 0 and r['loss_ratio'] > 0
    assert_conservation(r)


@pytest.mark.parametrize('kwargs', [dict(seed=True), dict(packets=-1), dict(packets=1025),
                                   dict(queue_limit=True), dict(payload_bytes=0),
                                   dict(arrival_interval_ms=0), dict(arrival_interval_ms=float('inf')),
                                   dict(success_override=True), dict(success_override=float('nan')),
                                   dict(success_override=1.01)])
def test_invalid_simulation_parameters(kwargs):
    args = dict(seed=354, packets=4)
    args.update(kwargs)
    with pytest.raises(ValueError):
        m.simulate(m.make_policy(), 'balanced_control', **args)


def test_seed_control_reproducibility_and_actual_parameter_sensitivity():
    p = m.make_policy()
    a = m.simulate(p, 'foliage_chain0_stronger', 354, packets=24)
    assert a == m.simulate(p, 'foliage_chain0_stronger', 354, packets=24)
    assert a != m.simulate(p, 'foliage_chain0_stronger', 355, packets=24)
    for scenario in m.SCENARIOS:
        for seed in m.SEEDS:
            assert_conservation(m.simulate(p, scenario, seed, packets=24))
    # A synthetic mirrored chain impairment must affect the chosen final chain.
    a = m._success_probability(p.series[3], (25., 0.), 0.)
    other = m._success_probability(m.make_policy(final_branch='chain1').series[3], (25., 0.), 0.)
    assert a > other
    assert m._success_probability(p.series[0], (20., 20.), 5.) < m._success_probability(p.series[0], (20., 20.), 0.)


def test_pymoo_pareto_matches_independent_dominance_and_order_invariance():
    rows = [dict(policy_id=k, objectives=f) for k, f in
            [('a', [-10., 5., .1]), ('b', [-12., 4., .05]), ('c', [-8., 2., .01]), ('d', [-12., 4., .05])]]
    expected = [r['policy_id'] for r in rows if not any(
        all(a <= b for a, b in zip(other['objectives'], r['objectives'])) and
        any(a < b for a, b in zip(other['objectives'], r['objectives'])) for other in rows)]
    result = m.rank_pareto(rows)
    assert sorted(result['pareto_ids']) == sorted(expected)
    assert result == m.rank_pareto(list(reversed(rows)))
    assert result['n_evaluated'] == 4 and result['n_generations'] == 1
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize('rows', [[], [dict(policy_id=[], objectives=[0, 0, 0])],
                                 [dict(policy_id='a', objectives=[True, 0, 0])],
                                 [dict(policy_id='a', objectives=[float('inf'), 0, 0])],
                                 [dict(policy_id='a', objectives=[0, 0, 0])] * 2])
def test_invalid_pareto_inputs(rows):
    with pytest.raises(ValueError):
        m.rank_pareto(rows)


def test_complete_small_study_repro_and_baseline_qualification():
    a = m.analyze(packets=4)
    assert a == m.analyze(packets=4)
    assert a['summary']['candidates'] == 18 and a['summary']['replications'] == 240
    assert len(a['policies']) == a['pareto']['n_evaluated'] == 20
    assert {r['policy_id'] for r in a['policies'] if r['kind'] == 'MODELED_BASELINE_PROXY'} == {
        'FIXED_2SS_PROXY', 'DESCENDING_2SS_PROXY'}
    for row in a['policies']:
        assert len(row['runs']) == 12
        for run in row['runs']:
            assert_conservation(run)


def test_saved_artifact_header_bindings_doc_and_no_hardware_executor():
    r = m.c.load(m.ROOT / m.OUT)
    assert r['summary']['replications'] == 240 and r['summary']['hardware_results'] == 0
    assert r['primary_descriptor_header']['source']['sha256'] == m.HEADER_SHA256
    assert r['primary_descriptor_header']['source']['path'] == m.SERIES_HEADER
    assert not Path(m.SERIES_HEADER).is_absolute()
    sender = r['binary_sender']
    assert sender['declared_length_bytes'] == 188 and sender['declared_command_id'] == 0x9044
    assert not sender['native_series_layout_authenticated']
    assert len(sender['bounded_instruction_checks']) == 4
    assert m.c.sha(m.c.read(m.ROOT / sender['path'])) == sender['sha256']
    for src in r['static_sources']:
        assert m.c.sha(m.c.read(m.ROOT / src['path'])) == src['sha256']
    b = r['boundary']
    assert b['native_188b_wmi_abi'] == 'BLOCKED' and b['native_wmi_payload_hex'] is None
    assert not any(b[k] for k in ('hardware_access', 'network_access', 'module_execution',
                                  'deployment_allowed', 'physical_acceptance', 'measured_rf_improvement',
                                  'packet_fields_complete', 'transport_endianness_verified'))
    text = (m.ROOT / m.DOC).read_text('utf-8')
    assert text.startswith('<!-- doc-head:') and len(text.splitlines()) < 220
    assert text.count('<!-- doc-head:') == text.count('<!-- /doc-head -->') == 1
    assert m.c.sha((m.ROOT / m.DOC).read_bytes()) == r['outputs'][m.DOC]['sha256']
    tree = ast.parse(Path(m.__file__).read_text('utf-8'))
    imports = [n.module or '' for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    assert not any(x.startswith(('tools.bench', 'tools.deploy', 'paramiko', 'socket', 'subprocess')) for x in imports)


def test_build_from_portable_fixture_root_without_global_temp_header(tmp_path):
    source = m.c.load(m.ROOT / m.OUT)
    paths = [s['path'] for s in source['static_sources']] + [m.SERIES_HEADER, source['binary_sender']['path']]
    for relative in paths:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((m.ROOT / relative).read_bytes())
    report = m.build(tmp_path)
    assert report['primary_descriptor_header']['source']['path'] == m.SERIES_HEADER
    assert report['primary_descriptor_header']['source']['sha256'] == m.HEADER_SHA256
    assert (tmp_path / m.OUT).is_file() and (tmp_path / m.DOC).is_file()
    assert (tmp_path / m.OUT).read_bytes() == (m.ROOT / m.OUT).read_bytes()
