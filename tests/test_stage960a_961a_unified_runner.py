"""PB030..033 integration through actual Flent/RegressionGatekeeper, entirely offline."""
from __future__ import annotations

import copy
import hashlib
import json
import socket
import subprocess

import pytest

from controller import pb_030_031_phy_response_surface_harness as pb030
from controller import pb_032_033_ratemask_sgi_solver as pb032
from tests.test_stage959a_unified_physical_runner import make_fixture_acquirer
from tools.autoresearch import run_stage959a_unified_physical_retest_runner as runner


@pytest.fixture(params=[
    (pb030, 'freeze_pb_030_031_physical_retest_plan', 'run_pb_030_031_physical_retest'),
    (pb032, 'freeze_pb_032_033_physical_retest_plan', 'run_pb_032_033_physical_retest'),
], ids=['PB030_031', 'PB032_033'])
def controller(request):
    module, freeze_name, run_name = request.param
    return module, getattr(module, freeze_name), getattr(module, run_name)


@pytest.fixture(autouse=True)
def no_transport(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError('offline controller fixtures may not launch transport')
    monkeypatch.setattr(socket, 'create_connection', denied)
    monkeypatch.setattr(socket.socket, 'connect', denied)
    monkeypatch.setattr(subprocess, 'Popen', denied)


def make_plan(controller, **changes):
    options = dict(campaign_id='controller-fixture',
                   baseline_config={'channel_width_mhz': 20, 'queue_limit': 1024},
                   candidate_config={'channel_width_mhz': 20, 'queue_limit': 512},
                   station_hosts=['station-fixture'], created_at_s=1)
    options.update(changes)
    return controller[1](**options)


def test_inspection_is_default_and_does_not_acquire(controller, tmp_path):
    plan = make_plan(controller)
    source = make_fixture_acquirer(plan)
    result = controller[2](plan, acquire_window=source, evidence_root=tmp_path)
    assert result['status'] == 'PLANNED'
    assert source.calls == []
    assert result['deployment_authorized'] is False
    assert not list(tmp_path.iterdir())


def test_actual_pipeline_has_all_phases_and_hashed_raw_evidence(controller, tmp_path):
    plan = make_plan(controller)
    source = make_fixture_acquirer(plan)
    result = controller[2](plan, acquire_window=source, evidence_root=tmp_path, execute=True)
    assert result['status'] == 'SYNTHETIC_DIAGNOSTIC_COMPLETE', result
    assert result['completed_phases'] == list(runner.PHASES)
    assert len(result['raw_windows']) == len(source.calls) == 54
    assert result['promotion_eligible'] is result['deployment_authorized'] is False
    assert result['physical_acceptance'] == 'UNKNOWN'
    for pin in result['evidence_manifest']:
        assert hashlib.sha256((tmp_path / pin['path']).read_bytes()).hexdigest() == pin['sha256']
    roles = {json.loads((tmp_path / pin['path']).read_bytes())['experiment_role']
             for pin in result['raw_windows']}
    assert roles == {controller[0].PHYSICAL_EXPERIMENT_ROLE}
    for phase in ('AB_DISCOVERY', 'AB_HOLDOUT'):
        assert result['phase_results'][phase]['raw_gate']['verdict'] == 'SYNTHETIC_PASS'


@pytest.mark.parametrize('fault', ['empty_ping', 'iperf_error', 'copied_holdout', 'hash_drift'])
def test_acquisition_faults_fail_closed_in_actual_pipeline(controller, tmp_path, fault):
    plan = make_plan(controller)
    source = make_fixture_acquirer(plan, fault=fault, evidence_root=tmp_path)
    result = controller[2](plan, acquire_window=source, evidence_root=tmp_path, execute=True)
    assert result['status'] == 'FAILED_CLOSED', result
    assert result['promotion_eligible'] is result['deployment_authorized'] is False
    assert 'AB_HOLDOUT' not in result['completed_phases']
    if fault != 'copied_holdout':
        assert all(spec['phase'] == 'AA_CONTROL' for spec in source.calls)
    else:
        assert 'AB_DISCOVERY' in result['completed_phases']
        assert any(spec['phase'] == 'AB_HOLDOUT' for spec in source.calls)


def test_cross_controller_role_and_plan_tampering_reject_before_callback(controller, tmp_path):
    plan = make_plan(controller)
    source = make_fixture_acquirer(plan)
    bad = copy.deepcopy(plan)
    bad['experiment_role'] = 'OTHER_CONTROLLER'
    with pytest.raises(ValueError, match='experiment-role'):
        controller[2](bad, acquire_window=source, evidence_root=tmp_path, execute=True)
    bad = copy.deepcopy(plan)
    bad['candidate_config']['queue_limit'] = 128
    with pytest.raises(ValueError, match='frozen_plan_hash_mismatch'):
        controller[2](bad, acquire_window=source, evidence_root=tmp_path, execute=True)
    assert source.calls == []


def test_holdout_boolean_and_metric_summary_cannot_replace_acquisition(controller, tmp_path):
    plan = make_plan(controller)
    with pytest.raises(TypeError):
        controller[2](plan, acquire_window=lambda spec: None, evidence_root=tmp_path,
                      holdout_replicated=True)
    result = controller[2](plan, acquire_window=lambda spec: {'goodput_mbps': 100},
                           evidence_root=tmp_path, execute=True)
    assert result['status'] == 'FAILED_CLOSED'
    assert 'raw_window_bytes' in result['failure_reason']


def test_physical_requires_frozen_acquirer_and_family(controller):
    with pytest.raises(ValueError, match='acquirer_source'):
        make_plan(controller, execution_kind='PHYSICAL')
    plan = make_plan(controller, execution_kind='PHYSICAL',
                     acquirer_source_path='tests/test_stage960a_961a_unified_runner.py')
    assert plan['acquirer_source'] == runner.source_pin('tests/test_stage960a_961a_unified_runner.py')
    assert plan['family_fingerprints'] == [runner.config_fingerprint(plan['candidate_config'])]
    with pytest.raises(ValueError, match='family'):
        make_plan(controller, family_fingerprints=['0' * 64])
