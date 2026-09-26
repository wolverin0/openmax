#!/usr/bin/env python3
"""Unpack a Ubiquiti airOS .bin firmware container into its parts.

Covers: the UBNT/PART container format used by airOS fwupdate images - header, part table,
per-part extraction. Keywords: airOS firmware, UBNT container, PART header, squashfs rootfs,
umac.ko, radio firmware, G08. Read when: you need the kernel or rootfs out of a published
airOS image. Operates on a downloaded file only - never touches a device.
Verdict: CURRENT. Analysis-only; extracted proprietary blobs must not be redistributed.

Usage: python tools/research/unpack_airos.py <image.bin> [outdir]
"""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def unpack(path: Path, outdir: Path) -> int:
    b = path.read_bytes()
    if b[:4] != b"UBNT":
        print(f"FATAL: not a UBNT container (magic {b[:4]!r})", file=sys.stderr)
        return 1

    version = b[4:260].split(b"\x00")[0].decode("ascii", "replace")
    print(f"image   : {path.name}")
    print(f"size    : {len(b)} bytes")
    print(f"sha256  : {hashlib.sha256(b).hexdigest()}")
    print(f"version : {version}\n")

    outdir.mkdir(parents=True, exist_ok=True)
    off = 264  # header: magic(4) + version(256) + crc(4)
    parts = []
    while off + 56 <= len(b):
        magic = b[off:off + 4]
        if magic == b"END.":
            print(f"END. marker at 0x{off:08x}")
            break
        if magic != b"PART":
            # tolerate small misalignment by scanning forward for the next PART/END.
            nxt = b.find(b"PART", off)
            end = b.find(b"END.", off)
            if nxt == -1 or (end != -1 and end < nxt):
                print(f"stopping: no further PART at 0x{off:08x} (magic {magic!r})")
                break
            off = nxt
            continue

        name = b[off + 4:off + 20].split(b"\x00")[0].decode("ascii", "replace")
        (memaddr, index, baseaddr, entryaddr, data_size, part_size) = struct.unpack(
            ">6I", b[off + 32:off + 56]
        )
        data_off = off + 56
        data = b[data_off:data_off + data_size]

        kind = "unknown"
        if data[:4] in (b"hsqs", b"sqsh"):
            kind = "squashfs"
        elif data[:2] == b"\x27\x05":
            kind = "uImage"
        elif data[:4] == b"\x1f\x8b\x08\x00":
            kind = "gzip"

        dest = outdir / f"{index:02d}-{name}.bin"
        dest.write_bytes(data)
        parts.append((name, data_size, kind, dest))
        print(f"  PART {name:<12} index={index} size={data_size:>9}  base=0x{baseaddr:08x}  "
              f"type={kind:<9} -> {dest.name}")
        off = data_off + data_size

    print("\nsummary:")
    for name, size, kind, dest in parts:
        print(f"  {name:<12} {size:>9} B  {kind:<9} sha256={hashlib.sha256(dest.read_bytes()).hexdigest()[:16]}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    img = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else img.with_suffix("") / "parts"
    raise SystemExit(unpack(img, out))
