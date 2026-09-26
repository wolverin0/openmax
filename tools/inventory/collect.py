#!/usr/bin/env python3
"""FuturaMAX G04: read-only hardware inventory collector for airOS units.

Covers: SSH (dropbear) collection of board identity, radio PCI/chip ID, firmware version,
driver stack, airMAX module parameters, SoC/clocks/memory, flash map, GPS and spectral
capability. Keywords: inventory, LAP-GPS, QCA988x, ubnt_poll_host, read-only, G04.
Read when: closing the hardware-identity gap on real units.
SAFETY: every command is cat/dmesg/grep/ls. Nothing writes flash, config, or reboots.
Credentials come from $UBNT_PASS and are never written to disk. Verdict: CURRENT.

Usage:  UBNT_PASS='...' python tools/inventory/collect.py [host_label ...]
"""
from __future__ import annotations

import os
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "research" / "raw" / "hardware"

# label -> host. Production units; read-only access authorised by the operator 2026-08-08.
TARGETS = {
    "lap-gps": "10.10.100.181",
    "liteap-ac": "10.10.100.83",
    "litebeam-5ac-lr": "10.10.200.9",
    "litebeam-5ac": "10.10.110.162",
    "rocket-prism-2ac": "10.10.100.3",
    "nano-ac": "10.10.200.163",
}

# (section label, command). Strictly read-only.
PROBES = [
    ("airos_version", "cat /etc/version 2>/dev/null; cat /usr/lib/version 2>/dev/null"),
    ("board_info", "cat /proc/ubnthal/board.info 2>/dev/null"),
    ("board_inc", "cat /proc/ubnthal/board.inc 2>/dev/null | head -80"),
    ("board_dmesg", "dmesg | grep -iE 'ubnthal|board found|sysid|Ubiquiti Networks.*board' | head -12"),
    ("radio_identity", "dmesg | grep -iE 'qca98|chip_id|TARGET TYPE|Radio:|PCIe WLAN|U-AME|subsystem' | head -25"),
    ("radio_firmware", "dmesg | grep -iE 'ol_transfer_bin_file|firmware ver|FIRMWARE:|Download Firmware|wmi|htt' | head -25"),
    ("driver_stack", "dmesg | grep -iE 'ath_pci:|ath_hal:|ath10k|ath_dev|ath_rate' | head -20"),
    ("airmax_module", "dmesg | grep -iE 'ubnt_poll_host|ubnt-poll-host' | head -40"),
    ("lsmod", "lsmod 2>/dev/null | head -40"),
    ("cpu", "cat /proc/cpuinfo 2>/dev/null | head -10"),
    ("clocks_mem", "dmesg | grep -iE 'ath_sys_frequency|Clocks:|Determined physical RAM|CPU revision|SoC:' | head -10; grep MemTotal /proc/meminfo"),
    ("flash_map", "cat /proc/mtd 2>/dev/null"),
    ("gps", "dmesg | grep -i gps | head -20; ls -la /dev/gps* /dev/pps* 2>/dev/null; cat /proc/ubnthal/board.info 2>/dev/null | grep -i gps"),
    ("spectral", "dmesg | grep -iE 'spectral|SPECTRAL|HAL_CAP' | head -25"),
    ("wireless_mode", "iwconfig 2>/dev/null | head -30"),
    ("pci", "cat /proc/bus/pci/devices 2>/dev/null | head -5"),
]


def collect(label: str, host: str, password: str) -> tuple[str, bool]:
    import paramiko

    lines = [
        f"# FuturaMAX read-only inventory",
        f"# label: {label}",
        f"# collected_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"# method: SSH (paramiko), read-only commands only",
        "",
    ]
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect(host, username="ubnt", password=password, timeout=20,
                  banner_timeout=25, auth_timeout=25, look_for_keys=False, allow_agent=False)
    except Exception as ex:
        lines.append(f"CONNECTION FAILED: {type(ex).__name__}: {ex}")
        return "\n".join(lines), False

    t = c.get_transport()
    lines.append(f"ssh_banner: {t.remote_version if t else '?'}\n")
    for name, cmd in PROBES:
        try:
            _, o, e = c.exec_command(cmd, timeout=30)
            out = o.read().decode("utf-8", errors="replace").rstrip()
            err = e.read().decode("utf-8", errors="replace").strip()
        except Exception as ex:
            out, err = "", f"{type(ex).__name__}: {ex}"
        lines.append(f"===== {name} =====")
        lines.append(out if out else "(empty)")
        if err and "No such file" not in err and "not found" not in err:
            lines.append(f"[stderr] {err}")
        lines.append("")
    c.close()
    return "\n".join(lines), True


def main() -> int:
    password = os.environ.get("UBNT_PASS")
    if not password:
        print("FATAL: set UBNT_PASS in the environment (never hard-code it)", file=sys.stderr)
        return 1
    wanted = sys.argv[1:] or list(TARGETS)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for label in wanted:
        host = TARGETS.get(label)
        if not host:
            print(f"skip unknown label {label}")
            continue
        text, ok = collect(label, host, password)
        dest = OUTDIR / f"{label}-{date}.txt"
        dest.write_text(text, encoding="utf-8")
        status = "OK " if ok else "FAIL"
        print(f"[{status}] {label:<18} -> {dest.relative_to(ROOT).as_posix()} ({len(text)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
