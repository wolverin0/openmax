import json
from pathlib import Path
import subprocess
import pytest
from tools.verify import run_stage268a_release_regression as m


def test_combined_ranges_and_outside_stages():
    assert m.stages_in_name('test_stage241a_to_246a_x.py')==set(range(241,247))
    assert m.stages_in_name('test_stage269a.py')==set()


def test_catalog_missing_is_not_pass(tmp_path):
    p=tmp_path/'tests';p.mkdir();(p/'test_stage263a_only.py').write_text('def test_x(): pass\n')
    result=m.catalog(tmp_path)
    assert result['covered_stage_numbers']==[263] and 231 in result['missing_stage_numbers']
    assert len(result['suites'][0]['sha256'])==64


def test_junit_counts_failures_errors_skips(tmp_path):
    path=tmp_path/'junit.xml'
    path.write_text('<testsuites><testsuite tests="10" failures="2" errors="1" skipped="3"/></testsuites>')
    assert m.junit_counts(path)=={'tests':10,'failures':2,'errors':1,'skipped':3,'passed':4}


def test_timeout_is_recorded_without_fake_exit(monkeypatch,tmp_path):
    def fail(*args,**kwargs):raise subprocess.TimeoutExpired(args[0],1,output=b'partial')
    monkeypatch.setattr(m.subprocess,'run',fail)
    result=m.capture(['python','-m','pytest'],tmp_path,1)
    assert result['exit_code'] is None and result['timed_out'] and result['stdout']=='partial'


def test_capture_uses_argv_without_shell(monkeypatch,tmp_path):
    def fake(command,**kwargs):
        assert kwargs['shell'] is False and command==['python','--version']
        return subprocess.CompletedProcess(command,0,'Python','')
    monkeypatch.setattr(m.subprocess,'run',fake)
    assert m.capture(['python','--version'],tmp_path,1)['exit_code']==0


def test_real_catalog_is_bounded_and_includes_this_pure_suite():
    result=m.catalog(Path(__file__).resolve().parents[1])
    assert any(r['path']=='tests/test_stage268a_full_release_regression.py' for r in result['suites'])
    assert all(231<=n<=268 for n in result['covered_stage_numbers'])
    assert not any('269' in r['path'] for r in result['suites'])


def test_empty_catalog_never_invokes_unscoped_pytest(monkeypatch,tmp_path):
    calls=[]
    def fake(command,root,timeout):
        calls.append(command)
        assert command==['python','tools/verify/enforce_5pillar_research_gate.py','--check-repo']
        return {'command':command,'exit_code':0,'stdout':'','stderr':'','timed_out':False}
    monkeypatch.setattr(m,'capture',fake)
    r=m.run(tmp_path)
    assert len(calls)==1 and not r['summary']['all_available_tests_passed']
    run=json.loads((tmp_path/'artifacts/verification/stage268a/run_1/pytest.json').read_text())
    assert run['stderr']=='NO_SCOPED_SUITES' and run['exit_code'] is None


def test_all_skipped_never_counts_as_pass(monkeypatch,tmp_path):
    p=tmp_path/'tests/test_stage263a_docs_budget_audit.py';p.parent.mkdir();p.write_text('def test_x(): pass\n')
    def fake(command,root,timeout):
        if '-m' in command:
            Path(command[-1]).write_text('<testsuites><testsuite tests="1" failures="0" errors="0" skipped="1"/></testsuites>')
        return {'command':command,'exit_code':0,'stdout':'','stderr':'','timed_out':False}
    monkeypatch.setattr(m,'capture',fake)
    r=m.run(tmp_path)
    assert r['summary']['pytest']['passed']==0
    assert not r['summary']['all_available_tests_passed']
    assert not r['summary']['full_requested_range_accepted']
