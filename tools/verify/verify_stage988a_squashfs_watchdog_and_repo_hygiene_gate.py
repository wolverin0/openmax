#!/usr/bin/env python3
"""Offline983A..988A source gate; native image emission remains independently blocked."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.stage779_822_offline_common import (
    atomic_write, local, read_json, receipt, save, snapshot)
from tools.verify.enforce_5pillar_research_gate import (
    audit_repo_deterministic_gates, audit_stage_receipt_5pillars)
from tools.verify.verify_stage940a_public_release_v23_gate import (
    binding_matches, document_contract, index_hygiene, index_revision, pytest_summary)
from tools.verify.verify_stage964a_unified_physical_runner_gate import check_export, pins_match_index

STEM = 'stage988a_squashfs_watchdog_and_repo_hygiene_gate'
SELF = 'tools/verify/' + Path(__file__).name
CLASS = 'CONFIRMED_STATIC_BINARY'
KIT = 'firmware/openwrt/pbe5ac_gen2_ptp_kit'
BOOTSTRAP = KIT + '/99-fmx-pbe5ac-ptp'
WATCHDOG = KIT + '/fmx_ptp_rollback_watchdog.sh'
TRANSACTION = KIT + '/fmx_pbe_lbe_runtime_transaction.sh'
MANIFEST = KIT + '/SHA256SUMS'
GENERATOR = 'firmware/openwrt/build_universal_pbe5ac_lbe5ac_openwrt_factory.py'
WATCHDOG_BUILDER = 'tools/verify/build_stage984a_to_986a_watchdog_evidence.py'
HYGIENE_BUILDER = 'tools/verify/audit_stage987a_repo_status_and_orphan_artifacts.py'
COMMON = 'tools/verify/stage779_822_offline_common.py'
STEMS = {
    983: 'stage983a_squashfs_factory_fail_closed_contract',
    984: 'stage984a_guarded_ptp_startup_watchdog',
    985: 'stage985a_watchdog_loss_deadline_and_fault_tests',
    986: 'stage986a_ptp_active_source_sha256_manifest',
    987: 'stage987a_repo_status_and_orphan_artifacts',
}
TESTS = [
    'tests/test_stage983a_squashfs_factory_contract.py',
    'tests/test_stage984a_986a_watchdog.py',
    'tests/test_stage987a_repo_hygiene.py',
    'tests/test_stage983a_to_988a_suite.py',
]
EXPECTED_SOURCES = {
    983: {GENERATOR, TESTS[0], COMMON},
    984: {WATCHDOG, TRANSACTION, MANIFEST, WATCHDOG_BUILDER, TESTS[1], COMMON},
    985: {WATCHDOG, TRANSACTION, MANIFEST, WATCHDOG_BUILDER, TESTS[1], COMMON},
    986: {WATCHDOG, TRANSACTION, MANIFEST, WATCHDOG_BUILDER, TESTS[1], COMMON},
    987: {HYGIENE_BUILDER, TESTS[2], COMMON},
}
REQUIRED_PAYLOAD = [
    'etc/uci-defaults/99-fmx-pbe5ac-ptp',
    'usr/sbin/fmx_ptp_rollback_watchdog.sh',
    'usr/sbin/fmx_pbe_lbe_runtime_transaction.sh',
    'etc/rc.local',
]
PRIVATE_PREFIX = 'stage983_988/stage987a/runs/'


def artifact(stage: int) -> str:
    return f'artifacts/autoresearch/{STEMS[stage]}.json'


def _ordinary(root: Path, label: str) -> Path:
    path = local(root, label)
    lexical = root / label
    for parent in (lexical, *lexical.parents):
        if parent == root:
            break
        if parent.is_symlink() or getattr(parent, 'is_junction', lambda: False)():
            raise ValueError('indirect evidence path')
    if not path.is_file():
        raise ValueError('ordinary evidence file required')
    return path


def _count(value, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError('nonnegative integer required: ' + name)
    return value


def watchdog_test_contract(data: dict) -> list[str]:
    errors = []
    tests = data.get('tests', {})
    if not isinstance(tests, dict):
        return ['actual test summary required']
    if (type(tests.get('returncode')) is not int or tests['returncode'] != 0
            or type(tests.get('passed')) is not int or tests['passed'] <= 0
            or type(tests.get('tests')) is not int or tests['tests'] != tests['passed']
            or any(type(tests.get(k)) is not int or tests[k] != 0
                   for k in ('failures', 'errors', 'skipped'))
            or tests.get('all_passed') is not True):
        errors.append('watchdog tests require actual zero exit, positive count and no failures/skips')
    if data.get('real_ping_executed') is not False or data.get('real_45_or_120_second_wait_executed') is not False:
        errors.append('command-stub evidence cannot certify native ping or real deadline execution')
    return errors


def audit_manifest(root: Path, data: dict) -> dict:
    errors = []
    try:
        if (data.get('member_count') != 21 or type(data.get('member_count')) is not int
                or data.get('binary_images_emitted') != 0
                or data.get('original_historical_receipts_repinned') is not False):
            raise ValueError('21 source members only; no binary emission or historical repinning')
        descriptor = data['manifest']
        if descriptor.get('path') != MANIFEST:
            raise ValueError('exact PBE source manifest required')
        binding_matches(root, descriptor)
        members = data['members']
        if not isinstance(members, list) or len(members) != 21:
            raise ValueError('complete21 source inventory required')
        paths = [item['path'] for item in members]
        if len(set(paths)) != 21 or not {BOOTSTRAP, WATCHDOG, TRANSACTION} <= set(paths):
            raise ValueError('unique bootstrap/watchdog/transaction source membership required')
        expected = {}
        for source in members:
            label = source['path']
            if not label.startswith(KIT + '/'):
                raise ValueError('manifest source outside PBE kit')
            name = label[len(KIT) + 1:]
            if (any(part in ('', '.', '..') for part in name.split('/'))
                    or name.startswith(('public_release', 'public_assets'))
                    or Path(name).suffix.lower() in {'.bin', '.ko', '.sqfs', '.squashfs'}):
                raise ValueError('archive/binary/external member prohibited')
            binding_matches(root, source)
            if not _ordinary(root, label).read_bytes().startswith(b'#!/bin/sh\n'):
                raise ValueError('shell source membership required')
            expected[name] = source['sha256']
        parsed = {}
        for line in _ordinary(root, MANIFEST).read_text(encoding='ascii').splitlines():
            match = re.fullmatch(r'([0-9a-f]{64})  ([A-Za-z0-9_./-]+)', line)
            if not match or match[2] in parsed:
                raise ValueError('strict unique SHA256SUMS lines required')
            parsed[match[2]] = match[1]
        if parsed != expected:
            raise ValueError('SHA256SUMS membership/hash mismatch')
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError) as exc:
        errors.append(str(exc))
    return {'compliant': not errors, 'failures': errors, 'scope': '21 current source scripts; no image evidence'}


def verify_private_inventory(gitdir: Path, evidence: list[dict], audit: dict, cleanup: dict) -> None:
    """Recompute disclosed counts from the retained capture, not today's changing status."""
    required = {'git_status_porcelain.z', 'git_index.z', 'git_ignored.z', 'git_untracked.z',
                'inventory.json', 'restore_map.json'}
    directories = {str(Path(row['path']).parent).replace('\\', '/') for row in evidence}
    by_name = {Path(row['path']).name: row['path'] for row in evidence}
    if len(directories) != 1 or set(by_name) != required or len(evidence) != len(required):
        raise ValueError('complete single-run private Git inventory required')
    from tools.verify.audit_stage987a_repo_status_and_orphan_artifacts import (
        status_rows, TEMP_NAME, FORBIDDEN, summary_json, contains_raw)
    raw_status = _ordinary(gitdir, by_name['git_status_porcelain.z']).read_bytes()
    raw_index = _ordinary(gitdir, by_name['git_index.z']).read_bytes()
    rows = status_rows(raw_status)
    tracked = set()
    for item in raw_index.split(b'\0'):
        if item:
            metadata, label = item.split(b'\t', 1)
            fields = metadata.split()
            if len(fields) != 3:
                raise ValueError('malformed captured index')
            tracked.add(label.decode('utf-8'))
    ignored = {x.decode('utf-8') for x in _ordinary(gitdir, by_name['git_ignored.z']).read_bytes().split(b'\0') if x}
    others = {x.decode('utf-8') for x in _ordinary(gitdir, by_name['git_untracked.z']).read_bytes().split(b'\0') if x}
    counts = {'staged': sum(row['status'][0] not in (' ', '?', '!') for row in rows),
              'unstaged': sum(row['status'][1] not in (' ', '?', '!') for row in rows),
              'untracked': len(others), 'ignored': len(ignored)}
    if (audit['status_counts'] != counts or audit['tracked_index_count'] != len(tracked)
            or audit['index_signature_sha256'] != hashlib.sha256(raw_index).hexdigest()):
        raise ValueError('captured Git counts/index signature mismatch')
    inventory = read_json(gitdir, by_name['inventory.json'])
    for key, expected in [('git_status', rows), ('tracked_paths', sorted(tracked)),
                          ('ignored_paths', sorted(ignored)), ('untracked_paths', sorted(others))]:
        if inventory.get(key) != expected:
            raise ValueError('private inventory does not match captured Git data')
    candidates = inventory.get('candidates')
    if not isinstance(candidates, list):
        raise ValueError('captured candidate inventory required')
    proved = [row for row in candidates if row.get('eligible') is True]
    if len({row['path'] for row in candidates}) != len(candidates):
        raise ValueError('duplicate captured candidate')
    if len(proved) != cleanup['proven_orphans'] or len(candidates)-len(proved) != cleanup['retained_candidates']:
        raise ValueError('captured orphan classification counts mismatch')
    if proved and inventory.get('reference_scan_complete') is not True:
        raise ValueError('quarantine requires a complete reference scan')
    restoration = read_json(gitdir, by_name['restore_map.json'])
    moves = restoration.get('moves')
    if (restoration.get('state') != cleanup['transaction_state'] or not isinstance(moves, list)
            or len(moves) != cleanup['quarantined'] or restoration.get('restored_after_failure') != 0):
        raise ValueError('private restoration map/state mismatch')
    allowed = {row['path']: row for row in proved}
    if len({move.get('original_path') for move in moves}) != len(moves):
        raise ValueError('duplicate restoration-map original')
    run_dir = next(iter(directories))
    total_bytes = 0
    for move in moves:
        original = move['original_path']
        target = move['quarantine_path']
        if (original not in allowed or original in tracked or original not in ignored
                or not original.startswith(('artifacts/autoresearch/', 'artifacts/verification/'))
                or not isinstance(target, str) or not target.startswith('quarantine/')
                or any(part in ('', '.', '..') for part in target.split('/'))):
            raise ValueError('unbounded or unproved restoration-map move')
        blob = _ordinary(gitdir, run_dir + '/' + target).read_bytes()
        source = allowed[original]
        if (move.get('sha256') != source['sha256'] or move.get('bytes') != source['bytes']
                or len(blob) != source['bytes'] or hashlib.sha256(blob).hexdigest() != source['sha256']):
            raise ValueError('quarantined bytes differ from private candidate proof')
        match = TEMP_NAME.fullmatch(Path(original).name)
        value = summary_json(blob)
        expected_stage = match['stage'].upper().removeprefix('STAGE') if match else None
        declared = str(value.get('stage', '')).upper().replace('STAGE ', '').replace('STAGE-', '')
        if (not match or FORBIDDEN.search(original) or not value.get('schema_version')
                or declared != expected_stage or contains_raw(value)
                or source.get('reason') != 'proven_ignored_atomic_summary_orphan'):
            raise ValueError('restoration map must contain generated-summary orphans only')
        total_bytes += len(blob)
    if len(moves) > 64 or total_bytes > 32 * 1024 * 1024:
        raise ValueError('captured quarantine exceeds bounded move budget')


def hygiene_evidence_errors(root: Path, data: dict, *, public: bool = False) -> list[str]:
    errors = []
    try:
        audit, cleanup = data['audit'], data['cleanup']
        if (data.get('all_gates_passed') is not True
                or data.get('unrelated_dirty_work_preserved') is not True
                or data.get('private_inventory_public_contents_emitted') is not False
                or data.get('private_evidence_available_to_public_checkout') is not False):
            raise ValueError('private inventory and preserved user-work scope required')
        if audit.get('complete') is not True or audit.get('index_unchanged') is not True:
            raise ValueError('complete nonmutating Git inventory required')
        if not re.fullmatch('[0-9a-f]{64}', str(audit.get('index_signature_sha256'))):
            raise ValueError('captured index signature required')
        if not isinstance(audit.get('status_counts'), dict):
            raise ValueError('captured Git status counts required')
        for key in ('staged', 'unstaged', 'untracked', 'ignored'):
            _count(audit['status_counts'].get(key), key)
        _count(audit.get('tracked_index_count'), 'tracked index count')
        if (cleanup.get('mode') != 'QUARANTINE' or cleanup.get('complete') is not True
                or cleanup.get('transaction_state') not in ('NO_PROVEN_ORPHANS', 'QUARANTINED')):
            raise ValueError('completed bounded quarantine/no-op required')
        for key in ('irreversible_deletions', 'tracked_or_user_files_moved', 'failed', 'restored_after_failure'):
            if _count(cleanup.get(key), key) != 0:
                raise ValueError('failed or destructive cleanup cannot certify release')
        if any(cleanup.get(k) is not True for k in (
                'all_moves_within_bounds', 'restore_map_retained')):
            raise ValueError('bounded reversible move proof required')
        proved = _count(cleanup.get('proven_orphans'), 'proven orphans')
        moved = _count(cleanup.get('quarantined'), 'quarantined')
        if moved > 64:
            raise ValueError('quarantine count exceeds bounded move budget')
        _count(cleanup.get('retained_candidates'), 'retained candidates')
        if moved != proved or ((proved == 0) != (cleanup['transaction_state'] == 'NO_PROVEN_ORPHANS')):
            raise ValueError('orphan/quarantine counts disagree')
        evidence = data.get('private_evidence')
        if not isinstance(evidence, list) or not evidence:
            raise ValueError('private complete inventory and restore-map bindings required')
        labels = []
        gitdir = None
        if not public:
            gitdir = Path(subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'],
                                                 cwd=root, text=True).strip())
        for row in evidence:
            label = row['path']
            if (not isinstance(label, str) or not label.startswith(PRIVATE_PREFIX)
                    or '\\' in label or ':' in label
                    or any(p in ('', '.', '..') for p in label.split('/'))
                    or type(row.get('bytes')) is not int or not 0 <= row['bytes'] <= 64 * 1024 * 1024
                    or not re.fullmatch('[0-9a-f]{64}', str(row.get('sha256')))):
                raise ValueError('bounded private inventory binding required')
            labels.append(label)
            if not public:
                blob = _ordinary(gitdir, label).read_bytes()
                if len(blob) != row['bytes'] or hashlib.sha256(blob).hexdigest() != row['sha256']:
                    raise ValueError('private Git inventory or restore-map drift')
        if len(labels) != len(set(labels)):
            raise ValueError('duplicate private evidence binding')
        if not public:
            verify_private_inventory(gitdir, evidence, audit, cleanup)
        elif ({Path(row['path']).name for row in evidence} != {
                'git_status_porcelain.z', 'git_index.z', 'git_ignored.z', 'git_untracked.z',
                'inventory.json', 'restore_map.json'} or len(evidence) != 6):
            raise ValueError('public metadata must declare the complete withheld inventory')
    except (OSError, ValueError, TypeError, KeyError, AttributeError, subprocess.CalledProcessError) as exc:
        errors.append(str(exc))
    return errors


def audit_stage(root: Path, stage: int, *, public: bool = False) -> dict:
    errors = []
    try:
        data = read_json(root, artifact(stage))
        if data.get('stage') != f'{stage}A' or data.get('status') != 'CONFIRMED':
            errors.append('stage identity or offline software status')
        if data.get('evidence_provenance_class') != CLASS:
            errors.append('only scoped offline software provenance is accepted')
        boundary = data.get('boundary', {})
        if not isinstance(boundary, dict):
            raise ValueError('explicit offline boundary required')
        if any(boundary.get(key) is not False for key in (
                'network_access', 'ssh_executed', 'device_writes', 'flash_approved')):
            errors.append('offline boundary violated')
        if boundary.get('physical_acceptance') != 'UNKNOWN' or data.get('physical_acceptance') != 'UNKNOWN':
            errors.append('physical acceptance must remain UNKNOWN')
        if not audit_stage_receipt_5pillars(data)['compliant']:
            errors.append('five-pillar structural references required')
        sources = data.get('sources')
        if not isinstance(sources, list) or not sources:
            raise ValueError('current source bindings required')
        labels = [source['path'] for source in sources]
        if len(labels) != len(set(labels)) or not EXPECTED_SOURCES[stage] <= set(labels):
            errors.append('mandatory source coverage missing/duplicated')
        for source in sources:
            binding_matches(root, source)
        text = _ordinary(root, f'docs/{STEMS[stage].upper()}.md').read_text(encoding='utf-8')
        if not document_contract(text):
            errors.append('document budget/header')
        if stage == 983:
            if (data.get('native_image_emission') != 'NOT_EXECUTED'
                    or data.get('packaging_readiness') != 'BLOCKED'
                    or data.get('required_payload') != REQUIRED_PAYLOAD
                    or data.get('qdisc_mode') != 'auto'
                    or data.get('vendor_signature_verified') is not False
                    or data.get('source_only_release') is not True
                    or data.get('deployment_authorized') is not False):
                errors.append('software tests cannot authorize native image emission')
            if 'REVIEWED_ACTIVE_BOOTSTRAP_REQUIRED' not in data.get('blockers', []):
                errors.append('retired bootstrap is still a packaging blocker')
        elif stage in (984, 985, 986):
            if data.get('all_gates_passed') is not True or data.get('tested_revision_unchanged') is not True:
                errors.append('source-bound watchdog verification required')
            if type(data.get('fresh_live_windows')) is not int or data['fresh_live_windows'] != 0:
                errors.append('no new native windows were executed')
            if stage == 984:
                deadlines = data.get('deadlines_s')
                if (deadlines != {'non-dfs': 45, 'dfs': 120}
                        or any(type(value) is not int for value in deadlines.values())
                        or data.get('default_mode') != '--dry-run' or data.get('qdisc_mode') != 'auto'
                        or data.get('firmware_restore_authorized') is not False
                        or data.get('flash_executed') is not False):
                    errors.append('exact45/120 guarded RAM-only watchdog required')
            if stage == 985:
                errors.extend(watchdog_test_contract(data))
            if stage == 986:
                errors.extend(audit_manifest(root, data)['failures'])
        elif stage == 987:
            errors.extend(hygiene_evidence_errors(root, data, public=public))
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        errors.append(str(exc))
    return {'stage': f'{stage}A', 'compliant': not errors, 'failures': errors,
            'acceptance_scope': 'offline source/tests; no native image or hardware approval'}


def audit_release(root: Path = ROOT, *, public: bool = False) -> dict:
    rows = [audit_stage(Path(root).resolve(), stage, public=public) for stage in STEMS]
    return {'compliant': all(row['compliant'] for row in rows), 'stages': rows,
            'native_image_emission': 'NOT_EXECUTED', 'packaging_readiness': 'BLOCKED',
            'physical_acceptance': 'UNKNOWN',
            'private_inventory_scope': 'WITHHELD_GIT_METADATA' if public else 'HASH_VERIFIED_LOCAL_METADATA'}


def freeze_sources(root: Path) -> list[dict]:
    labels = {SELF, *TESTS, COMMON,
              'tools/verify/enforce_5pillar_research_gate.py',
              'tools/verify/verify_stage826a_public_git_hygiene_and_push_gate.py',
              'tools/verify/verify_stage940a_public_release_v23_gate.py',
              'tools/verify/verify_stage964a_unified_physical_runner_gate.py'}
    for stage in STEMS:
        labels.update((artifact(stage), f'docs/{STEMS[stage].upper()}.md'))
        try:
            labels.update(source['path'] for source in read_json(root, artifact(stage))['sources'])
            if stage == 986:
                labels.update(source['path'] for source in read_json(root, artifact(stage))['members'])
        except (OSError, ValueError, TypeError, KeyError):
            pass  # The failed explicit audit above prevents closure.
    return [snapshot(root, label) for label in sorted(labels)]


def run_tests(root: Path, logs: Path, name: str) -> dict:
    path = logs / (name + '.xml')
    proc = subprocess.run([sys.executable, '-m', 'pytest', *TESTS, '-q', '--junitxml=' + str(path)],
                          cwd=root, capture_output=True, text=True, timeout=1200)
    atomic_write(logs / (name + '.stdout'), proc.stdout)
    atomic_write(logs / (name + '.stderr'), proc.stderr)
    return pytest_summary(path, proc.returncode)


def build(root: Path = ROOT, public_root: Path | None = None) -> dict:
    root = Path(root).resolve()
    gitdir = Path(subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'],
                                         cwd=root, text=True).strip())
    logs = gitdir / 'stage983_988'
    logs.mkdir(parents=True, exist_ok=True)
    original_index = index_revision(root)
    local_audit = audit_release(root)
    repository = audit_repo_deterministic_gates(root)
    pins = freeze_sources(root)
    hygiene, selected = index_hygiene(root, logs)
    indexed_sources = pins_match_index(pins, selected)
    blocked = {'returncode': None, 'tests': 0, 'all_passed': False, 'reason': 'PREREQUISITES_FAILED'}
    prerequisites = local_audit['compliant'] and hygiene['compliant'] and indexed_sources['compliant']
    local_tests = run_tests(root, logs, 'stage988_local') if prerequisites else blocked
    public_audit = {'compliant': False, 'reason': 'PUBLIC_CHECKOUT_REQUIRED'}
    public_export, public_tests = dict(public_audit), dict(blocked)
    if public_root is not None:
        public_root = Path(public_root).resolve()
        public_export = check_export(root, public_root, selected)
        public_audit = audit_release(public_root, public=True)
        if prerequisites and public_export['compliant'] and public_audit['compliant']:
            public_tests = run_tests(public_root, logs, 'stage988_public')
            public_export = check_export(root, public_root, selected)
    unchanged = all(source.get('available') is True and snapshot(root, source['path']) == source for source in pins)
    index_unchanged = index_revision(root) == original_index
    still_valid = audit_release(root)['compliant']
    local_passed = (local_audit['compliant'] and repository['compliant'] and hygiene['compliant']
                    and indexed_sources['compliant'] and local_tests['all_passed']
                    and unchanged and index_unchanged and still_valid)
    passed = (local_passed
              and local_tests['all_passed'] and public_audit['compliant'] and public_export['compliant']
              and public_tests['all_passed'] and unchanged and index_unchanged and still_valid)
    status = 'CONFIRMED' if passed else 'PREPARED' if public_root is None and local_passed else 'FAILED'
    data = receipt(988, 'SquashFS, startup-watchdog and repository hygiene source gate', pins)
    data.update(status=status, all_gates_passed=passed,
                evidence_provenance_class=CLASS,
                provenance_scope='offline executable-source, disposable-stub and metadata contracts only',
                local_release_audit=local_audit, public_release_audit=public_audit,
                repository_gate=repository, local_tests=local_tests, public_tests=public_tests,
                public_export=public_export, index_hygiene={'compliant': hygiene['compliant'],
                    'findings': hygiene['findings_by_rule']},
                indexed_tested_sources=indexed_sources,
                tested_revision_unchanged=unchanged, publication_index_unchanged=index_unchanged,
                verification_sources=pins, native_image_emission='NOT_EXECUTED',
                packaging_readiness='BLOCKED', physical_acceptance='UNKNOWN',
                fresh_live_windows=0, deployment_authorized=False, publication_executed=False)
    return save(root, STEM, data,
                f"Offline software/publication gate: {status}.\n\n"
                f"Local focused pytest: {local_tests['tests']} tests; return code {local_tests['returncode']}.\n"
                f"Clean public focused pytest: {public_tests['tests']} tests; return code {public_tests['returncode']}.\n"
                'Current source bytes, guarded45/120-second startup behavior, actual test results and21 source checksums are bound.\n'
                'Local inventory and reversible-quarantine receipts are verified against private Git metadata hashes.\n'
                'The public checkout validates disclosed inventory metadata, without pretending private native replay.\n'
                'Git index and mandatory source hashes are frozen before tests and checked again afterwards.\n'
                'Every relevant tested source must already match its selected index blob before any test starts.\n'
                'Public membership, modes, object IDs, bytes and clean status must exactly match the tested candidate.\n'
                'Software PASS does not create or approve a native SquashFS/factory image.\n'
                'The retired bootstrap and missing bound native toolchain leave image emission BLOCKED / NOT_EXECUTED.\n'
                'No flash, vendor firmware rollback, SSH, live ping, native target action or durable-memory ingestion is executed.\n'
                'Five-pillar references are structural; external research and memory ingestion remain deferred.\n'
                'Parent publication still requires a final staged-byte check and remote commit verification.\n'
                'Physical acceptance UNKNOWN; deployment is not authorized.\n')


def write_prepared(root: Path = ROOT) -> dict:
    data = receipt(988, 'SquashFS, startup-watchdog and repository hygiene source gate', [snapshot(root, SELF)])
    data.update(status='PREPARED', all_gates_passed=False, evidence_provenance_class=CLASS,
                native_image_emission='NOT_EXECUTED', packaging_readiness='BLOCKED',
                physical_acceptance='UNKNOWN', deployment_authorized=False,
                reason='PENDING_COORDINATOR_COMPLETE_PUBLIC_CHECKOUT',
                local_tests={'returncode': None, 'tests': 0, 'all_passed': False},
                public_tests={'returncode': None, 'tests': 0, 'all_passed': False})
    return save(root, STEM, data,
                'PREPARED source only; the complete local/public gate has not run.\n'
                'No passing-test, native image, hardware, cleanup or publication outcome is inferred.\n'
                'The coordinator must supply the complete clean public Git checkout and execute this gate.\n'
                'Native image emission remains BLOCKED / NOT_EXECUTED; physical acceptance UNKNOWN.\n')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--public-root', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    prepare = args.prepare_only or args.public_root is None
    data = write_prepared(args.root) if prepare else build(args.root, args.public_root)
    print(json.dumps({key: data[key] for key in ('status', 'all_gates_passed', 'local_tests',
                                               'public_tests', 'packaging_readiness')}, indent=2))
    return 0 if prepare or data['all_gates_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
