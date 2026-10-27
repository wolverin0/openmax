"""Frozen physical records: preserve evidence and the actual experimental units."""
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json

import pytest

from orchestration.autoresearch import fmx_offline_data as data


def receipt(number):
    path = data.R16_TO_R21_RECEIPTS[number - 16]
    return json.loads(path.read_text(encoding='utf-8'))


def write_receipt(tmp_path, payload):
    path = tmp_path / 'receipt.json'
    path.write_text(json.dumps(payload), encoding='utf-8')
    return path


def test_default_corpus_and_legacy_output_are_exactly_preserved():
    records, refs = data.load_all21_measurements()
    prior = json.loads(data.R15_NORMALIZED_OUTPUT.read_text(encoding='utf-8'))
    old = [row for row in records if int(row.round_id[1:]) <= 15]
    assert [{**asdict(row), 'policy_key': row.policy_key} for row in old] == [
        {**row, 'ap_policy': {**row['ap_policy'], 'aql_by_ac': tuple(tuple(v) for v in row['ap_policy']['aql_by_ac'])},
         'cpe_policy': None if row['cpe_policy'] is None else {**row['cpe_policy'], 'aql_by_ac': tuple(tuple(v) for v in row['cpe_policy']['aql_by_ac'])},
         **{key: tuple(row[key]) for key in ('goodputs_mbps', 'rtts_ms', 'flags', 'associated_cpes')}}
        for row in prior['records']]
    assert len(records) == 112 and len(old) == 89 and len(refs) == 21
    assert [sum(r.round_id == f'R{i}' for r in records) for i in range(16, 22)] == [3, 4, 4, 4, 4, 4]
    assert len(data.load_all21_measurements(include_auxiliary=False)[0]) == 110


def test_frozen_manifest_has_exactly_the_eighteen_authorized_files():
    manifest = json.loads((data.QRST_ARTIFACTS / 'inputs_manifest.json').read_text())
    assert len(manifest) == 18
    for row in manifest:
        raw = (data.ROOT / row['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['sha256']
        assert len(raw) == row['bytes']


def test_88_crossed_observations_are_24_matched_units_not_88_trials():
    blocks = data.load_all21_block_observations()
    crossed, sequential = blocks['crossed'], blocks['sequential']
    assert len(crossed) == 88
    assert len({(b['round_id'], b['block_index']) for b in crossed}) == 24
    assert [sum(b['round_id'] == f'R{i}' for b in crossed) for i in (16, 18, 19, 20, 21)] == [24, 16, 16, 16, 16]
    assert len(sequential) == 16 and all(b['round_id'] == 'R17' for b in sequential)
    assert all('crossover_step' not in b for b in sequential)
    assert all('crossover_step' in b for b in crossed)
    assert len({(b['treatment_id'], b['block_index']) for b in sequential}) == 16


def test_physical_blocks_preserve_source_outcomes_loss_and_unknown_health():
    rows = data.load_all21_block_observations()['crossed']
    for row in rows:
        payload = receipt(int(row['round_id'][1:]))
        source = next(x for x in payload['iterations'] if x['commit'] == row['treatment_id'])
        raw = next(x for x in source['repetition_blocks'] if x['block_index'] == row['block_index'])
        assert row['observation']['goodput_rx_mbps'] == raw['total_goodput_mbps']
        assert row['rtts_ms'] == raw['rtts_ms']
        assert row['pings_rcvd'] == len(row['rtts_ms'])
        assert 'restoration_verified' not in row['observation']
        assert 'station_drops' not in row['observation']
    lossful = [r for r in rows if r['observation']['packet_loss_pct']]
    assert len(lossful) == 2
    assert all(r['observation']['packet_loss_pct'] == 10 for r in lossful)


def test_summary_disagreements_are_preserved_without_repair():
    records, _ = data.load_all21_measurements()
    new = [r for r in records if isinstance(r, data.ThreeTierMeasurement)]
    assert len(new) == 23 and all(not r.summary_consistency['consistent'] for r in new)
    r = next(r for r in new if r.iteration == 'r20_iter3_asym_paced_ack_150pps_both_vi_n40')
    assert r.goodput_mbps == 95.75
    assert r.dl_goodput_mbps + r.ul_goodput_mbps == 94.3
    assert r.summary_consistency['block_mean_total_mbps'] == 94.875
    assert 'reported_summary_disagrees_with_repetition_blocks' in r.flags
    assert r.mac_retry_rate is None and r.mac_tx_packets == 0


def test_ack_unknown_unpaced_and_disabled_remain_distinct():
    rows, _ = data.load_all21_measurements()
    r16 = next(r for r in rows if r.round_id == 'R16')
    r19 = next(r for r in rows if r.iteration == 'r19_iter3_asym_3tier_both_ack_vi_n40')
    r20 = next(r for r in rows if r.iteration == 'r20_iter2_asym_paced_ack_400pps_ap_vi_n40')
    r21 = next(r for r in rows if r.iteration == 'r21_iter2_asym_50pps_both_vi300_n40')
    assert r16.ap_ack_pps is None and r16.ap_tcp_ack_vi is None
    assert r19.ap_tcp_ack_vi is True and r19.ap_ack_pps is None
    assert (r20.ap_ack_pps, r20.ap_tcp_ack_vi, r20.cpe_ack_pps, r20.cpe_tcp_ack_vi) == (400, True, 0, False)
    assert (r21.ap_ack_pps, r21.cpe_ack_pps, r21.ap_ack_burst, r21.cpe_ack_burst) == (50, 50, 3, 3)
    assert replace(r21, ap_ack_burst=4).policy_key != r21.policy_key
    assert replace(r21, ap_ack_pps=80).policy_key != r21.policy_key


def test_cpu_raw_samples_and_cipher_are_not_crossed_trials():
    rows, _ = data.load_all21_measurements()
    crypto = [r for r in rows if r.round_id == 'R17']
    assert [r.encryption_mode for r in crypto] == ['psk2', 'psk2', 'psk2', 'none']
    assert all(r.block_design_kind == 'SEQUENTIAL_REPETITIONS_NO_CROSSOVER_STEP' for r in crypto)
    for r in crypto:
        assert len(r.cpu_telemetry['repetitions']) == 4
        assert 'ap_cpu_softirq_pct' in r.cpu_telemetry['repetitions'][0]
        assert all('crossover_step' not in b for b in r.repetition_blocks)
    assert crypto[-1].cpu_telemetry['reported_window_medians']['ap_cpu_busy_pct_median'] == 89.06


def test_programmed_3000m_and_fixed_threshold_remain_explicit():
    rows, _ = data.load_all21_measurements()
    r18 = [r for r in rows if r.round_id == 'R18']
    assert all(r.distance_meters == 3000 and r.ap_policy.distance_meters == 3000 for r in r18)
    a, b = r18[1:3]
    assert (a.ap_policy.aql_by_ac[2], b.ap_policy.aql_by_ac[2]) == ((1800, 3600), (1900, 3800))
    assert a.ap_policy.aql_threshold_us == b.ap_policy.aql_threshold_us == 7200


@pytest.mark.parametrize('field,value', [('ap_ack_pps', True), ('cpe_ack_pps', -1),
    ('ap_ack_burst', 2.5), ('cpe_ack_burst', 1_000_001), ('ap_tcp_ack_vi', 1), ('cpe_tcp_ack_vi', 'false')])
def test_invalid_ack_types_do_not_alias_valid_policies(field, value):
    row = next(r for r in data.load_all21_measurements()[0] if r.round_id == 'R21')
    with pytest.raises(ValueError):
        replace(row, **{field: value})


@pytest.mark.parametrize('mutation', ['bool_block', 'bool_step', 'duplicate_step', 'missing_step',
    'missing_id', 'received_count', 'negative_cpu', 'nonmonotone', 'block_direction_sum', 'duplicate_treatment'])
def test_malformed_physical_units_fail_closed(tmp_path, mutation):
    payload = receipt(17 if mutation == 'negative_cpu' else 16)
    arm = payload['iterations'][0]
    block = arm['repetition_blocks'][0]
    if mutation == 'bool_block': block['block_index'] = True
    elif mutation == 'bool_step': block['crossover_step'] = False
    elif mutation == 'duplicate_step': arm['repetition_blocks'][1] = deepcopy(block)
    elif mutation == 'missing_step': del block['crossover_step']
    elif mutation == 'missing_id': del block['block_index']
    elif mutation == 'received_count': block['pings_rcvd'] -= 1
    elif mutation == 'negative_cpu': block['ap_cpu_busy_pct'] = -1
    elif mutation == 'nonmonotone': block['p95_rtt_ms'] = block['p99_rtt_ms'] + 1
    elif mutation == 'block_direction_sum': block['dl_goodput_mbps'] += 1
    else: payload['iterations'][1]['commit'] = arm['commit']
    with pytest.raises(ValueError):
        data.load_all21_block_observations([write_receipt(tmp_path, payload)])


def test_sequential_repetition_does_not_gain_a_synthetic_step(tmp_path):
    payload = receipt(17)
    payload['iterations'][0]['repetition_blocks'][0]['crossover_step'] = 0
    with pytest.raises(ValueError, match='sequential'):
        data.load_all21_block_observations([write_receipt(tmp_path, payload)])


@pytest.mark.parametrize('mutation', ['raw_membership', 'ack_conflict', 'bool_ack', 'window_repetitions', 'loss', 'encryption_conflict'])
def test_invalid_window_evidence_is_not_silently_repaired(tmp_path, mutation):
    payload = receipt(20)
    arm = payload['iterations'][0]
    if mutation == 'raw_membership': arm['raw_rtts_ms'][0] += 1
    elif mutation == 'ack_conflict': arm['ap_ack_pps'] = 4
    elif mutation == 'bool_ack': arm['ap_ack_pps'] = True
    elif mutation == 'window_repetitions': arm['observation']['repetitions'] += 1
    elif mutation == 'loss': arm['observation']['packet_loss_pct'] = 50
    else: arm['candidate_knobs']['ap_state']['encryption_mode'] = 'none'
    with pytest.raises(ValueError):
        data.load_all21_measurements([write_receipt(tmp_path, payload)])


def test_only_frozen_or_prior_output_json_is_opened(monkeypatch):
    original = data.local_json
    accessed = []
    def guard(path):
        p = data.Path(path).resolve()
        assert p.is_relative_to(data.QRST_ARTIFACTS.resolve()) or p.is_relative_to(data.MNOP_ARTIFACTS.resolve())
        accessed.append(p)
        return original(path)
    monkeypatch.setattr(data, 'local_json', guard)
    assert len(data.load_all21_measurements()[0]) == 112
    assert all('r22' not in p.name.lower() for p in accessed)


def test_tampered_owned_snapshot_is_rejected(tmp_path, monkeypatch):
    inputs = tmp_path / 'inputs'
    inputs.mkdir()
    frozen = inputs / 'round.json'
    frozen.write_text(json.dumps(receipt(16)), encoding='utf-8')
    manifest = [{'path':str(frozen), 'bytes':frozen.stat().st_size, 'sha256':'0' * 64}]
    (tmp_path / 'inputs_manifest.json').write_text(json.dumps(manifest))
    monkeypatch.setattr(data, 'QRST_INPUTS', inputs)
    monkeypatch.setattr(data, 'QRST_ARTIFACTS', tmp_path)
    with pytest.raises(ValueError, match='checksum'):
        data.load_all21_block_observations([frozen])


def test_missing_historical_input_completes_unknown_check(tmp_path):
    rows, refs = data.load_all21_measurements([tmp_path / 'missing.json'])
    assert len(rows) == 89
    assert refs[-1]['status'] == 'UNKNOWN_LOCAL_ARTIFACT_ABSENT'
    assert refs[-1]['check_complete'] is True


@pytest.mark.parametrize('path', ['https://example.invalid/round.json', r'\\server\share\round.json', '//server/share/round.json'])
def test_remote_paths_are_rejected_before_any_filesystem_probe(monkeypatch, path):
    def forbidden_probe(*args):
        raise AssertionError('Remote path reached a filesystem probe')
    monkeypatch.setattr(data.Path, 'is_file', forbidden_probe)
    with pytest.raises(ValueError, match='offline local'):
        data.load_all21_block_observations([path])


def test_duplicate_round_and_bad_selectors_are_rejected():
    with pytest.raises(ValueError, match='Duplicate'):
        data.load_all21_measurements([data.R16_TO_R21_RECEIPTS[0]] * 2)
    with pytest.raises(ValueError):
        data.load_all21_measurements(include_auxiliary=1)
    with pytest.raises(ValueError):
        data.load_all21_block_observations([])


def test_normalized_output_keeps_counts_and_no_actuation():
    normalized = data.normalized_real_crossover_dataset()
    assert normalized['observed_record_count'] == 112
    assert normalized['primary_window_count'] == 110 and normalized['auxiliary_window_count'] == 2
    assert normalized['crossed_observation_count'] == 88
    assert normalized['matched_round_scoped_block_count'] == 24
    assert normalized['sequential_repetition_count'] == 16
    assert normalized['automatic_execution_allowed'] is False
    assert normalized['historical_checks'][0]['check_complete'] is True


def test_cli_writes_owned_output_and_keeps_inputs_protected(tmp_path, monkeypatch):
    # Build from actual snapshots before temporarily changing the output boundary.
    normalized = data.normalized_real_crossover_dataset()
    monkeypatch.setattr(data, 'normalized_real_crossover_dataset', lambda: normalized)
    monkeypatch.setattr(data, 'QRST_ARTIFACTS', tmp_path)
    monkeypatch.setattr(data, 'QRST_INPUTS', tmp_path / 'inputs')
    target = tmp_path / 'normalized.json'
    assert data.main(['--all-rounds21', '--output', str(target)]) == 0
    assert json.loads(target.read_text())['observed_record_count'] == 112
    with pytest.raises(ValueError, match='never frozen inputs'):
        data.main(['--all-rounds21', '--output', str(tmp_path / 'inputs' / 'forbidden.json')])
    assert not (tmp_path / 'inputs' / 'forbidden.json').exists()
