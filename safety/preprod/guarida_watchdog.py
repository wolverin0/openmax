"""Bounded EXTERNAL CONTROLLER watchdog; recording driver only, never AP code.

Default PLAN_ONLY. --run-recording runs a real host process against local fixture
health reports. No Python/native runtime is assumed on the AP. Host/watchdog death
does NOT provide autonomous AP recovery; a restart refuses the durable owner/latch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import time

from safety.preprod.rollback_snapshot import RecoveryVerification, RollbackManager, TransferOutcome

BINARY = getattr(os, 'O_BINARY', 0)


def require(ok, gate):
    if not ok:
        raise ValueError(gate)


def regular(path, bound=4096):
    st = Path(path).lstat()
    require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and st.st_size <= bound,
            'NON_REGULAR_LINKED_OR_LARGE_LOCAL_FILE')
    require(st.st_uid == (os.getuid() if hasattr(os, 'getuid') else 0), 'LOCAL_FILE_OWNER')
    return st


def read_json(path):
    regular(path)
    return json.loads(Path(path).read_bytes())


def write_all(fd, data):
    view = memoryview(data)
    while view:
        n = os.write(fd, view)
        require(n > 0, 'SHORT_LOCAL_WRITE')
        view = view[n:]


def exclusive_json(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | BINARY, 0o600)
    try:
        write_all(fd, json.dumps(value, sort_keys=True).encode())
        os.fsync(fd)
    finally:
        os.close(fd)


def bound_identity(value, cfg):
    return isinstance(value, dict) and all(value.get(k) == cfg[k] for k in ('attempt_id', 'nonce'))


def load_contract(path):
    path = Path(path)
    require(path.parent.is_dir() and not path.parent.is_symlink(), 'STATE_DIRECTORY')
    cfg = read_json(path)
    require(cfg.get('execution_driver') == 'recording_stub', 'PRODUCTION_DRIVER_DISABLED')
    require(re.fullmatch(r'[A-Za-z0-9_-]{1,64}', cfg.get('attempt_id', ''))
            and re.fullmatch('[0-9a-f]{64}', cfg.get('nonce', '')), 'CONTRACT_IDENTITY')
    for key, ceiling in [('health_timeout_seconds', 60), ('maximum_seconds', 600)]:
        value = cfg.get(key)
        require(type(value) in (int, float) and math.isfinite(value) and 0 < value <= ceiling,
                'CONTRACT_DEADLINE')
    require(cfg['maximum_seconds'] >= cfg['health_timeout_seconds'], 'CONTRACT_DEADLINE_ORDER')
    require(cfg.get('rollback_fixture', 'delivered') in ('delivered', 'timeout', 'verification_failure'),
            'RECORDING_FIXTURE_ALLOWLIST')
    require(re.fullmatch('[0-9a-f]{64}', cfg.get('golden_sha256', '')), 'GOLDEN_HASH_FORMAT')
    golden = path.parent.parent / 'own-stock.return.bin.gz'
    regular(golden, 64 * 1024 * 1024)
    with golden.open('rb') as f:
        require(hashlib.file_digest(f, 'sha256').hexdigest() == cfg['golden_sha256'], 'GOLDEN_HASH')
    return cfg, golden


def run_recording(contract):
    cfg, golden = load_contract(contract)
    directory = Path(contract).parent
    identity = {k: cfg[k] for k in ('attempt_id', 'nonce')}
    base = dict(layer='external_controller_host_process', execution_driver='recording_stub',
                production_execution_enabled=False, physical_recovery_qualified=False,
                autonomous_across_host_or_AP_power_loss=False, **identity)
    # Immutable per-attempt owner and intent: no automatic restart/rearm, even
    # after forced process death. Foreign identity never authorizes an action.
    for name in ('watchdog.owner.json', 'rollback.intent.json'):
        path = directory / name
        if path.exists() or path.is_symlink():
            prior = read_json(path)
            require(bound_identity(prior, cfg), 'FOREIGN_OWNER_OR_INTENT')
            return dict(base, status='HOLD_PREEXISTING_OWNER_OR_INTENT', rollback_triggered=False), 2
    exclusive_json(directory / 'watchdog.owner.json', dict(identity, pid=os.getpid(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    start = time.monotonic()
    deadline = start + cfg['maximum_seconds']
    last_observed = start
    health_seen = False
    reason = None
    try:
        while True:
            now = time.monotonic()
            health_path = directory / 'health.json'
            if health_path.exists() or health_path.is_symlink():
                health = read_json(health_path)
                now = time.monotonic()
                require(bound_identity(health, cfg), 'FOREIGN_HEALTH_IDENTITY')
                stamp = health.get('observed_host_monotonic')
                require(type(stamp) in (int, float) and math.isfinite(stamp)
                        and last_observed <= stamp <= now, 'HEALTH_CLOCK_OR_REPLAY')
                require(type(health.get('healthy')) is bool and type(health.get('complete')) is bool,
                        'HEALTH_PROTOCOL')
                last_observed, health_seen = stamp, True
                if health['healthy'] is False:
                    reason = 'health_failure'; break
                if now < deadline and now - stamp <= cfg['health_timeout_seconds'] and health['complete'] is True:
                    result = dict(base, status='PASS_WATCHDOG_HEALTH_ACCEPTED_NO_ROLLBACK',
                                  rollback_triggered=False, elapsed_seconds=now - start)
                    exclusive_json(directory / 'watchdog.result.json', result)
                    return result, 0
            if now >= deadline:
                reason = 'watchdog_deadline'; break
            if now - last_observed >= cfg['health_timeout_seconds']:
                reason = 'health_timeout_or_writer_death' if health_seen else 'no_health_timeout'
                break
            time.sleep(min(.05, deadline - now))

        exclusive_json(directory / 'rollback.intent.json', dict(identity, reason=reason,
            golden_sha256=cfg['golden_sha256'], observed_host_monotonic=time.monotonic()))
        actions = []
        action_fd = os.open(directory / 'recording-actions.jsonl', os.O_WRONLY | os.O_CREAT | os.O_EXCL | BINARY, 0o600)
        try:
            def action(name):
                actions.append(name)
                write_all(action_fd, (json.dumps(dict(action=name, **identity)) + '\n').encode())
                os.fsync(action_fd)
            class RecordingPower:
                def trigger_tftp_recovery(self, *args, **kwargs):
                    action('SIMULATED_POWER_RESET'); return True
            def soft(path):
                action('SIMULATED_ROLLBACK_TRANSFER')
                if cfg.get('rollback_fixture') == 'timeout': raise TimeoutError('recording fixture')
                return TransferOutcome.DELIVERED
            def verify(context):
                action('SIMULATED_POSTBOOT_VERIFICATION')
                return RecoveryVerification(context.target_host, True, True, True, True,
                    cfg.get('rollback_fixture') != 'verification_failure', 'RECORDING_NOT_PHYSICAL_EVIDENCE',
                    context.attempt_id, context.image_sha256, time.time())
            manager = RollbackManager('RECORDING_NOT_A_HOST', 0, golden, cfg['golden_sha256'], RecordingPower())
            incident = manager.execute_recovery(reason, ssh_sysupgrade_fn=soft, verify_recovery_fn=verify)
            result = dict(base, status='PASS_WATCHDOG_RECORDING_ROLLBACK' if incident.success else 'HOLD_ROLLBACK_UNCERTAIN',
                          rollback_triggered=True, reason=reason, actions=actions,
                          simulated_restore_verified=incident.success, elapsed_seconds=time.monotonic() - start)
        finally:
            os.close(action_fd)
        exclusive_json(directory / 'watchdog.result.json', result)
        return result, 0 if incident.success else 2
    except (ValueError, OSError, json.JSONDecodeError) as error:
        result = dict(base, status='HOLD_WATCHDOG_ERROR', error_type=type(error).__name__,
                      gate=str(error) if isinstance(error, ValueError) else 'LOCAL_IO_ERROR',
                      rollback_triggered=(directory / 'rollback.intent.json').exists())
        if not (directory / 'watchdog.result.json').exists():
            exclusive_json(directory / 'watchdog.result.json', result)
        return result, 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-recording', action='store_true')
    parser.add_argument('--contract', type=Path)
    args = parser.parse_args(argv)
    if not args.run_recording:
        print(json.dumps(dict(status='PLAN_ONLY', execution_driver='recording_stub',
                              production_execution_enabled=False, layer='external_controller_host_process')))
        return 0
    if args.contract is None:
        parser.error('--contract required for local recording process')
    try:
        result, code = run_recording(args.contract)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        result, code = dict(status='HOLD_CONTRACT_OR_OWNERSHIP_ERROR', error_type=type(error).__name__,
                            production_execution_enabled=False), 2
    print(json.dumps(result))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
