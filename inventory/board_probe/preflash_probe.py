#!/usr/bin/env python3
"""Read-only pre-flash probe for airOS WA-board units (FMX-0002 evidence).

Summary: collects every fact needed to decide an OpenWrt install path and to prove a
bootloader recovery route, WITHOUT writing anything to the device. Pulls u-boot (mtd0)
to the host for offline analysis of the recovery/TFTP surface, and fingerprints
/bin/ubntbox so the correct signature-check patch (if any) can be identified.
Keywords: FMX-0002, preflash, ubntbox, fwupdate.real, u-boot, TFTP recovery, urescue,
mtd map, LAP-120, read-only.
Read when: before any flash of a lab radio, or to re-verify a unit's recovery posture.

SAFETY ENVELOPE (enforced, not advisory):
  * every remote command is a read: cat / md5sum / ls / dmesg. No writes, ever.
  * mtd devices are only ever read (`cat /dev/mtdN`); nothing is written.
  * the script ABORTS if the unit reports associated stations (it is then not a lab unit).
  * no reboot, no config change, no fwupdate invocation.

Usage:
    python preflash_probe.py [--host 192.168.1.20] [--user ubnt] [--password ubnt]
                             [--outdir <repo>/research/raw/hardware]
"""

from __future__ import annotations

import argparse

import hashlib
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTDIR = ROOT / "research" / "raw" / "hardware"

# Artifacts pulled to the host for offline analysis. Reading is safe; the list is kept
# minimal on purpose. u-boot answers "what recovery path does the bootloader offer?" and
# ubntbox answers "which signature-check patch does THIS airOS build need?".
PULL_ARTIFACTS = [
    ("/dev/mtd0", "mtd0-u-boot"),
    ("/bin/ubntbox", "bin-ubntbox"),
]

# (section label, command). Strictly read-only. Anything not here is not authorised.
PROBES = [
    ("airos_version", "cat /etc/version 2>/dev/null; cat /usr/lib/version 2>/dev/null"),
    ("board_identity", "cat /proc/ubnthal/system.info 2>/dev/null"),
    ("flash_map", "cat /proc/mtd 2>/dev/null"),
    ("kernel_cmdline", "cat /proc/cmdline 2>/dev/null"),
    # SAFETY GATE: parsed below. Non-zero => abort.
    ("assoc_stations", "wstalist 2>/dev/null | grep -c mac; iwconfig ath0 2>/dev/null | head -5"),
    (
        "ubntbox_fingerprint",
        "ls -la /bin/ubntbox /sbin/fwupdate* /bin/fwupdate* 2>/dev/null; "
        "md5sum /bin/ubntbox 2>/dev/null; "
        "cat /proc/ubnthal/system.info 2>/dev/null | grep -i version",
    ),
    (
        "recovery_binaries",
        "ls -la /sbin/urescue /bin/urescue /usr/sbin/urescue 2>/dev/null; "
        "which urescue tftp tftpd 2>/dev/null",
    ),
    (
        "bootloader_hints",
        "dmesg | grep -iE 'u-boot|bootloader|MyLoader|flash_size passed' | head -10; "
        "cat /proc/ubnthal/board.info 2>/dev/null | head -40",
    ),
    ("mtd_ro_status", "cat /sys/class/mtd/mtd0/flags 2>/dev/null; ls -la /dev/mtd* 2>/dev/null | head -20"),
    ("free_tmp", "df -h /tmp 2>/dev/null; free 2>/dev/null"),
]

# Fragments that are dangerous wherever they appear (they ARE the write).
BANNED_FRAGMENTS = ("of=/dev/mtd", "of=/dev/mtdblock", ">/dev/mtd", "mtd write", "mtd erase")
# Executables that must never be INVOKED. Matched in command position only, so that
# `ls /bin/fwupdate*` and `which urescue` stay legal -- naming a binary is not running it.
BANNED_EXECUTABLES = {
    "fwupdate", "fwupdate.real", "ubntbox", "flashcp", "mtd",
    "reboot", "halt", "poweroff", "cfgmtd", "ubntconf", "dd",
}
_SEPARATORS = (";", "&&", "||", "|", "\n")


def _command_positions(cmd: str) -> list[str]:
    """Split a shell string into segments and return the first token of each."""
    segments = [cmd]
    for sep in _SEPARATORS:
        segments = [piece for seg in segments for piece in seg.split(sep)]
    heads = []
    for seg in segments:
        tokens = seg.strip().split()
        if not tokens:
            continue
        # skip leading env assignments (VAR=value cmd)
        idx = 0
        while idx < len(tokens) and "=" in tokens[idx] and not tokens[idx].startswith("/"):
            idx += 1
        if idx < len(tokens):
            heads.append(tokens[idx].rsplit("/", 1)[-1].lower())
    return heads


def assert_read_only(cmd: str, allow: frozenset[str] = frozenset()) -> None:
    low = cmd.lower()
    for bad in BANNED_FRAGMENTS:
        if bad in low:
            raise SystemExit(f"REFUSED: probe command contains a write primitive: {cmd!r}")
    for head in _command_positions(cmd):
        if head in BANNED_EXECUTABLES and head not in allow:
            raise SystemExit(f"REFUSED: probe command invokes {head!r}: {cmd!r}")


class Unit:
    def __init__(self, host: str, user: str, password: str) -> None:
        import paramiko

        self.host = host
        self.c = paramiko.SSHClient()
        self.c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.c.connect(
            host,
            username=user,
            password=password,
            timeout=20,
            look_for_keys=False,
            allow_agent=False,
        )

    def run(self, cmd: str, binary: bool = False, allow: frozenset[str] = frozenset()):
        assert_read_only(cmd, allow)
        _, out, err = self.c.exec_command(cmd, timeout=120)
        data = out.read()
        errtxt = err.read().decode("utf-8", "replace")
        if binary:
            return data, errtxt
        return data.decode("utf-8", "replace"), errtxt

    def close(self) -> None:
        self.c.close()


def pull_file(unit: Unit, path: str) -> bytes:
    """Read a device or file off the unit over the SSH channel.

    airOS 8.5.12 busybox has no `base64`, and the SSH channel is binary-safe, so a plain
    `cat` is both the simplest and the least surprising thing to do. `cat` cannot write.
    """
    data, _ = unit.run(f"cat {path}", binary=True)
    return data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="192.168.1.20")
    ap.add_argument("--user", default="ubnt")
    ap.add_argument("--password", default="ubnt")
    ap.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    ap.add_argument("--label", default="lab-lap120")
    ap.add_argument("--skip-pull", action="store_true", help="do not download u-boot")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

    unit = Unit(args.host, args.user, args.password)
    print(f"connected to {args.host}\n")

    report = [f"===== FUTURAMAX PRE-FLASH PROBE {stamp} host={args.host} ====="]
    sections: dict[str, str] = {}

    for label, cmd in PROBES:
        out, err = unit.run(cmd)
        sections[label] = out
        report.append(f"\n--- {label} ---\n{out.rstrip()}")
        if err.strip():
            report.append(f"[stderr] {err.strip()}")

    # SAFETY GATE -- refuse to continue on a unit with clients.
    first_line = sections.get("assoc_stations", "0").strip().splitlines()
    try:
        n_sta = int(first_line[0].strip()) if first_line else 0
    except ValueError:
        n_sta = 0
    if n_sta > 0:
        print(f"ABORT: {n_sta} associated stations -- this is not a lab unit", file=sys.stderr)
        unit.close()
        return 2
    report.append(f"\n--- safety_gate ---\nassociated stations: {n_sta} (OK, lab unit)")

    # Pull u-boot + ubntbox for offline recovery-surface analysis.
    if not args.skip_pull:
        for remote, name in PULL_ARTIFACTS:
            blob = pull_file(unit, remote)
            if not blob:
                report.append(f"\n--- pulled {remote} ---\nFAILED: 0 bytes")
                print(f"WARNING: {remote} returned 0 bytes", file=sys.stderr)
                continue
            digest = hashlib.sha256(blob).hexdigest()
            path = outdir / f"{args.label}-{name}-{stamp}.bin"
            path.write_bytes(blob)
            report.append(
                f"\n--- pulled {remote} ---\n"
                f"bytes: {len(blob)}\nsha256: {digest}\nsaved: {path.name}"
            )
            print(f"pulled {remote}: {len(blob)} bytes  sha256={digest[:16]}...")

    unit.close()

    report.append("\n===== END =====")
    text = "\n".join(report)
    outpath = outdir / f"{args.label}-preflash-{stamp}.txt"
    outpath.write_text(text, encoding="utf-8")
    print(f"\nwrote {outpath}")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
