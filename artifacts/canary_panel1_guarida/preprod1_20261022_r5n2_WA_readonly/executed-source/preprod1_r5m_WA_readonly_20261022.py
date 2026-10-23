"""Bounded PREPROD1 diagnostic: existing guarded open AP, exact WA reads only."""
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys
import threading
import time
from datetime import datetime, timezone

import paramiko
import root_four_cpe_access_20261022 as a

HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
utc = lambda: datetime.now(timezone.utc).isoformat()


def readonly_command(client, command, timeout=6, limit=65536, check=True):
    """Bound channel opening separately; close only this query channel at expiry."""
    channel = client.get_transport().open_session(timeout=timeout)
    channel.settimeout(timeout)
    expired = threading.Event()
    def expire():
        expired.set()
        channel.close()
    timer = threading.Timer(timeout, expire)
    timer.daemon = True
    timer.start()
    try:
        channel.exec_command(command)
        channel.shutdown_write()
        raw = channel.makefile('rb', -1).read(limit + 1)
        error = channel.makefile_stderr('rb', -1).read(8193)
        code = channel.recv_exit_status()
        a.require(not expired.is_set(), 'READONLY_QUERY_EXEC_DEADLINE')
        a.require(len(raw) <= limit and len(error) <= 8192, 'READONLY_QUERY_OUTPUT_BOUND')
        result = dict(exit_code=code, stdout=raw.decode(errors='replace'), stderr=error.decode(errors='replace'))
        if check and (code != 0 or error):
            failure = RuntimeError('READONLY_QUERY_EXIT_' + str(code))
            failure.query_result = result  # Retained only in the private evidence envelope.
            raise failure
        return result
    except BaseException:
        a.require(not expired.is_set(), 'READONLY_QUERY_EXEC_DEADLINE')
        raise
    finally:
        timer.cancel()
        channel.close()


def public_WA_diagnostic(data):
    queries = data['queries']
    a.require(all(queries[name]['exit_code'] == 0 and not queries[name]['stderr'] for name in ['status', 'log', 'kernel']), 'WA_ESSENTIAL_READ_FAILED')
    states = re.findall(r'^wpa_state=(\S+)\s*$', queries['status']['stdout'], re.M)
    a.require(len(states) == 1 and states[0] in {'DISCONNECTED', 'INACTIVE', 'INTERFACE_DISABLED', 'SCANNING', 'ASSOCIATING', 'ASSOCIATED', '4WAY_HANDSHAKE', 'GROUP_HANDSHAKE', 'COMPLETED'}, 'WA_STATUS_PROTOCOL_INVALID')
    a.require(bool(queries['log']['stdout'] or queries['kernel']['stdout']), 'WA_LOGS_EMPTY_NO_DIAGNOSTIC')
    pattern = r'CTRL-EVENT|deauth.*reason|disassoc.*reason|Authentication with|Trying to associate|Trying to authenticate|Associated with|WPA:.*negotiation completed'
    return dict(WA_identity=data['identity'], observed_wpa_state=states[0],
                WA_readonly={name: result for name, result in queries.items() if name not in ['log', 'kernel', 'radio']},
                private_radio_query_sha256=hashlib.sha256(json.dumps(queries['radio'], sort_keys=True).encode()).hexdigest(),
                WA_authentication_log_lines={name: [line for line in queries[name]['stdout'].splitlines() if re.search(pattern, line, re.I)] for name in ['log', 'kernel']})


def before_deadline(client, command, end, check=True):
    remaining = end - time.monotonic()
    a.require(remaining > 0, 'DIAGNOSTIC_PHASE_DEADLINE')
    result = readonly_command(client, command, timeout=min(6, remaining / 2), check=check)
    a.require(time.monotonic() < end, 'DIAGNOSTIC_PHASE_DEADLINE')
    return result


def subscribe_WA(ap):
    channel = ap.get_transport().open_session(timeout=6)
    channel.settimeout(6)
    timer = threading.Timer(6, channel.close); timer.daemon = True
    timer.start()
    try:
        channel.exec_command("set -eu\nprintf 'FMX_LISTENER_OWNED %s %s\\n' \"$$\" \"$(awk '{print $22}' /proc/$$/stat)\"\nexec ubus -t 90 subscribe hostapd.phy0-ap0")
        first = bytearray()
        while not first.endswith(b'\n'):
            chunk = channel.recv(1)
            a.require(bool(chunk) and len(first) < 128, 'DIAGNOSTIC_LISTENER_ID_PROTOCOL')
            first.extend(chunk)
        identity = first.decode().split()
        a.require(len(identity) == 3 and identity[0] == 'FMX_LISTENER_OWNED' and all(value.isdigit() and int(value) > 0 for value in identity[1:]), 'DIAGNOSTIC_LISTENER_ID_PROTOCOL')
        a.require(not channel.closed, 'DIAGNOSTIC_LISTENER_START_DEADLINE')
        return channel, identity[1], identity[2]
    except BaseException:
        channel.close()
        raise
    finally:
        timer.cancel()


def acquire_secure_WA(ap, helper, rec, data, save):
    # Reuse the successful initial admission recipe, without CPE commands.
    readonly_command(ap, 'set -eu\nwifi down radio0\nuci revert wireless.default_radio0.encryption\nwifi up radio0\n', timeout=20)
    end = time.monotonic() + 20
    while time.monotonic() < end:
        state = json.loads(before_deadline(ap, 'ubus call network.wireless status', end)['stdout'])
        if state.get('radio0', {}).get('up'):
            ready = helper.readiness(before_deadline(ap, 'iw dev', end)['stdout'],
                                     before_deadline(ap, 'iw reg get', end)['stdout'],
                                     before_deadline(ap, 'iw phy phy0 info', end)['stdout'], state)
            rec['secure_AP_ready'] = ready; save(); break
        time.sleep(.2)
    else:
        raise RuntimeError('SECURE_AP_READY_DEADLINE')
    source = (HERE.parent.parent / 'tools/bench/preprod1_admitter.sh').read_text(encoding='utf8')
    elements = re.findall(r'^IE=([0-9a-f]+)$', source, re.M)
    a.require(len(elements) == 1 and len(bytes.fromhex(elements[0])) == 60, 'EXACT_60_BYTE_IE_REQUIRED')
    listener, pid, ticks = subscribe_WA(ap)
    rec['discovery_listener_id'] = dict(pid=pid, ticks=ticks)
    transcript = bytearray(); buffer = ''; decoder = json.JSONDecoder()
    cleared = False; end = time.monotonic() + 90
    rec['WA_discovery_events'] = []
    try:
        rec['WA_discovery_set'] = before_deadline(ap, 'set -eu\nubus -t 4 call hostapd.phy0-ap0 set_vendor_elements ' + shlex.quote(json.dumps({'vendor_elements': elements[0]})) + '\nubus -t 4 call hostapd.phy0-ap0 update_beacon', end)
        save()
        while time.monotonic() < end:
            a.require(not listener.closed and not listener.recv_stderr_ready(), 'DIAGNOSTIC_LISTENER_FAILED')
            while listener.recv_ready():
                chunk = listener.recv(8192)
                a.require(bool(chunk), 'DIAGNOSTIC_LISTENER_EOF')
                transcript.extend(chunk); buffer += chunk.decode()
                a.require(len(transcript) <= 262144, 'DIAGNOSTIC_EVENT_OUTPUT_BOUND')
            while buffer.strip():
                buffer = buffer.lstrip()
                try:
                    value, used = decoder.raw_decode(buffer)
                except json.JSONDecodeError:
                    break
                buffer = buffer[used:]
                probe = value.get('probe', {})
                if probe.get('address') == 'fc:ec:da:c2:54:0a':
                    rec['WA_discovery_events'].append(dict(mono=time.monotonic(), value=value))
                    if not cleared and probe.get('target') == 'ff:ff:ff:ff:ff:ff':
                        a.require(probe.get('freq') == 5180 and probe.get('ifname') == 'phy0-ap0', 'WA_PROBE_CONTEXT_CHANGED')
                        time.sleep(.5)
                        rec['WA_discovery_clear'] = before_deadline(ap, 'set -eu\nubus -t 4 call hostapd.phy0-ap0 set_vendor_elements \'{"vendor_elements":""}\'\nubus -t 4 call hostapd.phy0-ap0 update_beacon', end)
                        cleared = True
            a.require(len(buffer) < 8192, 'DIAGNOSTIC_PARTIAL_EVENT_BOUND')
            row = json.loads(before_deadline(ap, 'ubus -t 4 call hostapd.phy0-ap0 get_clients', end)['stdout']).get('clients', {}).get('fc:ec:da:c2:54:0a', {})
            rec['WA_AP_flags'] = row; save()
            if cleared and all(row.get(flag) is True for flag in ['auth', 'assoc', 'authorized', 'wds']):
                rec['WA_secure_authorized'] = True
                return
            time.sleep(.2)
        raise RuntimeError('WA_SECURE_DIAGNOSTIC_ADMISSION_DEADLINE')
    finally:
        data['AP_discovery_stream'] = transcript.decode(errors='replace')
        listener.close()


def finish_discovery_listener(ap, identity):
    pid, ticks = identity['pid'], identity['ticks']
    a.require(all(value.isdigit() and int(value) > 0 for value in [pid, ticks]), 'LISTENER_ID_CHANGED')
    command = 'set -eu\np=' + pid + '; s=' + ticks + '\n'
    command += '''if test -r /proc/$p/stat && test "$(awk '{print $22}' /proc/$p/stat)" = "$s" && test "$(awk '{print $3}' /proc/$p/stat)" != Z; then kill -TERM "$p"; fi
for n in 1 2 3 4 5; do
 if test ! -r /proc/$p/stat || test "$(awk '{print $22}' /proc/$p/stat)" != "$s" || test "$(awk '{print $3}' /proc/$p/stat)" = Z; then echo LISTENER_ENDED; exit 0; fi
 sleep 1
done
exit 79
'''
    result = readonly_command(ap, command, timeout=8)
    a.require(result['stdout'].strip() == 'LISTENER_ENDED', 'LISTENER_END_PROTOCOL')
    return result


def main(label):
    a.require(re.fullmatch(r'[A-Za-z0-9_-]+', label) is not None, 'INVALID_DIAGNOSTIC_LABEL')
    planpath = HERE / ('preprod1_plan_' + label + '.json')
    plan = json.loads(planpath.read_text(encoding='utf8'))
    a.require(plan['frozen'] and plan['production_access_permitted'] is False, 'SCOPE_NOT_FROZEN')
    for name, digest in plan['source_bindings'].items():
        a.require(sha(HERE.parent.parent / name) == digest, 'SOURCE_CHANGED_' + name)
    review = json.loads((HERE / plan['review_file']).read_text(encoding='utf8'))
    a.require(review['status'].startswith('PASS') and review['plan_sha256'] == sha(planpath)
              and review['source_bindings'] == plan['source_bindings'], 'REVIEW_NOT_BOUND')
    out = HERE / ('preprod1_' + label)
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
        acquire_secure_WA(ap, helper, rec, data, save)
        end = time.monotonic() + 45
        rec['WA_radio_probes'] = []
        while time.monotonic() < end:
            remaining = end - time.monotonic()
            a.require(remaining > 0, 'WA_READONLY_RF_PATH_DEADLINE')
            result = readonly_command(ap, 'ping -6 -c 1 -W 1 -I br-lan fe80::feec:daff:fec2:540a', check=False, timeout=min(4, remaining / 2))
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
        identity = readonly_command(wa, probe.IDENTITY)
        a.require('board.sysid=0xe7fa' in identity['stdout'].lower() and 'fcecda' in identity['stdout'].replace(':', '').lower(), 'WA_IDENTITY_MISMATCH')
        data['identity'] = identity
        data['bridge_MAC'] = readonly_command(wa, 'cat /sys/class/net/br0/address')
        a.require(data['bridge_MAC']['stdout'].strip().lower() == 'fc:ec:da:c2:54:0a', 'WA_EXACT_MAC_MISMATCH')
        queries = {'status': 'wpa_cli -i ath0 status', 'radio': 'iwconfig ath0',
                   'bss': 'wpa_cli -i ath0 bss 18:e8:29:74:55:a2',
                   'log': 'logread | tail -n 400', 'kernel': 'dmesg | tail -n 150',
                   'uptime': 'cat /proc/uptime',
                   'hashes': 'md5sum /tmp/system.cfg /tmp/running.cfg /etc/wpasupplicant_AUTO.conf'}
        before = readonly_command(wa, queries['hashes'])
        data['queries'] = {name: readonly_command(wa, command, check=False) for name, command in queries.items()}
        after = readonly_command(wa, queries['hashes'])
        a.require(before == after, 'READONLY_WA_CONFIG_HASH_CHANGED')
        rec['WA_readonly_hashes_unchanged'] = True
        rec.update(public_WA_diagnostic(data))
        rec['diagnostic_acquired'] = True
    except BaseException as exc:
        if hasattr(exc, 'query_result'):
            data['failed_query_result'] = exc.query_result
        rec['failures'].append(dict(type=type(exc).__name__, gate=str(exc)[:160]))
    finally:
        if wa is not None:
            try:
                wa.close()
            except BaseException as exc:
                rec['cleanup_errors'].append(dict(stage='WA_close', type=type(exc).__name__))
        if ap is not None and rec.get('discovery_listener_id'):
            try:
                rec['discovery_listener_ended'] = finish_discovery_listener(ap, rec['discovery_listener_id'])
            except BaseException as exc:
                if hasattr(exc, 'query_result'):
                    data['failed_listener_end_query_result'] = exc.query_result
                rec['cleanup_errors'].append(dict(stage='listener_end', type=type(exc).__name__, gate=str(exc)[:100]))
        try:
            private = HERE / 'preprod_guarida_20261022/history'
            private.mkdir(exist_ok=True)
            rawpath = private / ('preprod1_' + label + '_private_raw.json')
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
            try:
                ap.close()
            except BaseException as exc:
                rec['cleanup_errors'].append(dict(stage='AP_close', type=type(exc).__name__))
        passed = rec.get('diagnostic_acquired') and rec.get('discovery_listener_ended') and rec.get('AP_restoration', {}).get('guard_ended_verified') and not rec['failures'] and not rec['cleanup_errors']
        rec.update(status='PASS_READONLY_WA_DIAGNOSTIC_AP_RESTORED' if passed else 'INCOMPLETE_READONLY_DIAGNOSTIC_PRESERVED', ended_utc=utc(), exit_code=0 if passed else 1)
        save()
    print(json.dumps(rec, indent=2))
    return rec['exit_code']


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != '--execute':
        raise SystemExit('PLAN_ONLY: --execute LABEL and a bound independent review required')
    raise SystemExit(main(sys.argv[2]))
