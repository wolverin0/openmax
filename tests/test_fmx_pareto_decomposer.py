"""Bound disposable evidence exercises the eleven-context strict facade."""
from copy import deepcopy
import hashlib
import json
import pytest
from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import EvidenceViewPaths,load_operator_evidence,select_operator_policy
from orchestration.autoresearch.fmx_pareto_decomposer import DISTANCE_CLASSES,WORKLOAD_REGIMES,decompose_context,decompose_distance_grid
from tests.test_fmx_multi_regime_dyadic_selector import make_as_operator_view,dump


class NoRead:
    def parse(self):raise AssertionError('Invalid request must reject before evidence access')


def bound(tmp_path,*,regime='bidir_6flow',distance=7500,round_id='R77',**kwargs):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,regime=regime,distance=distance,**kwargs)
    return load_operator_evidence(current=cfg),cfg,t,c


@pytest.mark.parametrize('distance,round_id',[(1500,'R76'),(7500,'R77'),(10500,'R78'),(13500,'R79')])
@pytest.mark.parametrize('regime',['bidir_2flow','bidir_4flow','bidir_6flow','bidir_8flow'])
def test_new_context_facade_has_guarded_synthetic_positive_path(tmp_path,distance,round_id,regime):
    evidence,_,_,_=bound(tmp_path,distance=distance,round_id=round_id,regime=regime,gp_loss=1.25)
    out=decompose_context(evidence,regime=regime,distance_meters=distance)
    assert out['status']=='ELIGIBLE_OFFLINE_STRICT_CONTEXT',out
    assert out['selected']['round_id']==round_id
    assert out['selected']['strict_literal_goodput_drop_below_2pct']
    assert out['automatic_execution_allowed'] is out['physical_acceptance'] is False


@pytest.mark.parametrize('loss,eligible',[(1.999999,True),(2,False),(2.000001,False),(-.79,True)])
def test_facade_uses_literal_strict_boundary(tmp_path,loss,eligible):
    evidence,_,_,_=bound(tmp_path,gp_loss=loss)
    parent=select_operator_policy(evidence,regime='bidir_6flow',distance_meters=7500)
    assert bool(parent['selected']) is (loss<=2)
    out=decompose_context(evidence,regime='bidir_6flow',distance_meters=7500)
    assert bool(out['selected']) is eligible,out
    if not eligible:assert 'STRICT_LITERAL_GOODPUT_DROP_NOT_BELOW_2PCT' in out['structural_profiles'][0]['reasons']


@pytest.mark.parametrize('distance',[None,True,1500.0,7501,-1,'7500'])
def test_invalid_or_unobserved_encoding_cannot_read_evidence(distance):
    out=decompose_context(NoRead(),regime='bidir_6flow',distance_meters=distance)
    assert out['status']=='BLOCKED' and out['selected'] is None


@pytest.mark.parametrize('regime',['bidir_3flow','unidir_dl_2flow',None,True])
def test_only_four_named_bidir_regimes_are_in_facade_scope(regime,tmp_path):
    # Retain the historical node ID while its authorized scope expands.
    if regime=='unidir_dl_2flow':
        evidence,_,_,_=bound(tmp_path,regime=regime,round_id='R81',distance=100)
        assert decompose_context(evidence,regime=regime,distance_meters=100)['selected'] is not None
    else:
        assert decompose_context(NoRead(),regime=regime,distance_meters=7500)['status']=='BLOCKED'


def test_future_round_scope_rejects_before_access():
    assert decompose_context(NoRead(),regime='bidir_6flow',distance_meters=7500,round_ids=['R135'])['status']=='BLOCKED'


def test_missing_cartesian_cell_never_inherits_neighbor(tmp_path):
    evidence,_,_,_=bound(tmp_path)
    out=decompose_context(evidence,regime='bidir_6flow',distance_meters=13500)
    assert out['selected'] is None and out['reason']=='NO_OBSERVED_CONTEXT'


def test_full_grid_reports_all44_cells_but_only_observed_one_can_qualify(tmp_path):
    evidence,_,_,_=bound(tmp_path,gp_loss=1.25)
    out=decompose_distance_grid(evidence)
    assert len(out['cells'])==72
    assert {(c['regime'],c['distance_meters']) for c in out['cells']}=={(r,d) for r in WORKLOAD_REGIMES for d in DISTANCE_CLASSES}
    chosen=[c for c in out['cells'] if c['selected']]
    assert [(c['regime'],c['distance_meters']) for c in chosen]==[('bidir_6flow',7500)]
    assert out['all44_cells_qualified'] is False
    assert out['physical_acceptance'] is out['automatic_execution_allowed'] is False


def test_healthy_positive_gp_cannot_rescue_nonunanimity(tmp_path):
    evidence,_,_,_=bound(tmp_path,round_id='R80',gp_loss=-.5,p50_reversal=True)
    out=decompose_context(evidence,regime='bidir_6flow',distance_meters=7500)
    assert out['selected'] is None
    assert any('NOT_16_OF_16_FAVORABLE_p50_rtt_ms' in p['reasons'] for p in out['structural_profiles'])


def test_advice_is_pinned_snapshot_and_a_fresh_load_rejects_disk_tampering(tmp_path):
    evidence,cfg,_,_=bound(tmp_path,gp_loss=1.25)
    before=decompose_context(evidence,regime='bidir_6flow',distance_meters=7500)
    assert before['selected']
    cfg.records_path.write_bytes(cfg.records_path.read_bytes()+b' ')
    assert decompose_context(evidence,regime='bidir_6flow',distance_meters=7500)==before
    assert before['evidence_freshness']=='IMMUTABLE_LOADED_SNAPSHOT_RELOAD_TO_CHECK_CURRENT_FILES'
    with pytest.raises(ValueError,match='Artifact hash/size'):
        load_operator_evidence(current=cfg)



def test_faster_inclusive_only_candidate_cannot_veto_another_strict_candidate(tmp_path):
    prior,_,_=make_as_operator_view(tmp_path,name='prior',round_id='R77',distance=7500,gp_loss=1.25)
    def faster(records,blocks,stats):
        target=next(r for r in records['records'] if r['round_id']=='R80' and r['iteration']=='target')
        old=target['policy_key'];pair=json.loads(old)
        for p in pair:p['airtime_flags']=3
        target.update(policy_key=json.dumps(pair,sort_keys=True,separators=(',',':')),airtime_flags=3,p50_ms=1,p95_ms=1,p99_ms=1,rtts_ms=[1]*160)
        for b in blocks['crossed']:
            if b['round_id']=='R80' and b['treatment_id']=='target':
                b['rtts_ms']=[1]*10
                for m in ('p50_rtt_ms','p95_rtt_ms','p99_rtt_ms'):b['observation'][m]=1
        for c in stats['promotion_evidence']['contrasts']:
            c['target_policy_id']=target['policy_key']
            if c['metric'].startswith('p'):c['effect_hl']=-3
    cfg,_,_=make_as_operator_view(tmp_path,name='current',round_id='R80',distance=7500,gp_loss=2,mutate=faster)
    records=json.loads(cfg.records_path.read_text());blocks=json.loads(cfg.blocks_path.read_text())
    records['records']+=json.loads(prior.records_path.read_text())['records']
    blocks['crossed']+=json.loads(prior.blocks_path.read_text())['crossed']
    dump(cfg.records_path,records);dump(cfg.blocks_path,blocks)
    stats=json.loads(cfg.stats_path.read_text())
    stats['promotion_evidence']['source_inputs']={k+'_sha256':hashlib.sha256(getattr(cfg,k+'_path').read_bytes()).hexdigest() for k in ('records','blocks','manifest')}
    dump(cfg.stats_path,stats)
    pins=[dict(path=str(getattr(cfg,k+'_path')),bytes=getattr(cfg,k+'_path').stat().st_size,sha256=hashlib.sha256(getattr(cfg,k+'_path').read_bytes()).hexdigest()) for k in ('records','blocks','stats','manifest')]
    pin=dump(cfg.receipt_path,{'bindings':pins})
    cfg=EvidenceViewPaths(**{**vars(cfg),'expected_receipt_sha256':pin['sha256']})
    evidence=load_operator_evidence(current=cfg,prior_views=(prior,))
    parent=select_operator_policy(evidence,regime='bidir_6flow',distance_meters=7500)
    assert parent['selected']['round_id']=='R80',parent
    strict=decompose_context(evidence,regime='bidir_6flow',distance_meters=7500)
    assert strict['selected']['round_id']=='R77',strict
    assert next(p for p in strict['structural_profiles'] if p['round_id']=='R80')['status']=='BLOCKED'


@pytest.mark.parametrize('bad',[float('nan'),float('inf'),object(),['7500']])
@pytest.mark.parametrize('field',['regime','distance_meters'])
def test_rejected_queries_have_machine_serializable_diagnostics(bad,field):
    query={'regime':'bidir_6flow','distance_meters':7500};query[field]=bad
    out=decompose_context(NoRead(),**query)
    assert out['status']=='BLOCKED' and out['selected'] is None
    json.dumps(out,allow_nan=False)


@pytest.mark.parametrize('regime,round_id',[('unidir_dl_2flow','R81'),('unidir_ul_2flow','R82')])
def test_bk_unidirectional_facade_selects_only_its_observed_active_direction(tmp_path,regime,round_id):
    evidence,_,target,_=bound(tmp_path,regime=regime,round_id=round_id,distance=100)
    out=decompose_context(evidence,regime=regime,distance_meters=100)
    assert out['status']=='ELIGIBLE_OFFLINE_STRICT_CONTEXT',out
    assert out['selected']['policy_id']==target
    assert out['pareto_metric_scope']==['goodput_rx_mbps','p95_rtt_ms','p99_rtt_ms','wds_mac_retry_rate']
    assert out['selected']['profile_contrast_scope']['complete_five_outcome_qualification'] is False
    missing=decompose_context(evidence,regime=regime,distance_meters=3000)
    assert missing['status']=='ABSTAIN' and missing['selected'] is None


def test_bk_all_six_regimes_are_explicit_and_grid_contains66_cells(tmp_path):
    assert set(WORKLOAD_REGIMES)=={'bidir_2flow','bidir_4flow','bidir_6flow','bidir_8flow','unidir_dl_2flow','unidir_ul_2flow'}
    evidence,_,_,_=bound(tmp_path,gp_loss=1.25)
    grid=decompose_distance_grid(evidence)
    assert len(grid['cells'])==72 and grid['context_count']==72
    assert grid['all66_cells_qualified'] is False
    assert len({(c['regime'],c['distance_meters'])for c in grid['cells']})==72


@pytest.mark.parametrize('regime',WORKLOAD_REGIMES)
def test_bo_unsupported_historical_class33_blocks_before_evidence_access(regime):
    out=decompose_context(NoRead(),regime=regime,distance_meters=15000)
    assert out['status']=='BLOCKED' and out['selected'] is None
    assert out['reason']=='COVERAGE_CLASS_EXCEEDS_SUPPORTED_POLICY_MAX31'
    assert out['coverage_policy']['maximum_class']==31
    assert out['coverage_policy']['hardware_ceiling_verified'] is False


def test_bo_grid_separates72_declared66_policy6_historical_cells(tmp_path):
    evidence,_,_,_=bound(tmp_path,round_id='R90',distance=14000)
    grid=decompose_distance_grid(evidence)
    assert grid['context_count']==len(grid['cells'])==72
    assert grid['supported_policy_context_count']==66
    assert grid['historical_unsupported_context_count']==6
    assert grid['declared_distance_classes'][14000]==31
    assert grid['declared_distance_classes'][15000]==33
    assert sum(c['reason']=='COVERAGE_CLASS_EXCEEDS_SUPPORTED_POLICY_MAX31' for c in grid['cells'] if c.get('reason'))==6
    assert grid['all72_cells_qualified'] is False
