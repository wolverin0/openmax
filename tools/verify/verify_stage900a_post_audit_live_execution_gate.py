# PUBLIC_REDACTED_DERIVATIVE; original_sha256=b6b964d1e5b88d243e726a34873f15e63455f35a61fa4c3abb4be462411fa906
# Private originals are required for native replay.
"""Post-audit live evidence gate. Local PASS never substitutes for missing apply/holdout."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.autoresearch import stage861_866_common as c
from tools.autoresearch import stage897_900_gate_adapter as adapter
from tools.autoresearch import run_stage899a_live_powerbeam_rocket_readonly_aa as s899
from tools.verify.verify_stage866a_live_pbe5ac_ptp_v6_gate import verify_pin, record_bindings, doc_contract
from workloads.flent_orchestrator import FlentWorkloadOrchestrator as FWO
OUT = ROOT / 'artifacts/autoresearch/stage900a_post_audit_live_execution_gate.json'
STEMS = {'897A': 'stage897a_live_wa_hardened_kit_verify', '898A': 'stage898a_live_wa_aa_and_holdout', '899A': 'stage899a_live_powerbeam_rocket_readonly_aa', '900A': 'stage900a_post_audit_live_execution_gate'}

def replay_window(wrapper):
    raw = wrapper['measurement']
    binding = raw['native_capture']
    if not verify_pin(ROOT, binding):
        raise ValueError('native_capture_sha_mismatch')
    native = c.load(ROOT / binding['path'])
    row = native['results'][0]
    if native.get('phase') != 'MEASURED_AA_WINDOW' or row.get('stdin_sha256') != c.sha(s899.WINDOW.encode()):
        raise ValueError('native_program_or_phase_mismatch')
    for key in ('arm', 'block_index', 'window_start_s', 'window_end_s', 'dataset_id'):
        if native[key] != raw[key]:
            raise ValueError('native_window_identity_mismatch')
    for config_binding in (native['prewindow_config'], raw['postwindow_config_capture']):
        if not verify_pin(ROOT, config_binding):
            raise ValueError('native_config_capture_sha_mismatch')
        cfg = c.load(ROOT / config_binding['path'])['results'][0]
        if s899.config_from_capture(cfg) != raw['config_readback']:
            raise ValueError('native_config_disagrees')
    regenerated = s899.normalize_window(row, raw['config_readback'], arm=raw['arm'], index=raw['block_index'], dataset=raw['dataset_id'], session=raw['session_id'], window_start=native['window_start_s'], window_end=native['window_end_s'], raw_pin=binding)
    if regenerated['acquisition'] != raw['acquisition'] or regenerated['firmware_resets'] != raw['firmware_resets']:
        raise ValueError('native_to_measurement_recomputation_mismatch')
    ping = FWO.parse_ping_output(row['stdout'])
    if (ping['sent'], ping['received'], ping['latencies_ms']) != (raw['acquisition']['packets_sent'], raw['acquisition']['packets_received'], raw['acquisition']['latencies_ms']):
        raise ValueError('hardened_flent_ping_parser_disagrees')
    pcts = FWO.calculate_percentiles(ping['latencies_ms'])
    prepared = adapter.prepare_measurement(raw, wrapper['receipt_path'])
    if prepared['sha256'] != wrapper['receipt_sha256']:
        raise ValueError('normalized_receipt_hash_disagrees')
    binding = dict(path=wrapper['receipt_path'], bytes=len(prepared['blob']), sha256=prepared['sha256'])
    if not verify_pin(ROOT, binding):
        raise ValueError('normalized_receipt_file_disagrees')
    return dict(run_id=raw['run_id'], receiver_bytes=raw['acquisition']['receiver_bytes'], packets_sent=ping['sent'], packets_received=ping['received'], p95_ms=pcts['p95'], p99_ms=pcts['p99'], native_recomputed=True, hardened_flent_parsed=True, normalized_binding=binding)

def build(validation=None):
    checks = []
    inputs = []
    records = {}
    replayed = []
    local_validation = c.load(validation) if validation else None
    if local_validation:
        for binding in record_bindings(local_validation):
            checks.append(dict(check='validation:' + binding['path'], passed=verify_pin(ROOT, binding)))
        tests = local_validation.get('tests', {})
        checks.append(dict(check='validation_pytest_exit_and_counts', passed=tests.get('exit_code') == 0 and tests.get('passed', 0) > 0 and (tests.get('failures') == 0) and (tests.get('errors') == 0)))
    for stage, stem in STEMS.items():
        doc = ROOT / 'docs' / f'{stem.upper()}.md'
        checks.append(dict(check='doc_' + stage, passed=doc.exists() and doc_contract(doc.read_text(encoding='utf-8'))))
        if stage == '900A':
            continue
        path = ROOT / 'artifacts/autoresearch' / f'{stem}.json'
        try:
            record = c.load(path)
            if record['stage'] != stage:
                raise ValueError('wrong_stage')
        except (OSError, ValueError, KeyError, TypeError):
            checks.append(dict(check='receipt_' + stage, passed=False))
            continue
        records[stage] = record
        inputs.append(c.pin(path))
        for binding in record_bindings(record):
            checks.append(dict(check=stage + ':' + binding['path'], passed=verify_pin(ROOT, binding)))
        for field in ('native_captures', 'readonly_preflight_bindings'):
            for binding in record.get(field, []):
                checks.append(dict(check=stage + ':' + binding['path'], passed=verify_pin(ROOT, binding)))
        for field in ('native_dry_run', 'native_verify_mode_probe'):
            binding = record.get(field)
            if binding:
                checks.append(dict(check=stage + ':' + field, passed=verify_pin(ROOT, binding)))
    evaluation = None
    if '899A' in records:
        record = records['899A']
        try:
            if not verify_pin(ROOT, record['frozen_plan']):
                raise ValueError('frozen_plan_sha_mismatch')
            plan = c.load(ROOT / record['frozen_plan']['path'])
            for binding in plan['producer_source_bindings']:
                if not verify_pin(ROOT, binding):
                    raise ValueError('producer_source_drift')
            for wrapper in record['rows']:
                replayed.append(replay_window(wrapper))
            evaluation = adapter.evaluate_campaign(record['rows'], evidence_root=ROOT, frozen_plan=plan, mode='AA_CONTROL', gate_options=dict(num_hypotheses_tested=1))
            evaluation = json.loads(json.dumps(evaluation, allow_nan=False))
            checks.append(dict(check='native_AA_and_gate_replay', passed=evaluation == record['evaluation']))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            checks.append(dict(check='native_AA_replay', passed=False, reason=str(exc)))
    health = []
    for path in sorted((ROOT / 'artifacts/verification/stage899a').glob('read_only_*.json')):
        capture = c.load(path)
        if capture.get('phase') != 'POST_COHORT_HEALTH_AND_CLEANUP':
            continue
        try:
            same = s899.config_from_capture(capture['results'][0]) == records['899A']['rows'][0]['measurement']['config_readback']
            clean = all((x.get('exit_code') == 0 and (not x.get('timed_out')) for x in capture['results']))
            for label in ('PRIVATE_TMP', 'OWN_PROCESSES'):
                value, rc = s899.section(capture['results'][1]['stdout'], label)
                clean = clean and rc == 0 and (value is not None) and (not value.strip())
            health.append(dict(binding=c.pin(path), configuration_unchanged=same, collector_clean=bool(clean)))
        except (ValueError, KeyError, TypeError, IndexError):
            health.append(dict(binding=c.pin(path), configuration_unchanged=False, collector_clean=False))
    checks.append(dict(check='post_cohort_health_and_cleanup', passed=bool(health) and all((x['configuration_unchanged'] and x['collector_clean'] for x in health))))
    acquisitions = [x['measurement']['acquisition'] for x in records.get('899A', {}).get('rows', [])]
    raw_gate = (evaluation or {}).get('raw_gate') or {}
    statistical_test_reached = raw_gate.get('paired_blocks_count', 0) > 0
    blockers = []
    wa = records.get('897A', {})
    campaign = records.get('898A', {})
    pbe = records.get('899A', {})
    if not wa.get('apply_executed') or not wa.get('verify_configuration_succeeded'):
        blockers.append('WA_APPLY_AND_REQUESTED_FQ_CODEL_VERIFY_NOT_EXECUTED')
    if campaign.get('holdout', {}).get('state') != 'EXECUTED':
        blockers.append('NO_DISJOINT_WA_AB_HOLDOUT')
    if pbe.get('measured_windows') != 16 or pbe.get('failures'):
        blockers.append('PBE_AA_COHORT_INCOMPLETE')
    if evaluation is None or evaluation.get('status') != 'EVALUATED':
        blockers.append('AA_DATA_OR_INFERENCE_NOT_VALIDATED')
    elif evaluation.get('control_result') == 'FAIL_FALSE_POSITIVE':
        blockers.append('MEASURED_AA_FALSE_POSITIVE_DETECTED')
    if not statistical_test_reached:
        blockers.append('AA_STATISTICAL_TEST_NOT_REACHED_SAFETY_REJECTION')
    blockers.extend(['FULL_QDISC_AND_EXCLUSIVE_OTA_ROUTE_COVERAGE_UNVERIFIED', 'NO_ROCKET_2_4GHZ_PEER_AA_COHORT'])
    return dict(stage='900A', schema_version=1, status='INCOMPLETE', acceptance='NOT_ACCEPTED', implementation=c.pin(__file__), analysis_dependencies=[c.pin(c.__file__), c.pin(s899.__file__), c.pin(ROOT / 'tools/verify/verify_stage866a_live_pbe5ac_ptp_v6_gate.py'), c.pin(ROOT / 'workloads/flent_orchestrator.py'), *adapter.source_bindings()], source_bindings=inputs, local_integrity=checks, local_integrity_passed=all((x['passed'] for x in checks)), stage_status={key: value['status'] for key, value in records.items()}, replayed_native_windows=replayed, measured_aa_gate=evaluation, blockers=blockers, post_cohort_health=health, measurement_summary=dict(windows=len(acquisitions), receiver_bytes=sum((x['receiver_bytes'] for x in acquisitions)), packets_sent=sum((x['packets_sent'] for x in acquisitions)), packets_received=sum((x['packets_received'] for x in acquisitions)), paired_statistical_test_reached=statistical_test_reached, raw_gate_statistics_interpretation='NOT_COMPUTED_AFTER_SAFETY_REJECT' if not statistical_test_reached else 'PAIRED_TEST_OUTPUT', false_positive_calibration_accepted=False), local_validation=local_validation, local_validation_binding=c.pin(validation) if validation else None, target_configuration_writes=False, deployment_authorized=False, next_action='Resolve actual WA STA access and audited native kit compatibility, then acquire separate new WA AA/discovery/holdout; do not relabel this baseline AA as kit acceptance')

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validation', type=Path)
    args = parser.parse_args(argv)
    r = build(args.validation)
    c.write(OUT, r)
    print(json.dumps(dict(stage='900A', status=r['status'], local_integrity_passed=r['local_integrity_passed'], replayed_windows=len(r['replayed_native_windows']))))
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
