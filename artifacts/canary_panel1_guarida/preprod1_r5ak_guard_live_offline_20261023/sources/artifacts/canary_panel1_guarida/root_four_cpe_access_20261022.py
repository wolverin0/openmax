"""Pinned LAP forwarding and operator-named legacy-device access; no flash."""
from pathlib import Path
import hashlib
import importlib.util
import io
import json
import re
import time
import paramiko

HERE = Path(__file__).resolve().parent
DEVICES = {'SXT': ('10.99.0.3', '64:d1:54:1b:96:97'),
           'LBM5': ('10.99.0.4', 'f0:9f:c2:b2:b6:ba')}
sha = lambda b: hashlib.sha256(b).hexdigest()


def require(ok, gate):
    if not ok:
        raise RuntimeError(gate)


def load(name):
    spec = importlib.util.spec_from_file_location('_four_' + name.removesuffix('.py'), HERE / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def remote(client, command, timeout=15, check=True, limit=65536):
    i, o, e = client.exec_command(command, timeout=timeout)
    i.close()
    try:
        raw, err = o.read(limit + 1), e.read(8193)
        rc = o.channel.recv_exit_status()
        require(len(raw) <= limit and len(err) <= 8192, 'OUTPUT_BOUND')
        if check:
            require(rc == 0 and not err, 'REMOTE_EXIT_' + str(rc) + '_' + err.decode(errors='replace')[:100])
        return dict(exit_code=rc, stdout=raw.decode(errors='replace'), stderr=err.decode(errors='replace'))
    finally:
        o.channel.close()


def connect_legacy(ap, name, pin=None, address_override=None):
    address, mac = DEVICES[name]
    address = address_override or address
    sock = ap.get_transport().open_channel('direct-tcpip', (address, 22), ('10.99.0.1', 0), timeout=8)
    transport = paramiko.Transport(sock)
    try:
        transport.start_client(timeout=8)
        observed_pin = sha(transport.get_remote_server_key().asbytes())
        if pin is not None:
            require(observed_pin == pin, name + '_SSH_PIN_CHANGED')
        if name == 'LBM5':
            transport.auth_password('ubnt', 'ubnt')
        else:
            try:
                transport.auth_none('root')
            except paramiko.AuthenticationException:
                try:
                    transport.auth_password('root', '')
                except paramiko.AuthenticationException:
                    # Explicit operator pointer: the existing LAP root key.
                    for path, cls in [('/root/.ssh/id_ed25519', paramiko.Ed25519Key),
                                      ('/root/.ssh/id_rsa', paramiko.RSAKey)]:
                        result = remote(ap, 'cat ' + path, check=False, limit=16384)
                        if result['exit_code'] != 0:
                            continue
                        material = io.StringIO(result['stdout'])
                        try:
                            key = cls.from_private_key(material)
                            transport.auth_publickey('root', key)
                            if transport.is_authenticated():
                                break
                        except (paramiko.AuthenticationException, paramiko.SSHException):
                            pass
                        finally:
                            material.close(); result.clear()
        require(transport.is_authenticated(), name + '_AUTH_FAILED')
        client = paramiko.SSHClient(); client._transport = transport
        # The RF MAC is additionally checked before any mutation; first-use
        # host key is recorded and bound for the subsequent treatment.
        devname = 'phy0-sta0' if name == 'SXT' else 'ath0'
        identity = remote(client, 'cat /sys/class/net/' + devname + '/address')['stdout'].strip().lower()
        require(identity == mac, name + '_RADIO_MAC_CHANGED')
        return client, observed_pin
    except BaseException:
        transport.close()
        raise


def ap_helper():
    module = load('root_four_cpe_ap_window_20261022.py')
    module.NATIVE = HERE / 'root_goal_direct_link_cycle_20261022_native_install/receipt.json'
    module.NATIVE_SHA = 'ff6fdbac93c279ad55468e0165767de0f05dddd79db21c7bd3ce1f38a1ac0f92'
    return module


def intake(label):
    out = HERE / ('root_four_cpe_' + label)
    out.mkdir(mode=0o700, exist_ok=False)
    record = dict(experiment='FMX-0016', stage='OPEN_RF_READONLY_LEGACY_INTAKE', status='INCOMPLETE', devices={})
    ap = None; helper = None; armed = False
    def private(name, content):
        raw = content.encode() if isinstance(content, str) else content
        with (out / name).open('xb') as f:
            f.write(raw)
        return dict(file=name, bytes=len(raw), sha256=sha(raw))
    try:
        ap = load('root_goal_direct_link_connection_20261022.py').ap_client()
        helper = ap_helper(); record['ready'] = helper.arm(ap); armed = True
        end = time.monotonic() + 30
        reachable = set(); probes = []
        while time.monotonic() < end and len(reachable) != 2:
            for name, (address, mac) in DEVICES.items():
                if name in reachable: continue
                result = remote(ap, 'ping -c 1 -W 1 -I br-lan ' + address, check=False, timeout=3)
                probes.append(dict(device=name, result=result))
                if result['exit_code'] == 0: reachable.add(name)
            if len(reachable) != 2: time.sleep(.4)
        record['probes'] = probes
        record['live_stations'] = remote(ap, 'iw dev; iw dev phy0-ap0 station dump; ip neigh show dev br-lan', check=False)
        require(reachable == set(DEVICES), 'LEGACY_OPEN_RF_NOT_REACHABLE_' + '_'.join(sorted(set(DEVICES)-reachable)))
        for name in DEVICES:
            client, pin = connect_legacy(ap, name)
            try:
                if name == 'SXT':
                    data = remote(client, 'cat /etc/openwrt_release; ubus call system board; iw dev; ip -4 addr; uci changes wireless; sha256sum /etc/config/wireless; command -v wifi; command -v uci; cat /proc/mtd')['stdout']
                    cfg = remote(client, 'cat /etc/config/wireless')['stdout']
                    record['devices'][name] = dict(pin=pin, identity=data, wireless_config=private('sxt-wireless.cfg', cfg),
                                                   wireless_changes=remote(client, 'uci changes wireless')['stdout'])
                    require("24.10.4" in data and not record['devices'][name]['wireless_changes'].strip(), 'SXT_RELEASE_OR_DIRTY_UCI')
                else:
                    data = remote(client, 'cat /etc/version; cat /proc/sys/kernel/random/boot_id; iwconfig ath0; brctl show; ip -4 addr; cat /proc/mtd; command -v wpa_supplicant; command -v wpa_cli; command -v iwpriv; ps | grep "[w]pa_supplicant"; iwpriv ath0 get_authmode', check=False)
                    cfg = remote(client, 'cat /tmp/system.cfg')['stdout']
                    tools = remote(client, 'wpa_supplicant -v; wpa_supplicant -h; iwpriv ath0 get_wds; ls -ld /tmp; cat /proc/mounts', check=False)
                    record['devices'][name] = dict(pin=pin, identity=data, system_config=private('lbm5-system.cfg', cfg),
                                                   system_md5=hashlib.md5(cfg.encode()).hexdigest(), tools=tools)
                    require('6.1.4' in data['stdout'], 'LBM5_RELEASE_CHANGED')
                record['devices'][name]['boot_id'] = remote(client, 'cat /proc/sys/kernel/random/boot_id')['stdout'].strip()
            finally:
                client.close()
        record['status'] = 'PASS_OPEN_RF_LEGACY_IDENTITY_CONFIG_INTAKE'
    except BaseException as e:
        record['failure'] = dict(type=type(e).__name__, gate=str(e)[:180])
    finally:
        if helper is not None and armed:
            try: record['restoration'] = helper.restore(ap)
            except BaseException as e: record['restore_failure'] = dict(type=type(e).__name__, gate=str(e)[:180])
        if ap: ap.close()
        with (out / 'receipt.json').open('x', encoding='utf-8') as f: json.dump(record, f, indent=2)
    print(json.dumps({k:record.get(k) for k in ['status','failure','restore_failure','restoration','devices']}, indent=2), flush=True)
    return record


if __name__ == '__main__':
    intake('intake_20261022_run1')
