from tools.verify.verify_stage854a_ground_up_v14_854stage_gate import audit_release, pytest_summary


def test_absent_receipts_do_not_pass(tmp_path):
    result = audit_release(tmp_path)
    assert not result['all_artifacts_ok']
    assert not result['target_met']
    assert len(result['stage_audits']) == 5


def test_missing_pytest_evidence_is_failure(tmp_path):
    assert not pytest_summary(tmp_path / 'absent.xml', 0)['all_passed']


def test_skip_is_not_full_acceptance(tmp_path):
    xml = tmp_path / 'result.xml'
    xml.write_text('<testsuites><testsuite><testcase><skipped/></testcase></testsuite></testsuites>')
    assert not pytest_summary(xml, 0)['all_passed']


def test_fresh_test_success_required(tmp_path):
    xml = tmp_path / 'result.xml'
    xml.write_text('<testsuites><testsuite><testcase/></testsuite></testsuites>')
    assert pytest_summary(xml, 0)['all_passed']
    assert not pytest_summary(xml, 1)['all_passed']


def test_mutation_during_pytest_cannot_be_pinned_as_tested(tmp_path, monkeypatch):
    import json
    from pathlib import Path
    from types import SimpleNamespace
    from tools.verify import verify_stage854a_ground_up_v14_854stage_gate as gate
    from tools.verify import verify_stage853a_public_git_sync_and_push_v2 as publication
    from tools.verify.stage779_822_offline_common import snapshot
    from tools.verify.stage849_854_release_common import artifact
    code = tmp_path / 'code.py'
    code.write_text('tested = True\n')
    for n in range(849, 854):
        path = tmp_path / artifact(n)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'sources': [snapshot(tmp_path, 'code.py')]}))
    monkeypatch.setattr(gate, 'publication_paths', lambda: ['code.py'])
    monkeypatch.setattr(gate, 'audit_release', lambda root: {'all_artifacts_ok': True})
    monkeypatch.setattr(gate, 'audit_repo_deterministic_gates', lambda root: {'compliant': True})
    monkeypatch.setattr(publication, 'check_index', lambda root: {'compliant': True, 'findings_by_rule': {}})
    def during_pytest(command, **kwargs):
        xml = Path(next(a.split('=', 1)[1] for a in command if a.startswith('--junitxml=')))
        xml.write_text('<testsuites><testsuite><testcase/></testsuite></testsuites>')
        code.write_text('untested = True\n')
        return SimpleNamespace(returncode=0, stdout='1 passed', stderr='')
    monkeypatch.setattr(gate, 'subprocess', SimpleNamespace(run=during_pytest,
        check_output=lambda *args, **kwargs: str(tmp_path / '.git')))
    result = gate.build(tmp_path)
    assert result['pytest']['all_passed']
    assert not result['tested_revision_unchanged']
    assert not result['all_gates_passed']
    assert result['status'] == 'FAILED'
