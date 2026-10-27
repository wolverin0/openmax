"""Meaningful offline regression checks; never import the Stage779A SSH runner."""
import json
from pathlib import Path
import zipfile

import pytest

from tools.verify import stage779_822_offline_common as c
from tools.firmware import build_stage781a_cross_fleet_champion_bundle_v58 as bundle
from tools.sim import run_stage782a_guarida_32cpe_ani_and_napi_pareto as sim
from tools.observability import build_stage783a_memorymaster_264w_v58_ledger as ledger
from tools.verify import verify_stage784a_multi_radio_264w_v58_gate as gate

ROOT = Path(__file__).resolve().parents[1]


def test_prerequisites_are_source_only_or_simulated():
    assert (ROOT / bundle.SOURCES[0]).is_file()
    source = (ROOT / bundle.SOURCES[0]).read_text(encoding='utf-8')
    assert 'paramiko' in source  # explicitly never execute this prerequisite in this lane
    model = c.read_json(ROOT, 'artifacts/autoresearch/stage780a_nsga3_pareto_ani_immunity_and_irq52_napi.json')
    assert model['execution_mode'] == 'OFFLINE_SIMULATION'
    assert model['five_pillar_audit']['compliant']
    assert model['physical_acceptance'] == 'UNKNOWN'


def test_bundle_bytes_and_missing_evidence_are_honest(tmp_path):
    for label in bundle.SOURCES:
        if '779a_multi_radio_264w_milestone_campaign.json' in label:
            continue
        path = tmp_path / label; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'fixture\n')
    data = bundle.build(tmp_path)
    assert len(data['missing_sources']) == 1
    assert data['new_live_windows'] == 0
    assert data['runtime_activation'].startswith('BLOCKED')
    with zipfile.ZipFile(tmp_path / data['package']['path']) as archive:
        for item in data['sources']:
            if item['available']:
                assert archive.read(item['path']) == (tmp_path / item['path']).read_bytes()
    assert bundle.build(tmp_path)['package']['sha256'] == data['package']['sha256']


def test_pareto_and_topology():
    assert sum(p['provisioned'] for p in sim.TOPOLOGY) == 32
    assert sum(p['active'] for p in sim.TOPOLOGY) == 31
    rows = [dict(x=0,y=1), dict(x=1,y=0), dict(x=2,y=2)]
    assert c.pareto(rows, ('x','y')) == rows[:2]
    assert sim.model(4,480,48,80)['loss_pct'] > sim.model(2,480,48,80)['loss_pct']
    with pytest.raises(ValueError):
        sim.model(5,480,48,80)


def test_ledger_requires_inputs_and_never_claims_ingestion(tmp_path):
    with pytest.raises(ValueError):
        ledger.build(tmp_path)
    for label in ledger.SOURCES:
        path = tmp_path / label; path.parent.mkdir(parents=True, exist_ok=True); path.write_text('{}')
    data = ledger.build(tmp_path)
    assert data['ingestion_status'] == 'NOT_INGESTED'
    assert data['measured_windows_added'] == 0


def test_gate_rejects_missing_artifacts_and_source_tampering(tmp_path):
    assert not gate.build(tmp_path)['compliant']
    script, test, stem = 'tools/x.py', 'tests/x.py', 'stage781a_fixture'
    for label in [script,test,'data/input.txt']:
        p=tmp_path/label;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('original')
    c.save(tmp_path, stem, c.receipt(781,'fixture',[c.snapshot(tmp_path,'data/input.txt')]), 'fixture\n')
    assert c.verify_stage(tmp_path,781,script,stem,test)['compliant']
    (tmp_path/'data/input.txt').write_text('tampered')
    assert not c.verify_stage(tmp_path,781,script,stem,test)['compliant']


def test_repository_gate_and_docs():
    result = gate.build(ROOT)
    assert result['compliant'], result['stages_verified']
    assert result['physical_acceptance'] == 'UNKNOWN'
    for row in result['stages_verified']:
        assert row['doc_lines'] < 180 and row['doc_heads'] == 1


@pytest.mark.parametrize('field,value', [('network_access',True),('physical_acceptance','CONFIRMED')])
def test_gate_rejects_incompatible_offline_evidence(tmp_path,field,value):
    for label in ['tools/x.py','tests/x.py']:
        p=tmp_path/label;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
    data=c.receipt(781,'fixture',[]);data['boundary'][field]=value
    c.save(tmp_path,'stage781a_fixture',data,'fixture\n')
    result=c.verify_stage(tmp_path,781,'tools/x.py','stage781a_fixture','tests/x.py')
    assert not result['compliant'], result


def test_missing_source_is_qualified_and_duplicate_json_rejected(tmp_path):
    for label in ['tools/x.py','tests/x.py']:
        p=tmp_path/label;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
    c.save(tmp_path,'stage781a_fixture',c.receipt(781,'fixture',[
        dict(path='absent.json',status='MISSING')]),'fixture\n')
    assert c.verify_stage(tmp_path,781,'tools/x.py','stage781a_fixture','tests/x.py')['compliant']
    (tmp_path/'duplicate.json').write_text('{"status":1,"status":2}')
    with pytest.raises(ValueError):
        c.read_json(tmp_path,'duplicate.json')


def test_explicit_offline_boundary_and_source_digest_required(tmp_path):
    for label in ['tools/x.py','tests/x.py','source.txt']:
        p=tmp_path/label;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
    data=c.receipt(781,'fixture',[dict(path='source.txt',available=True)])
    c.save(tmp_path,'stage781a_fixture',data,'fixture\n')
    result=c.verify_stage(tmp_path,781,'tools/x.py','stage781a_fixture','tests/x.py')
    assert 'source hash required: source.txt' in result['failures']
    data['sources']=[c.snapshot(tmp_path,'source.txt')];del data['boundary']
    c.save(tmp_path,'stage781a_fixture',data,'fixture\n')
    result=c.verify_stage(tmp_path,781,'tools/x.py','stage781a_fixture','tests/x.py')
    assert 'explicit offline network boundary required' in result['failures']


@pytest.mark.parametrize('label',['../escape','/absolute','C:/host','a/../b','a\\b'])
def test_local_paths_only(tmp_path,label):
    with pytest.raises(ValueError):
        c.local(tmp_path,label)
