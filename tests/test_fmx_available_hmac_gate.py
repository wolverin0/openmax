"""Saved hMAC/voice packages cannot inherit ordinary bidirectional acceptance."""
import hashlib
import json
from pathlib import Path

import pytest

from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import (
    audit_available_hmac_packages,select_available_hmac_policy,_hmac_observed_goodput,
    OPERATOR_REGIMES)
from orchestration.autoresearch.fmx_structural_promotion_gate import audit_available_hmac_promotion


BASE=Path(__file__).resolve().parents[1]/'artifacts/autoresearch/waves_cg_to_cj_20261024'
MANIFEST=BASE/'inputs_manifest_v2.json'
PB=BASE/'inputs/artifacts/qca988x/pb_021_031_050_live_lap120_silicon_qualification_20261024.json'


@pytest.fixture(scope='module')
def options():
    return dict(manifest_path=MANIFEST,expected_manifest_sha256=hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
                silicon_path=PB,expected_silicon_sha256=hashlib.sha256(PB.read_bytes()).hexdigest())


@pytest.fixture(scope='module')
def report(options):
    return audit_available_hmac_packages(**options)


def test_real_packages_are_separate_and_fail_closed(report):
    assert report['status']=='ABSTAIN_NO_QUALIFIED_HMAC_PACKAGE'
    assert [row['round_id'] for row in report['packages']]==[f'R{i}' for i in range(135,140)]
    assert report['records']==370 and report['crossed_windows']==3516 and report['sequential_windows']==16
    assert report['missing_at_cutoff']==list(range(140,147))
    assert report['recommended_policy'] is None
    assert report['physical_acceptance'] is report['automatic_execution_allowed'] is False
    assert report['independently_accepted_same_regime_statistics'] is False
    assert 'bidir_8flow_voip_hmac' not in OPERATOR_REGIMES
    for row in report['packages']:
        assert row['status']=='BLOCKED'
        assert 'NO_ACCEPTED_SAME_REGIME_STATISTICAL_RECEIPT' in row['reasons']
        assert 'EFFECTIVE_HMAC_QUEUE_GATING_UNQUALIFIED' in row['reasons']
        assert row['generic_rtt_is_not_automatically_voip_service_latency'] is True
        assert row['utility']['statistical_noninferiority_qualified'] is False


def test_saved_ack_conflict_does_not_replace_recorded_values(report):
    rows=report['packages']
    assert [(row['declared_ack_timeout_us'],row['saved_probe_reported_ack_timeout_us']) for row in rows]==[
        (30,36),(48,48),(69,69),(90,90),(108,108)]
    assert [row['declaration_matches_saved_probe_ack'] for row in rows]==[False,True,True,True,True]
    assert all(row['effective_timing_verified'] is False for row in rows)


@pytest.mark.parametrize('target,expected',[(97.999,False),(98,False),(98.001,True),(100,True),(101,True)])
def test_literal_goodput_boundary_is_descriptive_and_strict(target,expected):
    result=_hmac_observed_goodput(100,target)
    assert result['observed_total_goodput_drop_strictly_below_2pct'] is expected
    assert result['statistical_noninferiority_qualified'] is False


@pytest.mark.parametrize('value',[True,None,0,-1,float('nan'),float('inf'),'100',10**400])
def test_goodput_cannot_be_coerced(value):
    with pytest.raises(ValueError):
        _hmac_observed_goodput(value,100)


@pytest.mark.parametrize('distance,coverage',[(True,2),(1000,True),(1000,6),(3000,2),(14000,33),(0,0)])
def test_context_conflict_is_rejected_before_loading_sources(distance,coverage):
    with pytest.raises(ValueError):
        select_available_hmac_policy(distance_meters=distance,coverage_class=coverage)


def test_exact_context_returns_abstention_even_when_a_package_is_present(options):
    result=select_available_hmac_policy(distance_meters=1000,coverage_class=2,**options)
    assert result['status']=='ABSTAIN' and result['recommended_policy'] is None
    assert len(result['recorded_packages'])==1
    assert result['recorded_packages'][0]['round_id']=='R135'
    assert result['physical_acceptance'] is result['automatic_execution_allowed'] is False


def test_untested_requested_context_does_not_borrow_a_nearby_package(options):
    result=select_available_hmac_policy(distance_meters=14000,coverage_class=31,**options)
    assert result['recorded_packages']==[] and result['status']=='ABSTAIN'


@pytest.mark.parametrize('rid',['R134','R147','R0135',135,True,None])
def test_structural_gate_rejects_out_of_scope_identity_before_source_read(rid):
    with pytest.raises(ValueError):
        audit_available_hmac_promotion(round_id=rid)


def test_structural_gate_keeps_missing_receipt_and_present_receipt_blocked(options):
    present=audit_available_hmac_promotion(round_id='R135',**options)
    absent=audit_available_hmac_promotion(round_id='R140',**options)
    assert present['status']==absent['status']=='BLOCKED'
    assert present['package']['round_id']=='R135' and absent['package'] is None
    assert absent['reasons']==['REQUESTED_HMAC_RECEIPT_NOT_AVAILABLE_AT_CUTOFF']
    assert present['historical_gate_contracts_changed'] is False


@pytest.mark.parametrize('key',['expected_manifest_sha256','expected_silicon_sha256'])
def test_wrong_source_pin_yields_a_blocked_diagnostic(options,key):
    changed={**options,key:'0'*64}
    result=audit_available_hmac_packages(**changed)
    assert result['status']=='BLOCKED' and result['packages']==[]
    assert result['reasons']==['MALFORMED_OR_UNBOUND_HMAC_EVIDENCE']
    assert result['physical_acceptance'] is result['automatic_execution_allowed'] is False
