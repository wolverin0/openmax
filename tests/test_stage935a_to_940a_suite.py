"""Source-release contracts; no test launches a gate or contacts a target."""
import json
from pathlib import Path
import subprocess

import pytest

from tools.verify import verify_stage940a_public_release_v23_gate as gate
from tools.verify.stage779_822_offline_common import receipt, save, snapshot

ROOT = Path(__file__).resolve().parents[1]


def fixture_receipt(root, stage=935):
    source = root / 'source.py'
    source.write_text('value = 1\n', encoding='utf-8')
    data = receipt(stage, 'Disposable static software contract', [snapshot(root, 'source.py')])
    data.update(evidence_provenance_class=gate.CLASS, physical_acceptance='UNKNOWN')
    if stage == 936:
        data.update(all_gates_passed=True, tested_revision_unchanged=True,
                    tests={'returncode': 0, 'passed': 1, 'failures': 0, 'errors': 0,
                           'skipped': 0, 'all_passed': True})
    save(root, gate.STEMS[stage], data, 'Disposable source test only.\n')
    return data


def write_receipt(root, stage, data):
    (root / gate.artifact(stage)).write_text(json.dumps(data), encoding='utf-8')


@pytest.mark.parametrize('stage', range(935, 940))
def test_current_release_receipt_contract(stage):
    # Public checkout deliberately withholds historical archives; current source pins remain mandatory.
    result = gate.audit_stage(ROOT, stage, public=True)
    assert result['compliant'], result


def test_current_checksum_membership_matches_active_release():
    result = gate.audit_release(ROOT, public=True)
    assert result['compliant'], result


def test_missing_receipt_cannot_pass(tmp_path):
    result = gate.audit_stage(tmp_path, 935)
    assert not result['compliant']
    assert result['failures']


def test_source_tamper_and_deletion_fail_closed(tmp_path):
    fixture_receipt(tmp_path)
    assert gate.audit_stage(tmp_path, 935)['compliant']
    source = tmp_path / 'source.py'
    source.write_text('value = 2\n', encoding='utf-8')
    assert not gate.audit_stage(tmp_path, 935)['compliant']
    source.unlink()
    assert not gate.audit_stage(tmp_path, 935)['compliant']


@pytest.mark.parametrize('change', [
    {'status': 'CONFIRMED_LIVE_HARDWARE'},
    {'evidence_provenance_class': 'CONFIRMED_LIVE_HARDWARE'},
    {'physical_acceptance': 'CONFIRMED'},
    {'sources': []},
])
def test_forged_status_or_missing_provenance_rejected(tmp_path, change):
    data = fixture_receipt(tmp_path)
    data.update(change)
    write_receipt(tmp_path, 935, data)
    assert not gate.audit_stage(tmp_path, 935)['compliant']


def test_deployment_boundary_cannot_inherit_static_pass(tmp_path):
    data = fixture_receipt(tmp_path)
    data['boundary']['device_writes'] = True
    write_receipt(tmp_path, 935, data)
    result = gate.audit_stage(tmp_path, 935)
    assert not result['compliant']
    assert any('device_writes' in reason for reason in result['failures'])


@pytest.mark.parametrize('change', [
    {'all_gates_passed': False},
    {'tested_revision_unchanged': False},
    {'tests': {'returncode': 0, 'passed': 1, 'failures': 1, 'errors': 0,
               'skipped': 0, 'all_passed': True}},
    {'tests': {'returncode': False, 'passed': 1, 'failures': 0, 'errors': 0,
               'skipped': 0, 'all_passed': True}},
])
def test_adversarial_result_requires_real_zero_exit_and_no_failures(tmp_path, change):
    data = fixture_receipt(tmp_path, 936)
    assert gate.audit_stage(tmp_path, 936)['compliant']
    data.update(change)
    write_receipt(tmp_path, 936, data)
    assert not gate.audit_stage(tmp_path, 936)['compliant']


def test_only_explicit_historical_archives_may_be_withheld(tmp_path):
    source = {'path': 'firmware/ltu_safe_kit/public_release_v1/old.sh',
              'available': True, 'bytes': 3, 'sha256': '0' * 64}
    declared = {source['path']}
    assert gate.binding_matches(tmp_path, source, public=True,
                                withheld_paths=declared) == 'WITHHELD_HISTORICAL_ARCHIVE'
    with pytest.raises(ValueError, match='missing source'):
        gate.binding_matches(tmp_path, source, public=True)
    with pytest.raises(ValueError, match='missing source'):
        gate.binding_matches(tmp_path, source)
    source['path'] = 'firmware/ltu_safe_kit/active.sh'
    with pytest.raises(ValueError, match='missing source'):
        gate.binding_matches(tmp_path, source, public=True)


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def test_clean_checkout_with_extra_tracked_or_ignored_file_is_rejected(tmp_path):
    root = tmp_path / 'operator'
    public = tmp_path / 'public'
    root.mkdir(); public.mkdir()
    git(public, 'init', '-q')
    git(public, 'config', 'user.name', 'Disposable Test')
    git(public, 'config', 'user.email', 'test@example.invalid')
    (public / 'safe.py').write_bytes(b'value=1\n')
    (public / '.gitignore').write_text('ignored.py\n')
    git(public, 'add', 'safe.py', '.gitignore')
    git(public, 'commit', '-qm', 'fixture')
    selected = [snapshot(public, label) for label in ('safe.py', '.gitignore')]
    assert gate.check_export(root, public, selected)['compliant']
    (public / 'extra.py').write_text('untested=True\n')
    git(public, 'add', 'extra.py')
    git(public, 'commit', '-qm', 'extra')
    result = gate.check_export(root, public, selected)
    assert result['clean_git_checkout'] and not result['exact_index_membership']
    assert not result['compliant']
    # Even a Git-ignored Python source can shadow imports and must be rejected.
    selected.append(snapshot(public, 'extra.py'))
    (public / 'ignored.py').write_text('untested=True\n')
    assert not gate.check_export(root, public, selected)['compliant']


@pytest.fixture
def mocked_build(tmp_path, monkeypatch):
    """A passing software run with isolated sources and explicit mutation hooks."""
    from types import SimpleNamespace
    root = tmp_path / 'operator'; root.mkdir()
    public = tmp_path / 'public'; public.mkdir()
    input_path = root / 'private_measurement.json'
    input_path.write_text('{"value":1}\n')
    private_binding = snapshot(root, 'private_measurement.json')
    code = root / 'source.py'; code.write_text('value=1\n')
    source = snapshot(root, 'source.py')
    labels = {gate.SELF, *gate.TESTS, 'tools/verify/stage779_822_offline_common.py',
              'tools/verify/verify_stage826a_public_git_hygiene_and_push_gate.py',
              'tools/verify/enforce_5pillar_research_gate.py', 'README.md', 'docs/PUBLIC_OVERVIEW.md'}
    for n in gate.STEMS:
        path = root / gate.artifact(n)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {'sources': [source]}
        if n == 938:
            data['private_input_bindings'] = [private_binding]
        path.write_text(json.dumps(data))
        labels.add(f'docs/{gate.STEMS[n].upper()}.md')
    for label in labels:
        path = root / label
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('fixture\n')
    state = {'index': 'initial', 'mutate_private': False, 'mutate_index': False}
    monkeypatch.setattr(gate, 'audit_release', lambda *args, **kwargs: {'compliant': True})
    monkeypatch.setattr(gate, 'audit_repo_deterministic_gates', lambda *args: {'compliant': True})
    monkeypatch.setattr(gate, 'index_hygiene', lambda *args: ({'compliant': True, 'findings_by_rule': {}}, []))
    monkeypatch.setattr(gate, 'check_export', lambda *args: {'compliant': True})
    monkeypatch.setattr(gate, 'index_revision', lambda *args: state['index'])
    monkeypatch.setattr(gate, 'measurement_evidence_errors', lambda *args, **kwargs: [])
    monkeypatch.setattr(gate, 'subprocess', SimpleNamespace(
        check_output=lambda *args, **kwargs: str(root / '.git')))
    def tests(where, logs, name):
        if where == root:
            if state['mutate_private']:
                input_path.write_text('{"value":2}\n')
            if state['mutate_index']:
                state['index'] = 'different'
        return {'returncode': 0, 'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0, 'all_passed': True}
    monkeypatch.setattr(gate, 'run_tests', tests)
    return root, public, state


def test_index_only_mutation_during_pytest_is_not_a_tested_revision(mocked_build):
    root, public, state = mocked_build
    state['mutate_index'] = True
    result = gate.build(root, public)
    assert result['local_tests']['all_passed'] and result['public_tests']['all_passed']
    assert result['tested_revision_unchanged']
    assert not result['index_revision_unchanged']
    assert not result['all_gates_passed']


def test_private_measurement_input_mutation_during_tests_rejects_release(mocked_build):
    root, public, state = mocked_build
    state['mutate_private'] = True
    result = gate.build(root, public)
    assert result['tested_revision_unchanged'] and result['index_revision_unchanged']
    assert not result['private_original_inputs_unchanged']
    assert not result['all_gates_passed']


def test_unchanged_complete_isolated_run_can_pass(mocked_build):
    root, public, _ = mocked_build
    result = gate.build(root, public)
    assert result['tested_revision_unchanged'] and result['index_revision_unchanged']
    assert result['private_original_inputs_unchanged']
    assert result['all_gates_passed']


def native_discovery_fixture(root):
    """A tiny acquired-byte fixture, not evidence about an actual device."""
    from tools.observability.build_stage937a_to_939a_public_v23_evidence_and_manifests import evidence_ledger
    data = fixture_receipt(root, 938)
    capture = root / 'artifacts/verification/stage905a/capture.json'
    capture.parent.mkdir(parents=True)
    capture.write_text(json.dumps({'results': [{'exit_code': 0, 'timed_out': False}]}))
    source = root / 'artifacts/autoresearch/stage905a_fixture.json'
    source.write_text(json.dumps({'stage': '905A', 'evidence_provenance_class': 'CONFIRMED_LIVE_HARDWARE',
                      'native_captures': [snapshot(root, capture.relative_to(root).as_posix())]}))
    data.update(evidence_ledger(root))
    write_receipt(root, 938, data)
    return data, capture


def test_verified_native_claims_require_complete_original_input_bindings(tmp_path):
    data, _ = native_discovery_fixture(tmp_path)
    assert gate.audit_stage(tmp_path, 938)['compliant']
    data['private_input_bindings'] = []
    write_receipt(tmp_path, 938, data)
    assert not gate.audit_stage(tmp_path, 938)['compliant']
    assert gate.measurement_evidence_errors(tmp_path, data, public=True)


def test_local_measurement_audit_replays_raw_capture_chain(tmp_path):
    data, capture = native_discovery_fixture(tmp_path)
    assert not gate.measurement_evidence_errors(tmp_path, data, public=False)
    # The original905 receipt bytes remain unchanged; only its bound raw capture changes.
    binding = data['private_input_bindings'][0]
    capture.write_text(json.dumps({'results': [{'exit_code': 1, 'timed_out': False}]}))
    assert snapshot(tmp_path, binding['path']) == binding
    assert gate.measurement_evidence_errors(tmp_path, data, public=False)
    # Public metadata validation honestly does not pretend to possess/replay private raw captures.
    assert not gate.measurement_evidence_errors(tmp_path, data, public=True)


def checksum_fixture(tmp_path):
    folder = tmp_path / 'firmware/ltu_safe_kit'
    folder.mkdir(parents=True)
    (folder / 'active.sh').write_bytes(b'#!/bin/sh\nexit 0\n')
    member = snapshot(tmp_path, 'firmware/ltu_safe_kit/active.sh')
    manifest = folder / 'SHA256SUMS'
    manifest.write_text(member['sha256'] + '  active.sh\n', encoding='ascii')
    descriptor = snapshot(tmp_path, 'firmware/ltu_safe_kit/SHA256SUMS')
    descriptor['members'] = [member]
    return descriptor


def test_checksum_file_and_member_bytes_are_checked_independently(tmp_path):
    descriptor = checksum_fixture(tmp_path)
    assert gate.validate_checksums(tmp_path, descriptor) == {'firmware/ltu_safe_kit/active.sh'}
    (tmp_path / descriptor['members'][0]['path']).write_bytes(b'changed\n')
    with pytest.raises(ValueError, match='source drift'):
        gate.validate_checksums(tmp_path, descriptor)


def test_rehashing_manifest_cannot_hide_extra_member(tmp_path):
    descriptor = checksum_fixture(tmp_path)
    path = tmp_path / descriptor['path']
    path.write_text(path.read_text() + '0' * 64 + '  rogue.sh\n', encoding='ascii')
    updated = snapshot(tmp_path, descriptor['path'])
    updated['members'] = descriptor['members']
    with pytest.raises(ValueError, match='membership'):
        gate.validate_checksums(tmp_path, updated)


@pytest.mark.parametrize('text', [
    '<testsuites/>',
    '<testsuites><testsuite><testcase><skipped/></testcase></testsuite></testsuites>',
    '<testsuites><testsuite><testcase><failure/></testcase></testsuite></testsuites>',
    '<invalid',
])
def test_empty_skipped_failed_or_invalid_junit_is_not_acceptance(tmp_path, text):
    path = tmp_path / 'pytest.xml'
    path.write_text(text)
    assert not gate.pytest_summary(path, 0)['all_passed']


def test_junit_success_does_not_override_failing_process(tmp_path):
    path = tmp_path / 'pytest.xml'
    path.write_text('<testsuites><testsuite><testcase/></testsuite></testsuites>')
    assert gate.pytest_summary(path, 0)['all_passed']
    assert not gate.pytest_summary(path, 1)['all_passed']


def test_document_budget_requires_one_paired_initial_header():
    text = '<!-- doc-head: fixture -->\n<!-- /doc-head -->\n# Fixture\n'
    assert gate.document_contract(text)
    assert not gate.document_contract('prefix\n' + text)
    assert not gate.document_contract(text + '<!-- doc-head: another -->\n')
    assert not gate.document_contract(text + '\n' * 180)
