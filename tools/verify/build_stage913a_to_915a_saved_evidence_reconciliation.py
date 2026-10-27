#!/usr/bin/env python3
"""Reconcile saved evidence locally; never acquire, approve or rewrite history."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify import stage779_822_offline_common as c
from tools.verify import verify_stage884a_live_pbe5ac_quad_patch_v7_gate as gate884
from tools.verify import verify_stage900a_post_audit_live_execution_gate as gate900

STEMS = {
    '913A': 'stage913a_saved_879_to_884_software_compatibility',
    '914A': 'stage914a_saved_897_to_900_evidence_replay',
    '915A': 'stage915a_qualified_publication_readiness',
}
SELF = 'tools/verify/build_stage913a_to_915a_saved_evidence_reconciliation.py'
HELPER = 'firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh'
HISTORICAL_KIT_SHA = 'df1501405609c5c1a6d89c6ee6a2b185519db40dcc512f0bb51f116aaaf3d485'
SOURCE_LABELS = (
    SELF, HELPER, 'tools/verify/stage779_822_offline_common.py',
    'tools/verify/verify_stage884a_live_pbe5ac_quad_patch_v7_gate.py',
    'tools/verify/verify_stage900a_post_audit_live_execution_gate.py',
    'tools/autoresearch/run_stage897a_live_wa_hardened_kit_verify.py',
    'tools/autoresearch/run_stage899a_live_powerbeam_rocket_readonly_aa.py',
    'tools/autoresearch/stage897_900_gate_adapter.py',
    'analysis/regression_gate/gatekeeper.py', 'analysis/metrics/schema.py',
    'workloads/flent_orchestrator.py', 'tests/test_stage879a_to_884a_suite.py',
    'tests/test_stage897a_to_900a_suite.py',
)


def checked_pin(root: Path, binding: dict) -> dict:
    """Require an exact saved pin, without allowing booleans as lengths."""
    if (not isinstance(binding, dict) or type(binding.get('bytes')) is not int
            or binding['bytes'] < 0 or not isinstance(binding.get('sha256'), str)
            or not re.fullmatch('[0-9a-f]{64}', binding['sha256'])):
        raise ValueError('invalid_saved_binding')
    actual = c.snapshot(root, binding['path'])
    if (not actual['available'] or actual['bytes'] != binding['bytes']
            or actual['sha256'] != binding['sha256']):
        raise ValueError('saved_binding_mismatch')
    return actual


def historical_summary(root: Path, bindings: list[dict]) -> dict:
    """Public summary omits private paths and does not upgrade stale pins."""
    inventory = [gate884.binding_state(root, row) for row in bindings]
    return dict(count=len(inventory), current_matches=sum(x['current_binding_verified'] for x in inventory),
                current_drift=sum(x['state'] == 'CURRENT_DRIFT' for x in inventory),
                missing=sum(x['state'] == 'MISSING' for x in inventory),
                declaration_hashes=[x['original_binding']['sha256'] for x in inventory],
                historical_declarations_rewritten=False, stale_review_acceptance=False)


def stage913(root: Path) -> dict:
    bindings, captures, statuses = [], 0, []
    for stage, stem in gate884.STEMS.items():
        if stage == '884A':
            continue
        row = c.read_json(root, f'artifacts/autoresearch/{stem}.json')
        if row.get('stage') != stage or row.get('acceptance') != 'NOT_ACCEPTED':
            raise ValueError('historical_stage_or_acceptance_changed')
        statuses.append(dict(stage=stage, status=row['status'], acceptance=row['acceptance']))
        bindings.extend(gate884.record_bindings(row))
        if row.get('evidence'):
            checked_pin(root, row['evidence'])
            captures += 1
    review = c.read_json(root, 'artifacts/verification/stage879a/independent_patch_spec_review.json')
    bindings.extend(dict(path=x['path'], sha256=x['sha256'], bytes=x.get('bytes', x.get('size_bytes')))
                    for x in review['reviewed_files'])
    return dict(saved_stages=statuses, capture_bindings_verified=captures,
                historical_sources=historical_summary(root, bindings),
                physical_acceptance='UNKNOWN', hardware_gate_acceptance='NOT_ACCEPTED',
                review_of_changed_helper='NOT_INFERRED_FROM_HISTORICAL_REVIEW')


def replay_window(root: Path, wrapper: dict) -> dict:
    """Use current pure parsers against hash-bound saved observations only."""
    raw = wrapper['measurement']
    binding = raw['native_capture']
    checked_pin(root, binding)
    native = c.read_json(root, binding['path'])
    row = native['results'][0]
    parser = gate900.s899
    if (native.get('phase') != 'MEASURED_AA_WINDOW'
            or row.get('stdin_sha256') != hashlib.sha256(parser.WINDOW.encode()).hexdigest()):
        raise ValueError('saved_native_program_or_phase_mismatch')
    for key in ('arm', 'block_index', 'window_start_s', 'window_end_s', 'dataset_id'):
        if native[key] != raw[key]:
            raise ValueError('saved_native_window_identity_mismatch')
    for pin in (native['prewindow_config'], raw['postwindow_config_capture']):
        checked_pin(root, pin)
        config = c.read_json(root, pin['path'])['results'][0]
        if parser.config_from_capture(config) != raw['config_readback']:
            raise ValueError('saved_config_readback_mismatch')
    regenerated = parser.normalize_window(row, raw['config_readback'], arm=raw['arm'],
        index=raw['block_index'], dataset=raw['dataset_id'], session=raw['session_id'],
        window_start=native['window_start_s'], window_end=native['window_end_s'], raw_pin=binding)
    if (regenerated['acquisition'] != raw['acquisition']
            or regenerated['firmware_resets'] != raw['firmware_resets']):
        raise ValueError('saved_native_recomputation_mismatch')
    ping = gate900.FWO.parse_ping_output(row['stdout'])
    if (ping['sent'], ping['received'], ping['latencies_ms']) != (
            raw['acquisition']['packets_sent'], raw['acquisition']['packets_received'],
            raw['acquisition']['latencies_ms']):
        raise ValueError('saved_ping_recomputation_mismatch')
    prepared = gate900.adapter.prepare_measurement(raw, wrapper['receipt_path'])
    if prepared['sha256'] != wrapper['receipt_sha256']:
        raise ValueError('saved_normalized_hash_mismatch')
    checked_pin(root, dict(path=wrapper['receipt_path'], bytes=len(prepared['blob']),
                           sha256=prepared['sha256']))
    return dict(receiver_bytes=raw['acquisition']['receiver_bytes'], packets_sent=ping['sent'],
                packets_received=ping['received'])


def stage914(root: Path) -> dict:
    rows = {stage: c.read_json(root, f'artifacts/autoresearch/{stem}.json')
            for stage, stem in gate900.STEMS.items()}
    for stage, row in rows.items():
        if row.get('stage') != stage or row.get('acceptance') != 'NOT_ACCEPTED':
            raise ValueError('saved_stage_or_acceptance_changed')
    # Saved900 is the cross-reference for the original897..899 receipt bytes.
    for pin in rows['900A']['source_bindings']:
        checked_pin(root, pin)
    wa = rows['897A']
    modes = []
    for field in ('native_dry_run', 'native_verify_mode_probe'):
        checked_pin(root, wa[field])
        modes.append(c.read_json(root, wa[field]['path'])['results'][0])
    if any(row.get('stdin_sha256') != HISTORICAL_KIT_SHA for row in modes):
        raise ValueError('historical_kit_capture_hash_changed')
    if (modes[0].get('exit_code') != 0 or 'PLANNED' not in modes[0].get('stdout', '')
            or modes[1].get('exit_code') != 64):
        raise ValueError('historical_mode_outcome_changed')
    if wa.get('apply_executed') is not False or wa.get('verify_configuration_succeeded') is not False:
        raise ValueError('historical_wa_acceptance_changed')
    for pin in wa.get('native_captures', []):
        checked_pin(root, pin)
    if rows['898A'].get('holdout', {}).get('state') != 'NOT_EXECUTED':
        raise ValueError('saved_holdout_state_changed')
    cohort = rows['899A']
    if cohort.get('measured_windows') != 16 or cohort.get('failures'):
        raise ValueError('saved_aa_cohort_incomplete')
    checked_pin(root, cohort['frozen_plan'])
    plan = c.read_json(root, cohort['frozen_plan']['path'])
    for pin in plan['producer_source_bindings']:
        checked_pin(root, pin)
    replayed = [replay_window(root, wrapper) for wrapper in cohort['rows']]
    if len(replayed) != 16:
        raise ValueError('saved_window_count_changed')
    evaluation = gate900.adapter.evaluate_campaign(cohort['rows'], evidence_root=root,
        frozen_plan=plan, mode='AA_CONTROL', gate_options=dict(num_hypotheses_tested=1))
    evaluation = json.loads(json.dumps(evaluation, allow_nan=False))
    if evaluation != cohort['evaluation'] or evaluation != rows['900A']['measured_aa_gate']:
        raise ValueError('saved_gate_recomputation_mismatch')
    raw_gate = evaluation.get('raw_gate') or {}
    if raw_gate.get('verdict') != 'REJECT' or raw_gate.get('paired_blocks_count') != 0:
        raise ValueError('saved_safety_rejection_changed')
    helper = c.snapshot(root, HELPER)
    return dict(saved_windows_replayed=len(replayed),
        receiver_bytes=sum(x['receiver_bytes'] for x in replayed),
        packets_sent=sum(x['packets_sent'] for x in replayed),
        packets_received=sum(x['packets_received'] for x in replayed),
        captured_kit_sha256=HISTORICAL_KIT_SHA, current_helper_sha256=helper.get('sha256'),
        current_helper_matches_captured_kit=helper.get('sha256') == HISTORICAL_KIT_SHA,
        capture_kit_hash_rewritten=False, apply_executed=False, holdout_executed=False,
        saved_gate_verdict='REJECT', paired_statistics_reached=False,
        false_positive_calibration_accepted=False, hardware_gate_acceptance='NOT_ACCEPTED')


def validation(root: Path, path, sources: list[dict]) -> dict:
    if path is None:
        return dict(passed=False, reason='SOURCE_BOUND_LOCAL_TEST_VALIDATION_REQUIRED')
    label = Path(path).as_posix()
    record = c.read_json(root, label)
    tests = record.get('tests', {})
    if (type(tests.get('exit_code')) is not int or tests['exit_code'] != 0
            or type(tests.get('passed')) is not int or tests['passed'] <= 0
            or type(tests.get('failures')) is not int or tests['failures'] != 0
            or type(tests.get('errors')) is not int or tests['errors'] != 0):
        raise ValueError('local_validation_tests_not_passed')
    declared = record.get('source_bindings', [])
    by_path = {row['path']: row for row in declared}
    if len(by_path) != len(declared):
        raise ValueError('duplicate_validation_source')
    for source in sources:
        if source['path'] not in by_path:
            raise ValueError('validation_source_missing')
        checked_pin(root, by_path[source['path']])
    return dict(passed=True, tests=dict(tests), binding=c.snapshot(root, label))


def build(root: Path = ROOT, validation_path=None) -> dict:
    root = Path(root).resolve()
    sources = [c.snapshot(root, label) for label in SOURCE_LABELS]
    if not all(row['available'] for row in sources):
        raise ValueError('mandatory_current_source_missing')
    verified = validation(root, validation_path, sources)
    details = {'913A': stage913(root), '914A': stage914(root)}
    details['915A'] = dict(publication_status='QUALIFIED_LOCAL_CANDIDATE' if verified['passed'] else 'PENDING_VALIDATION',
        publication_executed=False, deployment_authorized=False,
        privacy_scope='Aggregated outcomes and source hashes only; no customer topology or raw capture contents',
        physical_acceptance='UNKNOWN', changed_helper_runtime_acceptance='UNKNOWN',
        saved_history_is_current_runtime_evidence=False)
    result = {}
    for stage, detail in details.items():
        number = int(stage[:-1])
        report = c.receipt(number, STEMS[stage].replace('_', ' '), sources)
        report.update(detail, software_compatibility='PASS' if verified['passed'] else 'UNKNOWN',
            evidence_provenance_class='CONFIRMED_STATIC_BINARY',
            provenance_scope='offline executable source verification; original live capture provenance retained separately',
            local_validation=verified, hardware_acceptance='NOT_ACCEPTED', fresh_live_windows=0,
            saved_capture_or_review_rewritten=False)
        body = ('This stage reconciles saved local evidence and current software contracts only.\n'
                'Historical pins retain their original scope. Drift is reported; old reviews do not validate changed bytes.\n'
                'The immutable captured-kit hash is compared to saved captures, independently of the current helper.\n'
                'Saved A/A replay and a safety rejection do not establish calibration, treatment, holdout or live acceptance.\n'
                'Local PASS requires explicit passing tests bound to every current mandatory source hash.\n'
                'No producer, device, network, publication or durable-memory write is performed.\n'
                'Physical acceptance and changed-helper runtime compatibility remain UNKNOWN; deployment remains unauthorized.\n')
        # Detect changes during reconciliation before replacing any receipt.
        if [c.snapshot(root, x['path']) for x in sources] != sources:
            raise ValueError('current_sources_changed_during_reconciliation')
        result[stage] = c.save(root, STEMS[stage], report, body)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validation', help='Repository-relative source-bound local test JSON')
    args = parser.parse_args(argv)
    result = build(validation_path=args.validation)
    print(json.dumps({stage: row['software_compatibility'] for stage, row in result.items()}))
    return 0 if all(x['software_compatibility'] == 'PASS' for x in result.values()) else 2


if __name__ == '__main__':
    raise SystemExit(main())
