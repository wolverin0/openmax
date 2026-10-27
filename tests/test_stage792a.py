import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest
from tools.verify import verify_stage792a_codex_787a_to_792a_gate as m

HEAD='<!-- doc-head: fixture -->\nFixture\n<!-- /doc-head -->\n'


@pytest.fixture
def repo(tmp_path):
    for label in m.INPUTS:
        p=tmp_path/label;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(HEAD if label.endswith('.md')else 'fixture\n')
    for stage,(script,receipt,doc)in m.STAGES.items():
        raw=tmp_path/f'raw{stage}.txt';raw.write_text('held')
        _,sources=m.h.freeze(tmp_path,stage,[raw.name])
        r=dict(stage=f'{stage}A',status='QUALIFIED_OFFLINE_FIXTURE',boundary=dict(m.h.BOUNDARY),new_hardware_results=0,
            implementation=m.h.snapshot(tmp_path,script)[1],outputs={doc:m.h.snapshot(tmp_path,doc)[1]},
            analysis_dependencies=[m.h.snapshot(tmp_path,p)[1]for p in m.h.DEPS],static_sources=sources)
        m.c.write_json(tmp_path/receipt,r)
        labels=(*m.STAGES[stage],f'tests/test_stage{stage}a.py',*m.h.DEPS,f'artifacts/verification/stage{stage}a/frozen_sources.json')
        review=dict(verdict='PASS_QUALIFIED',blocking_findings=[],reviewed_files=[m.h.snapshot(tmp_path,p)[1]for p in labels])
        m.c.write_json(tmp_path/f'artifacts/verification/stage{stage}a/independent_review.json',review)
    return tmp_path


def executor(mode='pass',gate_exit=0):
    def execute(command,root,timeout):
        if command==m.GATE:
            if mode=='origin_change':(root/'raw787.txt').write_text('origin changed')
            if mode=='frozen_change':
                r=m.h.json_source(m.h.snapshot(root,m.STAGES[787][1])[0]);(root/r['static_sources'][0]['frozen']['path']).write_text('corrupted')
            return dict(command=command,exit_code=gate_exit,stdout='fixture gate',stderr='',timed_out=False)
        xml=Path(next(x.split('=',1)[1]for x in command if x.startswith('--junitxml=')))
        tree=ET.Element('testsuites');suite=ET.SubElement(tree,'testsuite');labels=list(m.SUITES)
        if mode=='partial':labels.pop()
        if mode=='zero':labels=[]
        if mode=='extra':labels.append('tests/unexpected.py')
        for label in labels:
            case=ET.SubElement(suite,'testcase',file=label,name='fixture')
            if mode in ('failure','skipped','error'):ET.SubElement(case,mode)
            if mode=='missing_file':case.attrib.pop('file')
        suite.set('tests',str(len(labels)))
        if mode!='no_junit':xml.write_bytes(ET.tostring(tree))
        return dict(command=command,exit_code=None if mode=='timeout'else 1 if mode=='exit1'else 0,
                    stdout='fixture pytest',stderr='',timed_out=mode=='timeout')
    return execute


def test_local_gate_pass_is_not800_or_physical_acceptance(repo):
    r=m.run(repo,execute=executor())
    assert r['status']=='PASS_LOCAL_TOOLING_ONLY' and r['gaps']==[]
    assert r['pytest_counts']==dict(tests=7,passed=7,failures=0,errors=0,skipped=0)
    assert r['milestone800_acceptance']=='NOT_ACCEPTED' and r['readiness800']=='HOLD_EVIDENCE_GAPS'
    assert json.loads((repo/m.OUT).read_text())==r


@pytest.mark.parametrize('mode',['partial','zero','extra','failure','skipped','error','missing_file','no_junit','timeout','exit1','frozen_change'])
def test_incomplete_collection_failures_and_frozen_drift_fail_closed(repo,mode):
    r=m.run(repo,execute=executor(mode))
    assert r['status']=='INCOMPLETE_OR_FAILED_LOCAL_EVIDENCE' and r['gaps']


def test_origin_change_is_diagnostic_and_never_silently_repins_frozen_input(repo):
    original=m.h.snapshot(repo,m.STAGES[787][1])[1]
    r=m.run(repo,execute=executor('origin_change'))
    assert r['status']=='PASS_LOCAL_TOOLING_ONLY' and not r['input_drift']
    changes=r['origin_diagnostics_after_run'][0]['changes']
    assert changes[0]['status']=='CHANGED_SINCE_FROZEN_CUTOFF'
    assert m.h.snapshot(repo,m.STAGES[787][1])[1]==original


def test_missing_suite_does_not_start_unscoped_or_any_child(repo):
    (repo/m.SUITES[-1]).unlink()
    def forbidden(*args):raise AssertionError('must not execute children')
    assert 'MISSING_INPUTS_NO_CHILD_EXECUTION'in m.run(repo,execute=forbidden)['gaps']


@pytest.mark.parametrize('field',['boundary','outputs','analysis_dependencies','static_sources'])
def test_malformed_stage_containers_preserve_incomplete_result(repo,field):
    p=repo/m.STAGES[787][1];r=json.loads(p.read_text());r[field]=None;m.c.write_json(p,r)
    result=m.run(repo,execute=executor())
    assert result['status']=='INCOMPLETE_OR_FAILED_LOCAL_EVIDENCE'
    assert json.loads((repo/result['run_directory']/'result.json').read_text())==result


def test_boundary_false_is_typed_boolean_not_zero(repo):
    p=repo/m.STAGES[787][1];r=json.loads(p.read_text());r['boundary']['network_access']=0;m.c.write_json(p,r)
    with pytest.raises(ValueError,match='offline_boundary'):m.stage_evidence(repo,787)


@pytest.mark.parametrize('change',['missing_blockers','blocked','missing_pin','unsafe','stale','not_object'])
def test_review_requires_explicit_pass_current_pins_and_empty_blockers(repo,change):
    p=repo/m.REVIEWS[0];r=json.loads(p.read_text())
    if change=='missing_blockers':r.pop('blocking_findings')
    elif change=='blocked':r['blocking_findings']=['fix needed']
    elif change=='missing_pin':r['reviewed_files'].pop()
    elif change=='unsafe':r['reviewed_files'][0]['path']='../outside'
    elif change=='stale':r['reviewed_files'][0]['sha256']='0'*64
    else:r=[]
    m.c.write_json(p,r)
    assert m.review(repo,787)['status']!='PASS_REVISION_BOUND_REVIEW'


def test_manifest_mismatch_is_rejected(repo):
    p=repo/'artifacts/verification/stage787a/frozen_sources.json';r=json.loads(p.read_text());r['sources']=[];m.c.write_json(p,r)
    with pytest.raises(ValueError,match='manifest'):m.stage_evidence(repo,787)


def test_missing_frozen_manifest_never_runs_children_or_recreates_cutoff(repo):
    path=repo/'artifacts/verification/stage790a/frozen_sources.json';path.unlink()
    def forbidden(*args):raise AssertionError('invalid preflight must not run pytest or repin sources')
    result=m.run(repo,execute=forbidden)
    assert result['status']=='INCOMPLETE_OR_FAILED_LOCAL_EVIDENCE' and not path.exists()


def test_wiring_gate_failure_and_failed_run_history_are_preserved(repo):
    first=m.run(repo,execute=executor(gate_exit=2));second=m.run(repo,execute=executor())
    assert 'WIRING_GATE_FAILED'in first['gaps'] and second['status']=='PASS_LOCAL_TOOLING_ONLY'
    assert first['run_directory']!=second['run_directory']
    assert json.loads((repo/first['run_directory']/'result.json').read_text())==first


def test_xml_dtd_and_contract_rejections(tmp_path):
    p=tmp_path/'bad.xml';p.write_text('<!DOCTYPE testsuites><testsuites/>')
    with pytest.raises(ValueError):m.junit(p)
    for doc in ('no header',HEAD*2,HEAD+'x\n'*200):
        with pytest.raises(ValueError):m.document_contract(doc)


@pytest.mark.parametrize('where,attribute,value',[('suite','errors','1'),('empty','errors','1'),
    ('root','failures','1'),('suite','skipped','1'),('root','tests','8'),('suite','errors','-1')])
def test_contradictory_declared_junit_counts_are_not_silent_pass(tmp_path,where,attribute,value):
    root=ET.Element('testsuites');suite=ET.SubElement(root,'testsuite',tests='7',errors='0',failures='0',skipped='0')
    for label in m.SUITES:ET.SubElement(suite,'testcase',file=label,name='fixture')
    target=suite if where=='suite'else root if where=='root'else ET.SubElement(root,'testsuite',tests='0')
    target.set(attribute,value);path=tmp_path/'bad_counts.xml';path.write_bytes(ET.tostring(root))
    with pytest.raises(ValueError):m.junit(path)


def test_exact_command_scope_and_no_final_receipt_cycle(repo):
    calls=[]
    def execute(command,root,timeout):calls.append(command);return executor()(command,root,timeout)
    m.run(repo,execute=execute)
    assert calls[1]==['python','tools/verify/enforce_5pillar_research_gate.py','--check-repo']
    assert all(p in calls[0]for p in m.SUITES)and len(m.SUITES)==7
    assert 'addopts='in calls[0]and 'junit_family=xunit1'in calls[0]
    assert m.OUT not in m.INPUTS
