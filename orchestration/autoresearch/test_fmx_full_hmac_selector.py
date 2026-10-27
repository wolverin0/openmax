"""The full hMAC/VoIP cohort cannot borrow ordinary bidirectional statistics."""
import importlib
from copy import deepcopy
import pytest


@pytest.fixture(scope='module')
def report():
    s=importlib.import_module('orchestration.autoresearch.fmx_multi_regime_dyadic_selector')
    d=importlib.import_module('orchestration.autoresearch.fmx_full_hmac_dataset')
    return s.audit_full_hmac_packages(manifest_path=d.MANIFEST,expected_manifest_sha256=d.MANIFEST_SHA256)


def test_full_selector_returns_explicit_abstention_without_invented_authority():
    s=importlib.import_module('orchestration.autoresearch.fmx_multi_regime_dyadic_selector')
    d=importlib.import_module('orchestration.autoresearch.fmx_full_hmac_dataset')
    result=s.audit_full_hmac_packages(manifest_path=d.MANIFEST,expected_manifest_sha256=d.MANIFEST_SHA256)
    assert len(result['packages'])==12 and all(p['status']=='BLOCKED'for p in result['packages'])
    assert result['recommended_policy']is None and result['physical_acceptance']is False
    assert result['historical_selector_behavior_changed']is False


def test_full_audit_preserves_distinct_packages_timing_and_source_health(report):
    assert report['records']==384 and report['crossed_windows']==3740 and report['sequential_windows']==16
    p={r['round_id']:r for r in report['packages']}
    assert p['R135']['declared_ack_timeout_us']==30 and p['R141']['declared_ack_timeout_us']==36
    assert p['R135']['declaration_matches_saved_probe_ack']is False
    assert p['R141']['declaration_matches_saved_probe_ack']is True
    assert p['R138']['control_saved_health']['packet_loss_pct']==.625
    assert p['R142']['control_saved_health']['packet_loss_pct']==1.25
    assert p['R144']['control_saved_health']['packet_loss_pct']==.625
    assert all(r['control_saved_health']['station_drops']==0 and r['control_saved_health']['restoration_verified']is True for r in p.values())
    assert p['R135']['policy_key']!=p['R141']['policy_key']
    assert p['R136']['policy_key']!=p['R142']['policy_key']
    assert all('NO_ACCEPTED_SAME_REGIME_STATISTICAL_RECEIPT'in r['reasons']for r in p.values())


@pytest.mark.parametrize('distance,coverage',[(1000,2),(3000,6),(6000,13),(9000,20),(12000,26),(14000,31)])
def test_every_exact_context_abstains_and_retains_both_recorded_packages(report,monkeypatch,distance,coverage):
    s=importlib.import_module('orchestration.autoresearch.fmx_multi_regime_dyadic_selector')
    monkeypatch.setattr(s,'audit_full_hmac_packages',lambda **kwargs:deepcopy(report))
    result=s.select_full_hmac_policy(distance_meters=distance,coverage_class=coverage)
    assert result['status']=='ABSTAIN'and result['recommended_policy']is None
    assert len(result['recorded_packages'])==2 and all(p['status']=='BLOCKED'for p in result['recorded_packages'])
    assert result['physical_acceptance']is False and result['automatic_execution_allowed']is False


@pytest.mark.parametrize('distance,coverage',[(100,0),(1500,3),(1000,6),(1000.0,2),(True,2),(1000,True),(14000,33)])
def test_selector_rejects_unobserved_or_malformed_context_before_access(monkeypatch,distance,coverage):
    s=importlib.import_module('orchestration.autoresearch.fmx_multi_regime_dyadic_selector')
    monkeypatch.setattr(s,'audit_full_hmac_packages',lambda **kwargs:pytest.fail('Bad context must fail before source access'))
    with pytest.raises(ValueError):s.select_full_hmac_policy(distance_meters=distance,coverage_class=coverage)


def test_no_ordinary_regime_evidence_or_keep_label_can_supply_eligibility(monkeypatch):
    s=importlib.import_module('orchestration.autoresearch.fmx_multi_regime_dyadic_selector')
    d=importlib.import_module('orchestration.autoresearch.fmx_full_hmac_dataset')
    monkeypatch.setattr(s,'load_operator_evidence',lambda **kwargs:pytest.fail('No other regime statistics may be borrowed'))
    monkeypatch.setattr(s,'select_operator_policy',lambda *args,**kwargs:pytest.fail('No ordinary regime promotion'))
    result=s.audit_full_hmac_packages(manifest_path=d.MANIFEST,expected_manifest_sha256=d.MANIFEST_SHA256)
    assert result['recommended_policy']is None and len(result['packages'])==12
    assert all(p['status']=='BLOCKED'for p in result['packages'])


def test_bad_manifest_pin_and_unbound_silicon_fail_closed_without_partial_packages():
    s=importlib.import_module('orchestration.autoresearch.fmx_multi_regime_dyadic_selector')
    d=importlib.import_module('orchestration.autoresearch.fmx_full_hmac_dataset')
    result=s.audit_full_hmac_packages(manifest_path=d.MANIFEST,expected_manifest_sha256='0'*64)
    assert result['status']=='BLOCKED'and result['packages']==[]
    result=s.audit_full_hmac_packages(manifest_path=d.MANIFEST,expected_manifest_sha256=d.MANIFEST_SHA256,
        silicon_path=d.MANIFEST,expected_silicon_sha256=d.MANIFEST_SHA256)
    assert result['status']=='BLOCKED'and result['packages']==[]
