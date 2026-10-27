import hashlib
import json
from pathlib import Path
import pytest
from tools.wiki import update_stage267a_human_context as m


def test_context_and_receipt_bind_real_evidence():
    root=Path(__file__).resolve().parents[1];r=json.loads((root/m.RECEIPT).read_text())
    data=(root/m.DOC).read_bytes();text=data.decode()
    assert len(text.splitlines())<220 and text.startswith('<!-- doc-head:')
    assert text.count('<!-- doc-head:')==text.count('<!-- /doc-head -->')==1
    assert hashlib.sha256(data).hexdigest()==r['outputs'][m.DOC]['sha256']
    for row in r['static_sources']:
        assert hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256']
    for phrase in ['263A','264A','265A','266A','UNKNOWN','Audit exit1','Panel1','NO','mtd2','v8.7.25']:
        assert phrase.lower() in text.lower()
    assert not r['boundary']['hardware_access'] and not r['boundary']['remote_state_checked']
    assert 'si la STA remota sigue stock airOS PtP (is_ubnt_ptp=1)' in text


def test_previous_document_preserved():
    root=Path(__file__).resolve().parents[1];r=json.loads((root/m.RECEIPT).read_text())
    p=r['previous_document'];assert hashlib.sha256((root/p['path']).read_bytes()).hexdigest()==p['sha256']


def test_missing_input_does_not_replace_context(tmp_path):
    path=tmp_path/m.DOC;path.parent.mkdir(parents=True);path.write_text('unchanged')
    with pytest.raises(OSError):m.build(tmp_path)
    assert path.read_text()=='unchanged'
