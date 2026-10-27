"""Operator utility contract; immutable disposable saved-evidence fixtures."""
import pytest
import hashlib
import json
from dataclasses import replace
from pathlib import Path

from tests.test_fmx_multi_regime_dyadic_selector import make_operator_view,make_retry_preserving_view,make_as_operator_view
from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import load_operator_evidence
from orchestration.autoresearch.fmx_structural_promotion_gate import audit_operator_promotion,audit_retry_preserving_promotion


@pytest.mark.parametrize('loss,expected',[(0,True),(1.25,True),(2,False),(2.01,False)])
def test_structural_literal_less_than_two_is_stricter_than_operator_inclusive_limit(tmp_path,loss,expected):
    cfg,t,c=make_operator_view(tmp_path,round_id='R50',gp_loss=loss)
    result=audit_operator_promotion(load_operator_evidence(current=cfg),regime='bidir_6flow',
        round_id='R50',policy_id=t,control_policy_id=c)
    assert result['strict_literal_goodput_drop_below_2pct'] is expected
    assert result['status'].startswith('ELIGIBLE_') is expected
    assert not result['automatic_execution_allowed'] and not result['physical_acceptance']


def test_structural_numerical_threshold_does_not_override_packet_loss(tmp_path):
    def mutate(records,blocks,stats):records['records'][1]['packet_loss_pct']=1
    cfg,t,c=make_operator_view(tmp_path,round_id='R50',gp_loss=1.25,mutate=mutate)
    result=audit_operator_promotion(load_operator_evidence(current=cfg),regime='bidir_6flow',
        round_id='R50',policy_id=t,control_policy_id=c)
    assert result['strict_literal_goodput_drop_below_2pct']
    assert result['status']=='BLOCKED'


@pytest.mark.parametrize('loss,expected',[(1.25,True),(2,False),(2.01,False)])
def test_retry_profile_has_literal_strict_budget_without_all_five_tail_claim(tmp_path,loss,expected):
    cfg,t,c=make_retry_preserving_view(tmp_path,gp_loss=loss)
    evidence=load_operator_evidence(current=cfg)
    result=audit_retry_preserving_promotion(evidence,regime='bidir_6flow',round_id='R59',
        policy_id=t,control_policy_id=c,distance_meters=100)
    assert result['status'].startswith('ELIGIBLE_') is expected,result
    assert result['strict_literal_goodput_drop_below_2pct'] is expected
    assert result['complete_five_outcome_qualification'] is False
    assert result['paired_block_wins']['p99_rtt_ms']['wins']==15
    assert not result['automatic_execution_allowed'] and not result['physical_acceptance']
    assert audit_operator_promotion(evidence,regime='bidir_6flow',round_id='R59',policy_id=t,control_policy_id=c,
        distance_meters=100)['status']=='BLOCKED'


@pytest.mark.parametrize('round_id,regime,distance', [('R61','bidir_6flow',3000),
    ('R62','bidir_6flow',6000),('R64','bidir_4flow',100),('R65','bidir_6flow',100)])
def test_au_structural_strict_new_context_profiles(tmp_path, round_id, regime, distance):
    cfg,t,c = make_as_operator_view(tmp_path,round_id=round_id,regime=regime,distance=distance,gp_loss=1.25)
    result = audit_operator_promotion(load_operator_evidence(current=cfg),regime=regime,round_id=round_id,
        policy_id=t,control_policy_id=c,distance_meters=distance)
    assert result['status']=='ELIGIBLE_OFFLINE_STRICT_OPERATOR_PROMOTION',result
    assert result['strict_literal_goodput_drop_below_2pct']


def test_au_structural_r63_positive_goodput_cannot_override_one_p50_reversal(tmp_path):
    cfg,t,c = make_as_operator_view(tmp_path,round_id='R63',regime='bidir_8flow',distance=100,
        gp_loss=-.125,p50_reversal=True)
    result = audit_operator_promotion(load_operator_evidence(current=cfg),regime='bidir_8flow',round_id='R63',
        policy_id=t,control_policy_id=c,distance_meters=100)
    assert result['strict_literal_goodput_drop_below_2pct']
    assert result['status']=='BLOCKED'
    assert 'NOT_16_OF_16_FAVORABLE_p50_rtt_ms' in result['reasons']


@pytest.mark.parametrize('round_id,distance',[('R69',9000),('R70',4500)])
def test_ay_structural_strict_new_distance_profiles_require_all_old_gates(tmp_path,round_id,distance):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,distance=distance,gp_loss=1.25)
    result=audit_operator_promotion(load_operator_evidence(current=cfg),round_id=round_id,
        regime='bidir_6flow',policy_id=t,control_policy_id=c,distance_meters=distance)
    assert result['status'].startswith('ELIGIBLE_OFFLINE_'),result
    assert result['strict_literal_goodput_drop_below_2pct'] is True


@pytest.mark.parametrize('round_id,distance,loss',[('R68',4500,2.139503),('R70',4500,2.0)])
def test_ay_structural_new_classes_keep_literal_less_than_two(tmp_path,round_id,distance,loss):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,distance=distance,gp_loss=loss)
    result=audit_operator_promotion(load_operator_evidence(current=cfg),round_id=round_id,
        regime='bidir_6flow',policy_id=t,control_policy_id=c,distance_meters=distance)
    assert result['status']=='BLOCKED'
    assert result['strict_literal_goodput_drop_below_2pct'] is False


@pytest.mark.parametrize('round_id,distance',[('R73',12000),('R75',15000)])
@pytest.mark.parametrize('loss,eligible',[(1.25,True),(2,False)])
def test_bc_declared_distance_profiles_keep_strict_numerical_and_source_conjunction(tmp_path,round_id,distance,loss,eligible):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,distance=distance,gp_loss=loss)
    result=audit_operator_promotion(load_operator_evidence(current=cfg),round_id=round_id,
        regime='bidir_6flow',policy_id=t,control_policy_id=c,distance_meters=distance)
    assert result['status'].startswith('ELIGIBLE_OFFLINE_') is (eligible and distance!=15000),result
    assert result['strict_literal_goodput_drop_below_2pct'] is eligible
    if distance==15000:assert 'COVERAGE_CLASS_EXCEEDS_SUPPORTED_POLICY_MAX31' in result['reasons']
    assert result['automatic_execution_allowed'] is result['physical_acceptance'] is False


@pytest.mark.parametrize('round_id,distance',[('R76',1500),('R77',7500),('R78',10500),('R79',13500),('R80',7500)])
@pytest.mark.parametrize('loss,eligible',[(1.99,True),(2,False),(2.01,False),(-.79,True)])
def test_bg_new_declared_contexts_keep_structural_literal_budget(tmp_path,round_id,distance,loss,eligible):
    cfg,t,c=make_as_operator_view(tmp_path,round_id=round_id,distance=distance,gp_loss=loss)
    result=audit_operator_promotion(load_operator_evidence(current=cfg),round_id=round_id,regime='bidir_6flow',policy_id=t,control_policy_id=c,distance_meters=distance)
    assert result['status'].startswith('ELIGIBLE_OFFLINE_') is eligible,result
    assert result['strict_literal_goodput_drop_below_2pct'] is eligible
    assert result['automatic_execution_allowed'] is result['physical_acceptance'] is False


@pytest.mark.parametrize('round_id,regime,distance',[('R81','unidir_dl_2flow',100),('R82','unidir_ul_2flow',100),('R83','bidir_4flow',3000),('R84','bidir_4flow',6000),('R85','bidir_6flow',7500),('R86','bidir_4flow',9000)])
def test_bk_structural_profile_uses_applicable_outcomes_without_relaxing_budget(tmp_path,round_id,regime,distance):
    cfg,target,control=make_as_operator_view(tmp_path,round_id=round_id,regime=regime,distance=distance,gp_loss=1.25)
    out=audit_operator_promotion(load_operator_evidence(current=cfg),regime=regime,round_id=round_id,
        policy_id=target,control_policy_id=control,distance_meters=distance)
    assert out['status']=='ELIGIBLE_OFFLINE_STRICT_OPERATOR_PROMOTION',out
    if regime.startswith('unidir'):
        scope=out['profile_contrast_scope']
        assert len(scope['required_unanimous_metrics'])==4
        assert scope['complete_five_outcome_qualification'] is False
        assert 'jain_fairness' in scope['excluded_inapplicable_metrics']
    assert out['strict_literal_goodput_drop_below_2pct']
    assert out['automatic_execution_allowed'] is out['physical_acceptance'] is False


@pytest.mark.parametrize('round_id,regime',[('R81','unidir_dl_2flow'),('R82','unidir_ul_2flow')])
@pytest.mark.parametrize('fault',['active_alias','direction','flow','loss'])
def test_bk_unidirectional_profile_cannot_borrow_bidirectional_or_inactive_evidence(tmp_path,round_id,regime,fault):
    def mutate(records,blocks,stats):
        row=records['records'][0]
        if fault=='active_alias':
            opposite='ul_goodput_mbps' if regime=='unidir_dl_2flow' else 'dl_goodput_mbps'
            row[opposite]=1
            for b in blocks['crossed']:
                if b['treatment_id']=='target':b[opposite]=1
        elif fault=='direction':row['bidirectional']=True
        elif fault=='flow':row['active_flow_count']=4
        else:row['packet_loss_pct']=.01
    cfg,target,control=make_as_operator_view(tmp_path,round_id=round_id,regime=regime,distance=100,mutate=mutate)
    out=audit_operator_promotion(load_operator_evidence(current=cfg),regime=regime,round_id=round_id,
        policy_id=target,control_policy_id=control,distance_meters=100)
    assert out['status']=='BLOCKED' and out['automatic_execution_allowed'] is False


def _bk_manifest_with_copies(tmp_path, *, copy_value='VALID', documentary_path=True, drift=None):
    from tests.test_fmx_multi_regime_dyadic_selector import dump
    cfg, target, control = make_as_operator_view(tmp_path, round_id='R81', regime='unidir_dl_2flow', distance=100)
    entries = json.loads(cfg.manifest_path.read_text())
    originals = []
    for index, entry in enumerate(entries):
        original = tmp_path / f'never_read_original_{index}.json'
        originals.append(original)
        frozen = entry['path']
        if documentary_path:
            entry['path'] = str(original)
        entry['copy'] = frozen if copy_value == 'VALID' else copy_value
        if drift == 'sha256': entry['sha256'] = '0' * 64
        if drift == 'bytes': entry['bytes'] += 1
    dump(cfg.manifest_path, dict(entries=entries))
    stats = json.loads(cfg.stats_path.read_text())
    stats['promotion_evidence']['source_inputs']['manifest_sha256'] = hashlib.sha256(cfg.manifest_path.read_bytes()).hexdigest()
    dump(cfg.stats_path, stats)
    pins = [dict(path=str(path), bytes=len(path.read_bytes()), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            for path in (cfg.records_path, cfg.blocks_path, cfg.stats_path, cfg.manifest_path)]
    accepted = dump(cfg.receipt_path, dict(bindings=pins))
    return replace(cfg, expected_receipt_sha256=accepted['sha256']), entries, originals, target, control


def test_bk_explicit_frozen_copy_projects_provenance_without_reading_original(tmp_path, monkeypatch):
    cfg, entries, originals, target, control = _bk_manifest_with_copies(tmp_path)
    native_file, native_read = Path.is_file, Path.read_bytes
    def is_file(path):
        if path in originals: raise AssertionError('Documentary original was probed')
        return native_file(path)
    def read_bytes(path):
        if path in originals: raise AssertionError('Documentary original was opened')
        return native_read(path)
    monkeypatch.setattr(Path, 'is_file', is_file)
    monkeypatch.setattr(Path, 'read_bytes', read_bytes)
    evidence = load_operator_evidence(current=cfg)
    parsed = evidence.parse()[cfg.name]['manifest']
    assert [entry['path'] for entry in parsed] == [entry['copy'] for entry in entries]
    assert [entry['original_path'] for entry in parsed] == [entry['path'] for entry in entries]
    assert json.loads(cfg.manifest_path.read_text())['entries'] == entries
    result = audit_operator_promotion(evidence, regime='unidir_dl_2flow', round_id='R81',
        policy_id=target, control_policy_id=control, distance_meters=100)
    assert result['status'] == 'ELIGIBLE_OFFLINE_STRICT_OPERATOR_PROMOTION', result


@pytest.mark.parametrize('copy_value', [None, False, 0, '', '  ', 'https://example.invalid/source', '//invalid-host/share/source'])
def test_bk_present_invalid_copy_never_falls_back_to_valid_path(tmp_path, copy_value):
    cfg, _, _, _, _ = _bk_manifest_with_copies(tmp_path, copy_value=copy_value, documentary_path=False)
    with pytest.raises(ValueError): load_operator_evidence(current=cfg)


def test_bk_copy_outside_inputs_rejected_before_probe(tmp_path, monkeypatch):
    outside = tmp_path / 'outside_source.json'
    cfg, _, _, _, _ = _bk_manifest_with_copies(tmp_path, copy_value=str(outside), documentary_path=False)
    native = Path.is_file
    def is_file(path):
        if path == outside: raise AssertionError('Outside source was probed')
        return native(path)
    monkeypatch.setattr(Path, 'is_file', is_file)
    with pytest.raises(ValueError): load_operator_evidence(current=cfg)


@pytest.mark.parametrize('drift', ['sha256', 'bytes'])
def test_bk_copy_hash_and_size_still_required(tmp_path, drift):
    cfg, _, _, _, _ = _bk_manifest_with_copies(tmp_path, documentary_path=False, drift=drift)
    with pytest.raises(ValueError): load_operator_evidence(current=cfg)
