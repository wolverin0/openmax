"""Additive frozen BQ-CF ingestion contracts; no acquisition imports."""
from orchestration.autoresearch import fmx_live_dataset as live
from orchestration.autoresearch import fmx_offline_data as old
from copy import deepcopy
from dataclasses import asdict, replace
import json
import ast
from pathlib import Path
import pytest


def test_new_revision_interfaces_exist_without_widening_historical_contract():
    assert callable(live.load_all134_measurements)
    assert callable(live.load_all107_block_observations)


def test_ul_hammer_keeps_eight_flow_identity_and_directional_alias():
    result = old.audit_directional_throughput('unidir_ul_8flow_hammer', total=5, dl=0, ul=5,
        jain=.5, blocks=[dict(observation=dict(goodput_rx_mbps=5,jain_fairness=.5),
                             dl_goodput_mbps=0,ul_goodput_mbps=5)])
    assert result['regime'] == 'unidir_ul_8flow_hammer'
    assert result['active_direction'] == 'UL'


@pytest.fixture(scope='module')
def campaign():
    return live._new_data134()


@pytest.fixture(scope='module')
def sources():
    m=live._inputs134()
    return {n:{Path(e['path']).suffix:e for e in m['entries'] if e['round']==n}
            for n in live.ROUND134_SPECS}


def raw(sources,n=122):
    entries=sources[n]
    return live._json(live.ROOT/entries['.json']['path'])


def recipe(sources,n=122):
    return (live.ROOT/sources[n]['.py']['path']).read_text(encoding='utf-8')


def test_actual_available_missing_counts_and_all_exact_identities(campaign):
    rows,blocks,refs,audits=campaign
    assert (len(rows),len(blocks),len(refs))==(76,1216,38)
    assert len({(b['round_id'],b['block_index'])for b in blocks})==608
    assert sum(len(r.rtts_ms)for r in rows)==12160
    assert {a['round_id']for a in audits if a['status']=='UNKNOWN_LOCAL_MEASUREMENT_ARTIFACT_ABSENT'}=={'R110','R111','R112','R113'}
    assert not any(a['status']=='BLOCKED_SOURCE_CONFLICT'for a in audits)
    assert all(e['path'].startswith(live.BQCF_ARTIFACTS.relative_to(live.ROOT).as_posix()+'/inputs/')for e in refs)
    assert all(r.certified_wds_evidence['source_package_effective_actuation_verified']is False for r in rows)
    assert sum(r.dyadic_mean_audit['all_zero_ulp']for r in rows)==76


def test_new_contexts_policy_full_tsq_and_literal_controls(campaign):
    rows=campaign[0]
    a=next(r for r in rows if r.round_id=='R120'and '_iter1_'in r.iteration)
    assert (a.distance_meters,a.coverage_class)==(12000,26)
    assert a.certified_wds_evidence['slot_time_us']==87
    b=next(r for r in rows if r.round_id=='R134'and '_iter1_'in r.iteration)
    assert (b.workload_regime,b.active_flow_count,b.bidirectional)==('unidir_ul_8flow_hammer',8,False)
    assert b.cpe_policy.tcp_notsent_lowat==4294967295
    key=json.loads(b.policy_key)
    assert key[0]['new_source_controls']==dict(rts_threshold='off',ap_ack_clocking=False)
    assert key[1]['new_source_controls']==dict(rts_threshold='off')
    c=next(r for r in rows if r.round_id=='R122'and '_iter1_'in r.iteration)
    assert c.ap_policy.rts_threshold==c.cpe_policy.rts_threshold==256
    assert next(r for r in rows if r.round_id=='R121').new_source_controls=={}
    assert 'new_source_controls'not in json.loads(next(r for r in rows if r.round_id=='R121').policy_key)[0]


@pytest.mark.parametrize('field,value',[('active_flow_count',2),('active_flow_count',True),('bidirectional',True),
    ('distance_meters',3000.),('distance_meters',6000),('coverage_class',True),('coverage_class',13),('round_id','R135')])
def test_typed_hammer_context_is_not_label_only(campaign,field,value):
    row=next(r for r in campaign[0] if r.round_id=='R122')
    with pytest.raises(ValueError):replace(row,**{field:value})


@pytest.mark.parametrize('controls',[None,[],{'unknown':1},{'rts_threshold':False},{'rts_threshold':'0256'},
    {'rts_threshold':'0'},{'rts_threshold':'65536'},{'rts_threshold':'OFF'},{'ap_ack_clocking':1}])
def test_literal_new_control_types_fail_closed(campaign,controls):
    row=next(r for r in campaign[0] if r.round_id=='R122')
    with pytest.raises(ValueError):replace(row,new_source_controls=controls)


@pytest.mark.parametrize('n',[103,107,108,115,122,134])
def test_explicit_period_adapter_roundtrip_abba_and_no_health_imputation(sources,n):
    payload=raw(sources,n); before=deepcopy(payload)
    blocks=old._exact_campaign_block_rows(payload,max_round=134)
    assert payload==before
    assert len(blocks)==32
    assert {b['source_step_field']for b in blocks}=={'step_in_block'}
    assert all(b['source_step_in_block']==b['crossover_step']+1 for b in blocks)
    assert sum(b['crossover_step']==0 and b['treatment_id']==payload['iterations'][0]['commit']for b in blocks)==8
    for b in blocks:
        original=next(x for a in payload['iterations'] if a['commit']==b['treatment_id']for x in a['repetition_blocks']if x['block_index']==b['block_index'])
        if 'observation'not in original:
            assert 'restoration_verified'not in b['observation']


@pytest.mark.parametrize('step',[True,1.,0,3,None])
def test_bad_one_based_period_never_becomes_valid_coordinate(sources,step):
    payload=raw(sources,103);payload['iterations'][0]['repetition_blocks'][0]['step_in_block']=step
    with pytest.raises(ValueError):old._exact_campaign_block_rows(payload,max_round=134)


def test_contradictory_and_mixed_coordinates_rejected(sources):
    payload=raw(sources,103);block=payload['iterations'][0]['repetition_blocks'][0]
    block['crossover_step']=block['step_in_block']%2
    with pytest.raises(ValueError):old._exact_campaign_block_rows(payload,max_round=134)
    block['crossover_step']=block['step_in_block']-1
    with pytest.raises(ValueError):old._exact_campaign_block_rows(payload,max_round=134)


@pytest.mark.parametrize('level',[0,1,2])
@pytest.mark.parametrize('field,value',[('coverage_class',True),('distance_m',1000.0),('slot_time_us',31),
    ('ack_timeout_us',True),('active_flow_count',2),('bidirectional',True),('traffic_regime','unidir_ul_2flow')])
def test_each_shared_declaration_level_is_typed_and_matches_source(sources,level,field,value):
    payload=raw(sources);item=payload['iterations'][1]
    (payload,item,item['candidate_knobs'])[level][field]=value
    with pytest.raises(ValueError):live._context(122,payload,item,catalog=live.ROUND134_SPECS)


def test_recipe_filename_is_documentary_but_actual_contents_binding_is_strict(sources):
    payload=raw(sources,115);text=recipe(sources,115)
    assert 'covclass6_3000m'in sources[115]['.py']['original_path']
    assert live._recipe_context86(text,2)['both_endpoints_declared']is True
    live._literal_recipe_packages(text,payload)
    with pytest.raises(ValueError):live._recipe_context86(text.replace('set coverage 2 ','set coverage 6 '),2)
    with pytest.raises(ValueError):live._literal_recipe_packages(text.replace('be_low_us=1550','be_low_us=1900'),payload)


def test_recipe_no_execution_and_missing_endpoint_prep_rejected(sources):
    text=recipe(sources,122)
    # Mutate actual AST callsites, independent of the source's multiline layout.
    for kind in ('prep','reset'):
        tree=ast.parse(text);changed=0
        for call in ast.walk(tree):
            if not isinstance(call,ast.Call)or not isinstance(call.func,ast.Name)or call.func.id!='rpc'or len(call.args)<2:
                continue
            if ast.unparse(call.args[0])!='b.client':continue
            second=ast.unparse(call.args[1])
            if (kind=='prep'and 'prep_cmd'in second)or(kind=='reset'and 'set coverage 0'in second):
                call.args[0]=ast.Attribute(value=ast.Name(id='b',ctx=ast.Load()),attr='ap',ctx=ast.Load());changed+=1
        assert changed==1
        with pytest.raises(ValueError):live._recipe_context86(ast.unparse(tree),6)


@pytest.mark.parametrize('key,value',[('rts_threshold','off'),('ap_ack_clocking',1)])
def test_json_and_recipe_control_declarations_cannot_disagree(sources,key,value):
    payload=raw(sources);payload['iterations'][1]['candidate_knobs'][key]=value
    with pytest.raises(ValueError):live._literal_recipe_packages(recipe(sources),payload)


def test_tsv_is_a_rounded_projection_not_replacement_metrics(sources):
    payload=raw(sources,93);text=(live.ROOT/sources[93]['.tsv']['path']).read_text()
    assert live._audit_tsv134(text,payload)['source_repaired']is False
    with pytest.raises(ValueError):live._audit_tsv134(text.replace('67.54','67.55'),payload)


def test_one_source_conflict_does_not_fabricate_or_block_independent_rounds(monkeypatch,sources):
    read=live._json;bad=live.ROOT/sources[115]['.json']['path']
    def changed(path):
        result=read(path)
        if Path(path)==bad:result['iterations'][0]['coverage_class']=6
        return result
    monkeypatch.setattr(live,'_json',changed)
    rows,blocks,_,audits=live._new_data134()
    assert len(rows)==74 and len(blocks)==1184
    assert not any(r.round_id=='R115'for r in rows)
    assert next(a for a in audits if a['round_id']=='R115')['status']=='BLOCKED_SOURCE_CONFLICT'
    assert any(r.round_id=='R134'for r in rows)


@pytest.mark.parametrize('scope',[135,136,True,134.,'134',110])
def test_future_or_unsupported_scope_rejected_before_any_content(monkeypatch,scope):
    monkeypatch.setattr(live,'_json',lambda *args:pytest.fail('No content read allowed'))
    with pytest.raises(ValueError):live.load_live_dataset(through_round=scope)
    with pytest.raises(ValueError):live.load_crossed_dataset(through_round=scope)


@pytest.mark.parametrize('copy',['../outside','/absolute','C:/outside','artifacts/autoresearch/../../outside',None,False])
def test_frozen_copy_path_never_falls_back_to_original(monkeypatch,copy):
    read=live._json
    def altered(path):
        result=read(path)
        if Path(path)==live.BQCF_INPUT_MANIFEST:result['entries'][0]['copy']=copy
        return result
    monkeypatch.setattr(live,'_json',altered)
    with pytest.raises(ValueError):live._inputs134()


def test_frozen_hash_drift_cannot_be_a_per_round_skip(monkeypatch,sources):
    bind=live._binding;bad=live.ROOT/sources[93]['.json']['path']
    def changed(path):
        result=bind(path)
        if Path(path)==bad:result['sha256']='0'*64
        return result
    monkeypatch.setattr(live,'_binding',changed)
    with pytest.raises(ValueError):live._new_data134()


@pytest.mark.parametrize('revision',[56,60,65,70,75,80,86,92])
def test_all_eight_historical_serialized_pairs_are_byte_identical(revision):
    encode=lambda value:(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
    assert encode(live.load_live_dataset(through_round=revision))==getattr(live,f'R{revision}_RECORDS_OUTPUT').read_bytes()
    assert encode(live.load_crossed_dataset(through_round=revision))==getattr(live,f'R{revision}_BLOCKS_OUTPUT').read_bytes()


def test_latest_schema_preserves284_records2140_blocks_and16sequential():
    data=live.load_live_dataset();blocks=live.load_crossed_dataset()
    assert (len(data['records']),len(blocks['crossed']),len(blocks['sequential']))==(360,3356,16)
    prior=live._sealed92(live.R92_RECORDS_OUTPUT);pb=live._sealed92(live.R92_BLOCKS_OUTPUT)
    assert data['records'][:284]==prior['records']
    assert blocks['crossed'][:2140]==pb['crossed']and blocks['sequential']==pb['sequential']
    assert data['automatic_execution_allowed']is False and data['physical_acceptance_claim']is False
    typed,_=live.load_all134_measurements()
    assert all(r.policy_key==item['policy_key']for r,item in zip(typed,data['records']))
