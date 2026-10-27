"""A saved report's title/readback cannot become silicon or TDMA acceptance."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from orchestration.autoresearch.fmx_silicon_receipt import (
    SavedSiliconReceipt, load_saved_silicon_receipt, audit_saved_silicon_receipt,
    TIMING, CHANINFO, CONTROLS)


ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'artifacts/autoresearch/waves_cg_to_cj_20261024/inputs/artifacts/qca988x/pb_021_031_050_live_lap120_silicon_qualification_20261024.json'


def bound(value):
    raw=json.dumps(value,allow_nan=True).encode()
    return SavedSiliconReceipt(raw,hashlib.sha256(raw).hexdigest())


@pytest.fixture
def source():
    return json.loads(SOURCE.read_text(encoding='utf-8'))


def test_real_saved_report_keeps_claims_and_qualification_distinct(source):
    report=audit_saved_silicon_receipt(bound(source))
    assert report['internally_consistent_under_reported_clock'] is True
    assert report['status']=='DOCUMENTARY_PROBE_ONLY'
    assert 'CONFIRMED_ON_SILICON' in report['source_claims']['pb_031_verdict']
    for key in ('physical_acceptance','automatic_execution_allowed','stage4_tdma_qualified',
                'coarse_hmac_cadence_qualified','operational_csi_qualified','effective_ampdu_qualified',
                'per_peer_power_qualified','restoration_independently_verified',
                'clock_frequency_independently_verified','ldpc_control_or_latency_qualified',
                'quantiles_independently_recomputed','timing_formula_transfer_qualified'):
        assert report[key] is False, key


def test_ack_conflict_is_explicit_without_historical_rewrite(source):
    report=audit_saved_silicon_receipt(bound(source))
    assert len(report['timing_rows'])==7
    assert all(not row['same_as_historical_advisory'] for row in report['timing_rows'])
    assert [(r['coverage_class'],r['reported_ack_timeout_us'],r['historical_advisory_ack_us'])
            for r in report['timing_rows']][:3]==[(0,30,18),(2,36,30),(6,48,54)]
    assert report['historical_ack_metadata_rewritten'] is False


def test_tsf_and_capture_observations_do_not_prove_clock_or_csi(source):
    result=audit_saved_silicon_receipt(bound(source))
    assert result['repeated_tsf2_words'] is True
    assert result['channel_capture_bit']==0
    assert set(result['channel_bank_word_counts'].values())=={16}
    assert result['raw_clock_samples_present'] is False
    assert result['reported_sample_count']==160
    assert result['reported_quantiles']['debugfs_two_reg_mmio_roundtrip_us']['p99']==2758.85


def test_reported_restoration_is_only_a_state_claim(source):
    result=audit_saved_silicon_receipt(bound(source))
    assert result['reported_restoration']=={'coverage_class_restored':0,'htt_max_amsdu_ampdu_restored':'3 64'}
    assert result['host_htt_readback_consistent'] is True
    assert result['restoration_independently_verified'] is False


@pytest.mark.parametrize('field,value',[
    ('coverage_class',True),('coverage_class',32),('nominal_distance_m',False),
    ('dcu_gbl_ifs_slot_cycles_88mhz',792.0),('ack_timeout_us',True),
    ('cts_timeout_us',float('inf')),('dcu_gbl_ifs_slot_0x21070_hex','0x100000000'),
    ('pcu_time_out_0x28014_hex','-0x1'),('sample_mac_pcu_tsf2_l32_0x28120',None)])
def test_bad_timing_context_is_not_coerced(source,field,value):
    source[TIMING]['coverage_class_silicon_table'][0][field]=value
    with pytest.raises(ValueError):
        audit_saved_silicon_receipt(bound(source))


@pytest.mark.parametrize('section,key,value',[
    (TIMING,'mac_core_clock_hz',True),(TIMING,'mac_core_clock_cycles_per_us',0),
    (TIMING,'coverage_class_silicon_table',[]),(CHANINFO,'chaninfo_ctrl_decoded',{}),
    (CONTROLS,'htt_max_amsdu_ampdu_readbacks',[]),(CONTROLS,'ldpc_latency_cycles',True),
    (CONTROLS,'pb_031_verdict',None)])
def test_missing_or_malformed_probe_fields_fail_closed(source,section,key,value):
    source[section][key]=value
    with pytest.raises(ValueError):
        audit_saved_silicon_receipt(bound(source))


@pytest.mark.parametrize('mutation',[
    'slot','hex','ack','capture','readback'])
def test_arithmetic_conflict_is_preserved_as_blocked_evidence(source,mutation):
    row=source[TIMING]['coverage_class_silicon_table'][0]
    if mutation=='slot': row['dcu_gbl_ifs_slot_us']=10
    elif mutation=='hex': row['dcu_gbl_ifs_slot_0x21070_hex']='0x00000319'
    elif mutation=='ack': row['ack_timeout_cycles_88mhz']=2641
    elif mutation=='capture': source[CHANINFO]['chaninfo_ctrl_decoded']['CAPTURE_CHAN_INFO_bit0']=1
    else: source[CONTROLS]['htt_max_amsdu_ampdu_readbacks'][0]['readback']='3 64'
    result=audit_saved_silicon_receipt(bound(source))
    assert result['status']=='DOCUMENTARY_PROBE_CONFLICT'
    assert 'SAVED_ARITHMETIC_OR_READBACK_CONFLICT' in result['blocking_reasons']
    assert result['physical_acceptance'] is False


def test_duplicate_coverage_context_rejected(source):
    source[TIMING]['coverage_class_silicon_table'][1]=deepcopy(source[TIMING]['coverage_class_silicon_table'][0])
    with pytest.raises(ValueError,match='Unique'):
        audit_saved_silicon_receipt(bound(source))


@pytest.mark.parametrize('key,value',[
    ('n_samples',True),('n_samples',159),('single_pcie_mmio_syscall_us_p95',1),
    ('host_vs_target_midpoint_jitter_abs_us_p99',-1),
    ('measured_clock_ratio_cycles_per_us_mean',float('nan')),
    ('measured_clock_ratio_cycles_per_us_mean',10**400)])
def test_clock_aggregate_context_rejected_when_malformed(source,key,value):
    source[TIMING]['n160_paired_clock_benchmark'][key]=value
    with pytest.raises(ValueError):
        audit_saved_silicon_receipt(bound(source))


def test_input_object_and_original_bytes_are_not_mutated(source):
    original=deepcopy(source)
    saved=SOURCE.read_bytes()
    audit_saved_silicon_receipt(bound(source))
    assert source==original
    assert SOURCE.read_bytes()==saved


def test_loader_requires_caller_pin_and_rechecks_bound_bytes(tmp_path,source):
    p=tmp_path/'receipt.json'
    raw=json.dumps(source).encode()
    p.write_bytes(raw)
    sha=hashlib.sha256(raw).hexdigest()
    result=load_saved_silicon_receipt(p,expected_sha256=sha)
    assert result.parse()==source
    with pytest.raises(ValueError,match='hash mismatch'):
        replace(result,payload=result.payload+b' ').parse()
    p.write_bytes(raw+b' ')
    with pytest.raises(ValueError,match='hash mismatch'):
        load_saved_silicon_receipt(p,expected_sha256=sha)


@pytest.mark.parametrize('pin',[None,'','0'*63,'G'*64,True])
def test_invalid_pin_rejected_before_file_read(tmp_path,pin):
    with pytest.raises(ValueError,match='SHA256'):
        load_saved_silicon_receipt(tmp_path/'absent.json',expected_sha256=pin)


@pytest.mark.parametrize('path',['https://example.invalid/receipt.json','\\\\device\\share\\receipt.json','//device/share/receipt.json'])
def test_network_location_rejected_before_any_read(path):
    with pytest.raises(ValueError,match='local'):
        load_saved_silicon_receipt(path,expected_sha256='0'*64)


@pytest.mark.parametrize('raw',[b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":1e999}',b'[]'])
def test_ambiguous_json_is_not_accepted(raw):
    with pytest.raises(ValueError):
        SavedSiliconReceipt(raw,hashlib.sha256(raw).hexdigest()).parse()


def test_embedded_metadata_never_opens_other_paths(tmp_path,source):
    source['raw_samples_path']='\\\\LAP-120\\must-not-open'
    source['command']='ssh device destructive-command'
    p=tmp_path/'receipt.json'
    raw=json.dumps(source).encode();p.write_bytes(raw)
    result=audit_saved_silicon_receipt(load_saved_silicon_receipt(p,expected_sha256=hashlib.sha256(raw).hexdigest()))
    assert result['physical_acceptance'] is False


@pytest.mark.parametrize('value',[None,[],'reported',True])
def test_clock_container_must_be_an_object(source,value):
    source[TIMING]['n160_paired_clock_benchmark']=value
    with pytest.raises(ValueError,match='object'):
        audit_saved_silicon_receipt(bound(source))
