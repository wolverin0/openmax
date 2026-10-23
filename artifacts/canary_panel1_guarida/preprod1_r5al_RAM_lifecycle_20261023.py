"""Reviewed LAP120 RF-off test of the existing AP guard's RAM wpad rollback.

Default PLAN_ONLY. --execute requires an exact independently reviewed plan SHA.
No CPE connection, radio enable, firmware write, package install or production.
"""
import argparse
import hashlib
import json
import re
import shlex
import time
from datetime import datetime, timezone
from pathlib import Path

import root_four_cpe_access_20261022 as access


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PLAN = HERE / 'preprod1_r5al_RAM_lifecycle_plan_20261023.json'
sha = lambda data: hashlib.sha256(data).hexdigest()


def setup(plan, preview=False):
    access.require(re.fullmatch('[0-9a-f]{32}', plan['helper_token']), 'LIFECYCLE_OWNER_TOKEN')
    helper = access.ap_helper()
    helper.TOKEN = plan['helper_token']
    helper.DIR = '/tmp/fmx-step1c-ap-observer-' + helper.TOKEN
    helper.TTL = 45
    original_guard = helper.guard_body
    helper.guard_body = lambda: original_guard().replace('+480))', '+45))')
    compat_module = access.load('preprod1_AP_compat_20261023.py')
    trial = access.load('preprod1_trial_20261022.py')
    private = HERE / 'preprod_guarida_20261022/history'
    label = 'preprod1_r5al_lifecycle_preview' if preview else 'preprod1_r5al_lifecycle'
    compat = compat_module.Compat(helper, private / label, trial.remote, HERE / plan['binary_file'])
    return helper, compat, trial.remote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', metavar='PLAN_SHA256')
    args = parser.parse_args()
    plan = json.loads(PLAN.read_text())
    if not args.execute:
        print(json.dumps({'status': 'PLAN_ONLY', 'plan_sha256': sha(PLAN.read_bytes()),
                          'radio_enable': False, 'connections': False}))
        return
    access.require(plan['frozen'] is True and plan['production_access_permitted'] is False,
                   'LIFECYCLE_SCOPE_NOT_FROZEN')
    access.require(args.execute == sha(PLAN.read_bytes()), 'LIFECYCLE_PLAN_CHANGED')
    for path, digest in plan['source_bindings'].items():
        access.require(sha((ROOT / path).read_bytes()) == digest, 'LIFECYCLE_SOURCE_CHANGED_' + path)
    for row in plan['preconditions']:
        access.require(sha((HERE / row['file']).read_bytes()) == row['sha256'],
                       'LIFECYCLE_PRECONDITION_CHANGED_' + row['file'])
    review = json.loads((HERE / plan['review_file']).read_text())
    access.require(review['status'].startswith('PASS') and
                   review['plan_sha256'] == args.execute and
                   review['source_bindings'] == plan['source_bindings'],
                   'LIFECYCLE_INDEPENDENT_REVIEW_NOT_BOUND')
    out = HERE / 'preprod1_r5al_RAM_lifecycle_20261023'
    out.mkdir(exist_ok=False)
    record = {'status': 'INCOMPLETE', 'started_utc': datetime.now(timezone.utc).isoformat(),
              'plan_sha256': args.execute, 'review_sha256': sha((HERE / plan['review_file']).read_bytes()),
              'radio_enable': False, 'CPE_or_production_access': False, 'cleanup_errors': []}

    def save():
        (out / 'receipt.json').write_text(json.dumps(record, indent=2) + '\n')

    save()
    ap = compat = helper = None
    try:
        helper, compat, remote = setup(plan)
        access.require(sha(helper.guard_body().encode()) == plan['rendered_guard_sha256'] and
                       sha(helper.restore_body().encode()) == plan['rendered_restore_sha256'],
                       'LIFECYCLE_RENDER_CHANGED')
        for name, data in [('guard.sh', helper.guard_body()), ('restore.sh', helper.restore_body())]:
            (out / name).write_text(data)
        ap = access.load('root_goal_direct_link_connection_20261022.py').ap_client()
        helper.off(ap)
        record['baseline'] = remote(ap, 'sha256sum /usr/sbin/wpad /etc/config/network /etc/config/wireless; '
                                   'cat /proc/sys/kernel/random/boot_id')['stdout']
        record['compat'] = compat.record
        save()
        compat.prepare_and_activate(ap)
        access.require(compat.record.get('status') == 'COMPAT_ACTIVE_RADIO_OFF', 'LIFECYCLE_COMPAT_NOT_ACTIVE')
        record['compat'] = compat.record
        record['activated_monotonic'] = time.monotonic()
        save()
        # Do not invoke restore: this phase must be completed by the native guard.
        end = time.monotonic() + 65
        marker = shlex.quote(helper.DIR + '/restored')
        while time.monotonic() < end:
            state = remote(ap, 'test -f ' + marker, timeout=4, check=False)
            if state['exit_code'] == 0:
                record['native_guard_restore_observed'] = True
                break
            time.sleep(1)
        access.require(record.get('native_guard_restore_observed'), 'NATIVE_GUARD_RESTORE_DEADLINE')
        record['restoration'] = compat.verify_restored(ap)
        access.require(record['restoration'].get('status') == 'PASS_COMPAT_STOCK_RESTORED',
                       'LIFECYCLE_RESTORATION_NOT_CONFIRMED')
        record['after'] = remote(ap, 'sha256sum /usr/sbin/wpad /etc/config/network /etc/config/wireless; '
                                'cat /proc/sys/kernel/random/boot_id')['stdout']
        access.require(record['after'] == record['baseline'], 'RF_OFF_BASELINE_NOT_EXACTLY_RESTORED')
        record['guard_logs'] = remote(ap, 'cat ' + shlex.quote(helper.DIR + '/guard.log') + '; '
                                     'cat ' + shlex.quote(helper.DIR + '/restore.log'), timeout=8)['stdout']
        command = 'set -eu\n' + helper.header() + helper.file_guards()
        for name in ['owner', 'ready', 'guard.id', 'deadline', 'guard.sh', 'restore.sh',
                     'guard.log', 'restore.log', 'restored'] + list(compat.cleanup_names):
            command += 'test ! -L "$D/' + name + '"; rm -f "$D/' + name + '"\n'
        command += 'rmdir "$D"\ntest ! -e "$D"\necho OWNED_RAM_REMOVED\n'
        record['RAM_cleanup'] = remote(ap, command, timeout=10)
        record['status'] = 'PASS_RF_OFF_RAM_WPAD_NATIVE_GUARD_RESTORED'
    except BaseException as exc:
        record['error'] = type(exc).__name__ + ': ' + str(exc)
        record['status'] = 'NOT_ACCEPTED_RF_OFF_LIFECYCLE'
        if ap is not None and compat is not None:
            try:
                record['failure_restoration'] = compat.restore_if_needed(ap)
            except BaseException as cleanup:
                record['cleanup_errors'].append(str(cleanup))
    finally:
        if compat is not None:
            record['compat'] = compat.record
        if ap is not None:
            try:
                ap.close()
            except BaseException as close_error:
                record['cleanup_errors'].append('AP_close: ' + str(close_error))
                record['status'] = 'NOT_ACCEPTED_RF_OFF_LIFECYCLE'
        record['ended_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    print(json.dumps({'status': record['status'], 'cleanup_errors': record['cleanup_errors'],
                      'error': record.get('error'), 'receipt_sha256': sha((out / 'receipt.json').read_bytes())}))
    return 0 if record['status'] == 'PASS_RF_OFF_RAM_WPAD_NATIVE_GUARD_RESTORED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
