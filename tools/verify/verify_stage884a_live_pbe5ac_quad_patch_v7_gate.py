# PUBLIC_REDACTED_DERIVATIVE; original_sha256=28438b101dd48dfa0e3358d07cc027b9f34551678604d08e1d51fb4e73e3ecd1
# Private originals are required for native replay.
"""Consolidated879..884 integrity and acceptance gate; no implicit live approval."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.autoresearch import stage861_866_common as c
from tools.verify.verify_stage866a_live_pbe5ac_ptp_v6_gate import verify_pin, record_bindings, doc_contract
OUT = ROOT / 'artifacts/autoresearch/stage884a_live_pbe5ac_quad_patch_v7_gate.json'
STEMS = {'879A': 'stage879a_verified_pb070_and_pb080_native_sgmt_binaries', '880A': 'stage880a_live_pbe5ac_verified_quad_patch_ota_bench', '881A': 'stage881a_live_rocket2ac_251_and_wa_coexistence_audit', '882A': 'stage882a_guarida_34endpoint_complete_readiness_audit', '883A': 'stage883a_pbe5ac_lbe5ac_verified_quad_patch_tester_kit_v7', '884A': 'stage884a_live_pbe5ac_quad_patch_v7_gate'}

def binding_state(root, binding):
    """Describe current bytes without rewriting the historical expected pin.

    A declared old hash is evidence of the review's scope, not proof that the
    original bytes are still available and not acceptance of changed source.
    """
    expected = dict(binding)
    path = (Path(root) / expected['path']).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError('historical_binding_outside_repository')
    current = None
    if path.is_file():
        blob = path.read_bytes()
        current = dict(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest())
    matched = bool(current and type(expected.get('bytes')) is int and (current['bytes'] == expected['bytes']) and (current['sha256'] == expected.get('sha256')))
    return dict(original_binding=expected, current_bytes=current, state='CURRENT_MATCH' if matched else 'CURRENT_DRIFT' if current else 'MISSING', current_binding_verified=matched, original_bytes_available_at_recorded_path=matched, historical_review_applies_to_current_bytes=matched, physical_acceptance='UNKNOWN')

def build(validation=None):
    checks, inputs, states, binding_inventory = ([], [], {}, [])
    for stage, stem in STEMS.items():
        doc = ROOT / 'docs' / f'{stem.upper()}.md'
        checks.append(dict(check='doc_' + stage, passed=doc.exists() and doc_contract(doc.read_text(encoding='utf-8'))))
        if stage == '884A':
            continue
        path = ROOT / 'artifacts/autoresearch' / f'{stem}.json'
        try:
            r = c.load(path)
            if r.get('stage') != stage:
                raise ValueError('wrong_stage')
        except (OSError, ValueError, AttributeError):
            states[stage] = 'MISSING_OR_INVALID'
            checks.append(dict(check=stage, passed=False))
            continue
        inputs.append(c.pin(path))
        states[stage] = r.get('status', 'UNKNOWN')
        checks.append(dict(check='implementation_present_' + stage, passed=isinstance(r.get('implementation'), dict)))
        for item in record_bindings(r):
            checks.append(dict(check=stage + ':' + item.get('path', 'MALFORMED'), passed=verify_pin(ROOT, item)))
            binding_inventory.append(binding_state(ROOT, item))
        if r.get('evidence'):
            checks.append(dict(check='capture_' + stage, passed=verify_pin(ROOT, r['evidence'])))
    review_path = ROOT / 'artifacts/verification/stage879a/independent_patch_spec_review.json'
    review = None
    if review_path.exists():
        review = c.pin(review_path)
        r = c.load(review_path)
        for item in r.get('reviewed_files', []):
            binding = dict(path=item['path'], sha256=item['sha256'], bytes=item.get('bytes', item.get('size_bytes')))
            checks.append(dict(check='independent_review:' + item['path'], passed=verify_pin(ROOT, binding)))
            binding_inventory.append(binding_state(ROOT, binding))
    else:
        checks.append(dict(check='independent_review', passed=False))
    return dict(schema_version=1, stage='884A', status='INCOMPLETE', acceptance='NOT_ACCEPTED', question='Are verified Quad/Penta, live direct OTA and a tested two-board v7 kit accepted?', implementation=c.pin(__file__), analysis_dependencies=[c.pin(c.__file__), c.pin(ROOT / 'tools/verify/verify_stage866a_live_pbe5ac_ptp_v6_gate.py')], source_bindings=inputs, local_integrity=checks, historical_binding_inventory=binding_inventory, local_integrity_passed=all((item['passed'] for item in checks)), stage_status=states, independent_review=review, local_validation=c.load(validation) if validation else None, blockers=['PB070_RC_SEMANTIC_CONTRACT_MISSING', 'PB080_QUEUE_TARGET_MISSING', 'NO_NATIVE_QUAD_PENTA_OR_12_WINDOW_TREATMENT', 'WA250_AUTHENTICATION_AND_34_ENDPOINT_RUNTIME_GAPS', 'NO_QUAD_TESTED_PBE_LBE_V7_KIT'], target_writes=False, quad_emitted=False, penta_emitted=False, live_benchmark_executed=False, v7_flash_or_publish_approved=False, next_action='Operator clarifies PB070 behavior/PB080 target; map exact native sites and independently review before guarded RAM loading')

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validation', type=Path)
    args = parser.parse_args(argv)
    result = build(args.validation)
    c.write(OUT, result)
    print(json.dumps(dict(stage='884A', status=result['status'], local_integrity_passed=result['local_integrity_passed'], stage_status=result['stage_status'])))
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
