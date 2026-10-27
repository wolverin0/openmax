"""Synthetic raw acquisition/fault fixtures; no transport or radio execution."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import socket
import subprocess

import pytest

from tools.autoresearch import run_stage959a_unified_physical_retest_runner as runner


def fixture_plan(**changes):
    options = dict(campaign_id='fixture-campaign', baseline_config={'channel_width_mhz': 40, 'queue_limit': 1024},
                   candidate_config={'channel_width_mhz': 40, 'queue_limit': 512},
                   station_hosts=['station-fixture'], duration_seconds=10,
                   pairs_per_phase=8, created_at_s=1, execution_kind='SYNTHETIC')
    options.update(changes)
    return runner.freeze_plan(**options)


class FixtureAcquirer:
    """Produces synthetic exact native-output shapes, never physical evidence."""
    def __init__(self, plan, fault=None, evidence_root=None):
        self.plan = plan
        self.fault = fault
        self.evidence_root = Path(evidence_root) if evidence_root else None
        self.calls = []
        self.discovery_stations = None

    def __call__(self, spec):
        self.calls.append(copy.deepcopy(spec))
        phase_index = runner.PHASES.index(spec['phase'])
        start = 100 + phase_index*1000000 + spec['ordinal']*(spec['duration_seconds']+1)
        latency = 8 if spec['phase'] != 'AA_CONTROL' and spec['arm'] == 'B' else 10
        raw = {key: copy.deepcopy(spec[key]) for key in (
            'campaign_id','phase','arm','block_index','is_sentinel','window_id','dataset_id',
            'epoch_id','experiment_role','plan_nonce','plan_sha256','execution_kind')}
        raw.update(session_id='session:' + hashlib.sha256(spec['window_id'].encode()).hexdigest()[:40],
                   window_start_s=start, window_end_s=start+spec['duration_seconds'],
                   config_readback=copy.deepcopy(spec['config']), firmware_resets=0, capture_drops=0,
                   stations={})
        for host in spec['station_hosts']:
            native_session = hashlib.sha256((spec['window_id']+host+spec['plan_nonce']).encode()).hexdigest()
            iperf = dict(start={'cookie':native_session,'connected':[{'remote_host':spec['server_host']}]},
                         end={'sum_received':{'bits_per_second':10000000,'bytes':12500000,
                                              'seconds':spec['duration_seconds']},
                              'sum_sent':{'bits_per_second':11000000,'retransmits':0}})
            # Fixed duration10s uses the same exact receiver byte/time relation; other durations scale bytes.
            iperf['end']['sum_received']['bytes'] = int(10000000*spec['duration_seconds']/8)
            ping = '\n'.join(f'64 bytes from peer: icmp_seq={i} ttl=64 time={latency} ms' for i in range(1,21))
            ping += '\n20 packets transmitted, 20 packets received, 0% packet loss\n'
            raw['stations'][host] = dict(iperf3_json=json.dumps(iperf), ping_stdout=ping)
        if spec['phase']=='AB_DISCOVERY' and self.discovery_stations is None:
            self.discovery_stations=copy.deepcopy(raw['stations'])
        fault_phase = spec['phase']=='AA_CONTROL' and spec['ordinal']==1
        if self.fault=='empty_ping' and fault_phase:
            raw['stations'][spec['station_hosts'][0]]['ping_stdout']=''
        elif self.fault=='iperf_error' and fault_phase:
            raw['stations'][spec['station_hosts'][0]]['iperf3_json']=json.dumps({'error':'fixture acquisition failed'})
        elif self.fault=='loss' and fault_phase:
            text=raw['stations'][spec['station_hosts'][0]]['ping_stdout']
            raw['stations'][spec['station_hosts'][0]]['ping_stdout']=text.replace('20 packets received','19 packets received')
        elif self.fault=='reset' and fault_phase:
            raw['firmware_resets']=1
        elif self.fault=='sentinel_loss' and spec['ordinal']==0:
            text=raw['stations'][spec['station_hosts'][0]]['ping_stdout']
            raw['stations'][spec['station_hosts'][0]]['ping_stdout']=text.replace('20 packets received','19 packets received')
        elif self.fault=='copied_holdout' and spec['phase']=='AB_HOLDOUT':
            raw['stations']=copy.deepcopy(self.discovery_stations)
        elif self.fault=='overlap' and spec['phase']=='AB_HOLDOUT':
            raw['window_start_s']=101
            raw['window_end_s']=111
        elif self.fault=='config_drift' and fault_phase:
            raw['config_readback']['queue_limit']=999
        elif self.fault=='hash_drift' and spec['ordinal']==2:
            if self.evidence_root is None:
                raise ValueError('fixture hash_drift requires evidence_root')
            first=self.evidence_root/'campaigns'/spec['campaign_id']/'AA_CONTROL/0.raw.json'
            first.write_bytes(first.read_bytes()+b' ')
        elif self.fault=='plan_drift' and fault_phase:
            self.plan['experiment_role']='MUTATED_AFTER_FREEZE'
        elif self.fault=='plan_reseal' and fault_phase:
            self.plan['experiment_role']='MUTATED_AFTER_FREEZE'
            body={key:value for key,value in self.plan.items() if key!='plan_sha256'}
            self.plan['plan_sha256']=runner.digest(runner.canonical(body))
        elif self.fault=='missing_station' and fault_phase:
            raw['stations'].clear()
        elif self.fault=='missing_sentinel' and spec['ordinal']==0:
            raw.pop('is_sentinel')
        elif self.fault=='copied_session' and spec['ordinal']==1:
            first=next(iter(runner.window_specs(self.plan,'AA_CONTROL')))
            raw['session_id']='session:'+hashlib.sha256(first['window_id'].encode()).hexdigest()[:40]
        return runner.canonical(raw)


def make_fixture_acquirer(plan, *, fault=None, evidence_root=None):
    return FixtureAcquirer(plan, fault=fault, evidence_root=evidence_root)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError('network or process acquisition is forbidden in959fixtures')
    monkeypatch.setattr(socket,'create_connection',denied)
    monkeypatch.setattr(socket.socket,'connect',denied)
    monkeypatch.setattr(subprocess,'Popen',denied)


def test_default_inspection_never_invokes_acquirer(tmp_path):
    plan=fixture_plan()
    def denied(spec):
        pytest.fail('inspection invoked a physical source')
    result=runner.run_campaign(plan,acquire_window=denied,evidence_root=tmp_path)
    assert result['status']=='PLANNED' and result['callbacks_invoked']==0
    assert not list(tmp_path.iterdir())


def test_real_flent_and_gate_synthetic_pipeline_is_nonpromotable(tmp_path):
    plan=fixture_plan()
    source=make_fixture_acquirer(plan)
    result=runner.run_campaign(plan,acquire_window=source,evidence_root=tmp_path,execute=True)
    assert result['status']=='SYNTHETIC_DIAGNOSTIC_COMPLETE',result
    assert result['completed_phases']==list(runner.PHASES)
    assert result['phase_results']['AB_DISCOVERY']['raw_gate']['verdict']=='SYNTHETIC_PASS'
    assert result['phase_results']['AB_HOLDOUT']['raw_gate']['verdict']=='SYNTHETIC_PASS'
    assert result['promotion_eligible'] is result['deployment_authorized'] is False
    assert result['physical_acceptance']=='UNKNOWN'
    assert len(result['raw_windows'])==3*(2*8+2)==len(source.calls)
    for pin in result['evidence_manifest']:
        blob=(tmp_path/pin['path']).read_bytes()
        assert hashlib.sha256(blob).hexdigest()==pin['sha256']
    roles={json.loads((tmp_path/pin['path']).read_bytes())['experiment_role'] for pin in result['raw_windows']}
    assert roles=={plan['experiment_role']}


@pytest.mark.parametrize('fault', ['empty_ping','iperf_error','loss','reset','sentinel_loss',
    'copied_holdout','overlap','config_drift','hash_drift','plan_drift','plan_reseal','missing_station',
    'missing_sentinel','copied_session'])
def test_faults_never_promote_and_stop_campaign(tmp_path,fault):
    plan=fixture_plan()
    source=make_fixture_acquirer(plan,fault=fault,evidence_root=tmp_path)
    result=runner.run_campaign(plan,acquire_window=source,evidence_root=tmp_path,execute=True)
    assert result['status']=='FAILED_CLOSED',result
    assert not result['promotion_eligible'] and not result['deployment_authorized']
    if fault not in ('copied_holdout','overlap'):
        assert all(row['phase']=='AA_CONTROL' for row in source.calls)


def test_plan_tampering_and_source_drift_reject_before_callback(tmp_path,monkeypatch):
    plan=fixture_plan()
    plan['pairs_per_phase']=9
    with pytest.raises(ValueError,match='frozen_plan_hash_mismatch'):
        runner.run_campaign(plan,acquire_window=lambda spec:None,evidence_root=tmp_path,execute=True)
    plan=fixture_plan()
    real=runner.source_pin
    monkeypatch.setattr(runner,'source_pin',lambda label:dict(real(label),sha256='0'*64))
    with pytest.raises(ValueError,match='source_drift'):
        runner.run_campaign(plan,acquire_window=lambda spec:None,evidence_root=tmp_path,execute=True)


def test_existing_campaign_cannot_overwrite_raw_evidence(tmp_path):
    plan=fixture_plan()
    result=runner.run_campaign(plan,acquire_window=make_fixture_acquirer(plan),evidence_root=tmp_path,execute=True)
    assert result['status']=='SYNTHETIC_DIAGNOSTIC_COMPLETE'
    with pytest.raises(FileExistsError):
        runner.run_campaign(plan,acquire_window=make_fixture_acquirer(plan),evidence_root=tmp_path,execute=True)


def test_empty_metrics_cannot_replace_raw_callback_output(tmp_path):
    plan=fixture_plan()
    result=runner.run_campaign(plan,acquire_window=lambda spec:{'goodput_mbps':100},evidence_root=tmp_path,execute=True)
    assert result['status']=='FAILED_CLOSED'
    assert 'raw_window_bytes' in result['failure_reason']


def test_physical_requires_frozen_source_and_cannot_relabel_fast_fixture(tmp_path):
    with pytest.raises(ValueError,match='acquirer_source'):
        fixture_plan(execution_kind='PHYSICAL')
    plan=fixture_plan(execution_kind='PHYSICAL',acquirer_source_path='tests/test_stage959a_unified_physical_runner.py')
    source=make_fixture_acquirer(plan)
    result=runner.run_campaign(plan,acquire_window=source,evidence_root=tmp_path,execute=True)
    assert result['status']=='FAILED_CLOSED'
    assert 'fresh_physical_duration' in result['failure_reason']
    assert not result['promotion_eligible']


@pytest.mark.parametrize('change', [dict(pairs_per_phase=0), dict(physical_clock_skew_s=100000),
    dict(physical_min_elapsed_fraction=0),dict(acquirer_source=None,execution_kind='PHYSICAL'),
    dict(station_hosts=[]),dict(family_fingerprints=['0'*64]),dict(duration_seconds=.00001)])
def test_resealed_unsafe_plan_is_not_an_authority(change,tmp_path):
    plan=fixture_plan()
    plan.update(change)
    body={key:value for key,value in plan.items() if key!='plan_sha256'}
    plan['plan_sha256']=runner.digest(runner.canonical(body))
    with pytest.raises(ValueError):
        runner.run_campaign(plan,acquire_window=lambda spec:pytest.fail('unsafe plan called source'),
                            evidence_root=tmp_path,execute=True)


def test_physical_schema_fixture_connects_actual_adapter_holdout_gate(tmp_path,monkeypatch):
    # This controlled-clock fixture verifies SOFTWARE SCHEMA ONLY, never real elapsed RF acquisition.
    from types import SimpleNamespace
    class ControlledClock:
        value=100.0
        def read(self):return self.value
    clock=ControlledClock()
    monkeypatch.setattr(runner,'time',SimpleNamespace(time=clock.read,monotonic=clock.read))
    plan=fixture_plan(execution_kind='PHYSICAL',acquirer_source_path='tests/test_stage959a_unified_physical_runner.py')
    class SchemaAcquirer(FixtureAcquirer):
        def __call__(self,spec):
            raw=runner.strict_json(super().__call__(spec))
            raw['window_start_s']=clock.value
            clock.value+=spec['duration_seconds']
            raw['window_end_s']=clock.value
            return runner.canonical(raw)
    result=runner.run_campaign(plan,acquire_window=SchemaAcquirer(plan),evidence_root=tmp_path,execute=True)
    assert result['status']=='PHYSICAL_STATISTICAL_REPLICATION_COMPLETE',result
    assert result['phase_results']['AB_DISCOVERY']['raw_gate']['verdict']=='KEEP_FOR_REPLICATION'
    assert result['phase_results']['AB_HOLDOUT']['raw_gate']['verdict']=='PROMOTE'
    assert result['physical_acceptance']=='UNKNOWN'
    assert result['deployment_authorized'] is False


def test_raised_callback_is_counted_as_an_attempt(tmp_path):
    plan=fixture_plan()
    def failed(spec):raise RuntimeError('fixture transport timeout')
    result=runner.run_campaign(plan,acquire_window=failed,evidence_root=tmp_path,execute=True)
    assert result['status']=='FAILED_CLOSED' and result['callbacks_invoked']==1


def test_public_source_tree_cannot_be_used_for_raw_capture_root():
    plan=fixture_plan()
    with pytest.raises(ValueError,match='private_evidence_directory'):
        runner.run_campaign(plan,acquire_window=lambda spec:None,
                            evidence_root=runner.ROOT/'artifacts/autoresearch',execute=True)


@pytest.mark.parametrize('change', [dict(pairs_per_phase=3),dict(duration_seconds=float('nan')),
    dict(station_hosts=['one','one']),dict(execution_kind='CONFIRMED_LIVE_HARDWARE'),
    dict(baseline_config={'channel_width_mhz':40,'psk':'placeholder'})])
def test_bad_frozen_contracts_rejected(change):
    with pytest.raises(ValueError):
        fixture_plan(**change)
