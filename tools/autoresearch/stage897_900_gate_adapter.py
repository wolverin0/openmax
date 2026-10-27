# PUBLIC_REDACTED_DERIVATIVE; original_sha256=ce3d5e2a361273912d836958d2e9a6bfe98d8ea7b8ae72e610b14518cd92b50c
# Private originals are required for native replay.
"""Strict measured-data adapter for the paired-block / single-step Sidak gate.

No SSH, load generation or target access lives here. prepare_measurement creates
receipt bytes in memory; its caller must persist those exact bytes. evaluate_campaign
then asks the real gate to validate them under evidence_root. An AA control never
changes the gate's verdict to hide a false positive. Fixture receipts prove only
the adapter's arithmetic and binding, not the honesty of a physical instrument.
"""
from __future__ import annotations
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import re
from analysis.regression_gate import gatekeeper as gate
MODES = ('AA_CONTROL', 'AB_DISCOVERY', 'AB_HOLDOUT')
PHYSICAL_STATES = frozenset((s.value for s in gate.EvidenceState if s not in (gate.EvidenceState.SYNTHETIC, gate.EvidenceState.STATIC_VERIFIED)))
ROOT = Path(__file__).resolve().parents[2]
MAX_RECEIPT = 8 * 1024 * 1024

class SourceDrift(ValueError):
    """The acquisition plan or disk no longer matches imported gate semantics."""

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')

def digest(blob):
    return hashlib.sha256(blob).hexdigest()

def _identity(value, name):
    if not isinstance(value, str) or not re.fullmatch('[A-Za-z0-9_.:-]{1,160}', value):
        raise ValueError('missing_or_invalid_' + name)
    return value

def _number(value, name, *, low=0, high=None):
    try:
        finite = type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite or value < low or (high is not None and value > high):
        raise ValueError('missing_or_invalid_' + name)
    return value

def _integer(value, name, *, low=0):
    if type(value) is not int or value < low or value > 2 ** 64 - 1:
        raise ValueError('missing_or_invalid_' + name)
    return value

def _relative_path(value):
    if not isinstance(value, str) or not value or '\\' in value or (':' in value) or value.startswith('/') or any((p in ('', '.', '..') for p in value.split('/'))):
        raise ValueError('safe_relative_receipt_path_required')
    return value

def _hash(value, name):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('missing_or_invalid_' + name)
    return value

def prepare_measurement(raw, receipt_path):
    """Normalize explicit receiver/ping observations; reject every absent metric.

    Required raw identity: run_id, arm, block_index, block_id, dataset_id,
    epoch_id, session_id, peer_id, profile_id, experiment_role, evidence_state,
    is_sentinel (explicit bool; paired A/B windows normally False),
    window_start_s/end_s. Readback must explicitly contain channel_width_mhz.
    acquisition must contain receiver_bytes, duration_seconds, packets_sent/
    received, latencies_ms, capture_drops, expected_peers, peer_receiver_bytes.
    firmware_resets is an observed required integer. No metric is defaulted.
    """
    if not isinstance(raw, dict):
        raise ValueError('measurement_object_required')
    encoded = canonical(raw)
    if len(encoded) > MAX_RECEIPT:
        raise ValueError('measurement_size_limit')
    safe = json.loads(encoded)
    for key in ('run_id', 'block_id', 'dataset_id', 'epoch_id', 'session_id', 'peer_id', 'profile_id', 'experiment_role'):
        _identity(safe.get(key), key)
    if safe.get('arm') not in ('A', 'B'):
        raise ValueError('A_or_B_arm_required')
    if type(safe.get('is_sentinel')) is not bool:
        raise ValueError('explicit_boolean_is_sentinel_required')
    index = _integer(safe.get('block_index'), 'block_index')
    if safe['block_id'] != safe['dataset_id'] + ':' + str(index):
        raise ValueError('block_id_must_bind_dataset_and_index')
    if safe.get('evidence_state') not in PHYSICAL_STATES:
        raise ValueError('explicit_physical_evidence_origin_required')
    start = _number(safe.get('window_start_s'), 'window_start_s')
    end = _number(safe.get('window_end_s'), 'window_end_s')
    if end <= start:
        raise ValueError('positive_time_window_required')
    config = safe.get('config_readback')
    if not isinstance(config, dict) or not config:
        raise ValueError('actual_config_readback_required')
    width = config.get('channel_width_mhz')
    if type(width) is not int:
        raise ValueError('explicit_channel_width_required')
    acquisition = safe.get('acquisition')
    if not isinstance(acquisition, dict):
        raise ValueError('actual_acquisition_required')
    if acquisition.get('goodput_source', 'receiver') != 'receiver':
        raise ValueError('sender_rate_is_not_receiver_observation')
    if acquisition.get('percentile_method', 'nearest_rank') != 'nearest_rank':
        raise ValueError('percentile_method_changed')
    duration = _number(acquisition.get('duration_seconds'), 'duration_seconds', low=1e-12)
    if not math.isclose(duration, end - start, rel_tol=0.01):
        raise ValueError('receiver_duration_and_window_disagree')
    received_bytes = _integer(acquisition.get('receiver_bytes'), 'receiver_bytes')
    sent = _integer(acquisition.get('packets_sent'), 'packets_sent', low=1)
    received = _integer(acquisition.get('packets_received'), 'packets_received', low=1)
    if received > sent:
        raise ValueError('received_packets_exceed_sent')
    if _integer(acquisition.get('capture_drops'), 'capture_drops') != 0:
        raise ValueError('capture_coverage_incomplete')
    samples = acquisition.get('latencies_ms')
    if not isinstance(samples, list) or len(samples) != received:
        raise ValueError('actual_ping_sample_coverage_required')
    for sample in samples:
        _number(sample, 'latency_ms')
    peers = acquisition.get('expected_peers')
    byte_map = acquisition.get('peer_receiver_bytes')
    if not isinstance(peers, list) or not peers or any((not isinstance(p, str) for p in peers)) or (len(peers) != len(set(peers))) or (not isinstance(byte_map, dict)) or (set(peers) != set(byte_map)):
        raise ValueError('explicit_unique_peer_denominator_required')
    for peer, count in byte_map.items():
        _identity(peer, 'configured_peer')
        _integer(count, 'peer_receiver_bytes')
    if sum(byte_map.values()) != received_bytes or received_bytes <= 0:
        raise ValueError('receiver_peer_bytes_missing_or_disagree')
    reset_count = _integer(safe.get('firmware_resets'), 'firmware_resets')
    rates = {peer: count * 8 / duration / 1000000.0 for peer, count in byte_map.items()}
    rate = received_bytes * 8 / duration / 1000000.0
    fairness = sum(rates.values()) ** 2 / (len(rates) * sum((v * v for v in rates.values())))
    ordered = sorted(samples)
    metrics = dict(goodput_mbps=rate, p95_lat_ms=ordered[math.ceil(0.95 * received) - 1], p99_lat_ms=ordered[math.ceil(0.99 * received) - 1], loss_pct=100 * (sent - received) / sent, jain_fairness=fairness, channel_width_mhz=width, worst_peer_goodput_mbps=min(rates.values()), firmware_resets=reset_count)
    if 'metrics' in safe:
        if not isinstance(safe['metrics'], dict):
            raise ValueError('metrics_summary_object_required')
        for key, value in safe['metrics'].items():
            if key not in metrics or type(value) not in (int, float) or (not math.isfinite(value)) or (not math.isclose(value, metrics[key], abs_tol=1e-06)):
                raise ValueError('supplied_summary_disagrees_with_observations')
    config_fingerprint = digest(json.dumps(config, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())
    record = {key: safe[key] for key in ('run_id', 'arm', 'block_index', 'block_id', 'is_sentinel', 'dataset_id', 'epoch_id', 'session_id', 'peer_id', 'profile_id', 'experiment_role', 'evidence_state', 'window_start_s', 'window_end_s')}
    record.update(config_readback=config, metrics=metrics, acquisition=dict(acquisition, goodput_source='receiver', percentile_method='nearest_rank', peer_goodput_mbps=rates))
    blob = canonical(record)
    if len(blob) > MAX_RECEIPT:
        raise ValueError('receipt_size_limit')
    path = _relative_path(receipt_path)
    run = gate.RunMetrics(run_id=safe['run_id'], arm=safe['arm'], **metrics, block_index=index, evidence_state=safe['evidence_state'], raw_sha256=digest(blob), raw_evidence_path=path, session_id=safe['session_id'], peer_id=safe['peer_id'], is_sentinel=safe['is_sentinel'], window_start_s=start, window_end_s=end, applied_config_sha256=config_fingerprint)
    return dict(record=record, blob=blob, sha256=digest(blob), run=run)

def _prepare_rows(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError('nonempty_measured_rows_required')
    prepared = []
    for wrapper in rows:
        if not isinstance(wrapper, dict):
            raise ValueError('measured_row_wrapper_required')
        item = prepare_measurement(wrapper.get('measurement'), wrapper.get('receipt_path'))
        if item['sha256'] != _hash(wrapper.get('receipt_sha256'), 'receipt_sha256'):
            raise ValueError('provided_receipt_sha_mismatch')
        prepared.append(item)
    records = [item['record'] for item in prepared]
    for name in ('run_id',):
        if len({r[name] for r in records}) != len(records):
            raise ValueError('duplicate_' + name)
    if len({item['sha256'] for item in prepared}) != len(prepared) or len({item['run'].raw_evidence_path for item in prepared}) != len(prepared):
        raise ValueError('duplicate_receipt_identity')
    for a, b in zip(records, records[1:]):
        if a['window_end_s'] > b['window_start_s']:
            raise ValueError('overlapping_or_reordered_measured_windows')
    blocks = gate.build_paired_blocks([item['run'] for item in prepared])
    if not blocks:
        raise ValueError('complete_paired_blocks_required')
    return prepared

def _validate_plan(plan, evaluator, rows, mode):
    if not isinstance(plan, dict):
        raise ValueError('frozen_plan_object_required')
    created = _number(plan.get('created_at_s'), 'plan_created_at_s')
    if created >= min((item['run'].window_start_s for item in rows)):
        raise ValueError('plan_not_frozen_before_acquisition')
    if plan.get('contract') != evaluator.frozen_contract:
        raise ValueError('frozen_objective_or_family_contract_changed')
    family = plan.get('family_fingerprints')
    if not isinstance(family, list) or len(family) != evaluator.num_hypotheses_tested or len(set(family)) != len(family):
        raise ValueError('frozen_family_count_or_identity_mismatch')
    for fp in family:
        _hash(fp, 'family_fingerprint')
    fingerprints = {item['run'].applied_config_sha256 for item in rows if item['run'].arm == 'B'}
    if len(fingerprints) != 1 or not fingerprints <= set(family):
        raise ValueError('candidate_readback_not_in_frozen_family')
    role = 'AA_NEGATIVE_CONTROL' if mode == 'AA_CONTROL' else 'AB_EXPERIMENT'
    if any((item['record']['experiment_role'] != role for item in rows)):
        raise ValueError('experiment_role_does_not_match_mode')
    profiles = {item['record']['profile_id'] for item in rows}
    if mode == 'AA_CONTROL':
        if len(profiles) != 1 or len({item['run'].applied_config_sha256 for item in rows}) != 1:
            raise ValueError('AA_requires_same_profile_and_readback')
    else:
        if len(profiles) != 2:
            raise ValueError('AB_requires_two_declared_profiles')
        for arm in ('A', 'B'):
            if len({item['record']['profile_id'] for item in rows if item['run'].arm == arm}) != 1:
                raise ValueError('profile_arm_identity_changed')
            if len({item['run'].applied_config_sha256 for item in rows if item['run'].arm == arm}) != 1:
                raise ValueError('applied_readback_changed_within_arm')
        if len({item['run'].applied_config_sha256 for item in rows}) != 2:
            raise ValueError('AB_requires_distinct_stable_applied_readbacks')

def evaluate_campaign(rows, *, evidence_root, frozen_plan, mode, gate_options=None, discovery_rows=None, replication_receipt_path=None, replication_receipt_sha256=None):
    """Run the real gate; invalid observations are never a passing AA control.

    rows=[{'measurement': raw, 'receipt_path': relative path,
           'receipt_sha256': SHA of prepare_measurement(raw,path)['blob']}].
    There is deliberately no holdout_replicated boolean input.
    """
    result = dict(status='INVALID_DATA', mode=mode, raw_gate=None, control_result='INVALID_DATA', reasons=[], normalized_measurements=[], deployment_authorized=False, pairing_unit='paired_block', multiplicity_method='single_step_Sidak')
    try:
        if mode not in MODES:
            raise ValueError('declared_campaign_mode_required')
        _validate_source_revision(frozen_plan)
        if gate_options is not None and (not isinstance(gate_options, dict)):
            raise ValueError('gate_options_object_required')
        options = dict(gate_options or {})
        if 'evidence_root' in options:
            raise ValueError('evidence_root_must_be_explicit')
        evaluator = gate.RegressionGatekeeper(evidence_root=evidence_root, **options)
        prepared = _prepare_rows(rows)
        _validate_plan(frozen_plan, evaluator, prepared, mode)
        runs = [item['run'] for item in prepared]
        provenance = gate.validate_run_provenance(runs, evidence_root)
        if provenance:
            result['reasons'] = provenance
            return result
        discovery = None
        if mode == 'AB_HOLDOUT':
            earlier = _prepare_rows(discovery_rows)
            _validate_plan(frozen_plan, evaluator, earlier, 'AB_DISCOVERY')
            for arm in ('A', 'B'):
                if {x['run'].applied_config_sha256 for x in earlier if x['run'].arm == arm} != {x['run'].applied_config_sha256 for x in prepared if x['run'].arm == arm}:
                    raise ValueError('discovery_holdout_applied_readback_changed_' + arm)
            for identity in ('run_id', 'session_id', 'epoch_id', 'block_id', 'dataset_id'):
                if {x['record'][identity] for x in earlier} & {x['record'][identity] for x in prepared}:
                    raise ValueError('discovery_holdout_overlap_' + identity)
            if {x['run'].raw_evidence_path for x in earlier} & {x['run'].raw_evidence_path for x in prepared}:
                raise ValueError('discovery_holdout_overlap_receipt_path')
            path = _relative_path(replication_receipt_path)
            _, actual_hash = gate._read_evidence(Path(evidence_root), path)
            if actual_hash != _hash(replication_receipt_sha256, 'replication_receipt_sha256'):
                raise ValueError('replication_receipt_sha_mismatch')
            discovery = [item['run'] for item in earlier]
            errors = gate.validate_holdout_evidence(discovery, runs, runs[1].applied_config_sha256, evidence_root, path, contract=evaluator.frozen_contract)
            if errors:
                result['reasons'] = errors
                return result
        elif discovery_rows is not None or replication_receipt_path is not None or replication_receipt_sha256 is not None:
            raise ValueError('replication_evidence_only_for_disjoint_holdout')
        decision = evaluator.evaluate_paired(runs, discovery_runs=discovery, replication_receipt_path=replication_receipt_path, candidate_fingerprint=runs[1].applied_config_sha256 if mode != 'AA_CONTROL' else None)
        result.update(status='EVALUATED', raw_gate=asdict(decision), normalized_measurements=[dict(run_id=r.run_id, arm=r.arm, block_index=r.block_index, goodput_mbps=r.goodput_mbps, raw_sha256=r.raw_sha256, raw_evidence_path=r.raw_evidence_path, applied_config_sha256=r.applied_config_sha256) for r in runs], reasons=[decision.rationale])
        if mode == 'AA_CONTROL':
            result['control_result'] = 'FAIL_FALSE_POSITIVE' if decision.verdict in ('KEEP', 'KEEP_FOR_REPLICATION', 'PROMOTE', 'SYNTHETIC_PASS') else 'PASS_NO_PROMOTION'
        else:
            result['control_result'] = 'NOT_A_CONTROL'
        return result
    except SourceDrift as exc:
        result['status'] = 'SOURCE_DRIFT'
        result['reasons'] = [str(exc)]
        return result
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
        result['reasons'] = [str(exc)]
        return result

def _snapshot_source_bindings():
    """Read current bounded source bytes solely to detect post-import drift."""
    paths = (Path(__file__), Path(gate.__file__), ROOT / 'analysis/metrics/schema.py')
    pins = []
    for path in paths:
        with path.open('rb') as stream:
            blob = stream.read(1024 * 1024 + 1)
        if not blob or len(blob) > 1024 * 1024:
            raise SourceDrift('SOURCE_DRIFT: source missing or outside bounded size')
        pins.append(dict(path=path.relative_to(ROOT).as_posix(), bytes=len(blob), sha256=digest(blob)))
    return pins

def _pin_tuple(bindings):
    if not isinstance(bindings, list) or len(bindings) != 3 or any((not isinstance(x, dict) for x in bindings)):
        raise ValueError('three_frozen_source_bindings_required')
    if len({x.get('path') for x in bindings}) != 3:
        raise ValueError('unique_frozen_source_paths_required')
    result = []
    for item in bindings:
        path = _relative_path(item.get('path'))
        size = _integer(item.get('bytes'), 'source_size', low=1)
        result.append((path, size, _hash(item.get('sha256'), 'source_sha256')))
    return tuple(sorted(result))

def source_bindings():
    """Return copies of the immutable import-time revision, never repin new bytes.

    Freeze these in the acquisition plan before capture. A changed source requires
    a new process/import and a new plan, not reassignment of an old campaign's pins.
    """
    return [dict(path=path, bytes=size, sha256=checksum) for path, size, checksum in _IMPORTED_SOURCE_BINDINGS]

def _validate_source_revision(plan):
    if not isinstance(plan, dict) or 'source_bindings' not in plan:
        raise ValueError('frozen_plan_source_bindings_required')
    if _pin_tuple(plan['source_bindings']) != _IMPORTED_SOURCE_BINDINGS:
        raise SourceDrift('SOURCE_DRIFT: frozen acquisition sources differ from imported adapter/gate/schema')
    try:
        current = _pin_tuple(_snapshot_source_bindings())
    except OSError as exc:
        raise SourceDrift('SOURCE_DRIFT: current source unavailable') from exc
    if current != _IMPORTED_SOURCE_BINDINGS:
        raise SourceDrift('SOURCE_DRIFT: current disk sources differ from imported adapter/gate/schema')
_IMPORTED_SOURCE_BINDINGS = _pin_tuple(_snapshot_source_bindings())
