import pytest
from tools.verify import verify_stage792a_codex_787a_to_792a_gate as m


@pytest.mark.parametrize('stage',list(m.STAGES))
def test_five_stage_receipts_code_docs_dependencies_and_frozen_manifests(stage):
    row=m.stage_evidence(m.ROOT,stage)
    assert row['stage']==f'{stage}A' and row['physical_acceptance']=='NOT_ASSESSED'


@pytest.mark.parametrize('doc',[p[2]for p in m.STAGES.values()]+[m.DOC])
def test_six_documents_under200_and_single_initial_paired_header(doc):
    result=m.document_contract(m.h.snapshot(m.ROOT,doc)[0].decode('utf-8'))
    assert result['lines']<200 and result['initial_paired_head']


def test_seven_explicit_suites_with_final_receipt_checked_after_creation():
    assert len(m.SUITES)==len(set(m.SUITES))==7 and all((m.ROOT/p).is_file()for p in m.SUITES)
    assert m.OUT not in m.INPUTS


def test_research_unknowns_are_not_promoted_by_the_regression_gate():
    receipts={n:m.h.json_source(m.h.snapshot(m.ROOT,p[1])[0])for n,p in m.STAGES.items()}
    assert not receipts[787]['model']['empirical_calibration']
    assert receipts[788]['evidence']['native_subframe_pointer']is None
    assert receipts[789]['eradication_verdict']=='UNKNOWN_NOT_PROVEN'
    assert receipts[790]['empirical_outage_rate_bound']is None
    assert receipts[791]['readiness']=='HOLD_EVIDENCE_GAPS' and receipts[791]['accepted_stage_count']is None
    assert all(not any(r['boundary'].values())for r in receipts.values())


def test_continuity_compact_and_updated():
    for name in ('CURRENT_STATE.md','MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md','BENCH_PLAN.md'):
        text=(m.ROOT/'docs'/name).read_text(encoding='utf-8')
        assert len(text.splitlines())<250 and text.startswith('<!-- doc-head:')
        assert text.count('<!-- doc-head:')==text.count('<!-- /doc-head -->')==1
        assert '787' in text and '792' in text
