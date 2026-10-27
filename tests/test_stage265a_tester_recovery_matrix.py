import hashlib
import json
from pathlib import Path
import pytest
from tools.firmware import update_stage265a_tester_recovery_matrix as m


def test_matrix_contract_and_two_guides():
    root=Path(__file__).resolve().parents[1]
    receipt=json.loads((root/'artifacts/autoresearch/stage265a_tester_recovery_matrix_receipt.json').read_text())
    for rel in m.GUIDES:
        data=(root/rel).read_bytes();text=data.decode()
        assert hashlib.sha256(data).hexdigest()==receipt['outputs'][rel]['sha256']
        assert len(text.splitlines())<220 and text.count('<!-- doc-head:')==1
        assert text.count(m.START)==text.count(m.END)==1
        assert 'Recuperaci\u00f3n' in text
        assert '\u00c3' not in text[text.index(m.START):]
        for phrase in ['TFTP','192.168.1.20','mtd2','/proc/mtd','radio.1.ptpmode=0','APPLY','ARP/IPv4','STA','v8.7.25','sin -J']:
            assert phrase in text


def test_replacement_is_idempotent():
    text='<!-- doc-head: test -->\n<!-- /doc-head -->\n\nbody\n'
    assert m.replace_section(m.replace_section(text))==m.replace_section(text)


@pytest.mark.parametrize('tail',[m.START,m.END,m.START+m.START+m.END])
def test_ambiguous_markers_rejected(tail):
    with pytest.raises(ValueError,match='ambiguous'):m.replace_section('<!-- doc-head: x -->\n'+tail)


def test_budget_failure():
    with pytest.raises(ValueError,match='budget'):m.replace_section('<!-- doc-head: x -->\n'+'x\n'*219)


def test_missing_evidence_does_not_rewrite_guides(tmp_path):
    for rel in m.GUIDES:
        p=tmp_path/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('unchanged')
    with pytest.raises(OSError):m.build(tmp_path)
    assert all((tmp_path/rel).read_text()=='unchanged' for rel in m.GUIDES)
