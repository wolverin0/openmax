#!/usr/bin/env python3
"""Run bounded, stub-only field-kit regressions and bind their exact source bytes."""
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

STEM = 'stage936a_pbe_ltu_adversarial_test_evidence'
TEST = 'tests/test_chatgpt_audit_pbe_and_ltu_kits.py'
SELF = 'tools/verify/build_stage936a_pbe_ltu_adversarial_test_evidence.py'
DIRECTORIES = ('firmware/openwrt/pbe5ac_gen2_ptp_kit', 'firmware/ltu_safe_kit')


def shell_sources(root: Path) -> list[str]:
    sources = []
    for label in DIRECTORIES:
        for path in sorted((root / label).rglob('*')):
            if not path.is_file() or path.is_symlink():
                continue
            try:
                with path.open(encoding='utf-8') as stream:
                    first = stream.readline()
            except UnicodeError:
                continue
            if first.startswith('#!') and 'sh' in first:
                sources.append(path.relative_to(root).as_posix())
    return sources


def summary(path: Path, returncode: int) -> dict:
    cases = ET.parse(path).findall('.//testcase') if path.is_file() else []
    failures = sum(case.find('failure') is not None for case in cases)
    errors = sum(case.find('error') is not None for case in cases)
    skipped = sum(case.find('skipped') is not None for case in cases)
    return dict(returncode=returncode, tests=len(cases), passed=len(cases)-failures-errors-skipped,
                failures=failures, errors=errors, skipped=skipped,
                all_passed=returncode == 0 and bool(cases) and not (failures or errors or skipped))


def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    labels = shell_sources(root) + [TEST, SELF,
                                    'tools/verify/stage779_822_offline_common.py']
    sources = [snapshot(root, label) for label in labels]
    if not all(source['available'] for source in sources):
        raise ValueError('mandatory regression or shell sources missing')
    gitdir = Path(subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'],
                                         cwd=root, text=True).strip())
    logs = gitdir / 'stage935_940'
    logs.mkdir(parents=True, exist_ok=True)
    xml = logs / 'stage936_adversarial.xml'
    command = [sys.executable, '-m', 'pytest', TEST, '-q', '--junitxml=' + str(xml)]
    process = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=1200)
    atomic_write(logs / 'stage936_adversarial.stdout', process.stdout)
    atomic_write(logs / 'stage936_adversarial.stderr', process.stderr)
    counts = summary(xml, process.returncode)
    unchanged = labels == shell_sources(root) + [TEST, SELF,
                         'tools/verify/stage779_822_offline_common.py'] and all(
                             snapshot(root, source['path']) == source for source in sources)
    passed = counts['all_passed'] and unchanged
    data = receipt(936, 'PowerBeam and LTU adversarial command-stub evidence', sources)
    data.update(status='CONFIRMED' if passed else 'FAILED', all_gates_passed=passed,
                evidence_provenance_class='CONFIRMED_STATIC_BINARY',
                evidence_scope='source and simulated-command software validation only; no target binary or hardware test',
                tests=counts, tested_revision_unchanged=unchanged,
                shell_source_count=len(shell_sources(root)), device_commands_executed=False,
                fixture_boundary='all device tools use disposable local command stubs',
                archived_source_scope='Immutable historical release snapshots are pinned only, excluded from runtime testing and v23 packaging',
                physical_acceptance='UNKNOWN', fresh_live_windows=0,
                target_firmware_loaded=False, native_firewall_changed=False)
    return save(root, STEM, data,
                f"Software-only adversarial tests: {'PASS' if passed else 'FAIL'}.\n\n"
                f"Fresh pytest: {counts['passed']} passed, {counts['failures']} failures, "
                f"{counts['errors']} errors, {counts['skipped']} skipped.\n"
                'All shell entrypoint and test bytes are pinned before execution and checked afterwards.\n'
                'Defaults, supported transactions and blocked legacy entrypoints have distinct contracts.\n'
                'Tests use disposable uci/tc/sysfs/sysctl command stubs; no host or device knob is changed.\n'
                'Fault cases reject unsupported defaults, failed getters, false readbacks and failed restoration.\n'
                'The static provenance enum describes source/software evidence only, not native binary acceptance.\n'
                'Zero live windows. Physical acceptance: UNKNOWN.\n')


if __name__ == '__main__':
    result = build()
    print(json.dumps(dict(status=result['status'], tests=result['tests'],
                          tested_revision_unchanged=result['tested_revision_unchanged'])))
    raise SystemExit(0 if result['all_gates_passed'] else 1)
