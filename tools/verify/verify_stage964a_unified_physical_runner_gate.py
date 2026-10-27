#!/usr/bin/env python3
"""Source-bound offline verification of the959A..964A acquisition/inference bridge."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.stage779_822_offline_common import (atomic_write, local, read_json,
                                                     receipt, save, snapshot)
from tools.verify.enforce_5pillar_research_gate import (audit_repo_deterministic_gates,
                                                      audit_stage_receipt_5pillars)
from tools.verify.verify_stage940a_public_release_v23_gate import (
    binding_matches, document_contract, index_hygiene, index_revision, pytest_summary)

STEM = 'stage964a_unified_physical_runner_gate'
SELF = 'tools/verify/' + Path(__file__).name
RUNNER = 'tools/autoresearch/run_stage959a_unified_physical_retest_runner.py'
PHASES = ['AA_CONTROL', 'AB_DISCOVERY', 'AB_HOLDOUT']
CLASS = 'CONFIRMED_STATIC_BINARY'
STEMS = {
    959: 'stage959a_unified_physical_retest_runner',
    960: 'stage960a_pb030_031_unified_runner_migration',
    961: 'stage961a_pb032_033_unified_runner_migration',
    962: 'stage962a_pb050_051_unified_runner_migration',
    963: 'stage963a_pb053_054_unified_runner_migration',
}
CONTROLLERS = {
    960: 'controller/pb_030_031_phy_response_surface_harness.py',
    961: 'controller/pb_032_033_ratemask_sgi_solver.py',
    962: 'controller/pb_050_051_scheduler_timing_harness.py',
    963: 'controller/pb_053_054_hmac_epoch_controller.py',
}
TESTS = [
    'tests/test_stage959a_unified_physical_runner.py',
    'tests/test_stage960a_961a_unified_runner.py',
    'tests/test_stage962a_963a_unified_runner.py',
    'tests/test_pb_030_031_phy_response_surface_harness.py',
    'tests/test_pb_032_033_ratemask_sgi_solver.py',
    'tests/test_pb_050_051_scheduler_timing_harness.py',
    'tests/test_pb_053_054_hmac_epoch_controller.py',
    'tests/test_stage959a_to_964a_suite.py',
]
SHARED = {RUNNER, 'workloads/flent_orchestrator.py',
          'analysis/regression_gate/gatekeeper.py',
          'tools/autoresearch/stage897_900_gate_adapter.py'}


def artifact(stage: int) -> str:
    return f'artifacts/autoresearch/{STEMS[stage]}.json'


def audit_stage(root: Path, stage: int) -> dict:
    """Bind every software declaration to the current, ordinary source bytes."""
    errors = []
    try:
        data = read_json(root, artifact(stage))
        if data.get('stage') != f'{stage}A' or data.get('status') != 'CONFIRMED':
            errors.append('stage identity or construction status')
        if data.get('evidence_provenance_class') != CLASS:
            errors.append('software evidence cannot be promoted to physical provenance')
        boundary = data.get('boundary', {})
        if not isinstance(boundary, dict):
            raise ValueError('explicit boundary object required')
        for key in ('network_access', 'ssh_executed', 'device_writes', 'flash_approved'):
            if boundary.get(key) is not False:
                errors.append('offline boundary: ' + key)
        if (boundary.get('physical_acceptance') != 'UNKNOWN'
                or data.get('physical_acceptance') != 'UNKNOWN'):
            errors.append('physical acceptance must remain UNKNOWN')
        if not audit_stage_receipt_5pillars(data)['compliant']:
            errors.append('five-pillar structural references')
        sources = data.get('sources')
        if not isinstance(sources, list) or not sources:
            raise ValueError('nonempty source bindings required')
        labels = [row['path'] for row in sources]
        if len(set(labels)) != len(labels):
            errors.append('duplicate source binding')
        expected = set(SHARED)
        if stage in CONTROLLERS:
            expected.add(CONTROLLERS[stage])
        if not expected <= set(labels):
            errors.append('unified runner/controller/Flent/gate source binding incomplete')
        for source in sources:
            try:
                binding_matches(root, source)
            except (OSError, ValueError, TypeError, KeyError) as exc:
                errors.append(str(exc))
        if stage == 959:
            phases = data.get('required_phases')
            if (data.get('raw_window_sha256') is not True or data.get('gatekeeper_direct') is not True
                    or data.get('acquisition_default') != 'INSPECT_ONLY'
                    or data.get('live_campaign_executed') is not False
                    or data.get('deployment_authorized') is not False):
                errors.append('runner offline acquisition/inference contract')
        else:
            phases = data.get('mandatory_campaign_phases', data.get('required_campaign_phases'))
            if data.get('controller') != CONTROLLERS[stage]:
                errors.append('controller identity')
            if stage in (960, 961) and (data.get('holdout_boolean_shortcut') is not False
                    or data.get('inspection_invokes_acquisition') is not False
                    or data.get('actual_flent_and_gatekeeper_required') is not True):
                errors.append('controller physical inference contract')
            if stage in (962, 963) and (data.get('diagnostic_array_promotion_allowed') is not False
                    or data.get('historical_receipts_reaccepted') is not False):
                errors.append('legacy diagnostics cannot replace physical retesting')
        if phases != PHASES:
            errors.append('A/A, discovery and disjoint holdout are mandatory')
        text = local(root, f'docs/{STEMS[stage].upper()}.md').read_text(encoding='utf-8')
        if not document_contract(text):
            errors.append('document budget and paired initial header')
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        errors.append(type(exc).__name__ + ': ' + str(exc))
    return {'stage': f'{stage}A', 'compliant': not errors, 'failures': errors,
            'acceptance_scope': 'offline source and software contracts only'}


def audit_release(root: Path = ROOT) -> dict:
    rows = [audit_stage(Path(root).resolve(), n) for n in STEMS]
    return {'compliant': all(row['compliant'] for row in rows), 'stage_audits': rows,
            'physical_acceptance': 'UNKNOWN', 'fresh_live_windows': 0}


def index_entries(root: Path) -> dict[str, tuple[str, str]]:
    entries = {}
    raw = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=root)
    for part in raw.split(b'\0'):
        if not part:
            continue
        metadata, label = part.split(b'\t', 1)
        mode, oid, stage = metadata.split()
        if mode not in (b'100644', b'100755') or stage != b'0':
            raise ValueError('only unconflicted regular source files are releasable')
        entries[label.decode('utf-8')] = (mode.decode(), oid.decode())
    return entries


def check_export(root: Path, public_root: Path, selected: list[dict]) -> dict:
    """Exact Git membership, modes, object IDs and byte content, without hidden source."""
    public_root = Path(public_root).resolve()
    if public_root == root.resolve() or str(public_root).startswith('\\\\'):
        raise ValueError('separate local public checkout required')
    expected = index_entries(root)
    actual = index_entries(public_root)
    top = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=public_root,
                         capture_output=True, text=True)
    status = subprocess.run(['git', 'status', '--porcelain=v1', '--untracked-files=all'],
                            cwd=public_root, capture_output=True, text=True)
    clean = (top.returncode == 0 and Path(top.stdout.strip()).resolve() == public_root
             and status.returncode == 0 and not status.stdout.strip())
    mismatches = [row['path'] for row in selected
                  if snapshot(public_root, row['path']).get('sha256') != row['sha256']]
    extras = []
    for path in public_root.rglob('*'):
        relative = path.relative_to(public_root)
        if any(part in {'.git', '__pycache__', '.pytest_cache'} for part in relative.parts):
            continue
        if path.is_file() and relative.as_posix() not in expected:
            extras.append(relative.as_posix())
    return {'compliant': clean and expected == actual and not mismatches and not extras,
            'clean_git_checkout': clean, 'exact_index_membership_modes_and_objects': expected == actual,
            'actual_index_blobs_match': not mismatches, 'mismatch_count': len(mismatches),
            'extra_file_count': len(extras)}


def freeze_sources(root: Path) -> list[dict]:
    labels = {SELF, *TESTS, *SHARED, *CONTROLLERS.values(),
              'tools/verify/stage779_822_offline_common.py',
              'tools/verify/verify_stage940a_public_release_v23_gate.py',
              'tools/verify/verify_stage826a_public_git_hygiene_and_push_gate.py',
              'tools/verify/enforce_5pillar_research_gate.py'}
    for stage in STEMS:
        labels.update((artifact(stage), f'docs/{STEMS[stage].upper()}.md'))
        try:
            labels.update(source['path'] for source in read_json(root, artifact(stage))['sources'])
        except (OSError, ValueError, TypeError, KeyError):
            pass  # Prerequisite failures are reported explicitly by audit_release.
    return [snapshot(root, label) for label in sorted(labels)]


def pins_match_index(pins: list[dict], selected: list[dict]) -> dict:
    """Pre-existing staged bytes must be the same revision tested locally."""
    indexed = {row['path']: row for row in selected}
    mismatches = [row['path'] for row in pins if row.get('available') is not True
                  or row['path'] not in indexed
                  or indexed[row['path']].get('sha256') != row.get('sha256')
                  or indexed[row['path']].get('bytes') != row.get('bytes')]
    return {'compliant': bool(pins) and not mismatches,
            'mismatching_source_count': len(mismatches), 'mismatching_paths': mismatches}


def run_tests(root: Path, logs: Path, name: str) -> dict:
    path = logs / (name + '.xml')
    proc = subprocess.run([sys.executable, '-m', 'pytest', *TESTS, '-q',
                           '--junitxml=' + str(path)], cwd=root,
                          capture_output=True, text=True, timeout=1200)
    atomic_write(logs / (name + '.stdout'), proc.stdout)
    atomic_write(logs / (name + '.stderr'), proc.stderr)
    return pytest_summary(path, proc.returncode)


def build(root: Path = ROOT, public_root: Path | None = None) -> dict:
    root = Path(root).resolve()
    gitdir = Path(subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'], cwd=root,
                                         text=True).strip())
    logs = gitdir / 'stage959_964'
    logs.mkdir(parents=True, exist_ok=True)
    local_audit = audit_release(root)
    repository = audit_repo_deterministic_gates(root)
    before_index = index_revision(root)
    pins = freeze_sources(root)
    hygiene, selected = index_hygiene(root, logs)
    indexed_sources = pins_match_index(pins, selected)
    blocked = {'returncode': None, 'tests': 0, 'all_passed': False, 'reason': 'PREREQUISITES_FAILED'}
    prerequisites = local_audit['compliant'] and hygiene['compliant'] and indexed_sources['compliant']
    local_tests = run_tests(root, logs, 'stage964_local') if prerequisites else blocked
    public_audit = {'compliant': False, 'reason': 'PUBLIC_CHECKOUT_REQUIRED'}
    public_export = dict(public_audit)
    public_tests = {'returncode': None, 'tests': 0, 'all_passed': False,
                    'reason': 'PUBLIC_CHECKOUT_REQUIRED'}
    if public_root is not None:
        public_root = Path(public_root).resolve()
        public_export = check_export(root, public_root, selected)
        public_audit = audit_release(public_root)
        if prerequisites and public_export['compliant'] and public_audit['compliant']:
            public_tests = run_tests(public_root, logs, 'stage964_public')
            public_export = check_export(root, public_root, selected)
    unchanged = all(source.get('available') is True and snapshot(root, source['path']) == source
                    for source in pins)
    index_unchanged = index_revision(root) == before_index
    release_still_valid = audit_release(root)['compliant']
    passed = (local_audit['compliant'] and repository['compliant'] and hygiene['compliant']
              and local_tests['all_passed'] and public_audit['compliant']
              and public_export['compliant'] and public_tests['all_passed']
              and unchanged and index_unchanged and release_still_valid and indexed_sources['compliant'])
    data = receipt(964, 'Unified physical-retest runner offline source gate', pins)
    data.update(status='CONFIRMED' if passed else 'FAILED', all_gates_passed=passed,
                evidence_provenance_class=CLASS,
                provenance_scope='local synthetic/fault fixtures and source-byte validation only',
                local_release_audit=local_audit, public_release_audit=public_audit,
                repository_gate=repository, index_hygiene={'compliant': hygiene['compliant'],
                'findings': hygiene['findings_by_rule']},
                local_tests=local_tests, public_tests=public_tests, public_export=public_export,
                tested_revision_unchanged=unchanged, publication_index_unchanged=index_unchanged,
                indexed_tested_sources=indexed_sources,
                verification_sources=pins, physical_acceptance='UNKNOWN', fresh_live_windows=0,
                deployment_authorized=False, publication_executed=False)
    return save(root, STEM, data,
                f"Offline source release gate: {'PASS' if passed else 'FAIL'}.\n\n"
                f"Local focused pytest: {local_tests['tests']}; return code {local_tests['returncode']}.\n"
                f"Clean public focused pytest: {public_tests['tests']}; return code {public_tests['returncode']}.\n"
                'Source959A and controller migrations960A..963A are bound to actual current source bytes.\n'
                'The suite exercises actual hardened Flent parsing and the actual RegressionGatekeeper.\n'
                'A/A health, discovery, disjoint holdout, raw hashes and callback inspection defaults are mandatory.\n'
                'Synthetic captures and historical metric summaries cannot promote physical evidence.\n'
                'Before/after source hashes and the full actual Git index are frozen across both test runs.\n'
                'Frozen local source bytes must already match the staged blobs before pytest can run.\n'
                'The public checkout must match index membership, modes, object IDs and content and stay clean.\n'
                'Five-pillar checks are structural; external research and memory ingestion remain deferred.\n'
                'No physical campaign, SSH, device write, firmware activation, commit or push is executed here.\n'
                'Coordinator publication requires a separate final staged-byte and remote-commit check.\n'
                'Physical acceptance: UNKNOWN; deployment is not authorized.\n')


def write_prepared(root: Path = ROOT) -> dict:
    """Materialize truthful placeholders so the complete candidate can be exported."""
    data = receipt(964, 'Unified physical-retest runner offline source gate', [snapshot(root, SELF)])
    data.update(status='PREPARED', all_gates_passed=False,
                evidence_provenance_class=CLASS, physical_acceptance='UNKNOWN',
                local_tests={'all_passed': False, 'tests': 0, 'returncode': None},
                public_tests={'all_passed': False, 'tests': 0, 'returncode': None},
                reason='PENDING_COORDINATOR_COMPLETE_PUBLIC_CHECKOUT', deployment_authorized=False)
    return save(root, STEM, data,
                'PREPARED only. The complete source-bound local and public gate has not run.\n'
                'This placeholder makes no passing-test, physical or publication claim.\n'
                'The coordinator must supply a separate clean public Git checkout and run the gate.\n')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--public-root', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    data = write_prepared(args.root) if args.prepare_only else build(args.root, args.public_root)
    print(json.dumps({key: data[key] for key in (
        'status', 'all_gates_passed', 'local_tests', 'public_tests')}, indent=2))
    return 0 if args.prepare_only or data['all_gates_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
