#!/usr/bin/env python3
"""Execute offline WA stub tests and immutable saved-evidence replay only."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.stage779_822_offline_common import atomic_write, receipt, save, snapshot
from tools.firmware.build_stage911a_wa_tc_optional_field_kits import build as package_kits, HELPERS
from tools.verify.build_stage913a_to_915a_saved_evidence_reconciliation import (
    build as reconcile, SOURCE_LABELS)
from tools.verify.enforce_5pillar_research_gate import audit_repo_deterministic_gates

STEM = 'stage916a_wa_tcless_and_live_receipts_gate'
TESTS = ['tests/test_stage911a_to_916a_suite.py',
         'tests/test_stage879a_to_884a_suite.py', 'tests/test_stage897a_to_900a_suite.py',
         'tests/test_stage884a.py', 'tests/test_stage911_public_hygiene_python_expressions.py']
SELF = 'tools/verify/' + Path(__file__).name


def test_counts(path: Path, code: int) -> dict:
    cases = ET.parse(path).findall('.//testcase') if path.is_file() else []
    failures = sum(x.find('failure') is not None for x in cases)
    errors = sum(x.find('error') is not None for x in cases)
    skipped = sum(x.find('skipped') is not None for x in cases)
    return {'exit_code': code, 'passed': len(cases)-failures-errors-skipped,
            'failures': failures, 'errors': errors, 'skipped': skipped,
            'all_passed': code == 0 and bool(cases) and not (failures or errors or skipped)}


def checked_run(root: Path, command: list[str], stem: str, logs: Path) -> tuple[dict, dict]:
    xml = logs / (stem + '.xml')
    argv = [sys.executable, *command, '--junitxml=' + str(xml)]
    proc = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=1200)
    atomic_write(logs / (stem + '.stdout'), proc.stdout)
    atomic_write(logs / (stem + '.stderr'), proc.stderr)
    return test_counts(xml, proc.returncode), {'stdout': proc.stdout, 'stderr': proc.stderr}


def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    gitdir = Path(subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'],
                                         cwd=root, text=True).strip())
    logs = gitdir / 'stage911_916'
    logs.mkdir(parents=True, exist_ok=True)
    from tools.verify.verify_chatgpt_audit_1afaeb7 import CORE_TESTS
    labels = sorted(set(SOURCE_LABELS) | set(HELPERS) | set(TESTS) | set(CORE_TESTS) | {
        SELF, 'tools/firmware/build_stage911a_wa_tc_optional_field_kits.py',
        'tools/verify/verify_stage826a_public_git_hygiene_and_push_gate.py',
        'tools/verify/verify_chatgpt_audit_1afaeb7.py'})
    sources = [snapshot(root, p) for p in labels]
    if not all(row['available'] for row in sources):
        raise ValueError('required software or regression sources missing')
    # Pin before executing tests; a concurrent edit cannot inherit an earlier PASS.
    audit, _ = checked_run(root, ['tools/verify/verify_chatgpt_audit_1afaeb7.py'], 'audit_core', logs)
    local, _ = checked_run(root, ['-m', 'pytest', *TESTS, '-q'], 'native_and_historical', logs)
    unchanged = all(snapshot(root, row['path']) == row for row in sources)
    repository = audit_repo_deterministic_gates(root)
    passed = audit['all_passed'] and local['all_passed'] and unchanged and repository['compliant']
    validation = {'tests': {'exit_code': 0 if passed else 1,
                  'passed': audit['passed'] + local['passed'],
                  'failures': audit['failures'] + local['failures'],
                  'errors': audit['errors'] + local['errors']}, 'source_bindings': sources}
    label = '.git/stage911_916/source_bound_validation.json'
    atomic_write(root / label, json.dumps(validation, indent=2))
    if passed:
        package_kits(root)
        reconciled = reconcile(root, validation_path=label)
        passed = all(r['software_compatibility'] == 'PASS' for r in reconciled.values())
    data = receipt(916, 'WA tc-less and saved live-receipt offline gate', sources)
    data.update(status='CONFIRMED' if passed else 'FAILED', all_gates_passed=passed,
                evidence_provenance_class='CONFIRMED_STATIC_BINARY',
                provenance_scope='offline executable-source tests and immutable private capture replay only',
                audit_core=audit, native_and_historical=local, tested_revision_unchanged=unchanged,
                repository_gate=repository, physical_acceptance='UNKNOWN',
                live_receipt_scope='existing immutable captures replayed locally; no fresh device access',
                current_target_acceptance=False, old_historical_hashes_rewritten=False,
                publication_scope='public derivatives require a separate staged-blob privacy audit and export tests')
    save(root, STEM, data,
         f"Offline software gate: {'PASS' if passed else 'FAIL'}.\n\n"
         f"Audit core: {audit['passed']} passed, {audit['failures']} failures, {audit['errors']} errors.\n"
         f"Native stub and historical replay suites: {local['passed']} passed, {local['failures']} failures, {local['errors']} errors.\n"
         'All mandatory sources are pinned before testing and checked afterwards.\n'
         'Kits911/912 package current software;913/914 preserve original capture/review bindings and report drift.\n'
         'Stage915 is qualified software readiness, never live treatment/holdout/physical approval.\n'
         'tc-less readback proves the default policy and configured sysfs/debugfs/sysctl knobs only.\n'
         'It does not prove that an existing root qdisc is fq_codel or has custom tc parameters.\n'
         'Historical A/A safety rejection, missing identity fields and unapplied treatments remain blocked.\n'
         'No new SSH, radio write, flash, firewall change or durable-memory ingestion is executed.\n'
         'Publication is restricted to privacy-audited public derivatives; raw evidence stays local.\n'
         'Public source/test projections are tested separately from private original replay.\n'
         'Physical acceptance: UNKNOWN.\n')
    return data


if __name__ == '__main__':
    result = build()
    print(json.dumps({key: result[key] for key in (
        'all_gates_passed', 'audit_core', 'native_and_historical', 'tested_revision_unchanged')}, indent=2))
    raise SystemExit(0 if result['all_gates_passed'] else 1)
