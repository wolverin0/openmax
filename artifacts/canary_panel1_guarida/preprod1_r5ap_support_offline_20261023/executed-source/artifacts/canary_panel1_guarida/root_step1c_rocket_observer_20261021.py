"""Root-owned Rocket observer connection and read-only baseline."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import paramiko

HERE = Path(__file__).resolve().parent
PIN = '73cdf5e81449068a04b2d897f1648fa0856afef040e8fc4e4ab86678ace3b39a'
BOOT = '49a9a78e-4943-4917-8d62-62bd1783379f'
sha = lambda b: hashlib.sha256(b).hexdigest()

def require(ok, gate):
    if not ok:
        raise RuntimeError(gate)

def command(client, cmd, limit=65536, timeout=20):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    stdin.close()
    data, error = stdout.read(limit+1), stderr.read(8193)
    code = stdout.channel.recv_exit_status()
    stdout.channel.close()
    require(len(data) <= limit and len(error) <= 8192, 'OUTPUT_BOUND')
    require(code == 0, 'REMOTE_EXIT_' + str(code))
    return data, error

def connect():
    receipt = json.loads((HERE / 'rocket198_observer_handoff_receipt_20261021.json').read_text())
    require(receipt['ssh_host_key_sha256_hex'] == PIN and receipt['boot_id'] == BOOT, 'HANDOFF_CHANGED')
    require(receipt['ownership_status'] == 'CEDED_EXCLUSIVELY_TO_CODEX_RUN_204f7681fd7c_FOR_FMX0015_MONITOR_OBSERVER', 'OWNERSHIP_MISSING')
    auth = json.loads((HERE.parent / 'stage11_rocket_prism_bench_20261021.json').read_text())['auth_verified'].split()[0].split('/')
    require(len(auth) == 2, 'CREDENTIAL_POINTER_FORMAT')
    client = paramiko.SSHClient()
    class Pin(paramiko.MissingHostKeyPolicy):
        def missing_host_key(self, connection, host, key):
            require(sha(key.asbytes()) == PIN, 'SSH_PIN_CHANGED')
            connection.get_host_keys().add(host, key.get_name(), key)
    client.set_missing_host_key_policy(Pin())
    try:
        client.connect('192.168.100.198', username=auth[0], password=auth[1], timeout=8, banner_timeout=8, auth_timeout=8, look_for_keys=False, allow_agent=False)
    finally:
        auth.clear()
    try:
        data, _ = command(client, 'cat /etc/version; cat /sys/class/net/eth0/address; grep -E "^board.(sysid|hwaddr)=" /etc/board.info')
        require(data.decode().splitlines() == ['XC.v8.7.25', 'b4:fb:e4:5d:d5:d2', 'board.sysid=0xe7e9', 'board.hwaddr=B4FBE45CD5D2'], 'DEVICE_IDENTITY_CHANGED')
    except BaseException:
        client.close()
        raise
    return client

def main():
    if sys.argv[1:] != ['--intake']:
        print('PLAN_ONLY: pinned Rocket read-only intake')
        return 0
    out = HERE / 'root_step1c_rocket_intake_v2_20261021'
    out.mkdir(exist_ok=False)
    client = connect()
    record = dict(status='INCOMPLETE_INTAKE', device_writes=False, source_sha256=sha(Path(__file__).read_bytes()), ssh_pin=PIN, started_utc=datetime.now(timezone.utc).isoformat())
    try:
        query = '''set -e
echo __BOOT__; cat /proc/sys/kernel/random/boot_id; cat /proc/uptime
echo __HASHES__; md5sum /tmp/system.cfg /tmp/running.cfg /dev/mtd0 /dev/mtd1 /dev/mtd2 /dev/mtd3 /dev/mtd4 /dev/mtd5 /lib/modules/2.6.32.68/ubnt_poll_host.ko /lib/modules/2.6.32.68/umac.ko
echo __INTERFACES__; iwconfig 2>&1; brctl show; cat /proc/net/if_inet6
echo __UPH__; ls -la /proc/sys/dev/uph; ls -d /proc/sys/dev/uph_wifi* 2>/dev/null || true
echo __PROCESSES__; for n in wpa_supplicant ubntspecd crond; do echo "$n"; pidof "$n" || true; done
echo __MODULES__; lsmod
echo __TOOLS__; for n in tcpdump wlanconfig iwconfig iwpriv athchans timeout killall; do command -v "$n" || true; done
echo __KERNEL__; dmesg | tail -n 18
echo __END__'''
        data, error = command(client, query)
        (out / 'runtime.txt').write_bytes(data)
        (out / 'stderr.txt').write_bytes(error)
        for remote, local, limit in [('/tmp/system.cfg','system.cfg',65536),('/tmp/running.cfg','running.cfg',65536),('/dev/mtd4','mtd4.bin',262144)]:
            content, error = command(client, 'cat '+remote, limit=limit)
            require(not error, 'BASELINE_READ_ERROR')
            (out / local).write_bytes(content)
            record[local] = dict(bytes=len(content), sha256=sha(content))
        require(data.decode().split('__BOOT__\n',1)[1].splitlines()[0] == BOOT, 'BOOT_CHANGED_SINCE_HANDOFF')
        record.update(status='PASS_PINNED_ROCKET_READONLY_INTAKE', runtime_sha256=sha(data))
        print(json.dumps({k:record[k] for k in ('status','runtime_sha256','device_writes')}))
        return 0
    finally:
        client.close()
        record['ended_utc'] = datetime.now(timezone.utc).isoformat()
        (out / 'receipt.json').write_text(json.dumps(record,indent=2))

if __name__ == '__main__':
    raise SystemExit(main())
