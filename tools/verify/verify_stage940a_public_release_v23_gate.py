#!/usr/bin/env python3
"""Source-bound v23 release checks; no target access and no publication side effects."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.stage779_822_offline_common import (atomic_write, local, read_json,
                                                     receipt, save, snapshot)
from tools.verify.enforce_5pillar_research_gate import (audit_repo_deterministic_gates,
                                                      audit_stage_receipt_5pillars)

STEM = 'stage940a_public_release_v23_gate'
SELF = 'tools/verify/' + Path(__file__).name
STEMS = {
    935: 'stage935a_pbe_ltu_fail_closed_kits',
    936: 'stage936a_pbe_ltu_adversarial_test_evidence',
    937: 'stage937a_v23_active_source_sha256_manifests',
    938: 'stage938a_905_to_934_verified_saved_measurements',
    939: 'stage939a_public_v23_evidence_documentation_sync',
}
TESTS = ['tests/test_chatgpt_audit_pbe_and_ltu_kits.py',
         'tests/test_stage937a_to_939a_evidence.py',
         'tests/test_stage940_public_shell_hygiene.py',
         'tests/test_stage935a_to_940a_suite.py']
KIT_ROOTS = ('firmware/openwrt/pbe5ac_gen2_ptp_kit', 'firmware/ltu_safe_kit')
CLASS = 'CONFIRMED_STATIC_BINARY'


def artifact(stage: int) -> str:
    return f'artifacts/autoresearch/{STEMS[stage]}.json'


def historical_archive(label: str) -> bool:
    for prefix in KIT_ROOTS:
        if label.startswith(prefix + '/'):
            first = label[len(prefix) + 1:].split('/')[0]
            return first.startswith('public_release') or first == 'public_assets'
    return False


def document_contract(text: str) -> bool:
    return (len(text.splitlines()) < 180 and text.startswith('<!-- doc-head:')
            and text.count('<!-- doc-head:') == 1 and text.count('<!-- /doc-head -->') == 1)


def binding_matches(root: Path, source: dict, *, public: bool = False,
                    withheld_paths: set[str] | None = None) -> str:
    """Public v23 omits immutable historical archives, never substitutes their hashes."""
    if (not isinstance(source, dict) or not isinstance(source.get('path'), str)
            or source.get('available') is not True or type(source.get('bytes')) is not int
            or source['bytes'] < 0 or not re.fullmatch('[0-9a-f]{64}', str(source.get('sha256')))):
        raise ValueError('invalid source binding')
    path = local(root, source['path'])
    if not path.is_file():
        if public and historical_archive(source['path']) and source['path'] in (withheld_paths or set()):
            return 'WITHHELD_HISTORICAL_ARCHIVE'
        raise ValueError('missing source: ' + source['path'])
    lexical = root / source['path']
    for node in (lexical, *lexical.parents):
        if node == root:
            break
        if node.is_symlink() or getattr(node, 'is_junction', lambda: False)():
            raise ValueError('indirect source path: ' + source['path'])
    current = snapshot(root, source['path'])
    if current['sha256'] != source['sha256'] or current['bytes'] != source['bytes']:
        raise ValueError('source drift: ' + source['path'])
    return 'VERIFIED_CURRENT_BYTES'


def measurement_evidence_errors(root: Path, data: dict, *, public: bool) -> list[str]:
    """Public schemas retain declarations; local acceptance replays private raw chains."""
    errors = []
    rows, inputs = data.get('rows'), data.get('private_input_bindings')
    verified, missing = data.get('verified_native_stages'), data.get('missing_stages')
    expected = [f'{n}A' for n in range(905, 935)]
    if (not isinstance(rows, list) or [row.get('stage') for row in rows] != expected
            or not isinstance(inputs, list) or not isinstance(verified, list)
            or not isinstance(missing, list) or data.get('stage_range') != '905A..934A'):
        return ['complete 905A..934A measurement ledger declarations required']
    if type(data.get('available_stage_count')) is not int or data['available_stage_count'] != len(inputs):
        errors.append('measurement input count mismatch')
    by_stage = {}
    for pin in inputs:
        if not isinstance(pin, dict):
            errors.append('invalid original measurement binding'); continue
        match = re.fullmatch(r'artifacts/autoresearch/stage(90[5-9]|9[12][0-9]|93[0-4])a[^/]*\.json',
                             str(pin.get('path', '')))
        if (not match or pin.get('available') is not True or type(pin.get('bytes')) is not int
                or pin['bytes'] < 0 or not re.fullmatch('[0-9a-f]{64}', str(pin.get('sha256')))):
            errors.append('invalid original measurement binding'); continue
        stage = match[1] + 'A'
        if stage in by_stage:
            errors.append('duplicate original measurement stage')
        by_stage[stage] = pin
    claimed = []
    for row in rows:
        if type(row.get('native_observation_verified')) is not bool:
            errors.append('explicit native observation result required')
        digest = row.get('receipt_sha256')
        if digest is not None and (row['stage'] not in by_stage or by_stage[row['stage']]['sha256'] != digest):
            errors.append('measurement row has no matching original input binding')
        if row.get('native_observation_verified') is True:
            claimed.append(row['stage'])
            if (not digest or row.get('source_class') != 'CONFIRMED_LIVE_HARDWARE'
                    or row.get('state') != 'SAVED_NATIVE_BYTES_AND_OBSERVATIONS_VERIFIED'
                    or not isinstance(row.get('observation'), dict) or not row['observation']):
                errors.append('native observation declaration lacks its receipt evidence')
    if verified != claimed or len(set(verified)) != len(verified):
        errors.append('verified native-stage inventory mismatch')
    if missing != [row['stage'] for row in rows if row.get('state') == 'MISSING']:
        errors.append('missing-stage inventory mismatch')
    if not public:
        from tools.observability.build_stage937a_to_939a_public_v23_evidence_and_manifests import evidence_ledger
        # This function is pure local replay; it never calls the acquisition runners.
        fresh = evidence_ledger(root)
        for key in ('rows', 'private_input_bindings', 'available_stage_count',
                    'missing_stages', 'verified_native_stages'):
            if fresh[key] != data.get(key):
                errors.append('private native-chain replay differs: ' + key)
    return errors


def audit_stage(root: Path, stage: int, *, public: bool = False) -> dict:
    failures, withheld = [], 0
    try:
        data = read_json(root, artifact(stage))
        withheld_paths = set()
        if public:
            inventory = data if stage == 935 else read_json(root, artifact(935))
            for archived in inventory.get('historical_archives', []):
                if (not historical_archive(archived['path'])
                        or archived.get('state') != 'LEGACY_ARCHIVE_NOT_RELEASED'
                        or archived.get('execution_allowed') is not False
                        or archived.get('release_membership') is not False):
                    raise ValueError('invalid historical archive declaration')
                if archived['path'] in withheld_paths:
                    raise ValueError('duplicate historical archive declaration')
                withheld_paths.add(archived['path'])
        if data.get('stage') != f'{stage}A' or data.get('status') != 'CONFIRMED':
            failures.append('stage identity or offline construction status')
        if data.get('evidence_provenance_class') != CLASS:
            failures.append('offline software provenance must not be promoted to live evidence')
        boundary = data.get('boundary', {})
        for key in ('network_access', 'ssh_executed', 'device_writes', 'flash_approved'):
            if boundary.get(key) is not False:
                failures.append('offline boundary: ' + key)
        if (boundary.get('physical_acceptance') != 'UNKNOWN'
                or data.get('physical_acceptance') != 'UNKNOWN'):
            failures.append('physical acceptance must remain UNKNOWN')
        if not audit_stage_receipt_5pillars(data)['compliant']:
            failures.append('five-pillar structural contract')
        sources = data.get('sources')
        if not isinstance(sources, list) or not sources:
            failures.append('source bindings required')
        else:
            labels = [source.get('path') for source in sources]
            if len(labels) != len(set(labels)):
                failures.append('duplicate source binding')
            for source in sources:
                try:
                    withheld += binding_matches(root, source, public=public,
                                                withheld_paths=withheld_paths) == 'WITHHELD_HISTORICAL_ARCHIVE'
                except (OSError, ValueError, TypeError, KeyError) as exc:
                    failures.append(str(exc))
        text = local(root, f'docs/{STEMS[stage].upper()}.md').read_text(encoding='utf-8')
        if not document_contract(text):
            failures.append('document budget/header')
        if stage == 936:
            counts = data.get('tests', {})
            if (data.get('all_gates_passed') is not True
                    or data.get('tested_revision_unchanged') is not True
                    or counts.get('all_passed') is not True
                    or type(counts.get('returncode')) is not int or counts['returncode'] != 0
                    or type(counts.get('passed')) is not int or counts['passed'] <= 0
                    or any(type(counts.get(k)) is not int or counts[k] != 0
                           for k in ('failures', 'errors', 'skipped'))):
                failures.append('executed adversarial acceptance required')
        if stage == 938:
            failures.extend(measurement_evidence_errors(root, data, public=public))
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        failures.append(type(exc).__name__ + ': ' + str(exc))
    return {'stage': f'{stage}A', 'compliant': not failures, 'failures': failures,
            'withheld_historical_archives': withheld}


def validate_checksums(root: Path, descriptor: dict) -> set[str]:
    binding_matches(root, descriptor)
    members = descriptor.get('members')
    if not isinstance(members, list) or not members:
        raise ValueError('checksum members required')
    labels = [member['path'] for member in members]
    if len(set(labels)) != len(labels) or any(historical_archive(label) for label in labels):
        raise ValueError('duplicate or archived checksum member')
    for source in members:
        binding_matches(root, source)
    parent = Path(descriptor['path']).parent.as_posix()
    expected = {}
    for source in members:
        prefix = parent + '/'
        if not source['path'].startswith(prefix):
            raise ValueError('checksum member outside kit')
        expected[source['path'][len(prefix):]] = source['sha256']
    actual = {}
    text = local(root, descriptor['path']).read_text(encoding='ascii')
    for line in text.splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if not match or match[2] in actual:
            raise ValueError('malformed or duplicate SHA256SUMS row')
        local(root, parent + '/' + match[2])
        actual[match[2]] = match[1]
    if actual != expected:
        raise ValueError('checksum membership or content mismatch')
    return set(labels)


def audit_release(root: Path = ROOT, *, public: bool = False) -> dict:
    root = Path(root).resolve()
    rows = [audit_stage(root, n, public=public) for n in STEMS]
    failures = []
    try:
        kit = read_json(root, artifact(935))
        members = kit['release_source_members']
        if (not isinstance(members, list) or not members or len(set(members)) != len(members)
                or any(historical_archive(label) for label in members)
                or kit.get('native_engines') != 2 or kit.get('source_only_release') is not True
                or type(kit.get('active_entrypoints')) is not int or kit['active_entrypoints'] != len(members)
                or type(kit.get('retired_legacy_entrypoints')) is not int
                or kit['retired_legacy_entrypoints'] != len(members) - 2
                or kit.get('runtime_compatibility') != 'UNKNOWN'):
            failures.append('active source-only membership contract')
        for archive in kit.get('historical_archives', []):
            if (not historical_archive(archive['path']) or archive.get('execution_allowed') is not False
                    or archive.get('release_membership') is not False
                    or archive.get('state') != 'LEGACY_ARCHIVE_NOT_RELEASED'):
                failures.append('historical archive must remain excluded and non-executable')
        manifests = read_json(root, artifact(937))['checksum_manifests']
        if not isinstance(manifests, list) or len(manifests) != 2:
            raise ValueError('two exact kit checksum manifests required')
        combined = set()
        for descriptor in manifests:
            group = validate_checksums(root, descriptor)
            if combined.intersection(group):
                raise ValueError('checksum manifests overlap')
            combined.update(group)
        if combined != set(members):
            failures.append('active inventory and SHA256SUMS disagree')
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        failures.append(type(exc).__name__ + ': ' + str(exc))
    for label in ('README.md', 'docs/PUBLIC_OVERVIEW.md'):
        try:
            if not document_contract(local(root, label).read_text(encoding='utf-8')):
                failures.append('public reading-route document contract: ' + label)
        except OSError:
            failures.append('public reading-route document missing: ' + label)
    return {'compliant': all(row['compliant'] for row in rows) and not failures,
            'stage_audits': rows, 'release_failures': failures,
            'physical_acceptance': 'UNKNOWN',
            'public_native_measurement_replay': 'NOT_EXECUTED' if public else 'SEPARATE_PRIVATE_EVIDENCE_CHECK',
            'claim_scope': 'v23 offline software/source release, not native deployment acceptance'}


def pytest_summary(path: Path, returncode: int) -> dict:
    try:
        cases = ET.parse(path).findall('.//testcase') if path.is_file() else []
    except ET.ParseError:
        cases = []
    counts = {key: sum(case.find(tag) is not None for case in cases)
              for key, tag in [('failures', 'failure'), ('errors', 'error'), ('skipped', 'skipped')]}
    return {'returncode': returncode, 'tests': len(cases), **counts,
            'all_passed': returncode == 0 and bool(cases) and not any(counts.values())}


def run_tests(root: Path, logs: Path, name: str) -> dict:
    xml = logs / (name + '.xml')
    proc = subprocess.run([sys.executable, '-m', 'pytest', *TESTS, '-q',
                           '--junitxml=' + str(xml)], cwd=root, capture_output=True,
                          text=True, timeout=1200)
    atomic_write(logs / (name + '.stdout'), proc.stdout)
    atomic_write(logs / (name + '.stderr'), proc.stderr)
    return pytest_summary(xml, proc.returncode)


def index_hygiene(root: Path, logs: Path) -> tuple[dict, list[dict]]:
    from tools.verify.verify_stage826a_public_git_hygiene_and_push_gate import audit
    gitdir = Path(subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'],
                                         cwd=root, text=True).strip())
    policy = gitdir / 'stage826a/private_terms.json'
    terms = json.loads(policy.read_text(encoding='utf-8')) if policy.is_file() else []
    result, selected, findings = audit(root, private_terms=terms)
    atomic_write(logs / 'index_audit.json', json.dumps({'result': result, 'findings': findings}, indent=2))
    return result, selected


def check_export(root: Path, public_root: Path, selected: list[dict]) -> dict:
    public_root = Path(public_root).resolve()
    if public_root == root.resolve() or str(public_root).startswith('\\\\'):
        raise ValueError('a separate local public checkout is required')
    changed = [source['path'] for source in selected
               if snapshot(public_root, source['path']).get('sha256') != source['sha256']]
    status = subprocess.run(['git', 'status', '--porcelain=v1', '--untracked-files=normal'],
                            cwd=public_root, capture_output=True, text=True)
    top = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=public_root,
                         capture_output=True, text=True)
    entries = subprocess.run(['git', 'ls-files', '--stage', '-z'], cwd=public_root, capture_output=True)
    tracked, regular = set(), entries.returncode == 0
    if entries.returncode == 0:
        for entry in entries.stdout.split(b'\0'):
            if not entry:
                continue
            metadata, label = entry.split(b'\t', 1)
            mode, _, stage = metadata.split()
            tracked.add(label.decode('utf-8'))
            regular = regular and mode in (b'100644', b'100755') and stage == b'0'
    expected = {source['path'] for source in selected}
    # Ignored executable sources can still shadow imports; only ordinary test caches are excluded.
    extras = []
    for path in public_root.rglob('*'):
        relative = path.relative_to(public_root)
        if ('.git' in relative.parts or '.pytest_cache' in relative.parts
                or '__pycache__' in relative.parts):
            continue
        if path.is_file() and relative.as_posix() not in expected:
            extras.append(relative.as_posix())
    clean = (status.returncode == 0 and not status.stdout.strip() and top.returncode == 0
             and Path(top.stdout.strip()).resolve() == public_root)
    membership = regular and tracked == expected and not extras
    return {'compliant': not changed and clean and membership, 'clean_git_checkout': clean,
            'actual_index_blobs_match': not changed, 'mismatching_path_count': len(changed),
            'exact_index_membership': membership, 'extra_file_count': len(extras),
            'tracked_membership_difference_count': len(tracked.symmetric_difference(expected)),
            'regular_tracked_modes': regular}


def index_revision(root: Path) -> str:
    raw = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=root)
    return hashlib.sha256(raw).hexdigest()


def build(root: Path = ROOT, public_root: Path | None = None) -> dict:
    root = Path(root).resolve()
    gitdir = Path(subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'], cwd=root,
                                         text=True).strip())
    logs = gitdir / 'stage935_940'
    logs.mkdir(parents=True, exist_ok=True)
    local_audit = audit_release(root)
    repository = audit_repo_deterministic_gates(root)
    original_index = index_revision(root)
    private_inputs = read_json(root, artifact(938)).get('private_input_bindings', [])
    labels = {SELF, *TESTS, 'tools/verify/stage779_822_offline_common.py',
              'tools/verify/verify_stage826a_public_git_hygiene_and_push_gate.py',
              'tools/verify/enforce_5pillar_research_gate.py', 'README.md', 'docs/PUBLIC_OVERVIEW.md'}
    labels.update(artifact(n) for n in STEMS)
    labels.update(f'docs/{STEMS[n].upper()}.md' for n in STEMS)
    for stage in STEMS:
        try:
            labels.update(source['path'] for source in read_json(root, artifact(stage))['sources']
                          if not historical_archive(source['path']))
        except (OSError, ValueError, KeyError, TypeError):
            pass  # The explicit failed audit above prevents release acceptance.
    pins = [snapshot(root, label) for label in sorted(labels)]
    hygiene, selected = index_hygiene(root, logs)
    local_tests = run_tests(root, logs, 'stage940_local') if local_audit['compliant'] else {
        'returncode': None, 'tests': 0, 'all_passed': False, 'reason': 'PREREQUISITES_FAILED'}
    public_audit = {'compliant': False, 'reason': 'PUBLIC_CHECKOUT_REQUIRED'}
    public_export = {'compliant': False, 'reason': 'PUBLIC_CHECKOUT_REQUIRED'}
    public_tests = {'returncode': None, 'tests': 0, 'all_passed': False, 'reason': 'PUBLIC_CHECKOUT_REQUIRED'}
    if public_root is not None:
        public_root = Path(public_root).resolve()
        public_export = check_export(root, public_root, selected)
        public_audit = audit_release(public_root, public=True)
        if public_export['compliant'] and public_audit['compliant']:
            public_tests = run_tests(public_root, logs, 'stage940_public')
            public_export = check_export(root, public_root, selected)
    unchanged = all(snapshot(root, source['path']) == source for source in pins)
    private_unchanged = True
    for source in private_inputs:
        try:
            binding_matches(root, source)
        except (OSError, ValueError, TypeError, KeyError):
            private_unchanged = False
    index_unchanged = index_revision(root) == original_index
    measurement_unchanged = not measurement_evidence_errors(root, read_json(root, artifact(938)), public=False)
    passed = (local_audit['compliant'] and local_tests['all_passed'] and hygiene['compliant']
              and public_audit['compliant'] and public_export['compliant']
              and public_tests['all_passed'] and unchanged and repository['compliant']
              and index_unchanged and private_unchanged and measurement_unchanged
              and all(source['available'] for source in pins))
    data = receipt(940, 'Public v23 source-release gate', pins)
    data.update(status='CONFIRMED' if passed else 'FAILED', all_gates_passed=passed,
                evidence_provenance_class=CLASS,
                provenance_detail='Executable-source inspection and command-stub software tests only',
                local_release_audit=local_audit, public_release_audit=public_audit,
                repository_gate=repository,
                local_tests=local_tests, public_tests=public_tests, public_export=public_export,
                index_hygiene={'compliant': hygiene['compliant'], 'findings': hygiene['findings_by_rule']},
                tested_revision_unchanged=unchanged, verification_sources=pins,
                tested_index_revision=original_index, index_revision_unchanged=index_unchanged,
                private_original_inputs_unchanged=private_unchanged,
                private_native_chain_replay_unchanged=measurement_unchanged,
                physical_acceptance='UNKNOWN', fresh_live_windows=0,
                publication_executed=False, deployment_authorized=False,
                private_original_replay='SEPARATE_916A_EVIDENCE_NOT_PUBLICLY_RECREATED')
    return save(root, STEM, data,
                f"Offline v23 release gate: {'PASS' if passed else 'FAIL'}.\n\n"
                f"Local focused pytest: {local_tests['tests']} tests; return code {local_tests['returncode']}.\n"
                f"Clean public focused pytest: {public_tests['tests']} tests; return code {public_tests['returncode']}.\n"
                'Receipts935A..939A, paired document headers, active source hashes and exact SHA256SUMS membership are checked.\n'
                '40 legacy actuators are explicitly retired;2 separately selected transient engines are tested with command stubs.\n'
                '103 immutable historical archives are excluded from v23 packaging, not rewritten or exercised.\n'
                'The public checkout must match every audited index blob and remain clean before and after tests.\n'
                'Sources are pinned before testing and checked afterwards; source drift rejects release acceptance.\n'
                'Actual index membership and private measurement inputs are frozen across both test executions.\n'
                'Static provenance does not certify native hardware, radio performance or all905A..934A campaigns.\n'
                'Historical measurements remain separately source-qualified; private original replay is not public replay.\n'
                'Five-pillar structural references preserve deferred external research and memory-ingestion boundaries.\n'
                'No SSH, flash, native device knob, firewall change, commit or push is executed by this gate.\n'
                'Coordinator publication requires a final staged-byte check and explicit remote hash verification.\n'
                'Physical acceptance: UNKNOWN.\n')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--public-root', type=Path,
                        help='Separate clean Git checkout exported from the actual publication index')
    args = parser.parse_args()
    data = build(args.root, args.public_root)
    print(json.dumps({key: data[key] for key in ('all_gates_passed', 'local_tests', 'public_tests',
                                                'public_export', 'tested_revision_unchanged')}, indent=2))
    return 0 if data['all_gates_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
