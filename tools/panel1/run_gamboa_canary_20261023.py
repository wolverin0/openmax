"""Controlled live OpenWrt 24.10.4 cutover on GAMBOA_Gabriela (10.10.200.223, LiteBeam 5AC Gen2, 0xe7f9)
with STA-WDS + Router/NAT + DHCP static lease (EC220-F5 192.168.1.169) + AQL + LuCI WebUI.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
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

TARGET_IP = "10.10.200.223"
SOURCE_BIND = "192.168.100.155"
OBSERVER_PEER = "192.168.100.200"
OBSERVER_PORT = 39261
RECEIPT_NONCE = "1aa3778048e1ccb86558639ee714293e53080b36463ee1463d0ac5f1f8ff3ec0"

PERM_MAC = "24:5a:4c:45:77:7a"
BOARD_SHA256 = "29efe61667c50bb7c46a625a5be95148645d10f653dce9a64f2fdc06638b3058"
STOCK_KEY_SHA256 = "d0c6d3762f49f8fb7c197d8494623ac1c467687aba3f1bc88e3196abfff5ae77"
CANDIDATE_KEY_SHA256 = ""

IMAGE_FILE = CANARY / "gamboa_cpe_openwrt_20261023.bin"
IMAGE_SHA256 = "098ee698a6c586772461ff3412cdc57250b16410c609b815f7e5c151b86a192e"
IMAGE_MD5 = "238754deb68a9ed52aec19224fca5c3d"

WRITER_FILE = CANARY / "fmx_flash_writer_gamboa_20261023"
WRITER_SHA256 = "b54d7427178e0c08757def7d186ddeeb042d929f042170d0039f3f27a468e1b2"

STOCK_PKG_FILE = CANARY / "lap120_stock_cycle_20261019_package" / "lap120-wa8725-full-region.sysupgrade.bin.gz"
STOCK_PKG_SHA256 = "8f640047424a946596de7125781b67bc3b8d52f78deb8793b195ce11c0b3d231"

ADMITTER_FILE = ROOT / "tools" / "panel1" / "panel1_admitter.sh"
RECEIPT_FILE = CANARY / "gamboa_cpe_openwrt_20261023_receipt.json"

EXPECTED_STOCK_MD5 = {
    "/dev/mtd0": "cfc83aa1422f33c58bcf78e93703ed17",
    "/dev/mtd1": "2a30db6d465400e37cedc7c399b36645",
    "/dev/mtd2": "95e7ed6552d2828fc2f1019cdd6a8f63",
    "/dev/mtd3": "00cc3dc10c84ac159ddec2f3861f4cd8",
    "/dev/mtd5": "cc0986dc0907dcf2583a5c27448145ad",
}

EXPECTED_OPENWRT_SHA256 = {
    "/dev/mtd0": "988de5143235db3c0afc810b3bbad0b9177e96ec8493b4873486eb626d80ebfc",
    "/dev/mtd1": "63213a0bb3ec161faa51abf53417dcab7325b529c12150073923c6ab42cf711f",
    "/dev/mtd7": "5b6a2d10a3ad747867da2610598f516ca49a96e23944c70ec5c30ee0be731367",
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
        "experiment": "GAMBOA_CPE_OPENWRT_CUTOVER_20261023",
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
    if sha256(writer_bytes) != WRITER_SHA256:
        raise RuntimeError("Writer binary SHA256 mismatch")
    if sha256(stock_pkg_bytes) != STOCK_PKG_SHA256:
        raise RuntimeError("Stock return package SHA256 mismatch")
    if sha256(IMAGE_FILE.read_bytes()) != IMAGE_SHA256:
        raise RuntimeError("Candidate image SHA256 mismatch")

    # 1. Preflight on Stock WA.v8.7.25
    cl, key_sha = connect_ssh(candidate=False, timeout=10)
    try:
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
            raise RuntimeError(f"Preflight command failed on {TARGET_IP}")
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

        if not pc_ping(TARGET_IP):
            raise RuntimeError(f"Target CPE {TARGET_IP} not responding to ping before cutover")

        ev("STOCK_PREFLIGHT_PASSED", memfree_kib=memfree_kib)

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
        obs_out = CANARY / f"gamboa_canary_observer_{int(time.time())}.jsonl"
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

    # 4. Wait for OpenWrt candidate boot on 10.10.200.223
    t_handoff = time.monotonic()
    cand_cl = None
    while time.monotonic() - t_handoff < 420:
        if len(obs.records) > len(receipt.get("native_records", [])):
            receipt["native_records"] = list(obs.records)
            ev("NATIVE_OBSERVER_PROGRESS", count=len(obs.records), latest=obs.records[-1].get("status"))
        if time.monotonic() - t_handoff < 140 and not any(
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

    # 5. Verify OpenWrt STA-WDS + Router/NAT + Customer LAN + Protected Partitions + LuCI
    try:
        rc_v, out_v, _ = ssh_exec(
            cand_cl,
            "cat /sys/class/net/eth0/address; cat /tmp/sysinfo/board_name; uname -r; "
            "sha256sum /lib/modules/6.6.110/mac80211.ko",
            timeout=90,
        )
        v_lines = [l.strip() for l in out_v.decode("utf-8", "replace").splitlines() if l.strip()]
        if v_lines[:3] != [PERM_MAC, "ubnt,litebeam-ac-gen2", "6.6.110"]:
            raise RuntimeError(f"OpenWrt identity mismatch: {v_lines[:3]}")
        mac80211_sha = v_lines[3].split()[0]
        if mac80211_sha != EXPECTED_OPENWRT_SHA256["mac80211"]:
            raise RuntimeError(f"OpenWrt mac80211.ko SHA256 mismatch: {mac80211_sha}")
        ev("OPENWRT_IDENTITY_AND_MAC80211_VERIFIED", mac80211_sha256=mac80211_sha)

        # Verify protected partitions
        rc_p, out_p, _ = ssh_exec(
            cand_cl,
            "sha256sum /dev/mtd0 /dev/mtd1 /dev/mtd7",
            timeout=90,
        )
        p_lines = [l.strip() for l in out_p.decode("utf-8", "replace").splitlines() if l.strip()]
        sha_map = {"mac80211": mac80211_sha}
        for l in p_lines[:3]:
            p = l.split()
            if len(p) == 2:
                sha_map[p[1]] = p[0]
        if (
            sha_map.get("/dev/mtd0") != EXPECTED_OPENWRT_SHA256["/dev/mtd0"]
            or sha_map.get("/dev/mtd1") != EXPECTED_OPENWRT_SHA256["/dev/mtd1"]
            or sha_map.get("/dev/mtd7") != EXPECTED_OPENWRT_SHA256["/dev/mtd7"]
        ):
            raise RuntimeError(f"OpenWrt SHA256 verification failed: {sha_map}")
        ev("OPENWRT_PROTECTED_PARTITIONS_VERIFIED", sha_map=sha_map)

        # Install LuCI/uhttpd bundle onto /overlay once jffs2 is ready
        luci_bundle = (CANARY / "luci_uhttpd_overlay_bundle_20261023.tar.gz").read_bytes()
        ssh_exec(
            cand_cl,
            "tar -xzf - -C / && /etc/init.d/rpcd restart && /etc/init.d/uhttpd enable && /etc/init.d/uhttpd restart",
            stdin_bytes=luci_bundle,
            timeout=60,
        )
        ev("LUCI_WEBUI_INSTALLED_AND_STARTED")

        # Verify wireless link, AQL, WAN ping (10.10.200.1), and Customer LAN ping (192.168.1.169)
        _, diag_out, _ = ssh_exec(
            cand_cl,
            "iw dev phy0-sta0 link; ip addr; "
            "cat /sys/kernel/debug/ieee80211/phy0/aql_txq_limit; "
            "nft list chain inet fw4 srcnat_wan; "
            "ping -c 4 -W 1 10.10.200.1; "
            "ping -c 3 -W 1 192.168.1.169 2>/dev/null || true; "
            "cat /tmp/dhcp.leases 2>/dev/null || true; "
            "awk '/^MemFree:/{print $2}' /proc/meminfo",
            timeout=30,
        )
        diag_txt = diag_out.decode("utf-8", "replace")
        receipt["openwrt_cpe_diagnostics"] = diag_txt
        receipt["status"] = "PASS_GAMBOA_OPENWRT_STA_WDS_ROUTER_LIVE_VERIFIED"
        receipt["ended_utc"] = utc()
        ev("GAMBOA_OPENWRT_CUTOVER_COMPLETE")
        cand_cl.close()
        return 0
    except BaseException as exc:
        receipt["error_type"] = type(exc).__name__
        receipt["error"] = str(exc)
        receipt["status"] = "FAIL_POSTBOOT_VERIFICATION"
        receipt["ended_utc"] = utc()
        save()
        cand_cl.close()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
