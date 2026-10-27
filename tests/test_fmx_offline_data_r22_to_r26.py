"""Lower-MAC declarations and physical units from owned R22-R26 snapshots."""
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json

import pytest

from orchestration.autoresearch import fmx_offline_data as data


def receipt(number):
    return json.loads(data.R22_TO_R26_RECEIPTS[number - 22].read_text(encoding='utf-8'))


def save(tmp_path, payload, name='fixture.json'):
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding='utf-8')
    return path


def json_value(value):
    return json.loads(json.dumps(value, allow_nan=False))


def test_131_records_preserve_all112_prior_records_and_keys():
    rows, refs = data.load_all26_measurements()
    prior = json.loads(data.R21_NORMALIZED_OUTPUT.read_text())
    unchanged = [{**asdict(row), 'policy_key': row.policy_key} for row in rows if int(row.round_id[1:]) <= 21]
    assert json_value(unchanged) == prior['records']
    assert len(rows) == 131 and len(refs) == 26
    assert [sum(r.round_id == f'R{i}' for r in rows) for i in range(22, 27)] == [4, 4, 4, 3, 4]
    assert len(data.load_all26_measurements(include_auxiliary=False)[0]) == 129


def test_all_15_inputs_remain_byte_identical():
    manifest = json.loads((data.UVWX_ARTIFACTS / 'inputs_manifest.json').read_text())
    assert len(manifest) == 15
    for row in manifest:
        raw = (data.ROOT / row['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['sha256'] and len(raw) == row['bytes']


def test_188_crossed_rows_are52_matched_units_and16_unpaired_rows():
    new = data.load_all26_block_observations()
    old = json.loads(data.R21_BLOCK_OUTPUT.read_text())
    assert len(new['crossed']) == 188 and len(new['sequential']) == 16
    assert len({(r['round_id'], r['block_index']) for r in new['crossed']}) == 52
    assert [r for r in new['crossed'] if int(r['round_id'][1:]) <= 21] == old['crossed']
    assert new['sequential'] == old['sequential']
    assert all('crossover_step' not in r for r in new['sequential'])
    assert [sum(r['round_id'] == f'R{i}' for r in new['crossed']) for i in range(22, 27)] == [16, 16, 16, 36, 16]


def test_r25_attempted_and_received_counts_are_not_conflated():
    rows = data.load_all26_block_observations()['crossed']
    r25 = [r for r in rows if r['round_id'] == 'R25']
    arms = sorted({r['treatment_id'] for r in r25})
    assert len(r25) == 36 and len({r['block_index'] for r in r25}) == 12
    assert [sum(r['pings_sent'] for r in r25 if r['treatment_id'] == arm) for arm in arms] == [120, 120, 120]
    assert [sum(r['pings_rcvd'] for r in r25 if r['treatment_id'] == arm) for arm in arms] == [117, 120, 120]
    assert all('restoration_verified' not in r['observation'] for r in r25)


def test_shared_hooks_are_typed_and_part_of_each_endpoint_identity():
    rows, _ = data.load_all26_measurements()
    r22 = next(r for r in rows if r.iteration == 'r22_iter2_asym_retry5_3_ftx0_n40')
    r23 = next(r for r in rows if r.iteration == 'r23_iter2_asym_ani0_af3_fql8192_n40')
    r26 = next(r for r in rows if r.iteration == 'r26_iter3_r23_winner_ftx1_retry63_n40')
    assert (r22.short_retry_limit, r22.long_retry_limit, r22.force_tx_status) == (5, 3, 0)
    assert r22.ani_enable is None and r22.fq_limit is None
    assert r23.ani_enable == 0 and type(r23.ani_enable) is int
    assert r23.short_retry_limit is None
    assert (r26.airtime_flags, r26.fq_limit, r26.force_tx_status, r26.short_retry_limit, r26.long_retry_limit) == (1, 2048, 1, 6, 3)
    for endpoint in json.loads(r26.policy_key):
        assert endpoint['airtime_flags'] == 1 and endpoint['fq_limit'] == 2048
        assert endpoint['force_tx_status'] == 1 and 'ack_burst' in endpoint
    assert replace(r26, force_tx_status=0).policy_key != r26.policy_key


def test_all19_summary_conflicts_survive_exact_directional_sums():
    rows, _ = data.load_all26_measurements()
    new = [r for r in rows if isinstance(r, data.LowerMACMeasurement)]
    assert len(new) == 19
    assert all(r.summary_consistency['consistent'] is False for r in new)
    assert all('reported_summary_disagrees_with_repetition_blocks' in r.flags for r in new)
    assert all(r.mac_tx_packets == 0 and r.mac_retry_rate is None for r in new)
    r24 = next(r for r in new if r.round_id == 'R24')
    assert abs(r24.goodput_mbps - r24.dl_goodput_mbps - r24.ul_goodput_mbps) < 1e-10
    assert r24.goodput_mbps != r24.summary_consistency['block_mean_total_mbps']


def test_sorted_rtt_pools_preserve_blocks_and_do_not_invent_chronology():
    rows, _ = data.load_all26_measurements()
    for row in rows:
        if not isinstance(row, data.LowerMACMeasurement):
            continue
        flat = [v for block in row.repetition_blocks for v in block['rtts_ms']]
        if row.round_id in ('R24', 'R25', 'R26'):
            assert list(row.rtts_ms) == sorted(flat)
            assert list(row.rtts_ms) != flat
            assert row.rtt_pool_order == 'SORTED_POOL_BLOCK_ARRAYS_RETAINED'
            assert 'pooled_RTTs_sorted_chronology_lost_block_arrays_preserved' in row.flags
        else:
            assert list(row.rtts_ms) == flat
            assert row.rtt_pool_order == 'CONCATENATED_BLOCK_ORDER'


@pytest.mark.parametrize('field,value', [('short_retry_limit', True), ('long_retry_limit', 256),
    ('force_tx_status', False), ('force_tx_status', 2), ('ani_enable', -1), ('ani_enable', '0'),
    ('airtime_flags', 4), ('airtime_flags', 1.0), ('fq_limit', 0), ('fq_limit', 2**32)])
def test_invalid_hook_representations_fail_closed(field, value):
    row = next(r for r in data.load_all26_measurements()[0] if r.round_id == 'R26')
    with pytest.raises(ValueError):
        replace(row, **{field: value})


@pytest.mark.parametrize('field', list(data.LOWER_MAC_BOUNDS))
def test_conflicting_shared_declarations_are_not_silently_overwritten(tmp_path, field):
    number = 23 if field == 'ani_enable' else 26
    payload = receipt(number)
    item = payload['iterations'][0]
    value = item[field]
    item['candidate_knobs'][field] = 1 - value if field in ('force_tx_status', 'ani_enable') else value + 1
    with pytest.raises(ValueError):
        data.load_all26_measurements([save(tmp_path, payload)])


@pytest.mark.parametrize('mutation', ['duplicate', 'bool_step', 'missing_step', 'received_count', 'future_round'])
def test_invalid_new_block_units_are_rejected(tmp_path, mutation):
    payload = receipt(25)
    block = payload['iterations'][0]['repetition_blocks'][0]
    if mutation == 'duplicate': payload['iterations'][0]['repetition_blocks'][1] = deepcopy(block)
    elif mutation == 'bool_step': block['crossover_step'] = True
    elif mutation == 'missing_step': del block['crossover_step']
    elif mutation == 'received_count': block['pings_rcvd'] -= 1
    else: payload['experiment_id'] = payload['experiment_id'].replace('-025-', '-027-')
    with pytest.raises(ValueError):
        data.load_all26_block_observations([save(tmp_path, payload)])


def test_sorted_pool_with_altered_member_is_not_accepted(tmp_path):
    payload = receipt(24)
    payload['iterations'][0]['raw_rtts_ms'][0] += .001
    with pytest.raises(ValueError, match='membership'):
        data.load_all26_measurements([save(tmp_path, payload)])


def test_old_physical_window_contract_remains_strict_on_sorted_pools():
    payload = receipt(24)
    item = payload['iterations'][0]
    blocks = [b for b in data._physical_block_rows(payload, max_round=26) if b['treatment_id'] == item['commit']]
    with pytest.raises(ValueError, match='membership'):
        data._physical_window(item, 24, 0, blocks)


def test_four_lossful_new_windows_are_kept():
    rows, _ = data.load_all26_measurements()
    losses = [(r.round_id, r.packet_loss_pct) for r in rows if isinstance(r, data.LowerMACMeasurement) and r.packet_loss_pct]
    assert losses == [('R22', 7.5), ('R23', 2.5), ('R25', 2.5), ('R26', 5.0)]


def test_missing_optional_local_receipt_completes_unknown(tmp_path):
    missing = tmp_path / 'absent.json'
    rows, refs = data.load_all26_measurements([missing])
    blocks = data.load_all26_block_observations([missing])
    assert len(rows) == 112 and len(blocks['crossed']) == 88
    assert refs[-1]['status'] == blocks['source_refs'][-1]['status'] == 'UNKNOWN_LOCAL_ARTIFACT_ABSENT'
    assert refs[-1]['check_complete'] is True


@pytest.mark.parametrize('path', ['https://example.invalid/round.json', r'\\server\share\receipt.json', '//server/share/receipt.json'])
def test_remote_input_is_refused_before_probe(monkeypatch, path):
    def forbidden(*args):
        raise AssertionError('Remote path reached filesystem probe')
    monkeypatch.setattr(data.Path, 'is_file', forbidden)
    with pytest.raises(ValueError, match='offline local'):
        data._verified_uvwx_json(path)


def test_tampered_owned_snapshot_is_refused(tmp_path, monkeypatch):
    inputs = tmp_path / 'inputs'
    inputs.mkdir()
    frozen = save(inputs, receipt(22))
    save(tmp_path, [{'path':str(frozen), 'sha256':'0' * 64, 'bytes':frozen.stat().st_size}], 'inputs_manifest.json')
    monkeypatch.setattr(data, 'UVWX_INPUTS', inputs)
    monkeypatch.setattr(data, 'UVWX_ARTIFACTS', tmp_path)
    with pytest.raises(ValueError, match='checksum'):
        data._verified_uvwx_json(frozen)


def test_prior_crossover_and_sequential_identity_cannot_be_reinterpreted(tmp_path):
    base = json.loads(data.R21_BLOCK_OUTPUT.read_text())
    base['sequential'][0]['crossover_step'] = 0
    with pytest.raises(ValueError, match='sequential'):
        data.load_all26_block_observations(base_dataset_path=save(tmp_path, base))


def test_duplicate_receipt_and_invalid_selectors_fail():
    with pytest.raises(ValueError, match='Unique'):
        data.load_all26_measurements([data.R22_TO_R26_RECEIPTS[0]] * 2)
    with pytest.raises(ValueError):
        data.load_all26_measurements(include_auxiliary=1)
    with pytest.raises(ValueError):
        data.load_all26_block_observations([])


def test_normalized_metadata_retains_units_and_no_actuation():
    normalized = data.normalized_lower_mac_dataset()
    assert (normalized['observed_record_count'], normalized['primary_window_count'], normalized['auxiliary_window_count']) == (131, 129, 2)
    assert normalized['crossed_observation_count'] == 188
    assert normalized['matched_round_scoped_block_count'] == 52
    assert normalized['sequential_repetition_count'] == 16
    assert normalized['automatic_execution_allowed'] is False
    assert normalized['physical_acceptance_claim'] is False


def test_cli_owned_output_and_input_protection(tmp_path, monkeypatch):
    normalized = data.normalized_lower_mac_dataset()
    monkeypatch.setattr(data, 'normalized_lower_mac_dataset', lambda: normalized)
    monkeypatch.setattr(data, 'UVWX_ARTIFACTS', tmp_path)
    monkeypatch.setattr(data, 'UVWX_INPUTS', tmp_path / 'inputs')
    target = tmp_path / 'normalized.json'
    assert data.main(['--all-rounds26', '--output', str(target)]) == 0
    assert json.loads(target.read_text())['observed_record_count'] == 131
    with pytest.raises(ValueError, match='never frozen inputs'):
        data.main(['--all-rounds26', '--output', str(tmp_path / 'inputs' / 'forbidden.json')])
