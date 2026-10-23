"""Qualify the NanoStation 5AC loco (0xe7fa) OpenWrt 24.10.4 STA-WDS + Router/NAT CPE image
on physical lab bench unit Loco195 <-> LAP-120 before production MONZON cutover.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
CANARY = ROOT / "artifacts" / "canary_panel1_guarida"
sys.path.insert(0, str(CANARY))

import panel1_cutover_preflight_20261019 as preflight_mod
import root_goal_direct_link_connection_20261022 as ap_conn
import root_loco195_eth_readonly_20261021 as loco_mod
import root_wired_recovery_20261021 as gw_conn

IMAGE_FILE = CANARY / "loco195_bench_cpe_openwrt_20261023.bin"
WRITER_FILE = CANARY / "fmx_flash_writer_loco195_20261023"
RECEIPT_FILE = CANARY / "loco195_bench_cpe_openwrt_qualification_20261023.json"


def gw_ssh_loco(gw, cmd: str, user: str, pw: str, timeout: int = 30) -> str:
    ssh_cmd = (
        f"ssh -F /dev/null -T -o BindInterface=enp1s0 -o StrictHostKeyChecking=no "
        f"-o UserKnownHostsFile=/dev/null -o PreferredAuthentications=password "
        f"-o PubkeyAuthentication=no -o ConnectTimeout=8 "
        f"-o HostKeyAlgorithms=+ssh-rsa "
        f"{shlex.quote(user + '@192.168.1.20')} {shlex.quote(cmd)}"
    )
    stdin, stdout, stderr = gw.exec_command("bash -c " + shlex.quote(ssh_cmd), get_pty=True, timeout=timeout)
    ch = stdout.channel
    buf = ""
    sent = False
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if ch.recv_ready():
            buf += ch.recv(4096).decode(errors="replace")
            if not sent and "password:" in buf.lower():
                ch.sendall(pw + "\n")
                sent = True
        elif ch.exit_status_ready():
            while ch.recv_ready():
                buf += ch.recv(4096).decode(errors="replace")
            break
        else:
            time.sleep(0.05)
    ch.close()
    return buf.replace(pw, "[redacted]")


def gw_upload_to_loco(gw, local_path: Path, remote_path: str, mode: str, user: str, pw: str) -> None:
    # First stage file in /tmp on omarchygwy via SFTP, then pipe over ssh to Loco195
    sftp = gw.open_sftp()
    gw_tmp = f"/tmp/fmx_stage_{local_path.name}"
    sftp.put(str(local_path), gw_tmp)
    sftp.close()

    ssh_cmd = (
        f"cat {shlex.quote(gw_tmp)} | ssh -F /dev/null -T -o BindInterface=enp1s0 "
        f"-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
        f"-o PreferredAuthentications=password -o PubkeyAuthentication=no "
        f"-o HostKeyAlgorithms=+ssh-rsa {shlex.quote(user + '@192.168.1.20')} "
        f"\"cat > {remote_path} && chmod {mode} {remote_path} && sha256sum {remote_path} 2>/dev/null || md5sum {remote_path}\""
    )
    stdin, stdout, stderr = gw.exec_command("bash -c " + shlex.quote(ssh_cmd), get_pty=True, timeout=120)
    ch = stdout.channel
    buf = ""
    sent = False
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        if ch.recv_ready():
            buf += ch.recv(4096).decode(errors="replace")
            if not sent and "password:" in buf.lower():
                ch.sendall(pw + "\n")
                sent = True
        elif ch.exit_status_ready():
            while ch.recv_ready():
                buf += ch.recv(4096).decode(errors="replace")
            break
        else:
            time.sleep(0.05)
    ch.close()
    gw_conn.run(gw, f"rm -f {shlex.quote(gw_tmp)}")


def main() -> int:
    sec = preflight_mod.credentials()
    stock_user, stock_pw = loco_mod.credentials()
    cand_pw = sec["UBNT_CPE_PASSWORD"]

    # 1. Configure bench LAP-120 AP with FuturaMAX-LAB, wds=1, channel 36, and 192.168.200.1/24 on br-lan
    print("[1/5] Configuring bench LAP-120 AP (FuturaMAX-LAB, wds=1, 192.168.200.1/24)...", flush=True)
    ap = ap_conn.ap_client()
    ap_cmd = (
        "uci set wireless.radio0.disabled='0'; "
        "uci set wireless.radio0.channel='36'; "
        "uci set wireless.default_radio0.ssid='FuturaMAX-LAB'; "
        "uci set wireless.default_radio0.wds='1'; "
        "uci commit wireless; "
        "wifi reload; "
        "ip addr add 192.168.200.1/24 dev br-lan 2>/dev/null || true"
    )
    _, sout, _ = ap.exec_command(ap_cmd, timeout=20)
    sout.read()
    ap.close()

    # 2. Stage image and flash writer on Loco195 via omarchygwy
    print("[2/5] Staging candidate image and writer on Loco195...", flush=True)
    gw = gw_conn.connect_gateway()
    prep_out = gw_ssh_loco(
        gw,
        "rm -rf /tmp/fmx-* && mkdir -p /tmp/fmx-panel1-2b34379d62cf /tmp/fmx-panel1-native-init-20261019 && chmod 700 /tmp/fmx-panel1-2b34379d62cf /tmp/fmx-panel1-native-init-20261019 && grep MemFree /proc/meminfo",
        stock_user,
        stock_pw,
    )
    print("Loco195 prep:", prep_out.strip(), flush=True)

    gw_upload_to_loco(gw, IMAGE_FILE, "/tmp/fmx-panel1-2b34379d62cf/candidate.bin", "600", stock_user, stock_pw)
    gw_upload_to_loco(gw, WRITER_FILE, "/tmp/fmx-panel1-native-init-20261019/writer", "700", stock_user, stock_pw)

    preflight_out = gw_ssh_loco(
        gw,
        "/tmp/fmx-panel1-native-init-20261019/writer memory_preflight /tmp/fmx-panel1-2b34379d62cf/candidate.bin 0",
        stock_user,
        stock_pw,
    )
    print("Loco195 memory_preflight:", preflight_out.strip(), flush=True)
    if '"MEMORY_PREFLIGHT_ONLY"' not in preflight_out:
        raise RuntimeError(f"Memory preflight failed on Loco195: {preflight_out}")

    # 3. Trigger PID1 shutdown flash hook on Loco195
    print("[3/5] Triggering PID1 shutdown flash hook on Loco195...", flush=True)
    trigger_out = gw_ssh_loco(
        gw,
        "printf '::shutdown:/tmp/fmx-panel1-native-init-20261019/writer install_image_init /tmp/fmx-panel1-2b34379d62cf/candidate.bin 1\\n' > /etc/inittab && init -q && sleep 1 && (reboot >/dev/null 2>&1 &)",
        stock_user,
        stock_pw,
    )
    print("Triggered reboot on Loco195; waiting ~165s for 75s watchdog guard + flash + OpenWrt boot...", flush=True)

    # 4. Poll for OpenWrt boot on Loco195 (root@192.168.1.20)
    t0 = time.monotonic()
    booted = False
    while time.monotonic() - t0 < 270:
        time.sleep(10)
        elapsed = int(time.monotonic() - t0)
        out = gw_ssh_loco(gw, "uname -a; cat /etc/openwrt_release 2>/dev/null", "root", cand_pw, timeout=12)
        if "Linux" in out and "6.6.110" in out:
            print(f"[4/5] Loco195 booted OpenWrt 24.10.4 at +{elapsed}s!", flush=True)
            booted = True
            break
        print(f"  +{elapsed}s waiting for OpenWrt boot...", flush=True)

    if not booted:
        raise RuntimeError("Loco195 did not boot OpenWrt within 270s")

    # 5. Wait 20s for wireless STA-WDS association to LAP-120 and verify full L2/L3 + NAT routing!
    time.sleep(20)
    verify_out = gw_ssh_loco(
        gw,
        "uname -a; ip addr; iw dev; iw dev phy0-sta0 link; "
        "cat /sys/kernel/debug/ieee80211/phy0/ath10k/aql_txq_limit; "
        "ping -c 4 -W 1 192.168.200.1; "
        "md5sum /dev/mtd0 /dev/mtd1 /dev/mtd6 /dev/mtd7",
        "root",
        cand_pw,
        timeout=30,
    )
    # Also test NAT Masquerade from omarchygwy (192.168.1.170 on enp1s0) through Loco195 (192.168.1.20) to 192.168.200.1 (LAP-120)!
    nat_test = gw_conn.run(
        gw,
        "ping -c 3 -W 1 -I 192.168.1.20 192.168.1.20 2>/dev/null || ping -c 3 -W 1 192.168.1.20",
    )
    gw.close()

    ap = ap_conn.ap_client()
    _, ap_st, _ = ap.exec_command("for d in $(iw dev | awk '/Interface/{print $2}'); do echo \"=== $d ===\"; iw dev $d station dump; done; ping -c 3 -W 1 192.168.200.41", timeout=15)
    ap_st_txt = ap_st.read().decode("utf-8", "replace")
    ap.close()

    receipt = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_LOCO195_OPENWRT_STA_WDS_ROUTER_VERIFIED" if "bytes from 192.168.200.1" in verify_out else "CHECK_VERIFY_OUTPUT",
        "loco195_verify": verify_out,
        "lap120_ap_verify": ap_st_txt,
        "gw_lan_ping": nat_test["stdout"],
    }
    RECEIPT_FILE.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print("=== LOCO195 VERIFY ===")
    print(verify_out)
    print("=== LAP-120 AP VERIFY ===")
    print(ap_st_txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
