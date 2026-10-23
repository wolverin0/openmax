"""Disposable local publication fixtures. No device, network or private input."""
import importlib.util
import json
from pathlib import Path

import pytest


PATH = Path(__file__).resolve().parents[1] / 'tools/bench/preprod1_public_projection.py'
spec = importlib.util.spec_from_file_location('preprod1_projection_fixture', PATH)
projection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(projection)


def test_nested_secret_and_foreign_identifiers_are_withheld_without_rescuing_failure():
    poison = 'PRIVATE_SENTINEL_please_never_publish'
    unknown = 'aa:bb:cc:dd:ee:ff'
    ipv6 = 'fe80::1234:5678:9abc:def0'
    value = dict(status='INCOMPLETE_FOUR_CPE_PRESERVED', experiment='PREPROD1_FMX0017_ZERO_TOUCH_RECOVERY',
                 full_PREPROD1_PASS=False, diagnostic_only=True, exit_code=1,
                 forbidden_actions_executed=False, persistent_config_writes=False,
                 stdout=poison, stderr=ipv6, events=[dict(probe=unknown)],
                 neighbors={unknown: ipv6}, credentials=dict(password=poison),
                 arbitrary=dict(raw_frame='dd' * 128, secret=poison),
                 epoch_traffic={'0': {'WA': dict(transmitted=32, received=31, paired=31,
                     qualifying=False, p95_ms=4.5, failures=['INSUFFICIENT_REPLIES ' + poison],
                     artifact=dict(file=poison, bytes=123, sha256='a' * 64),
                     stdout=poison, arbitrary_key=unknown)}},
                 AP_restoration=dict(status='PASS_RAM_WINDOW_RESTORED_RADIO_OFF',
                     deltas_empty=True, guard_ended_verified=True, stdout=poison, config=ipv6))
    raw = json.dumps(value).encode()
    result = projection.projection(raw, 'artifacts/canary_panel1_guarida/preprod1_fixture/receipt.json', projection.sha(raw))
    public = json.dumps(result)
    for secret in (poison, unknown, ipv6, 'dd' * 128):
        assert secret not in public
    assert result['raw_withheld'] and not result['byte_identical_to_raw']
    assert not result['runtime_precondition_replacement']
    assert result['status'] == value['status'] and result['full_PREPROD1_PASS'] is False
    traffic = result['epoch_traffic']['0']['WA']
    assert (traffic['transmitted'], traffic['received'], traffic['paired'], traffic['qualifying']) == (32, 31, 31, False)
    assert traffic['failure_categories'] == ['INSUFFICIENT_REPLIES']
    assert traffic['artifact'] == dict(bytes=123, sha256='a' * 64)
    assert result['AP_restoration']['guard_ended_verified'] is True


def test_actions_only_known_events_and_labels_no_raw_line_or_probe():
    text = '\n'.join([
        '12.5 FOUR_ADMITTED unknown=PRIVATE_SENTINEL',
        '13.2 DROP_REQUEST n=2 target=b4:fb:e4:5c:d5:d2 reason=3 secret=PRIVATE_SENTINEL',
        '14.2 RECOVERED n=2 target=aa:bb:cc:dd:ee:ff',
        '15.2 PROBE target=aa:bb:cc:dd:ee:ff',
        '16.2 STABLE_OK epoch=1 stdout=fe80::1234',
        '17.2 DROP_OBSERVED n=bad target=b4:fb:e4:5c:d5:d2'])
    result = projection.actions(text)
    assert result == [dict(timestamp=12.5, event='FOUR_ADMITTED'),
                      dict(timestamp=13.2, event='DROP_REQUEST', drop_n=2, target_label='XC'),
                      dict(timestamp=16.2, event='STABLE_OK', epoch=1)]
    assert 'PRIVATE_SENTINEL' not in json.dumps(result) and 'aa:bb' not in json.dumps(result)


def test_unknown_tokens_and_json_do_not_export_arbitrary_values():
    raw = json.dumps(dict(experiment='PREPROD1_FMX0017_ZERO_TOUCH_RECOVERY',
                          status='FAIL_PRIVATE_SENTINEL aa:bb:cc:dd:ee:ff',
                          gate='PRIVATE_SENTINEL', type='fe80::1234',
                          unknown_key='secret', started_utc='2026-10-23T06:00:00Z secret')).encode()
    result = projection.projection(raw, 'fixture.json', projection.sha(raw))
    assert result['status'] == 'UNRECOGNIZED_STATUS_WITHHELD'
    assert result['gate'] == result['type'] == 'UNRECOGNIZED_GATE_WITHHELD'
    assert 'PRIVATE_SENTINEL' not in json.dumps(result) and 'started_utc' not in result
    raw = b'{"experiment":"PREPROD1_FMX0017_ZERO_TOUCH_RECOVERY","status":"PASS PRIVATE_SENTINEL"}'
    assert projection.projection(raw, 'fixture.json', projection.sha(raw))['status'] == 'UNRECOGNIZED_STATUS_WITHHELD'
    raw = b'{"full_PREPROD1_PASS":true,"arbitrary":{"secret":"PRIVATE_SENTINEL"}}'
    result = projection.projection(raw, 'fixture.json', projection.sha(raw))
    assert result['status'] == 'UNKNOWN_JSON_CONTENT_WITHHELD'
    assert 'full_PREPROD1_PASS' not in result
    assert 'PRIVATE_SENTINEL' not in json.dumps(result)


def test_non_json_only_provenance_no_content():
    raw = b'PRIVATE_SENTINEL aa:bb:cc:dd:ee:ff fe80::1234 raw_frame=010203'
    result = projection.projection(raw, 'fixture.stdout', projection.sha(raw))
    assert result['raw_bytes'] == len(raw) and result['raw_sha256'] == projection.sha(raw)
    assert 'PRIVATE_SENTINEL' not in json.dumps(result)
    assert result['content_policy'] == 'PROVENANCE_ONLY_NON_JSON_CONTENT_WITHHELD'


def test_pinned_hash_mismatch_skips_and_originals_remain_exact(tmp_path):
    base = tmp_path / Path(projection.BASE)
    raw_path = base / 'preprod1_fixture/receipt.json'
    raw_path.parent.mkdir(parents=True)
    original = b'{"status":"FAIL","full_PREPROD1_PASS":false}'
    raw_path.write_bytes(original)
    rel = raw_path.relative_to(tmp_path).as_posix()
    inventory = dict(foreign_probe_raw_projection_required=[dict(file=rel, sha256='0' * 64)],
                     non_JSON_raw_projection_required=[])
    data = json.dumps(inventory).encode()
    pin = tmp_path / 'inventory.json'; pin.write_bytes(data)
    output = base / 'preprod1_public_evidence_fixture'
    result = projection.generate(tmp_path, pin, output, projection.sha(data))
    assert result['projected_count'] == 0 and result['unresolved_count'] == 1
    assert result['unresolved'][0]['reason'] == 'RAW_SHA_MISMATCH'
    assert raw_path.read_bytes() == original
    with pytest.raises(FileExistsError):
        projection.generate(tmp_path, pin, output, projection.sha(data))


def test_mutable_and_active_raw_paths_excluded():
    root = str(projection.BASE)
    inventory = dict(foreign_probe_raw_projection_required=[dict(file=root + '/' + x) for x in [
        'preprod1_bench_result_20261022.json', 'preprod1_20261022_run5am/receipt.json',
        'preprod1_20261022_run5an/receipt.json', 'preprod1_20261022_run5al/receipt.json']],
        non_JSON_raw_projection_required=[])
    assert [row['file'] for row in projection.selected(inventory)] == [root + '/preprod1_20261022_run5al/receipt.json']


def test_real_trial_success_status_is_retained_and_cleanup_failure_is_not_hidden():
    import ast
    source = PATH.parents[2] / 'artifacts/canary_panel1_guarida/preprod1_trial_20261022.py'
    statuses = {n.value for n in ast.walk(ast.parse(source.read_text(encoding='utf8')))
                if isinstance(n, ast.Constant) and isinstance(n.value, str)
                and n.value.startswith('PASS_PREPROD1_AP_ONLY_')}
    assert len(statuses) == 1
    status = statuses.pop()
    value = dict(experiment='PREPROD1_FMX0017_ZERO_TOUCH_RECOVERY', status=status,
                 full_PREPROD1_PASS=True, failures=[], cleanup_errors=['PRIVATE_SENTINEL'],
                 rocket_restoration=dict(status='PASS_EXACT_HASHES_RULES_BRIDGE_ORDERED_IPv4_ROUTES_GUARD_ENDED',
                                         stdout='PRIVATE_SENTINEL'))
    raw = json.dumps(value).encode()
    result = projection.projection(raw, 'fixture.json', projection.sha(raw))
    assert result['status'] == status and result['full_PREPROD1_PASS'] is True
    assert result['cleanup_error_count'] == 1 and result['failure_count'] == 0
    assert result['rocket_restoration']['status'] == value['rocket_restoration']['status']
    assert 'PRIVATE_SENTINEL' not in json.dumps(result)
