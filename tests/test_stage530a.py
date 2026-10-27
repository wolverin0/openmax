"""Disposable runner fixtures; no recursive pytest or repository scan."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest
from tools.verify import verify_stage530a_codex_530stage_master_gate as m


@pytest.fixture
def repo(tmp_path):
    for label in m.INPUTS:
        path = tmp_path/label; path.parent.mkdir(parents=True, exist_ok=True); path.write_text('fixture\n')
    for stage, (script, receipt, doc) in m.STAGES.items():
        r = dict(stage=f'{stage}A', implementation=m.h.snapshot(tmp_path, script)[1],
                 analysis_dependencies=[m.h.snapshot(tmp_path, p)[1] for p in m.DEPS[:3]],
                 outputs={doc: m.h.snapshot(tmp_path, doc)[1]},
                 boundary={k: False for k in ('target_access','network_access','target_commands_executed','physical_acceptance','flash_approved')},
                 status='FAIL_OR_UNASSESSED_REPOSITORY_ARTIFACT_POLICY' if stage == 529 else 'QUALIFIED_SAVED_EVIDENCE',
                 static_sources=[m.h.snapshot(tmp_path,m.DEPS[-1])[1]],
                 summary={'new_hardware_results': 0})
        m.c.write_json(tmp_path/receipt, r)
        review = dict(verdict='PASS_QUALIFIED', blocking_findings=[], frozen_review_files=[
            m.h.snapshot(tmp_path, p)[1] for p in (script, receipt, doc, f'tests/test_stage{stage}a.py')])
        m.c.write_json(tmp_path/f'artifacts/verification/stage{stage}a/independent_review.json', review)
    return tmp_path


def executor(mode='pass', gate_exit=0):
    def execute(command, root, timeout):
        if command == m.GATE:
            return dict(command=command, exit_code=gate_exit, stdout='fixture gate', stderr='', timed_out=False)
        path = Path(next(p.split('=',1)[1] for p in command if p.startswith('--junitxml=')))
        suites = ET.Element('testsuites'); suite = ET.SubElement(suites,'testsuite')
        labels = list(m.SUITES)
        if mode == 'partial': labels.pop()
        if mode == 'extra': labels.append('tests/unexpected.py')
        if mode == 'zero': labels = []
        for label in labels:
            case = ET.SubElement(suite,'testcase',file=label,name='fixture',classname='fixture')
            if mode == 'skip': ET.SubElement(case,'skipped')
            if mode == 'failure': ET.SubElement(case,'failure')
            if mode == 'missing_file': case.attrib.pop('file')
        suite.set('tests',str(len(labels)))
        if mode != 'no_junit': path.write_bytes(ET.tostring(suites))
        if mode == 'drift': (root/m.SUITES[0]).write_text('changed after tests')
        return dict(command=command, exit_code=None if mode == 'timeout' else 1 if mode == 'exit1' else 0,
                    stdout='fixture pytest', stderr='', timed_out=mode == 'timeout')
    return execute


def test_policy_findings_are_not_global_pass(repo):
    r = m.run(repo, execute=executor())
    assert r['status'] == 'VALIDATED_TOOLING_WITH_REPOSITORY_FINDINGS'
    assert r['pytest_counts'] == dict(tests=7,passed=7,failures=0,errors=0,skipped=0)
    assert r['gaps'] == [] and r['repo_gate']['exit_code'] == 0
    assert json.loads((repo/m.OUT).read_text()) == r
    assert r['physical_acceptance'].startswith('NOT_ASSESSED')


@pytest.mark.parametrize('mode', ['partial','extra','zero','skip','failure','missing_file','no_junit','timeout','exit1','drift'])
def test_runner_rejects_incomplete_or_failed_evidence(repo, mode):
    r = m.run(repo, execute=executor(mode))
    assert r['status'] == 'INCOMPLETE_OR_FAILED_LOCAL_EVIDENCE' and r['gaps']


def test_wiring_failure_is_separate(repo):
    r = m.run(repo, execute=executor(gate_exit=2))
    assert 'REPOSITORY_WIRING_GATE_FAILED' in r['gaps']


def test_missing_suite_never_invokes_children(repo):
    (repo/m.SUITES[-1]).unlink()
    def forbidden(*args): raise AssertionError('children must not run')
    r = m.run(repo, execute=forbidden)
    assert r['pytest_counts'] is None and 'MISSING_INPUTS_NO_CHILD_EXECUTION' in r['gaps']


@pytest.mark.parametrize('mutation', ['array','missing_blockers','blocking','missing_pin','unsafe_pin','drift'])
def test_review_fails_closed(repo, mutation):
    path = repo/m.REVIEWS[0]; review=json.loads(path.read_text())
    if mutation == 'array': review=[]
    elif mutation == 'missing_blockers': review.pop('blocking_findings')
    elif mutation == 'blocking': review['blocking_findings']=['must fix']
    elif mutation == 'missing_pin': review['frozen_review_files'].pop()
    elif mutation == 'unsafe_pin': review['frozen_review_files'][0]['path']='../outside'
    else: review['frozen_review_files'][0]['sha256']='0'*64
    m.c.write_json(path,review)
    assert m.reviewed(repo,525)['status'] != 'PASS_REVISION_BOUND_REVIEW'


def test_failures_are_preserved_between_invocations(repo):
    first=m.run(repo,execute=executor('failure')); second=m.run(repo,execute=executor())
    assert first['run_directory'] != second['run_directory']
    assert json.loads((repo/first['run_directory']/'result.json').read_text()) == first
    assert first['pytest_counts']['failures']==7 and second['pytest_counts']['failures']==0


def test_stale_stage_implementation_is_rejected(repo):
    (repo/m.STAGES[525][0]).write_text('new revision')
    with pytest.raises(ValueError,match='stale_implementation'): m.stage_evidence(repo,525)


def test_omitted_analysis_dependency_is_rejected(repo):
    path=repo/m.STAGES[525][1];r=json.loads(path.read_text());r['analysis_dependencies'].pop()
    m.c.write_json(path,r)
    with pytest.raises(ValueError,match='exact_three'):m.stage_evidence(repo,525)


def test_no_silent_boundary_upgrade(repo):
    path=repo/m.STAGES[525][1]; r=json.loads(path.read_text());r['boundary']['target_access']=True
    m.c.write_json(path,r)
    with pytest.raises(ValueError,match='boundary'):m.stage_evidence(repo,525)


@pytest.mark.parametrize('field', ['boundary','outputs'])
def test_malformed_containers_produce_retained_incomplete_result(repo,field):
    path=repo/m.STAGES[525][1];r=json.loads(path.read_text());r[field]=[];m.c.write_json(path,r)
    result=m.run(repo,execute=executor())
    assert result['status']=='INCOMPLETE_OR_FAILED_LOCAL_EVIDENCE'
    assert json.loads((repo/result['run_directory']/'result.json').read_text())==result


def test_declared_raw_source_drift_is_detected(repo):
    raw=repo/'held/raw.txt';raw.parent.mkdir();raw.write_text('before')
    path=repo/m.STAGES[525][1];r=json.loads(path.read_text());r['static_sources']=[m.h.snapshot(repo,'held/raw.txt')[1]]
    m.c.write_json(path,r)
    def execute(command,root,timeout):
        result=executor()(command,root,timeout)
        if command==m.GATE:raw.write_text('after')
        return result
    result=m.run(repo,execute=execute)
    assert 'held/raw.txt' in result['input_drift']


def test_source_changed_since_stage_cutoff_is_explicit_incomplete(repo):
    raw=repo/'held/raw.txt';raw.parent.mkdir();raw.write_text('before')
    path=repo/m.STAGES[525][1];r=json.loads(path.read_text());r['static_sources']=[m.h.snapshot(repo,'held/raw.txt')[1]]
    m.c.write_json(path,r);raw.write_text('after')
    result=m.run(repo,execute=executor())
    assert result['stage_source_drift_since_audit']
    assert 'SOURCE_DRIFT_SINCE_STAGE_AUDIT' in result['gaps']


def test_junit_dtd_rejected(tmp_path):
    path=tmp_path/'bad.xml';path.write_text('<!DOCTYPE testsuites><testsuites/>')
    with pytest.raises(ValueError,match='DTD'):m.junit_evidence(path)


def test_command_contract_and_budget(repo):
    calls=[]
    def execute(command,root,timeout):
        calls.append(command);return executor()(command,root,timeout)
    m.run(repo,execute=execute)
    assert calls[1]==['python','tools/verify/enforce_5pillar_research_gate.py','--check-repo']
    assert all(label in calls[0] for label in m.SUITES)
    assert 'addopts=' in calls[0] and 'junit_family=xunit1' in calls[0]
    assert m.OUT not in m.INPUTS and len(m.DOC_TEXT.splitlines())<220
    with pytest.raises(ValueError):m.run(repo,timeout=0,execute=execute)
