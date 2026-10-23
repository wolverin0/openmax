"""Recovery only for interrupted run5aa; no experiment, production or flash."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import threading
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
OUT = HERE / 'preprod1_r5aa_abort_restore_20261022.json'
RUN = HERE / 'preprod1_20261022_run5aa'
utc = lambda: datetime.now(timezone.utc).isoformat()
sha = lambda b: hashlib.sha256(b).hexdigest()
record = dict(status='INCOMPLETE_ABORT_RESTORATION', started_utc=utc(),
              source_sha256=sha(Path(__file__).read_bytes()), events=[], errors=[],
              production_access=False, experiment_acquisition=False)


def save():
    temp = OUT.with_suffix('.pending')
    temp.write_text(json.dumps(record, indent=2), encoding='utf8')
    temp.replace(OUT)


def require(ok, gate):
    if not ok:
        raise RuntimeError(gate)


def load(name):
    spec = importlib.util.spec_from_file_location('_aa_restore_' + name[:-3], HERE / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def remote(client, command, timeout=15, check=True, limit=65536):
    started = time.monotonic()
    channel = client.get_transport().open_session(timeout=timeout)
    expired = threading.Event()

    def expire():
        expired.set()
        channel.close()

    timer = threading.Timer(max(.001, timeout - (time.monotonic() - started)), expire)
    timer.daemon = True
    timer.start()
    try:
        channel.settimeout(max(.001, timeout - (time.monotonic() - started)))
        channel.exec_command(command)
        channel.shutdown_write()
        out, err = bytearray(), bytearray()
        while True:
            require(not expired.is_set(), 'OWN_CHANNEL_ABSOLUTE_DEADLINE')
            if channel.recv_ready():
                out.extend(channel.recv(min(4096, limit + 1 - len(out))))
            if channel.recv_stderr_ready():
                err.extend(channel.recv_stderr(min(4096, 8193 - len(err))))
            require(len(out) <= limit and len(err) <= 8192, 'OUTPUT_BOUND')
            if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready():
                rc = channel.recv_exit_status()
                break
            time.sleep(.01)
        require(not expired.is_set(), 'OWN_CHANNEL_ABSOLUTE_DEADLINE')
        if check:
            require(rc == 0 and not err, 'REMOTE_EXIT_' + str(rc) + '_' + err.decode(errors='replace')[:120])
        return dict(exit_code=rc, stdout=out.decode(errors='replace'), stderr=err.decode(errors='replace'))
    finally:
        timer.cancel()
        channel.close()


def main():
    require(not OUT.exists(), 'RESTORE_RECEIPT_EXISTS')
    rec = json.loads((RUN / 'receipt.json').read_text(encoding='utf8'))
    require(rec.get('ended_utc') is None and not rec['samples'] and not rec.get('daemon_dir'), 'AA_NOT_PREWINDOW_ABORT')
    record['interrupted_receipt_sha256'] = sha((RUN / 'receipt.json').read_bytes())
    record['reason'] = 'Host interrupted after EXEC-ACK hang at arm_legacy LBM5 readiness; no finally or admission.'
    access = load('root_four_cpe_access_20261022.py')
    access.remote = remote
    helper = access.ap_helper()
    helper.TOKEN = rec['bridge_isolation']['owner']
    helper.DIR = rec['AP_initial']['remote_ram']
    helper.checked = lambda c, cmd, timeout=25: remote(c, cmd, timeout=timeout)['stdout'].encode()
    # Validate against the exact archived scripts, including the owned nft cleanup.
    guard = (RUN / 'executed-source/AP_guard.sh').read_text(encoding='utf8').encode()
    restore = (RUN / 'executed-source/AP_restore.sh').read_text(encoding='utf8').encode()
    helper.file_guards = lambda: ('test ! -L "$D/guard.sh"; test ! -L "$D/restore.sh"\n'
                                'test "$(sha256sum "$D/guard.sh" | cut -d\' \' -f1)" = ' + sha(guard) + '\n'
                                'test "$(sha256sum "$D/restore.sh" | cut -d\' \' -f1)" = ' + sha(restore) + '\n')
    ap = rocket = None
    try:
        save()
        ap = access.load('root_goal_direct_link_connection_20261022.py').ap_client()
        helper.identity(ap)
        record['AP_guard_precheck'] = remote(ap, 'set -eu\n' + helper.header() + helper.file_guards() +
            'cat "$D/guard.id" "$D/deadline"; cat /proc/uptime\n')
        # The two preflight traces were staged but never started. Inventory only;
        # removal is performed later against exact captured inode/token/hash.
        inventory = remote(ap, "set -eu\nfor d in /tmp/fmx-assoc-debug-*; do\n"
            ' test -d "$d" || continue\n test ! -L "$d"\n'
            ' test ! -e "$d/guard.sh"\n test ! -e "$d/disarm"\n'
            ' test "$(ls -A "$d" | sort | tr \'\\n\' \' \')" = "cli owner "\n'
            ' printf "%s|%s|%s|%s|%s\\n" "$d" "$(cat "$d/owner")" '
            '"$(ls -lidn "$d" | awk \'{print $1,$2,$4,$5}\')" '
            '"$(sha256sum "$d/cli" | cut -d\' \' -f1)" "mtime_not_acquired"\ndone\n')
        rows = [x.split('|') for x in inventory['stdout'].splitlines()]
        require(len(rows) == 2, 'EXACT_TWO_UNSTARTED_STAGED_TRACES')
        for d, token, inode, digest, mtime in rows:
            require(re.fullmatch(r'/tmp/fmx-assoc-debug-[0-9a-f]{32}', d) and d.endswith(token), 'STAGED_OWNER_TOKEN')
            require(re.fullmatch(r'[0-9]+ drwx--x--- 0 101', inode), 'STAGED_INODE_MODE')
            require(digest == 'b168f06e135a598e2a61b4c170fd4cd77e58072bf0e5d149c182a177ccb39e52', 'STAGED_CLI_HASH')
        record['unstarted_staged_trace_inventory'] = rows
        save()
        # Restore the secure AP profile in RAM, solely to reach guards that have
        # already applied WPA2. Same channel/width/0dBm; no IE or daemon started.
        remote(ap, 'set -eu\n' + helper.header() + helper.file_guards() +
               'test ! -f "$D/restored"\nwifi down radio0\nuci revert wireless.default_radio0.encryption\nwifi up radio0\n', timeout=25)
        end = time.monotonic() + 45
        while time.monotonic() < end:
            status = json.loads(remote(ap, 'ubus call network.wireless status')['stdout'])
            if status.get('radio0', {}).get('up'):
                record['secure_restore_management_RF'] = helper.readiness(
                    remote(ap, 'iw dev')['stdout'], remote(ap, 'iw reg get')['stdout'],
                    remote(ap, 'iw phy phy0 info')['stdout'], status)
                break
            time.sleep(.3)
        require('secure_restore_management_RF' in record, 'RESTORE_MANAGEMENT_AP_NOT_READY')
        save()
        for name, g in rec['legacy_guards'].items():
            c = None
            try:
                for _ in range(3):
                    try:
                        c, pin = access.connect_legacy(ap, name, json.loads((HERE/'root_four_cpe_intake_20261022_run1/receipt.json').read_text(encoding='utf8'))['devices'][name]['pin'])
                        break
                    except Exception:
                        time.sleep(1)
                require(c is not None, 'RESTORE_LEGACY_CONNECT_' + name)
                d = shlex.quote(g['directory'])
                command = ('set -eu\nD=' + d + '\ntest ! -L "$D"\n'
                    'test "$(sha256sum "$D/guard.sh" | cut -d\' \' -f1)" = ' + g['source_sha256'] + '\n'
                    'read p s < "$D/guard.id"\ntest "$(awk \'{print $22}\' /proc/$p/stat)" = "$s"\n'
                    'test "$(awk \'{print $3}\' /proc/$p/stat)" != Z\n'
                    'test "$(tr \'\\000\' \' \' < /proc/$p/cmdline)" = "/bin/sh $D/guard.sh "\n'
                    'printf "IDENTITY %s %s\\n" "$p" "$s"\nkill -USR1 "$p"\n')
                identity = remote(c, command, timeout=6)
                record['events'].append(dict(device=name, action='owned_guard_USR1', evidence=identity))
            except Exception as error:
                record['events'].append(dict(device=name, action='guard_signal_uncertain_native_fallback', error=type(error).__name__))
            finally:
                if c:
                    c.close()
            save()
        remote(ap, 'set -eu\n' + helper.header() + helper.file_guards() +
               'test ! -f "$D/restored"\nwifi down radio0\nuci set wireless.default_radio0.encryption=none\nwifi up radio0\n', timeout=25)
        record['open_restore_management_ready'] = True
        save()
        # Match the original validation, then remove only that ended guard RAM.
        restored = set()
        end = time.monotonic() + 620
        intake = json.loads((HERE/'root_four_cpe_intake_20261022_run1/receipt.json').read_text(encoding='utf8'))
        while time.monotonic() < end and len(restored) != 2:
            for name, g in rec['legacy_guards'].items():
                if name in restored:
                    continue
                c = None
                try:
                    address = access.DEVICES[name][0]
                    if remote(ap, 'ping -c 1 -W 1 -I br-lan ' + address, timeout=3, check=False)['exit_code']:
                        continue
                    c, _ = access.connect_legacy(ap, name, intake['devices'][name]['pin'])
                    d = shlex.quote(g['directory'])
                    identity = remote(c, 'set -eu\nD='+d+'\ntest -f "$D/restored"\ntest "$(cat "$D/restore.rc")" = 0\ncat "$D/guard.id"\n')['stdout'].split()
                    require(len(identity)==2 and all(x.isdigit() for x in identity), 'LEGACY_RESTORE_ID')
                    pid, ticks = identity
                    require(remote(c, 'if test -r /proc/'+pid+'/stat && test "$(awk \'{print $22}\' /proc/'+pid+'/stat)" = '+ticks+' && test "$(awk \'{print $3}\' /proc/'+pid+'/stat)" != Z; then echo LIVE; else echo ENDED; fi')['stdout'].strip()=='ENDED', 'LEGACY_GUARD_LIVE')
                    command = ('cat /proc/sys/kernel/random/boot_id; sha256sum /etc/config/wireless; md5sum /dev/mtd0 /dev/mtd3 /dev/mtd4 /dev/mtd5 /dev/mtd6 /dev/mtd7 /dev/mtd8; ip -4 addr; ip route; uci changes wireless; iw dev phy0-sta0 link' if name=='SXT' else
                               'cat /proc/sys/kernel/random/boot_id; md5sum /tmp/system.cfg /dev/mtd0 /dev/mtd1 /dev/mtd4 /dev/mtd5; ip -4 addr; ip route; brctl show; iwconfig ath0; iwpriv ath0 get_authmode; iwpriv ath0 get_wds')
                    snapshot = remote(c, command, timeout=25)['stdout']
                    before = rec['legacy_baselines'][name]
                    require(snapshot.splitlines()[0] == before.splitlines()[0], 'LEGACY_BOOT_CHANGED')
                    hashes = lambda t: re.findall(r'(?m)^([0-9a-f]{32,64})\s+(/\S+)$', t)
                    require(hashes(snapshot) == hashes(before), 'LEGACY_HASH_CHANGED')
                    network = lambda t: (re.findall(r'(?m)^\s+inet ([^\n]+)', t), re.findall(r'(?m)^(?:default via|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(?:/[0-9]+)? via|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(?:/[0-9]+)? dev)[^\n]+', t))
                    require(network(snapshot) == network(before), 'LEGACY_NETWORK_CHANGED')
                    if name == 'SXT':
                        require(remote(c,'uci changes wireless')['stdout'].strip()=='' and remote(c,'uci -q get wireless.default_radio0.encryption')['stdout'].strip()=='none', 'SXT_NOT_OPEN')
                    else:
                        require('Encryption key:off' in snapshot and 'get_authmode:1' in snapshot and 'get_wds:0' in snapshot, 'LBM5_NOT_OPEN')
                    command = ('set -eu\nD='+d+'\ntest ! -L "$D"\ntest "$(sha256sum "$D/guard.sh" | cut -d\' \' -f1)" = '+g['source_sha256']+'\n')
                    for file in ['guard.sh','guard.log','guard.id','deadline','ready','applied','restored','restore.rc','client.conf','wpa.id','wpa.log','wpa.stdout','wpa.stderr']:
                        command += 'test ! -L "$D/'+file+'"; rm -f "$D/'+file+'"\n'
                    command += 'rmdir "$D"\ntest ! -e "$D"\necho OWNED_RAM_GUARD_REMOVED\n'
                    cleanup = remote(c, command)
                    record.setdefault('legacy_restoration', {})[name] = dict(status='PASS_OPEN_RF_CONFIG_PROTECTED_HASHES_GUARD_ENDED', snapshot=snapshot, cleanup=cleanup)
                    restored.add(name)
                    save()
                except Exception as error:
                    record.setdefault('last_restore_observation', {})[name] = dict(error_type=type(error).__name__, gate=str(error)[:120])
                finally:
                    if c:
                        c.close()
            if len(restored) != 2:
                time.sleep(1)
        require(len(restored)==2, 'LEGACY_RESTORATION_NOT_CONFIRMED')
        # The interrupted host lost Rocket's stream identity. Select exactly the
        # original inline guard bytes without exporting argv, then signal it.
        rocket = access.load('root_step1c_rocket_observer_20261021.py').connect()
        script = (RUN/'executed-source/Rocket_guard.sh').read_text(encoding='utf8')
        expected = '/bin/sh\n-c\n' + script.rstrip('\n')
        command = ('set -eu\nfound=\nfor p in /proc/[0-9]*; do\n test -r "$p/cmdline" || continue\n'
            ' args=$(tr \'\\000\' \'\\n\' < "$p/cmdline")\n test "$args" = '+shlex.quote(expected)+' || continue\n'
            ' test -z "$found"\n found=${p##*/}\ndone\n'
            'if test -n "$found"; then printf "OWNED_GUARD %s %s\\n" "$found" "$(awk \'{print $22}\' /proc/$found/stat)"; kill -USR1 "$found"; else echo OWNED_GUARD_ALREADY_ENDED; fi\n')
        record['Rocket_guard_signal'] = remote(rocket, command, timeout=12)
        time.sleep(3)
        identity = record['Rocket_guard_signal']['stdout'].split()
        if len(identity)==3 and identity[0]=='OWNED_GUARD':
            pid, ticks = identity[1:]
            require(pid.isdigit() and ticks.isdigit(), 'ROCKET_GUARD_ID')
            record['Rocket_guard_ended'] = remote(rocket, 'if test -r /proc/'+pid+'/stat && test "$(awk \'{print $22}\' /proc/'+pid+'/stat)" = '+ticks+' && test "$(awk \'{print $3}\' /proc/'+pid+'/stat)" != Z; then echo LIVE; else echo ENDED; fi')['stdout'].strip()
            require(record['Rocket_guard_ended']=='ENDED', 'ROCKET_GUARD_STILL_LIVE')
        old = access.load('root_multi_cpe_trial_20261022.py')
        after = {k:remote(rocket, cmd)['stdout'] for k,cmd in {'hashes':'md5sum '+old.HASH_FILES,'bridge':'brctl show; ifconfig br0 | head -n 4','addresses':'ip -4 addr show dev br0; route -n','rules':'ebtables -L FORWARD'}.items()}
        require(after==rec['rocket_baseline'], 'ROCKET_EXACT_RESTORE_CHANGED')
        record['rocket_restoration'] = dict(status='PASS_EXACT_HASHES_RULES_BRIDGE_ORDERED_IPv4_ROUTES', evidence=after)
        # Two staged-only directories have no running listener/guard and contain
        # only this held CLI and owner file; recheck every captured identity.
        for d, token, inode, digest, mtime in rows:
            command = ('set -eu\nd='+shlex.quote(d)+'\ntest ! -L "$d"\n'
                'test "$(ls -lidn "$d" | awk \'{print $1,$2,$4,$5}\')" = '+shlex.quote(inode)+'\n'
                'test "$(cat "$d/owner")" = '+token+'\n'
                'test "$(sha256sum "$d/cli" | cut -d\' \' -f1)" = '+digest+'\n'
                'test "$(ls -A "$d" | sort | tr \'\\n\' \' \')" = "cli owner "\n'
                'test ! -L "$d/cli"; test ! -L "$d/owner"\n'
                'rm "$d/cli" "$d/owner"\nrmdir "$d"\ntest ! -e "$d"\necho STAGED_ONLY_RAM_REMOVED\n')
            record['events'].append(dict(action='staged_only_RAM_cleanup', directory=d, evidence=remote(ap,command)))
        record['AP_restoration'] = helper.restore(ap)
        require(remote(ap, 'nft list tables')['stdout']==rec['bridge_isolation']['original_tables'], 'AP_NFT_NOT_RESTORED')
        command = 'set -eu\n'+helper.header()+helper.file_guards()
        for file in ['owner','ready','guard.id','deadline','guard.sh','restore.sh','guard.log','restore.log','restored']:
            command += 'test ! -L "$D/'+file+'"; rm -f "$D/'+file+'"\n'
        record['AP_guard_RAM_cleanup'] = remote(ap, command+'rmdir "$D"\ntest ! -e "$D"\necho AP_OWNED_RAM_REMOVED\n')
        record['status'] = 'PASS_ABORT_RESTORATION_ALL_BENCH_ORIGINAL_AP_OFF'
    except BaseException as error:
        record['errors'].append(dict(error_type=type(error).__name__, gate=str(error)[:160]))
    finally:
        for c in [rocket, ap]:
            if c:
                c.close()
        record['ended_utc'] = utc()
        save()
    print(json.dumps({k:record[k] for k in ['status','errors','started_utc','ended_utc']}), flush=True)
    return 0 if record['status'].startswith('PASS_') else 1


if __name__ == '__main__':
    raise SystemExit(main())
