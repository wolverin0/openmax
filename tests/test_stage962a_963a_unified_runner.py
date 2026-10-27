"""Real Flent/Gatekeeper integration using synthetic byte captures, never devices."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import socket
import subprocess

import pytest

from controller import pb_050_051_scheduler_timing_harness as scheduler
from controller import pb_053_054_hmac_epoch_controller as hmac

CONTROLLERS = [scheduler,hmac]


@pytest.fixture(autouse=True)
def forbid_external_acquisition(monkeypatch):
    def denied(*args,**kwargs):
        raise AssertionError('controller integration tests must acquire only local fixture bytes')
    monkeypatch.setattr(socket,'create_connection',denied)
    monkeypatch.setattr(socket.socket,'connect',denied)
    monkeypatch.setattr(subprocess,'Popen',denied)


def frozen(controller, suffix='case'):
    return controller.freeze_physical_retest_plan(campaign_id='controller-'+suffix,
        baseline_config={'channel_width_mhz':20,'radio_identity':'fixture-radio','mode':'baseline'},
        candidate_config={'channel_width_mhz':20,'radio_identity':'fixture-radio','mode':'candidate'},
        station_hosts=['fixture-cpe-a','fixture-cpe-b'],server_host='fixture-server',
        duration_seconds=10.0,pairs_per_phase=8,execution_kind='SYNTHETIC',created_at_s=1.0)


def source(plan,**kwargs):
    from tests.test_stage959a_unified_physical_runner import make_fixture_acquirer
    return make_fixture_acquirer(plan,**kwargs)


@pytest.mark.parametrize('controller',CONTROLLERS)
def test_default_inspection_never_acquires(controller,tmp_path):
    plan=frozen(controller,'inspect')
    calls=[]
    def acquire(spec):
        calls.append(spec)
        raise AssertionError('default inspection acquired a window')
    result=controller.run_physical_retest(plan,acquire_window=acquire,evidence_root=tmp_path)
    assert not calls
    assert not result['deployment_authorized']
    assert result['physical_acceptance']=='UNKNOWN'


@pytest.mark.parametrize('controller',CONTROLLERS)
def test_real_pipeline_persists_hashed_windows_without_synthetic_promotion(controller,tmp_path):
    plan=frozen(controller,'complete')
    acquire=source(plan)
    result=controller.run_physical_retest(plan,acquire_window=acquire,evidence_root=tmp_path,execute=True)
    assert result['status']=='SYNTHETIC_DIAGNOSTIC_COMPLETE',result
    assert result['completed_phases']==['AA_CONTROL','AB_DISCOVERY','AB_HOLDOUT']
    assert set(result['phase_results'])=={'AA_CONTROL','AB_DISCOVERY','AB_HOLDOUT'}
    assert not result['promotion_eligible'] and not result['deployment_authorized']
    assert result['physical_acceptance']=='UNKNOWN'
    assert result['raw_windows']
    for record in result['raw_windows']:
        raw=(tmp_path/record['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==record['sha256']


@pytest.mark.parametrize('controller',CONTROLLERS)
@pytest.mark.parametrize('fault',['empty_ping','iperf_error','hash_drift','config_drift'])
def test_actual_parser_faults_fail_before_discovery_or_holdout(controller,tmp_path,fault):
    plan=frozen(controller,fault)
    acquire=source(plan,fault=fault,evidence_root=tmp_path)
    result=controller.run_physical_retest(plan,acquire_window=acquire,evidence_root=tmp_path,execute=True)
    assert result['status']=='FAILED_CLOSED',result
    assert result['failure_reason']
    assert 'AB_DISCOVERY' not in result['completed_phases']
    assert 'AB_HOLDOUT' not in result['completed_phases']
    assert acquire.calls and all(row['phase']=='AA_CONTROL' for row in acquire.calls)
    assert not result['promotion_eligible'] and not result['deployment_authorized']


@pytest.mark.parametrize('controller',CONTROLLERS)
@pytest.mark.parametrize('fault',['copied_holdout','overlap'])
def test_copied_holdout_cannot_be_presented_as_replication(controller,tmp_path,fault):
    plan=frozen(controller,'copied-holdout')
    result=controller.run_physical_retest(plan,acquire_window=source(plan,fault=fault),
        evidence_root=tmp_path,execute=True)
    assert result['status']=='FAILED_CLOSED',result
    assert result['completed_phases']==['AA_CONTROL','AB_DISCOVERY']
    assert 'AB_HOLDOUT' not in result['completed_phases']
    assert not result['promotion_eligible']


@pytest.mark.parametrize('controller',CONTROLLERS)
def test_missing_real_readback_rejects_before_discovery(controller,tmp_path):
    plan=frozen(controller,'missing-readback')
    acquire=source(plan)
    def missing_readback(spec):
        raw=json.loads(acquire(spec))
        raw.pop('config_readback')
        return json.dumps(raw).encode()
    result=controller.run_physical_retest(plan,acquire_window=missing_readback,
        evidence_root=tmp_path,execute=True)
    assert result['status']=='FAILED_CLOSED',result
    assert result['completed_phases']==[]
    assert len(acquire.calls)==1
    assert not result['promotion_eligible'] and not result['deployment_authorized']


@pytest.mark.parametrize('controller',CONTROLLERS)
@pytest.mark.parametrize('field,value', [('channel_width_mhz',40),('radio_identity','different-radio')])
def test_mutated_frozen_configuration_is_rejected_before_acquisition(controller,tmp_path,field,value):
    plan=frozen(controller,'configuration-drift')
    broken=copy.deepcopy(plan)
    broken['candidate_config'][field]=value
    calls=[]
    with pytest.raises(ValueError):
        controller.run_physical_retest(broken,acquire_window=lambda spec:calls.append(spec),
            evidence_root=tmp_path,execute=True)
    assert not calls


@pytest.mark.parametrize('controller',CONTROLLERS)
def test_wrong_controller_role_is_rejected_before_acquisition(controller,tmp_path):
    calls=[]
    with pytest.raises(ValueError,match='experiment role'):
        controller.run_physical_retest({'experiment_role':'WRONG_CONTROLLER'},
            acquire_window=lambda spec:calls.append(spec),evidence_root=tmp_path,execute=True)
    assert not calls


@pytest.mark.parametrize('controller',CONTROLLERS)
def test_callers_cannot_override_the_frozen_controller_role(controller):
    with pytest.raises(ValueError,match='experiment role'):
        controller.freeze_physical_retest_plan(experiment_role='WRONG_CONTROLLER')
