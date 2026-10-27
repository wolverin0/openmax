"""Offline988 gate acceptance/fault contracts; no fixture contacts a target."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from tools.verify import verify_stage988a_squashfs_watchdog_and_repo_hygiene_gate as gate
from tools.verify.stage779_822_offline_common import receipt, save, snapshot

ROOT = Path(__file__).resolve().parents[1]


def _manifest(root: Path) -> dict:
    names = ['99-fmx-pbe5ac-ptp', 'fmx_ptp_rollback_watchdog.sh',
             'fmx_pbe_lbe_runtime_transaction.sh'] + [f'fixture{i}.sh' for i in range(18)]
    members = []
    for name in names:
        path = root / gate.KIT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'#!/bin/sh\nexit 0\n')
        members.append(snapshot(root, gate.KIT + '/' + name))
    path = root / gate.MANIFEST
    path.write_text(''.join(row['sha256'] + '  ' + row['path'][len(gate.KIT)+1:] + '\n'
                            for row in members), encoding='ascii')
    return {'manifest': snapshot(root, gate.MANIFEST), 'members': members,
            'member_count': 21, 'binary_images_emitted': 0,
            'original_historical_receipts_repinned': False}


def _private_metadata() -> dict:
    prefix = gate.PRIVATE_PREFIX + 'fixture/'
    names = ['git_status_porcelain.z', 'git_index.z', 'git_ignored.z', 'git_untracked.z',
             'inventory.json', 'restore_map.json']
    return {'all_gates_passed': True, 'unrelated_dirty_work_preserved': True,
            'private_inventory_public_contents_emitted': False,
            'private_evidence_available_to_public_checkout': False,
            'audit': {'complete': True, 'index_unchanged': True,
                'index_signature_sha256': hashlib.sha256(b'').hexdigest(),
                'tracked_index_count': 0,
                'status_counts': dict(staged=0, unstaged=0, untracked=0, ignored=0)},
            'cleanup': {'mode': 'QUARANTINE', 'complete': True,
                'transaction_state': 'NO_PROVEN_ORPHANS', 'proven_orphans': 0,
                'quarantined': 0, 'retained_candidates': 0, 'failed': 0,
                'restored_after_failure': 0, 'irreversible_deletions': 0,
                'tracked_or_user_files_moved': 0, 'all_moves_within_bounds': True,
                'restore_map_retained': True},
            'private_evidence': [{'path': prefix + name, 'bytes': 0,
                 'sha256': hashlib.sha256(b'').hexdigest()} for name in names]}


def _fixture_stage(root: Path, stage=983) -> dict:
    if stage == 986:
        detail = _manifest(root)
    else:
        detail = {}
    for label in gate.EXPECTED_SOURCES[stage]:
        path = root / label
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text('# fixture source bytes only\n', encoding='utf-8')
    sources = [snapshot(root, label) for label in sorted(gate.EXPECTED_SOURCES[stage])]
    data = receipt(stage, 'Disposable gate parser fixture only', sources)
    data.update(evidence_provenance_class=gate.CLASS, physical_acceptance='UNKNOWN')
    if stage == 983:
        data.update(native_image_emission='NOT_EXECUTED', packaging_readiness='BLOCKED',
                    required_payload=gate.REQUIRED_PAYLOAD, qdisc_mode='auto',
                    vendor_signature_verified=False, source_only_release=True,
                    deployment_authorized=False, blockers=['REVIEWED_ACTIVE_BOOTSTRAP_REQUIRED'])
    elif stage in (984, 985, 986):
        data.update(all_gates_passed=True, tested_revision_unchanged=True, fresh_live_windows=0)
        if stage == 984:
            data.update(deadlines_s={'non-dfs': 45, 'dfs': 120}, default_mode='--dry-run',
                        qdisc_mode='auto', firmware_restore_authorized=False, flash_executed=False)
        if stage == 985:
            data.update(tests={'returncode': 0, 'tests': 1, 'passed': 1, 'failures': 0,
                              'errors': 0, 'skipped': 0, 'all_passed': True},
                        real_ping_executed=False, real_45_or_120_second_wait_executed=False)
        data.update(detail)
    elif stage == 987:
        data.update(_private_metadata())
    save(root, gate.STEMS[stage], data, 'Disposable metadata contract; no native proof.\n')
    return data


def _write(root, stage, data):
    (root / gate.artifact(stage)).write_text(json.dumps(data), encoding='utf-8')


@pytest.mark.parametrize('stage', range(983, 988))
def test_current_release_receipt_contract(stage):
    result = gate.audit_stage(ROOT, stage, public=True)
    assert result['compliant'], result


def test_current_source_manifest_contract():
    data = json.loads((ROOT / gate.artifact(986)).read_text())
    result = gate.audit_manifest(ROOT, data)
    assert result['compliant'], result


def test_missing_stage_is_not_software_acceptance(tmp_path):
    assert not gate.audit_stage(tmp_path, 983)['compliant']


def test_current_source_tamper_is_rejected(tmp_path):
    _fixture_stage(tmp_path)
    assert gate.audit_stage(tmp_path, 983)['compliant']
    (tmp_path / gate.GENERATOR).write_text('changed = True\n')
    assert not gate.audit_stage(tmp_path, 983)['compliant']


@pytest.mark.parametrize('change', [
    {'native_image_emission': 'EMITTED'}, {'packaging_readiness': 'READY'},
    {'vendor_signature_verified': True}, {'deployment_authorized': True},
    {'qdisc_mode': 'tc'}, {'required_payload': ['usr/sbin/fmx_ptp_rollback_watchdog.sh']},
    {'evidence_provenance_class': 'CONFIRMED_LIVE_HARDWARE'},
    {'physical_acceptance': 'CONFIRMED'}, {'blockers': []},
])
def test_blocked_factory_contract_cannot_be_promoted(tmp_path, change):
    data = _fixture_stage(tmp_path)
    data.update(change)
    _write(tmp_path, 983, data)
    assert not gate.audit_stage(tmp_path, 983)['compliant']


@pytest.mark.parametrize('change', [
    {'deadlines_s': {'non-dfs': 44, 'dfs': 120}},
    {'deadlines_s': {'non-dfs': 45, 'dfs': 45}}, {'default_mode': '--apply'},
    {'firmware_restore_authorized': True}, {'flash_executed': True},
    {'tested_revision_unchanged': False},
])
def test_watchdog_deadline_or_native_authority_tamper_rejects(tmp_path, change):
    data = _fixture_stage(tmp_path, 984)
    assert gate.audit_stage(tmp_path, 984)['compliant']
    data.update(change)
    _write(tmp_path, 984, data)
    assert not gate.audit_stage(tmp_path, 984)['compliant']


@pytest.mark.parametrize('counts', [
    {'returncode': False, 'tests': 1, 'passed': 1, 'failures': 0, 'errors': 0, 'skipped': 0, 'all_passed': True},
    {'returncode': 0, 'tests': 1, 'passed': 1, 'failures': 1, 'errors': 0, 'skipped': 0, 'all_passed': True},
    {'returncode': 0, 'tests': 2, 'passed': 1, 'failures': 0, 'errors': 0, 'skipped': 1, 'all_passed': True},
    {'returncode': 0, 'tests': 0, 'passed': 0, 'failures': 0, 'errors': 0, 'skipped': 0, 'all_passed': True},
])
def test_watchdog_proof_requires_actual_passing_test_summary(tmp_path, counts):
    data = _fixture_stage(tmp_path, 985)
    data['tests'] = counts
    _write(tmp_path, 985, data)
    assert not gate.audit_stage(tmp_path, 985)['compliant']


def test_checksum_value_and_membership_tamper_is_rejected(tmp_path):
    data = _manifest(tmp_path)
    assert gate.audit_manifest(tmp_path, data)['compliant']
    manifest = tmp_path / gate.MANIFEST
    manifest.write_text(manifest.read_text().replace(data['members'][0]['sha256'], '0'*64))
    data['manifest'] = snapshot(tmp_path, gate.MANIFEST)
    assert not gate.audit_manifest(tmp_path, data)['compliant']


def test_old_source_or_duplicate_checksum_member_cannot_be_relabelled(tmp_path):
    data = _manifest(tmp_path)
    (tmp_path / data['members'][0]['path']).write_bytes(b'#!/bin/sh\nchanged=true\n')
    assert not gate.audit_manifest(tmp_path, data)['compliant']
    data = _manifest(tmp_path)
    data['members'][1] = data['members'][0]
    assert not gate.audit_manifest(tmp_path, data)['compliant']


@pytest.mark.parametrize('key,value', [
    ('irreversible_deletions', 1), ('tracked_or_user_files_moved', 1),
    ('all_moves_within_bounds', False), ('restore_map_retained', False),
    ('transaction_state', 'ROLLBACK_FAILED'), ('mode', 'AUDIT_ONLY'),
    ('quarantined', 1), ('failed', 1),
])
def test_cleanup_cannot_certify_destructive_or_incomplete_actions(key, value):
    data = _private_metadata()
    assert not gate.hygiene_evidence_errors(ROOT, data, public=True)
    data['cleanup'][key] = value
    assert gate.hygiene_evidence_errors(ROOT, data, public=True)


def test_complete_private_proof_list_required_even_in_public_metadata():
    data = _private_metadata()
    data['private_evidence'] = []
    assert gate.hygiene_evidence_errors(ROOT, data, public=True)
    data = _private_metadata()
    data['private_evidence'][0]['path'] = '../outside'
    assert gate.hygiene_evidence_errors(ROOT, data, public=True)


def _git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def _init(root):
    root.mkdir(parents=True, exist_ok=True)
    _git(root, 'init', '-q')


def _private_capture(root):
    _init(root)
    data = _private_metadata()
    prefix = gate.PRIVATE_PREFIX + 'fixture/'
    directory = root / '.git' / prefix
    directory.mkdir(parents=True)
    status = b'M  source.py\0?? work.py\0'
    index = ('100644 ' + 'a'*40 + ' 0\tsource.py\0').encode()
    inventory = {'git_status': [{'status': 'M ', 'path': 'source.py'},
                                {'status': '??', 'path': 'work.py'}],
                 'tracked_paths': ['source.py'], 'ignored_paths': ['artifacts/cache.tmp'],
                 'untracked_paths': ['work.py'], 'candidates': [], 'reference_scan_complete': True}
    blobs = {'git_status_porcelain.z': status, 'git_index.z': index,
             'git_ignored.z': b'artifacts/cache.tmp\0', 'git_untracked.z': b'work.py\0',
             'inventory.json': json.dumps(inventory).encode(),
             'restore_map.json': json.dumps({'state': 'NO_PROVEN_ORPHANS', 'moves': [],
                                              'restored_after_failure': 0}).encode()}
    data['private_evidence'] = []
    for name, blob in blobs.items():
        (directory / name).write_bytes(blob)
        data['private_evidence'].append({'path': prefix + name, 'bytes': len(blob),
                                        'sha256': hashlib.sha256(blob).hexdigest()})
    data['audit'].update(index_signature_sha256=hashlib.sha256(index).hexdigest(),
                         tracked_index_count=1,
                         status_counts={'staged': 1, 'unstaged': 0, 'untracked': 1, 'ignored': 1})
    return data


def test_private_captured_counts_are_recomputed_not_trusted(tmp_path):
    data = _private_capture(tmp_path)
    assert not gate.hygiene_evidence_errors(tmp_path, data)
    data['audit']['status_counts']['untracked'] = 0
    errors = gate.hygiene_evidence_errors(tmp_path, data)
    assert any('counts/index signature mismatch' in reason for reason in errors)


def test_resealed_private_file_cannot_override_captured_index_signature(tmp_path):
    data = _private_capture(tmp_path)
    row = next(row for row in data['private_evidence'] if row['path'].endswith('git_index.z'))
    path = tmp_path / '.git' / row['path']
    blob = ('100644 ' + 'b'*40 + ' 0\tsource.py\0').encode()
    path.write_bytes(blob)
    row.update(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest())
    errors = gate.hygiene_evidence_errors(tmp_path, data)
    assert any('counts/index signature mismatch' in reason for reason in errors)


def test_private_restore_map_must_agree_with_public_quarantine_outcome(tmp_path):
    data = _private_capture(tmp_path)
    row = next(row for row in data['private_evidence'] if row['path'].endswith('restore_map.json'))
    path = tmp_path / '.git' / row['path']
    blob = json.dumps({'state': 'ROLLBACK_FAILED', 'moves': [], 'restored_after_failure': 0}).encode()
    path.write_bytes(blob)
    row.update(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest())
    assert any('restoration map/state mismatch' in reason
               for reason in gate.hygiene_evidence_errors(tmp_path, data))


def _quarantine_capture(root, data, original='artifacts/autoresearch/stage777a_summary.json.abcdefgh.tmp'):
    directory = root / '.git' / gate.PRIVATE_PREFIX / 'fixture'
    blob = b'{"schema_version":1,"stage":"777A"}\n'
    digest = hashlib.sha256(blob).hexdigest()
    (directory / 'quarantine').mkdir()
    (directory / 'quarantine/one.orphan').write_bytes(blob)
    inventory = json.loads((directory / 'inventory.json').read_text())
    inventory['ignored_paths'] = [original]
    inventory['candidates'] = [{'path': original, 'eligible': True, 'bytes': len(blob),
                               'sha256': digest, 'reason': 'proven_ignored_atomic_summary_orphan'}]
    restoration = {'state': 'QUARANTINED', 'restored_after_failure': 0,
                   'moves': [{'original_path': original, 'quarantine_path': 'quarantine/one.orphan',
                              'bytes': len(blob), 'sha256': digest}]}
    changed = {'git_ignored.z': (original+'\0').encode(),
               'inventory.json': json.dumps(inventory).encode(),
               'restore_map.json': json.dumps(restoration).encode()}
    for name, content in changed.items():
        (directory / name).write_bytes(content)
        row = next(row for row in data['private_evidence'] if row['path'].endswith('/'+name))
        row.update(bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
    data['cleanup'].update(transaction_state='QUARANTINED', proven_orphans=1, quarantined=1)


def test_actual_retained_quarantine_bytes_are_checked(tmp_path):
    data = _private_capture(tmp_path)
    _quarantine_capture(tmp_path, data)
    assert not gate.hygiene_evidence_errors(tmp_path, data)
    path = tmp_path / '.git' / gate.PRIVATE_PREFIX / 'fixture/quarantine/one.orphan'
    path.write_bytes(b'changed')
    assert any('quarantined bytes differ' in reason
               for reason in gate.hygiene_evidence_errors(tmp_path, data))


def test_claimed_zero_user_file_moves_cannot_hide_an_out_of_scope_move(tmp_path):
    data = _private_capture(tmp_path)
    _quarantine_capture(tmp_path, data, original='controller/user_file.py')
    assert data['cleanup']['tracked_or_user_files_moved'] == 0
    assert any('unbounded or unproved' in reason
               for reason in gate.hygiene_evidence_errors(tmp_path, data))


@pytest.mark.parametrize('mutation', ['index', 'source', 'none'])
def test_gate_pins_index_and_source_before_tests(tmp_path, monkeypatch, mutation):
    _init(tmp_path)
    code = tmp_path / 'code.py'
    code.write_bytes(b'checked=True\n')
    _git(tmp_path, 'add', 'code.py')
    monkeypatch.setattr(gate, 'audit_release', lambda *a, **k: {'compliant': True})
    monkeypatch.setattr(gate, 'audit_repo_deterministic_gates', lambda root: {'compliant': True})
    monkeypatch.setattr(gate, 'freeze_sources', lambda root: [snapshot(root, 'code.py')])
    monkeypatch.setattr(gate, 'index_hygiene', lambda *a: (
        {'compliant': True, 'findings_by_rule': {}}, [snapshot(tmp_path, 'code.py')]))
    monkeypatch.setattr(gate, 'check_export', lambda *a: {'compliant': True})
    calls = []
    def run_tests(root, logs, name):
        calls.append(name)
        if len(calls) == 1 and mutation == 'index':
            oid = subprocess.check_output(['git', 'hash-object', '-w', '--stdin'],
                                           cwd=tmp_path, input=b'untested=True\n').decode().strip()
            _git(tmp_path, 'update-index', '--cacheinfo', '100644,' + oid + ',code.py')
        elif len(calls) == 1 and mutation == 'source':
            code.write_bytes(b'untested=True\n')
        return {'returncode': 0, 'tests': 1, 'all_passed': True}
    monkeypatch.setattr(gate, 'run_tests', run_tests)
    result = gate.build(tmp_path, tmp_path / 'public')
    assert result['all_gates_passed'] is (mutation == 'none')
    if mutation == 'index':
        assert result['tested_revision_unchanged']
        assert not result['publication_index_unchanged']
    if mutation == 'source':
        assert not result['tested_revision_unchanged']


def test_preexisting_unstaged_source_mismatch_blocks_all_test_execution(tmp_path, monkeypatch):
    _init(tmp_path)
    path = tmp_path / 'code.py'
    path.write_bytes(b'old=True\n')
    _git(tmp_path, 'add', 'code.py')
    selected = [snapshot(tmp_path, 'code.py')]
    path.write_bytes(b'new_untested=True\n')
    monkeypatch.setattr(gate, 'audit_release', lambda *a, **k: {'compliant': True})
    monkeypatch.setattr(gate, 'audit_repo_deterministic_gates', lambda root: {'compliant': True})
    monkeypatch.setattr(gate, 'freeze_sources', lambda root: [snapshot(root, 'code.py')])
    monkeypatch.setattr(gate, 'index_hygiene', lambda *a: (
        {'compliant': True, 'findings_by_rule': {}}, selected))
    monkeypatch.setattr(gate, 'run_tests', lambda *a: pytest.fail('mismatching source may not start tests'))
    result = gate.build(tmp_path)
    assert not result['all_gates_passed']
    assert not result['indexed_tested_sources']['compliant']
    assert result['local_tests']['tests'] == 0


def test_cli_default_only_prepares_without_running_tests(monkeypatch):
    calls = []
    monkeypatch.setattr(gate.sys, 'argv', ['gate988'])
    def prepare(root):
        calls.append('prepare')
        return {'status': 'PREPARED', 'all_gates_passed': False,
                'local_tests': {'tests': 0}, 'public_tests': {'tests': 0},
                'packaging_readiness': 'BLOCKED'}
    monkeypatch.setattr(gate, 'write_prepared', prepare)
    monkeypatch.setattr(gate, 'build', lambda *a: pytest.fail('default must not execute gate'))
    assert gate.main() == 0
    assert calls == ['prepare']


def test_clean_export_rejects_extra_tracked_source(tmp_path):
    operator = tmp_path / 'operator'
    public = tmp_path / 'public'
    for root in (operator, public):
        _init(root)
        (root / 'code.py').write_bytes(b'checked=True\n')
        _git(root, 'add', 'code.py')
        _git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
             '-c', 'core.hooksPath=.git/fixture-hooks', 'commit', '-qm', 'fixture')
    selected = [snapshot(operator, 'code.py')]
    assert gate.check_export(operator, public, selected)['compliant']
    (public / 'extra.py').write_bytes(b'untested=True\n')
    _git(public, 'add', 'extra.py')
    _git(public, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
         '-c', 'core.hooksPath=.git/fixture-hooks', 'commit', '-qm', 'extra')
    assert not gate.check_export(operator, public, selected)['compliant']
