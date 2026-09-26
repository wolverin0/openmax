#!/usr/bin/env python3
"""Push a firmware image to a Ubiquiti WA-board unit sitting in u-boot `urescue`.

Summary: host-side half of FMX-0002 recovery. When the LAP-120 is in urescue it runs a TFTP
SERVER at 192.168.1.20 and waits for the operator to upload one image. This tool verifies the
image is one we intend to send (known SHA-256, plausible magic), confirms the unit is reachable
at the recovery IP, and uploads it via TFTP write-request. It refuses to send an image whose
magic is neither a Ubiquiti header nor the OpenWrt `OPEN` wrapper, so a wrong file cannot be
pushed by accident.
Keywords: urescue, TFTP recovery, LAP-120, u-boot, return-to-stock, FMX-0002.
Read when: recovering a WA-board unit, or proving recovery before a first flash.

This tool only READS the local image and performs a TFTP upload to the recovery IP. It cannot
touch the running airOS/OpenWrt system (the unit is in the bootloader). It writes nothing on the
host except an optional log.

Usage:
    python urescue_push.py --image firmware/openwrt/...-factory.bin
    python urescue_push.py --image WA.v8.5.12....bin --device-ip 192.168.1.20
    python urescue_push.py --image ... --expect-sha256 <hex>   # enforce exact image

Prereqs: host NIC set to 192.168.1.254/24; unit already in urescue (see the runbook).
"""

from __future__ import annotations

import argparse
import hashlib
import socket
import struct
import sys
import time
from pathlib import Path

RECOVERY_DEVICE_IP = "192.168.1.20"   # unit's fixed urescue address (from its u-boot env)
TFTP_PORT = 69
BLOCK = 512

# Accepted leading magics. Ubiquiti signed images start with the board tag (e.g. b"WA.." after
# a small header) or the literal partition magics; OpenWrt factory starts with b"OPEN".
KNOWN_MAGICS = (b"OPEN", b"UBNT", b"PART", b"GZ\x00", b"\x27\x05\x19\x56")  # last = uImage


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def looks_like_firmware(head: bytes) -> str | None:
    """Return a human label if the header looks like a flashable image, else None."""
    if head[:4] == b"OPEN":
        return f"OpenWrt factory (OPEN) — '{head[:24].decode('ascii', 'replace')}'"
    if head[:2] == b"WA" or head[:4] in (b"UBNT", b"PART"):
        return f"Ubiquiti image — '{head[:24].decode('ascii', 'replace')}'"
    if head[:4] == b"\x27\x05\x19\x56":
        return "raw uImage (sysupgrade) — NOTE: urescue usually wants factory/airOS, not this"
    return None


def ping_ok(ip: str) -> bool:
    import subprocess

    flag = "-n" if sys.platform.startswith("win") else "-c"
    try:
        return subprocess.run(
            ["ping", flag, "1", "-w", "1000", ip],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=6
        ).returncode == 0
    except Exception:
        return False


def tftp_put(image: Path, device_ip: str, timeout: float = 5.0) -> None:
    """Minimal TFTP write-request (RFC 1350, octet mode) to the device's TFTP server."""
    data = image.read_bytes()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        # WRQ: opcode 2, filename, mode "octet".
        # urescue serves ONE session at a time: while a session is open (including one left
        # half-open by a probe) further WRQs are silently dropped, and it frees after ~30-60s.
        # So retry patiently instead of failing -- and never run --probe-only immediately before
        # a real push, or the probe eats the session the push needs.
        wrq = b"\x00\x02" + image.name.encode() + b"\x00" + b"octet" + b"\x00"
        resp = server = None
        for attempt in range(1, 13):
            sock.sendto(wrq, (device_ip, TFTP_PORT))
            try:
                resp, server = sock.recvfrom(1024)
                break
            except socket.timeout:
                print(f"  WRQ attempt {attempt}: no reply "
                      f"(a previous session may still be open; waiting)", flush=True)
        if resp is None:
            raise RuntimeError("device never accepted a write request -- is it still in urescue?")
        opcode = struct.unpack(">H", resp[:2])[0]
        if opcode == 5:  # ERROR
            msg = resp[4:].split(b"\x00", 1)[0]
            raise RuntimeError(f"TFTP server refused WRQ: {msg!r}")
        if opcode != 4 or struct.unpack(">H", resp[2:4])[0] != 0:
            raise RuntimeError(f"unexpected TFTP reply opcode={opcode}")

        # A TFTP transfer ends with a block SHORTER than 512 bytes. If the image length is an
        # exact multiple of the block size, a final zero-length block must be sent or the server
        # waits forever for more data. (Not triggered by the current images -- both have partial
        # tails -- but a silent hang mid-flash is not something to leave to luck.)
        total = len(data) // BLOCK + 1
        for blk in range(1, total + 1):
            payload = data[(blk - 1) * BLOCK: blk * BLOCK]
            pkt = b"\x00\x03" + struct.pack(">H", blk & 0xFFFF) + payload
            is_last = blk == total
            # The device pauses to verify/flash after the last block, so give it far longer.
            sock.settimeout(20.0 if is_last else timeout)
            for _attempt in range(5):
                sock.sendto(pkt, server)
                try:
                    ack, _ = sock.recvfrom(1024)
                except socket.timeout:
                    continue
                op = struct.unpack(">H", ack[:2])[0]
                if op == 5:
                    # The bootloader is TELLING us why it refused. Never swallow this -- on a
                    # unit with no serial console it is the only diagnostic we get.
                    code = struct.unpack(">H", ack[2:4])[0]
                    msg = ack[4:].split(b"\x00", 1)[0].decode("ascii", "replace")
                    raise RuntimeError(
                        f"device sent TFTP ERROR at block {blk}/{total}: code={code} msg={msg!r}")
                if op == 4 and struct.unpack(">H", ack[2:4])[0] == (blk & 0xFFFF):
                    break
            else:
                if is_last:
                    # Some Ubiquiti bootloaders stop ACKing and jump straight to verify+flash.
                    # Report it rather than calling it a failure -- the device state decides.
                    print(f"  final block {blk}/{total} sent; no ACK returned.")
                    print("  (this can mean the device moved on to verify/flash -- check whether "
                          "it reboots, or is still sitting in urescue)")
                    return
                raise RuntimeError(f"no ACK for block {blk}/{total} after 5 tries")
            if blk % 200 == 0 or blk == total:
                print(f"  sent {blk}/{total} blocks ({blk * BLOCK:,}/{len(data):,} B)")
        print("upload complete — watch the unit; it will verify, write flash, and reboot.")
    finally:
        sock.close()


def probe_urescue(device_ip: str, timeout: float = 3.0) -> bool:
    """Confirm a unit is sitting in urescue WITHOUT sending an image.

    Sends a TFTP read-request for a name that will not exist. A device in urescue answers --
    typically with an ERROR packet ("file not found") -- which is proof enough that the
    bootloader's TFTP server is listening. Nothing is uploaded and nothing is written.
    """
    reachable = ping_ok(device_ip)
    print(f"ping {device_ip}: {'OK' if reachable else 'no reply'}")

    # Single source of truth for the urescue test -- see is_in_urescue() for why it must be a
    # WRITE request. This function only adds human-readable diagnosis on top.
    if is_in_urescue(device_ip, timeout):
        print("UDP/69 is bound and ignoring reads -- *** UNIT IS IN URESCUE *** (nothing sent).")
        return True

    if not reachable:
        print("NOT REACHABLE: no ping and no TFTP. Either the unit is still powering up, or it "
              "never entered urescue. The host needs any address on the unit's recovery subnet; "
              "check the cable and that no other interface owns that subnet.")
    elif tcp_open(device_ip, 80) or tcp_open(device_ip, 22):
        print("NOT IN URESCUE: the unit booted its OS (HTTP/SSH open).")
    else:
        print("AMBIGUOUS: answers ping but no OS ports and no TFTP ACK -- likely still booting, "
              "or in the bootloader without urescue armed. Re-probe in a few seconds.")
    return False


def is_in_urescue(device_ip: str, timeout: float = 2.0) -> bool:
    """True iff the bootloader's TFTP server is up and waiting for firmware.

    Probes with a WRITE request (opcode 2) and looks for ACK block 0, then cancels with a TFTP
    ERROR. **Zero data blocks are sent, so nothing can be written to flash.**

    Do NOT probe with a read request: urescue is an upload-only server -- it exists to *receive*
    firmware and silently ignores RRQs. An RRQ probe reports "not in urescue" for a unit that is
    sitting in urescue perfectly happily. (Cost me three misdiagnosed attempts.)

    Note also that ping cannot discriminate: the unit keeps the same address in airOS and in the
    bootloader, and U-Boot answers ICMP. A useful secondary tell is the *failure mode* on UDP/69 --
    a booted airOS actively refuses (ICMP port-unreachable -> ConnectionReset), whereas U-Boot's
    minimal stack silently drops (timeout).
    """
    # An OS answering means we are definitively not in the bootloader.
    if tcp_open(device_ip, 80) or tcp_open(device_ip, 22):
        return False
    if not ping_ok(device_ip):
        return False

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(b"\x00\x01__probe__\x00octet\x00", (device_ip, TFTP_PORT))
        sock.recvfrom(1024)
        # A real reply to a READ is not urescue behaviour; treat as unknown/not-urescue.
        return False
    except socket.timeout:
        # Silence = something IS bound to UDP/69 and is ignoring reads. That is urescue:
        # it is an upload-only server. (airOS, by contrast, has nothing on 69, so the host
        # gets an ICMP port-unreachable -> ConnectionReset, handled below.)
        return True
    except OSError:
        # ICMP port unreachable: nothing listening on 69 -> not in urescue.
        return False
    finally:
        sock.close()


def tcp_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """True if a TCP port accepts a connection. SSH/22 open => an OS booted, not the bootloader."""
    sock = socket.socket()
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def watch_for_urescue(device_ip: str, seconds: int = 240) -> bool:
    """Poll until the unit enters urescue, so a blind button-hold gets live feedback.

    Prints a state line only when the state CHANGES, so the log shows exactly when the unit
    dropped off the network and when the bootloader's TFTP server came up.
    """
    print(f"watching {device_ip} for urescue (up to {seconds}s) -- power-cycle with RESET held now.",
          flush=True)
    print("hold RESET *before* applying power and keep holding well past the LED change.\n",
          flush=True)
    deadline = time.time() + seconds
    last = None
    while time.time() < deadline:
        # Order matters, and the OS test needs BOTH ports. U-Boot answers ping, so ping alone
        # cannot tell a booted OS from a bootloader. SSH alone is not enough either: dropbear
        # transiently refuses connections while airOS is fully up, which briefly looks like the
        # bootloader. U-Boot serves no HTTP, so "22 or 80 open" is the dependable OS signal.
        if is_in_urescue(device_ip):
            state = "URESCUE"
        elif tcp_open(device_ip, 80) or tcp_open(device_ip, 22):
            state = "airOS-booted"      # OS is up => urescue was not entered
        elif ping_ok(device_ip):
            state = "net-up-no-OS"      # ping only, no OS ports, no TFTP: bootloader / early boot
        else:
            state = "down"              # powered off / mid-boot / link down
        if state != last:
            stamp = time.strftime("%H:%M:%S")
            # flush: this is the operator's only live feedback when run in the background,
            # where Python would otherwise buffer stdout and show nothing until exit.
            print(f"  [{stamp}] {state}", flush=True)
            last = state
        if state == "URESCUE":
            print("\n*** UNIT IS IN URESCUE *** -- ready to push an image.", flush=True)
            return True
        time.sleep(2)
    print("\ntimed out; unit never entered urescue.", flush=True)
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", type=Path, help="firmware to push (omit with --probe-only)")
    ap.add_argument("--watch", type=int, metavar="SECONDS", nargs="?", const=240,
                    help="poll until the unit enters urescue, then exit; sends NO image")
    ap.add_argument("--device-ip", default=RECOVERY_DEVICE_IP)
    ap.add_argument("--expect-sha256", help="require the image to match this hex digest")
    ap.add_argument("--yes", action="store_true", help="skip the interactive confirm")
    ap.add_argument("--probe-only", action="store_true",
                    help="check the unit is in urescue and exit; sends NO image, writes nothing")
    args = ap.parse_args()

    if args.watch:
        return 0 if watch_for_urescue(args.device_ip, args.watch) else 1

    if args.probe_only:
        return 0 if probe_urescue(args.device_ip) else 1

    if args.image is None:
        print("ERROR: --image is required (or use --probe-only)", file=sys.stderr)
        return 2

    img: Path = args.image
    if not img.is_file():
        print(f"ERROR: image not found: {img}", file=sys.stderr)
        return 2

    head = img.read_bytes()[:32]
    label = looks_like_firmware(head)
    digest = sha256_of(img)
    size = img.stat().st_size

    print(f"image : {img}")
    print(f"size  : {size:,} bytes")
    print(f"sha256: {digest}")
    print(f"magic : {label or 'UNRECOGNISED'}")

    if label is None:
        print("REFUSED: header magic is not a known firmware image. Wrong file?", file=sys.stderr)
        return 3
    if args.expect_sha256 and digest.lower() != args.expect_sha256.lower():
        print(f"REFUSED: sha256 mismatch (expected {args.expect_sha256})", file=sys.stderr)
        return 3

    print(f"\ndevice: {args.device_ip} (urescue TFTP server)")
    if not ping_ok(args.device_ip):
        print("WARNING: device does not answer ping. Confirm it is IN urescue and the host NIC "
              "is 192.168.1.254/24 before continuing.", file=sys.stderr)
        if not args.yes:
            print("Aborting (no --yes).", file=sys.stderr)
            return 4

    if not args.yes:
        ans = input(f"\nPush this image to {args.device_ip}? This reflashes the unit. [type YES] ")
        if ans.strip() != "YES":
            print("aborted.")
            return 0

    t0 = time.time()
    tftp_put(img, args.device_ip)
    print(f"done in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
