import math
from pathlib import Path
import pytest
from tools.re import build_stage353a_sub20mhz_pll_ofdm_timing_matrix as m
from tools.re import ground_up_release_common as c


@pytest.mark.parametrize('width,symbol,slot',[(20,4,9),(10,8,13),(5,16,21)])
def test_source_timing_and_non_naive_slot(width,symbol,slot):
    r=m.timing(width)
    assert r['legacy_ofdm_symbol_us']==symbol and r['ath9k_slot_us']==slot
    assert r['legacy_ofdm_useful_symbol_us']+r['legacy_ofdm_guard_us']==symbol
    assert r['subcarrier_spacing_khz']*r['legacy_ofdm_useful_symbol_us']==1000
    assert r['timing_assumptions']=={'band':'5GHz','coverage_class':0,'dynack_enabled':False,'configured_20mhz_slottime_us':9}


@pytest.mark.parametrize('width',[True,0,6,40,float('nan')])
def test_invalid_width(width):
    with pytest.raises(ValueError):m.timing(width)


def test_matrix_sources_and_no_hardware_claim():
    r=c.load(m.ROOT/m.OUT)
    assert len(r['matrix'])==4 and not r['boundary']['physical_acceptance']
    assert r['source_findings']['ath10k_upstream_5_10_phymode_cases'] is False
    for source in r['static_sources']:
        assert c.sha(c.read(m.ROOT/source['path']))==source['sha256']
        assert all(a['line_numbers'] for a in source['anchors'])
    for module in r['binary_dissection'].values():
        assert c.sha(c.read(m.ROOT/module['path']))==module['sha256']
    assert r['binary_dissection']['WA_umac']['symbols']


def test_noise_arithmetic_is_conditional_not_a_receiver_measurement():
    assert math.isclose(m.timing(5)['fixed_nf_noise_bandwidth_delta_db'],-6.02059991,abs_tol=1e-8)
    assert 'NOT_VHT5_10' in m.timing(5)['qualification']


def test_doc_budget_and_pair():
    text=(m.ROOT/m.DOC).read_text()
    assert len(text.splitlines())<220 and text.startswith('<!-- doc-head:')
    assert text.count('<!-- doc-head:')==text.count('<!-- /doc-head -->')==1


def test_atomic_json_does_not_overwrite_preexisting_temp_path(tmp_path):
    target=tmp_path/'receipt.json';temp=tmp_path/'receipt.json.tmp';temp.write_text('unrelated')
    c.write_json(target,{'verified':True})
    assert c.load(target)=={'verified':True}
    assert temp.read_text()=='unrelated'
