"""Frozen R15 asymmetry and genuine crossover experimental-unit contracts."""
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import csv
import json

import pytest

from orchestration.autoresearch.fmx_offline_data import (
    MNOP_INPUTS, R15_RECEIPT, load_all_measurements, load_all14_measurements,
    load_all15_measurements, load_blocked_crossover_blocks, local_json,
    normalized_asymmetric_dataset, write_json,
)


def test_r15_uses_four_actual_windows_not_a_fabricated_ninetieth_record():
    rows,refs=load_all15_measurements()
    assert len(rows)==89 and len(refs)==15
    assert sum(row.round_id=='R15' for row in rows)==4
    assert sum(row.window_kind=='summary_validation' for row in rows)==2
    assert len(load_all15_measurements(include_auxiliary=False)[0])==87
    assert len(load_all_measurements()[0])==58
    assert len(load_all14_measurements()[0])==85
    assert len({(row.round_id,row.iteration) for row in rows})==len(rows)
    assert refs[-1]['sha256']==sha256(R15_RECEIPT.read_bytes()).hexdigest()
    data=normalized_asymmetric_dataset()
    assert data['requested_record_count']==90 and data['observed_record_count']==89
    assert data['historical_checks'][0]['check_complete'] is True


def test_r15_retains_separate_ap_cpe_controls_and_qualified_cipher_context():
    rows,_=load_all15_measurements();r15=[row for row in rows if row.round_id=='R15']
    assert [row.ap_policy.aql_by_ac[2] for row in r15]==[(5000,12000),(1800,3600),(1500,3000),(1350,2700)]
    assert [row.cpe_policy.aql_by_ac[2] for row in r15]==[(5000,12000),(1800,3600),(2100,4200),(2100,4200)]
    ap,cpe=r15[2].ap_policy,r15[2].cpe_policy
    assert (ap.fq_target_us,ap.fq_interval_us,ap.tcp_limit_output_bytes,ap.tcp_notsent_lowat)==(10000,50000,204800,102400)
    assert (cpe.fq_target_us,cpe.fq_interval_us,cpe.tcp_limit_output_bytes,cpe.tcp_notsent_lowat)==(12000,60000,327680,163840)
    assert all(row.encryption_mode=='psk2' and row.encryption_evidence.startswith('DECLARED_') for row in r15)
    assert all(len(row.rtts_ms)==40 and row.goodputs_mbps==() and row.repetitions_reported==4 for row in r15)
    assert all(row.distance_meters is None and row.associated_cpes==('Loco195',) for row in r15)
    assert all('RTT_repetition_membership_and_pairing_not_retained' in row.flags for row in r15)
    assert replace(r15[2],ap_policy=cpe,cpe_policy=ap).policy_key!=r15[2].policy_key


def test_frozen_tsv_and_json_agree_on_all_four_rounded_window_summaries():
    raw=local_json(R15_RECEIPT)
    with (MNOP_INPUTS/'lap120_loco195_r15_wpa2_asym_n40_results.tsv').open(encoding='utf-8',newline='') as handle:
        tsv=list(csv.DictReader(handle,delimiter='\t'))
    assert len(tsv)==len(raw['iterations'])==4
    for saved,row in zip(tsv,raw['iterations']):
        assert saved['commit']==row['commit']
        assert abs(float(saved['goodput_mbps'])-row['observation']['goodput_rx_mbps'])<=.006
        assert abs(float(saved['p95_rtt_ms'])-row['observation']['p95_rtt_ms'])<=.006
        assert abs(float(saved['jain_fairness'])-row['observation']['jain_fairness'])<.00001


def test_r15_does_not_create_block_ids_from_sorted_pings():
    assert load_blocked_crossover_blocks(R15_RECEIPT)==[]
    assert load_blocked_crossover_blocks({'iterations':[]})==[]


@pytest.mark.parametrize('change',[
    'missing_cpe','boolean_be','reversed_be','missing_ap_field','bad_identity',
    'bad_rtt_count','bad_mac','conflicting_distance','conflicting_crypto',
])
def test_malformed_asymmetric_receipts_fail_closed_without_touching_snapshots(tmp_path,change):
    raw=local_json(R15_RECEIPT);raw['iterations']=raw['iterations'][2:3]
    item=raw['iterations'][0];ap=item['candidate_knobs']['ap_state'];cpe=item['candidate_knobs']['cpe_state']
    if change=='missing_cpe':item['candidate_knobs'].pop('cpe_state')
    if change=='boolean_be':ap['be_low_us']=True
    if change=='reversed_be':cpe['be_low_us']=99999
    if change=='missing_ap_field':ap.pop('fq_quantum_bytes')
    if change=='bad_identity':raw['experiment_id']='FMX-AUTORESEARCH-LIVE-016'
    if change=='bad_rtt_count':item['rtt_sample_count']=41
    if change=='bad_mac':item['mac_retry_rate']=.9
    if change=='conflicting_distance':ap['distance_meters']=1500
    if change=='conflicting_crypto':cpe['encryption_mode']='none'
    path=tmp_path/'fixture.json';path.write_text(json.dumps(raw),encoding='utf-8')
    with pytest.raises(ValueError):load_all15_measurements(path)


def test_missing_historical_r15_is_unknown_without_blocking_prior_records(tmp_path):
    rows,refs=load_all15_measurements(tmp_path/'missing.json')
    assert len(rows)==85 and refs[-1]['status']=='UNKNOWN_LOCAL_ARTIFACT_ABSENT'
    assert refs[-1]['check_complete'] is True


def fixture():
    return {'experiment_id':'SYNTHETIC_OFFLINE_SCHEMA_TEST', 'repetition_blocks':[
        {'block_index':8,'crossover_step':2,'treatment_id':'B','observation':{'p95_rtt_ms':6.0}},
        {'block_index':8,'crossover_step':1,'treatment_id':'A','p95_ms':10.0},
        {'block_index':21,'crossover_step':1,'treatment_id':'B','p95_ms':5.0},
        {'block_index':21,'crossover_step':2,'treatment_id':'A','p95_ms':9.0},
    ]}


def test_genuine_noncontiguous_block_and_step_ids_are_preserved_and_detached(tmp_path):
    raw=fixture();before=deepcopy(raw);rows=load_blocked_crossover_blocks(raw)
    assert [(row['block_index'],row['crossover_step'],row['treatment_id']) for row in rows]==[(8,1,'A'),(8,2,'B'),(21,1,'B'),(21,2,'A')]
    assert [row['observation']['p95_rtt_ms'] for row in rows]==[10,6,5,9]
    rows[0]['observation']['p95_rtt_ms']=999
    assert raw==before
    path=tmp_path/'crossover.json';path.write_text(json.dumps(raw),encoding='utf-8')
    assert load_blocked_crossover_blocks(path)==load_blocked_crossover_blocks(raw)


def test_iteration_envelope_inherits_only_explicit_step_and_treatment_identity():
    raw={'iterations':[
        {'commit':'A','crossover_step':4,'repetition_blocks':[{'block_index':42,'p95_rtt_ms':10}]},
        {'commit':'B','crossover_step':7,'repetition_blocks':[{'block_index':42,'p95_rtt_ms':6}]},
    ]}
    rows=load_blocked_crossover_blocks(raw)
    assert [(r['block_index'],r['crossover_step'],r['treatment_id']) for r in rows]==[(42,4,'A'),(42,7,'B')]
    assert rows[0]['source_position']=='/iterations/0/repetition_blocks/0'


def test_abba_steps_remain_distinct_observations_until_the_auditor_aggregates():
    raw={'repetition_blocks':[{'block_index':17,'crossover_step':step,'treatment_id':arm,'p95_ms':10-step}
                              for step,arm in enumerate(('A','B','B','A'))]}
    rows=load_blocked_crossover_blocks(raw)
    assert len(rows)==4 and [r['treatment_id'] for r in rows]==list('ABBA')


@pytest.mark.parametrize('change',[
    'missing_block','missing_step','missing_treatment','boolean_block','boolean_step','negative_block',
    'duplicate_unit','bad_metric','metric_conflict','bad_quantiles','bad_rtts','bad_collection','step_conflict',
])
def test_malformed_or_ambiguous_crossover_units_are_never_silently_paired(change):
    raw=fixture();item=raw['repetition_blocks'][0]
    if change=='missing_block':item.pop('block_index')
    if change=='missing_step':item.pop('crossover_step')
    if change=='missing_treatment':item.pop('treatment_id')
    if change=='boolean_block':item['block_index']=True
    if change=='boolean_step':item['crossover_step']=False
    if change=='negative_block':item['block_index']=-1
    if change=='duplicate_unit':raw['repetition_blocks'].append(deepcopy(item))
    if change=='bad_metric':item['observation']['p95_rtt_ms']=float('nan')
    if change=='metric_conflict':item['p95_ms']=77
    if change=='bad_quantiles':item['observation'].update(p50_rtt_ms=9,p99_rtt_ms=5)
    if change=='bad_rtts':item['rtts_ms']=[True]
    if change=='bad_collection':raw['repetition_blocks']={}
    if change=='step_conflict':raw['crossover_step']=99
    with pytest.raises(ValueError):load_blocked_crossover_blocks(raw)


@pytest.mark.parametrize('path',[MNOP_INPUTS/'never.json',MNOP_INPUTS/'subdir/never.json'])
def test_new_outputs_cannot_overwrite_any_owned_frozen_input(path):
    with pytest.raises(ValueError):write_json(path,{})


@pytest.mark.parametrize('case',[
    'failed_restoration_masked','station_drop_masked','malformed_nested_drop_masked','malformed_nested_metric_masked',
])
def test_conflicting_or_malformed_nested_quality_cannot_be_overridden_by_a_positive_field(case):
    row={'block_index':5,'crossover_step':2,'treatment_id':'B','observation':{'p95_rtt_ms':6.0}}
    if case=='failed_restoration_masked':row.update(restoration_verified=True);row['observation']['restoration_verified']=False
    if case=='station_drop_masked':row.update(station_drops=0);row['observation']['station_drops']=2
    if case=='malformed_nested_drop_masked':row.update(station_drops=0);row['observation']['station_drops']=False
    if case=='malformed_nested_metric_masked':row.update(p95_rtt_ms=1);row['observation']['p95_rtt_ms']=True
    with pytest.raises(ValueError):load_blocked_crossover_blocks({'repetition_blocks':[row]})
