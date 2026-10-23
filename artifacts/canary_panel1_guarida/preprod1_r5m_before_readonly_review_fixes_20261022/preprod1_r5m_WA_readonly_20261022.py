"""Bounded PREPROD1 diagnostic: existing guarded open AP, exact WA reads only."""
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from datetime import datetime, timezone

import paramiko
import root_four_cpe_access_20261022 as a

HERE = Path(__file__).resolve().parent
LABEL = '20261022_r5m_WA_readonly'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
utc = lambda: datetime.now(timezone.utc).isoformat()


def main():
    planpath = HERE / ('preprod1_plan_' + LABEL + '.json')
    plan = json.loads(planpath.read_text(encoding='utf8'))
    a.require(plan['frozen'] and plan['production_access_permitted'] is False, 'SCOPE_NOT_FROZEN')
    for name, digest in plan['source_bindings'].items():
        a.require(sha(HERE.parent.parent / name) == digest, 'SOURCE_CHANGED_' + name)
    review = json.loads((HERE / plan['review_file']).read_text(encoding='utf8'))
    a.require(review['status'].startswith('PASS') and review['plan_sha256'] == sha(planpath)
              and review['source_bindings'] == plan['source_bindings'], 'REVIEW_NOT_BOUND')
    out = HERE / ('preprod1_' + LABEL)
    out.mkdir(exist_ok=False)
    rec = dict(status='INCOMPLETE_READONLY_DIAGNOSTIC', started_utc=utc(), failures=[],
               cleanup_errors=[], source_bindings=plan['source_bindings'],
               plan_sha256=sha(planpath), review_sha256=sha(HERE / plan['review_file']),
               scope='No PREPROD1 acceptance or CPE mutation; only prior-failure evidence retrieval')
    def save():
        (out / 'receipt.json').write_text(json.dumps(rec, indent=2), encoding='utf8')
    frozen = out / 'executed-source'; frozen.mkdir()
    for name in plan['source_bindings']:
        (frozen / Path(name).name).write_bytes((HERE.parent.parent / name).read_bytes())
    probe = a.load('root_loco195_eth_readonly_20261021.py')
    reuse = a.load('preprod1_trial_20261022.py')
    ap = wa = helper = None
    armed = False
    original_tables = None
    data = {}
    try:
        save()
        ap = a.load('root_goal_direct_link_connection_20261022.py').ap_client()
        helper = a.ap_helper()  # Existing 480s independently bounded AP rollback guard.
        rec['before_AP_off'] = helper.off(ap)
        table = 'fmx_preprod_' + helper.TOKEN
        rules, cleanup = reuse.bridge_isolation(table, helper.TOKEN)
        original_tables = a.remote(ap, 'nft list tables')['stdout']
        a.require(('table bridge ' + table) not in original_tables.splitlines(), 'TABLE_ALREADY_EXISTS')
        original_restore = helper.restore_body
        helper.restore_body = lambda: reuse.restore_with_bridge_isolation(original_restore(), cleanup)
        (frozen / 'AP_guard.sh').write_text(helper.guard_body(), encoding='utf8')
        (frozen / 'AP_restore.sh').write_text(helper.restore_body(), encoding='utf8')
        rec['AP_armed'] = helper.arm(ap); armed = True; save()
        rec['isolation_install'] = a.remote(ap, "set -eu\nnft -f - <<'FMX_ISOLATION'\n" + rules + 'FMX_ISOLATION\n')
        end = time.monotonic() + 45
        rec['WA_radio_probes'] = []
        while time.monotonic() < end:
            remaining = end - time.monotonic()
            a.require(remaining > 0, 'WA_READONLY_RF_PATH_DEADLINE')
            result = a.remote(ap, 'ping -6 -c 1 -W 1 -I br-lan fe80::feec:daff:fec2:540a', check=False, timeout=min(4, remaining))
            a.require(time.monotonic() < end, 'WA_READONLY_RF_PATH_DEADLINE')
            rec['WA_radio_probes'].append(dict(mono=time.monotonic(), result=result)); save()
            if result['exit_code'] == 0:
                break
            time.sleep(min(1, max(0, end - time.monotonic())))
        else:
            raise RuntimeError('WA_READONLY_RF_PATH_NOT_AVAILABLE')
        sock = ap.get_transport().open_channel('direct-tcpip', ('fe80::feec:daff:fec2:540a%br-lan', 22), ('10.99.0.1', 0), timeout=6)
        transport = paramiko.Transport(sock)
        transport.auth_timeout = 6
        transport.banner_timeout = 6
        wa = paramiko.SSHClient(); wa._transport = transport
        transport.start_client(timeout=6)
        a.require(hashlib.sha256(transport.get_remote_server_key().asbytes()).hexdigest() == probe.PIN, 'WA_PIN_MISMATCH')
        username, password = probe.credentials()
        transport.auth_password(username, password)
        del password
        identity = a.remote(wa, probe.IDENTITY, timeout=6)
        a.require('board.sysid=0xe7fa' in identity['stdout'].lower() and 'fcecda' in identity['stdout'].replace(':', '').lower(), 'WA_IDENTITY_MISMATCH')
        data['identity'] = identity
        data['bridge_MAC'] = a.remote(wa, 'cat /sys/class/net/br0/address', timeout=6)
        a.require(data['bridge_MAC']['stdout'].strip().lower() == 'fc:ec:da:c2:54:0a', 'WA_EXACT_MAC_MISMATCH')
        queries = {'status': 'wpa_cli -i ath0 status', 'radio': 'iwconfig ath0',
                   'bss': 'wpa_cli -i ath0 bss 18:e8:29:74:55:a2',
                   'log': 'logread | tail -n 400', 'kernel': 'dmesg | tail -n 150',
                   'uptime': 'cat /proc/uptime',
                   'hashes': 'md5sum /tmp/system.cfg /tmp/running.cfg /etc/wpasupplicant_AUTO.conf'}
        before = a.remote(wa, queries['hashes'], timeout=6)
        data['queries'] = {name: a.remote(wa, command, check=False, timeout=6, limit=65536) for name, command in queries.items()}
        after = a.remote(wa, queries['hashes'], timeout=6)
        a.require(before == after, 'READONLY_WA_CONFIG_HASH_CHANGED')
        rec['WA_readonly_hashes_unchanged'] = True
        rec['WA_identity'] = identity
        rec['WA_readonly'] = {name: result for name, result in data['queries'].items() if name not in ['log', 'kernel']}
        pattern = r'CTRL-EVENT|deauth.*reason|disassoc.*reason|Authentication with|Trying to associate|Trying to authenticate|Associated with|WPA:.*negotiation completed'
        rec['WA_authentication_log_lines'] = {name: [line for line in data['queries'][name]['stdout'].splitlines() if re.search(pattern, line, re.I)] for name in ['log', 'kernel']}
        rec['diagnostic_acquired'] = True
    except BaseException as exc:
        rec['failures'].append(dict(type=type(exc).__name__, gate=str(exc)[:160]))
    finally:
        if wa is not None:
            try:
                wa.close()
            except BaseException as exc:
                rec['cleanup_errors'].append(dict(stage='WA_close', type=type(exc).__name__))
        try:
            private = HERE / 'preprod_guarida_20261022/history'
            private.mkdir(exist_ok=True)
            rawpath = private / ('preprod1_' + LABEL + '_private_raw.json')
            rawpath.write_text(json.dumps(data, indent=2), encoding='utf8')
            rec['private_raw_sha256'] = sha(rawpath)
        except BaseException as exc:
            rec['cleanup_errors'].append(dict(stage='private_evidence', type=type(exc).__name__))
        if armed:
            try:
                rec['AP_restoration'] = helper.restore(ap)
                a.require(a.remote(ap, 'nft list tables')['stdout'] == original_tables, 'NFT_TABLES_NOT_RESTORED')
                rec['nft_exact_original_tables_restored'] = True
                command = 'set -eu\n' + helper.header() + helper.file_guards()
                for name in ['owner', 'ready', 'guard.id', 'deadline', 'guard.sh', 'restore.sh', 'guard.log', 'restore.log', 'restored']:
                    command += 'test ! -L "$D/' + name + '"; rm -f "$D/' + name + '"\n'
                command += 'rmdir "$D"\ntest ! -e "$D"\necho AP_OWNED_RAM_GUARD_REMOVED\n'
                rec['owned_RAM_cleanup'] = a.remote(ap, command)
            except BaseException as exc:
                rec['cleanup_errors'].append(dict(type=type(exc).__name__, gate=str(exc)[:160]))
        if ap is not None:
            ap.close()
        passed = rec.get('diagnostic_acquired') and rec.get('AP_restoration', {}).get('guard_ended_verified') and not rec['failures'] and not rec['cleanup_errors']
        rec.update(status='PASS_READONLY_WA_DIAGNOSTIC_AP_RESTORED' if passed else 'INCOMPLETE_READONLY_DIAGNOSTIC_PRESERVED', ended_utc=utc(), exit_code=0 if passed else 1)
        save()
    print(json.dumps(rec, indent=2))
    return rec['exit_code']


if __name__ == '__main__':
    if sys.argv[1:] != ['--execute']:
        raise SystemExit('PLAN_ONLY: exact --execute and a bound independent review required')
    raise SystemExit(main())
