# PUBLIC_REDACTED_DERIVATIVE; original_sha256=b01f82c22a0d1da3161285feec25de9a73f8b00074d7843af8bc1782cf725b96
# Private originals are required for native replay.
"""Native WA prerequisites and real immutable-kit dry-run, without guard bypass."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.autoresearch import stage897_900_live_common as n
from tools.autoresearch.run_stage864a_guarida_panel2_panel3_airmagic_and_slot_audit import section
c = n.c
KIT = ROOT / 'firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh'
OUT = ROOT / 'artifacts/autoresearch/stage897a_live_wa_hardened_kit_verify.json'
KIT_SHA = 'df1501405609c5c1a6d89c6ee6a2b185519db40dcc512f0bb51f116aaaf3d485'

def native(row):
    text = row.get('stdout', '')
    board, rc = section(text, 'BOARD')
    try:
        board = json.loads(board) if rc == 0 else None
    except (ValueError, TypeError):
        board = None
    iw, iw_rc = section(text, 'IW')
    tc, tc_rc = section(text, 'TC_REQUESTED_ATH0')
    return dict(host=row['host'], transport_ok=row.get('exit_code') == 0 and (not row.get('timed_out')), board=board, board_revision_available=bool(board and board.get('board_revision')), radio_interfaces=re.findall('Interface (\\S+)', iw or '') if iw_rc == 0 else [], requested_ath0_tc_exit=tc_rc, requested_ath0_tc_stdout=tc, tc_available=bool(re.search('^/[^\\n]*/tc$', section(text, 'TOOLS')[0] or '', re.M)), error_type=row.get('error_type'))

def build(captures=None, dry_run=None, verify_probe=None):
    observations = []
    for binding in captures or []:
        if c.sha((ROOT / binding['path']).read_bytes()) != binding['sha256']:
            raise ValueError('native_capture_drift')
        observations.extend((native(row) for row in c.load(ROOT / binding['path']).get('results', []) if 'BOARD' in row.get('stdout', '') or row.get('exit_code') is None))
    return dict(schema_version=1, stage='897A', status='BLOCKED', acceptance='NOT_ACCEPTED', implementation=c.pin(__file__), analysis_dependencies=[c.pin(n.__file__), c.pin(c.__file__), c.pin(ROOT / 'tools/autoresearch/run_stage864a_guarida_panel2_panel3_airmagic_and_slot_audit.py')], source_bindings=[c.pin(KIT), c.pin(ROOT / 'artifacts/verification/stage897a/independent_kit_review.json')], requested_profile=dict(kind='fq_codel', quantum=1514, target_ms=5, interval_ms=100, flows=1024, ecn=True), actual_kit_profile=dict(kind='fq_codel', quantum=3028, target_ms=2.5, interval_ms=50, flows=1024, ecn='INHERITED'), native_captures=captures or [], observations=observations, native_dry_run=dry_run, native_verify_mode_probe=verify_probe, apply_executed=False, verify_configuration_succeeded=False, target_configuration_writes=False, blockers=['REQUESTED_PROFILE_DIFFERS_FROM_CANONICAL_V13', 'VERIFY_MODE_UNSUPPORTED', 'AP20_TC_NOT_INSTALLED_AND_ATH0_NOT_PRESENT', 'UBUS_BOARD_REVISION_UNAVAILABLE', 'NATIVE_AQL_TEXT_LABELS_NOT_ACCEPTED_BY_NUMERIC_ONLY_KIT_PARSER', 'STA195_TIMEOUT_STA251_ROOT_AUTH_FAILED_ROUTER250_ROSSSH'], topology_observed=dict(ap='198.18.0.43', router_rosssh='198.18.0.47', operator_sta_candidates=['198.18.0.42', '198.18.0.48'], openwrt_sta_verified=False), next_action='Resolve native STA identity/access and audited runtime profile compatibility; do not forge revision or apply a different qdisc profile')

def dry_run_live():
    blob = KIT.read_bytes()
    if c.sha(blob) != KIT_SHA:
        raise ValueError('reviewed_kit_source_drift')
    user, password = c.credential()
    rows = []
    for mode in ('--dry-run', '--verify'):
        command = 'sh -s -- ' + mode
        row = n.run('198.18.0.43', command, password=password, input_bytes=blob)
        rows.append((mode, n.save('897a', 'EXACT_KIT_' + mode[2:].upper().replace('-', '_'), [row], target_configuration_writes=False, source=c.pin(KIT))))
    return dict(rows)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run-live', action='store_true')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    captures = [c.pin(p) for p in sorted((ROOT / 'artifacts/verification/stage897a').glob('read_only_*.json')) if c.load(p).get('phase') in ('READ_ONLY_PREFLIGHT', 'OPERATOR_CORRECTED_STA_DISCOVERY', 'EXPLICIT_OPERATOR_CREDENTIAL_PREFLIGHT')]
    dry = dry_run_live() if args.dry_run_live else {}
    result = build(captures, dry.get('--dry-run'), dry.get('--verify'))
    c.write(OUT, result)
    print(json.dumps(dict(stage='897A', status='BLOCKED', dry_run=result['native_dry_run'], apply_executed=False)))
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
