#!/usr/bin/env python3
"""Fail-closed offline release gate for849A..854A; stage count is a label."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.enforce_5pillar_research_gate import audit_repo_deterministic_gates
from tools.verify.stage779_822_offline_common import atomic_write, receipt, save, snapshot, read_json
from tools.verify.stage849_854_release_common import (CODE, STEMS, PRIVACY_PATHS, artifact, audit_stage,
                                                     publication_paths)

STEM = STEMS[854]
TEST_FILES = [f'tests/test_stage{n}a.py' for n in range(849, 855)] + [
    'tests/test_stage849a_to_854a_suite.py']


def audit_release(root: Path = ROOT) -> dict:
    rows = [audit_stage(root, n) for n in range(849, 854)]
    from tools.verify.stage779_822_offline_common import read_json
    try:
        count = read_json(root, artifact(852))['accounting']
        target = (count['target_windows'] == 1050 and count['actual_synthetic_windows'] >= 1050
                  and count['target_met'] is True and count['physical_windows_executed'] == 0
                  and count['promotion_allowed'] is False)
    except (OSError, ValueError, TypeError, KeyError):
        target = False
    return {'stage_audits': rows, 'target_met': target,
            'all_artifacts_ok': all(x['compliant'] for x in rows) and target,
            'physical_acceptance': 'UNKNOWN',
            'scope': '849A..854A offline release only; no claim of854 completed physical stages'}


def pytest_summary(xml_path: Path, returncode: int) -> dict:
    if not xml_path.is_file():
        return {'returncode': returncode, 'all_passed': False, 'tests': 0,
                'failures': 0, 'errors': 1, 'skipped': 0}
    tree = ET.parse(xml_path)
    cases = tree.findall('.//testcase')
    counts = {k: sum(c.find(tag) is not None for c in cases)
              for k, tag in [('failures', 'failure'), ('errors', 'error'), ('skipped', 'skipped')]}
    return {'returncode': returncode, 'tests': len(cases), **counts,
            'all_passed': returncode == 0 and bool(cases) and not any(counts.values())}


def build(root: Path = ROOT) -> dict:
    audit = audit_release(root)
    repository = audit_repo_deterministic_gates(root)
    sources = [snapshot(root, artifact(n)) for n in range(849, 854)]
    labels = {p for p in publication_paths() if p.endswith(('.py', '.txt')) and p not in PRIVACY_PATHS}
    for n in range(849, 854):
        labels.update(source['path'] for source in read_json(root, artifact(n))['sources'])
    verification_sources = [snapshot(root, label) for label in sorted(labels)]
    from tools.verify.verify_stage853a_public_git_sync_and_push_v2 import check_index
    hygiene = check_index(root)
    # No recursively launched gate in the tests: tests exercise audit_release and parsers only.
    with tempfile.TemporaryDirectory(prefix='openmax854-') as tmp:
        xml_path = Path(tmp) / 'pytest.xml'
        proc = subprocess.run([sys.executable, '-m', 'pytest', *TEST_FILES, '-q',
                               '--junitxml=' + str(xml_path)], cwd=root,
                              capture_output=True, text=True, timeout=240)
        result = pytest_summary(xml_path, proc.returncode)
        gitdir = subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'], cwd=root,
                                         text=True).strip()
        logs = Path(gitdir) / 'stage854a'
        logs.mkdir(parents=True, exist_ok=True)
        atomic_write(logs / 'pytest.stdout', proc.stdout)
        atomic_write(logs / 'pytest.stderr', proc.stderr)
        if xml_path.exists():
            atomic_write(logs / 'pytest.xml', xml_path.read_text(encoding='utf-8'))
    unchanged = all(snapshot(root, source['path']) == source for source in sources + verification_sources)
    ok = (audit['all_artifacts_ok'] and repository['compliant'] and hygiene['compliant']
          and result['all_passed'] and unchanged and audit_release(root)['all_artifacts_ok'])
    data = receipt(854, 'Ground-up v14 offline release gate through854A', sources)
    if not all(p['available'] for p in verification_sources):
        ok = False
    data.update(status='CONFIRMED' if ok else 'FAILED', all_gates_passed=ok,
                release_audit=audit, pytest=result, repository_gate=repository,
                final_index_hygiene={'compliant': hygiene['compliant'],
                                     'findings': hygiene['findings_by_rule']},
                verification_sources=verification_sources,
                tested_revision_unchanged=unchanged,
                validation_scope='local offline software tests; not device, DFS or RF acceptance',
                five_pillar_scope='structural references, truthful deferred external work',
                physical_acceptance='UNKNOWN')
    save(root, STEM, data,
         f"Offline release gate: {'PASS' if ok else 'FAIL'}.\n\n"
         f"Fresh scoped pytest: {result['tests']} tests; failures {result['failures']}; "
         f"errors {result['errors']}; skipped {result['skipped']}.\n"
         'Sources849A..853A are rebound to their actual bytes; missing/drifting evidence fails closed.\n'
         'This gate covers the named release block;854 is not a verified count of physical experiments.\n'
         'Pillars A/B/C/E retain explicit offline reference/plan/deferred/local-ledger states.\n'
         'Pillar D executes a bounded synthetic model and Pareto analysis.\n'
         'Repository hook wiring passes separately from external research or memory ingestion.\n'
         'Stage853A rechecks staged bytes before commit and verifies origin/main after push.\n'
         'Physical acceptance: UNKNOWN. No SSH, radio writes or flashing.\n')
    return data


if __name__ == '__main__':
    result = build()
    print(json.dumps({'all_gates_passed': result['all_gates_passed'], 'pytest': result['pytest']}, indent=2))
    raise SystemExit(0 if result['all_gates_passed'] else 1)
