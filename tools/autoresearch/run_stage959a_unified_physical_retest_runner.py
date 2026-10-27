#!/usr/bin/env python3
"""Frozen raw-acquisition runner: Flent -> A/A -> discovery -> disjoint holdout.

No transport is imported or invoked by inspection. Instrument honesty is not
authenticated by hashes; even a statistical PROMOTE never authorizes deployment.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import re
import runpy
import secrets
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from workloads.flent_orchestrator import FlentWorkloadConfig, FlentWorkloadOrchestrator
from analysis.regression_gate import gatekeeper as gate
from tools.autoresearch import stage897_900_gate_adapter as adapter

PHASES = ('AA_CONTROL', 'AB_DISCOVERY', 'AB_HOLDOUT')
STEM = 'stage959a_unified_physical_retest_runner'
MAX_RAW_BYTES = 8 * 1024 * 1024
SOURCE_LABELS = (
    'tools/autoresearch/run_stage959a_unified_physical_retest_runner.py',
    'workloads/flent_orchestrator.py', 'analysis/regression_gate/gatekeeper.py',
    'analysis/metrics/schema.py', 'tools/autoresearch/stage897_900_gate_adapter.py')


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def strict_json(blob):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate_json_key')
            result[key] = value
        return result
    def reject(value):
        raise ValueError('nonfinite_json')
    result = json.loads(blob, object_pairs_hook=pairs, parse_constant=reject)
    if not isinstance(result, dict):
        raise ValueError('object_required')
    return result


def identifier(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,120}', value):
        raise ValueError('invalid_' + label)
    return value


def number(value, label, *, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError('invalid_' + label)
    return value


def checked_root(value):
    path = Path(value).absolute()
    if str(path).startswith('\\\\') or getattr(path, 'is_reserved', lambda: False)():
        raise ValueError('network_evidence_root_forbidden')
    if os.name == 'nt':
        import ctypes
        if ctypes.windll.kernel32.GetDriveTypeW(str(path.anchor)) == 4:
            raise ValueError('mapped_network_evidence_root_forbidden')
    for parent in (path, *path.parents):
        if parent.is_symlink() or getattr(parent, 'is_junction', lambda: False)():
            raise ValueError('indirect_evidence_path_forbidden')
    return path


def source_pin(label):
    if (not isinstance(label, str) or '\\' in label or ':' in label or label.startswith('/')
            or any(p in ('', '.', '..') for p in label.split('/'))):
        raise ValueError('repository_relative_source_required')
    path = checked_root(ROOT / label)
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError('missing_local_source')
    blob = path.read_bytes()
    if not 0 < len(blob) <= MAX_RAW_BYTES:
        raise ValueError('bounded_source_required')
    return dict(path=label, bytes=len(blob), sha256=digest(blob))


def _current_sources():
    pins = [source_pin(label) for label in SOURCE_LABELS]
    current = tuple((p['path'],p['bytes'],p['sha256']) for p in pins)
    if current != _IMPORTED_RUNNER_SOURCES:
        raise ValueError('frozen_runner_or_flent_gate_source_drift_since_import')
    return pins


def config_fingerprint(value):
    return digest(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def validate_config(value):
    if not isinstance(value, dict) or type(value.get('channel_width_mhz')) is not int:
        raise ValueError('actual_config_with_explicit_width_required')
    # Secrets are neither acquisition controls nor safe configuration readbacks.
    def walk(node):
        if isinstance(node, dict):
            for key, item in node.items():
                if not isinstance(key, str) or re.search(r'(?i)(password|passwd|psk|secret|credential|access_token)', key):
                    raise ValueError('credential_configuration_forbidden')
                walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(value)
    # Validate the same carrier set as RunMetrics, including real30MHz carriers.
    gate.RunMetrics('width-validation', 'A', 1, 1, 1, 0, 1,
                    channel_width_mhz=value['channel_width_mhz'])
    return strict_json(canonical(value))


def freeze_plan(*, campaign_id, baseline_config, candidate_config, station_hosts,
                server_host='benchmark-server', duration_seconds=10.0, pairs_per_phase=8,
                gate_options=None, execution_kind='SYNTHETIC', created_at_s=None,
                experiment_role='GENERIC_PHYSICAL_RETEST', family_fingerprints=None,
                acquirer_source_path=None):
    """Freeze the complete statistical/acquisition contract before the first byte."""
    identifier(campaign_id, 'campaign_id')
    identifier(experiment_role, 'experiment_role')
    identifier(server_host, 'server_host')
    if (not isinstance(station_hosts, list) or not 1 <= len(station_hosts) <= 20
            or len(set(station_hosts)) != len(station_hosts)):
        raise ValueError('complete_unique_station_roster_required')
    for host in station_hosts:
        identifier(host, 'station_host')
    number(duration_seconds, 'duration_seconds', positive=True)
    if not 1 <= duration_seconds <= 120 or type(pairs_per_phase) is not int or not 8 <= pairs_per_phase <= 64:
        raise ValueError('bounded_duration_and_at_least8_pairs_required')
    if execution_kind not in ('SYNTHETIC', 'PHYSICAL'):
        raise ValueError('explicit_execution_kind_required')
    baseline, candidate = validate_config(baseline_config), validate_config(candidate_config)
    if baseline == candidate:
        raise ValueError('distinct_predeclared_applied_configurations_required')
    if baseline['channel_width_mhz'] != candidate['channel_width_mhz']:
        raise ValueError('gate_requires_matched_carrier_width_per_pair')
    options = strict_json(canonical(gate_options or {}))
    if 'evidence_root' in options:
        raise ValueError('evidence_root_not_a_statistical_option')
    evaluator = gate.RegressionGatekeeper(**options)
    family = list(family_fingerprints or [config_fingerprint(candidate)])
    if (len(family) != evaluator.num_hypotheses_tested or len(set(family)) != len(family)
            or config_fingerprint(candidate) not in family
            or any(not re.fullmatch('[0-9a-f]{64}', str(v)) for v in family)):
        raise ValueError('predeclared_family_count_or_candidate_mismatch')
    created = time.time() if created_at_s is None else number(created_at_s, 'created_at_s')
    if execution_kind == 'PHYSICAL' and acquirer_source_path is None:
        raise ValueError('physical_acquirer_source_binding_required')
    plan = dict(schema_version=1, campaign_id=campaign_id, experiment_role=experiment_role,
                baseline_config=baseline, candidate_config=candidate,
                station_hosts=list(station_hosts), server_host=server_host,
                duration_seconds=duration_seconds, pairs_per_phase=pairs_per_phase,
                execution_kind=execution_kind, created_at_s=created,
                plan_nonce=secrets.token_hex(16), gate_options=options,
                contract=evaluator.frozen_contract, family_fingerprints=family,
                source_bindings=_current_sources(),
                adapter_source_bindings=adapter.source_bindings(),
                acquirer_source=source_pin(acquirer_source_path) if acquirer_source_path else None,
                physical_clock_skew_s=1.0, physical_min_elapsed_fraction=.95,
                callback_overhead_limit_s=15.0)
    plan['plan_sha256'] = digest(canonical(plan))
    return plan


def validate_plan(plan):
    if not isinstance(plan, dict):
        raise ValueError('frozen_plan_required')
    safe = strict_json(canonical(plan))
    declared = safe.pop('plan_sha256', None)
    if declared != digest(canonical(safe)):
        raise ValueError('frozen_plan_hash_mismatch')
    safe['plan_sha256'] = declared
    if type(safe.get('schema_version')) is not int or safe.get('schema_version') != 1 or safe.get('execution_kind') not in ('SYNTHETIC', 'PHYSICAL'):
        raise ValueError('invalid_plan_schema')
    for key in ('campaign_id','experiment_role','server_host'):
        identifier(safe.get(key), key)
    roster = safe.get('station_hosts')
    if (not isinstance(roster,list) or not 1 <= len(roster) <= 20
            or any(not isinstance(x,str) for x in roster) or len(set(roster)) != len(roster)):
        raise ValueError('complete_unique_station_roster_required')
    for host in roster:
        identifier(host,'station_host')
    duration = number(safe.get('duration_seconds'),'duration_seconds',positive=True)
    pairs = safe.get('pairs_per_phase')
    if not 1 <= duration <= 120 or type(pairs) is not int or not 8 <= pairs <= 64:
        raise ValueError('bounded_duration_and_at_least8_pairs_required')
    number(safe.get('created_at_s'),'created_at_s')
    if (safe.get('physical_clock_skew_s') != 1.0
            or type(safe.get('physical_clock_skew_s')) not in (int,float)
            or safe.get('physical_min_elapsed_fraction') != .95
            or safe.get('callback_overhead_limit_s') != 15.0
            or not re.fullmatch('[0-9a-f]{32}',str(safe.get('plan_nonce')))):
        raise ValueError('fixed_bounded_physical_timing_and_nonce_required')
    baseline = validate_config(safe.get('baseline_config'))
    candidate = validate_config(safe.get('candidate_config'))
    if baseline == candidate or baseline['channel_width_mhz'] != candidate['channel_width_mhz']:
        raise ValueError('distinct_matched_width_applied_configurations_required')
    if safe['execution_kind'] == 'PHYSICAL' and not isinstance(safe.get('acquirer_source'),dict):
        raise ValueError('physical_acquirer_source_binding_required')
    if _current_sources() != safe.get('source_bindings'):
        raise ValueError('frozen_runner_or_flent_gate_source_drift')
    adapter._validate_source_revision({'source_bindings': safe.get('adapter_source_bindings')})
    evaluator = gate.RegressionGatekeeper(**safe['gate_options'])
    if safe.get('contract') != evaluator.frozen_contract:
        raise ValueError('frozen_gate_contract_mismatch')
    family = safe.get('family_fingerprints')
    if (not isinstance(family,list) or len(family) != evaluator.num_hypotheses_tested
            or len(set(family)) != len(family) or config_fingerprint(candidate) not in family
            or any(not re.fullmatch('[0-9a-f]{64}',str(fp)) for fp in family)):
        raise ValueError('predeclared_family_count_or_candidate_mismatch')
    if safe.get('acquirer_source') and source_pin(safe['acquirer_source']['path']) != safe['acquirer_source']:
        raise ValueError('acquirer_source_drift')
    return safe


def _assert_frozen(plan, frozen):
    current = validate_plan(plan)
    if canonical(current) != canonical(frozen):
        raise ValueError('campaign_plan_changed_after_initial_freeze')


def _write_new(root, label, blob):
    path = checked_root(root / label)
    if not path.is_relative_to(root):
        raise ValueError('evidence_path_escape')
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open('xb') as stream:
        stream.write(blob)
        stream.flush()
        os.fsync(stream.fileno())
    return dict(path=label, bytes=len(blob), sha256=digest(blob))


def _verify_pins(root, pins):
    for pin in pins:
        path = checked_root(root / pin['path'])
        blob = path.read_bytes()
        if len(blob) != pin['bytes'] or digest(blob) != pin['sha256']:
            raise ValueError('raw_or_normalized_evidence_hash_drift')


def window_specs(plan, phase):
    """Sentinels enclose every explicitly ordered paired acquisition cohort."""
    dataset = plan['campaign_id'] + ':' + phase
    schedule = [('A', plan['pairs_per_phase'] + 1, True)]
    schedule += [(arm, index, False) for index in range(plan['pairs_per_phase']) for arm in ('A', 'B')]
    schedule += [('A', plan['pairs_per_phase'] + 2, True)]
    for ordinal, (arm, index, sentinel) in enumerate(schedule):
        config = plan['baseline_config'] if phase == 'AA_CONTROL' or arm == 'A' else plan['candidate_config']
        yield dict(phase=phase, arm=arm, block_index=index, is_sentinel=sentinel,
                   ordinal=ordinal, dataset_id=dataset,
                   window_id=dataset + ':' + str(index) + ':' + arm + (':S' if sentinel else ''),
                   epoch_id=dataset + ':epoch', experiment_role=plan['experiment_role'],
                   campaign_id=plan['campaign_id'], plan_nonce=plan['plan_nonce'],
                   plan_sha256=plan['plan_sha256'], config=strict_json(canonical(config)),
                   duration_seconds=plan['duration_seconds'], station_hosts=list(plan['station_hosts']),
                   server_host=plan['server_host'], execution_kind=plan['execution_kind'])


def _parse_window(plan, spec, blob, observed, seen_sessions, seen_payloads):
    raw = strict_json(blob)
    for key in ('campaign_id', 'phase', 'arm', 'block_index', 'is_sentinel', 'window_id',
                'dataset_id', 'epoch_id', 'experiment_role', 'plan_nonce', 'plan_sha256', 'execution_kind'):
        if raw.get(key) != spec[key] or type(raw.get(key)) is not type(spec[key]):
            raise ValueError('acquisition_identity_mismatch:' + key)
    session = identifier(raw.get('session_id'), 'session_id')
    if session in seen_sessions:
        raise ValueError('reused_session_between_windows_or_phases')
    seen_sessions.add(session)
    start = number(raw.get('window_start_s'), 'window_start_s')
    end = number(raw.get('window_end_s'), 'window_end_s')
    if start <= plan['created_at_s'] or not math.isclose(end-start, plan['duration_seconds'], rel_tol=.01):
        raise ValueError('window_duration_or_prefreeze_capture')
    if plan['execution_kind'] == 'PHYSICAL':
        if (start < observed['wall_start_s'] - plan['physical_clock_skew_s']
                or end > observed['wall_end_s'] + plan['physical_clock_skew_s']
                or observed['elapsed_s'] < (end-start) * plan['physical_min_elapsed_fraction']
                or observed['elapsed_s'] > plan['duration_seconds'] + plan['callback_overhead_limit_s']):
            raise ValueError('not_fresh_physical_duration_or_clock_coverage')
    config = validate_config(raw.get('config_readback'))
    if canonical(config) != canonical(spec['config']):
        raise ValueError('actual_readback_differs_from_frozen_applied_configuration')
    for key in ('firmware_resets', 'capture_drops'):
        if type(raw.get(key)) is not int or raw[key] < 0:
            raise ValueError('explicit_observed_' + key + '_required')
    if raw['capture_drops'] or raw['firmware_resets']:
        raise ValueError('capture_drop_or_firmware_reset')
    stations = raw.get('stations')
    if not isinstance(stations, dict) or set(stations) != set(plan['station_hosts']):
        raise ValueError('incomplete_station_denominator')
    parsed_iperf, parsed_ping, byte_map, samples = {}, {}, {}, []
    sent = received = 0
    for host in plan['station_hosts']:
        capture = stations[host]
        if not isinstance(capture, dict) or set(capture) != {'iperf3_json', 'ping_stdout'}:
            raise ValueError('raw_iperf_and_ping_text_required')
        iperf, ping = capture['iperf3_json'], capture['ping_stdout']
        if not isinstance(iperf, str) or not isinstance(ping, str):
            raise ValueError('raw_iperf_and_ping_text_required')
        # Reject duplicate JSON keys/nonfinite values before the hardened parser.
        strict_json(iperf)
        parsed = FlentWorkloadOrchestrator.parse_iperf3_json(iperf, expected_peer=plan['server_host'])
        cookie = identifier(parsed['session_id'], 'native_iperf_cookie')
        cookie_key = ('iperf_cookie', cookie)
        if cookie_key in seen_payloads:
            raise ValueError('copied_iperf_session_or_payload')
        seen_payloads.add(cookie_key)
        payload_hash = digest(canonical(capture))
        if payload_hash in seen_payloads:
            raise ValueError('copied_raw_station_payload')
        seen_payloads.add(payload_hash)
        if type(parsed['received_bytes']) is not int or not math.isclose(parsed['duration_seconds'] or 0, end-start, rel_tol=.01):
            raise ValueError('actual_receiver_bytes_and_duration_required')
        parsed_iperf[host] = parsed
        parsed_ping[host] = FlentWorkloadOrchestrator.parse_ping_output(ping)
        if parsed_ping[host].get('duplicates'):
            raise ValueError('duplicate_native_ping_responses')
        if parsed['received_bytes'] <= 0:
            raise ValueError('configured_station_has_no_receiver_service')
        byte_map[host] = parsed['received_bytes']
        samples.extend(parsed_ping[host]['latencies_ms'])
        sent += parsed_ping[host]['sent']
        received += parsed_ping[host]['received']
    flent = FlentWorkloadOrchestrator(FlentWorkloadConfig(plan['server_host'], plan['station_hosts'],
        duration_seconds=plan['duration_seconds'])).synthesize_report(parsed_iperf, parsed_ping)
    if flent.status != 'VALID_NUMERIC':
        raise ValueError('hardened_flent_report_invalid')
    # A/A and the enclosing baseline sentinels must be healthy independently of a gate verdict.
    if (spec['phase'] == 'AA_CONTROL' or spec['is_sentinel']) and sent != received:
        raise ValueError('unhealthy_aa_or_sentinel_packet_loss')
    count = sum(byte_map.values())
    if count <= 0:
        raise ValueError('no_receiver_service')
    ordered = sorted(samples)
    rates = {peer: value*8/(end-start)/1e6 for peer, value in byte_map.items()}
    fairness = sum(rates.values())**2/(len(rates)*sum(v*v for v in rates.values()))
    metrics = dict(goodput_mbps=count*8/(end-start)/1e6,
        p95_lat_ms=ordered[math.ceil(.95*received)-1], p99_lat_ms=ordered[math.ceil(.99*received)-1],
        loss_pct=100*(sent-received)/sent, jain_fairness=fairness,
        channel_width_mhz=config['channel_width_mhz'], worst_peer_goodput_mbps=min(rates.values()),
        firmware_resets=raw['firmware_resets'])
    measurement = dict(run_id=spec['window_id'], arm=spec['arm'], block_index=spec['block_index'],
        block_id=spec['dataset_id'] + ':' + str(spec['block_index']), is_sentinel=spec['is_sentinel'],
        dataset_id=spec['dataset_id'], epoch_id=spec['epoch_id'], session_id=session,
        peer_id=plan['campaign_id'] + ':peers', profile_id='baseline' if config == plan['baseline_config'] else 'candidate',
        experiment_role='AA_NEGATIVE_CONTROL' if spec['phase'] == 'AA_CONTROL' else 'AB_EXPERIMENT',
        controller_role=plan['experiment_role'],
        evidence_state='SYNTHETIC' if plan['execution_kind'] == 'SYNTHETIC' else 'BENCH_EXECUTED',
        window_start_s=start, window_end_s=end, firmware_resets=raw['firmware_resets'], config_readback=config,
        acquisition=dict(receiver_bytes=count, duration_seconds=end-start, packets_sent=sent,
            packets_received=received, latencies_ms=samples, capture_drops=raw['capture_drops'],
            expected_peers=list(plan['station_hosts']), peer_receiver_bytes=byte_map,
            peer_goodput_mbps=rates, goodput_source='receiver', percentile_method='nearest_rank'), metrics=metrics)
    # Numerical Flent display rates round to2dp; raw byte/time ratios remain authoritative.
    if not math.isclose(flent.aggregate_goodput_mbps, round(sum(p['goodput_mbps'] for p in parsed_iperf.values()), 2), abs_tol=.001):
        raise ValueError('flent_aggregate_disagrees')
    return measurement


def _adapter_plan(plan, *, aa=False):
    options = dict(plan['gate_options'])
    if aa:
        options['num_hypotheses_tested'] = 1
    return dict(created_at_s=plan['created_at_s'],
                family_fingerprints=[config_fingerprint(plan['baseline_config'])] if aa else plan['family_fingerprints'],
                contract=gate.RegressionGatekeeper(**options).frozen_contract,
                source_bindings=plan['adapter_source_bindings'])


def _physical_gate(plan, rows, phase, root, options, discovery=None, replication_path=None):
    """Retain sentinels and use the declared B fingerprint, never a positional guess.

    The legacy adapter's campaign helper selects runs[1] as the candidate. Here a
    leading A sentinel makes that an A run, so use its strict normalization/plan
    checks and the real gate directly with the frozen candidate fingerprint.
    """
    frozen = _adapter_plan(plan, aa=phase == 'AA_CONTROL')
    adapter._validate_source_revision(frozen)
    evaluator = gate.RegressionGatekeeper(evidence_root=root, **options)
    prepared = adapter._prepare_rows(rows)
    adapter._validate_plan(frozen, evaluator, prepared, phase)
    runs = [item['run'] for item in prepared]
    errors = gate.validate_run_provenance(runs, root)
    if errors:
        raise ValueError('invalid_native_receipt_provenance:' + ';'.join(errors))
    earlier = None
    if discovery is not None:
        prior = adapter._prepare_rows(discovery)
        adapter._validate_plan(frozen, evaluator, prior, 'AB_DISCOVERY')
        earlier = [item['run'] for item in prior]
    decision = evaluator.evaluate_paired(runs, discovery_runs=earlier,
        replication_receipt_path=replication_path,
        candidate_fingerprint=None if phase == 'AA_CONTROL' else config_fingerprint(plan['candidate_config']))
    return dict(status='EVALUATED', raw_gate=asdict(decision),
        control_result=('PASS_NO_PROMOTION' if decision.verdict not in (
            'SYNTHETIC_PASS','KEEP','KEEP_FOR_REPLICATION','PROMOTE') else 'FAIL_FALSE_POSITIVE')
                if phase == 'AA_CONTROL' else 'NOT_A_CONTROL')


def run_campaign(plan, *, acquire_window, evidence_root, execute=False):
    """Invoke the declared acquirer only after explicit execution and source checks."""
    frozen = validate_plan(plan)
    outcome = dict(status='PLANNED', campaign_id=frozen['campaign_id'],
        experiment_role=frozen['experiment_role'], plan_sha256=frozen['plan_sha256'],
        execution_kind=frozen['execution_kind'], phase_results={}, completed_phases=[], raw_windows=[],
        promotion_eligible=False, deployment_authorized=False, physical_acceptance='UNKNOWN',
        instrument_honesty='NOT_AUTHENTICATED_BY_SOFTWARE', callbacks_invoked=0)
    if execute is not True:
        if execute is not False:
            raise ValueError('explicit_boolean_execute_required')
        return outcome
    if not callable(acquire_window):
        raise ValueError('callable_acquisition_source_required')
    if frozen['execution_kind'] == 'PHYSICAL':
        origin = inspect.getsourcefile(acquire_window if inspect.isfunction(acquire_window) else type(acquire_window))
        expected = frozen.get('acquirer_source')
        if not expected or origin is None or Path(origin).resolve() != (ROOT / expected['path']).resolve():
            raise ValueError('physical_callback_not_bound_to_frozen_source')
    root = checked_root(evidence_root)
    if root.is_relative_to(ROOT) and not any(root.is_relative_to(ROOT / label) for label in (
            '.git', 'artifacts/verification', 'private')):
        raise ValueError('raw_capture_requires_private_evidence_directory')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    namespace = 'campaigns/' + frozen['campaign_id']
    campaign_root = root / namespace
    campaign_root.parent.mkdir(mode=0o700, exist_ok=True)
    campaign_root.mkdir(mode=0o700)  # No overwrite/resume/reuse of previous campaign identity.
    pins = [_write_new(root, namespace + '/plan.json', canonical(frozen))]
    previous_end = frozen['created_at_s']
    sessions, payloads, phase_rows = set(), set(), {}
    try:
        for phase in PHASES:
            rows, runs = [], []
            for spec in window_specs(frozen, phase):
                _assert_frozen(plan, frozen)
                _verify_pins(root, pins)
                wall_start, mono_start = time.time(), time.monotonic()
                outcome['callbacks_invoked'] += 1
                request = strict_json(canonical(spec))
                request['deadline_wall_s'] = wall_start + frozen['duration_seconds'] + frozen['callback_overhead_limit_s']
                blob = acquire_window(request)
                observed = dict(wall_start_s=wall_start, wall_end_s=time.time(), elapsed_s=time.monotonic()-mono_start)
                if not isinstance(blob, bytes) or not 0 < len(blob) <= MAX_RAW_BYTES:
                    raise ValueError('bounded_exact_raw_window_bytes_required')
                stem = namespace + '/' + phase + '/' + str(spec['ordinal'])
                raw_pin = _write_new(root, stem + '.raw.json', blob)
                timing_pin = _write_new(root, stem + '.observed.json', canonical(observed))
                pins.extend([raw_pin, timing_pin])
                outcome['raw_windows'].append(dict(raw_pin, phase=phase, window_id=spec['window_id']))
                _assert_frozen(plan, frozen)
                measurement = _parse_window(frozen, spec, blob, observed, sessions, payloads)
                if measurement['window_start_s'] < previous_end:
                    raise ValueError('cross_phase_overlap_or_chronological_reordering')
                previous_end = measurement['window_end_s']
                path = stem + '.normalized.json'
                if frozen['execution_kind'] == 'PHYSICAL':
                    prepared = adapter.prepare_measurement(measurement, path)
                    record_blob, run = prepared['blob'], prepared['run']
                else:
                    record_blob = canonical(measurement)
                    run = gate.RunMetrics(measurement['run_id'], measurement['arm'], **measurement['metrics'],
                        block_index=measurement['block_index'], is_sentinel=measurement['is_sentinel'],
                        evidence_state='SYNTHETIC', raw_sha256=digest(record_blob), raw_evidence_path=path,
                        session_id=measurement['session_id'], peer_id=measurement['peer_id'],
                        window_start_s=measurement['window_start_s'], window_end_s=measurement['window_end_s'],
                        applied_config_sha256=config_fingerprint(measurement['config_readback']))
                normalized_pin = _write_new(root, path, record_blob)
                pins.append(normalized_pin)
                rows.append(dict(measurement=measurement, receipt_path=path, receipt_sha256=normalized_pin['sha256']))
                runs.append(run)
            _verify_pins(root, pins)
            phase_rows[phase] = rows
            options = dict(frozen['gate_options'])
            if phase == 'AA_CONTROL':
                options['num_hypotheses_tested'] = 1
            if frozen['execution_kind'] == 'PHYSICAL':
                extra = {}
                if phase == 'AB_HOLDOUT':
                    proof = dict(evidence_state='BENCH_REPLICATED',
                        candidate_fingerprint=config_fingerprint(frozen['candidate_config']),
                        frozen_plan=_adapter_plan(frozen),
                        discovery=[dict(run_id=r['measurement']['run_id'], raw_sha256=r['receipt_sha256'])
                                   for r in phase_rows['AB_DISCOVERY']],
                        holdout=[dict(run_id=r['measurement']['run_id'], raw_sha256=r['receipt_sha256']) for r in rows])
                    proof_pin = _write_new(root, namespace + '/replication.json', adapter.canonical(proof))
                    pins.append(proof_pin)
                    extra = dict(discovery_rows=phase_rows['AB_DISCOVERY'],
                                 replication_receipt_path=proof_pin['path'], replication_receipt_sha256=proof_pin['sha256'])
                result = _physical_gate(frozen, rows, phase, root, options,
                    discovery=extra.get('discovery_rows'), replication_path=extra.get('replication_receipt_path'))
            else:
                decision = gate.RegressionGatekeeper(evidence_root=root, **options).evaluate_paired(runs)
                result = dict(status='EVALUATED', raw_gate=asdict(decision),
                    control_result=('PASS_NO_PROMOTION' if decision.verdict not in (
                        'SYNTHETIC_PASS', 'KEEP', 'KEEP_FOR_REPLICATION', 'PROMOTE') else 'FAIL_FALSE_POSITIVE')
                        if phase == 'AA_CONTROL' else 'NOT_A_CONTROL')
            outcome['phase_results'][phase] = result
            result_pin = _write_new(root, namespace + '/' + phase + '/evaluation.json', canonical(result))
            pins.append(result_pin)
            if result.get('status') != 'EVALUATED':
                raise ValueError('phase_gate_invalid:' + phase)
            verdict = (result.get('raw_gate') or {}).get('verdict')
            if phase == 'AA_CONTROL':
                if result.get('control_result') != 'PASS_NO_PROMOTION' or verdict not in ('INCONCLUSIVE', 'REJECT'):
                    raise ValueError('AA_control_did_not_establish_no_promotion')
            elif phase == 'AB_DISCOVERY':
                expected = 'SYNTHETIC_PASS' if frozen['execution_kind'] == 'SYNTHETIC' else 'KEEP_FOR_REPLICATION'
                if verdict != expected:
                    outcome['status'] = 'DISCOVERY_NOT_CONFIRMED'
                    break
            else:
                expected = 'SYNTHETIC_PASS' if frozen['execution_kind'] == 'SYNTHETIC' else 'PROMOTE'
                if verdict != expected:
                    outcome['status'] = 'HOLDOUT_NOT_CONFIRMED'
                    break
            outcome['completed_phases'].append(phase)
        if outcome['completed_phases'] == list(PHASES):
            outcome['status'] = ('SYNTHETIC_DIAGNOSTIC_COMPLETE' if frozen['execution_kind'] == 'SYNTHETIC'
                                 else 'PHYSICAL_STATISTICAL_REPLICATION_COMPLETE')
            outcome['promotion_eligible'] = (frozen['execution_kind'] == 'PHYSICAL' and
                outcome['phase_results']['AB_HOLDOUT']['raw_gate']['promotion_eligible'] is True)
        _assert_frozen(plan, frozen)
        _verify_pins(root, pins)
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, OverflowError, AttributeError) as exc:
        outcome.update(status='FAILED_CLOSED', failure_reason=str(exc), promotion_eligible=False)
    outcome['evidence_manifest'] = pins
    _write_new(root, namespace + '/outcome.json', canonical(outcome))
    return outcome


def build_source_receipt(root=ROOT):
    from tools.verify.stage779_822_offline_common import receipt, save, snapshot
    _current_sources()
    labels = [*SOURCE_LABELS, 'tests/test_stage959a_unified_physical_runner.py']
    data = receipt(959, 'Unified raw physical-retest runner software contract', [snapshot(root, p) for p in labels])
    data.update(evidence_provenance_class='CONFIRMED_STATIC_BINARY',
        provenance_scope='source inspection and local synthetic/fault fixtures; not a physical campaign',
        physical_acceptance='UNKNOWN', live_campaign_executed=False, deployment_authorized=False,
        required_phases=list(PHASES), raw_window_sha256=True, gatekeeper_direct=True,
        acquisition_default='INSPECT_ONLY', physical_adapter_source_bound=True,
        software_instrument_authentication=False)
    return save(root, STEM, data,
        'Source-bound Flent raw parsing and the real RegressionGatekeeper are connected in one runner.\n'
        'freeze_plan binds controller role, configurations, station roster, family, gate contract and sources before A/A.\n'
        'Inspection never invokes an acquirer. Execution requires execute=True; the CLI requires --execute.\n'
        'A physical acquirer must match a frozen repository source file; the runner itself provides no SSH transport.\n'
        'Every window supplies exact raw envelope bytes with iperf3 JSON and native ping text for every configured station.\n'
        'Empty responses, iperf errors, absent receiver counts, missing peers/readbacks/sentinels and all capture/reset faults reject.\n'
        'A/A and every enclosing sentinel require zero loss. Passing a generic gate control label alone is insufficient.\n'
        'Discovery must pass before disjoint holdout. IDs, cookies, raw payloads, windows and sessions cannot be reused.\n'
        'Physical callbacks must consume the measured duration and timestamps must fit observed acquisition boundaries.\n'
        'Acquirers must enforce the supplied deadline and restore baseline on abort; synchronous callbacks cannot be forcibly cancelled here.\n'
        'The runner owns acquisition validation, not a universal transport timeout or hardware rollback implementation.\n'
        'Raw bytes, observed callback timing, normalized receipts, plan and phase results are saved with SHA256 hashes.\n'
        'Existing campaign directories and files are never overwritten. Root paths, source/data drift and duplicate JSON keys reject.\n'
        'Synthetic fixtures retain SYNTHETIC origin and can never become physical promotion evidence.\n'
        'Hashes authenticate supplied bytes, not the honesty of an instrument. Physical acceptance remains UNKNOWN.\n'
        'A statistical PROMOTE does not authorize deployment, flashing or radio mutation.\n'
        'All task verification is local; no radio campaign, SSH or durable-memory ingestion is executed.\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--acquirer', type=Path, help='Frozen local source implementing acquire_window(spec)->bytes')
    parser.add_argument('--evidence-root', type=Path)
    parser.add_argument('--build-receipt', action='store_true')
    args = parser.parse_args(argv)
    if args.build_receipt:
        if args.execute:
            parser.error('receipt construction never executes a campaign')
        print(json.dumps({'stage': '959A', 'status': build_source_receipt()['status']}))
        return 0
    if args.plan is None:
        print('PLANNED unified runner; provide a frozen plan; physical_acceptance=UNKNOWN')
        return 0
    plan = strict_json(args.plan.read_bytes())
    validate_plan(plan)
    if not args.execute:
        print(json.dumps(run_campaign(plan, acquire_window=None, evidence_root=args.evidence_root or '.git/stage959-inspection')))
        return 0
    if not args.acquirer or not args.evidence_root or plan['execution_kind'] != 'PHYSICAL':
        parser.error('physical execution requires frozen PHYSICAL plan, --acquirer and --evidence-root')
    pin = plan['acquirer_source']
    if args.acquirer.resolve() != (ROOT / pin['path']).resolve() or source_pin(pin['path']) != pin:
        parser.error('acquirer does not match the frozen source')
    loaded = runpy.run_path(str(args.acquirer.resolve()))
    callback = loaded.get('acquire_window')
    result = run_campaign(plan, acquire_window=callback, evidence_root=args.evidence_root, execute=True)
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PHYSICAL_STATISTICAL_REPLICATION_COMPLETE' else 1


_IMPORTED_RUNNER_SOURCES = tuple((p['path'],p['bytes'],p['sha256'])
                                for p in (source_pin(label) for label in SOURCE_LABELS))


if __name__ == '__main__':
    raise SystemExit(main())
