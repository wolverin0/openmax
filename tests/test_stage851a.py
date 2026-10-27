"""Scheduler conservation, seeded sensitivity and Pareto checks; no radio access."""
import json
import math
import socket
import subprocess

import pytest

from tools.sim import run_stage851a_guarida_tower_v11_gps_sync_and_pb080_pareto as model


@pytest.fixture(autouse=True)
def offline_guard(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError('network and external processes forbidden')
    monkeypatch.setattr(socket.socket, 'connect', denied)
    monkeypatch.setattr(socket, 'create_connection', denied)
    monkeypatch.setattr(subprocess, 'Popen', denied)
    monkeypatch.setattr(subprocess, 'run', denied)


def assert_conservation(row):
    counts = row['conservation']
    assert counts['scheduled_packets'] == counts['sent_packets'] + counts['not_sent_packets']
    assert counts['sent_packets'] == (counts['completed_packets'] + counts['dropped_packets']
                                     + counts['unfinished_packets'])
    assert counts['sent_bytes'] == (counts['completed_bytes'] + counts['dropped_bytes']
                                   + counts['unfinished_bytes'])
    assert row['goodput_mbps'] == pytest.approx(counts['completed_bytes'] * 8 / row['duration_s'] / 1e6)
    assert row['events_processed'] <= model.EVENT_CAP
    assert counts['scheduled_packets'] <= model.PACKET_CAP


def test_scheduler_reproducible_conserves_and_keeps_zero_receivers():
    config = model.configurations()[0]
    first = model.simulate_window(config, model.SEED_BASE)
    assert first == model.simulate_window(config, model.SEED_BASE)
    assert_conservation(first)
    assert first['expected_active_cpes'] == len(first['per_cpe_goodput_mbps']) == 31
    goodputs = list(first['per_cpe_goodput_mbps'].values())
    expected = sum(goodputs)**2 / (31 * sum(value * value for value in goodputs))
    assert first['jain_fairness'] == pytest.approx(expected)
    assert first['p50_latency_ms'] <= first['p95_latency_ms'] <= first['p99_latency_ms']


def test_deadline_censoring_and_queue_drops_are_separate():
    row = model.simulate_window(model.configurations()[0], model.SEED_BASE, queue_cap=1)
    assert_conservation(row)
    assert row['conservation']['dropped_packets'] > 0
    assert row['conservation']['unfinished_packets'] >= 0
    assert row['drop_pct'] == pytest.approx(100 * row['conservation']['dropped_packets']
                                          / row['conservation']['sent_packets'])


def test_arrival_compression_changes_bursts_not_mean_offered_window_rate():
    configs = [next(config for config in model.configurations()
                    if config['arrival_compression_scale'] == scale
                    and config['gps_phase_error_us'] == 200 and config['pb080_batch'] == 1)
               for scale in model.ARRIVAL_COMPRESSIONS]
    rows = [model.simulate_window(config, model.SEED_BASE) for config in configs]
    assert len({row['conservation']['sent_bytes'] for row in rows}) == 1
    assert all(row['offered_window_mbps'] == pytest.approx(138.756) for row in rows)
    traces = [model.packet_trace(model.SEED_BASE, scale) for scale in model.ARRIVAL_COMPRESSIONS]
    assert traces[0][0]['arrival_s'] != traces[1][0]['arrival_s'] != traces[2][0]['arrival_s']


def test_zero_responses_have_no_perfect_latency_or_fairness():
    row = model.simulate_window(model.configurations()[0], model.SEED_BASE, horizon_s=1e-9)
    assert_conservation(row)
    assert row['p99_latency_ms'] is None
    assert row['jain_fairness'] is None
    assert row['latency_objective_ms'] > 0


@pytest.mark.parametrize('override', [dict(event_cap=0), dict(event_cap=2001),
                                     dict(queue_cap=0), dict(horizon_s=float('nan'))])
def test_bound_violations_rejected(override):
    with pytest.raises(ValueError):
        model.simulate_window(model.configurations()[0], model.SEED_BASE, **override)


def test_event_cap_stops_scheduler():
    with pytest.raises(ValueError, match='event cap'):
        model.simulate_window(model.configurations()[0], model.SEED_BASE, event_cap=1)


def test_known_pareto_fixture_and_matched_arrival_compression_requirement():
    assert sorted(model.nondominated_indices([[1,1], [2,2], [0,3], [1,1]])) == [0,2,3]
    with pytest.raises(ValueError):
        model.nondominated_indices([[float('nan'), 1]])
    with pytest.raises(ValueError, match='matched arrival compression'):
        model.optimize_scenario([dict(arrival_compression_scale=.7), dict(arrival_compression_scale=1.0)])


def test_full_1050_window_contract_atomic_artifact_and_nondominance(tmp_path):
    result = model.build(tmp_path)
    assert result['scenario_count'] == result['configuration_count'] == 105
    assert result['replication_count'] == len(result['windows']) == 1050
    assert result['replications_per_configuration'] == 10
    assert len({row['window_id'] for row in result['windows']}) == 1050
    assert all(row['evidence_type'] == 'SYNTHETIC' for row in result['windows'])
    assert all(math.isfinite(row[key]) for row in result['windows'] for key in (
        'goodput_mbps','p95_latency_ms','p99_latency_ms','drop_pct','jain_fairness'))
    for row in result['windows']:
        assert_conservation(row)
    for load, front in zip(model.ARRIVAL_COMPRESSIONS, result['pareto_by_arrival_compression']):
        rows = [row for row in result['configurations'] if row['arrival_compression_scale'] == load]
        exact = {rows[index]['config_id'] for index in model.nondominated_indices([row['objectives'] for row in rows])}
        assert set(front['exact_front_config_ids']) == exact
        assert set(front['optimizer_config_ids']).issubset(exact)
        assert front['optimizer_evaluations'] >= 35
    assert result['new_live_windows'] == result['historical_live_windows_added'] == 0
    assert result['accepted_live_windows'] is None
    assert result['hardware_acceptance'] == 'UNKNOWN'
    assert result['model_scope'] == 'burst timing sensitivity, not mean offered load'
    assert result['boundary']['network_access'] is False
    assert result['five_pillar_compliance'][model.c.PILLARS[4]]['ingested'] is False
    path = tmp_path / 'artifacts/autoresearch' / (model.STEM + '.json')
    assert json.loads(path.read_text()) == result
    assert not list(path.parent.glob('*.tmp'))
    text = (tmp_path / 'docs' / (model.STEM.upper() + '.md')).read_text()
    assert len(text.splitlines()) < 180
    assert text.count('<!-- doc-head:') == text.count('<!-- /doc-head -->') == 1
