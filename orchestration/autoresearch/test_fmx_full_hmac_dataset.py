"""Frozen-only full hMAC ingestion; no acquisition or recipe execution."""
import importlib
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import json
import stat
from types import SimpleNamespace
import pytest


def module():return importlib.import_module('orchestration.autoresearch.fmx_full_hmac_dataset')


def test_full_cohort_is_additive_without_rewriting_historical_sources():
    s=module();data=s.load_full_hmac_dataset();blocks=s.load_full_hmac_blocks()
    old=json.loads(s.PRIOR_RECORDS.read_bytes());oldblocks=json.loads(s.PRIOR_BLOCKS.read_bytes())
    assert len(data['records'])==384 and len(blocks['crossed'])==3740
    assert data['records'][:370]==old['records']
    assert data['source_refs'][:len(old['source_refs'])]==old['source_refs']
    assert blocks['crossed'][:3516]==oldblocks['crossed']
    assert blocks['sequential']==oldblocks['sequential'] and len(blocks['sequential'])==16
    assert len([r for r in data['records']if r['round_id']=='R135'])==2
    assert len([r for r in data['records']if r['round_id']=='R146'])==2


def test_wrong_manifest_pin_is_rejected_before_content_read(monkeypatch):
    s=module()
    monkeypatch.setattr(Path,'read_bytes',lambda *a:pytest.fail('Wrong pin must reject before reading'))
    with pytest.raises(ValueError):s.load_full_hmac_dataset(expected_manifest_sha256='0'*64)


@pytest.fixture(scope='module')
def cumulative():
    s=module();return s.load_full_hmac_dataset(),s.load_full_hmac_blocks()


def typed_r141(cumulative):
    s=module();r=next(r for r in cumulative[0]['records']if r['round_id']=='R141'and r['source_position']=='/iterations/1')
    values={k:deepcopy(r[k])for k in s.FullHmacMeasurement.__dataclass_fields__}
    for key in ('ap_policy','cpe_policy'):values[key]=s.old.CrossLayerEndpointPolicy(**values[key])
    return s.FullHmacMeasurement(**values)


def test_typed_compound_pair_cannot_substitute_a_different_round_treatment(cumulative):
    r=typed_r141(cumulative);controls=deepcopy(r.compound_recipe_controls)
    controls['declared_endpoint_pairs']={'ap':[3,16],'cpe':[3,16]}
    with pytest.raises(ValueError):replace(r,compound_recipe_controls=controls)


@pytest.fixture(scope='module')
def inputs():return module()._inputs()


def case(inputs,number=141):
    s=module();manifest,refs,contents,_=inputs
    item=next(a for a in manifest['available']if a['round_id']==f'R{number}')
    return [number,json.loads(contents[item['receipt']]),deepcopy(refs[item['receipt']]),
        deepcopy(refs[item['recipe_paths'][0]]),contents[item['recipe_paths'][0]].decode(),contents[item['tsv_path']].decode()]


def test_historical_serializations_and_api_defaults_remain_exact():
    s=module()
    for loader,path in ((s.live.load_available_hmac_dataset,s.PRIOR_RECORDS),(s.live.load_available_hmac_blocks,s.PRIOR_BLOCKS)):
        assert (json.dumps(loader(),indent=2,allow_nan=False)+'\n').encode()==path.read_bytes()
    with pytest.raises(ValueError):s.live.load_available_hmac_dataset(round_ids=[140])


def test_source_timings_health_counts_and_no_voice_alias(cumulative):
    s=module();data,blocks=cumulative
    rows=[r for r in data['records']if r['workload_regime']==s.REGIME]
    own=[b for b in blocks['crossed']if int(b['round_id'][1:])>=135]
    assert len(rows)==24 and len(own)==384
    assert sum(b['pings_sent']for b in own)==3840
    assert sum(len(b['rtts_ms'])for b in own)==3836
    assert [(r['round_id'],r['packet_loss_pct'])for r in rows if r['packet_loss_pct']>0]==[('R138',.625),('R142',1.25),('R144',.625)]
    assert all(r['station_drops']==0 and r['restoration_verified']is True for r in rows)
    old=next(r for r in rows if r['round_id']=='R135');new=next(r for r in rows if r['round_id']=='R141')
    assert old['ack_timeout_us']==30 and new['ack_timeout_us']==36
    assert all(r['voip_evidence'][k]is None for r in rows for k in ('latency_ms','jitter_ms','packet_loss_pct','mos'))
    assert all(r['voip_evidence']['effective_AC_mapping_verified']is False for r in rows)
    assert data['historical_missing_rounds']==[110,111,112,113]and data['missing_at_cutoff']==[]


def test_declared_htt_pairs_are_endpoint_identity_not_factor_or_batch_title(cumulative):
    s=module();rows=[r for r in cumulative[0]['records']if int(r['round_id'][1:])>=140]
    for row in rows:
        number=int(row['round_id'][1:]);compound=row['compound_recipe_controls']
        assert row['reported_batch']is None and compound['effective_control_verified']is False
        assert compound['feedback_adaptive_control_verified']is False and compound['GI_LDPC_STBC_setter_verified']is False
        endpoints=json.loads(row['policy_key'])
        if number==140:
            assert compound['declared_endpoint_pairs']is None
            assert all('recipe_declared_htt_max_amsdu_ampdu'not in p for p in endpoints)
        else:
            expected=[3,64]if row['force_tx_status']==0 else[3,32 if number<=143 else 16]
            assert compound['declared_endpoint_pairs']=={'ap':expected,'cpe':expected}
            assert compound['readback_text_matches_declaration']=={'ap':True,'cpe':True}
            assert all(p['recipe_declared_htt_max_amsdu_ampdu']==expected for p in endpoints)
            assert expected[1]!=row['hmac_source_controls']['tx_aggr_factor']


@pytest.mark.parametrize('changes',[
    {'distance_meters':1000.0},{'coverage_class':True},{'active_flow_count':8.0},
    {'bidirectional':1},{'workload_regime':'bidir_8flow'},{'round_id':'R147'},
    {'voip_probe_tos':'0x0'},{'restoration_verified':1},{'station_drops':False},
    {'hmac_source_controls':{'tx_aggr_factor':True,'fq_flows':1024}},
    {'hmac_source_controls':{'tx_aggr_factor':2,'fq_flows':1024}},
    {'source_failure_metadata':{'disqualified':'false'}},
])
def test_typed_context_and_health_do_not_coerce_unknown_or_boolean(changes,cumulative):
    with pytest.raises(ValueError):replace(typed_r141(cumulative),**changes)


@pytest.mark.parametrize('mutate',[
    lambda p:p.update(experiment_id=p['experiment_id'].replace('141','147')),
    lambda p:p['iterations'][0].update(active_flow_count=True),
    lambda p:p['iterations'][1]['candidate_knobs'].update(coverage_class=2.0),
    lambda p:p['iterations'][0].pop('slot_time_us'),
    lambda p:p['iterations'][0]['candidate_knobs']['ap_state'].update(distance_m=1001),
    lambda p:p['iterations'][0]['repetition_blocks'][0].update(crossover_step=True),
    lambda p:p['iterations'][0]['repetition_blocks'][0]['observation'].update(restoration_ok=0),
])
def test_raw_context_or_paired_coordinate_forgery_fails(inputs,mutate):
    args=case(inputs);mutate(args[1])
    with pytest.raises(ValueError):module().convert_full_hmac_payload(*args)


def test_consistent_raw_factor_still_must_match_recipe_derivation(inputs):
    args=case(inputs);item=args[1]['iterations'][1]
    for d in (item,item['candidate_knobs'],item['readback']):d['tx_aggr_factor']=2
    with pytest.raises(ValueError,match='recipe-derived'):module().convert_full_hmac_payload(*args)


def test_missing_block_health_and_readback_are_unknown_not_inherited(inputs):
    s=module();args=case(inputs);item=args[1]['iterations'][1]
    item['repetition_blocks'][0]['observation'].pop('restoration_ok',None)
    item['repetition_blocks'][0]['observation'].pop('station_reset_count',None)
    item['readback'].pop('ap_readback')
    records,blocks,_=s.convert_full_hmac_payload(*args)
    target=records[1]
    assert target['compound_recipe_controls']['readback_text_matches_declaration']['ap']is False
    assert target['compound_recipe_controls']['readback_status']=='UNKNOWN_OR_CONFLICTING_SAVED_TEXT'
    b=next(b for b in blocks if b['treatment_id']==item['commit'])
    assert b['reported_block_health']=={'restoration_ok':None,'station_reset_count':None}
    assert target['voip_evidence']['latency_ms']is None


def test_readback_pair_parser_never_joins_separate_scalar_lines(inputs):
    s=module();args=case(inputs);item=args[1]['iterations'][1]
    for endpoint in ('ap','cpe'):item['readback'][endpoint+'_readback']='1\n6\n3 32\n'
    compound=s.recipe_compound_controls(args[4],args[1])[item['commit']]
    assert compound['readback_text_pairs']=={'ap':[[3,32]],'cpe':[[3,32]]}
    assert compound['readback_text_matches_declaration']=={'ap':True,'cpe':True}


@pytest.mark.parametrize('old,new',[
    ('"3 32"','"3 24"'),('"{force_tx_status}" = "1"','"{airtime_flags}" = "1"'),
    ('_peer_extra(pair.cpe_state)','_peer_extra(pair.ap_state)'),
])
def test_unproven_or_misaddressed_compound_recipe_rejected(inputs,old,new):
    args=case(inputs);assert old in args[4];args[4]=args[4].replace(old,new)
    with pytest.raises(ValueError):module().convert_full_hmac_payload(*args)


def test_future_or_boolean_round_rejected_before_payload_access():
    class Poison(dict):
        def __getitem__(self,key):pytest.fail('Out-of-scope payload was accessed')
        def get(self,*args):pytest.fail('Out-of-scope payload was accessed')
    for number in (147,True,140.0,139):
        with pytest.raises(ValueError):module().convert_full_hmac_payload(number,Poison(),None,None,None,None)


@pytest.mark.parametrize('value',[r'\\server\share\x','https://example.invalid/x','../outside','C:relative'])
def test_network_traversal_or_drive_relative_paths_reject_without_content(value,monkeypatch):
    monkeypatch.setattr(Path,'read_bytes',lambda *a:pytest.fail('Rejected path reached content'))
    with pytest.raises(ValueError):module()._safe_path(value)


def test_resolved_network_and_reparse_ancestor_reject_before_child_access(tmp_path,monkeypatch):
    s=module();fake=tmp_path/'virtual_parent'/'member.json';real_resolve=Path.resolve
    with monkeypatch.context()as m:
        m.setattr(Path,'resolve',lambda p,*a,**k:Path(r'\\offline-test.invalid\share\x')if p==fake else real_resolve(p,*a,**k))
        with pytest.raises(ValueError):s._safe_path(fake)
    real_lstat=Path.lstat;visited=[]
    def lstat(path,*a,**k):
        visited.append(path)
        if path==fake.parent:return SimpleNamespace(st_mode=stat.S_IFDIR,st_file_attributes=1024)
        if path==fake:pytest.fail('Reparse parent must reject before inspecting child')
        return real_lstat(path,*a,**k)
    monkeypatch.setattr(Path,'lstat',lstat)
    with pytest.raises(ValueError):s._safe_path(fake)
    assert fake not in visited


@pytest.mark.parametrize('value',[r'/\offline-test.invalid\share\x',r'\/offline-test.invalid/share/x'])
def test_mixed_separator_unc_rejected_before_any_filesystem_probe(value,monkeypatch):
    s=module();probes=[]
    def forbidden(path,*args,**kwargs):
        probes.append(str(path));raise AssertionError('Canonical UNC reached filesystem probe')
    monkeypatch.setattr(Path,'lstat',forbidden)
    monkeypatch.setattr(Path,'resolve',forbidden)
    monkeypatch.setattr(Path,'read_bytes',forbidden)
    with pytest.raises(ValueError):s._safe_path(value)
    assert probes==[]


@pytest.mark.parametrize('mutation',[
    lambda m:m['bindings'][0].update(path='../escape'),
    lambda m:m['bindings'][0].update(path='artifacts/anything_r147_unknown.json'),
    lambda m:m['bindings'][0].update(frozen_path='//remote/share/x'),
    lambda m:m['bindings'][0].update(bytes=True),
    lambda m:m['bindings'][0].update(sha256='not-a-hash'),
    lambda m:m['bindings'].append(deepcopy(m['bindings'][0])),
])
def test_manifest_structure_preflight_before_any_member_read(inputs,mutation,monkeypatch):
    s=module();manifest=deepcopy(inputs[0]);mutation(manifest);real=s._json;real_read=Path.read_bytes
    def decode(raw):
        return manifest if len(raw)==32706 else real(raw)
    def read(path,*args,**kwargs):
        if path!=s.MANIFEST:pytest.fail('Invalid manifest must reject before member reads')
        return real_read(path,*args,**kwargs)
    monkeypatch.setattr(s,'_json',decode);monkeypatch.setattr(Path,'read_bytes',read)
    with pytest.raises(ValueError):s._inputs()


def test_all_member_hashes_checked_before_conversion(inputs,monkeypatch):
    s=module();last=s.ROOT/inputs[1][inputs[0]['available'][-1]['tsv_path']]['path'];real=Path.read_bytes
    def read(path,*args,**kwargs):return b'corrupt'if path==last else real(path,*args,**kwargs)
    monkeypatch.setattr(Path,'read_bytes',read)
    monkeypatch.setattr(s,'convert_full_hmac_payload',lambda *a:pytest.fail('Conversion before all member hashes authenticated'))
    with pytest.raises(ValueError,match='hash or size'):s.load_full_hmac_dataset()
