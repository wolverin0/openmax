"""PRE-PROD2 uses only local files and recording stubs, never devices."""
import json
import socket
import struct
import zlib
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from safety.preprod import guarida as p


def no_network(*args, **kwargs):
    raise AssertionError('NETWORK_FORBIDDEN_IN_PREPROD2')


def test_default_plan_and_execute_refusal_create_nothing(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(socket, 'create_connection', no_network)
    out = tmp_path / 'unused'
    assert p.main(['--output', str(out)]) == 0
    assert json.loads(capsys.readouterr().out)['status'] == 'PLAN_ONLY'
    with pytest.raises(SystemExit) as error:
        p.main(['--execute', '--prepare-local', '--output', str(out)])
    assert error.value.code == 2 and not out.exists()


def test_pinned_files_refuse_tamper_size_and_escape(tmp_path):
    (tmp_path / 'input').write_bytes(b'fixture')
    assert p.read_bound(tmp_path, 'input', p.sha(b'fixture'), 7) == b'fixture'
    for digest, size in [('0' * 64, 7), (p.sha(b'fixture'), 8)]:
        with pytest.raises(ValueError): p.read_bound(tmp_path, 'input', digest, size)
    with pytest.raises(ValueError): p.read_bound(tmp_path / 'child', '../input', p.sha(b'fixture'))


def image_fixture():
    data = bytearray(b'\xff' * p.IMAGE_BYTES)
    payload = b'LOCAL FIXTURE NOT FIRMWARE'
    fields = (0x27051956, 0, 0, len(payload), 0x80060000, 0x80060000,
              zlib.crc32(payload), 5, 5, 2, 3, b'MIPS fixture')
    header = bytearray(struct.pack('>7I4B32s', *fields))
    header[4:8] = struct.pack('>I', zlib.crc32(header))
    data[:64] = header; data[64:64 + len(payload)] = payload
    data[0x290000:0x290004] = b'hsqs'
    data[0x6b0000:0x6b0004] = bytes.fromhex('deadc0de')
    return data


def test_candidate_crc_geometry_and_protected_exclusion():
    data = image_fixture()
    result = p.candidate_format(data)
    assert result['install_blocks'] == 108
    assert 0x50000 + p.IMAGE_BYTES <= 0xfb0000
    for offset in (4, 64, 0x290000, 0x6b0000):
        changed = bytearray(data); changed[offset] ^= 1
        with pytest.raises(ValueError): p.candidate_format(changed)
    with pytest.raises(ValueError): p.candidate_format(data[:-1])


def test_existing_rollback_failure_paths_with_recording_stubs_only(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, 'create_connection', no_network)
    golden = tmp_path / 'not-firmware'; golden.write_bytes(b'fixture image')
    result = p.rollback_dry_run(golden, p.sha(golden.read_bytes()))
    assert result['status'] == 'PASS_RECORDING_STUB_FAILURE_PATHS_ONLY'
    assert result['physical_recovery_qualified'] is False
    cases = {x['case']: x for x in result['scenarios']}
    assert cases['bad_image']['actions'] == []
    assert cases['transfer_timeout']['actions'] == ['SIMULATED_SOFT_TRANSFER']
    assert cases['transfer_timeout']['recovery_uncertain']
    assert cases['postboot_failure']['recovery_uncertain']
    assert cases['no_write_then_tftp']['actions'] == [
        'SIMULATED_SOFT_TRANSFER', 'SIMULATED_POWER_RESET',
        'SIMULATED_TFTP_TRANSFER', 'SIMULATED_POSTBOOT_VERIFICATION']


def test_bundle_holds_unselected_rejected_candidate_and_never_overwrites(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, 'create_connection', no_network)
    package = b'fixture return bytes'
    monkeypatch.setattr(p, 'PACKAGE_SHA', p.sha(package))
    monkeypatch.setattr(p, 'inventory', lambda root: dict(target={'label': 'fixture'},
        historical_candidate={'status': 'DRAFT_REJECTED_NOT_QUALIFIED'},
        candidate=b'fixture draft bytes', package=package))
    out = tmp_path / 'bundle'
    result = p.prepare(out, tmp_path)
    assert result['status'] == 'HOLD' and result['selected_deployment_candidate'] is None
    assert result['production_execution_enabled'] is False and result['publish_bundle'] is False
    assert result['historical_candidate']['status'] == 'DRAFT_REJECTED_NOT_QUALIFIED'
    assert 'bootloader' in result['prohibited_writes'] and 'calibration' in result['prohibited_writes']
    assert (out / 'own-stock.return.bin.gz').read_bytes() == package
    with pytest.raises(ValueError): p.prepare(out, tmp_path)


def test_invalid_input_creates_no_partial_bundle(tmp_path, monkeypatch):
    def rejected(root): raise ValueError('BAD_LOCAL_BACKUP')
    monkeypatch.setattr(p, 'inventory', rejected)
    out = tmp_path / 'bundle'
    with pytest.raises(ValueError): p.prepare(out, tmp_path)
    assert not out.exists()


# These start the SAME watchdog CLI as the packaged host process. Their only
# inputs/actions are disposable local files; no target driver is injectable.
def watchdog_fixture(tmp_path, **extra):
    golden = tmp_path / 'own-stock.return.bin.gz'
    golden.write_bytes(b'LOCAL RECORDING FIXTURE NOT FIRMWARE')
    state = tmp_path / 'watchdog'; state.mkdir()
    cfg = dict(execution_driver='recording_stub', attempt_id='fixture-1', nonce='a' * 64,
               golden_sha256=hashlib.sha256(golden.read_bytes()).hexdigest(),
               health_timeout_seconds=.6, maximum_seconds=3, **extra)
    contract = state / 'contract.json'; contract.write_text(json.dumps(cfg))
    return state, cfg, contract


def start_watchdog(contract):
    return subprocess.Popen([sys.executable, '-B', '-m', 'safety.preprod.guarida_watchdog',
                             '--run-recording', '--contract', str(contract)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def wait_owner(proc, state):
    end = time.monotonic() + 4
    while not (state / 'watchdog.owner.json').exists():
        assert proc.poll() is None
        assert time.monotonic() < end
        time.sleep(.01)
    # Owner is written immediately before establishing the monotonic epoch.
    time.sleep(.02)


def publish_health(state, cfg, healthy=True, complete=False, **extra):
    data = dict(attempt_id=cfg['attempt_id'], nonce=cfg['nonce'],
                observed_host_monotonic=time.monotonic(), healthy=healthy, complete=complete)
    data.update(extra)
    staged = state / 'new-health.json'; staged.write_text(json.dumps(data))
    os.replace(staged, state / 'health.json')


def finish_watchdog(proc):
    try:
        stdout, stderr = proc.communicate(timeout=6)
    except BaseException:
        proc.kill(); proc.communicate(); raise
    assert 'Traceback' not in stderr
    return proc.returncode, json.loads(stdout.strip().splitlines()[-1])


def test_actual_watchdog_health_failure_triggers_once_and_restart_refuses(tmp_path):
    state, cfg, contract = watchdog_fixture(tmp_path)
    proc = start_watchdog(contract); wait_owner(proc, state)
    publish_health(state, cfg, healthy=False)
    code, result = finish_watchdog(proc)
    assert code == 0 and result['reason'] == 'health_failure'
    assert result['layer'] == 'external_controller_host_process'
    assert result['autonomous_across_host_or_AP_power_loss'] is False
    actions = (state / 'recording-actions.jsonl').read_bytes()
    assert actions.count(b'SIMULATED_ROLLBACK_TRANSFER') == 1
    assert (state / 'rollback.intent.json').is_file()
    code, replay = finish_watchdog(start_watchdog(contract))
    assert code == 2 and replay['status'] == 'HOLD_PREEXISTING_OWNER_OR_INTENT'
    assert (state / 'recording-actions.jsonl').read_bytes() == actions


def test_actual_watchdog_no_report_times_out(tmp_path):
    state, cfg, contract = watchdog_fixture(tmp_path)
    code, result = finish_watchdog(start_watchdog(contract))
    assert code == 0 and result['reason'] == 'no_health_timeout'
    assert result['rollback_triggered'] and result['elapsed_seconds'] < 4


def test_actual_watchdog_healthy_completion_never_rolls_back(tmp_path):
    state, cfg, contract = watchdog_fixture(tmp_path)
    proc = start_watchdog(contract); wait_owner(proc, state)
    publish_health(state, cfg, complete=True)
    code, result = finish_watchdog(proc)
    assert code == 0 and result['status'] == 'PASS_WATCHDOG_HEALTH_ACCEPTED_NO_ROLLBACK'
    assert not (state / 'rollback.intent.json').exists()
    assert not (state / 'recording-actions.jsonl').exists()


def test_actual_watchdog_health_writer_process_death_triggers_stale_timeout(tmp_path):
    state, cfg, contract = watchdog_fixture(tmp_path)
    proc = start_watchdog(contract); wait_owner(proc, state)
    producer = subprocess.Popen([sys.executable, '-B', '-c',
        'import json,os,sys,time; p=sys.argv[1]; c=json.load(open(sys.argv[2])); '
        'd={k:c[k] for k in ("nonce","attempt_id")}; '
        'd.update(observed_host_monotonic=time.monotonic(),healthy=True,complete=False); '
        'open(p+".new","w").write(json.dumps(d)); os.replace(p+".new",p); '
        'print("READY",flush=True); time.sleep(20)', str(state / 'health.json'), str(contract)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        assert producer.stdout.readline().strip() == 'READY'
        time.sleep(.15)
        producer.kill(); producer.communicate(timeout=2)
        code, result = finish_watchdog(proc)
        assert code == 0 and result['reason'] == 'health_timeout_or_writer_death'
        assert result['actions'].count('SIMULATED_ROLLBACK_TRANSFER') == 1
    finally:
        if producer.poll() is None: producer.kill(); producer.communicate()
        if proc.poll() is None: proc.kill(); proc.communicate()


def test_actual_watchdog_killed_process_does_not_claim_autonomous_recovery(tmp_path):
    state, cfg, contract = watchdog_fixture(tmp_path)
    proc = start_watchdog(contract); wait_owner(proc, state)
    proc.kill(); proc.communicate(timeout=2)
    assert not (state / 'rollback.intent.json').exists()
    code, result = finish_watchdog(start_watchdog(contract))
    assert code == 2 and result['status'] == 'HOLD_PREEXISTING_OWNER_OR_INTENT'
    assert not (state / 'recording-actions.jsonl').exists()


@pytest.mark.parametrize('fixture,expected', [
    ('timeout', ['SIMULATED_ROLLBACK_TRANSFER']),
    ('verification_failure', ['SIMULATED_ROLLBACK_TRANSFER', 'SIMULATED_POSTBOOT_VERIFICATION'])])
def test_actual_watchdog_uncertain_restore_latches_without_escalation(tmp_path, fixture, expected):
    state, cfg, contract = watchdog_fixture(tmp_path, rollback_fixture=fixture)
    proc = start_watchdog(contract); wait_owner(proc, state)
    publish_health(state, cfg, healthy=False)
    code, result = finish_watchdog(proc)
    assert code == 2 and result['status'] == 'HOLD_ROLLBACK_UNCERTAIN'
    assert result['actions'] == expected
    assert finish_watchdog(start_watchdog(contract))[0] == 2


@pytest.mark.parametrize('kind', ['foreign_owner', 'foreign_health', 'bad_golden', 'real_driver'])
def test_actual_watchdog_refuses_unsafe_binding_before_actions(tmp_path, kind):
    state, cfg, contract = watchdog_fixture(tmp_path)
    if kind == 'foreign_owner':
        (state / 'watchdog.owner.json').write_text(json.dumps(dict(attempt_id='foreign', nonce='b' * 64)))
    if kind == 'bad_golden': (tmp_path / 'own-stock.return.bin.gz').write_bytes(b'changed')
    if kind == 'real_driver':
        cfg['execution_driver'] = 'production'; contract.write_text(json.dumps(cfg))
    proc = start_watchdog(contract)
    if kind == 'foreign_health':
        wait_owner(proc, state); publish_health(state, cfg, nonce='b' * 64, complete=True)
    code, result = finish_watchdog(proc)
    assert code == 2 and result['status'].startswith('HOLD_')
    assert not (state / 'recording-actions.jsonl').exists()
    assert not (state / 'rollback.intent.json').exists()


def test_watchdog_default_plan_creates_nothing(tmp_path):
    proc = subprocess.run([sys.executable, '-B', '-m', 'safety.preprod.guarida_watchdog'],
                          cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=3)
    assert proc.returncode == 0
    assert json.loads(proc.stdout)['status'] == 'PLAN_ONLY'


def test_watchdog_complete_report_after_total_deadline_never_accepts(tmp_path, monkeypatch):
    from safety.preprod import guarida_watchdog as w
    state, cfg, contract = watchdog_fixture(tmp_path)
    (state / 'health.json').write_text(json.dumps(dict(attempt_id=cfg['attempt_id'], nonce=cfg['nonce'],
        observed_host_monotonic=2, healthy=True, complete=True)))
    ticks = iter([1, 1.1, 5])
    monkeypatch.setattr(w.time, 'monotonic', lambda: next(ticks, 5))
    result, code = w.run_recording(contract)
    assert code == 0 and result['reason'] == 'watchdog_deadline'
    assert result['rollback_triggered']


def test_actual_watchdog_concurrent_second_process_never_dispatches_twice(tmp_path):
    state, cfg, contract = watchdog_fixture(tmp_path)
    first = start_watchdog(contract); wait_owner(first, state)
    code, second = finish_watchdog(start_watchdog(contract))
    assert code == 2 and second['status'] == 'HOLD_PREEXISTING_OWNER_OR_INTENT'
    publish_health(state, cfg, healthy=False)
    assert finish_watchdog(first)[0] == 0
    assert (state / 'recording-actions.jsonl').read_bytes().count(b'SIMULATED_ROLLBACK_TRANSFER') == 1


def test_snapshot_provenance_and_no_original_dirty_api_dependency(tmp_path):
    import inspect
    from safety.preprod import guarida_watchdog as w, rollback_snapshot as snapshot
    raw = Path(snapshot.__file__).read_bytes()
    assert hashlib.sha256(raw.split(b'# BEGIN ORIGINAL SOURCE\n')[1]).hexdigest() == (
        '85e412bde00b1e9003bf191a95fe2ebbc868adf4c4fd431ea3428fa8fe5f00c7')
    root = Path(snapshot.__file__).resolve().parents[2]
    import orchestration.power.smart_power as power
    dependency = Path(power.__file__).read_bytes()
    assert hashlib.sha256(dependency).hexdigest() == '7cf7146c460cc0353758290d3191d6742de49dd2dbf714be0e2629738f249083'
    for relative, data in [('safety/preprod/guarida_watchdog.py', Path(w.__file__).read_bytes()),
        ('safety/preprod/rollback_snapshot.py', raw), ('orchestration/power/smart_power.py', dependency),
        ('orchestration/rollback/workflow.py', b'raise AssertionError("DIRTY_API_IMPORT_FORBIDDEN")\n')]:
        path = tmp_path / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    environment = dict(os.environ); environment.pop('PYTHONPATH', None)
    result = subprocess.run([sys.executable, '-B', '-m', 'safety.preprod.guarida_watchdog'], cwd=tmp_path,
                            env=environment, capture_output=True, text=True, timeout=3)
    assert result.returncode == 0 and json.loads(result.stdout)['status'] == 'PLAN_ONLY'


def test_watchdog_epoch_established_before_owner_publication(tmp_path, monkeypatch):
    """A health writer may run as soon as the owner file becomes visible."""
    from safety.preprod import guarida_watchdog as watchdog

    state, cfg, contract = watchdog_fixture(tmp_path, rollback_fixture='timeout')
    original_publish = watchdog.exclusive_json
    ticks = iter([10.0, 11.0, 12.0, 13.0, 14.0])
    monkeypatch.setattr(watchdog.time, 'monotonic', lambda: next(ticks, 14.0))

    def publish_with_concurrent_health(path, value):
        original_publish(path, value)
        if Path(path).name == 'watchdog.owner.json':
            publish_health(state, cfg, healthy=False)

    monkeypatch.setattr(watchdog, 'exclusive_json', publish_with_concurrent_health)
    result, code = watchdog.run_recording(contract)
    assert code == 2 and result['status'] == 'HOLD_ROLLBACK_UNCERTAIN'
    assert result['reason'] == 'health_failure'
    assert result['actions'] == ['SIMULATED_ROLLBACK_TRANSFER']
    assert result['simulated_restore_verified'] is False
    assert (state / 'rollback.intent.json').is_file()
