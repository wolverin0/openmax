"""Saved R147-R169 integration without acquisition or unqualified advice."""
from pathlib import Path
import importlib
import json
from copy import deepcopy
from dataclasses import replace
import hashlib
import ast
import csv
import io
import pytest


def module():return importlib.import_module('orchestration.autoresearch.fmx_incremental_hmac_dataset')


def test_authenticated_increment_preserves_complete_R146_prefix():
    s=module();data=s.load_incremental_hmac_dataset();blocks=s.load_incremental_hmac_blocks()
    before=json.loads(s.PREFIX_RECORDS.read_bytes());oldblocks=json.loads(s.PREFIX_BLOCKS.read_bytes())
    assert len(data['records'])==430 and len(blocks['crossed'])==4476
    assert data['records'][:384]==before['records']
    assert data['source_refs'][:len(before['source_refs'])]==before['source_refs']
    assert blocks['crossed'][:3740]==oldblocks['crossed']and blocks['sequential']==oldblocks['sequential']
    assert data['rejected_rounds']==[]and len(data['new_round_audits'])==23


def test_all_advice_is_blocked_and_timing_is_never_imputed():
    s=module();audit=s.audit_incremental_hmac_packages()
    assert len(audit['packages'])==35 and len(audit['new_packages'])==23
    assert all(p['status']=='BLOCKED'for p in audit['packages'])
    result=s.select_incremental_hmac_policy(distance_meters=1000,coverage_class=2,slot_time_us=15,ack_timeout_us=36)
    assert result['status']=='ABSTAIN'and result['recommended_policy']is None
    assert all(p['declared_ack_timeout_us']==36 for p in result['recorded_packages'])


def test_wrong_pin_rejected_before_filesystem_access(monkeypatch):
    s=module();monkeypatch.setattr(Path,'read_bytes',lambda *args:pytest.fail('Bad pin reached content'))
    with pytest.raises(ValueError):s.load_incremental_hmac_dataset(expected_manifest_sha256='0'*64)


@pytest.fixture(scope='module')
def inputs():
    s=module();return s._inputs(s.MANIFEST,s.MANIFEST_SHA256)


def source(inputs,number):
    s=module();manifest,refs,contents,*_=inputs
    item=next(i for i in manifest['available']if i['round_id']==f'R{number}')
    return (deepcopy(s.full._json(contents[item['receipt']])),refs[item['receipt']],refs[item['recipe_paths'][0]],
            contents[item['recipe_paths'][0]].decode(),contents[item['tsv_path']].decode())


@pytest.fixture(scope='module')
def actual():
    return module().load_incremental_hmac_dataset()


@pytest.fixture(scope='module')
def advice():
    return module().audit_incremental_hmac_packages()


def test_all_member_hashes_are_checked_before_any_conversion(inputs,monkeypatch):
    s=module();last=inputs[0]['members'][-1]['frozen_path'];read=Path.read_bytes
    def corrupt(path):
        value=read(path)
        return value+b' 'if path==s.full._safe_path(last)else value
    monkeypatch.setattr(Path,'read_bytes',corrupt)
    monkeypatch.setattr(s,'convert_incremental_hmac_payload',lambda *a:pytest.fail('Conversion before all member hashes'))
    with pytest.raises(ValueError,match='SHA256'):s.load_incremental_hmac_dataset()


def test_prefix_hashes_are_checked_before_conversion(monkeypatch):
    s=module();read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b' 'if p==s.PREFIX_BLOCKS else read(p))
    monkeypatch.setattr(s,'convert_incremental_hmac_payload',lambda *a:pytest.fail('Unbound prefix conversion'))
    with pytest.raises(ValueError,match='SHA256'):s.load_incremental_hmac_blocks()


@pytest.mark.parametrize('mutation',[
    lambda m:m['members'][0].update(path='../escape.json'),
    lambda m:m['members'][0].update(path='artifacts/source_r170_future.json',round_id='R170'),
    lambda m:m['members'][0].update(frozen_path='//remote.invalid/share/member'),
    lambda m:m['members'][0].update(bytes=True),
    lambda m:m['members'][0].update(sha256='invalid'),
    lambda m:m['members'][0].update(kind='unknown'),
    lambda m:m['members'].__setitem__(1,deepcopy(m['members'][0])),
    lambda m:m['available'][0].update(recipe_paths=[]),
    lambda m:m['available'][0].update(receipt=m['available'][1]['receipt']),
    lambda m:m['prefix']['records'].update(sha256='0'*64),
    lambda m:m['prefix']['blocks'].update(path='other_local_file.json'),
    lambda m:m.update(planned_rounds=list(range(147,171))),
])
def test_manifest_shape_and_historical_anchor_preflight_before_member_content(inputs,mutation,monkeypatch):
    s=module();manifest=deepcopy(inputs[0]);mutation(manifest)
    decode=s.full._json;read=Path.read_bytes;manifest_bytes=read(s.MANIFEST)
    monkeypatch.setattr(s.full,'_json',lambda raw:manifest if raw==manifest_bytes else decode(raw))
    def no_members(path):
        if path!=s.MANIFEST:pytest.fail('Invalid structure reached member or prefix content')
        return read(path)
    monkeypatch.setattr(Path,'read_bytes',no_members)
    with pytest.raises(ValueError):s.load_incremental_hmac_dataset()


@pytest.mark.parametrize('path',['../escape.json','//offline.invalid/share/m.json',r'/\offline.invalid\share\m.json',r'\/offline.invalid/share/m.json','https://invalid/m.json','C:relative.json'])
def test_unsafe_manifest_paths_reject_before_any_filesystem_probe(monkeypatch,path):
    s=module()
    for method in ('lstat','resolve','read_bytes'):
        monkeypatch.setattr(Path,method,lambda *a,**k:pytest.fail('Unsafe path reached filesystem'))
    with pytest.raises(ValueError):s.load_incremental_hmac_dataset(manifest_path=path)


@pytest.mark.parametrize('number',[True,146,170,'147',147.0])
def test_future_or_wrong_typed_round_rejected_before_payload_access(number):
    with pytest.raises(ValueError):module().convert_incremental_hmac_payload(number,None,None,None,None,None)


@pytest.mark.parametrize('text',['{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}'])
def test_strict_json_rejects_duplicate_or_nonfinite(text):
    with pytest.raises(ValueError):module().full._json(text)


@pytest.mark.parametrize('number',range(147,170))
def test_actual_branch_selection_uses_each_recipe_and_saved_readback(inputs,number):
    s=module();payload,_,_,text,_=source(inputs,number)
    parsed=s.recipe_incremental_controls(text,payload)
    expected=64 if 165<=number<=168 else 16 if number in (150,151,152,156,157,158,162,163,164)else 32
    for item in payload['iterations']:
        result=parsed[item['commit']];value=expected if item['candidate_knobs']['force_tx_status']else 64
        assert result['declared_endpoint_pairs']=={'ap':[3,value],'cpe':[3,value]}
        assert all(result['readback_text_matches_declaration'].values())
        assert result['feedback_adaptive_control_verified']is False


def test_saved_readback_missing_is_unknown_without_fabricating_htt(inputs):
    s=module();payload,_,_,text,_=source(inputs,169)
    payload['iterations'][1]['readback']['ap_readback']=None
    parsed=s.recipe_incremental_controls(text,payload)[payload['iterations'][1]['commit']]
    assert parsed['declared_endpoint_pairs']['ap']==[3,32]
    assert parsed['readback_status']=='UNKNOWN_OR_CONFLICTING_SAVED_TEXT'
    assert parsed['readback_text_pairs']['ap']==[]


def test_scalar_readback_lines_cannot_masquerade_as_pair(inputs):
    s=module();payload,_,_,text,_=source(inputs,169)
    payload['iterations'][1]['readback']['ap_readback']='3\n32\n'
    parsed=s.recipe_incremental_controls(text,payload)[payload['iterations'][1]['commit']]
    assert not parsed['readback_text_matches_declaration']['ap']


@pytest.mark.parametrize('mutation',['extra_command','caller','branch','unknown_endpoint','unknown_shared'])
def test_unsupported_commands_or_controls_are_explicitly_rejected(inputs,mutation):
    s=module();payload,ref,recipe,text,tsv=source(inputs,165)
    if mutation=='extra_command':text=text.replace('echo 1 >','echo 9 >',1)
    elif mutation=='caller':text=text.replace('_peer_extra(pair.cpe_state)','_peer_extra(pair.ap_state)')
    elif mutation=='branch':text=text.replace('echo "3 64"','echo "3 48"',1)
    elif mutation=='unknown_endpoint':payload['iterations'][0]['candidate_knobs']['ap_state']['unknown_hook']=1
    else:payload['iterations'][0]['candidate_knobs']['unknown_hook']=1
    with pytest.raises(ValueError):s.convert_incremental_hmac_payload(165,payload,ref,recipe,text,tsv)


def test_unsupported_package_is_rejected_with_provenance_never_silently_dropped(monkeypatch):
    s=module();convert=s.convert_incremental_hmac_payload
    def unsupported(n,*a):
        if n==165:raise ValueError('Synthetic unsupported declared control')
        return convert(n,*a)
    monkeypatch.setattr(s,'convert_incremental_hmac_payload',unsupported)
    data=s.load_incremental_hmac_dataset()
    assert len(data['records'])==428 and len(data['new_round_audits'])==22
    assert len(data['rejected_rounds'])==1
    rejected=data['rejected_rounds'][0]
    assert rejected['round_id']=='R165'and rejected['receipt']['sha256']and rejected['recipe']['sha256']


@pytest.mark.parametrize('field,value',[('active_flow_count',True),('active_flow_count',8.0),('bidirectional',1),('distance_m',6000.0),('coverage_class',True),('slot_time_us',None),('ack_timeout_us',48)])
def test_shared_context_conflicts_reject(inputs,field,value):
    s=module();payload,ref,recipe,text,tsv=source(inputs,165)
    payload['iterations'][1]['candidate_knobs'][field]=value
    with pytest.raises(ValueError):s.convert_incremental_hmac_payload(165,payload,ref,recipe,text,tsv)


@pytest.mark.parametrize('field,value',[('tx_aggr_factor',True),('tx_aggr_factor',2),('fq_flows',False),('force_tx_status',True)])
def test_literal_control_types_and_derived_af_alias_reject(inputs,field,value):
    s=module();payload,ref,recipe,text,tsv=source(inputs,168)
    payload['iterations'][1]['candidate_knobs'][field]=value
    with pytest.raises(ValueError):s.convert_incremental_hmac_payload(168,payload,ref,recipe,text,tsv)


@pytest.mark.parametrize('mutation',['step','block_restoration','block_reset','negative_tid','zero_denominator'])
def test_block_identity_health_and_counters_fail_closed_or_remain_unknown(inputs,mutation):
    s=module();payload,ref,recipe,text,tsv=source(inputs,165)
    block=payload['iterations'][0]['repetition_blocks'][0]
    if mutation=='step':block['crossover_step']=True
    elif mutation=='block_restoration':block['observation']['restoration_ok']='false'
    elif mutation=='block_reset':block['observation']['station_reset_count']=True
    elif mutation=='negative_tid':block['tid0_be_tx_pkts_delta']=-1
    else:block['mac_tx_packets_delta']=0
    if mutation=='zero_denominator':
        # Unknown denominator may be retained by legacy accounting, never safe zero-rate evidence.
        try:_,blocks,_=s.convert_incremental_hmac_payload(165,payload,ref,recipe,text,tsv)
        except ValueError:return
        assert blocks[0].get('mac_retry_rate_from_counters')is None
    else:
        with pytest.raises(ValueError):s.convert_incremental_hmac_payload(165,payload,ref,recipe,text,tsv)


def test_labels_and_costs_do_not_create_policy_or_isolation_coordinates(inputs):
    s=module();payload,ref,recipe,text,tsv=source(inputs,165)
    before=s.convert_incremental_hmac_payload(165,payload,ref,recipe,text,tsv)
    for item in payload['iterations']:
        item['experiment_ref']='SGI GOLDEN POLICY NAME ONLY'
        for state in [item['candidate_knobs'],item['candidate_knobs']['ap_state'],item['candidate_knobs']['cpe_state']]:
            state.update(name='renamed',description='not authority',complexity_cost=987)
    # Metadata must remain consistent with its source declaration; that binding
    # is separate from whether the metadata belongs in the policy identity.
    tree=ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node,ast.Call)and isinstance(node.func,ast.Name)and node.func.id=='R11CrossLayerKnobState':
            for keyword in node.keywords:
                if keyword.arg in ('name','description','complexity_cost'):
                    keyword.value=ast.Constant(987 if keyword.arg=='complexity_cost'else'renamed'if keyword.arg=='name'else'not authority')
    text=ast.unparse(tree)
    table=list(csv.DictReader(io.StringIO(tsv),delimiter='\t'))
    for row in table:row['description']='not authority'
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=list(table[0]),delimiter='\t')
    writer.writeheader();writer.writerows(table);tsv=stream.getvalue()
    after=s.convert_incremental_hmac_payload(165,payload,ref,recipe,text,tsv)
    assert [r['policy_key']for r in before[0]]==[r['policy_key']for r in after[0]]
    assert before[2]['literal_control_deltas']==after[2]['literal_control_deltas']
    assert before[0][0]['source_candidate_metadata']!=after[0][0]['source_candidate_metadata']


def test_titles_do_not_separate_identical_observed_packages(actual):
    rows={(r['round_id'],r['source_position']):r for r in actual['records'][384:]}
    assert rows['R147','/iterations/1']['policy_key']==rows['R153','/iterations/1']['policy_key']


def test_actual_isolation_claims_keep_additional_dscp_threshold_ftx_and_both_endpoints(advice):
    by={p['round_id']:p for p in advice['new_packages']}
    coords=lambda n:{v['coordinate']for v in by[f'R{n}']['literal_control_deltas']}
    assert '/candidate_knobs/ap_state/dscp_micro_vo_steering'in coords(165)
    assert '/candidate_knobs/cpe_state/aql_threshold_us'in coords(165)
    assert coords(166)=={'/candidate_knobs/ap_state/fq_quantum_bytes','/candidate_knobs/cpe_state/fq_quantum_bytes'}
    assert len(coords(167))==4
    assert '/candidate_knobs/force_tx_status'in coords(169)
    assert '/recipe_declared_htt_max_amsdu_ampdu/ap'in coords(169)
    for p in by.values():assert p['status']=='BLOCKED'


def test_losses_and_optimizer_labels_are_not_erased_or_promoted(actual,advice):
    blocks=module().load_incremental_hmac_blocks()['crossed'][3740:]
    assert sum(b['pings_sent']for b in blocks)==7360
    assert sum(b['pings_rcvd']for b in blocks)==7351
    rows=[r for r in actual['records'][384:]if r['source_position']=='/iterations/1']
    assert {r['round_id']for r in rows if r['packet_loss_pct']>0}=={'R159','R166'}
    assert {p['round_id']for p in advice['new_packages']if not p['utility']['observed_total_goodput_drop_strictly_below_2pct']}=={'R150','R151','R157','R158','R164','R168'}
    assert next(p for p in advice['packages']if p['round_id']=='R144')['utility']['observed_total_goodput_drop_strictly_below_2pct']is False
    assert advice['packages'][:12]==json.loads((module().ROOT/module().PREFIX['package_audit']['path']).read_bytes())['packages']


@pytest.mark.parametrize('context',sorted(set([(1000,2,15,30),*[(1000,2,15,36),(3000,6,27,48),(6000,13,48,69),(9000,20,69,90),(12000,26,87,108),(14000,31,102,123)]])))
def test_seven_observed_timing_contexts_remain_separate_and_abstain(advice,monkeypatch,context):
    s=module();monkeypatch.setattr(s,'audit_incremental_hmac_packages',lambda **k:advice)
    result=s.select_incremental_hmac_policy(**dict(zip(('distance_meters','coverage_class','slot_time_us','ack_timeout_us'),context)))
    assert result['status']=='ABSTAIN'and result['recommended_policy']is None
    assert result['recorded_packages']
    assert all(p['declared_ack_timeout_us']==context[3]for p in result['recorded_packages'])


@pytest.mark.parametrize('context',[(1000,2,15,33),(2000,2,15,36),(1000,True,15,36),(1000,2,15.0,36),(1000,2,15,None)])
def test_unknown_or_malformed_timing_queries_never_open_evidence(monkeypatch,context):
    s=module();monkeypatch.setattr(s,'audit_incremental_hmac_packages',lambda **k:pytest.fail('Invalid context reached evidence'))
    with pytest.raises(ValueError):s.select_incremental_hmac_policy(**dict(zip(('distance_meters','coverage_class','slot_time_us','ack_timeout_us'),context)))


@pytest.mark.parametrize('target,accepted',[('98',False),('98.0000001',True),('97.9999999',False),('101',True)])
def test_strict_goodput_boundary_is_exact_descriptive_not_noninferiority(target,accepted):
    result=module()._utility(100,target)
    assert result['observed_total_goodput_drop_strictly_below_2pct']is accepted
    assert result['causal_noninferiority_established']is False


def test_persisted_metadata_order_is_independent_of_set_iteration(inputs,monkeypatch):
    s=module();payload,ref,recipe,text,tsv=source(inputs,165)
    class OrderedMetadata(set):
        reverse=False
        def __iter__(self):
            return iter(sorted(super().__iter__(),reverse=self.reverse))
    metadata=OrderedMetadata(s._METADATA)
    monkeypatch.setattr(s,'_METADATA',metadata)
    forward=s.convert_incremental_hmac_payload(165,payload,ref,recipe,text,tsv)
    metadata.reverse=True
    reverse=s.convert_incremental_hmac_payload(165,payload,ref,recipe,text,tsv)
    expected=sorted(metadata)
    for rows,_,audit in (forward,reverse):
        assert all(list(r['source_candidate_metadata'])==expected for r in rows)
        assert all(list(labels)==expected for labels in audit['reported_candidate_labels'])
    assert json.dumps(forward,allow_nan=False)==json.dumps(reverse,allow_nan=False)
