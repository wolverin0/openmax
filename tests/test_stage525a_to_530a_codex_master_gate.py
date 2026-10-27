"""Current held-file contracts; final530 receipt is checked after its creation."""
from pathlib import Path
import pytest
from tools.verify import verify_stage530a_codex_530stage_master_gate as m
from tools.autoresearch import build_stage529a_500stage_cross_lane_artifact_integrity_gate as scanner


@pytest.mark.parametrize('stage',list(m.STAGES))
def test_current_stage_implementation_dependency_document_and_boundary(stage):
    row=m.stage_evidence(m.ROOT,stage)
    assert row['stage']==f'{stage}A' and row['summary']['new_hardware_results']==0


@pytest.mark.parametrize('doc',[p[2] for p in m.STAGES.values()]+[m.DOC])
def test_six_compact_initial_paired_headers(doc):
    data=(m.ROOT/doc).read_text(encoding='utf-8')
    findings=scanner.markdown_policy(data)
    assert findings['findings']==[], (doc,findings)


def test_all_seven_explicit_suites_and_no_receipt_self_cycle():
    assert len(m.SUITES)==7 and len(set(m.SUITES))==7
    assert all((m.ROOT/p).is_file() for p in m.SUITES)
    assert m.OUT not in m.INPUTS and m.SCRIPT in m.INPUTS
    assert m.GATE==['python','tools/verify/enforce_5pillar_research_gate.py','--check-repo']


def test_repository_findings_remain_explicit():
    r,_=m.h.json_source(m.ROOT,m.STAGES[529][1])
    if r['status']=='PASS_SCOPED_STRUCTURAL_POLICY':
        assert r['summary']['markdown_with_findings']==r['summary']['stage_json_with_findings']==0
    else:
        assert r['status']=='FAIL_OR_UNASSESSED_REPOSITORY_ARTIFACT_POLICY'
        assert any(r['summary'][k] for k in ('markdown_with_findings','stage_json_with_findings','scan_issues',
                                           'source_drift','unclassified_invalid_nonstage_json'))
    assert r['snapshot']['file_hashes_rechecked'] is True


def test_continuity_docs_are_compact_and_have_one_initial_header():
    for name in ('CURRENT_STATE.md','MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md','BENCH_PLAN.md'):
        text=(m.ROOT/'docs'/name).read_text(encoding='utf-8')
        assert len(text.splitlines())<250
        assert text.startswith('<!-- doc-head:')
        assert text.count('<!-- doc-head:')==text.count('<!-- /doc-head -->')==1
        assert '525' in text and '530' in text
