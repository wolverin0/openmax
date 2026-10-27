"""Adversarial evidence and checksum fixtures; no transports or native actions."""
import hashlib
import json
from pathlib import Path
import socket
import subprocess

import pytest

from tools.observability import build_stage937a_to_939a_public_v23_evidence_and_manifests as s


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def denied(*args,**kwargs):
        raise AssertionError('external execution or network forbidden')
    monkeypatch.setattr(socket,'create_connection',denied)
    monkeypatch.setattr(subprocess,'run',denied)


def write(root,label,data):
    path=root/label
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data),encoding='utf-8')
    return s.c.snapshot(root,label)


def test_missing_stage_stays_missing(tmp_path):
    row,pin=s.evaluate_stage(tmp_path,930)
    assert row['state']=='MISSING' and pin is None
    assert not row['native_observation_verified']


@pytest.mark.parametrize('declared',['CONFIRMED','SIMULATED_MODEL_ONLY','CONFIRMED_STATIC_BINARY'])
def test_status_or_non_native_class_cannot_become_measurement(tmp_path,declared):
    write(tmp_path,'artifacts/autoresearch/stage930a_fake.json',
          dict(stage='930A',status='CONFIRMED',evidence_provenance_class=declared,goodput_mbps=999))
    row,_=s.evaluate_stage(tmp_path,930)
    assert row['state']=='NON_NATIVE_OR_UNCLASSIFIED'
    assert not row['native_observation_verified'] and 'observation' not in row


def test_hardware_label_without_primary_input_cannot_pass(tmp_path):
    write(tmp_path,'artifacts/autoresearch/stage905a_fake.json',
          dict(stage='905A',status='CONFIRMED',evidence_provenance_class='CONFIRMED_LIVE_HARDWARE',
               native_captures=[dict(path='private/missing.json',bytes=1,sha256='0'*64)]))
    row,_=s.evaluate_stage(tmp_path,905)
    assert row['state']=='INVALID_OR_UNAVAILABLE_NATIVE_EVIDENCE'
    assert not row['native_observation_verified'] and 'observation' not in row


def test_forged_capture_hash_is_rejected(tmp_path):
    pin=write(tmp_path,'private/capture.json',{'results':[]})
    (tmp_path/pin['path']).write_text('{"results": [1]}')
    with pytest.raises(ValueError,match='hash_mismatch'):
        s.binding(tmp_path,pin)


def test_unknown_future_native_declaration_is_unverified(tmp_path):
    write(tmp_path,'artifacts/autoresearch/stage934a_fake.json',
          dict(stage='934A',evidence_provenance_class='CONFIRMED_LIVE_HARDWARE',goodput_mbps=999))
    row,_=s.evaluate_stage(tmp_path,934)
    assert row['state']=='UNVERIFIED_NATIVE_DECLARATION'
    assert 'observation' not in row


def test_manifest_rejects_stale_source_pin(tmp_path):
    members=[]
    sources=[]
    for index in range(42):
        folder=s.KIT_DIRS[index%2]
        label=f'{folder}/fixture{index}.sh'
        path=tmp_path/label;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('#!/bin/sh\nexit 65\n')
        members.append(label);sources.append(s.c.snapshot(tmp_path,label))
    write(tmp_path,s.KIT_RECEIPT,dict(release_source_members=members,sources=sources))
    (tmp_path/members[0]).write_text('#!/bin/sh\nexit 0\n')
    with pytest.raises(ValueError,match='changed_or_invalid'):
        s.source_manifests(tmp_path)


def test_manifest_contains_only_actual42_source_bytes(tmp_path):
    members=[]
    sources=[]
    for index in range(42):
        label=f'{s.KIT_DIRS[index%2]}/fixture{index}.sh'
        path=tmp_path/label;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('#!/bin/sh\nexit 65\n')
        members.append(label);sources.append(s.c.snapshot(tmp_path,label))
    write(tmp_path,s.KIT_RECEIPT,dict(release_source_members=members,sources=sources))
    manifests=s.source_manifests(tmp_path)
    assert sum(len(row['members']) for row in manifests)==42
    for manifest in manifests:
        folder=Path(manifest['path']).parent
        for line in (tmp_path/manifest['path']).read_text().splitlines():
            expected,label=line.split('  ',1)
            assert hashlib.sha256((tmp_path/folder/label).read_bytes()).hexdigest()==expected


def test_doc_update_is_bounded_and_preserves_qualification():
    original='<!-- doc-head: old -->\n<!-- /doc-head -->\n\n# Existing\n\nImported old claim; UNKNOWN.\n'
    block='No physical acceptance.\n'
    once=s.update_document(original,block,readme=True)
    assert s.update_document(once,block,readme=True)==once
    assert 'Imported old claim; UNKNOWN.' in once
    assert len(once.splitlines())<180
    assert once.count('<!-- doc-head:')==once.count('<!-- /doc-head -->')==1
