"""PB campaign integrity regressions; all local observations are synthetic fixtures."""
from dataclasses import replace
import hashlib
import json

from analysis.regression_gate.gatekeeper import RunMetrics
from analysis.regression_gate.gatekeeper import RegressionGatekeeper
from controller.pb_060_070_autonomous_search_and_phy_gate import (
    SearchCandidateConfig, build_pb_060_070_pilot_report, deduplicate_candidates,
    evaluate_pb060_search_campaign,
)


def candidate(name='candidate', negative=False):
    return SearchCandidateConfig(name, 20, 18, True, False, True, 256, 3000, negative)


def runs(prefix, config, *, improvement=True):
    result = []
    for index in range(8):
        for arm in ('A', 'B'):
            change = improvement and arm == 'B'
            row = RunMetrics(run_id=f'{prefix}_{arm}_{index}', arm=arm,
                evidence_state='SYNTHETIC',
                goodput_mbps=120 if change else 100, p95_lat_ms=6 if change else 15,
                p99_lat_ms=10 if change else 25, loss_pct=.1, jain_fairness=.9,
                channel_width_mhz=20, block_index=index, worst_peer_goodput_mbps=30)
            row.applied_config_sha256 = config.fingerprint()
            result.append(row)
    return result


def campaign(*, with_control=True, empty_control=False):
    cand = candidate()
    ctrl = candidate('negative', True)
    configs = [cand, ctrl] if with_control else [cand]
    discovery = {'candidate': runs('disc', cand)}
    if with_control and not empty_control:
        discovery['negative'] = runs('null', ctrl, improvement=False)
    holdout = {'candidate': runs('hold', cand)}
    return configs, discovery, holdout


def test_missing_and_unobserved_controls_invalidate_campaign():
    for kwargs in ({'with_control': False}, {'empty_control': True}):
        result = evaluate_pb060_search_campaign(*campaign(**kwargs))
        assert result['campaign_passed'] is False
        assert result.get('integrity_errors')
        assert all(row['final_verdict'] not in ('PROMOTE', 'KEEP_FOR_REPLICATION', 'SYNTHETIC_PASS')
                   for row in result['candidate_evaluations'])


def test_synthetic_pilot_never_becomes_physical_promotion():
    result = build_pb_060_070_pilot_report()['pb060_autonomous_search_pilot']
    assert result['campaign_passed'] is False
    assert result['promoted_candidate_ids'] == []
    assert result['evidence_state'] == 'SYNTHETIC'
    assert result['diagnostic_passed'] is True
    assert any(row['final_verdict'] == 'SYNTHETIC_PASS' for row in result['candidate_evaluations'])


def test_duplicate_candidate_ids_are_rejected_not_silently_deduplicated():
    configs, disc, hold = campaign()
    configs.append(replace(configs[0], tx_power_dbm=19))
    result = evaluate_pb060_search_campaign(configs, disc, hold)
    assert not result['campaign_passed']
    assert any('duplicate' in error.lower() for error in result.get('integrity_errors', []))


def test_control_role_is_not_dropped_by_config_deduplication():
    normal, control = candidate('same_config'), candidate('control', True)
    unique, skipped = deduplicate_candidates([normal, control])
    assert {c.candidate_id for c in unique} == {'same_config', 'control'}
    assert skipped == []
    assert normal.fingerprint() == control.fingerprint()
    assert len(normal.fingerprint()) == 64


def test_extraneous_datasets_invalidate_campaign():
    configs, disc, hold = campaign()
    disc['not_declared'] = runs('extra', configs[0])
    result = evaluate_pb060_search_campaign(configs, disc, hold)
    assert not result['campaign_passed']
    assert any('extraneous' in error.lower() for error in result.get('integrity_errors', []))


def test_reused_discovery_ids_never_count_as_holdout():
    configs, disc, hold = campaign()
    hold['candidate'] = disc['candidate']
    result = evaluate_pb060_search_campaign(configs, disc, hold)
    assert not result['campaign_passed']
    assert result.get('integrity_errors') or any(
        'HOLDOUT' in row['final_verdict'] for row in result['candidate_evaluations'])


def test_candidate_is_bound_to_applied_config_fingerprint():
    configs, disc, hold = campaign()
    for row in disc['candidate'] + hold['candidate']:
        if row.arm == 'B':
            row.applied_config_sha256 = 'f' * 64
    result = evaluate_pb060_search_campaign(configs, disc, hold)
    assert not result['campaign_passed']
    assert any('config' in error.lower() for error in result.get('integrity_errors', []))


def test_improving_control_invalidates_and_is_retained():
    configs, disc, hold = campaign()
    disc['negative'] = runs('bad_control', configs[1], improvement=True)
    result = evaluate_pb060_search_campaign(configs, disc, hold)
    assert not result['campaign_passed']
    assert result['negative_control_false_positives'] >= 1
    assert any(row['candidate_id'] == 'negative' for row in result['candidate_evaluations'])


def test_incomplete_control_is_not_a_measured_null():
    configs, disc, hold = campaign()
    disc['negative'] = disc['negative'][:3]
    result = evaluate_pb060_search_campaign(configs, disc, hold)
    assert not result['campaign_passed']
    assert result.get('integrity_errors')


def test_underpowered_null_or_mutated_control_is_rejected():
    for pairs in (4, 8):
        configs, disc, hold = campaign()
        disc['negative'] = disc['negative'][:pairs * 2]
        if pairs == 8:
            disc['negative'][0].goodput_per_mhz = 999
        result = evaluate_pb060_search_campaign(configs, disc, hold)
        assert not result['diagnostic_passed']
        assert result['integrity_errors']


def test_mixed_width_pair_is_rejected_under_current_canonical_contract():
    configs, disc, hold = campaign()
    configs[0] = replace(configs[0], channel_width_mhz=10)
    for row in disc['candidate'] + hold['candidate']:
        if row.arm == 'B':
            row.channel_width_mhz = 10
            row.goodput_per_mhz = None
            row.applied_config_sha256 = configs[0].fingerprint()
    result = evaluate_pb060_search_campaign(configs, disc, hold)
    assert not result['diagnostic_passed']
    assert any('channel-width' in error for error in result['integrity_errors'])
    assert not result['campaign_passed']


def physical_schema_fixture(root):
    """Trusted-instrument schema/arithmetic fixture, NOT acquired radio evidence."""
    target = candidate()
    control = replace(candidate('negative', True), aql_be_limit_us=4000)
    root.mkdir(parents=True, exist_ok=True)
    def cohort(prefix, baseline, treatment, start, improved):
        rows = []
        for index in range(8):
            for arm in ('A', 'B'):
                config = baseline if arm == 'A' else treatment
                latency = 10.0 if improved and arm == 'B' else 25.0
                begin = start + index * 2 + (arm == 'B')
                row = RunMetrics(run_id=f'{prefix}_{arm}_{index}', arm=arm,
                    goodput_mbps=100.0, p95_lat_ms=latency, p99_lat_ms=latency,
                    loss_pct=0.0, jain_fairness=1.0, channel_width_mhz=20,
                    block_index=index, worst_peer_goodput_mbps=50.0,
                    evidence_state='BENCH_EXECUTED', session_id=prefix, peer_id='aggregate',
                    window_start_s=begin, window_end_s=begin + 1,
                    applied_config_sha256=config.fingerprint(), raw_evidence_path=f'{prefix}_{arm}_{index}.json')
                record = {name: getattr(row, name) for name in (
                    'run_id','arm','block_index','is_sentinel','session_id','peer_id',
                    'window_start_s','window_end_s','evidence_state')}
                record['metrics'] = {name: getattr(row, name) for name in (
                    'goodput_mbps','p95_lat_ms','p99_lat_ms','loss_pct','jain_fairness',
                    'channel_width_mhz','worst_peer_goodput_mbps','firmware_resets')}
                record['config_readback'] = config.canonical_payload()
                record['acquisition'] = dict(packets_sent=10, packets_received=10,
                    capture_drops=0, goodput_source='receiver', latencies_ms=[latency] * 10,
                    percentile_method='nearest_rank', duration_seconds=1.0,
                    receiver_bytes=12_500_000, expected_peers=['p0','p1'],
                    peer_goodput_mbps={'p0':50.0,'p1':50.0})
                blob = json.dumps(record, sort_keys=True).encode()
                (root / row.raw_evidence_path).write_bytes(blob)
                row.raw_sha256 = hashlib.sha256(blob).hexdigest()
                rows.append(row)
        return rows
    discovery = cohort('discovery', control, target, 100.0, True)
    holdout = cohort('holdout', control, target, 200.0, True)
    null = cohort('null', control, control, 300.0, False)
    gate = RegressionGatekeeper(evidence_root=root, min_blocks_for_keep=4, min_blocks_for_promote=6)
    receipt = dict(evidence_state='BENCH_REPLICATED', candidate_fingerprint=target.fingerprint(),
        discovery=[dict(run_id=row.run_id,raw_sha256=row.raw_sha256) for row in discovery],
        holdout=[dict(run_id=row.run_id,raw_sha256=row.raw_sha256) for row in holdout],
        frozen_plan=dict(created_at_s=0.0, family_fingerprints=[target.fingerprint()], contract=gate.frozen_contract))
    (root / 'replication.json').write_text(json.dumps(receipt), encoding='utf-8')
    return [target, control], {'candidate':discovery,'negative':null}, {'candidate':holdout}


def test_file_backed_physical_schema_can_pass_without_relaxing_objective(tmp_path):
    args = physical_schema_fixture(tmp_path)
    result = evaluate_pb060_search_campaign(*args, evidence_root=tmp_path,
        replication_receipts_by_candidate={'candidate':'replication.json'})
    assert result['campaign_passed'], result['integrity_errors']
    assert result['promoted_candidate_ids'] == ['candidate']
    assert result['evidence_state'] != 'SYNTHETIC'
    assert result['objective'] == 'LATENCY_WITH_CAPACITY_NONINFERIORITY'


def test_physical_schema_without_file_backed_replication_never_promotes(tmp_path):
    result = evaluate_pb060_search_campaign(*physical_schema_fixture(tmp_path), evidence_root=tmp_path)
    assert result['campaign_passed'] is False
    assert result['promoted_candidate_ids'] == []


def test_raw_byte_tampering_invalidates_whole_campaign(tmp_path):
    args = physical_schema_fixture(tmp_path)
    path = tmp_path / args[1]['candidate'][0].raw_evidence_path
    path.write_bytes(path.read_bytes() + b'\n')
    result = evaluate_pb060_search_campaign(*args, evidence_root=tmp_path,
        replication_receipts_by_candidate={'candidate':'replication.json'})
    assert not result['campaign_passed']
    assert any('SHA' in error for error in result['integrity_errors'])
