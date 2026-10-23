"""Bounded, operator-authorized stock WA/XC two-client RAM trial. No flash."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import sys
import time
from datetime import datetime, timezone

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
WA = 'fc:ec:da:c2:54:0a'
XC = 'b4:fb:e4:5c:d5:d2'
LL = {WA: 'fe80::feec:daff:fec2:540a', XC: 'fe80::b6fb:e4ff:fe5c:d5d2'}
CFG = 'c2d90e1e0dfa5b44cb0e2700b2ccd27f'
AUTO = '6cad92c5c89b6c3d19fbaa80d9d8fa04'
HASH_FILES = '/tmp/system.cfg /tmp/running.cfg /etc/wpasupplicant_AUTO.conf /lib/modules/2.6.32.68/ubnt_poll_host.ko /lib/modules/2.6.32.68/umac.ko /dev/mtdblock0 /dev/mtdblock1 /dev/mtdblock4 /dev/mtdblock5'
utc = lambda: datetime.now(timezone.utc).isoformat()
sha = lambda b: hashlib.sha256(b).hexdigest()


def require(ok, gate):
    if not ok:
        raise RuntimeError(gate)


def load(name):
    spec = importlib.util.spec_from_file_location('_multi_' + name.removesuffix('.py'), HERE / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def remote(client, command, timeout=15, check=True, limit=65536):
    i, o, e = client.exec_command(command, timeout=timeout)
    i.close()
    try:
        data, err = o.read(limit + 1), e.read(8193)
        code = o.channel.recv_exit_status()
        require(len(data) <= limit and len(err) <= 8192, 'OUTPUT_BOUND')
        if check:
            require(code == 0 and not err, 'REMOTE_EXIT_' + str(code) + '_' + err.decode(errors='replace')[:100])
        return dict(exit_code=code, stdout=data.decode(errors='replace'), stderr=err.decode(errors='replace'))
    finally:
        o.channel.close()


def ping_ok(result):
    m = re.search(r'(\d+) packets transmitted, (\d+) (?:packets )?received', result['stdout'])
    return result['exit_code'] == 0 and m is not None and int(m[1]) > 0 and m[1] == m[2]


def rocket_guard():
    # The entire rollback program remains an inline shell process; no remote
    # regular file is created. Original matching rules must be absent at intake.
    return r'''set -eu
trap '' HUP
one=0; two=0; restore=0
cleanup() {
 trap - EXIT USR1 TERM INT
 set +e
 wpa_cli -i ath0 reconfigure
 rc=$?
 test "$one" = 0 || ebtables -D FORWARD -i ath0 -o eth0 -j DROP || rc=91
 test "$two" = 0 || ebtables -D FORWARD -i eth0 -o ath0 -j DROP || rc=92
 sleep 2
 primary=$(ip -4 addr show dev br0 | awk '/inet /{print $2;exit}')
 if test "$primary" = 169.254.213.210/16; then
  if ip -4 addr show dev br0 | grep -q 'inet 192.168.100.198/24'; then
   ip -4 addr del 169.254.213.210/16 dev br0 || rc=93
   ip -4 addr add 169.254.213.210/16 brd 169.254.255.255 dev br0 || rc=94
  else rc=95; fi
 fi
 printf 'ROCKET_RESTORE_RC=%s\n' "$rc"
 exit "$rc"
}
trap cleanup EXIT
trap 'exit 0' USR1 TERM INT
ebtables -I FORWARD -i ath0 -o eth0 -j DROP
one=1
ebtables -I FORWARD -i eth0 -o ath0 -j DROP
two=1
wpa_cli -i ath0 disable_network 0 | grep -q '^OK$'
printf 'READY %s %s\n' "$$" "$(awk '{print $22}' /proc/$$/stat)"
end=$(($(cut -d. -f1 /proc/uptime)+420))
while test "$(cut -d. -f1 /proc/uptime)" -lt "$end"; do sleep 1; done
'''


def run(label):
    out = HERE / ('root_multi_cpe_' + label)
    out.mkdir(mode=0o700, exist_ok=False)
    rec = dict(status='INCOMPLETE', experiment='FMX0015-R18-MULTI-CPE-REPULSE',
               started_utc=utc(), source_sha256=sha(Path(__file__).read_bytes()), samples=[],
               events=[], cleanup_errors=[], remote_regular_file_writes_rocket=False,
               bridge_or_management_ip_changes=False, flash_or_reboot=False,
               acceptance={'stable_seconds': 60, 'repulse_seconds': 2, 'pulse_ping_loss_percent': 0})

    def save():
        p = out / 'receipt.pending'
        p.write_text(json.dumps(rec, indent=2), encoding='utf-8')
        os.replace(p, out / 'receipt.json')

    def artifact(name, value):
        raw = value if isinstance(value, bytes) else json.dumps(value, indent=2).encode()
        with (out / name).open('xb') as f:
            f.write(raw)
        return dict(file=name, bytes=len(raw), sha256=sha(raw))

    ap = rocket = window = guard = listener = None
    streams = []; active_pings = []
    armed = False; guard_identity = None; rules_before = hashes_before = bridge_before = None
    buffer = ''; transcript = bytearray(); listener_errors = bytearray()
    start = time.monotonic(); deadline = start + 310
    decoder = json.JSONDecoder()

    def left():
        v = deadline - time.monotonic()
        require(v > 0, 'WORK_DEADLINE')
        return v

    def events():
        nonlocal buffer
        values = []
        if listener.recv_ready():
            raw = listener.recv(8192); transcript.extend(raw); buffer += raw.decode()
            require(len(transcript) < 262144, 'LISTENER_OUTPUT_BOUND')
        if listener.recv_stderr_ready():
            listener_errors.extend(listener.recv_stderr(4096))
        require(not listener_errors, 'LISTENER_ERROR')
        while buffer.strip():
            buffer = buffer.lstrip(); require(buffer.startswith('{'), 'LISTENER_PROTOCOL')
            try: value, used = decoder.raw_decode(buffer)
            except json.JSONDecodeError: break
            buffer = buffer[used:]
            values.append(value)
            rec['events'].append(dict(utc=utc(), mono=time.monotonic(), value=value))
        return values

    def clients():
        raw = remote(ap, 'ubus call ' + obj + ' get_clients', timeout=min(8, left()))
        value = json.loads(raw['stdout'])
        rec.setdefault('client_observations', []).append(dict(utc=utc(), mono=time.monotonic(), data=value))
        return value.get('clients', {})

    def authorized(row):
        return all(row.get(k) is True for k in ('auth', 'assoc', 'authorized', 'wds'))

    def stations():
        devs = remote(ap, 'iw dev')['stdout']
        names = [interface] + re.findall(r'(?m)^\s*Interface (' + re.escape(interface) + r'\.sta[1-9]\d*)$', devs)
        text = ''.join(remote(ap, 'iw dev ' + name + ' station dump', timeout=min(8, left()))['stdout'] for name in names)
        blocks = re.split(r'(?m)^Station ', text)[1:]
        result = {}
        for block in blocks:
            mac = block.split()[0].lower()
            if mac not in LL: continue
            counts = {}
            for key, pattern in [('connected_seconds', r'connected time:\s*(\d+) seconds'),
                                 ('rx_bytes', r'(?m)^\s*rx bytes:\s*(\d+)\s*$'),
                                 ('tx_bytes', r'(?m)^\s*tx bytes:\s*(\d+)\s*$')]:
                m = re.search(pattern, block); require(m is not None, 'STATION_FIELD_MISSING')
                counts[key] = int(m[1])
            result[mac] = counts
        return result

    def start_ping(mac, seconds, interval=1, require_preflight=True):
        # A WDS child bind is attempted first. Source/route availability is
        # measured rather than assumed from interface creation.
        st = remote(ap, 'iw dev ' + interface + ' station get ' + mac)['stdout']
        m = re.search(r'(?m)^\s*WDS interface:\s*(\S+)', st)
        if m:
            child = m[1]
        else:
            # Hostapd exposes the exact dynamically-created WDS child.
            st = remote(ap, 'hostapd_cli -i ' + interface + ' sta ' + mac, check=False)['stdout']
            m = re.search(r'(?m)^(?:wds_ifname|ifname)=(\S+)', st)
            child = m[1] if m else None
        if child is None:
            devs = remote(ap, 'iw dev')['stdout']
            names = re.findall(r'(?m)^\s*Interface (' + re.escape(interface) + r'\.sta[1-9]\d*)$', devs)
            matches = []
            for name in names:
                dump = remote(ap, 'iw dev ' + name + ' station dump', check=False)
                if re.search(r'(?m)^Station ' + re.escape(mac) + r' ', dump['stdout']):
                    matches.append(name)
            if len(matches) == 1:
                child = matches[0]
        require(child is not None and re.fullmatch(re.escape(interface) + r'\.sta[1-9]\d*', child), 'WDS_CHILD_MAPPING_MISSING')
        preflight = remote(ap, 'ping -6 -c 3 -W 2 -I br-lan ' + LL[mac], check=False, timeout=8)
        rec.setdefault('pre_stream_ping_probes', []).append(dict(mac=mac, result=preflight))
        if not ping_ok(preflight) and require_preflight:
            rec.setdefault('pre_stream_failure_context', []).append(dict(mac=mac, ap=remote(ap,
                'ip -6 neigh show dev br-lan; brctl showmacs br-lan; iw dev ' + child + ' station dump', check=False)))
            raise RuntimeError('PRE_STREAM_PING_FAILED_' + mac)
        count = max(1, int(seconds / interval))
        filt = 'icmp6 and host ' + LL[mac] + ' and (ip6[40] == 128 or ip6[40] == 129)'
        capcmd = 'exec tcpdump -p -n -l -tt -s 128 -c ' + str(count * 2) + ' -i ' + child + ' ' + shlex.quote(filt)
        cap = ap.exec_command(capcmd, timeout=min(seconds + 15, left()))
        cap[0].close(); streams.append(cap)
        time.sleep(.25)
        if cap[1].channel.exit_status_ready():
            rec.setdefault('capture_start_failures', []).append(dict(mac=mac, stdout=cap[1].read().decode(), stderr=cap[2].read().decode(), exit_code=cap[1].channel.recv_exit_status()))
            raise RuntimeError('WDS_CAPTURE_START_FAILED')
        cmd = 'exec ping -6 -c ' + str(count) + ' -i ' + str(interval) + ' -W 1 -I br-lan ' + LL[mac]
        stream = ap.exec_command(cmd, timeout=min(seconds + 5, left()))
        stream[0].close(); streams.append(stream); active_pings.append((mac, stream, child, cap, count))
        return (mac, stream, child, cap, count)

    def finish_ping(item, name):
        mac, stream, child, cap, count = item
        data, err = stream[1].read(65537), stream[2].read(8193)
        rc = stream[1].channel.recv_exit_status()
        result = dict(exit_code=rc, stdout=data.decode(errors='replace'), stderr=err.decode(errors='replace'), mac=mac, child=child)
        capdata, caperr = bytearray(), bytearray()
        cap_end = time.monotonic() + 3
        ch = cap[1].channel
        while time.monotonic() < cap_end:
            while ch.recv_ready(): capdata.extend(ch.recv(4096))
            while ch.recv_stderr_ready(): caperr.extend(ch.recv_stderr(4096))
            require(len(capdata) <= 65536 and len(caperr) <= 8192, 'CAPTURE_OUTPUT_BOUND')
            if ch.exit_status_ready() and not ch.recv_ready(): break
            time.sleep(.05)
        caprc = ch.recv_exit_status() if ch.exit_status_ready() else None
        captext = capdata.decode(errors='replace')
        requests = re.findall(r'ICMP6, echo request, id (\d+), seq (\d+)', captext)
        replies = re.findall(r'ICMP6, echo reply, id (\d+), seq (\d+)', captext)
        matched = set(requests) & set(replies)
        path_ok = caprc == 0 and len(requests) == count and len(replies) == count and len(matched) == count
        result['wireless_capture'] = dict(child=child, exit_code=caprc, requests=len(requests), replies=len(replies),
            matched_request_reply_pairs=len(matched), expected=count, path_verified=path_ok,
            artifact=artifact(name + '_wds_capture.json', dict(stdout=captext, stderr=caperr.decode(errors='replace'))))
        rec[name] = artifact(name + '.json', result)
        rec[name + '_pass'] = ping_ok(result) and path_ok
        return ping_ok(result) and path_ok

    try:
        save()
        ap = load('root_goal_direct_link_connection_20261022.py').ap_client()
        rocket = load('root_step1c_rocket_observer_20261021.py').connect()
        hashes_before = remote(rocket, 'md5sum ' + HASH_FILES)['stdout']
        require(hashes_before.splitlines()[0].split()[0] == CFG and hashes_before.splitlines()[1].split()[0] == CFG
                and hashes_before.splitlines()[2].split()[0] == AUTO, 'ROCKET_BASELINE_CHANGED')
        bridge_before = remote(rocket, 'brctl show; ifconfig br0 | head -n 4')['stdout']
        addresses_before = remote(rocket, 'ip -4 addr show dev br0; route -n')['stdout']
        require(re.findall(r'inet ([0-9./]+)', addresses_before) == ['192.168.100.198/24', '169.254.213.210/16'], 'ROCKET_IPV4_BASELINE_CHANGED')
        rec['rocket_addresses_before'] = addresses_before
        rules_before = remote(rocket, 'ebtables -L FORWARD')['stdout']
        require(not re.search(r'-i (?:ath0 -o eth0|eth0 -o ath0) -j DROP', rules_before), 'MATCHING_BASELINE_RULE_EXISTS')
        rec['rocket_baseline'] = dict(hashes=hashes_before, bridge=bridge_before, rules=rules_before)
        guard = rocket.exec_command('exec /bin/sh -c ' + shlex.quote(rocket_guard()), timeout=8)
        guard[0].close(); streams.append(guard)
        line = guard[1].readline().strip()
        require(re.fullmatch(r'READY \d+ \d+', line), 'ROCKET_GUARD_NOT_READY_' + line[:80])
        guard_identity = line.split()[1:]; rec['rocket_guard'] = dict(pid=int(guard_identity[0]), start=int(guard_identity[1]), ttl=420)
        profile = [('ssid', '"FuturaMAX-LAB"'), ('psk', '"FuturaMAX2026"'), ('key_mgmt', 'WPA-PSK'),
                   ('proto', 'RSN'), ('pairwise', 'CCMP'), ('group', 'CCMP'), ('scan_freq', '5180')]
        for key, value in profile:
            r = remote(rocket, 'wpa_cli -i ath0 set_network 0 ' + key + ' ' + shlex.quote(value))
            require(r['stdout'].strip() == 'OK', 'WPA_SET_FAILED_' + key)
        rec['rocket_profile'] = dict(volatile=True, parameters=[k for k, _ in profile], state='DISABLED_UNTIL_LATE_PULSE')
        ie = load('root_multi_cpe_ie_window_20261022.py'); window = ie.Window()
        window.ap.NATIVE = HERE / 'root_goal_direct_link_cycle_20261022_native_install/receipt.json'
        window.ap.NATIVE_SHA = 'ff6fdbac93c279ad55468e0165767de0f05dddd79db21c7bd3ce1f38a1ac0f92'
        require(sha(window.ap.NATIVE.read_bytes()) == window.ap.NATIVE_SHA, 'CURRENT_NATIVE_RECEIPT_CHANGED')
        rec['bindings'] = {name: sha((HERE / name).read_bytes()) for name in ['root_multi_cpe_ie_window_20261022.py', 'root_multi_cpe_ap_window_20261022.py']}
        ready = window.arm(ap); armed = True; rec['ap_ready'] = ready
        interface = ready['interface']; obj = shlex.quote('hostapd.' + interface)
        sub = ap.exec_command('exec ubus -t 330 subscribe ' + obj, timeout=8)
        sub[0].close(); streams.append(sub); listener = sub[1].channel
        rec['discovery'] = window.phase(ap, 'WA_initial_discovery', True); save()
        cleared = False; wa_end = min(deadline, time.monotonic() + 90)
        while time.monotonic() < wa_end:
            for value in events():
                p = value.get('probe', {})
                if not cleared and p.get('address') == WA and p.get('target') == 'ff:ff:ff:ff:ff:ff':
                    require(p.get('freq') == 5180 and p.get('ifname') == interface, 'WA_PROBE_CONTEXT')
                    seen = time.monotonic(); time.sleep(.5); window.set_elements(ap, '')
                    cleared = True
                    rec['WA_initial_clear'] = dict(probe=p, seen_mono=seen, clear_ack_mono=time.monotonic())
            if cleared and authorized(clients().get(WA, {})): break
            time.sleep(.2)
        require(cleared and authorized(clients().get(WA, {})), 'WA_NOT_AUTHORIZED_BEFORE_LATE_PULSE')
        rec['WA_before_pulse'] = dict(mono=time.monotonic(), clients=clients(), stations=stations())
        pulse_ping = start_ping(WA, 8, 1)
        time.sleep(1)
        window.set_elements(ap, ie.TRIAL_IE)
        pulse_start = time.monotonic(); pulse_samples = []
        late_enabled = False
        while time.monotonic() < pulse_start + 2:
            if not late_enabled and time.monotonic() >= pulse_start + 1.7:
                r = remote(rocket, 'wpa_cli -i ath0 enable_network 0; wpa_cli -i ath0 reassociate')
                require(r['stdout'].split() == ['OK', 'OK'], 'ROCKET_LATE_ENABLE_FAILED')
                late_enabled = True
                rec['XC_late_enable_mono'] = time.monotonic()
            events(); pulse_samples.append(dict(mono=time.monotonic(), clients=clients()))
            time.sleep(min(.1, max(0, pulse_start + 2 - time.monotonic())))
        window.set_elements(ap, '')
        require(late_enabled, 'LATE_ENABLE_WINDOW_MISSED')
        pulse_clear = time.monotonic()
        rec['repulse'] = dict(start_mono=pulse_start, clear_ack_mono=pulse_clear, duration_api_ack_seconds=pulse_clear-pulse_start,
                              requested_seconds=2, client_samples=pulse_samples, ota_duration_qualified=False)
        rec['WA_after_pulse'] = dict(mono=time.monotonic(), clients=clients(), stations=stations())
        rec['pulse_ping_ok'] = finish_ping(pulse_ping, 'WA_pulse_ping')
        before = rec['WA_before_pulse']['stations'][WA]['connected_seconds']
        after = rec['WA_after_pulse']['stations'].get(WA, {}).get('connected_seconds', -1)
        disconnect_events = [e for e in rec['events'] if e['mono'] >= pulse_start and any(
            k in e['value'] and e['value'][k].get('address') == WA for k in ('deauth', 'disassoc'))]
        rec['WA_survived_repulse'] = bool(rec['pulse_ping_ok'] and after >= before
            and authorized(rec['WA_after_pulse']['clients'].get(WA, {}))
            and all(authorized(s['clients'].get(WA, {})) for s in pulse_samples) and not disconnect_events)
        save()
        xc_end = min(deadline - 85, time.monotonic() + 85)
        while time.monotonic() < xc_end:
            events(); rows = clients()
            if all(authorized(rows.get(mac, {})) for mac in (WA, XC)): break
            time.sleep(.5)
        require(all(authorized(clients().get(mac, {})) for mac in (WA, XC)), 'DUAL_AUTHORIZATION_NOT_REACHED')
        window.snapshot(ap)
        stable_start = time.monotonic(); first = stations(); previous = first
        pings = [start_ping(mac, 64, 1, require_preflight=False) for mac in (WA, XC)]
        while True:
            events(); rows = clients(); counts = stations(); now = time.monotonic()
            require(all(authorized(rows.get(mac, {})) for mac in (WA, XC)), 'SIMULTANEOUS_AUTHORIZATION_LOST')
            for mac in (WA, XC):
                require(mac in counts and all(counts[mac][k] >= previous[mac][k] for k in counts[mac]), 'STATION_COUNTER_RESET')
            rec['samples'].append(dict(mono=now, utc=utc(), clients=rows, stations=counts))
            previous = counts; save()
            if now - stable_start >= 60: break
            time.sleep(min(1, left()))
        rec['stability_seconds'] = now - stable_start
        rec['simultaneous_WPA2_WDS_60s_pass'] = True
        rec['dual_ping_ok'] = all([finish_ping(p, 'dual_ping_' + ('WA' if p[0] == WA else 'XC')) for p in pings])
        rec['wireless_counters_advanced'] = all(previous[mac]['rx_bytes'] > first[mac]['rx_bytes'] and previous[mac]['tx_bytes'] > first[mac]['tx_bytes'] for mac in (WA, XC))
        rec['normal_AP_dual_association_pass'] = rec['dual_ping_ok'] and rec['wireless_counters_advanced']
        rec['rocket_end_status'] = remote(rocket, 'wpa_cli -i ath0 status; iwconfig ath0; md5sum ' + HASH_FILES)['stdout']
    except BaseException as e:
        rec['failure'] = dict(type=type(e).__name__, gate=str(e)[:180])
    finally:
        if listener is not None:
            try: events()
            except Exception: pass
        rec['listener_transcript'] = artifact('hostapd_events.jsonl', bytes(transcript))
        if window is not None and armed:
            try: rec['ap_restoration'] = window.restore(ap)
            except BaseException as e: rec['cleanup_errors'].append('AP:' + str(e)[:150])
        elif window is not None and window.restoration:
            rec['ap_restoration'] = window.restoration
        if rocket is not None and guard_identity is not None:
            try:
                pid, ticks = guard_identity
                r = remote(rocket, 'set -eu\ntest "$(awk \'{print $22}\' /proc/' + pid + '/stat)" = ' + ticks + '\nkill -USR1 ' + pid)
                guard[1].channel.settimeout(12)
                data, err = guard[1].read(8193), guard[2].read(8193)
                rc = guard[1].channel.recv_exit_status()
                require(rc == 0 and not err and b'ROCKET_RESTORE_RC=0' in data, 'ROCKET_GUARD_RESTORE_FAILED')
                hashes_after = remote(rocket, 'md5sum ' + HASH_FILES)['stdout']
                rules_after = remote(rocket, 'ebtables -L FORWARD')['stdout']
                bridge_after = remote(rocket, 'brctl show; ifconfig br0 | head -n 4')['stdout']
                status = remote(rocket, 'wpa_cli -i ath0 list_networks; wpa_cli -i ath0 status')['stdout']
                addresses_after = remote(rocket, 'ip -4 addr show dev br0; route -n')['stdout']
                rec['rocket_addresses_after'] = addresses_after
                require(hashes_after == hashes_before and rules_after == rules_before and bridge_after == bridge_before
                        and addresses_after == addresses_before, 'ROCKET_EXACT_RESTORE_CHANGED')
                require('\tubnt\t' in status and 'FuturaMAX-LAB' not in status, 'ROCKET_PROFILE_NOT_RECONFIGURED')
                rec['rocket_restoration'] = dict(status='PASS_EXACT_HASHES_RULES_BRIDGE_WPA_RECONFIGURED', hashes=hashes_after,
                                                  rules=rules_after, wpa=status, guard_ended=True)
            except BaseException as e: rec['cleanup_errors'].append('Rocket:' + str(e)[:150])
        for s in streams:
            for f in s:
                try: f.close()
                except Exception: pass
        for c in (ap, rocket):
            if c: c.close()
        passed = bool(rec.get('normal_AP_dual_association_pass') and rec.get('WA_survived_repulse')
                      and rec.get('ap_restoration', {}).get('status') == 'PASS_RAM_WINDOW_RESTORED_RADIO_OFF'
                      and rec.get('rocket_restoration', {}).get('guard_ended') and not rec['cleanup_errors'] and not rec.get('failure'))
        rec.update(status='PASS_MULTI_CPE_REPULSE_60S_RESTORED' if passed else 'INCOMPLETE_MULTI_CPE_PRESERVED', ended_utc=utc(), exit_code=0 if passed else 1)
        save()
    print(json.dumps({k: rec.get(k) for k in ['status', 'failure', 'WA_survived_repulse', 'stability_seconds', 'cleanup_errors', 'ap_restoration', 'rocket_restoration']}, indent=2), flush=True)
    return rec['exit_code']


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--execute':
        raise SystemExit(run(sys.argv[2]))
    print('PLAN_ONLY: --execute requires unique local evidence-directory label')
