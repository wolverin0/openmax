"""Publication proof and local queue acceptance, without remote calls."""
from pathlib import Path
import pytest

from tools.verify import verify_stage830a_publication_and_ground_up_pytest_gate as gate
from tools.verify import stage779_822_offline_common as c

ROOT=Path(__file__).resolve().parents[1]


def test_publication_proof_rejects_unverified_or_different_commit():
    sha='1'*40
    tree='3'*40
    record=dict(stage='826A',status='CONFIRMED',phase='PUSH_VERIFIED',
                scope='actual Git index blobs only; prior history not rewritten',
                remote_url=gate.REMOTE,remote_ref='refs/heads/main',pushed_tree=tree,
                push_verified=True,compliant=True,pushed_commit=sha,remote_after_push=sha)
    assert gate.publication_proof(record,sha,tree)
    assert not gate.publication_proof(record,'2'*40,tree)
    assert not gate.publication_proof(record,sha,'4'*40)
    record['push_verified']=False
    assert not gate.publication_proof(record,sha,tree)


@pytest.mark.parametrize('value',[None,'',True,'main','g'*40,'a'*39])
def test_invalid_hash_cannot_establish_publication(value):
    assert not gate.publication_proof(dict(push_verified=True,compliant=True,pushed_commit=value),value,'1'*40)


@pytest.mark.parametrize('field,value',[('remote_url','https://example.invalid/other.git'),
                                      ('remote_ref','refs/heads/other'),('scope','working-tree publication plan')])
def test_wrong_remote_ref_or_plan_cannot_establish_publication(field,value):
    sha='1'*40;tree='2'*40
    record=dict(stage='826A',status='CONFIRMED',phase='PUSH_VERIFIED',
                scope='actual Git index blobs only; prior history not rewritten',
                remote_url=gate.REMOTE,remote_ref='refs/heads/main',pushed_tree=tree,
                push_verified=True,compliant=True,pushed_commit=sha,remote_after_push=sha)
    record[field]=value
    assert not gate.publication_proof(record,sha,tree)


def test_missing_checkout_fails_closed(tmp_path):
    result=gate.build(tmp_path)
    assert not result['compliant'] and not result['publication_verified']
    assert not result['index_hygiene_compliant']


def test_completed_local_gate():
    result=gate.build(ROOT)
    assert result['compliant'],result
    assert result['boundary']['physical_acceptance']=='UNKNOWN'
    assert result['publication_verified'] and result['index_hygiene_compliant']


def test_modeled_and_live_windows_stay_distinct():
    score=c.read_json(ROOT,'artifacts/autoresearch/stage827a_1000window_simpy_pymoo_master_scorecard.json')
    assert score['boundary']['network_access'] is False
    assert score['boundary']['physical_acceptance']=='UNKNOWN'
