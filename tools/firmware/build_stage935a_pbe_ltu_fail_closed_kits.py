#!/usr/bin/env python3
"""Inventory the active v23 kit boundary without executing any actuator."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.stage779_822_offline_common import receipt, save, snapshot

STEM = 'stage935a_pbe_ltu_fail_closed_kits'
KIT_ROOTS = ('firmware/openwrt/pbe5ac_gen2_ptp_kit', 'firmware/ltu_safe_kit')
ENGINES = (
    KIT_ROOTS[0] + '/fmx_pbe_lbe_runtime_transaction.sh',
    KIT_ROOTS[1] + '/fmx_ltu_runtime_transaction.sh',
)


def shell_inventory(root: Path) -> tuple[list[str], list[str]]:
    active, archived = [], []
    for label in KIT_ROOTS:
        directory = root / label
        for path in sorted(directory.rglob('*')):
            if not path.is_file() or path.is_symlink():
                continue
            blob = path.read_bytes()
            if not blob.startswith(b'#!') or b'sh' not in blob.splitlines()[0]:
                continue
            head = path.relative_to(directory).parts[0]
            target = archived if head.startswith('public_release') or head == 'public_assets' else active
            target.append(path.relative_to(root).as_posix())
    return sorted(active), sorted(archived)


def audit_active(root: Path, labels: list[str]) -> list[dict]:
    result = []
    for label in labels:
        text = (root / label).read_text(encoding='utf-8')
        engine = label in ENGINES
        checks = {
            'strict_shell': 'set -eu' in text and 'set -f' in text,
            'dry_run_default': 'MODE=--dry-run' in text,
            'explicit_modes': all(value in text for value in ('--apply', '--verify', '--rollback')),
            'qdisc_mode_contract': all(value in text for value in ('--qdisc-mode', 'auto', 'tc', 'sysfs-default')),
            'no_error_masking': '|| true' not in text,
            'no_invalid_qdisc_option': 'initial_quantum' not in text,
            'state': ('secure_state()' in text and "set -C" in text and '%u:%a:%h' in text)
                     if engine else 'PLANNED_RETIRED' in text,
        }
        if engine:
            checks.update(verify_before_success='verify_applied\nphase APPLIED_VERIFIED' in text,
                          verify_restoration='verify_restored' in text,
                          exact_identity='identity fingerprint' in text and 'revision mismatch' in text,
                          no_commit_reload='uci commit' not in text and '/etc/init.d/' not in text)
        else:
            checks['actuation_unavailable'] = all(value not in text for value in (
                'uci ', 'sysctl ', 'tc qdisc', 'iwpriv ', 'cfgmtd ', 'mtd write', 'reboot'))
        result.append({'path': label, 'kind': 'EXPLICIT_NATIVE_TRANSACTION' if engine else 'RETIRED_LEGACY_ACTUATOR',
                       'checks': checks, 'passed': all(checks.values())})
    return result


def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    active, archived = shell_inventory(root)
    if not active or not all(label in active for label in ENGINES):
        raise ValueError('both explicit native engines and active kit inventory required')
    checks = audit_active(root, active)
    if not all(row['passed'] for row in checks):
        raise ValueError('active kit source contract failed: ' + json.dumps(checks))
    sources = [snapshot(root, label) for label in active + [
        'tools/firmware/' + Path(__file__).name, 'tools/verify/stage779_822_offline_common.py']]
    data = receipt(935, 'PBE/LBE and LTU v23 fail-closed active kit boundary', sources)
    original = root / '.git/stage935_940/stage935_original_inventory.json'
    prior = json.loads(original.read_text(encoding='utf-8')) if original.is_file() else []
    prior_hashes = {row['path']: row['sha256'] for row in prior}
    data.update(evidence_provenance_class='CONFIRMED_STATIC_BINARY',
                provenance_detail='Static POSIX source audit only; no native binary or actuator executed',
                active_entrypoints=len(active), native_engines=len(ENGINES),
                retired_legacy_entrypoints=len(active)-len(ENGINES), active_source_audit=checks,
                historical_archives=[dict(snapshot(root, label),
                    state='LEGACY_ARCHIVE_NOT_RELEASED', execution_allowed=False,
                    release_membership=False) for label in archived],
                original_legacy_source_sha256={label: prior_hashes.get(label)
                    for label in active if label not in ENGINES},
                release_source_members=active, source_only_release=True,
                state_security='root-owned0700 directory; regular0600 single-link files; no temporary-path overwrite',
                qdisc_policy='tc strict snapshot/readback or configured kernel fq_codel default only',
                uci_policy='disabled by default; optional network.lan.mtu RAM delta only; no commit/reload',
                ltu_native_preconditions='exact native ubus board/revision and ethtool/driver evidence required; unavailable means BLOCKED',
                runtime_compatibility='UNKNOWN', physical_acceptance='UNKNOWN',
                firmware_images_built=0, target_commands_executed=False,
                original_legacy_sources_retained_locally=bool(prior))
    return save(root, STEM, data,
        f"Active source boundary: {len(active)} entrypoints:2 explicit native transactions and "
        f"{len(active)-2} retired legacy actuators.\n\n"
        'All active defaults return PLANNED without getters or device commands.\n'
        'Legacy entrypoints reject apply/verify/rollback; selecting a native replacement is an explicit operator decision.\n'
        'Native engines require exact board, revision, kernel, driver, firmware and interface-index identity.\n'
        'PBE/LBE uses an explicit PHY; LTU uses PHY=none and a native driver identity, never a mac80211 assumption.\n'
        'The current LTU board getter contract requires ubus; unavailable native getters block apply.\n'
        'Transient scope: egress tx_queue_len1000 and netdev_max_backlog1000; no radio reload or firmware activation.\n'
        'Optional --uci-mode ram edits only network.lan.mtu to1500, requires no prior pending changes, and never commits/reloads.\n'
        'Rollback reverts only that UCI key and verifies the original value and empty pending changes.\n'
        'qdisc-mode auto uses tc when present; tc errors never fall back. sysfs-default requires kernel default fq_codel.\n'
        'Default-policy readback does not establish an existing active root qdisc or custom tc parameters.\n'
        'Snapshots must be root-owned0700 directories with0600 single-link regular files; phase writes use noclobber.\n'
        'Every changed knob is read back; rollback is verified, and restoration failure reports ROLLBACK_FAILED.\n'
        f"{len(archived)} historical public_release/public_assets source snapshots remain immutable and excluded from v23 packaging.\n"
        'Original retired source bytes are retained in local Git metadata; credential-bearing legacy sources are not public payloads.\n'
        'Static-source provenance is not native acceptance, successful conversion, radio performance or safe flash approval.\n'
        'Physical acceptance, LTU native compatibility and runtime performance: UNKNOWN.\n')


if __name__ == '__main__':
    result = build()
    print(json.dumps({'stage': result['stage'], 'active': result['active_entrypoints'],
                      'retired': result['retired_legacy_entrypoints'],
                      'archives_excluded': len(result['historical_archives'])}))
