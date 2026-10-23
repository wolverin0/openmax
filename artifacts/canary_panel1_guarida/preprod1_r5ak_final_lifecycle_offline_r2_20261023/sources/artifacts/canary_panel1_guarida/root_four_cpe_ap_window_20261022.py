"""One HUP-guarded RAM-only bench AP window; root supplies authenticated client.
Default PLAN_ONLY. No connection/credential code, commit, vendor IE or reboot.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import secrets
import shlex
import time

HERE = Path(__file__).resolve().parent
NATIVE = HERE / 'root_step1c_bench_cycle_20261021_native_install/receipt.json'
NATIVE_SHA = 'ba849665e09ab6f42d99a4b0bf7f2ae9cb74098d5a0a31d5358eb5f5200a841b'
WIFI_SOURCE = HERE / 'root_step1c_candidate_wifi-script_20261021.txt'
WIFI_SHA = '61bc1bbc7e023b01702dc59db143cb98e408e8dd2a2dd69d608cd1422c6b0b7f'
CONFIG_SHA = 'f8e679e4639fc5c26b6c96d646e1e56b57fb58064a75eb215c34ad0462285a6a'
NETWORK_SHA = 'd273ab6bece9a950b119a4fc6c0f6f076543e4a88ab7346760e02d211b403015'
MAC = '18:e8:29:75:55:a2'
TOKEN = secrets.token_hex(16)
DIR = '/tmp/fmx-step1c-ap-observer-' + TOKEN
TTL = 480
_USED = False
sha = lambda value: hashlib.sha256(value).hexdigest()


def require(ok, gate):
    if not ok:
        raise RuntimeError(gate)


def evidence():
    require(sha(NATIVE.read_bytes()) == NATIVE_SHA and sha(WIFI_SOURCE.read_bytes()) == WIFI_SHA, 'LOCAL_EVIDENCE_CHANGED')
    native = json.loads(NATIVE.read_text())
    require(native['status'] == 'PASS_STEP1C_BENCH_FULL_IMAGE_BOOT_RADIO_OFF_OWN_STOCK_RETURN_PENDING'
            and native['after']['radio_disabled_verified'] is True, 'NATIVE_NOT_ACCEPTED')
    return native


def checked(client, command, timeout=25):
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    try:
        stdin.close()
        output, error = stdout.read(65537), stderr.read(65537)
        require(len(output) <= 65536 and len(error) <= 65536, 'OUTPUT_BOUND')
        require(stdout.channel.recv_exit_status() == 0 and not error, 'REMOTE_COMMAND_FAILED')
        return output
    finally:
        stdout.channel.close()


def client_pin(client):
    native = evidence()
    transport = client.get_transport()
    require(transport and transport.is_active() and transport.is_authenticated()
            and sha(transport.get_remote_server_key().asbytes()) == native['after']['ssh_key_sha256'], 'CLIENT_PIN_CHANGED')


def identity(client):
    client_pin(client)
    rows = checked(client, 'cat /sys/class/net/eth0/address; cat /tmp/sysinfo/board_name; uname -r; '
                   'sha256sum /lib/modules/6.6.110/mac80211.ko /etc/config/network /etc/config/wireless /sbin/wifi').decode().splitlines()
    require(rows[:3] == [MAC, 'ubnt,lap-120', '6.6.110'], 'BOARD_CHANGED')
    require(len(rows) == 7 and [r.split()[0] for r in rows[3:]] == [
        '19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416',
        NETWORK_SHA, CONFIG_SHA, sha(WIFI_SOURCE.read_bytes().replace(b'\r\n', b'\n'))], 'RUNTIME_HASH_CHANGED')


def header():
    return ('D=' + shlex.quote(DIR) + '\nTOKEN=' + TOKEN + '\n'
            'test ! -L "$D"; test -d "$D"\n'
            'test "$(ls -ldn "$D" | awk \'{print $1,$3,$4}\')" = "drwx------ 0 0"\n'
            'test ! -L "$D/owner"; test "$(cat "$D/owner")" = "$TOKEN"\n')


def restore_body():
    return ('#!/bin/sh\nset -eu\n' + header() + '''
wifi down radio0
if ! mkdir "$D/restoring"; then
 for n in 1 2 3 4; do test -f "$D/restored" && exit 0; sleep 1; done
 exit 80
fi
trap 'rmdir "$D/restoring"' EXIT
test "$(sha256sum /etc/config/wireless | awk '{print $1}')" = ''' + CONFIG_SHA + '''
test "$(sha256sum /etc/config/network | awk '{print $1}')" = ''' + NETWORK_SHA + '''
changes=$(uci changes wireless)
printf '%s\n' "$changes" | while IFS= read -r row; do
 case "$row" in ""|"wireless.radio0.disabled='0'"|"wireless.radio0.txpower='0'"|"wireless.default_radio0.wds='1'"|"wireless.default_radio0.encryption='none'"|"wireless.default_radio0.encryption='psk2'") ;; *) exit 81;; esac
done
test "$(uci -q get wireless.radio0.disabled)" = 0 -o "$(uci -q get wireless.radio0.disabled)" = 1
test "$(uci -q get wireless.radio0.txpower)" = 0 -o "$(uci -q get wireless.radio0.txpower)" = 18
if printf '%s\n' "$changes" | grep -q "^wireless.radio0.disabled="; then uci revert wireless.radio0.disabled; fi
if printf '%s\n' "$changes" | grep -q "^wireless.radio0.txpower="; then uci revert wireless.radio0.txpower; fi
if printf '%s\n' "$changes" | grep -q "^wireless.default_radio0.wds="; then uci revert wireless.default_radio0.wds; fi
if printf '%s\n' "$changes" | grep -q "^wireless.default_radio0.encryption="; then uci revert wireless.default_radio0.encryption; fi
test -z "$(uci changes wireless)"
test "$(uci -q get wireless.default_radio0.wds)" = 0
test "$(uci -q get wireless.radio0.disabled)" = 1
test "$(uci -q get wireless.radio0.txpower)" = 18
ubus call network reload >/dev/null
wifi down radio0
if ip -4 addr show dev br-lan | grep -q 'inet 10.99.0.1/24 '; then ip addr del 10.99.0.1/24 dev br-lan; fi
if ip -4 addr show dev br-lan | grep -q 'inet 10.99.0.1/'; then exit 82; fi
test "$(sha256sum /etc/config/wireless | awk '{print $1}')" = ''' + CONFIG_SHA + '''
: > "$D/restored"
echo RESTORE_OK
''')


def guard_body():
    return ('#!/bin/sh\ntrap \'\' HUP\nset -eu\n' + header() + '''
printf '%s %s\n' "$$" "$(awk '{print $22}' /proc/$$/stat)" > "$D/guard.id"
end=$(($(cut -d. -f1 /proc/uptime)+480))
echo "$end" > "$D/deadline"
: > "$D/ready"
while test "$(cut -d. -f1 /proc/uptime)" -lt "$end"; do
 test ! -f "$D/restored" || exit 0
 sleep 1
done
/bin/sh "$D/restore.sh" > "$D/restore.log" 2>&1
''')


def file_guards():
    return ('test ! -L "$D/restore.sh"; test ! -L "$D/guard.sh"\n'
            'test "$(sha256sum "$D/restore.sh" | awk \'{print $1}\')" = ' + sha(restore_body().encode()) + '\n'
            'test "$(sha256sum "$D/guard.sh" | awk \'{print $1}\')" = ' + sha(guard_body().encode()) + '\n')


def prepare():
    command = ('set -eu\ncommand -v wifi; command -v uci; command -v ubus; command -v iw; '
        'command -v sha256sum; command -v cut; command -v awk; command -v grep\n'
        'test "$(awk \'$2=="/tmp" && $3=="tmpfs"{n++} END{print n+0}\' /proc/mounts)" = 1\n'
        'test -z "$(uci changes)"\n'
        'if ip -4 addr show dev br-lan | grep -q "inet 10.99.0.1/"; then exit 83; fi\n'
        'test "$(uci -q get wireless.radio0.disabled)" = 1\n'
        'test "$(uci -q get wireless.radio0.txpower)" = 18\n'
        'test "$(uci -q get wireless.default_radio0.wds)" = 0\n'
        'test "$(uci -q get wireless.radio0.country)" = AR\n'
        'test "$(uci -q get wireless.radio0.channel)" = 36\n'
        'test "$(uci -q get wireless.radio0.htmode)" = VHT20\n'
        'test ! -e ' + DIR + '; test ! -L ' + DIR + '\numask 077\nmkdir ' + DIR + '\nset -C\n'
        + "printf '%s\\n' " + TOKEN + ' > ' + DIR + '/owner\n')
    for name, body in [('restore.sh', restore_body()), ('guard.sh', guard_body())]:
        command += 'printf %s ' + shlex.quote(body) + ' > ' + DIR + '/' + name + '\n'
    return command + '/bin/sh ' + DIR + '/guard.sh </dev/null >' + DIR + '/guard.log 2>&1 &\necho GUARD_DISPATCHED'


def guard_identity(client):
    output = checked(client, 'set -eu\n' + header() + file_guards() + '''
test -f "$D/ready"; test ! -f "$D/restored"
read p s < "$D/guard.id"
test "$(awk '{print $22}' /proc/$p/stat)" = "$s"
test "$(awk '{print $3}' /proc/$p/stat)" != Z
test "$(tr '\\000' ' ' < /proc/$p/cmdline)" = "/bin/sh $D/guard.sh "
test "$(cat "$D/deadline")" -gt "$(cut -d. -f1 /proc/uptime)"
printf '%s %s %s\n' "$p" "$s" "$(cat "$D/deadline")"
''')
    require(re.fullmatch(rb'[0-9]+ [0-9]+ [0-9]+\n', output), 'GUARD_PROTOCOL')
    return [int(v) for v in output.split()]


def off(client):
    identity(client)
    require(not checked(client, 'uci changes wireless').strip(), 'DELTAS_NOT_EMPTY')
    status = json.loads(checked(client, 'ubus call network.wireless status'))
    require(status.get('radio0', {}).get('disabled') is True and status['radio0'].get('up') is False, 'RADIO_NOT_OFF')
    require(b'Interface ' not in checked(client, 'iw dev'), 'RADIO_VAP_REMAINS')
    return dict(status='PASS_RAM_WINDOW_RESTORED_RADIO_OFF', config_sha256=CONFIG_SHA, deltas_empty=True)


def restore(client):
    client_pin(client)
    require(checked(client, 'cat /sys/class/net/eth0/address; cat /tmp/sysinfo/board_name; uname -r').decode().splitlines()
            == [MAC, 'ubnt,lap-120', '6.6.110'], 'RESTORE_BOARD_CHANGED')
    # Down is safe for the recognized owned radio even if later config/script
    # guards detect a concurrent writer. Revert still requires every exact gate.
    result = checked(client, 'set -eu\n' + header() + 'wifi down radio0\n' + file_guards() + '/bin/sh "$D/restore.sh"', timeout=25)
    require(b'RESTORE_OK' in result, 'RESTORE_NOT_CONFIRMED')
    result = off(client)
    for _ in range(5):
        ended = checked(client, 'set -eu\n' + header() + '''
read p s < "$D/guard.id"
if test -e /proc/$p/stat && test "$(awk '{print $22}' /proc/$p/stat)" = "$s" && test "$(awk '{print $3}' /proc/$p/stat)" != Z; then echo LIVE; else echo ENDED; fi
''').strip()
        if ended == b'ENDED':
            result['guard_ended_verified'] = True
            return result
        require(ended == b'LIVE', 'GUARD_END_UNKNOWN')
        time.sleep(1)
    raise RuntimeError('GUARD_END_UNKNOWN_NO_KILL')


def readiness(iw, reg, phy, status):
    def one(pattern):
        values = re.findall(pattern, iw, re.M)
        require(len(values) == 1, 'AP_READY_FIELD')
        return values[0]
    require(re.findall(r'^phy#([0-9]+)$', iw, re.M) == ['0'], 'AP_PHY_NOT_UNIQUE')
    blocks = re.split(r'(?m)^[ \t]*Interface ', iw)[1:]
    primary = [b for b in blocks if re.findall(r'^\s*type (\S+)$', b, re.M) == ['AP']]
    require(len(primary) == 1 and len(blocks) <= 5, 'AP_NOT_UNIQUE')
    base_name = primary[0].splitlines()[0].strip()
    base_addr = re.findall(r'^\s*addr (\S+)$', primary[0], re.M)
    require(len(base_addr) == 1, 'AP_BSSID_FORMAT')
    for block in blocks:
        if block == primary[0]: continue
        name = block.splitlines()[0].strip()
        require(re.fullmatch(re.escape(base_name) + r'\.sta[1-9][0-9]{0,3}', name)
                and re.findall(r'^\s*type (\S+)$', block, re.M) == ['AP/VLAN']
                and re.findall(r'^\s*addr (\S+)$', block, re.M) == base_addr,
                'UNEXPECTED_WDS_AUX_INTERFACE')
    iw = 'phy#0\n\tInterface ' + primary[0]  # Validate original AP RF fields below.
    require(one(r'^\s*type (\S+)$') == 'AP', 'AP_NOT_UNIQUE')
    bssid = one(r'^\s*addr (\S+)$').lower()
    require(re.fullmatch(r'(?:[0-9a-f]{2}:){5}[0-9a-f]{2}', bssid) is not None, 'AP_BSSID_FORMAT')
    octets = bytes.fromhex(bssid.replace(':', ''))
    require(any(octets) and not octets[0] & 1 and one(r'^\s*ssid (.+)$') == 'FuturaMAX-LAB', 'AP_IDENTITY')
    require(one(r'^\s*channel (.+)$').startswith('36 (5180 MHz), width: 20 MHz'), 'AP_FREQUENCY_WIDTH')
    require(float(one(r'^\s*txpower ([0-9.]+) dBm$')) == 0, 'AP_POWER_NOT_ZERO')
    global_reg = reg.split('phy#', 1)[0]
    require(re.search(r'^country AR:', global_reg, re.M), 'GLOBAL_AR_NOT_APPLIED')
    frequencies = [line for line in phy.splitlines() if re.search(r'\b5180(?:\.0)? MHz \[36\]', line)]
    require(len(frequencies) == 1 and not re.search(r'disabled|no IR|no initiating radiation', frequencies[0], re.I),
            'PHY_FREQUENCY_NOT_PERMITTED')
    require(status.get('radio0', {}).get('up') is True and status['radio0'].get('disabled') is False, 'RADIO_NOT_UP')
    domains = re.findall(r'^country (\S+):', reg, re.M)
    return dict(interface=one(r'^\s*Interface (\S+)$'), ifindex=int(one(r'^\s*ifindex ([0-9]+)$')),
                bssid=bssid, frequency_mhz=5180, width_mhz=20, txpower_dbm=0, global_country='AR',
                observed_regulatory_domains=domains, regulatory_sha256=sha(reg.encode()), phy_sha256=sha(phy.encode()))


def arm(client):
    global _USED
    require(not _USED, 'SINGLE_ATTEMPT_ALREADY_RESERVED')
    off(client)
    _USED = True
    try:
        checked(client, prepare())
        for _ in range(4):
            try:
                guard = guard_identity(client)
                break
            except RuntimeError:
                time.sleep(0.5)
        else:
            raise RuntimeError('GUARD_NOT_READY_NO_ENABLE')
        checked(client, 'set -eu\n' + header() + file_guards() + '''
test -f "$D/ready"; test ! -f "$D/restored"
test "$(cat "$D/deadline")" -ge "$(($(cut -d. -f1 /proc/uptime)+60))"
test -z "$(uci changes)"
uci set wireless.radio0.disabled=0
uci set wireless.radio0.txpower=0
uci set wireless.default_radio0.wds=1
uci set wireless.default_radio0.encryption=none
ip addr add 10.99.0.1/24 dev br-lan
wifi up radio0
''')
        end = time.monotonic() + 20
        while time.monotonic() < end:
            guard_identity(client)
            status = json.loads(checked(client, 'ubus call network.wireless status'))
            if status.get('radio0', {}).get('up') is True:
                ready = readiness(checked(client, 'iw dev').decode(), checked(client, 'iw reg get').decode(),
                                  checked(client, 'iw phy phy0 info').decode(), status)
                methods = checked(client, "ubus -v list 'hostapd.*'").decode()
                require('hostapd.' + ready['interface'] in methods, 'HOSTAPD_METHODS_ABSENT')
                ready.update(status='PASS_AP_OBSERVER_RAM_WINDOW_ARMED', guard_pid=guard[0], guard_start=guard[1],
                             guard_deadline_uptime=guard[2], ttl_seconds=TTL, remote_ram=DIR,
                             native_receipt_sha256=NATIVE_SHA, ubus_methods_sha256=sha(methods.encode()),
                             persistent_writes=False, vendor_ie_changed=False)
                return ready
            time.sleep(0.5)
        raise RuntimeError('AP_READY_DEADLINE')
    except BaseException as failure:
        try:
            restore(client)
        except BaseException as cleanup:
            raise RuntimeError('ARM_FAILED_RESTORE_UNCERTAIN_GUARD_OR_REMOTE_PRESERVED:' + type(cleanup).__name__) from failure
        raise


def main(argv=None):
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    evidence()
    print(json.dumps(dict(status='PLAN_ONLY_ROOT_INJECTED_CLIENT_REQUIRED', ttl_seconds=TTL,
                         ram_deltas=['wireless.radio0.disabled=0', 'wireless.radio0.txpower=0', 'wireless.default_radio0.wds=1'],
                         connects=False, persistent_writes=False, vendor_ie_changed=False)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

