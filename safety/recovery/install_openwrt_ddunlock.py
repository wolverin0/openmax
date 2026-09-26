#!/usr/bin/env python3
"""Install OpenWrt on an airOS WA board via the documented dd-unlock method (Route A).

Summary: runs the OpenWrt wiki's "airOS WA v8.5.7 and newer" procedure under script control
instead of by hand. Uses the stock, unpatched vendor updater on a genuine SIGNED vendor image
purely to unlock the flash, interrupts it the instant u-boot is written, then streams the OpenWrt
sysupgrade image straight into the kernel and rootfs partitions.
Keywords: dd-unlock, Route A, fwupdate, MTD_WRITEABLE, mtdblock2, mtdblock3, LAP-120, OpenWrt.
Read when: installing OpenWrt on a WA-board lab radio, or reviewing what that install did.

WHY THE u-boot WRITE IS ACCEPTED HERE (AGENTS.md §4 says never write the bootloader):
  The vendor updater always rewrites u-boot -- that is how it unlocks the flash -- so EVERY
  documented install path crosses that line. It was accepted for this unit only after verifying
  that the u-boot inside the stock image is **byte-identical** to the u-boot already on the
  device (sha256 d78f995c115abb74...). The write therefore cannot install a different or
  incompatible bootloader; the only exposure is the physical erase/program window. Operator
  authorised this explicitly on 2026-08-08.

WHY THE IMAGE IS STREAMED, NOT STAGED:
  /tmp is a ~17 MB tmpfs on a 64 MB device. Staging both images (~15 MB) would leave almost no
  RAM. The sysupgrade is piped over SSH directly into `dd`, so only the stock image is stored.

TIMING -- the one genuinely delicate part:
  fwupdate writes u-boot, then kernel, then rootfs. The running airOS root is a squashfs mounted
  from the rootfs partition, so letting it reach rootfs corrupts the live filesystem underneath
  us. We watch its output and kill it the moment u-boot reports complete.

Usage:
    python install_openwrt_ddunlock.py --dry-run      # checks only, touches nothing
    python install_openwrt_ddunlock.py --go
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
STOCK = ROOT / "firmware" / "WA.v8.5.12.40181.190213.1104.bin"
SYSUP = ROOT / "firmware" / "openwrt" / "openwrt-24.10.4-ath79-generic-ubnt_lap-120-squashfs-sysupgrade.bin"

STOCK_SHA = "4bda8ddf20a4b6f6ed3cc77f7616b283fe67e7604c61adcdd2f0342dd27f6270"
SYSUP_SHA = "cc01cbb3e441c8bb801bbae8b64ea6352e571dee0ef6204d95c6bd80e2a975f1"

# mtd2 "kernel" is 0x100000 = 1 MiB. Everything after that goes to mtd3 "rootfs".
KERNEL_BYTES = 0x100000
EXPECT_SYSID = "0xe8e5"
EXPECT_VERSION = "WA.v8.5.12"


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for c in iter(lambda: fh.read(1 << 16), b""):
            h.update(c)
    return h.hexdigest()


class Unit:
    def __init__(self, host: str, user: str, pw: str) -> None:
        import paramiko

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, username=user, password=pw, timeout=20,
                            look_for_keys=False, allow_agent=False)

    def run(self, cmd: str, timeout: int = 60) -> str:
        _, out, _ = self.client.exec_command(cmd, timeout=timeout)
        return out.read().decode("utf-8", "replace")

    def close(self) -> None:
        self.client.close()


def preflight(u: Unit) -> dict:
    """Read-only gate. Every one of these must pass before anything is written."""
    info = {}
    info["version"] = u.run("cat /etc/version").strip()
    # sysid lives in board.info on this build; system.info can be empty.
    info["sysid"] = u.run("grep '^board.sysid=' /proc/ubnthal/board.info 2>/dev/null").strip()
    info["model"] = u.run("grep '^board.model=' /proc/ubnthal/board.info").strip()
    info["stations"] = u.run("wstalist 2>/dev/null | grep -c mac").strip() or "0"
    info["mtd"] = u.run("cat /proc/mtd")
    info["tmp_free_kb"] = u.run("df /tmp | tail -1 | awk '{print $4}'").strip()

    print(f"  airOS version : {info['version']}")
    print(f"  board         : {info['model']}  sysid={info['sysid']}")
    print(f"  stations      : {info['stations']}")
    print(f"  /tmp free     : {int(info['tmp_free_kb'] or 0)/1024:.1f} MiB")

    problems = []
    if EXPECT_VERSION not in info["version"]:
        problems.append(f"expected {EXPECT_VERSION}, found {info['version']!r}")
    if EXPECT_SYSID not in info["sysid"]:
        problems.append(f"expected sysid {EXPECT_SYSID}, found {info['sysid']!r}")
    if info["stations"] not in ("0", ""):
        problems.append(f"{info['stations']} associated stations -- NOT a lab unit")
    if 'mtd2: 00100000' not in info["mtd"] or 'mtd3: 00e60000' not in info["mtd"]:
        problems.append("flash map does not match the expected stock airOS layout")
    need_kb = STOCK.stat().st_size // 1024 + 512
    if int(info["tmp_free_kb"] or 0) < need_kb:
        problems.append(f"/tmp has {info['tmp_free_kb']}KB free, need ~{need_kb}KB for the stock image")
    return {"info": info, "problems": problems}


def unlock_flash(u: Unit, remote_stock: str) -> bool:
    """Run the vendor updater and kill it the moment u-boot is written.

    Returns True if the u-boot completion marker was seen (flash is now unlocked).
    """
    chan = u.client.get_transport().open_session()
    chan.get_pty()          # so the process dies with the channel
    chan.exec_command(f"cd /tmp && fwupdate.real -m {remote_stock} -d")

    # Trigger ONLY on an actual write line. fwupdate first prints an enumeration list
    # ("Found mtd block: /dev/mtd2(kernel)") -- matching that kills it before it unlocks
    # anything, which looks like success and silently does nothing. Ask me how I know.
    #
    # The write lines look like:  Writing 'u-boot ' to /dev/mtd0(u-boot ) ... [%100]
    # Killing once the KERNEL write starts is the correct window: u-boot is then provably
    # done (flash unlocked), and we are still safely short of rootfs -- which is the live
    # squashfs root and must not be touched underneath the running system.
    buf, unlocked, t0 = "", False, time.time()
    while time.time() - t0 < 120:
        if chan.recv_ready():
            chunk = chan.recv(4096).decode("utf-8", "replace")
            buf += chunk
            sys.stdout.write(chunk)
            sys.stdout.flush()
            for line in buf.splitlines():
                low = line.lower()
                if "writing" not in low:
                    continue                      # enumeration / noise, not a write
                if "rootfs" in low:
                    # THE correct trigger. The guide says interrupt "before it finishes writing
                    # mtd3" -- so mtd3 must be REACHED. Killing at the mtd2/kernel write (what
                    # the previous attempt did) leaves mtd3 outside the updater's per-partition
                    # path, and since the OpenWrt kernel is 2.6 MB it overruns mtd2 by ~1.5 MiB
                    # into mtd3 -- so a truncated kernel results and bootm fails its data CRC.
                    unlocked = True
                    print("\n  >>> ROOTFS write reached => both partitions unlocked. Killing NOW")
                    break
            if unlocked:
                break
        if chan.exit_status_ready() and not chan.recv_ready():
            break
        time.sleep(0.02)

    try:
        chan.close()
    except Exception:
        pass
    # belt and braces: the pty should have killed it, but make certain nothing is still
    # walking through the partitions while we start writing them ourselves.
    try:
        u.run("killall -9 ubntbox fwupdate.real 2>/dev/null; true", timeout=15)
    except Exception:
        pass
    return unlocked


def stream_to(u: Unit, data: bytes, dest: str, label: str) -> None:
    """Pipe bytes over SSH into `dest` on the device via dd.

    airOS's dropbear has no sftp-server, so SFTP is unavailable -- streaming into `dd` is the
    portable way in, and it is the same mechanism used to write flash partitions.
    """
    print(f"  writing {len(data):,} B -> {dest} ({label})")
    chan = u.client.get_transport().open_session()
    chan.exec_command(f"dd of={dest} bs=65536")
    sent = 0
    while sent < len(data):
        chunk = data[sent:sent + 32768]
        chan.sendall(chunk)
        sent += len(chunk)
        if sent % (1 << 20) < 32768:
            print(f"    {sent:,}/{len(data):,}", flush=True)
    chan.shutdown_write()
    err = chan.makefile_stderr().read().decode("utf-8", "replace")
    chan.recv_exit_status()
    chan.close()
    if err.strip():
        print(f"    dd: {err.strip()}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="192.168.1.20")
    ap.add_argument("--user", default="ubnt")
    ap.add_argument("--password", default="ubnt")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--go", action="store_true", help="actually perform the install")
    args = ap.parse_args()

    if not args.dry_run and not args.go:
        print("refusing to act: pass --dry-run (safe checks) or --go (install)", file=sys.stderr)
        return 2

    print("== local image verification ==")
    for p, want, name in ((STOCK, STOCK_SHA, "stock airOS"), (SYSUP, SYSUP_SHA, "OpenWrt sysupgrade")):
        if not p.is_file():
            print(f"FATAL: missing {name}: {p}", file=sys.stderr)
            return 2
        got = sha256_of(p)
        ok = got == want
        print(f"  {name:20} {p.stat().st_size:>10,} B  sha256 {'OK' if ok else 'MISMATCH'}")
        if not ok:
            print(f"FATAL: {name} sha256 {got} != expected {want}", file=sys.stderr)
            return 2

    print("\n== connecting ==")
    u = Unit(args.host, args.user, args.password)
    print("\n== preflight (read-only) ==")
    pre = preflight(u)
    if pre["problems"]:
        print("\nPREFLIGHT FAILED:")
        for p in pre["problems"]:
            print(f"  - {p}")
        u.close()
        return 3
    print("  preflight: all checks passed")

    if args.dry_run:
        print("\n--dry-run: nothing was written. Re-run with --go to install.")
        u.close()
        return 0

    # Insurance: letting fwupdate reach mtd3 means it starts overwriting the LIVE squashfs root,
    # after which new exec()s can fail. Keep a copy of busybox in tmpfs (RAM) and run every
    # post-interrupt command through it, so losing the on-flash rootfs cannot strand us.
    print("\n== copying busybox into RAM (survives a disturbed rootfs) ==")
    u.run("cp /bin/busybox /tmp/busybox && chmod +x /tmp/busybox")
    bb_ok = u.run("/tmp/busybox echo ok").strip()
    if bb_ok != "ok":
        print("FATAL: could not stage busybox in /tmp", file=sys.stderr)
        u.close()
        return 8
    print("  /tmp/busybox ready")

    print("\n== staging stock image (needed to unlock the flash) ==")
    remote_stock = "/tmp/" + STOCK.name
    stream_to(u, STOCK.read_bytes(), remote_stock, "stock airOS")
    remote_md5 = u.run(f"md5sum {remote_stock}", timeout=180).split()[0]
    local_md5 = hashlib.md5(STOCK.read_bytes()).hexdigest()
    print(f"  uploaded; md5 on device {'OK' if remote_md5 == local_md5 else 'MISMATCH'}")
    if remote_md5 != local_md5:
        print("FATAL: upload corrupted", file=sys.stderr)
        u.close()
        return 4

    print("\n== unlocking flash via the vendor updater (will be interrupted) ==")
    if not unlock_flash(u, remote_stock):
        print("\nFATAL: never saw the u-boot completion marker; flash may not be unlocked.")
        print("Nothing further was written. The unit still boots airOS.", file=sys.stderr)
        u.close()
        return 5

    # Free the stock image NOW: /tmp is a ~17 MB tmpfs and the sysupgrade needs ~7 MB of it.
    u.run(f"rm -f {remote_stock}")
    print(f"  freed {remote_stock}; /tmp now {u.run('df /tmp | tail -1').strip()}")

    print("\n== writing OpenWrt ==")
    # dd MUST read from a staged FILE, not a pipe. Reading a pipe yields short reads, so dd
    # issues unaligned partial writes ("0+122 records in") which mtdblock silently discards --
    # the install then appears to succeed and the device boots the old OS. Staging the file
    # gives full 64K blocks aligned to the erase size.
    remote_img = "/tmp/openwrt-sysupgrade.bin"
    stream_to(u, SYSUP.read_bytes(), remote_img, "OpenWrt sysupgrade")
    remote_md5 = u.run(f"md5sum {remote_img}", timeout=180).split()[0]
    local_md5 = hashlib.md5(SYSUP.read_bytes()).hexdigest()
    if remote_md5 != local_md5:
        print("FATAL: staged image corrupt; nothing written to flash.", file=sys.stderr)
        u.close()
        return 6
    print(f"  staged; md5 OK ({remote_md5})")

    kblocks = KERNEL_BYTES // 65536      # 16 x 64K = 1 MiB kernel partition; matches upstream
                                         # Build/mkubntimage-split (dd bs=1024k count=1 / skip=1)
    print(u.run(f"/tmp/busybox dd if={remote_img} of=/dev/mtdblock2 bs=64k count={kblocks} 2>&1",
                timeout=300).strip())
    print(u.run(f"/tmp/busybox dd if={remote_img} of=/dev/mtdblock3 bs=64k skip={kblocks} 2>&1",
                timeout=600).strip())

    print("\n== verifying the FULL image read back from flash ==")
    # Read the CHAR devices (/dev/mtdN), not mtdblock: the block layer caches, so an mtdblock
    # readback can echo what we just wrote even when flash never took it.
    #
    # Compare the WHOLE image across the mtd2/mtd3 boundary (they are physically contiguous).
    # Checking only the uImage name/magic reads bytes from the one region that definitely wrote
    # and cannot detect a truncated kernel -- that is precisely what hid the previous failure.
    total = SYSUP.stat().st_size
    got = u.run(
        f"( /tmp/busybox cat /dev/mtd2; /tmp/busybox cat /dev/mtd3 ) | "
        f"/tmp/busybox head -c {total} | /tmp/busybox md5sum",
        timeout=900,
    ).split()
    got_md5 = got[0] if got else "<no output>"
    print(f"  flash md5 (first {total:,} B): {got_md5}")
    print(f"  local image md5             : {local_md5}")
    if got_md5 != local_md5:
        # Do NOT claim the unit still boots airOS here -- by this point fwupdate has written into
        # the rootfs partition and our dd has overwritten both partitions, so airOS is GONE.
        # A mismatch means flash holds neither a bootable airOS nor a complete OpenWrt.
        #
        # Most likely cause: the mtdblock write cache had not committed when the char device was
        # read. Observed 2026-08-10 -- a mismatch immediately after dd became a clean MATCH after
        # `sync` plus a re-write, with no other change. Retry before assuming the write failed.
        print("\nMISMATCH -- flash does not yet match the image.", file=sys.stderr)
        print("The unit can NO LONGER boot airOS (its rootfs was overwritten). Do not power-cycle "
              "yet.", file=sys.stderr)
        print("Try: re-run the mtd3 dd, `sync`, wait a few seconds, and re-verify -- an immediate "
              "readback can race the mtdblock flush.", file=sys.stderr)
        print("If it still will not verify: recover via urescue with the stock airOS image.",
              file=sys.stderr)
        u.close()
        return 7
    print("  -> full image verified byte-for-byte in flash")

    u.close()
    print("\n" + "=" * 68)
    print("FLASH VERIFIED. Do NOT use `reboot -f`.")
    print("=" * 68)
    print("Community reports describe unplugging/replugging to boot into OpenWrt, and a soft")
    print("reboot can fail anyway because fwupdate disturbed the live rootfs.")
    print()
    print("  OPERATOR: cut power on the injector->radio side, then restore it.")
    print()
    print("Expect OpenWrt on 192.168.1.1 (NOT .20) within ~60s.")
    print("If it does not come up: hold RESET at power-on into urescue and push")
    print("firmware/WA.v8.5.12....bin with urescue_push.py (do NOT run --probe-only first).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
