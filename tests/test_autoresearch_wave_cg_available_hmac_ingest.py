"""Frozen hMAC/VoIP ingestion only; never import acquisition recipes."""
from orchestration.autoresearch import fmx_live_dataset as live
from orchestration.autoresearch import fmx_offline_data as old
from copy import deepcopy
from pathlib import Path
from dataclasses import fields
import ast
import hashlib
import json
import pytest


def test_available_hmac_new_api_and_separate_regime():
    data=live.load_available_hmac_dataset()
    assert len(data['records'])==370
    assert {r['workload_regime']for r in data['records'][360:]}=={'bidir_8flow_voip_hmac'}
    assert data['missing_at_cutoff']==list(range(140,147))


def test_available_hmac_block_api_preserves_sequential_history():
    data=live.load_available_hmac_blocks()
    assert len(data['crossed'])==3516 and len(data['sequential'])==16
    assert len({(r['round_id'],r['block_index'])for r in data['crossed']})==1670


@pytest.fixture(scope='module')
def loaded():return live.load_available_hmac_dataset(),live.load_available_hmac_blocks()


@pytest.fixture
def source():
    manifest,refs=live._hmac_inputs();item=manifest['available'][0]
    ref=refs[item['receipt']];recipe=refs[item['recipe_paths'][0]]
    return live._json(live.ROOT/ref['path']),ref,recipe,(live.ROOT/recipe['path']).read_text(),(live.ROOT/refs[item['tsv_path']]['path']).read_text()


def convert(source):return live._convert_available_hmac_payload(135,*source)


def test_prior_records_blocks_and_16_sequential_dicts_untouched(loaded):
    records,blocks=loaded
    assert records['records'][:360]==live._json(live.HMAC_PRIOR_RECORDS)['records']
    prior=live._json(live.HMAC_PRIOR_BLOCKS)
    assert blocks['crossed'][:3356]==prior['crossed']and blocks['sequential']==prior['sequential']
    assert records['source_refs'][:130]==live._json(live.HMAC_PRIOR_RECORDS)['source_refs']


def test_voices_not_invented_and_missing_block_health_not_inherited(loaded):
    records,blocks=loaded
    for row in records['records'][360:]:
        assert row['voip_evidence']['status'].startswith('UNKNOWN_')
        assert all(row['voip_evidence'][k]is None for k in ('latency_ms','jitter_ms','packet_loss_pct','mos'))
        assert row['voip_evidence']['effective_AC_mapping_verified']is False
        assert 'bidir_8flow_voip_hmac'in row['policy_key']
    for row in blocks['crossed'][3356:]:
        assert 'restoration_verified'not in row['observation']and'station_drops'not in row['observation']
        assert row['reported_block_health']==dict(restoration_ok=True,station_reset_count=0)


def test_literal_new_timing_not_historical_formula_and_fq_readback_conflict(loaded):
    records,_=loaded
    expected={135:(15,30),136:(27,48),137:(48,69),138:(69,90),139:(87,108)}
    for row in records['records'][360:]:
        assert (row['slot_time_us'],row['ack_timeout_us'])==expected[int(row['round_id'][1:])]
        e=row['certified_wds_evidence'];assert e['timing_formula_transfer_qualified']is False
        assert e['physical_distance_verified']is False and e['effective_timing_independently_verified']is False
        if row['source_position']=='/iterations/1':
            assert row['hmac_source_controls']['fq_flows']==1024
            assert e['fq_flows_readback_text_values']==dict(ap=[4096],cpe=[4096])
            assert e['fq_flows_declared_vs_text_readback_match']==dict(ap=False,cpe=False)


@pytest.mark.parametrize('rounds',[(140,),(146,),(135,140),(True,),(135.0,),(135,135),()])
def test_missing_future_or_malformed_round_rejected_before_access(rounds,monkeypatch):
    monkeypatch.setattr(live,'_hmac_inputs',lambda *a,**k:pytest.fail('Future input access forbidden'))
    with pytest.raises(ValueError):live.load_available_hmac_dataset(round_ids=rounds)
    with pytest.raises(ValueError):live.load_available_hmac_blocks(round_ids=rounds)


def test_external_wrong_manifest_pin_rejected_before_members(monkeypatch):
    monkeypatch.setattr(live,'_binding',lambda *a:pytest.fail('Wrong pin must reject before reading member'))
    with pytest.raises(ValueError):live._hmac_inputs(expected_manifest_sha256='0'*64)


def test_changed_frozen_member_hash_rejected(monkeypatch):
    original=live._binding
    def tamper(path):
        result=original(path)
        if str(path).endswith('.tsv'):result['sha256']='0'*64
        return result
    monkeypatch.setattr(live,'_binding',tamper)
    with pytest.raises(ValueError,match='size/hash'):live._hmac_inputs()


def test_manifest_future_path_rejected_before_member_reads(monkeypatch):
    m=live._json(live.HMAC_MANIFEST);m['bindings'][1]['path']='artifacts/autoresearch/r140_unavailable.json'
    monkeypatch.setattr(live,'_json',lambda path:m)
    original=live._binding
    monkeypatch.setattr(live,'_binding',lambda path:original(path)if Path(path)==live.HMAC_MANIFEST else pytest.fail('No member access'))
    with pytest.raises(ValueError):live._hmac_inputs()


@pytest.mark.parametrize('where,key,bad',[
    ('root','traffic_regime','bidir_8flow'),('root','active_flow_count',True),('root','distance_m',1000.0),
    ('item','bidirectional',1),('knobs','voip_probe_tos',None),('knobs','coverage_class',6),
    ('knobs','ack_timeout_us',36),('knobs','fq_flows',2048),('knobs','tx_aggr_factor',False)])
def test_context_and_package_malformations_rejected(source,where,key,bad):
    payload=source[0]
    obj=payload if where=='root'else payload['iterations'][0]if where=='item'else payload['iterations'][0]['candidate_knobs']
    obj[key]=bad
    with pytest.raises(ValueError):convert(source)


@pytest.mark.parametrize('key,bad',[('crossover_step',2),('block_index',True),('mac_tx_packets_delta',True),('tid6_vo_tx_pkts_delta',False)])
def test_malformed_block_ids_and_counters_rejected(source,key,bad):
    source[0]['iterations'][0]['repetition_blocks'][0][key]=bad
    with pytest.raises(ValueError):convert(source)


def test_schedule_conflict_and_health_type_rejected(source):
    payload=source[0];saved=deepcopy(payload['crossover_schedule']);payload['crossover_schedule'][0]=['B','A']
    with pytest.raises(ValueError):convert(source)
    payload['crossover_schedule']=saved;payload['iterations'][0]['repetition_blocks'][0]['observation']['restoration_ok']='false'
    with pytest.raises(ValueError):convert(source)


def test_missing_tid_counter_remains_unknown_not_zero(source):
    del source[0]['iterations'][0]['repetition_blocks'][0]['tid6_vo_tx_pkts_delta']
    records,blocks,_=convert(source)
    assert blocks[0]['tid_counters']['tid6_vo_tx_pkts_delta']is None
    assert records[0]['certified_wds_evidence']['tid_counter_block_sums']['tid6_vo_tx_pkts_delta']is None
    assert records[0]['certified_wds_evidence']['tid_counter_sums_match']is False


def test_tsv_is_checked_not_ignored(source):
    payload,ref,recipe,text,tsv=source
    with pytest.raises(ValueError):live._convert_available_hmac_payload(135,payload,ref,recipe,text,tsv.replace('87.10','87.11',1))


def test_no_source_recipe_execution_or_imports(source,monkeypatch):
    import builtins
    original=builtins.__import__
    def guarded(name,*args,**kwargs):
        if name.startswith('tools.bench'):pytest.fail('Recipe must never be imported')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',guarded)
    assert len(convert(source)[0])==2


def test_all_historical_function_and_class_ASTs_exactly_preserved():
    folder=live.HMAC_ARTIFACTS/'dataset_before_implementation'
    for name in ('fmx_live_dataset.py','fmx_offline_data.py'):
        before=ast.parse((folder/name).read_text());after=ast.parse((live.ROOT/'orchestration/autoresearch'/name).read_text())
        current={n.name:ast.dump(n,include_attributes=False)for n in after.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
        for node in before.body:
            if isinstance(node,(ast.FunctionDef,ast.ClassDef)):assert current[node.name]==ast.dump(node,include_attributes=False)


@pytest.mark.parametrize('revision',[56,60,65,70,75,80,86,92,96,102,107,134])
def test_all_twelve_historical_record_and_block_serializations_byte_exact(revision):
    group={96:'waves_bq_to_bt_20261024',102:'waves_bu_to_bx_20261024',107:'waves_by_to_cb_20261024'}
    folder=live.ROOT/'artifacts/autoresearch'/group[revision]if revision in group else live.BQCF_ARTIFACTS
    record_path=getattr(live,f'R{revision}_RECORDS_OUTPUT',folder/f'normalized_r1_to_r{revision}_measurements_20261024.json')
    block_path=getattr(live,f'R{revision}_BLOCKS_OUTPUT',folder/f'normalized_r16_to_r{revision}_block_observations_20261024.json')
    for result,path in ((live.load_live_dataset(through_round=revision),record_path),(live.load_crossed_dataset(through_round=revision),block_path)):
        assert (json.dumps(result,indent=2,allow_nan=False)+'\n').encode()==path.read_bytes()


def test_consistent_raw_tx_aggr_factor_cannot_override_recipe_airtime_contract(source):
    clean=deepcopy(source)
    arm=source[0]['iterations'][0]
    for envelope in (arm,arm['candidate_knobs'],arm['readback']):envelope['tx_aggr_factor']=2
    with pytest.raises(ValueError,match='tx_aggr_factor.*recipe'):
        convert(source)
    payload,ref,recipe,text,tsv=clean
    changed=text.replace('"tx_aggr_factor": airtime_flags','"tx_aggr_factor": 2',1)
    assert changed!=text
    with pytest.raises(ValueError,match='tx_aggr_factor.*recipe'):
        live._convert_available_hmac_payload(135,payload,ref,recipe,changed,tsv)
