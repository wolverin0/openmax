import json
from pathlib import Path
import pytest
from tools.autoresearch import build_stage529a_500stage_cross_lane_artifact_integrity_gate as m

HEAD='<!-- doc-head: fixture -->\nSummary.\n<!-- /doc-head -->\n'


def put(root,label,data):
    p=root/label;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(data if isinstance(data,bytes) else data.encode());return p


def test_all_repository_locations_and_generic_stage_declarations(tmp_path):
    put(tmp_path,'research/stage9a_receipt.json',json.dumps({'stage':'9A','summary':{}}))
    put(tmp_path,'firmware/unusual.json',json.dumps({'meta':{'stage':'10A'}}))
    put(tmp_path,'outside_docs/guide.md',HEAD)
    put(tmp_path,'normal_config.json',json.dumps({'stage':'development','version':1}))
    put(tmp_path,'.git/stage99a_hidden.json','not json')
    r=m.audit(tmp_path)
    assert r['summary']['stage_json_candidates']==2 and r['summary']['markdown_files']==1
    assert r['summary']['nonstage_json_examined']==1
    assert r['status']=='PASS_SCOPED_STRUCTURAL_POLICY'
    assert r['declared_numeric_stage_ids']==[9,10] and r['snapshot']['excluded_directory_counts']=={'.git':1}


@pytest.mark.parametrize('text,code',[(HEAD+'\n<!-- doc-head: body -->','SINGLE_DOC_HEAD_AT_LINE1_REQUIRED'),
    (HEAD.replace('<!-- /doc-head -->\n',''),'SINGLE_INITIAL_PAIRED_CLOSE_REQUIRED'),
    ('\n'+HEAD,'SINGLE_DOC_HEAD_AT_LINE1_REQUIRED'),
    (HEAD+'\n'+'line\n'*216,'LINE_BUDGET_GE220')])
def test_actual_header_and_line_violations(text,code):
    assert code in m.markdown_policy(text)['findings']


def test_code_examples_not_misclassified_as_active_headers():
    text=HEAD+'\n```markdown\n<!-- doc-head: example -->\n<!-- /doc-head -->\n```\nUse `<!-- doc-head: inline -->` here.\n'
    assert not m.markdown_policy(text)['findings']
    assert not m.markdown_policy(HEAD+'x\n'*216)['findings']
    assert 'LINE_BUDGET_GE220' in m.markdown_policy(HEAD+'x\n'*217)['findings']


@pytest.mark.parametrize('raw',['{"stage":"7A","stage":"7A"}','{"stage":"7A","x":NaN}',
    '{"stage":"7A","x":1e999}','{broken'])
def test_stage_json_strict_duplicate_nonfinite_and_syntax(tmp_path,raw):
    put(tmp_path,'artifacts/stage7a_bad.json',raw)
    r=m.audit(tmp_path)
    assert r['summary']['stage_json_with_findings']==1
    assert r['stage_json_inventory'][0]['schema']['kind']=='INVALID_JSON'
    assert r['status']!='PASS_SCOPED_STRUCTURAL_POLICY'


def test_schema_identity_conflict_underspecified_suffix_and_unknown_shapes():
    assert not m.json_schema({'stage':'7A'},'stage7_legacy.json')['findings']
    assert 'FILENAME_DECLARED_STAGE_CONFLICT' in m.json_schema({'stage':'8A'},'stage7a_bad.json')['findings']
    assert 'DECLARED_STAGE_CONFLICT' in m.json_schema({'stage':'7A','meta':{'stage':'7B'}},'stage7_notes.json')['findings']
    assert 'STATIC_SOURCES_NOT_ARRAY' in m.json_schema({'stage':'7A','static_sources':{}},'stage7a_bad.json')['findings']
    assert 'EXIT_CODE_NOT_INT_OR_NULL' in m.json_schema({'command':['fixture'],'exit_code':True},'capture.json')['findings']
    assert not m.json_schema({'command':['fixture'],'exit_code':None},'capture.json')['findings']
    assert m.json_schema([1,2],'stage7a_data.json')['kind']=='UNASSESSED_DATA'


def test_unclassified_or_unknown_schema_never_becomes_scientific_pass(tmp_path):
    put(tmp_path,'stage6a_raw.json','{"arbitrary":[1,2]}')
    put(tmp_path,'generic_unknown.json','{broken')
    r=m.audit(tmp_path)
    assert r['summary']['unclassified_invalid_nonstage_json']==1
    assert r['stage_json_inventory'][0]['schema']['kind']=='UNASSESSED_OBJECT_SCHEMA'
    assert r['status']!='PASS_SCOPED_STRUCTURAL_POLICY'


@pytest.mark.parametrize('limit',['MAX_BYTES','MAX_FILE','MAX_ENTRIES','MAX_FILES'])
def test_bounds_are_explicit_incomplete_coverage(tmp_path,monkeypatch,limit):
    put(tmp_path,'docs/stage1a.md',HEAD)
    monkeypatch.setattr(m,limit,0)
    r=m.audit(tmp_path)
    assert r['scan_issues'] and r['status']!='PASS_SCOPED_STRUCTURAL_POLICY'


def test_source_drift_is_retained_without_replacing_captured_hash(tmp_path,monkeypatch):
    p=put(tmp_path,'docs/guide.md',HEAD);original=m.read_bounded;calls=0
    def change(path,**kwargs):
        nonlocal calls
        data=original(path,**kwargs);calls+=1
        if calls==1:p.write_text(HEAD+'changed\n')
        return data
    monkeypatch.setattr(m,'read_bounded',change)
    r=m.audit(tmp_path)
    assert r['source_drift']==['docs/guide.md']
    assert r['markdown_inventory'][0]['sha256']==m.c.sha(HEAD.encode())
    assert r['status']!='PASS_SCOPED_STRUCTURAL_POLICY'


def test_third_party_archived_roles_and_explicit_self_exclusion(tmp_path):
    put(tmp_path,'repos/upstream/README.md','upstream content\n')
    put(tmp_path,'docs/archive/old.md','old content\n')
    put(tmp_path,m.OUT,'not-yet-a-receipt')
    r=m.audit(tmp_path)
    assert {x['role'] for x in r['markdown_inventory']}=={'THIRD_PARTY_REFERENCE','ARCHIVED_REFERENCE'}
    assert r['summary']['markdown_with_findings']==2 and r['summary']['stage_json_candidates']==0
    assert r['snapshot']['self_exclusion']==[m.OUT]


def test_current_report_is_qualified_audit_not_all_stages_accepted():
    r=m.c.load(m.ROOT/m.OUT)
    assert not any(r['boundary'].values()) and r['summary']['new_hardware_results']==0
    assert r['summary']['stage_json_candidates']>500 and r['summary']['markdown_files']>500
    assert r['snapshot']['file_hashes_rechecked']
    for p in r['static_sources']+r['analysis_dependencies']:assert m.c.binding(m.ROOT/p['path'],m.ROOT)==p
    doc=(m.ROOT/m.DOC).read_text(encoding='utf-8')
    assert len(doc.splitlines())<220 and doc.count('<!-- doc-head:')==doc.count('<!-- /doc-head -->')==1


def test_malformed_close_with_extra_text_is_not_an_initial_paired_header():
    text=HEAD.replace('<!-- /doc-head -->','prefix <!-- /doc-head --> suffix')
    assert m.markdown_policy(text)['findings']


def test_indented_fence_cannot_hide_active_body_head():
    text=HEAD+'\n    ```\n<!-- doc-head: body -->\n'
    assert 'SINGLE_DOC_HEAD_AT_LINE1_REQUIRED' in m.markdown_policy(text)['findings']


def test_fence_with_trailing_text_is_not_a_closing_fence():
    text=HEAD+'\n```\n```still_code\n<!-- doc-head: sample -->\n```\n'
    assert not m.markdown_policy(text)['findings']


def test_scandir_is_bounded_before_materialization(tmp_path,monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(m,'MAX_ENTRIES',2)
    class Entries:
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def __iter__(self):
            for i in range(100):
                if i>2:pytest.fail('scandir consumed beyond bounded sentinel entry')
                yield SimpleNamespace(name=f'{i}.txt',path=str(tmp_path/f'{i}.txt'),stat=lambda **kw:SimpleNamespace(st_mode=m.stat.S_IFREG,st_file_attributes=0))
    monkeypatch.setattr(m.os,'scandir',lambda p:Entries())
    _,issues,_=m.enumerate_files(tmp_path)
    assert any(x['reason']=='ENTRY_LIMIT' for x in issues)


def test_recheck_reads_share_the_explicit_total_budget(tmp_path,monkeypatch):
    body='{"stage":"1A"}';put(tmp_path,'stage1a.json',body);put(tmp_path,'doc.md',HEAD)
    monkeypatch.setattr(m,'MAX_BYTES',len(body.encode())+len(HEAD.encode()))
    r=m.audit(tmp_path)
    assert r['status']!='PASS_SCOPED_STRUCTURAL_POLICY'
    assert any(x['reason']=='RECHECK_READ_BUDGET' for x in r['scan_issues'])
    assert r['snapshot']['read_bytes']<=m.MAX_BYTES
    assert not r['snapshot']['file_hashes_rechecked']


def test_invalid_utf8_markdown_retains_byte_binding(tmp_path):
    data=b'\xff\xfe';put(tmp_path,'invalid.md',data)
    r=m.audit(tmp_path)
    assert r['markdown_inventory'][0]['sha256']==m.c.sha(data)
    assert r['markdown_inventory'][0]['findings']==['UTF8_DECODE_ERROR']


def test_empty_scope_does_not_pass(tmp_path):
    assert m.audit(tmp_path)['status']!='PASS_SCOPED_STRUCTURAL_POLICY'


@pytest.mark.parametrize('body', ['```bad` <!-- doc-head: body -->\n', '\\`<!-- doc-head: body -->\\`\n'])
def test_invalid_fence_or_escaped_backtick_cannot_hide_body_header(body):
    assert 'SINGLE_DOC_HEAD_AT_LINE1_REQUIRED' in m.markdown_policy(HEAD+body)['findings']


def test_local_path_guard_precedes_initial_and_recheck_stat(tmp_path,monkeypatch):
    p=put(tmp_path,'doc.md',HEAD); original=m.c.local_path;calls=[]
    def guard(path):
        if path==p:calls.append('guard')
        return original(path)
    monkeypatch.setattr(m.c,'local_path',guard)
    monkeypatch.setattr(m,'read_bounded',lambda path,**kw:path.read_bytes())
    monkeypatch.setattr(m,'enumerate_files',lambda root:([p],[],{}))
    m.audit(tmp_path)
    assert calls==['guard','guard']
