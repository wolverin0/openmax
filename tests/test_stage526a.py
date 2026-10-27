"""Local saved strings and metadata only; no producer/decoder/target execution."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pytest
from tools.autoresearch import build_stage526a_xtensa_ram_canary_pb040_pb050_abi_auditor as m


@pytest.fixture
def sources():
    return [json.loads((m.ROOT/p).read_text('utf-8')) for p in (m.S403,m.S507,m.SPEC)]


def ap_readback(sources):
    b=sources[0]['pb040_live_ram_canary_verification']
    return b['ap_20_fw_checksums_readback'],dict(expected_sha256={m.TARGET:b['patched_firmware_sha256'],m.TMP040:b['patched_firmware_sha256']},
                                                expected_checksums=b['patched_fw_checksums'])


def test_endpoint_evidence_preserves_stock_cpe_and_staging_distinction(sources):
    r=m.audit(*sources);ap=r['pb040']['endpoints']['ap'];cpe=r['pb040']['endpoints']['cpe']
    assert ap['status']=='CONSISTENT_SAVED_READBACK'
    assert ap['checksums']['firmware-N.bin']=='912bcb63' and ap['checksums']['athwlan']=='278d2d76'
    assert cpe['status']=='UNKNOWN' and cpe['checksums']['firmware-N.bin']=='3e4cf97f' and cpe['checksums']['athwlan']=='477a6960'
    assert cpe['file_sha256'][m.TARGET].startswith('398e4380') and cpe['file_sha256'][m.TMP040].startswith('8d50c1ce')
    assert not cpe['expected_sha256_matches'][m.TARGET] and cpe['expected_sha256_matches'][m.TMP040]
    assert r['pb040']['cpe_stock_consistency']['status']=='CONSISTENT_SAVED_READBACK'
    assert not r['pb040']['both_endpoints_support_patched_target_text']
    for name in ('ap','cpe'):
        endpoint=r['pb050']['endpoints'][name]
        assert endpoint['status']=='CONSISTENT_SAVED_READBACK'
        assert endpoint['checksums']['firmware-N.bin']=='92363606' and endpoint['checksums']['athwlan']=='12b29d01'
        assert endpoint['file_sha256'][m.TMP050].startswith('a49160ff')
        assert r['pb050']['target_path_sha256_status'][name]=='MISSING'
        assert not endpoint['native_loaded_payload_bound'] and not endpoint['bind_reload_execution_proven']
    assert not r['native_abi_acceptance'] and not any(r['boundary'].values())


@pytest.mark.parametrize('change',['missing','empty','duplicate_checksum','duplicate_hash','truncated','wrong_checksum','wrong_hash','unsafe_hash_path','nul','surrogate','oversize'])
def test_readback_incomplete_ambiguous_or_mutated_is_unknown(sources,change):
    text,kwargs=ap_readback(sources)
    if change=='missing':text=None
    elif change=='empty':text=''
    elif change=='duplicate_checksum':text+='\nfirmware-N.bin\t912bcb63'
    elif change=='duplicate_hash':text+='\n'+text.splitlines()[-1]
    elif change=='truncated':text=text[:-8]
    elif change=='wrong_checksum':text=text.replace('912bcb63','3e4cf97f')
    elif change=='wrong_hash':text=text.replace('8d50c1ce','0d50c1ce')
    elif change=='unsafe_hash_path':text=text.replace(m.TARGET,m.TARGET.replace('/lib/','/lib/../lib/'))
    elif change=='nul':text+='\0'
    elif change=='surrogate':text+='\ud800'
    else:text='A'*65537
    result=m.audit_readback(text,**kwargs)
    assert result['status']=='UNKNOWN' and result['reason_codes']
    assert not result['native_loaded_payload_bound']


@pytest.mark.parametrize('value',[True,None,'a'*63,'G'*64])
def test_expected_hash_requires_exact_canonical_hex(sources,value):
    text,kwargs=ap_readback(sources);kwargs['expected_sha256'][m.TARGET]=value
    with pytest.raises(ValueError):m.audit_readback(text,**kwargs)


def test_untrusted_extra_text_cannot_become_register_or_execution_proof(sources):
    b=sources[0]['pb040_live_ram_canary_verification']
    b['ap_20_fw_checksums_readback']+='\nreg_value 0x13761320\nsecret=DO-NOT-ECHO-STAGE526'
    r=m.audit(*sources)
    assert r['pb040']['register_getter_status']=='UNKNOWN_NO_RETAINED_GETTER_TEXT'
    assert r['pb040']['direct_host_register_write_confounds_sgmt_effect']
    assert 'DO-NOT-ECHO-STAGE526' not in json.dumps(r)
    assert not r['native_abi_acceptance']


def test_r43_and_r50_configured_controls_remain_confounded_not_getters(sources):
    r=m.audit(*sources);r43=r['pb040']['r43_configured_windows'];r50=r['pb050']['r50_configured_windows']
    assert [w['configured_register_value'] for w in r43]==['0x13721320','0x13761320','0x13721320','0x13761320']
    assert [w['nf_cal_period'] for w in r50]==[30,120,30,120]
    assert [w['active_fw_stats_poll'] for w in r50]==[0,1,0,1]
    assert r['pb050']['other_changed_configured_fields']==['nf_cal_period','active_fw_stats_poll']
    assert all(w['getter_status']=='NOT_RETAINED_CONFIGURED_DICT_ONLY' for w in r43+r50)
    assert not r['pb050']['isolated_patch_effect_proven']


@pytest.mark.parametrize('change',['reordered','duplicate','boolean_nf','negative_nf','boolean_poll','invalid_hex'])
def test_configured_round_shapes_and_integer_hex_domains(sources,change):
    doc=sources[1];windows=doc['rounds'][0]['windows'];cfg=windows[0]['knob_readback']
    if change=='reordered':windows[0],windows[1]=windows[1],windows[0]
    elif change=='duplicate':windows[2]=deepcopy(windows[0])
    elif change=='boolean_nf':cfg['nf_cal_period']=True
    elif change=='negative_nf':cfg['nf_cal_period']=-1
    elif change=='boolean_poll':cfg['active_fw_stats_poll']=True
    else:cfg['bb_timing_29e00_hex']='0x1376132g'
    with pytest.raises(ValueError):m.audit(*sources)


def test_distinct_address_domains_and_old_vendor_build_are_never_transplanted(sources):
    r=m.audit(*sources);claims=r['pb050']['address_claims'];vendor=r['vendor_context']
    assert claims['data_vaddr']=='0x0040c140' and claims['file_offset']=='0x3b1d' and claims['lit4_vaddr']=='0x00980754'
    assert (claims['from_ms'],claims['to_ms'])==(2000,4000)
    assert not claims['address_domains_interchangeable']
    assert vendor['old_vendor_ap_segment2_vaddr']=='0x0040d140'
    assert vendor['claimed_ct_data_minus_old_vendor_segment2']==-0x1000
    assert not vendor['same_binary_build_or_abi_proven'] and not vendor['offset_transplant_allowed']


@pytest.mark.parametrize('change',['units','bad_vaddr','oversize'])
def test_pb050_reported_claim_must_have_bounded_consistent_units(sources,change):
    b=sources[1]['pb050_live_ram_seg2_verification']
    if change=='units':b['seg2_rc_probe_patch']=b['seg2_rc_probe_patch'].replace('(2000ms)','(2001ms)')
    elif change=='bad_vaddr':b['seg2_rc_probe_patch']=b['seg2_rc_probe_patch'].replace('0x0040c140','0xnotHEX00')
    else:b['seg2_rc_probe_patch']='A'*513
    with pytest.raises(ValueError):m.audit(*sources)


@pytest.mark.parametrize('change',['source_hash','decoder_hash','container_hash','payload_size'])
def test_held_proof_is_bound_to_actual_source_decoder_and_static_spec(sources,change):
    proof=json.loads((m.ROOT/m.PROOF).read_text('utf-8'))
    if change=='source_hash':proof['source']['sha256']='0'*64
    elif change=='decoder_hash':proof['decoder']['sha256']='0'*64
    elif change=='container_hash':proof['sgmt_sha256']='0'*64
    else:proof['payload_segments'][2]['bytes']+=1
    with pytest.raises(ValueError):m.verify_held_proof(m.ROOT,proof,sources[2])


def test_saved_report_hashes_compact_doc_and_no_acquisition_execution_imports():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    r=json.loads((m.ROOT/m.OUT).read_text('utf-8'));proof=r['held_vendor_static_proof']
    assert r['stage']=='526A' and r['summary']['new_hardware_results']==0
    assert proof['status']=='STATIC_ROOT_DECODING_NOT_CT_ABI' and not proof['decoding_reexecuted']
    assert proof['container_bytes']==251681 and sum(p['bytes'] for p in proof['payload_segments'])==309464
    assert not proof['ct_firmware_context_equivalent'] and not r['native_abi_acceptance']
    assert not any(r['boundary'].values()) and not r['static_loader']['register_write_intrinsic_proven']
    assert not r['static_loader']['helper_reexecuted']
    for pin in r['static_sources']+r['analysis_dependencies']:
        assert sha(m.ROOT/pin['path'])==pin['sha256']
    assert r['implementation']['sha256']==sha(Path(m.__file__))
    doc=(m.ROOT/m.DOC).read_text('utf-8')
    assert len(doc.splitlines())<220 and doc.startswith('<!-- doc-head:')
    assert doc.count('<!-- doc-head:')==doc.count('<!-- /doc-head -->')==1
    assert sha(m.ROOT/m.DOC)==r['outputs'][m.DOC]['sha256']
    tree=ast.parse(Path(m.__file__).read_text('utf-8'))
    imports=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
    assert not any(name.startswith(('tools.benchmarks','tools.research.sgmt','subprocess','socket','paramiko')) for name in imports)
