#!/usr/bin/env python3
"""Push a firmware image to a Ubiquiti WA-board unit sitting in u-boot `urescue`.

Summary: host-side half of FMX-0002 recovery. When the LAP-120 is in urescue it runs a TFTP
SERVER at 192.168.1.20 and waits for the operator to upload one image. This tool verifies the
image is one we intend to send (known SHA-256, plausible magic), confirms the unit is reachable
at the recovery IP, and uploads it via TFTP write-request. It refuses to send an image whose
magic is neither a Ubiquiti header nor the OpenWrt `OPEN` wrapper. Header recognition alone
does not establish board compatibility, signature validity or a qualified installation path.
Keywords: urescue, TFTP recovery, LAP-120, u-boot, return-to-stock, FMX-0002.
Read when: recovering a WA-board unit, or proving recovery before a first flash.

This tool only READS the local image and performs a TFTP upload to the recovery IP. It cannot
touch the running airOS/OpenWrt system (the unit is in the bootloader). It writes nothing on the
host except an optional log.

Usage:
    python urescue_push.py --image firmware/openwrt/...-factory.bin --expect-sha256 <hex>
    python urescue_push.py --image WA.v8.5.12....bin --expect-sha256 <hex> --device-ip 192.168.1.20

Prereqs: host NIC set to 192.168.1.254/24; unit already in urescue (see the runbook).
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import re
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
KNOWN_MAGICS = (b"OPEN", b"UBNT", b"PART")


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
    return None


def _validated_payload(image: Path, expected_sha256: str | None) -> bytes:
    """Pin the exact bytes to send before opening any upload socket."""
    if not isinstance(expected_sha256, str) or not re.fullmatch(
        r"[0-9a-fA-F]{64}", expected_sha256
    ):
        raise ValueError("A valid expected SHA256 is required for every upload")
    if image.is_symlink() or not image.is_file():
        raise ValueError("Image must be a regular, non-symlink file")
    data = image.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha256.lower():
        raise ValueError("SHA256 mismatch; no upload packet sent")
    if looks_like_firmware(data[:32]) is None:
        raise ValueError("Unsupported firmware header; raw uImage is not accepted by this TFTP tool")
    return data


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


def _receive_ack(sock: socket.socket, device_ip: str, block: int,
                 server: tuple[str, int] | None = None) -> tuple[str, int]:
    """Require one exact ACK from the intended peer; ambiguity never triggers a resend."""
    try:
        packet, source = sock.recvfrom(1024)
    except OSError as error:
        raise RuntimeError(
            f"No confirmed ACK for block {block}: device state UNKNOWN; "
            "do not retry automatically.") from error
    if (len(source) != 2 or source[0] != device_ip
            or not isinstance(source[1], int) or not 1 <= source[1] <= 65535
            or (server is not None and source != server)):
        raise RuntimeError(
            f"Unexpected TFTP peer for block {block}: device state UNKNOWN; "
            "do not retry automatically.")
    if len(packet) >= 5 and packet[:2] == b"\x00\x05" and packet.endswith(b"\x00"):
        code = struct.unpack(">H", packet[2:4])[0]
        message = packet[4:-1].decode("ascii", "replace")
        raise RuntimeError(f"TFTP ERROR at block {block}: code={code} msg={message!r}; "
                           "device recovery is not verified; do not retry automatically.")
    if len(packet) != 4 or struct.unpack(">HH", packet) != (4, block & 0xFFFF):
        raise RuntimeError(
            f"Malformed or unexpected ACK for block {block}: device state UNKNOWN; "
            "do not retry automatically.")
    return source


def tftp_put(image: Path, device_ip: str, timeout: float = 5.0,
             *, expected_sha256: str | None = None) -> None:
    """Send each WRQ/DATA once; ACKs confirm delivery, never flash or recovery."""
    device_ip = str(ipaddress.IPv4Address(device_ip))
    data = _validated_payload(image, expected_sha256)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        # The first reply selects a transfer port, but must come from the exact target IP.
        # No retries: an unacknowledged write may already have reached the receiver.
        wrq = b"\x00\x02" + image.name.encode() + b"\x00" + b"octet" + b"\x00"
        sock.sendto(wrq, (device_ip, TFTP_PORT))
        server = _receive_ack(sock, device_ip, 0)

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
            sock.sendto(pkt, server)
            _receive_ack(sock, device_ip, blk, server)
            if blk % 200 == 0 or blk == total:
                print(f"  acknowledged {blk}/{total} blocks "
                      f"({min(blk * BLOCK, len(data)):,}/{len(data):,} B)")
        print("TFTP delivery acknowledged. Flash, boot and recovery are NOT verified.")
    finally:
        sock.close()


def probe_urescue(device_ip: str, timeout: float = 3.0) -> bool:
    """Diagnose reachability without sending image data; cannot certify urescue."""
    reachable = ping_ok(device_ip)
    print(f"ping {device_ip}: {'OK' if reachable else 'no reply'}")

    is_in_urescue(device_ip, timeout)

    if not reachable:
        print("NOT REACHABLE: no ping and no TFTP. Either the unit is still powering up, or it "
              "never entered urescue. The host needs any address on the unit's recovery subnet; "
              "check the cable and that no other interface owns that subnet.")
    elif tcp_open(device_ip, 80) or tcp_open(device_ip, 22):
        print("NOT IN URESCUE: the unit booted its OS (HTTP/SSH open).")
    else:
        print("UNKNOWN: reachability and an RRQ response or silence cannot identify urescue. "
              "Confirm recovery mode independently; no image was sent.")
    return False


def is_in_urescue(device_ip: str, timeout: float = 2.0) -> bool:
    """Return False (unverified) for this non-mutating probe, including on silence.

    An RRQ cannot authenticate an upload-only bootloader: timeout may mean packet loss or
    filtering, and a reply may come from an ordinary TFTP server. Never send a WRQ merely to
    probe, because it can consume the bootloader's only upload session.
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
        return False
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
    """Watch reachability; this read-only diagnostic cannot certify recovery mode.

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
        if tcp_open(device_ip, 80) or tcp_open(device_ip, 22):
            state = "airOS-booted"      # OS is up => urescue was not entered
        elif ping_ok(device_ip):
            state = "net-up-recovery-UNKNOWN"
        else:
            state = "down"              # powered off / mid-boot / link down
        if state != last:
            stamp = time.strftime("%H:%M:%S")
            # flush: this is the operator's only live feedback when run in the background,
            # where Python would otherwise buffer stdout and show nothing until exit.
            print(f"  [{stamp}] {state}", flush=True)
            last = state
        time.sleep(2)
    print("\nwatch ended; recovery mode remains UNKNOWN. No image was sent.", flush=True)
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", type=Path, help="firmware to push (omit with --probe-only)")
    ap.add_argument("--watch", type=int, metavar="SECONDS", nargs="?", const=240,
                    help="watch reachability; recovery mode remains unverified; sends NO image")
    ap.add_argument("--device-ip", default=RECOVERY_DEVICE_IP)
    ap.add_argument("--expect-sha256", help="required for uploads: expected SHA256 of the exact image")
    ap.add_argument("--yes", action="store_true", help="skip the interactive confirm")
    ap.add_argument("--probe-only", action="store_true",
                    help="diagnose reachability without certifying urescue; sends NO image")
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

    try:
        initial_payload = _validated_payload(img, args.expect_sha256)
    except (OSError, ValueError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 3
    label = looks_like_firmware(initial_payload[:32])
    digest = hashlib.sha256(initial_payload).hexdigest()
    size = len(initial_payload)

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
    try:
        tftp_put(img, args.device_ip, expected_sha256=args.expect_sha256)
    except (RuntimeError, OSError, ValueError) as error:
        print(f"TRANSFER NOT CONFIRMED: {error}", file=sys.stderr)
        return 5
    print(f"TFTP delivery acknowledged in {time.time() - t0:.1f}s; recovery NOT verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
