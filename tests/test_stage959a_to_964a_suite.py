"""Offline release contracts plus real raw-capture fault paths; no target access."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import socket
import subprocess

import pytest

from tools.verify import verify_stage964a_unified_physical_runner_gate as gate
from tools.verify.stage779_822_offline_common import receipt, save, snapshot

ROOT = Path(__file__).resolve().parents[1]


def fixture_receipt(root: Path, stage=959):
    labels = sorted(gate.SHARED | ({gate.CONTROLLERS[stage]} if stage in gate.CONTROLLERS else set()))
    for label in labels:
        path = root / label
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('# Disposable source-binding fixture only.\n')
    data = receipt(stage, 'Disposable source contract', [snapshot(root, p) for p in labels])
    data.update(evidence_provenance_class=gate.CLASS, physical_acceptance='UNKNOWN')
    if stage == 959:
        data.update(required_phases=gate.PHASES, raw_window_sha256=True, gatekeeper_direct=True,
                    acquisition_default='INSPECT_ONLY', live_campaign_executed=False,
                    deployment_authorized=False)
    save(root, gate.STEMS[stage], data, 'Source-binding fixture; no acquisition.\n')
    return data


def overwrite(root, stage, data):
    (root / gate.artifact(stage)).write_text(json.dumps(data), encoding='utf-8')


@pytest.mark.parametrize('stage', range(959, 964))
def test_current_source_contract(stage):
    result = gate.audit_stage(ROOT, stage)
    assert result['compliant'], result


def test_missing_receipt_cannot_pass(tmp_path):
    result = gate.audit_release(tmp_path)
    assert not result['compliant']
    assert len(result['stage_audits']) == 5


def test_source_drift_and_missing_source_fail_closed(tmp_path):
    data = fixture_receipt(tmp_path)
    assert gate.audit_stage(tmp_path, 959)['compliant']
    victim = tmp_path / data['sources'][0]['path']
    victim.write_text('Changed source bytes.\n')
    assert not gate.audit_stage(tmp_path, 959)['compliant']
    victim.unlink()
    assert not gate.audit_stage(tmp_path, 959)['compliant']


@pytest.mark.parametrize('change', [
    {'status': 'CONFIRMED_LIVE_HARDWARE'}, {'evidence_provenance_class': 'CONFIRMED_LIVE_HARDWARE'},
    {'physical_acceptance': 'CONFIRMED'}, {'sources': []},
    {'required_phases': ['AB_DISCOVERY']}, {'acquisition_default': 'EXECUTE'},
    {'live_campaign_executed': True}, {'deployment_authorized': True},
])
def test_forged_provenance_and_shortcuts_rejected(tmp_path, change):
    data = fixture_receipt(tmp_path)
    data.update(change)
    overwrite(tmp_path, 959, data)
    assert not gate.audit_stage(tmp_path, 959)['compliant']


def test_source_dependencies_cannot_be_replaced_with_unrelated_hashes(tmp_path):
    data = fixture_receipt(tmp_path)
    data['sources'] = data['sources'][:1]
    overwrite(tmp_path, 959, data)
    assert not gate.audit_stage(tmp_path, 959)['compliant']


def test_duplicate_source_declaration_rejected(tmp_path):
    data = fixture_receipt(tmp_path)
    data['sources'].append(data['sources'][0])
    overwrite(tmp_path, 959, data)
    assert not gate.audit_stage(tmp_path, 959)['compliant']


def test_offline_boundary_is_not_inherited_from_static_provenance(tmp_path):
    data = fixture_receipt(tmp_path)
    data['boundary']['device_writes'] = True
    overwrite(tmp_path, 959, data)
    assert not gate.audit_stage(tmp_path, 959)['compliant']


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def repo(root):
    root.mkdir()
    git(root, 'init', '-q')
    git(root, 'config', 'user.name', 'Offline Test')
    git(root, 'config', 'user.email', 'test@example.invalid')
    git(root, 'config', 'core.filemode', 'false')
    (root / 'source.py').write_text('value=1\n')
    git(root, 'add', 'source.py')
    git(root, '-c', 'core.hooksPath=.git/test-hooks', 'commit', '-qm', 'fixture')


def test_public_checkout_requires_exact_membership_and_modes(tmp_path):
    first, public = tmp_path / 'first', tmp_path / 'public'
    repo(first); repo(public)
    selected = [snapshot(first, 'source.py')]
    assert gate.check_export(first, public, selected)['compliant']
    (public / 'extra.py').write_text('raise RuntimeError("extra executable source")\n')
    git(public, 'add', 'extra.py')
    git(public, '-c', 'core.hooksPath=.git/test-hooks', 'commit', '-qm', 'extra')
    assert not gate.check_export(first, public, selected)['compliant']


def test_public_checkout_rejects_mode_only_divergence(tmp_path):
    first, public = tmp_path / 'first', tmp_path / 'public'
    repo(first); repo(public)
    selected = [snapshot(first, 'source.py')]
    git(public, 'update-index', '--chmod=+x', 'source.py')
    git(public, '-c', 'core.hooksPath=.git/test-hooks', 'commit', '-qm', 'mode')
    assert not gate.check_export(first, public, selected)['compliant']


def mocked_gate_inputs(tmp_path, monkeypatch):
    root = tmp_path / 'release'
    repo(root)
    monkeypatch.setattr(gate, 'audit_release', lambda root: {'compliant': True})
    monkeypatch.setattr(gate, 'audit_repo_deterministic_gates', lambda root: {'compliant': True})
    monkeypatch.setattr(gate, 'freeze_sources', lambda root: [snapshot(root, 'source.py')])
    monkeypatch.setattr(gate, 'index_hygiene', lambda root, logs: (
        {'compliant': True, 'findings_by_rule': {}}, [snapshot(root, 'source.py')]))
    monkeypatch.setattr(gate, 'check_export', lambda *args: {'compliant': True})
    return root


def passing_tests(*args):
    return {'all_passed': True, 'tests': 1, 'returncode': 0,
            'failures': 0, 'errors': 0, 'skipped': 0}


def test_local_success_without_public_execution_is_not_release_pass(tmp_path, monkeypatch):
    root = mocked_gate_inputs(tmp_path, monkeypatch)
    monkeypatch.setattr(gate, 'run_tests', passing_tests)
    result = gate.build(root)
    assert result['local_tests']['all_passed']
    assert not result['all_gates_passed']
    assert result['status'] == 'FAILED'


def test_index_only_change_during_tests_cannot_inherit_success(tmp_path, monkeypatch):
    root = mocked_gate_inputs(tmp_path, monkeypatch)
    calls = []
    def mutate_index(run_root, logs, name):
        calls.append(name)
        if name == 'stage964_local':
            changed = root / 'new.py'
            changed.write_text('untested_source = True\n')
            git(root, 'add', 'new.py')
        return passing_tests()
    monkeypatch.setattr(gate, 'run_tests', mutate_index)
    result = gate.build(root, tmp_path / 'public')
    assert result['local_tests']['all_passed'] and result['public_tests']['all_passed']
    assert result['tested_revision_unchanged']
    assert not result['publication_index_unchanged']
    assert not result['all_gates_passed']


def test_working_source_change_during_tests_is_rejected(tmp_path, monkeypatch):
    root = mocked_gate_inputs(tmp_path, monkeypatch)
    def mutate_source(run_root, logs, name):
        if name == 'stage964_local':
            (root / 'source.py').write_text('untested = True\n')
        return passing_tests()
    monkeypatch.setattr(gate, 'run_tests', mutate_source)
    result = gate.build(root, tmp_path / 'public')
    assert result['local_tests']['all_passed'] and result['public_tests']['all_passed']
    assert not result['tested_revision_unchanged']
    assert not result['all_gates_passed']


def test_preexisting_unstaged_source_cannot_inherit_public_pass(tmp_path, monkeypatch):
    root = mocked_gate_inputs(tmp_path, monkeypatch)
    indexed_source = snapshot(root, 'source.py')
    (root / 'source.py').write_text('unstaged_new_revision = True\n')
    monkeypatch.setattr(gate, 'index_hygiene', lambda root, logs: (
        {'compliant': True, 'findings_by_rule': {}}, [indexed_source]))
    def forbidden_tests(*args):
        pytest.fail('an unindexed local revision must fail before pytest execution')
    monkeypatch.setattr(gate, 'run_tests', forbidden_tests)
    result = gate.build(root, tmp_path / 'public')
    assert not result['indexed_tested_sources']['compliant']
    assert not result['all_gates_passed']


def test_every_release_source_requires_a_matching_indexed_blob():
    pin = {'path': 'source.py', 'available': True, 'bytes': 1, 'sha256': 'a'*64}
    assert gate.pins_match_index([pin], [pin])['compliant']
    assert not gate.pins_match_index([pin], [])['compliant']
    assert not gate.pins_match_index([pin], [{**pin, 'sha256': 'b'*64}])['compliant']


@pytest.fixture
def deny_acquisition(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('only synthetic local acquisition bytes are authorized')
    monkeypatch.setattr(socket, 'create_connection', deny)
    monkeypatch.setattr(socket.socket, 'connect', deny)
    monkeypatch.setattr(subprocess, 'Popen', deny)


@pytest.mark.usefixtures('deny_acquisition')
def test_actual_runner_inspection_has_no_acquisition(tmp_path):
    from tools.autoresearch import run_stage959a_unified_physical_retest_runner as runner
    from tests.test_stage959a_unified_physical_runner import fixture_plan
    def denied(spec):
        pytest.fail('inspection acquired a native window')
    result = runner.run_campaign(fixture_plan(), acquire_window=denied, evidence_root=tmp_path)
    assert result['status'] == 'PLANNED'
    assert result['callbacks_invoked'] == 0
    assert not result['deployment_authorized']


@pytest.mark.usefixtures('deny_acquisition')
def test_actual_runner_hashes_every_window_without_physical_promotion(tmp_path):
    from tools.autoresearch import run_stage959a_unified_physical_retest_runner as runner
    from tests.test_stage959a_unified_physical_runner import fixture_plan, make_fixture_acquirer
    plan = fixture_plan()
    result = runner.run_campaign(plan, acquire_window=make_fixture_acquirer(plan),
                                 evidence_root=tmp_path, execute=True)
    assert result['status'] == 'SYNTHETIC_DIAGNOSTIC_COMPLETE', result
    assert result['completed_phases'] == gate.PHASES
    assert not result['promotion_eligible'] and not result['deployment_authorized']
    assert result['physical_acceptance'] == 'UNKNOWN'
    for row in result['raw_windows']:
        assert hashlib.sha256((tmp_path / row['path']).read_bytes()).hexdigest() == row['sha256']


@pytest.mark.usefixtures('deny_acquisition')
@pytest.mark.parametrize('fault', ['empty_ping', 'iperf_error', 'hash_drift',
                                  'copied_holdout', 'overlap'])
def test_actual_raw_faults_cannot_create_physical_promotion(tmp_path, fault):
    from tools.autoresearch import run_stage959a_unified_physical_retest_runner as runner
    from tests.test_stage959a_unified_physical_runner import fixture_plan, make_fixture_acquirer
    plan = fixture_plan()
    result = runner.run_campaign(plan, acquire_window=make_fixture_acquirer(
        plan, fault=fault, evidence_root=tmp_path), evidence_root=tmp_path, execute=True)
    assert result['status'] == 'FAILED_CLOSED', result
    assert not result['promotion_eligible'] and not result['deployment_authorized']
    assert 'AB_HOLDOUT' not in result['completed_phases']
