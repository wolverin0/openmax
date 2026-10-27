#!/usr/bin/env python3
"""Package source-bound WA tc-optional transaction evidence; never run a kit."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.stage779_822_offline_common import receipt, save, snapshot

STEMS = {911: 'stage911a_wa_tc_optional_native_field_kits',
         912: 'stage912a_wa_tc_and_kernel_default_regressions'}
HELPERS = ['firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh',
           'firmware/openwrt/common/fmx_wa_v14_356window_field_kit.sh',
           'firmware/openwrt/common/fmx_wa_v15_368window_field_kit.sh']


def build(root: Path = ROOT) -> dict:
    sources = [snapshot(root, p) for p in HELPERS + [
        'tools/firmware/' + Path(__file__).name,
        'tests/test_chatgpt_audit_wa_kit.py', 'tests/test_stage911a_to_916a_suite.py']]
    if not all(row['available'] for row in sources):
        raise ValueError('required kit, builder and regression sources missing')
    data = receipt(911, 'Native WA tc-optional field-kit source package', sources)
    data.update(qdisc_modes=['auto', 'tc', 'sysfs-default'], default_mode='auto',
                evidence_provenance_class='CONFIRMED_STATIC_BINARY',
                provenance_scope='source-byte inspection and offline software stubs; no native firmware or RF acceptance',
                apply_requires='--apply plus exact identity contract and absolute state directory',
                backends={'tc': {'qdisc_parameters_readback': 'tc -d qdisc show',
                                 'root_replacement': True},
                          'kernel_default_fq_codel': {
                              'precondition': '/proc/sys/net/core/default_qdisc equals fq_codel',
                              'active_qdisc': 'UNKNOWN', 'root_replacement': False,
                              'custom_quantum_target_interval_applied': False}},
                native_readbacks=['per-AC AQL', 'pktlog_filter', 'BQL limit_max',
                                  'tx_queue_len', 'profile sysctls', 'selected backend'],
                snapshot_backend_and_profile_bound=True, runtime_acceptance='UNKNOWN',
                legacy_snapshot_policy='Use the original kit to restore old snapshots before a new transaction',
                board_revision_policy='Missing board revision remains a blocking identity precondition',
                states=['PLANNED', 'APPLIED_VERIFIED', 'FAILED_ROLLED_BACK',
                        'FAILED_PRECONDITION', 'ROLLBACK_FAILED'])
    save(root, STEMS[911], data,
         'Source package only; no radio is contacted or mutated by this builder.\n'
         '`--qdisc-mode auto|tc|sysfs-default` defaults to auto. Inspection/dry-run performs no getters.\n'
         'Auto selects tc when installed; tc command/readback failure never silently selects another backend.\n'
         'Without tc, the kernel default must read exactly fq_codel; otherwise fail before device writes.\n'
         'Kernel-default mode tunes/readbacks AQL, pktlog, BQL, tx_queue_len1000 and profile sysctls.\n'
         'It does not set or verify custom qdisc quantum, target or interval and does not prove an existing active root qdisc.\n'
         '`qdisc_backend=kernel_default_fq_codel`, `qdisc_readback=default_policy_only`, `active_qdisc=UNKNOWN`.\n'
         '`--verify --identity FILE --state-dir ABSOLUTE` requires a matching successful transaction and performs real reads.\n'
         'Snapshot profile/backend are fixed across apply, verify, idempotence and rollback; no fallback after drift.\n'
         'Existing state requires root-owned mode700 directories, mode600 single-link regular files and no phase temporary file.\n'
         'BusyBox-compatible stat -c metadata support is required; missing tools fail before writes.\n'
         'All three kits require exact board/revision/driver/firmware/interface identity; old positional v14/v15 calls fail closed.\n'
         'Native AQL VO/VI/BE/BK and numeric AC rows are normalized; duplicate/incomplete rows are rejected.\n'
         'Failure restores all changed knobs and verifies restoration; failed restoration is ROLLBACK_FAILED.\n'
         'Missing board_revision and other historical897A blockers are not bypassed.\n'
         'Attribution: Linux/mac80211/ath10k configuration; hardware and physical acceptance UNKNOWN.\n')
    tests = receipt(912, 'WA tc and kernel-default regression contract', sources)
    tests.update(test_contract='local command stubs only; executed results are recorded by916A',
                 evidence_provenance_class='CONFIRMED_STATIC_BINARY',
                 provenance_scope='offline executable-source regression contract, not firmware execution',
                 tests_executed_by_this_builder=False, physical_acceptance='UNKNOWN')
    save(root, STEMS[912], tests,
         'Regression sources exercise tc present, absent tc with fq_codel default, and absent/incorrect defaults.\n'
         'Additional contracts cover dry-run, exact identity, per-profile native AQL labels, real verify readbacks,\n'
         'backend persistence, readback drift, mutation failure rollback and failed restoration.\n'
         'Tests replace every device getter/setter and restrict PATH for the tc-less path.\n'
         'This receipt pins the test sources; it does not substitute declarations for executed pytest.\n'
         'Fresh executed counts and exit codes are in Stage916A. Physical acceptance UNKNOWN.\n')
    return {'911A': data, '912A': tests}


if __name__ == '__main__':
    print(json.dumps({stage: row['status'] for stage, row in build().items()}))
