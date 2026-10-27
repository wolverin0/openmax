# PUBLIC_REDACTED_DERIVATIVE; original_sha256=a1a743ebc37955095cac730db5e8ef2ceb95ec573748baf8957cf43589a39ccd
# Private originals are required for native replay.
"""Stage866: consolidate real evidence without promoting blocked live stages."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.autoresearch import stage861_866_common as c
OUT = ROOT / 'artifacts/autoresearch/stage866a_live_pbe5ac_ptp_v6_gate.json'
RECEIPTS = {'861A': 'stage861a_live_pbe5ac_quad_patch_pb040_to_pb070_ota.json', '862A': 'stage862a_live_pbe5ac_ptp_champion_v6_counterbalanced.json', '863A': 'stage863a_live_pbe5ac_mk1_251_e2e_v6.json', '864A': 'stage864a_guarida_panel2_panel3_airmagic_and_slot_audit.json', '865A': 'stage865a_pbe5ac_lbe5ac_tester_release_package_v6.json'}
DOCS = {'861A': 'STAGE861A_LIVE_PBE5AC_QUAD_PATCH_PB040_TO_PB070_OTA.md', '862A': 'STAGE862A_LIVE_PBE5AC_PTP_CHAMPION_V6_COUNTERBALANCED.md', '863A': 'STAGE863A_LIVE_PBE5AC_MK1_251_E2E_V6.md', '864A': 'STAGE864A_GUARIDA_PANEL2_PANEL3_AIRMAGIC_AND_SLOT_AUDIT.md', '865A': 'STAGE865A_PBE5AC_LBE5AC_TESTER_RELEASE_PACKAGE_V6.md', '866A': 'STAGE866A_LIVE_PBE5AC_PTP_V6_GATE.md'}

def doc_contract(text):
    lines = text.splitlines()
    return 0 < len(lines) < 180 and lines[0].startswith('<!-- doc-head: ') and lines[0].endswith(' -->') and (text.count('<!-- doc-head') == 1) and (text.count('<!-- /doc-head -->') == 1) and ('<!-- /doc-head -->' in lines[1:8])

def verify_pin(root, binding):
    try:
        path = (root / binding['path']).resolve()
        if not path.is_relative_to(root.resolve()):
            return False
        data = path.read_bytes()
        return len(data) == binding['bytes'] and c.sha(data) == binding['sha256']
    except (OSError, KeyError, TypeError):
        return False

def record_bindings(record):
    result = list(record.get('source_bindings', [])) + list(record.get('analysis_dependencies', []))
    if record.get('implementation'):
        result.append(record['implementation'])
    result.extend(record.get('outputs', {}).values())
    for item in record.get('baseline_references', []):
        result.append(dict(path=item['source_path'], bytes=item['bytes'], sha256=item['sha256']))
    return result

def build(root=ROOT, validation=None):
    root = Path(root)
    records, integrity, blocked, bindings = ({}, [], [], [])
    for stage, filename in RECEIPTS.items():
        path = root / 'artifacts/autoresearch' / filename
        try:
            record = c.load(path)
            if record.get('stage') != stage:
                raise ValueError('wrong_stage')
        except (OSError, ValueError, AttributeError):
            integrity.append(dict(check='receipt_' + stage, passed=False))
            blocked.append(stage + ':MISSING_OR_INVALID_RECEIPT')
            continue
        records[stage] = record
        integrity.append(dict(check='implementation_present_' + stage, passed=isinstance(record.get('implementation'), dict)))
        bindings.append(dict(path=path.relative_to(root).as_posix(), bytes=path.stat().st_size, sha256=c.sha(path.read_bytes())))
        evidence = record.get('evidence')
        if evidence:
            integrity.append(dict(check='capture_' + stage, passed=verify_pin(root, evidence)))
        prerequisite = record.get('source_prerequisite')
        if prerequisite:
            integrity.append(dict(check='source_' + stage, passed=verify_pin(root, prerequisite['source'])))
        for binding in record_bindings(record):
            integrity.append(dict(check=stage + ':' + binding.get('path', 'MALFORMED'), passed=verify_pin(root, binding)))
        if record.get('status') not in ('ACCEPTED',):
            blocked.append(stage + ':' + str(record.get('status', 'UNKNOWN')))
    for stage, filename in DOCS.items():
        path = root / 'docs' / filename
        try:
            text = path.read_text(encoding='utf-8')
            passed = doc_contract(text)
        except OSError:
            passed = False
        integrity.append(dict(check='doc_' + stage, passed=passed))
    payload_review = root / 'artifacts/verification/stage861a/independent_payload_review.json'
    try:
        review = c.load(payload_review)
        review_summary = dict(verdict=review.get('verdict'), binding=dict(path=payload_review.relative_to(root).as_posix(), bytes=payload_review.stat().st_size, sha256=c.sha(payload_review.read_bytes())))
        for item in review.get('reviewed_files', []):
            binding = dict(path=item['path'], bytes=item['size_bytes'], sha256=item['sha256'])
            integrity.append(dict(check='payload_review:' + item['path'], passed=verify_pin(root, binding)))
    except (OSError, ValueError):
        review_summary = dict(verdict='MISSING')
        integrity.append(dict(check='independent_payload_review', passed=False))
    validation_record = None
    if validation is not None:
        validation_record = c.load(validation)
    return dict(schema_version=1, stage='866A', status='INCOMPLETE', acceptance='NOT_ACCEPTED', implementation=c.pin(__file__), analysis_dependencies=[c.pin(c.__file__)], question='Were861..865 physically executed and independently accepted?', source_bindings=bindings, local_integrity=integrity, local_integrity_passed=bool(integrity) and all((x['passed'] for x in integrity)), stage_status={stage: value['status'] for stage, value in records.items()}, blockers=blocked + ['NO_NATIVE_PB070_QUAD', 'NO_V5_V6_ABAB_OR_MK1_E2E_ACCEPTANCE', 'NO_TWO_BOARD_V6_RUNTIME_COMPATIBILITY'], independent_payload_review=review_summary, local_test_validation=validation_record, firmware_loaded=False, runtime_release_approved=False, target_writes=False, exact_next_action='Develop and independently verify native PB070, identify MK1 route, then resume guarded bench activation')

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validation', type=Path)
    args = parser.parse_args(argv)
    result = build(validation=args.validation)
    c.write(OUT, result)
    print(json.dumps(dict(stage='866A', status=result['status'], local_integrity_passed=result['local_integrity_passed'], stage_status=result['stage_status'])))
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
