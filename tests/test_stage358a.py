import json
from pathlib import Path
import pytest
from tools.verify import run_stage358a_ground_up_regression as m


def seed(root):
    for label in m.INPUTS:
        p = root/label; p.parent.mkdir(parents=True, exist_ok=True); p.write_text('unit fixture\n')
    for n, (script, receipt, doc) in m.STAGES.items():
        labels = [script, 'artifacts/autoresearch/'+receipt, 'docs/'+doc, f'tests/test_stage{n}a.py']
        p = root/f'artifacts/verification/stage{n}a/independent_review.json'; p.parent.mkdir(parents=True, exist_ok=True)
        m.c.write_json(p, {'verdict': 'PASS_FIXTURE', 'blocking_findings': [],
                          'reviewed_files': [m.c.binding(root/label, root) for label in labels]})


def fake_executor(*, skipped=0, exit_code=0, make_xml=True, mutation=None, complete=True):
    calls = []
    def execute(command, root, timeout):
        calls.append(command)
        arg = next((v for v in command if v.startswith('--junitxml=')), None)
        if arg and make_xml:
            cases = [f'<testcase name="fixture" file="{s}">'+('<skipped/>' if skipped else '')+'</testcase>' for s in m.SUITES]
            if not complete: cases = ['<testcase name="lost_collection"/>']
            text = f'<testsuite tests="{len(cases)}">'+''.join(cases)+'</testsuite>'
            Path(arg.split('=',1)[1]).write_text(text)
        if arg and mutation: mutation(root)
        return dict(command=command, exit_code=exit_code, stdout='fixture', stderr='', timed_out=False)
    return execute, calls


def test_fixed_scoped_commands_revision_reviews_and_exclusive_attempts(tmp_path):
    seed(tmp_path); execute, calls = fake_executor()
    first = m.run(tmp_path, execute=execute); second = m.run(tmp_path, execute=execute)
    assert first['status'] == second['status'] == 'PASS_LOCAL_TOOLING_ONLY'
    assert first['pytest_counts'] == dict(tests=7, passed=7, skipped=0, failures=0, errors=0)
    assert first['run_directory'] != second['run_directory']
    assert calls[1] == ['python','tools/verify/enforce_5pillar_research_gate.py','--check-repo']
    assert tuple(v for v in calls[0] if v in m.SUITES) == m.SUITES
    assert 'addopts=' in calls[0] and 'junit_family=xunit1' in calls[0]
    assert m.c.load(tmp_path/first['run_directory']/'result.json') == first
    assert not first['boundary']['target_access'] and not first['boundary']['physical_acceptance']


@pytest.mark.parametrize('kwargs', [{'skipped': 1}, {'exit_code': 1}, {'make_xml': False}])
def test_skip_failure_and_absent_junit_cannot_pass(tmp_path, kwargs):
    seed(tmp_path); execute, _ = fake_executor(**kwargs)
    assert m.run(tmp_path, execute=execute)['status'] == 'FAIL_LOCAL_REGRESSION'


def test_missing_suite_never_runs_unscoped_pytest(tmp_path):
    seed(tmp_path); (tmp_path/m.SUITES[0]).unlink(); execute, calls = fake_executor()
    result = m.run(tmp_path, execute=execute)
    assert not calls and result['status'] == 'INCOMPLETE_MISSING_INPUTS'
    assert m.SUITES[0] in result['missing_inputs']


def test_partially_collected_junit_cannot_claim_all_seven_suites(tmp_path):
    seed(tmp_path); execute, _ = fake_executor(complete=False)
    # One file-less case represents lost collection despite a nominal zero exit.
    assert m.run(tmp_path, execute=execute)['status'] == 'FAIL_LOCAL_REGRESSION'


def test_nonobject_review_is_incomplete_not_unrecorded_abort(tmp_path):
    seed(tmp_path)
    m.c.write_json(tmp_path/'artifacts/verification/stage353a/independent_review.json', [])
    assert m.review_status(tmp_path)[0]['status'] == 'MISSING_OR_INVALID'


def test_source_drift_and_stale_review_prevent_closure(tmp_path):
    seed(tmp_path)
    execute, _ = fake_executor(mutation=lambda root: (root/m.INPUTS[0]).write_text('changed'))
    r = m.run(tmp_path, execute=execute)
    assert r['status'] == 'INCOMPLETE_EVIDENCE' and m.INPUTS[0] in r['input_drift']
    assert 'MISSING_FAILED_OR_STALE_INDEPENDENT_REVIEW' in r['gaps']


@pytest.mark.parametrize('xml', ['<testsuite tests="0"/>',
    '<testsuite tests="2"><testcase/></testsuite>',
    '<!DOCTYPE testsuite><testsuite/>',
    '<testsuite><testcase><error/><skipped/></testcase></testsuite>'])
def test_junit_zero_or_inconsistent_evidence(tmp_path, xml):
    p = tmp_path/'j.xml'; p.write_text(xml)
    if 'tests="0"' in xml: assert m.junit_counts(p)['passed'] == 0
    else:
        with pytest.raises(ValueError): m.junit_counts(p)


def test_host_capture_errors_are_not_invented_exits(tmp_path, monkeypatch):
    def fail(*a, **k): raise OSError('unit unavailable')
    monkeypatch.setattr(m.subprocess, 'run', fail)
    result = m.capture(['fixture'], tmp_path, 1)
    assert result['exit_code'] is None and not result['timed_out']


def test_inherited_pytest_selection_and_plugins_are_removed(tmp_path, monkeypatch):
    monkeypatch.setenv('PYTEST_ADDOPTS', '--ignore=tests/test_stage353a.py')
    monkeypatch.setenv('PYTEST_PLUGINS', 'untrusted_plugin')
    def inspect(*a, **kwargs):
        assert 'PYTEST_ADDOPTS' not in kwargs['env'] and 'PYTEST_PLUGINS' not in kwargs['env']
        return type('Result', (), dict(returncode=0, stdout='', stderr=''))()
    monkeypatch.setattr(m.subprocess, 'run', inspect)
    assert m.capture(['fixture'], tmp_path, 1)['exit_code'] == 0


@pytest.mark.parametrize('value', [0, True, 901])
def test_timeout_domain(value, tmp_path):
    with pytest.raises(ValueError): m.run(tmp_path, timeout=value)
