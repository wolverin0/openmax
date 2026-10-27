#!/usr/bin/env python3
"""Source-bound local watchdog tests and the PBE/LBE active-source checksum list."""
from __future__ import annotations

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
from tools.verify.stage779_822_offline_common import atomic_write, receipt, save, snapshot, local

STEMS = {
    984: 'stage984a_guarded_ptp_startup_watchdog',
    985: 'stage985a_watchdog_loss_deadline_and_fault_tests',
    986: 'stage986a_ptp_active_source_sha256_manifest',
}
KIT = 'firmware/openwrt/pbe5ac_gen2_ptp_kit'
WATCHDOG = KIT + '/fmx_ptp_rollback_watchdog.sh'
TRANSACTION = KIT + '/fmx_pbe_lbe_runtime_transaction.sh'
MANIFEST = KIT + '/SHA256SUMS'
TEST = 'tests/test_stage984a_986a_watchdog.py'
SELF = 'tools/verify/' + Path(__file__).name


def refresh_manifest(root: Path) -> list[dict]:
    """Retain exact existing active membership; never add archived payloads or binaries."""
    path = local(root, MANIFEST)
    labels = []
    for line in path.read_text(encoding='ascii').splitlines():
        match = re.fullmatch(r'[0-9a-f]{64}  ([A-Za-z0-9_./-]+)', line)
        if not match or any(p in ('', '.', '..') for p in match[1].split('/')):
            raise ValueError('invalid checksum membership')
        name = match[1]
        if name.startswith('/') or name.startswith(('public_release', 'public_assets')):
            raise ValueError('archived or external checksum member')
        labels.append(KIT + '/' + name)
    if len(labels) != len(set(labels)) or WATCHDOG not in labels or TRANSACTION not in labels:
        raise ValueError('unique active watchdog and transaction members required')
    sources = []
    for label in labels:
        lexical = root / label
        if lexical.is_symlink() or not lexical.is_file():
            raise ValueError('ordinary active source required')
        source = snapshot(root, label)
        if not lexical.read_bytes().startswith(b'#!/bin/sh\n'):
            raise ValueError('shell source shebang required')
        sources.append(source)
    text = ''.join(source['sha256'] + '  ' + source['path'][len(KIT)+1:] + '\n'
                   for source in sources)
    atomic_write(path, text)
    return sources


def test_counts(path: Path, returncode: int) -> dict:
    cases = ET.parse(path).findall('.//testcase') if path.is_file() else []
    failures = sum(case.find('failure') is not None for case in cases)
    errors = sum(case.find('error') is not None for case in cases)
    skipped = sum(case.find('skipped') is not None for case in cases)
    return dict(returncode=returncode, tests=len(cases), passed=len(cases)-failures-errors-skipped,
                failures=failures, errors=errors, skipped=skipped,
                all_passed=returncode == 0 and bool(cases) and not (failures or errors or skipped))


def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    members = refresh_manifest(root)
    labels = [WATCHDOG, TRANSACTION, MANIFEST, TEST, SELF,
              'tools/verify/stage779_822_offline_common.py']
    sources = [snapshot(root, label) for label in labels]
    if not all(source['available'] for source in sources):
        raise ValueError('watchdog and verification sources required')
    gitdir = Path(subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'],
                                         cwd=root, text=True).strip())
    logs = gitdir / 'stage983_988'
    logs.mkdir(parents=True, exist_ok=True)
    xml = logs / 'watchdog_source_bound.xml'
    result = subprocess.run([sys.executable, '-m', 'pytest', TEST, '-q', '--junitxml=' + str(xml)],
                            cwd=root, capture_output=True, text=True, timeout=240)
    atomic_write(logs / 'watchdog_source_bound.stdout', result.stdout)
    atomic_write(logs / 'watchdog_source_bound.stderr', result.stderr)
    tests = test_counts(xml, result.returncode)
    unchanged = all(snapshot(root, row['path']) == row for row in sources + members)
    passed = tests['all_passed'] and unchanged
    reports = {}
    common = dict(evidence_provenance_class='CONFIRMED_STATIC_BINARY',
                  provenance_scope='offline shell source and command-stub verification only',
                  physical_acceptance='UNKNOWN', fresh_live_windows=0,
                  tested_revision_unchanged=unchanged, all_gates_passed=passed)
    details = {
        984: dict(deadlines_s={'non-dfs': 45, 'dfs': 120},
                  guard_scope='bounded startup health observation; not continuous uptime or radio firmware rollback',
                  restoration_scope='reviewed native transient RAM transaction only',
                  default_mode='--dry-run', qdisc_mode='auto',
                  source_marker='SOURCE_STAGE984_WATCHDOG_V1',
                  restored_state_verify='fail-closed; requires a separate baseline audit, never repeats writes',
                  arming_responsibility='immediately after trusted native readback under lock, before watch-state IO',
                  state_record_failure='reported separately from verified native restoration',
                  firmware_restore_authorized=False, flash_executed=False),
        985: dict(tests=tests,
                  fixture_scope='all ping/clock/sleep/native transaction commands replaced with disposable local stubs',
                  real_ping_executed=False, real_45_or_120_second_wait_executed=False,
                  adversarial_coverage=['45s non-DFS and120s DFS unreachable deadlines',
                    'no getter on default inspection', 'healthy link and real native verify dispatch',
                    'probe and verification latency included in the deadline',
                    'clock error, regression, stall, sleep and ping command failures',
                    'arming mkdir and every state write fail closed with native restore',
                    'signals during trusted readback and before first probe; invalid identity never restores',
                    'signal after arming requires verified restore', 'rollback error or false success marker',
                    'unknown channel class and wrong native identity', 'native source hash drift',
                    'snapshot hardlink temporary and deadline rearm rejected']),
        986: dict(manifest=snapshot(root, MANIFEST), member_count=len(members), members=members,
                  membership_policy='existing21 PBE/LBE active shell sources; historical archives excluded',
                  original_historical_receipts_repinned=False, binary_images_emitted=0),
    }
    bodies = {
        984: ('A source-bound startup watchdog requires an already verified native RAM transaction and explicit --apply.\n'
              'Default inspection performs no getters. Explicit channel class selects45s non-DFS or120s DFS; unknown class fails.\n'
              'The fixed sibling fmx_pbe_lbe_runtime_transaction.sh must match the supplied SHA256 and root0755 single-link metadata.\n'
              'Native identity/snapshot validation is delegated to that reviewed exact source, under lock before arming.\n'
              'Trusted readback immediately assigns rollback responsibility before any watchdog snapshot IO.\n'
              'Every arming mkdir/write failure and early signal restores without requiring a writable watchdog directory.\n'
              'A failed state record is reported separately from native rollback/readback; false restoration still exits70.\n'
              'Monotonic /proc/uptime checks bracket every probe and native verification; late success cannot disarm the deadline.\n'
              'Unreachable startup link dispatches verified native --rollback; probe/clock/sleep failures and signals do the same once armed.\n'
              'Failed rollback/readback is ROLLBACK_FAILED, never safe. A watch directory cannot restart its original deadline.\n'
              'Healthy exit proves only the fresh ping plus native configuration readback at that moment.\n'
              'It does not prove ongoing uptime, zero false positives, factory bootability or physical interoperability.\n'
              'A later --verify of a rolled-back event fails closed rather than mutating or inventing fresh baseline proof.\n'
              'No flash, reboot, vendor firmware restore, global DHCP change or protected partition operation is implemented.\n'),
        985: (f"Fresh source-bound pytest: {tests['passed']} PASS, {tests['failures']} FAIL, {tests['errors']} errors, {tests['skipped']} skips.\n"
              'All target commands use disposable stubs; no packets or physical device commands are dispatched.\n'
              'Synthetic monotonic clocks reach45/120 seconds without waiting those wall durations.\n'
              'Retirement RED, intermediate fixture failures and the14-failure P1 arming-IO RED remain in Git metadata.\n'
              'P1 injections cover mkdir, every initial state write, phase move and signal before the first probe.\n'
              'Source hashes are frozen before pytest and checked afterwards; a prior PASS cannot authorize changed code.\n'),
        986: (f'Updated SHA256SUMS retains the exact existing{len(members)} active PBE/LBE source members.\n'
              'Every digest describes the actual current source bytes; no binary or historical archive is added.\n'
              'Old935/936/937 source declarations remain historical and are not rewritten to conceal watchdog drift.\n'
              'The bootstrap remains independently subject to983 validation; a reviewed watchdog alone does not authorize image emission.\n'),
    }
    for stage, detail in details.items():
        data = receipt(stage, STEMS[stage].replace('_', ' '), sources)
        data.update(common, **detail)
        data['status'] = 'CONFIRMED' if passed else 'FAILED'
        reports[stage] = save(root, STEMS[stage], data, bodies[stage] +
                              'Physical acceptance remains UNKNOWN; research and memory ingestion remain deferred offline.\n')
    return reports


if __name__ == '__main__':
    result = build()
    print(json.dumps({str(stage): {'status': row['status'], 'all_gates_passed': row['all_gates_passed']}
                      for stage, row in result.items()}))
    raise SystemExit(0 if all(row['all_gates_passed'] for row in result.values()) else 1)
