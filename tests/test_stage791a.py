import pytest
from tools.verify import build_stage791a_800stage_horizon_readiness_audit as m


def dirs(root):
    for folder,_,_ in m.FOLDERS:(root/folder).mkdir(parents=True)


def test_800_filename_is_not_parsed_schema_or_accepted_experiment(tmp_path):
    dirs(tmp_path)
    (tmp_path/'artifacts/autoresearch/stage800a.json').write_text('broken json')
    (tmp_path/'docs/STAGE1A_SAMPLE.md').write_text('no header')
    (tmp_path/'tests/test_stage1b_sample.py').write_text('not executed')
    (tmp_path/'artifacts/autoresearch/stage801a.json').write_text('{}')
    r=m.catalog(tmp_path)
    assert r['numeric_ids_present']==[1,800] and r['stage_labels_present']==['1A','1B','800A']
    assert r['accepted_stage_count'] is None and r['receipt_schema_validity'].startswith('NOT_ASSESSED')
    assert not r['complete_manifest'] and r['above800_matched_files']==1
    assert 2 in r['numeric_ids_without_matching_basename']


def test_aggregate_suite_name_does_not_claim_all_internal_stage_coverage(tmp_path):
    dirs(tmp_path);(tmp_path/'tests/test_stage787a_to_792a_suite.py').write_text('')
    r=m.catalog(tmp_path)
    assert r['numeric_ids_present']==[787] and r['rows'][0]['role']=='TEST_BASENAME_NOT_FULL_COVERAGE'


@pytest.mark.parametrize('limit',['MAX_ENTRIES','MAX_FILES'])
def test_catalog_limits_are_explicit_incomplete(tmp_path,monkeypatch,limit):
    dirs(tmp_path);(tmp_path/'artifacts/autoresearch/stage1a.json').write_text('{}')
    monkeypatch.setattr(m,limit,0)
    assert m.catalog(tmp_path)['issues']


def test_missing_folders_remain_issues_not_empty_pass(tmp_path):
    assert len(m.catalog(tmp_path)['issues'])==3


def test_missing_receipts_fail_closed():
    with pytest.raises(ValueError):m.assess({}, {'issues':[]})


def test_current_readiness_is_qualified_hold_not800_accepted():
    r=m.h.json_source(m.h.snapshot(m.ROOT,m.OUT)[0])
    assert r['readiness']=='HOLD_EVIDENCE_GAPS' and r['milestone_acceptance']=='NOT_ACCEPTED'
    assert r['accepted_stage_count'] is None and not r['physical_promotion_authorized']
    assert not r['reused529_is_current_global_compliance']
    checks={row['question']:row for row in r['checks']}
    assert checks['Bench/tower DHCP eradication and persistence']['evidence']=='UNKNOWN_NOT_PROVEN'
    assert checks['Historical530 acceptance']['evidence']['failures']==2
    assert not any(r['boundary'].values()) and r['new_hardware_results']==0
    for pin in [r['implementation'],*r['analysis_dependencies'],r['outputs'][m.DOC]]:assert m.h.snapshot(m.ROOT,pin['path'])[1]==pin
    for s in r['static_sources']:assert m.h.snapshot(m.ROOT,s['frozen']['path'])[1]==s['frozen']
