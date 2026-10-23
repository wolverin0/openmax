"""Whitelist projections of pinned, completed PREPROD1 evidence; local only.

Default PLAN_ONLY. Raw files are never modified, followed as references, or
replaced. A projection cannot satisfy a raw runtime/precondition SHA binding.
"""
import argparse
import datetime
import hashlib
import json
import math
import re
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
BASE = PurePosixPath('artifacts/canary_panel1_guarida')
INVENTORY = BASE / 'preprod1_r5am_publication_inventory_review_20261023.json'
INVENTORY_SHA = '6c85a295a6fac4463e0f88b917943b1c603ecd24b2e3dce05c18685291800712'
OUTPUT = BASE / 'preprod1_public_evidence_20261023'
LABELS = {'fc:ec:da:c2:54:0a': 'WA', 'b4:fb:e4:5c:d5:d2': 'XC',
          '64:d1:54:1b:96:97': 'SXT', 'f0:9f:c2:b2:b6:ba': 'LBM5'}
EVENTS = frozenset(('FOUR_ADMITTED', 'STABLE_START', 'STABLE_DONE', 'STABLE_OK',
                    'DROP_REQUEST', 'DROP_OBSERVED', 'OLD_WDS_RETIRED', 'RECOVERED', 'COMPLETE'))
STATUSES = frozenset(('PASS', 'FAIL', 'INCOMPLETE', 'INCOMPLETE_FOUR_CPE_PRESERVED',
    'PASS_PREPROD1_AP_ONLY_ZERO_TOUCH_FOUR_CPE_MULTICYCLE_RESTORED',
    'PASS_EXACT_HASHES_RULES_BRIDGE_ORDERED_IPv4_ROUTES_GUARD_ENDED',
    'PASS_OPEN_RF_CONFIG_PROTECTED_HASHES_GUARD_ENDED',
    'DIAGNOSTIC_ONLY_XC_RECOVERY_CONFIRMED_ALL_RESTORED', 'PASS_RAM_WINDOW_RESTORED_RADIO_OFF',
    'PASS_AP_OBSERVER_RAM_WINDOW_ARMED', 'PASS_COMPAT_STOCK_RESTORED',
    'PASS_NO_COMPAT_REMOTE_RESOURCES_CREATED', 'PASS_RESTORED', 'RESTORED'))
GATES = frozenset(('RECOVERY_TIMEOUT', 'ADMISSION_TIMEOUT', 'NATIVE_NEGATIVE',
    'RUNTIMEERROR', 'TIMEOUTERROR', 'ASSERTIONERROR', 'INSUFFICIENT_REPLIES',
    'INSUFFICIENT_RADIO_PAIRS', 'INSUFFICIENT_TRANSMITTED', 'TRAFFIC_NOT_QUALIFIED'))
BOOLS = frozenset(('full_PREPROD1_PASS', 'diagnostic_only', 'forbidden_actions_executed',
    'persistent_config_writes', 'production_access_permitted', 'daemon_acceptance',
    'daemon_diagnostic_acceptance', 'daemon_RAM_files_removed', 'recovery_matrix_complete',
    'traffic_qualification_complete', 'multicycle_pass', 'diagnostic_acquisition_complete',
    'acquisition_complete', 'qualifying', 'qualified', 'accepted', 'complete', 'deltas_empty',
    'guard_ended_verified', 'RAM_guard_cleanup', 'stock_service_healthy', 'owned_mount_absent',
    'restored', 'restore_verified', 'cleanup_verified', 'radio_off', 'source_unchanged'))
HASHES = frozenset(('source_sha256', 'daemon_source_sha256', 'frozen_plan_sha256',
                   'review_sha256', 'intake_sha256', 'raw_receipt_sha256'))
NUMBERS = frozenset(('transmitted', 'received', 'paired', 'reply_timings', 'p95_ms',
                     'elapsed_seconds', 'duration_seconds', 'sample_count', 'exit_code'))
RESTORATIONS = ('AP_restoration', 'rocket_restoration', 'legacy_restoration', 'AP_compat_restoration')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def finite(value, minimum=0):
    return type(value) in (int, float) and math.isfinite(value) and minimum <= value <= 2**53


def token(value, allowed, fallback):
    if not isinstance(value, str):
        return fallback
    first = value.split(maxsplit=1)[0].rstrip(':').upper() if value.split() else ''
    return first if first in allowed else fallback


def artifact(value):
    """Metadata only; never follow any file or credential pointer."""
    if not isinstance(value, dict):
        return {}
    result = {}
    if re.fullmatch(r'[0-9a-fA-F]{64}', str(value.get('sha256', ''))):
        result['sha256'] = value['sha256'].lower()
    if type(value.get('bytes')) is int and finite(value['bytes']):
        result['bytes'] = value['bytes']
    return result


def safe_scalars(value):
    result = {}
    if not isinstance(value, dict):
        return result
    for key in BOOLS:
        if type(value.get(key)) is bool:
            result[key] = value[key]
    for key in NUMBERS:
        if key in value and finite(value[key], -255 if key == 'exit_code' else 0):
            result[key] = value[key]
    if 'status' in value:
        result['status'] = value['status'] if isinstance(value['status'], str) and value['status'] in STATUSES else 'UNRECOGNIZED_STATUS_WITHHELD'
    for key in ('gate', 'failure_gate', 'fail_gate', 'type'):
        if key in value:
            result[key] = token(value[key], GATES, 'UNRECOGNIZED_GATE_WITHHELD')
    if isinstance(value.get('cleanup_errors'), list):
        result['cleanup_error_count'] = len(value['cleanup_errors'])
    failures = value.get('failures')
    if isinstance(failures, list):
        result['failure_count'] = len(failures)
        result['failure_categories'] = [token(v, GATES, 'UNRECOGNIZED_GATE_WITHHELD') for v in failures]
    return result


def actions(text):
    result = []
    if not isinstance(text, str):
        return result
    for line in text.splitlines():
        fields = line.split()
        if len(fields) < 2 or fields[1] not in EVENTS or not re.fullmatch(r'\d+(?:\.\d+)?', fields[0]):
            continue
        when = float(fields[0])
        if not finite(when):
            continue
        row = dict(timestamp=when, event=fields[1])
        invalid = False
        for field in fields[2:]:
            key, sep, value = field.partition('=')
            if sep and key in ('epoch', 'n'):
                dest = 'drop_n' if key == 'n' else key
                if not re.fullmatch(r'\d{1,4}', value) or dest in row:
                    invalid = True
                    break
                row[dest] = int(value)
            elif sep and key == 'target':
                label = LABELS.get(value.lower())
                if not label or 'target_label' in row:
                    invalid = True
                    break
                row['target_label'] = label
        if not invalid:
            result.append(row)
    return result


def projection(raw, relative, digest):
    result = dict(schema='preprod1-safe-public-projection-v1', raw_relative_path=relative,
                  raw_sha256=digest, raw_bytes=len(raw), raw_withheld=True,
                  byte_identical_to_raw=False, runtime_precondition_replacement=False)
    if not relative.endswith('.json'):
        result['content_policy'] = 'PROVENANCE_ONLY_NON_JSON_CONTENT_WITHHELD'
        return result
    value = json.loads(raw)
    if not isinstance(value, dict):
        result['status'] = 'UNKNOWN_JSON_CONTENT_WITHHELD'
        return result
    if value.get('experiment') != 'PREPROD1_FMX0017_ZERO_TOUCH_RECOVERY' and 'actions.log' not in value:
        status = value.get('status')
        result['status'] = status if isinstance(status, str) and status in STATUSES else 'UNKNOWN_JSON_CONTENT_WITHHELD'
        return result
    result.update(safe_scalars(value))
    if value.get('experiment') == 'PREPROD1_FMX0017_ZERO_TOUCH_RECOVERY':
        result['experiment'] = value['experiment']
    for key in HASHES:
        v = value.get(key)
        if isinstance(v, str) and re.fullmatch(r'[0-9a-fA-F]{64}', v):
            result[key] = v.lower()
    for key in ('utc', 'started_utc', 'ended_utc'):
        v = value.get(key)
        if isinstance(v, str) and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?(?:Z|[+-]\d\d:\d\d)', v):
            try:
                datetime.datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                continue
            result[key] = v
    traffic = value.get('epoch_traffic')
    if isinstance(traffic, dict):
        epochs = {}
        for epoch, peers in traffic.items():
            if not re.fullmatch(r'\d{1,4}', str(epoch)) or not isinstance(peers, dict):
                continue
            rows = {}
            for label in LABELS.values():
                peer = peers.get(label)
                if isinstance(peer, dict):
                    rows[label] = safe_scalars(peer)
                    meta = artifact(peer.get('artifact'))
                    if meta:
                        rows[label]['artifact'] = meta
            if rows:
                epochs[str(int(epoch))] = rows
        if epochs:
            result['epoch_traffic'] = epochs
    resets = value.get('verified_session_resets')
    if isinstance(resets, list):
        result['verified_session_resets'] = [int(v) for v in resets
            if type(v) is int and 0 <= v <= 9999 or isinstance(v, str) and re.fullmatch(r'\d{1,4}', v)]
    for key in RESTORATIONS:
        v = value.get(key)
        if not isinstance(v, dict):
            continue
        safe = safe_scalars(v)
        # A fixed target-label map, not arbitrary nested field names.
        for label in LABELS.values():
            if isinstance(v.get(label), dict):
                safe[label] = safe_scalars(v[label])
        result[key] = safe
    if 'actions.log' in value:
        result['native_actions'] = actions(value['actions.log'])
    for key, dest in (('restore.rc', 'native_restore_exit'), ('exit.rc', 'native_exit')):
        v = value.get(key)
        if isinstance(v, str) and re.fullmatch(r'-?\d{1,3}\s*', v):
            result[dest] = int(v)
    if not any(k in result for k in ('status', 'native_exit', 'epoch_traffic', 'native_actions')):
        result['status'] = 'UNKNOWN_JSON_CONTENT_WITHHELD'
    return result


def selected(inventory):
    rows = inventory['foreign_probe_raw_projection_required'] + inventory['non_JSON_raw_projection_required']
    mutable = str(BASE / 'preprod1_bench_result_20261022.json')
    return [row for row in rows if row['file'] != mutable and not any(
        part in ('preprod1_20261022_run5am', 'preprod1_20261022_run5an') for part in PurePosixPath(row['file']).parts)]


def generate(root, inventory_path, output, expected_inventory_sha=INVENTORY_SHA):
    root, inventory_path, output = Path(root).resolve(), Path(inventory_path), Path(output)
    raw_inventory = inventory_path.read_bytes()
    if sha(raw_inventory) != expected_inventory_sha:
        raise ValueError('INVENTORY_SHA_MISMATCH')
    inventory = json.loads(raw_inventory)
    rows = selected(inventory)
    if not output.resolve().is_relative_to(root / Path(BASE)) or not output.name.startswith('preprod1_public_evidence'):
        raise ValueError('OUTPUT_SCOPE')
    output.mkdir(mode=0o700, exist_ok=False)
    index = dict(schema='preprod1-public-projection-index-v1', status='INCOMPLETE',
                 inventory_sha256=expected_inventory_sha, projections=[], unresolved=[],
                 raw_originals_modified=False, physical_or_publication_acceptance=False)
    for row in rows:
        rel = PurePosixPath(row['file'])
        if '..' in rel.parts or not str(rel).startswith(str(BASE) + '/preprod1'):
            raise ValueError('RAW_PATH_SCOPE')
        path = root / Path(rel)
        if not path.resolve().is_relative_to(root) or any(p.is_symlink() or p.is_junction() for p in [path, *path.parents] if p != root):
            raise ValueError('RAW_PATH_LINK')
        try:
            raw = path.read_bytes()
            if sha(raw) != row['sha256']:
                index['unresolved'].append(dict(raw_relative_path=str(rel), reason='RAW_SHA_MISMATCH',
                                                expected_sha256=row['sha256'], observed_sha256=sha(raw)))
                continue
            safe = projection(raw, str(rel), row['sha256'])
        except (OSError, ValueError, TypeError):
            index['unresolved'].append(dict(raw_relative_path=str(rel), reason='READ_OR_JSON_FAILED'))
            continue
        dest = output / Path(rel.relative_to(BASE)).with_suffix('.public.json')
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = (json.dumps(safe, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()
        with dest.open('xb') as stream:
            stream.write(data)
        index['projections'].append(dict(raw_relative_path=str(rel), raw_sha256=row['sha256'], raw_bytes=len(raw),
                                        projection_relative_path=dest.relative_to(root).as_posix(),
                                        projection_sha256=sha(data), projection_bytes=len(data)))
    index.update(status='GENERATED_SAFE_PROJECTIONS_REVIEW_PENDING' if not index['unresolved'] else 'INCOMPLETE_UNRESOLVED_RAW_FILES',
                 projected_count=len(index['projections']), unresolved_count=len(index['unresolved']))
    (output / 'index.json').write_text(json.dumps(index, indent=2, sort_keys=True) + '\n', encoding='utf8')
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-local', action='store_true')
    args = parser.parse_args()
    if not args.generate_local:
        print(json.dumps(dict(status='PLAN_ONLY', inventory_sha256=INVENTORY_SHA,
                              output=OUTPUT.as_posix(), raw_mutation=False)))
        return 0
    result = generate(ROOT, ROOT / Path(INVENTORY), ROOT / Path(OUTPUT))
    print(json.dumps(dict(status=result['status'], projected_count=result['projected_count'],
                          unresolved_count=result['unresolved_count'])))
    return int(bool(result['unresolved']))


if __name__ == '__main__':
    raise SystemExit(main())
