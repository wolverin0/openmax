"""Complete the PRIVATE offline kit. PLAN_ONLY by default; no device adapter."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from safety.preprod import guarida as p

INITIAL_MANIFEST_SHA = 'd62241e53b25b1ce1b569a32339d1f2c8daae2425666874d2a455bef1f969269'
INITIAL_READINESS_SHA = 'ed70595be751d6e3d4b5c50f9d526d866525fdbb0997b08e8906dda21f1fc419'
SOURCES = ('safety/preprod/guarida_watchdog.py', 'safety/preprod/rollback_snapshot.py',
           'orchestration/power/smart_power.py')


def copy_verified(destination, data):
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    p._write(destination, data)
    p.require(destination.read_bytes() == data, 'COPY_READBACK')
    return dict(bytes=len(data), sha256=p.sha(data))


def complete(bundle=p.DEFAULT_OUT, evidence=p.EVIDENCE):
    bundle, evidence = Path(bundle), Path(evidence)
    initial = p.read_bound(bundle, 'manifest.json', INITIAL_MANIFEST_SHA)
    readiness = p.read_bound(evidence, 'preprod_guarida_readiness_20261022.json', INITIAL_READINESS_SHA)
    p.require(not (bundle / 'manifest.watchdog-v2.json').exists()
              and not (bundle / 'host').exists() and not (bundle / 'backups').exists(), 'KIT_ALREADY_STARTED')
    data = p.inventory(evidence)
    p.require((bundle / 'draft-v3.REJECTED.bin').read_bytes() == data.pop('candidate')
              and (bundle / 'own-stock.return.bin.gz').read_bytes() == data.pop('package'), 'EXISTING_COPY_BINDING')
    components = {}
    def save(name, content): components[name] = copy_verified(bundle / name, content)
    save('history/initial/manifest.json', initial)
    save('history/initial/readiness.json', readiness)
    review = evidence / 'preprod_guarida_independent_review_20261022.json'
    if review.is_file(): save('history/initial/independent-review.json', review.read_bytes())
    save('history/initial/guarida.py', (p.REPO / 'safety/preprod/guarida.py').read_bytes())
    save('history/initial/test_preprod_guarida.py', (p.REPO / 'tests/test_preprod_guarida.py').read_bytes())
    baseline = p.read_bound(evidence, p.BASELINE + '/receipt.json', p.BASELINE_SHA)
    save('backups/receipt.json', baseline)
    p.require(len(data['historical_backup']['captures']) == 20, 'BACKUP_CAPTURE_COUNT')
    for name, row in data['historical_backup']['captures'].items():
        save('backups/' + name, p.read_bound(evidence, p.BASELINE + '/' + name, row['sha256'], row['bytes']))
    for name in SOURCES: save('host/' + name, (p.REPO / name).read_bytes())
    # Public test excerpt contains only synthetic fixtures and host subprocesses.
    tests = (p.REPO / 'tests/test_preprod_guarida.py').read_text(encoding='utf-8')
    marker = '# These start the SAME watchdog CLI'
    p.require(tests.count(marker) == 1, 'TEST_EXCERPT_BOUNDARY')
    test_excerpt = ('import json, hashlib, os, subprocess, sys, time\nfrom pathlib import Path\nimport pytest\n\n'
                    + marker + tests.split(marker)[1])
    test_excerpt = test_excerpt.replace('cwd=Path(__file__).resolve().parents[1]',
                                        'cwd=Path(__file__).resolve().parent')
    save('host/test_watchdog.py', test_excerpt.encode())
    checklist = (
        'HOLD: OFFLINE PREPARATION ONLY. Production execution is disabled.\n'
        'PRIVATE backups and firmware must never be published. Windows ACL privacy is not qualified.\n'
        'Layer: external_controller_host_process. A Python host is required; no AP Python assumed.\n'
        'Health uses the SAME HOST monotonic clock, exact nonce/attempt and atomic file replacement.\n'
        'Only recording_stub exists. No network, power, firmware or TFTP adapter is provided.\n'
        'The real watchdog detects local health failure/timeout and journals ONE simulated rollback.\n'
        'Owner/intent files are retained, including after process death: never remove them to retry.\n'
        'Host/watchdog/AP power loss is NOT autonomous recovery; physical restore remains UNQUALIFIED.\n'
        'Local tests: from host/, python -B -m pytest test_watchdog.py -q. Fixtures are disposable.\n'
        'Local default: from host/, python -B -m safety.preprod.guarida_watchdog (PLAN_ONLY).\n'
        'watchdog-recording/ is a consumed, immutable demo; do not rerun/rearm it.\n'
        'Before any deployment: select/qualify exact image, fresh exact board/backups/protected state,\n'
        'prove failed-boot recovery and real rollback adapter/independent health, obtain execution order.\n'
        'Historical rejected image and reachable own-stock return do not satisfy those requirements.\n'
        'Never use install_openwrt_ddunlock or write bootloader/ART/factory/calibration/MAC/cfg.\n')
    save('host/CHECKLIST.txt', checklist.encode())
    contract = dict(execution_driver='recording_stub', attempt_id='offline-demo-20261022',
                    nonce='c57b3047b4e341499847e8d1f8d1580fb8bf3dab868f4dffb9b59f1f2d98250d',
                    health_timeout_seconds=.5, maximum_seconds=3, golden_sha256=p.PACKAGE_SHA)
    save('watchdog-recording/contract.json', json.dumps(contract, indent=2).encode())
    command = [sys.executable, '-B', '-m', 'safety.preprod.guarida_watchdog', '--run-recording',
               '--contract', str((bundle / 'watchdog-recording/contract.json').resolve())]
    environment = dict(os.environ); environment.pop('PYTHONPATH', None)
    result = subprocess.run(command, cwd=bundle / 'host', env=environment,
                            capture_output=True, timeout=10)
    save('watchdog-recording/process.stdout', result.stdout)
    save('watchdog-recording/process.stderr', result.stderr)
    demo = json.loads(result.stdout.strip().splitlines()[-1])
    p.require(result.returncode == 0 and demo['status'] == 'PASS_WATCHDOG_RECORDING_ROLLBACK'
              and demo['reason'] == 'no_health_timeout', 'REAL_HOST_PROCESS_DEMO_FAILED')
    for name in ('watchdog.owner.json', 'rollback.intent.json', 'recording-actions.jsonl', 'watchdog.result.json'):
        raw = (bundle / 'watchdog-recording' / name).read_bytes()
        components['watchdog-recording/' + name] = dict(bytes=len(raw), sha256=p.sha(raw))
    # Public-safe derivative contains metadata, source and synthetic tests ONLY.
    for name in SOURCES: save('public-safe/' + name, (bundle / 'host' / name).read_bytes())
    save('public-safe/test_watchdog.py', test_excerpt.encode())
    save('public-safe/CHECKLIST.txt', checklist.encode())
    public = dict(schema='preprod-offline-watchdog-metadata-v2', status='HOLD', GO=False,
        production_execution_enabled=False, selected_deployment_candidate=None,
        historical_candidate_status='DRAFT_REJECTED_NOT_QUALIFIED',
        layer='external_controller_host_process', execution_driver='recording_stub',
        actual_host_process_tested=True, autonomous_across_host_or_AP_power_loss=False,
        physical_recovery_qualified=False, target_rollback_adapter_qualified=False,
        backup_components={f'private_backup_{i:02d}': row for i, row in enumerate(
            data['historical_backup']['captures'].values(), 1)},
        private_firmware_components={name: dict(bytes=(bundle / name).stat().st_size,
            sha256=p.sha((bundle / name).read_bytes())) for name in ('draft-v3.REJECTED.bin', 'own-stock.return.bin.gz')},
        sources={name: components['host/' + name] for name in SOURCES},
        real_process_result=demo['status'], real_process_exit_code=result.returncode,
        scope='Local integrity and recording-driver mechanism only; no device/network/credential access.')
    save('public-safe/metadata.json', json.dumps(public, indent=2).encode())
    manifest = dict(schema='preprod-private-watchdog-kit-v2', status='HOLD', GO=False,
        production_execution_enabled=False, selected_deployment_candidate=None,
        layer='external_controller_host_process', execution_driver='recording_stub',
        backup_count=20, private_bundle=True, publish_bundle=False,
        self_contained_scope='Host watchdog recording process plus held private backups; NOT a physical recovery kit.',
        actual_host_process_tested=True, physical_recovery_qualified=False,
        target_rollback_adapter_qualified=False, autonomous_across_host_or_AP_power_loss=False,
        components=components, original_manifest_sha256=p.sha(initial),
        original_readiness_sha256=p.sha(readiness), real_process_result=demo,
        source_sha256=p.sha(Path(__file__).read_bytes()), blockers=json.loads(initial)['blockers'])
    save('manifest.watchdog-v2.json', json.dumps(manifest, indent=2).encode())
    return manifest


def repair_snapshot_dependencies(bundle=p.DEFAULT_OUT):
    """Add a new immutable kit variant; never overwrite the failed v2 variant."""
    bundle = Path(bundle)
    host, public = bundle / 'host-snapshot-v3', bundle / 'public-safe-snapshot-v3'
    p.require(not host.exists() and not public.exists(), 'SNAPSHOT_KIT_ALREADY_STARTED')
    old_manifest = (bundle / 'manifest.watchdog-v2.json').read_bytes()
    old = json.loads(old_manifest)
    for name, row in old['components'].items():
        p.read_bound(bundle, name, row['sha256'], row['bytes'])
    p.read_bound(bundle, 'own-stock.return.bin.gz', p.PACKAGE_SHA)
    snapshot = (p.REPO / 'safety/preprod/rollback_snapshot.py').read_bytes()
    marker = b'# BEGIN ORIGINAL SOURCE\n'
    p.require(snapshot.count(marker) == 1, 'SNAPSHOT_BOUNDARY')
    original_sha = '85e412bde00b1e9003bf191a95fe2ebbc868adf4c4fd431ea3428fa8fe5f00c7'
    p.require(p.sha(snapshot.split(marker)[1]) == original_sha, 'SNAPSHOT_BODY_PROVENANCE')
    power_sha = '7cf7146c460cc0353758290d3191d6742de49dd2dbf714be0e2629738f249083'
    p.read_bound(p.REPO, 'orchestration/power/smart_power.py', power_sha)
    tests = (p.REPO / 'tests/test_preprod_guarida.py').read_text(encoding='utf-8')
    test_marker = '# These start the SAME watchdog CLI'
    p.require(tests.count(test_marker) == 1, 'TEST_EXCERPT_BOUNDARY')
    excerpt = ('import json, hashlib, os, subprocess, sys, time\nfrom pathlib import Path\nimport pytest\n\n'
               + test_marker + tests.split(test_marker)[1]).replace(
                   'cwd=Path(__file__).resolve().parents[1]', 'cwd=Path(__file__).resolve().parent')
    components = {}
    for destination in (host, public):
        for name in SOURCES:
            components[str((destination / name).relative_to(bundle)).replace('\\', '/')] = copy_verified(
                destination / name, (p.REPO / name).read_bytes())
        for name, raw in [('test_watchdog.py', excerpt.encode()),
                          ('CHECKLIST.txt', (bundle / 'host/CHECKLIST.txt').read_bytes())]:
            components[str((destination / name).relative_to(bundle)).replace('\\', '/')] = copy_verified(destination / name, raw)
    state = bundle / 'watchdog-recording-snapshot-v3'
    contract = dict(execution_driver='recording_stub', attempt_id='offline-snapshot-v3', nonce='d' * 64,
                    health_timeout_seconds=.5, maximum_seconds=3, golden_sha256=p.PACKAGE_SHA)
    copy_verified(state / 'contract.json', json.dumps(contract, indent=2).encode())
    environment = dict(os.environ); environment.pop('PYTHONPATH', None)
    result = subprocess.run([sys.executable, '-B', '-m', 'safety.preprod.guarida_watchdog',
        '--run-recording', '--contract', str((state / 'contract.json').resolve())],
        cwd=host, env=environment, capture_output=True, timeout=10)
    copy_verified(state / 'process.stdout', result.stdout)
    copy_verified(state / 'process.stderr', result.stderr)
    demo = json.loads(result.stdout.strip().splitlines()[-1])
    p.require(result.returncode == 0 and demo['status'] == 'PASS_WATCHDOG_RECORDING_ROLLBACK', 'SNAPSHOT_REAL_PROCESS')
    metadata = json.loads((bundle / 'public-safe/metadata.json').read_bytes())
    metadata.update(schema='preprod-offline-watchdog-snapshot-v3', sources={name:dict(
        sha256=p.sha((p.REPO / name).read_bytes()), bytes=(p.REPO / name).stat().st_size) for name in SOURCES},
        snapshot_original_path='orchestration/rollback/workflow.py', snapshot_body_sha256=original_sha,
        power_dependency_HEAD_sha256=power_sha, prior_dirty_api_import_failure_preserved=True)
    copy_verified(public / 'metadata.json', json.dumps(metadata, indent=2).encode())
    manifest = dict(status='HOLD', GO=False, production_execution_enabled=False,
        selected_deployment_candidate=None, execution_driver='recording_stub',
        layer='external_controller_host_process', snapshot_body_sha256=original_sha,
        power_dependency_HEAD_sha256=power_sha, components=components,
        old_manifest_sha256=p.sha(old_manifest), real_process_result=demo,
        backup_copies_verified=20, physical_recovery_qualified=False,
        autonomous_across_host_or_AP_power_loss=False,
        source_sha256=p.sha(Path(__file__).read_bytes()))
    copy_verified(bundle / 'manifest.snapshot-v3.json', json.dumps(manifest, indent=2).encode())
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--complete-local-kit', action='store_true')
    parser.add_argument('--repair-snapshot-local', action='store_true')
    args = parser.parse_args(argv)
    if not args.complete_local_kit and not args.repair_snapshot_local:
        print(json.dumps(dict(status='PLAN_ONLY', production_execution_enabled=False))); return 0
    if args.repair_snapshot_local:
        manifest = repair_snapshot_dependencies()
        print(json.dumps(dict(status=manifest['status'], production_execution_enabled=False,
                              snapshot_body_sha256=manifest['snapshot_body_sha256'])))
        return 0
    manifest = complete()
    print(json.dumps(dict(status=manifest['status'], backup_count=manifest['backup_count'],
        process_test=manifest['real_process_result']['status'], production_execution_enabled=False)))
    return 0


if __name__ == '__main__': raise SystemExit(main())
