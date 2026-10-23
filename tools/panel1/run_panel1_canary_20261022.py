"""Controlled live OpenWrt canary cutover on Panel1-Guarida (10.10.100.84) with
Zero-Touch Stock airOS 8 (WA.v8.7.25) WDS + Vendor-IE admission and automatic
Stock WA.v8.7.25 rollback guard.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import paramiko

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
CANARY = ROOT / "artifacts" / "canary_panel1_guarida"
if str(CANARY) not in sys.path:
    sys.path.insert(0, str(CANARY))

import init_v3_observer_stopfix_20261019 as observer_mod
import panel1_cutover_preflight_20261019 as preflight_mod

TARGET_IP = "10.10.100.84"
SOURCE_BIND = "192.168.100.155"
OBSERVER_PEER = "192.168.100.200"
OBSERVER_PORT = 39261
RECEIPT_NONCE = "1aa3778048e1ccb86558639ee714293e53080b36463ee1463d0ac5f1f8ff3ec0"

PERM_MAC = "78:45:58:a1:34:a2"
BOARD_SHA256 = "97f3b8a0b1c55e319c6414992f9c1e9a01a78e919708d4b6154cb7a6a5eb1c21"
STOCK_KEY_SHA256 = "2dacf88fcdd32b7cecdf90f872b74f8b5bc4dd56cc35ca02e61b3da26be44400"
CANDIDATE_KEY_SHA256 = "6425baaf032f71a8c5019837e5391721d9fd60c9723cca037980bad12e8e2feb"

IMAGE_FILE = CANARY / "panel1_firmware_lap120_proven_v3_20261019.bin"
IMAGE_SHA256 = "2b34379d62cff6738e769c1dd613b6e82bd3b19092be936a54d1b55d416e69a5"
IMAGE_MD5 = "11d5aa04fa8c25a06cd08be68269ff56"

WRITER_FILE = CANARY / "fmx_flash_writer_panel1_native_20261019"
WRITER_SHA256 = "051bf5801f5055d8d36a2e2a0d140e252fb7c2c688ad2c225c9088bc3e98294d"

STOCK_PKG_FILE = CANARY / "lap120_stock_cycle_20261019_package" / "lap120-wa8725-full-region.sysupgrade.bin.gz"
STOCK_PKG_SHA256 = "8f640047424a946596de7125781b67bc3b8d52f78deb8793b195ce11c0b3d231"

ADMITTER_FILE = ROOT / "tools" / "panel1" / "panel1_admitter.sh"
RECEIPT_FILE = CANARY / "panel1_zero_touch_canary_20261022_receipt.json"

ACTIVE_CPES = [
    {"mac": "24:5a:4c:44:77:7a", "ip": "10.10.200.223", "name": "GAMBOA_Gabriela"},
    {"mac": "24:5a:4c:e0:05:40", "ip": "10.10.200.41", "name": "MONZON Stella Maris"},
]

BASELINE_DIR = CANARY / "panel1_native_baseline_20261019_ready"
EXPECTED_STOCK_MD5 = {
    f"/dev/mtd{i}": hashlib.md5((BASELINE_DIR / f"mtd{i}.bin").read_bytes()).hexdigest()
    for i in (0, 1, 2, 3, 5)
}

EXPECTED_OPENWRT_SHA256 = {
    "/dev/mtd0": "988de5143235db3c0afc810b3bbad0b9177e96ec8493b4873486eb626d80ebfc",
    "/dev/mtd1": "63213a0bb3ec161faa51abf53417dcab7325b529c12150073923c6ab42cf711f",
    "/dev/mtd7": "58ece05258e859698dc9da7d2d323aea9160513aa0de4cb86519beba83abc729",
    "immutable_prefix": "98c756b293ebe05b410365ac5cc663250d9a3c085c0300234b03904e17f0e723",
    "mac80211": "19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416",
}


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def log(msg: str) -> None:
    print(f"[{utc()}] {msg}", flush=True)


def pc_ping(ip: str, count: int = 2, timeout_ms: int = 1200) -> bool:
    r = subprocess.run(
        ["ping", "-n", str(count), "-w", str(timeout_ms), ip],
        capture_output=True,
        text=True,
    )
    return r.returncode == 0 and "TTL=" in r.stdout


def connect_ssh(candidate: bool = False, timeout: int = 10) -> tuple[paramiko.SSHClient, str]:
    sec = preflight_mod.credentials()
    client = paramiko.SSHClient()
    observed_key = {"sha": ""}

    class PinPolicy(paramiko.MissingHostKeyPolicy):
        def missing_host_key(self, cli, hostname, key):
            k_sha = sha256(key.asbytes())
            observed_key["sha"] = k_sha
            if candidate:
                if k_sha == STOCK_KEY_SHA256:
                    raise RuntimeError("Still stock SSH host key; candidate not booted yet")
            else:
                if k_sha != STOCK_KEY_SHA256:
                    raise RuntimeError(f"Unexpected stock SSH key: {k_sha}")
            cli.get_host_keys().add(hostname, key.get_name(), key)

    client.set_missing_host_key_policy(PinPolicy())
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(timeout)
        sock.bind((SOURCE_BIND, 0))
        sock.connect((TARGET_IP, 22))
        client.connect(
            TARGET_IP,
            username="root" if candidate else sec["UBNT_CPE_USER"],
            password=sec["UBNT_CPE_PASSWORD"],
            sock=sock,
            timeout=timeout,
            auth_timeout=timeout,
            banner_timeout=timeout,
            look_for_keys=False,
            allow_agent=False,
        )
        return client, observed_key["sha"]
    except BaseException:
        client.close()
        sock.close()
        raise


def ssh_exec(client: paramiko.SSHClient, cmd: str, stdin_bytes: bytes | None = None, timeout: int = 30) -> tuple[int, bytes, bytes]:
    sin, sout, serr = client.exec_command(cmd, timeout=timeout)
    if stdin_bytes is not None:
        sin.write(stdin_bytes)
        sin.channel.shutdown_write()
    sin.close()
    out = sout.read()
    err = serr.read()
    rc = sout.channel.recv_exit_status()
    return rc, out, err


def main() -> int:
    receipt: dict = {
        "experiment": "PANEL1_GUARIDA_ZERO_TOUCH_CANARY_20261022",
        "target": TARGET_IP,
        "started_utc": utc(),
        "status": "STARTING",
        "events": [],
    }

    def save() -> None:
        RECEIPT_FILE.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    def ev(phase: str, **kw) -> None:
        entry = {"utc": utc(), "phase": phase, **kw}
        receipt["events"].append(entry)
        save()
        log(f"{phase}: {json.dumps(kw)}")

    # Verify local artifacts
    writer_bytes = WRITER_FILE.read_bytes()
    stock_pkg_bytes = STOCK_PKG_FILE.read_bytes()
    admitter_bytes = ADMITTER_FILE.read_bytes().replace(b"\r\n", b"\n")
    if sha256(writer_bytes) != WRITER_SHA256:
        raise RuntimeError("Writer binary SHA256 mismatch")
    if sha256(stock_pkg_bytes) != STOCK_PKG_SHA256:
        raise RuntimeError("Stock return package SHA256 mismatch")
    if sha256(IMAGE_FILE.read_bytes()) != IMAGE_SHA256:
        raise RuntimeError("Candidate image SHA256 mismatch")

    # 1. Preflight on Stock WA.v8.7.25
    cl, key_sha = connect_ssh(candidate=False, timeout=10)
    try:
        # Stage candidate.bin in /tmp if not already resident
        rc_c, out_c, _ = ssh_exec(
            cl,
            "md5sum /tmp/fmx-panel1-2b34379d62cf/candidate.bin 2>/dev/null || echo MISSING",
            timeout=15,
        )
        if IMAGE_MD5 not in out_c.decode("utf-8", "replace"):
            ev("STAGING_CANDIDATE_IMAGE_IN_TMP")
            image_bytes = IMAGE_FILE.read_bytes()
            ssh_exec(
                cl,
                "rm -rf /tmp/fmx-panel1-* /tmp/diff.sh /tmp/system.cfg.stock_bak && "
                "sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true && "
                "umask 077 && mkdir -p /tmp/fmx-panel1-2b34379d62cf",
                timeout=15,
            )
            rc_up, _, err_up = ssh_exec(
                cl,
                "cat > /tmp/fmx-panel1-2b34379d62cf/candidate.bin && chmod 600 /tmp/fmx-panel1-2b34379d62cf/candidate.bin",
                stdin_bytes=image_bytes,
                timeout=120,
            )
            if rc_up != 0:
                raise RuntimeError(f"Failed to upload candidate.bin: {err_up.decode()}")

        rc, out, _ = ssh_exec(
            cl,
            "cat /sys/class/net/eth0/address; cat /etc/version; uname -r; "
            "md5sum /dev/mtd0 /dev/mtd1 /dev/mtd2 /dev/mtd3 /dev/mtd5; "
            "md5sum /tmp/fmx-panel1-2b34379d62cf/candidate.bin; "
            "awk '/^MemFree:/{print $2}' /proc/meminfo",
            timeout=30,
        )
        if rc != 0:
            raise RuntimeError("Preflight command failed on 10.10.100.84")
        lines = [l.strip() for l in out.decode("utf-8", "replace").splitlines() if l.strip()]
        if lines[0].lower() != PERM_MAC or lines[1] != "WA.v8.7.25" or lines[2] != "2.6.32.68":
            raise RuntimeError(f"Unexpected stock identity: {lines[:3]}")
        md5_map = {}
        for l in lines[3:9]:
            parts = l.split()
            if len(parts) == 2:
                md5_map[parts[1]] = parts[0]
        for dev, exp_md5 in EXPECTED_STOCK_MD5.items():
            if md5_map.get(dev) != exp_md5:
                raise RuntimeError(f"Stock partition MD5 mismatch on {dev}: {md5_map.get(dev)} != {exp_md5}")
        if md5_map.get("/tmp/fmx-panel1-2b34379d62cf/candidate.bin") != IMAGE_MD5:
            raise RuntimeError("Resident candidate.bin MD5 mismatch in /tmp")
        memfree_kib = int(lines[9])
        if memfree_kib < 8878:
            raise RuntimeError(f"Insufficient MemFree before staging: {memfree_kib} KiB")

        rc_w, out_w, _ = ssh_exec(cl, "wstalist", timeout=15)
        st_list = json.loads(out_w.decode("utf-8", "replace"))
        assoc_macs = {s.get("mac", "").lower(): s.get("lastip") for s in st_list}
        for cpe in ACTIVE_CPES:
            if cpe["mac"] not in assoc_macs:
                raise RuntimeError(f"Active CPE {cpe['name']} ({cpe['mac']}) missing from wstalist before cutover")
            if not pc_ping(cpe["ip"]):
                raise RuntimeError(f"Active CPE {cpe['name']} ({cpe['ip']}) not responding to ping before cutover")

        ev("STOCK_PREFLIGHT_PASSED", memfree_kib=memfree_kib, active_cpes=ACTIVE_CPES)

        # 2. Stage writer and inittab hook in RAM
        rc_i, orig_inittab, _ = ssh_exec(cl, "cat /var/etc/inittab", timeout=10)
        if rc_i != 0 or not orig_inittab:
            raise RuntimeError("Failed to read /var/etc/inittab")
        hook_line = b"::shutdown:/tmp/fmx-panel1-native-init-20261019/writer install_image_init /tmp/fmx-panel1-2b34379d62cf/candidate.bin 1\n"
        new_inittab = hook_line
        if len(new_inittab) != 119 or sha256(new_inittab) != "1c1e6bd7809404041073545123b96432fb08c258bebaabd5db976a4c4d3f3820":
            raise RuntimeError("Unexpected hook_line length or SHA256")

        ssh_exec(
            cl,
            "rm -rf /tmp/fmx-panel1-native-init-20261019 && umask 077 && mkdir /tmp/fmx-panel1-native-init-20261019",
            timeout=10,
        )
        rc_u1, _, err_u1 = ssh_exec(
            cl,
            "cat > /tmp/fmx-panel1-native-init-20261019/writer && chmod 700 /tmp/fmx-panel1-native-init-20261019/writer",
            stdin_bytes=writer_bytes,
            timeout=45,
        )
        if rc_u1 != 0:
            raise RuntimeError(f"Failed to upload writer: {err_u1.decode()}")
        ssh_exec(
            cl,
            "cat > /tmp/fmx-panel1-native-init-20261019/inittab.original && chmod 644 /tmp/fmx-panel1-native-init-20261019/inittab.original",
            stdin_bytes=orig_inittab,
            timeout=10,
        )
        ssh_exec(
            cl,
            "cat > /tmp/fmx-panel1-native-init-20261019/inittab.new && chmod 644 /tmp/fmx-panel1-native-init-20261019/inittab.new",
            stdin_bytes=new_inittab,
            timeout=10,
        )
        rc_m, out_m, _ = ssh_exec(cl, "awk '/^MemFree:/{print $2}' /proc/meminfo", timeout=10)
        memfree_after = int(out_m.decode().strip())
        if memfree_after < 8352:
            raise RuntimeError(f"MemFree after hook staging below floor: {memfree_after} KiB")
        ev("RAM_STAGE_COMPLETE", memfree_after_kib=memfree_after)

        # 3. Start TCP ReceiptObserver & trigger atomic reboot handoff
        obs_out = CANARY / f"panel1_canary_observer_{int(time.time())}.jsonl"
        obs = observer_mod.ReceiptObserver(
            host=SOURCE_BIND,
            port=OBSERVER_PORT,
            peer=OBSERVER_PEER,
            nonce=RECEIPT_NONCE,
            output=obs_out,
            duration=420,
        )
        obs.start()
        try:
            rc_mv, out_mv, err_mv = ssh_exec(
                cl,
                "mv /tmp/fmx-panel1-native-init-20261019/inittab.new /var/etc/inittab && cat /var/etc/inittab",
                timeout=10,
            )
            if rc_mv != 0 or out_mv != hook_line:
                raise RuntimeError(f"RAM shutdown hook readback mismatch: rc={rc_mv} err={err_mv.decode()}")
            ev("RAM_INITTAB_VERIFIED")
            rc_hup, _, _ = ssh_exec(cl, "kill -HUP 1", timeout=10)
            ev("PID1_HUP_RELOAD_COMPLETE", rc=rc_hup)
            try:
                rc_h, _, _ = ssh_exec(cl, "/sbin/reboot", timeout=10)
                ev("REBOOT_HANDOFF_SENT", rc=rc_h)
            except Exception as exc_rb:
                ev("REBOOT_REQUEST_TRANSPORT_UNCERTAIN", error=str(exc_rb))
        finally:
            cl.close()
    except BaseException:
        cl.close()
        raise

    # 4. Wait for OpenWrt candidate boot on 10.10.100.84
    t_handoff = time.monotonic()
    cand_cl = None
    while time.monotonic() - t_handoff < 420:
        if len(obs.records) > len(receipt.get("native_records", [])):
            receipt["native_records"] = list(obs.records)
            ev("NATIVE_OBSERVER_PROGRESS", count=len(obs.records), latest=obs.records[-1].get("status"))
        # Do not poll port 22 until after INIT_AP_IMAGE_VERIFIED (or 110s elapsed) so dropbear quiesce is undisturbed
        if time.monotonic() - t_handoff < 110 and not any(
            r.get("status") == "INIT_AP_IMAGE_VERIFIED" for r in obs.records
        ):
            time.sleep(2)
            continue
        try:
            cand_cl, cand_key = connect_ssh(candidate=True, timeout=20)
            ev("OPENWRT_SSH_CONNECTED", elapsed_s=round(time.monotonic() - t_handoff, 2), ssh_key_sha256=cand_key)
            break
        except Exception:
            time.sleep(2)

    if cand_cl is None:
        obs.stop()
        receipt["status"] = "FAIL_CANDIDATE_SSH_TIMEOUT"
        save()
        return 1

    obs.stop()
    receipt["native_records"] = list(obs.records)

    # 5. Immediately verify runtime, enable wds=1, launch panel1_admitter.sh, and arm Stock WA.v8.7.25 rollback watchdog
    rollback_needed = True
    stock_staged = False
    try:
        # 5a. Fast RAM/page-cache verification of OpenWrt identity & mac80211.ko (avoids blocking on first-boot jffs2_gcd_mtd5 SPI erase)
        rc_v, out_v, _ = ssh_exec(
            cand_cl,
            "cat /sys/class/net/eth0/address; cat /tmp/sysinfo/board_name; uname -r; "
            "sha256sum /lib/modules/6.6.110/mac80211.ko",
            timeout=90,
        )
        v_lines = [l.strip() for l in out_v.decode("utf-8", "replace").splitlines() if l.strip()]
        if v_lines[:3] != [PERM_MAC, "ubnt,lap-120", "6.6.110"]:
            raise RuntimeError(f"OpenWrt identity mismatch: {v_lines[:3]}")
        mac80211_sha = v_lines[3].split()[0]
        if mac80211_sha != EXPECTED_OPENWRT_SHA256["mac80211"]:
            raise RuntimeError(f"OpenWrt mac80211.ko SHA256 mismatch: {mac80211_sha}")
        ev("OPENWRT_IDENTITY_AND_MAC80211_VERIFIED", mac80211_sha256=mac80211_sha)

        # 5b. Stage stock return image & arm 480s AP-local watchdog FIRST (while radio0 is still quiet)
        ssh_exec(cand_cl, "wifi down radio0 2>/dev/null || true", timeout=15)
        rc_s, _, err_s = ssh_exec(
            cand_cl,
            "rm -rf /tmp/fmx-panel1-own-stock-return-20261020 && umask 077 && "
            "mkdir -p /tmp/fmx-panel1-own-stock-return-20261020 && "
            "cat > /tmp/fmx-panel1-own-stock-return-20261020/stock.bin.gz && "
            "chmod 600 /tmp/fmx-panel1-own-stock-return-20261020/stock.bin.gz && "
            "sysupgrade -T /tmp/fmx-panel1-own-stock-return-20261020/stock.bin.gz",
            stdin_bytes=stock_pkg_bytes,
            timeout=120,
        )
        if rc_s != 0:
            raise RuntimeError(f"Failed to stage/validate stock rollback package: {err_s.decode()}")
        stock_staged = True

        watchdog_sh = b"""#!/bin/sh
trap '' HUP
sleep 480
if [ ! -e /tmp/fmx_canary_passed ]; then
  logger -t fmx_watchdog "Canary timeout reached; executing automatic Stock WA.v8.7.25 rollback"
  /sbin/sysupgrade -n /tmp/fmx-panel1-own-stock-return-20261020/stock.bin.gz
fi
"""
        ssh_exec(
            cand_cl,
            "rm -f /tmp/fmx_canary_passed && cat > /tmp/fmx_rollback_watchdog.sh && "
            "chmod 700 /tmp/fmx_rollback_watchdog.sh && "
            "(/tmp/fmx_rollback_watchdog.sh </dev/null >/dev/null 2>&1 & echo $! > /tmp/fmx_rollback_watchdog.pid)",
            stdin_bytes=watchdog_sh,
            timeout=15,
        )
        ev("AP_ROLLBACK_WATCHDOG_ARMED", timeout_s=480)

        # 5c. Verify protected partitions & immutable firmware prefix BEFORE starting radio0 & admitter (so CPU/flash is 100% idle during admission)
        rc_p, out_p, _ = ssh_exec(
            cand_cl,
            "sha256sum /dev/mtd0 /dev/mtd1 /dev/mtd7; head -c 7012352 /dev/mtd2 | sha256sum",
            timeout=120,
        )
        p_lines = [l.strip() for l in out_p.decode("utf-8", "replace").splitlines() if l.strip()]
        sha_map = {"mac80211": mac80211_sha}
        for l in p_lines[:3]:
            p = l.split()
            if len(p) == 2:
                sha_map[p[1]] = p[0]
        sha_map["immutable_prefix"] = p_lines[3].split()[0]
        if (
            sha_map.get("/dev/mtd0") != EXPECTED_OPENWRT_SHA256["/dev/mtd0"]
            or sha_map.get("/dev/mtd1") != EXPECTED_OPENWRT_SHA256["/dev/mtd1"]
            or sha_map.get("/dev/mtd7") != EXPECTED_OPENWRT_SHA256["/dev/mtd7"]
            or sha_map.get("immutable_prefix") != EXPECTED_OPENWRT_SHA256["immutable_prefix"]
        ):
            raise RuntimeError(f"OpenWrt SHA256 verification failed: {sha_map}")
        ev("OPENWRT_RUNTIME_AND_PROTECTED_VERIFIED", sha_map=sha_map)

        # 5d. Synchronously start radio0 with wds=1 and beacon_int=30 in RAM and launch panel1_admitter.sh now that CPU/SPI bus is completely idle
        ssh_exec(
            cand_cl,
            "uci set wireless.default_radio0.wds='1' && uci set wireless.radio0.beacon_int='30' && wifi up radio0",
            timeout=45,
        )
        ap_ready = False
        for _ in range(35):
            rc_u, out_u, _ = ssh_exec(
                cand_cl,
                "grep -q '^wds_sta=1$' /var/run/hostapd-phy0.conf 2>/dev/null && "
                "ubus list hostapd.phy0-ap0 2>/dev/null && "
                "iw dev phy0-ap0 info 2>/dev/null | grep -q 'channel 48 (5240 MHz)' && echo READY_WDS1",
                timeout=10,
            )
            if rc_u == 0 and b"READY_WDS1" in out_u:
                ap_ready = True
                break
            time.sleep(1)
        if not ap_ready:
            raise RuntimeError("hostapd.phy0-ap0 with wds_sta=1 on channel 48 did not come up")
        time.sleep(1)

        rc_a, _, err_a = ssh_exec(
            cand_cl,
            "rm -rf /tmp/fmx-panel1-admitter && mkdir -p /tmp/fmx-panel1-admitter && "
            "chmod 700 /tmp/fmx-panel1-admitter && "
            "cat > /tmp/fmx-panel1-admitter/panel1_admitter.sh && "
            "chmod 700 /tmp/fmx-panel1-admitter/panel1_admitter.sh && "
            "(/tmp/fmx-panel1-admitter/panel1_admitter.sh /tmp/fmx-panel1-admitter </dev/null >/tmp/fmx-panel1-admitter/stdout.log 2>&1 & echo $! > /tmp/fmx-panel1-admitter/pid)",
            stdin_bytes=admitter_bytes,
            timeout=20,
        )
        if rc_a != 0:
            raise RuntimeError(f"Failed to start panel1_admitter.sh: {err_a.decode()}")
        ev("WDS1_AND_ADMITTER_STARTED")

        # 6. Poll up to 360s for both active Stock WA.v8.7.25 CPEs to associate in WDS mode and pass L3 ping
        t_admit = time.monotonic()
        receipt["observations"] = []
        while time.monotonic() - t_admit < 360:
            rc_c, out_c, _ = ssh_exec(
                cand_cl,
                "if ! kill -0 $(cat /tmp/fmx-panel1-admitter/pid 2>/dev/null) 2>/dev/null; then "
                "(/tmp/fmx-panel1-admitter/panel1_admitter.sh /tmp/fmx-panel1-admitter </dev/null >>/tmp/fmx-panel1-admitter/stdout.log 2>&1 & echo $! > /tmp/fmx-panel1-admitter/pid); "
                "fi; "
                "ubus call hostapd.phy0-ap0 get_clients 2>/dev/null || echo '{}'",
                timeout=10,
            )
            _, out_log, _ = ssh_exec(
                cand_cl,
                "tail -n 20 /tmp/fmx-panel1-admitter/actions.log 2>/dev/null || true",
                timeout=10,
            )
            clients_obj = json.loads(out_c.decode("utf-8", "replace") or "{}").get("clients", {})
            wds_auth_macs = [
                m for m, info in clients_obj.items()
                if isinstance(info, dict) and info.get("authorized") is True and info.get("wds") is True
            ]
            obs_row = {
                "utc": utc(),
                "elapsed_s": round(time.monotonic() - t_admit, 1),
                "clients": {
                    m: {
                        "auth": info.get("auth"),
                        "assoc": info.get("assoc"),
                        "authorized": info.get("authorized"),
                        "wds": info.get("wds"),
                        "aid": info.get("aid"),
                        "signal": info.get("signal"),
                        "bytes": info.get("bytes"),
                    }
                    for m, info in clients_obj.items()
                    if isinstance(info, dict)
                },
                "admitter_tail": out_log.decode("utf-8", "replace").strip().splitlines()[-6:],
            }
            receipt["observations"].append(obs_row)
            save()
            log(f"Poll +{obs_row['elapsed_s']}s: wds_auth={wds_auth_macs} | log={obs_row['admitter_tail'][-2:] if obs_row['admitter_tail'] else []}")

            if all(cpe["mac"] in wds_auth_macs for cpe in ACTIVE_CPES):
                ev("BOTH_ACTIVE_CPES_WDS_AUTHORIZED", wds_auth_macs=wds_auth_macs)
                # Verify L3 ping from AP and from Management PC
                ap_pings = {}
                pc_pings = {}
                all_pings_ok = True
                for cpe in ACTIVE_CPES:
                    ip = cpe["ip"]
                    rc_p, out_p, _ = ssh_exec(cand_cl, f"ping -c 2 -W 1 {ip}", timeout=10)
                    ap_pings[ip] = {"rc": rc_p, "out": out_p.decode("utf-8", "replace")}
                    pc_ok = pc_ping(ip, count=4, timeout_ms=1500)
                    pc_pings[ip] = pc_ok
                    if not pc_ok:
                        all_pings_ok = False
                if all_pings_ok:
                    _, st_dump, _ = ssh_exec(
                        cand_cl,
                        "iw dev; for i in $(iw dev | awk '/Interface phy0-ap0/{print $2}'); do echo === $i ===; iw dev $i station dump; done; cat /tmp/fmx-panel1-admitter/actions.log",
                        timeout=20,
                    )
                    receipt["ap_pings"] = ap_pings
                    receipt["pc_pings"] = pc_pings
                    receipt["openwrt_station_dump_and_admitter_log"] = st_dump.decode("utf-8", "replace")

                    # Disarm rollback watchdog, persist wds=1 + panel1_admitter.sh on /overlay, and free RAM
                    persist_cmd = (
                        "touch /tmp/fmx_canary_passed && "
                        "kill $(cat /tmp/fmx_rollback_watchdog.pid 2>/dev/null) 2>/dev/null || true && "
                        "rm -rf /tmp/fmx-panel1-own-stock-return-20261020 /tmp/fmx_rollback_watchdog.sh /tmp/fmx_rollback_watchdog.pid && "
                        "uci commit wireless && "
                        "cp /tmp/fmx-panel1-admitter/panel1_admitter.sh /usr/sbin/panel1_admitter.sh && "
                        "chmod 755 /usr/sbin/panel1_admitter.sh && "
                        "printf '#!/bin/sh\\n/usr/sbin/panel1_admitter.sh /tmp/fmx-panel1-admitter >/tmp/fmx-panel1-admitter.boot.log 2>&1 &\\nexit 0\\n' > /etc/rc.local && "
                        "chmod 755 /etc/rc.local && sync && "
                        "awk '/^MemFree:/{print $2}' /proc/meminfo"
                    )
                    _, out_free, _ = ssh_exec(cand_cl, persist_cmd, timeout=60)
                    rollback_needed = False
                    receipt["status"] = "PASS_PANEL1_GUARIDA_OPENWRT_LIVE_ZERO_TOUCH_WDS_AND_L3_VERIFIED"
                    receipt["memfree_after_cleanup_kib"] = int(out_free.decode().strip())
                    receipt["ended_utc"] = utc()
                    ev("CANARY_PASS_PERSISTED_AND_WATCHDOG_DISARMED", memfree_kib=receipt["memfree_after_cleanup_kib"])
                    cand_cl.close()
                    return 0
            time.sleep(5)

        raise TimeoutError("Timed out waiting for both active CPEs to associate in WDS mode and pass L3 ping")

    except BaseException as exc:
        receipt["error_type"] = type(exc).__name__
        receipt["error"] = str(exc)
        ev("CANARY_GATE_FAILED_INITIATING_AUTOMATIC_STOCK_ROLLBACK", error=str(exc))
        try:
            _, out_log, _ = ssh_exec(
                cand_cl,
                "cat /tmp/fmx-panel1-admitter/actions.log 2>/dev/null || true; echo === EVENTS ===; tail -n 30 /tmp/fmx-panel1-admitter/events.jsonl 2>/dev/null || true",
                timeout=10,
            )
            receipt["failure_admitter_diagnostics"] = out_log.decode("utf-8", "replace")
        except Exception:
            pass
        if rollback_needed:
            try:
                if not stock_staged:
                    ssh_exec(
                        cand_cl,
                        "rm -rf /tmp/fmx-panel1-own-stock-return-20261020 && umask 077 && "
                        "mkdir -p /tmp/fmx-panel1-own-stock-return-20261020 && "
                        "cat > /tmp/fmx-panel1-own-stock-return-20261020/stock.bin.gz && "
                        "chmod 600 /tmp/fmx-panel1-own-stock-return-20261020/stock.bin.gz",
                        stdin_bytes=stock_pkg_bytes,
                        timeout=120,
                    )
                ssh_exec(
                    cand_cl,
                    "kill $(cat /tmp/fmx_rollback_watchdog.pid 2>/dev/null) 2>/dev/null || true; "
                    "(/sbin/sysupgrade -n /tmp/fmx-panel1-own-stock-return-20261020/stock.bin.gz </dev/null >/dev/null 2>&1 &)",
                    timeout=15,
                )
                ev("AUTOMATIC_SYSUPGRADE_STOCK_RETURN_TRIGGERED")
            except Exception as rexc:
                ev("SSH_ROLLBACK_TRIGGER_ERR_RELYING_ON_AP_WATCHDOG", error=str(rexc))
        cand_cl.close()

        # Wait for Stock WA.v8.7.25 to come back and both CPEs to reassociate
        t_rb = time.monotonic()
        while time.monotonic() - t_rb < 300:
            try:
                st_cl, _ = connect_ssh(candidate=False, timeout=6)
                _, out_w, _ = ssh_exec(st_cl, "wstalist", timeout=10)
                st_cl.close()
                st_rows = json.loads(out_w.decode("utf-8", "replace") or "[]")
                st_macs = {r.get("mac", "").lower() for r in st_rows}
                if all(c["mac"] in st_macs and pc_ping(c["ip"]) for c in ACTIVE_CPES):
                    receipt["status"] = "ROLLED_BACK_TO_STOCK_WA8725_AND_SERVICE_RESTORED"
                    receipt["ended_utc"] = utc()
                    ev("STOCK_WA8725_AND_CPE_SERVICE_RESTORED_AFTER_ROLLBACK")
                    return 1
            except Exception:
                pass
            time.sleep(5)
        receipt["status"] = "ROLLBACK_IN_PROGRESS_TIMEOUT"
        receipt["ended_utc"] = utc()
        save()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
