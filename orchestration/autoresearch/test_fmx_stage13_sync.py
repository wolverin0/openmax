"""Authenticated Stage13 views keep saved evidence and missingness distinct."""
from pathlib import Path
import json
import pytest
from orchestration.autoresearch import fmx_offline_data as core
from orchestration.autoresearch import fmx_stage13_sync as data
from orchestration.autoresearch import fmx_stage13_statistics as statistics
from copy import deepcopy
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'orchestration/autoresearch/stage13_sync_20261025'
OPTIONS=dict(manifest_path=BASE/'inputs_manifest.json',expected_manifest_sha256='916904d8d37512dfdbb1eb84de3d911731c45cf61ab3cc826b2a3b9240f258a9')


def test_additive_bench_prefix_and_overlap_are_exact():
    value=core.load_stage13_sync_dataset(**OPTIONS)
    old=json.loads((BASE/'frozen_prefix/normalized_r1_to_r169_measurements_20261024.json').read_bytes())
    assert value['records'][:430]==old['records']
    assert len(value['records'])==480 and len(value['bench_cohort'])==96
    assert len(value['overlap_rounds_verified'])==23


def test_ul_block_ids_and_absent_health_are_not_relabelled():
    value=core.load_stage13_sync_blocks(**OPTIONS)
    selected=[r for r in value['crossed']if r['round_id']=='R189']
    assert len(selected)==32 and {r['block_index']for r in selected}==set(range(1,17))
    assert {r['source_step_in_block']for r in selected}=={1,2}
    assert all(r['reported_block_health']['restoration_ok']is None for r in selected)
    assert all(r['tid_counters']is None and r['hmac_source_controls']['fq_flows']is None for r in selected)


def test_multiradio_aggregates_do_not_become_bench_blocks():
    value=core.load_stage13_multiradio_packages(**OPTIONS)
    assert len(value['packages'])==110 and sum(len(p['phases'])for p in value['packages'])==440
    assert all(p['inference_status']=='UNAVAILABLE_PHASE_AGGREGATES_NOT_RAW_INDEPENDENT_TRIALS'for p in value['packages'])
    assert all(p['raw_rtts_ms']is None and p['paired_unit_ids']is None for p in value['packages'])


def _normalized_fixture(tmp_path,monkeypatch):
    """Disposable coherent freeze: reconstruction, rather than flags, is authority."""
    family=dict(family_size=336,metric_slots=list(statistics.METRICS),bootstrap_seed=20261025)
    manifest=dict(statistical_family_recipe={'sha256':'fixture-family'})
    prefix=dict(records=dict(records=[],source_refs=[]),blocks=dict(crossed=[],sequential=[],source_refs=[]))
    multi=[dict(round_id='SYNTHETIC',phases={'A1':{'p95':1}},source={'sha256':'source'},
                source_pointer='/rounds/0',declared_controls={'candidate_val':None})]
    expected=(manifest,prefix,[],[],[],[],[],multi,{},family)
    records=dict(records=[],source_refs=[],bench_cohort=[],multiradio_packages=deepcopy(multi))
    blocks=dict(crossed=[],sequential=[],source_refs=[],bench_cohort_crossed=[])
    monkeypatch.setattr(data,'BASE',tmp_path)
    monkeypatch.setattr(data,'authenticate',lambda **kw:(manifest,{}, {},prefix,{},family,{}))
    monkeypatch.setattr(data,'_build',lambda **kw:expected)
    monkeypatch.setattr(statistics,'dependency_bindings',lambda:[])
    paths={k:tmp_path/name for k,name in [('records','records.json'),('blocks','blocks.json'),
          ('manifest','manifest.json'),('freeze','statistics_dependency_freeze.json')]}
    def publish():
        for key,value in [('records',records),('blocks',blocks),('manifest',manifest)]:
            paths[key].write_text(json.dumps(value),encoding='utf-8')
        freeze=dict(source_inputs={k:data.binding(v)for k,v in paths.items()if k!='freeze'},
                    source_bindings=[],family_recipe=manifest['statistical_family_recipe'])
        paths['freeze'].write_text(json.dumps(freeze),encoding='utf-8')
    def call():
        publish()
        return statistics._frozen_inputs(records_path=paths['records'],blocks_path=paths['blocks'],
            manifest_path=paths['manifest'],expected_manifest_sha256='synthetic',dependency_freeze_path=paths['freeze'])
    return records,blocks,call


@pytest.mark.parametrize('field',['phase','pointer','controls','missingness','source'])
def test_statistics_rejects_tampered_multiradio_before_inference(tmp_path,monkeypatch,field):
    records,_,call=_normalized_fixture(tmp_path,monkeypatch)
    package=records['multiradio_packages'][0]
    if field=='phase':package['phases']['A1']['p95']=999
    elif field=='pointer':package['source_pointer']='/rounds/9'
    elif field=='controls':package['declared_controls']['candidate_val']=0
    elif field=='missingness':package['declared_controls']['candidate_val']='UNKNOWN'
    else:package['source']['sha256']='substituted'
    with pytest.raises(ValueError,match='MultiRadio'):
        call()


def test_statistics_accepts_exact_reconstruction_fixture(tmp_path,monkeypatch):
    records,blocks,call=_normalized_fixture(tmp_path,monkeypatch)
    actual=call()
    assert actual[0]==records and actual[1]==blocks


@pytest.mark.parametrize('kind',['records','blocks'])
def test_statistics_rejects_unbound_source_references(tmp_path,monkeypatch,kind):
    records,blocks,call=_normalized_fixture(tmp_path,monkeypatch)
    (records if kind=='records'else blocks)['source_refs'].append({'sha256':'invented'})
    with pytest.raises(ValueError,match='source references'):call()


@pytest.fixture(scope='module')
def frozen_sources():
    return data.authenticate(**OPTIONS)


def _round_fixture(frozen_sources,number):
    manifest,refs,contents,*_=frozen_sources
    item=next(i for i in manifest['available']if i['round_id']==f'R{number}')
    dependencies={name:contents[name].decode('utf-8')for name in manifest['supplementary_recipe_sources']}
    return [number,data.full._json(contents[item['receipt']]),refs[item['receipt']],refs[item['recipe']],
            contents[item['recipe']].decode('utf-8'),contents[item['tsv']].decode('utf-8'),dependencies]


@pytest.mark.parametrize('value',[True,False,'1',float('nan'),float('inf'),None])
def test_observations_require_typed_finite_numbers(value):
    with pytest.raises(ValueError):data.finite(value,'synthetic measurement')


@pytest.mark.parametrize('value',[True,False,1.0,'1',-1])
def test_source_unit_ids_are_not_coerced(value):
    with pytest.raises(ValueError):data.integer(value,'synthetic ID')


@pytest.mark.parametrize('field,value',[('slot_time_us',True),('ack_timeout_us',None),('bidirectional',1),('distance_m',4500)])
def test_shared_context_conflict_is_not_repaired_by_class(frozen_sources,field,value):
    args=_round_fixture(frozen_sources,170);payload=args[1]
    payload['iterations'][0]['candidate_knobs'][field]=value
    with pytest.raises(ValueError,match='context|direction|regime'):
        data._context(170,payload,payload['iterations'][0])


@pytest.mark.parametrize('number',[169,176,189,194])
def test_saved_schema_roundtrip_and_missing_fields(frozen_sources,number):
    args=_round_fixture(frozen_sources,number)
    records,rows=data.parse_bench_round(*args)
    assert len(records)==2 and len(rows)==32
    assert all(r['stage13_policy_key']is not None for r in records)
    assert sum(len(r['rtts_ms'])for r in rows)==sum(len(r['raw_rtts_ms'])for r in args[1]['iterations'])
    if number>=189:
        assert {r['block_index']for r in rows}==set(range(1,17))
        assert all(r['crossover_step']==r['source_step_in_block']-1 and r['schedule_lookup_index']==r['block_index']-1 for r in rows)
        assert all(r['reported_block_health']=={'restoration_ok':None,'station_reset_count':None}for r in rows)
        assert all(r['recipe_control_audit']['actual_declared_controls']['recipe_declared_endpoint_htt_pairs']is None for r in records)
    if number==176:
        assert [r['recipe_control_audit']['actual_declared_controls']['recipe_declared_rts_threshold']for r in records]==['off',256]
        assert all(r['recipe_control_audit']['causal_isolation_verified']is False for r in records)


@pytest.mark.parametrize('mutation',['duplicate_ID','mixed_step','lost_sample','bool_counter','health_type'])
def test_malformed_saved_blocks_fail_closed(frozen_sources,mutation):
    args=_round_fixture(frozen_sources,189 if mutation=='mixed_step'else 170)
    blocks=args[1]['iterations'][0]['repetition_blocks']
    if mutation=='duplicate_ID':blocks[1]['block_index']=blocks[0]['block_index']
    elif mutation=='mixed_step':blocks[0]['crossover_step']=0
    elif mutation=='lost_sample':blocks[0]['rtts_ms']=blocks[0]['rtts_ms'][:-1]
    elif mutation=='bool_counter':blocks[0]['mac_tx_packets_delta']=True
    else:blocks[0]['observation']['restoration_ok']=0
    with pytest.raises(ValueError):data.parse_bench_round(*args)


def test_unknown_setter_retains_measurements_without_control_identity(frozen_sources):
    args=_round_fixture(frozen_sources,170)
    args[4]=args[4].replace('echo 1 > /sys/kernel/debug/ieee80211/phy0/ath10k/ani_enable',
                            'echo 0 > /sys/kernel/debug/ieee80211/phy0/ath10k/ani_enable')
    assert 'echo 0 > /sys/kernel/debug/ieee80211/phy0/ath10k/ani_enable'in args[4]
    records,rows=data.parse_bench_round(*args)
    assert len(records)==2 and len(rows)==32
    assert all(r['stage13_policy_key']is None and r['recipe_control_audit']['control_attribution']=='UNSUPPORTED_SETTER_ATTRIBUTION'for r in records)


def test_policy_identity_ignores_labels_but_retains_real_controls(frozen_sources):
    args=_round_fixture(frozen_sources,170);payload=args[1]
    original=data._recipe_audit(170,args[4],payload,args[6])
    for item in payload['iterations']:
        item['candidate_knobs']['name']='SYNTHETIC_TITLE_NOT_A_CONTROL'
        item['candidate_knobs']['description']='no effective authority'
        item['candidate_knobs']['complexity_cost']=999
    renamed=data._recipe_audit(170,args[4],payload,args[6])
    assert [x['stage13_policy_key']for x in original]==[x['stage13_policy_key']for x in renamed]
    identity=json.loads(original[0]['stage13_policy_key'])
    assert identity['endpoint_controls']['ap']['tcp_notsent_lowat']==4294967295


@pytest.mark.parametrize('value',[0,None,True])
def test_missing_or_invalid_retry_denominator_never_imputes_zero(value):
    row=dict(counter_interface='phy0-ap0.sta1',mac_tx_packets_delta=value,mac_tx_retries_delta=0)
    with pytest.raises(ValueError):statistics.metric_value(row,'wds_retry_fraction')


def test_pairing_requires_round_scoped_source_ids(frozen_sources):
    records,rows=data.parse_bench_round(*_round_fixture(frozen_sources,189))
    control,target=[r['iteration']for r in records]
    pairs=statistics.pair_rows(rows,control,target,'goodput_mbps')
    assert [p['block_index']for p in pairs]==list(range(1,17))
    assert {p['sequence']for p in pairs}=={'AB','BA'}
    rows[0]['round_id']='R190'
    with pytest.raises(ValueError,match='mixed-round'):statistics.pair_rows(rows,control,target,'goodput_mbps')


def test_unidirectional_alias_is_verified_not_guessed(frozen_sources):
    records,rows=data.parse_bench_round(*_round_fixture(frozen_sources,189))
    result=statistics.alias_audit(records,rows)
    assert result['inapplicable_metrics']==['ul_goodput_mbps','jain_fairness']
    rows[0]['dl_goodput_mbps']=1
    with pytest.raises(ValueError,match='alias'):statistics.alias_audit(records,rows)


@pytest.mark.parametrize('changes',[{'round_id':False},{'phases':{'A1':{},'B1':{}}},
    {'phases':{k:{'throughput':True}for k in ('A1','B1','A2','B2')}},
    {'phases':{k:{'throughput':float('nan')}for k in ('A1','B1','A2','B2')}}])
def test_multiradio_aggregate_types_do_not_fabricate_trials(changes):
    args=dict(round_id='SYNTHETIC',source={},source_pointer='/rounds/0',phases={k:{}for k in ('A1','B1','A2','B2')},
              declared_controls={},saved_summary={},source_metadata={})
    args.update(changes)
    with pytest.raises(ValueError):data.MultiRadioAggregatePackage(**args)


def test_manifest_bad_pin_rejected_before_read(monkeypatch):
    def forbidden(*a,**kw):raise AssertionError('No source read allowed for a bad manifest pin')
    monkeypatch.setattr(Path,'read_bytes',forbidden)
    with pytest.raises(ValueError,match='manifest pin'):
        data.authenticate(manifest_path='not_opened.json',expected_manifest_sha256='0'*64)


def test_frozen_source_hash_mismatch_is_not_a_status_override(tmp_path):
    path=tmp_path/'source.json';path.write_bytes(b'{}')
    with pytest.raises(ValueError,match='SHA256'):
        data._bound(path,{'bytes':2,'sha256':'0'*64,'accepted':True})


@pytest.mark.parametrize('raw',['//offline.invalid/share/x','/\\offline.invalid\\share\\x','\\/offline.invalid/share/x'])
def test_remote_path_rejected_before_any_filesystem_probe(monkeypatch,raw):
    def forbidden(*a,**kw):raise AssertionError('No remote probe permitted')
    monkeypatch.setattr(Path,'lstat',forbidden)
    with pytest.raises(ValueError):data.full._safe_path(raw)


def test_future_round_fails_before_source_inspection():
    with pytest.raises(ValueError,match='cutoff'):
        data.parse_bench_round(195,None,None,None,None,None,None)


def test_cli_exclusively_dispatches_stage13_help_without_inference():
    module=ROOT/'orchestration/autoresearch/fmx_statistical_audit.py'
    result=subprocess.run([sys.executable,'-B',str(module),'--campaign','STAGE13_SYNC','--help'],
        cwd=ROOT,capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stderr
    assert '--dependency-freeze'in result.stdout and '--records'in result.stdout
    assert 'STAGE13_SYNC'in result.stdout
