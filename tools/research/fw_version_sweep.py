#!/usr/bin/env python3
"""FuturaMAX G21: download airOS releases and diff the embedded radio firmware across versions.

Covers: Ubiquiti firmware API enumeration, download, UBNT container parse, squashfs extract,
symbol-accurate carving of athwlan_AR9888v2_{ptp,ptmp_ap,ptmp_sta}_bin from umac.ko, and a
per-version size/hash matrix plus changelog capture.
Keywords: G21, airOS versions, radio firmware diff, athwlan, umac.ko, changelog, ubnt-poll.
Read when: dating when a scheduling behaviour landed, or refreshing the version matrix.
Downloads only from Ubiquiti's public API. No device is touched. Proprietary blobs are
hashed and measured, never committed. Verdict: CURRENT.

Usage: python tools/research/fw_version_sweep.py <workdir> [max_versions]
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API = "https://fw-update.ubnt.com/api/firmware?filter=eq~~platform~~airmax&limit=400"
SEVENZIP = r"C:\Program Files\7-Zip\7z.exe"
SYMS = ["athwlan_AR9888v2_ptp_bin", "athwlan_AR9888v2_ptmp_ap_bin", "athwlan_AR9888v2_ptmp_sta_bin"]
UA = {"User-Agent": "Mozilla/5.0 (FuturaMAX research)"}


def get(url: str, timeout: int = 180) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


def unpack_container(b: bytes) -> dict[str, bytes]:
    """Parse a UBNT airOS container into {part_name: data}."""
    if b[:4] != b"UBNT":
        raise ValueError(f"not a UBNT container: {b[:4]!r}")
    parts, off = {}, 264
    while off + 56 <= len(b):
        if b[off:off + 4] == b"END.":
            break
        if b[off:off + 4] != b"PART":
            nxt, end = b.find(b"PART", off), b.find(b"END.", off)
            if nxt == -1 or (end != -1 and end < nxt):
                break
            off = nxt
            continue
        name = b[off + 4:off + 20].split(b"\x00")[0].decode("ascii", "replace")
        data_size = struct.unpack(">I", b[off + 48:off + 52])[0]
        parts[name] = b[off + 56:off + 56 + data_size]
        off += 56 + data_size
    return parts


def carve_symbols(ko: bytes) -> dict[str, bytes]:
    """Extract the firmware arrays from umac.ko using its ELF symbol table."""
    end = ">"
    e_shoff = struct.unpack(end + "I", ko[32:36])[0]
    e_shentsize, e_shnum, e_shstrndx = struct.unpack(end + "HHH", ko[46:52])

    def sh(i):
        o = e_shoff + i * e_shentsize
        n, t, f, a, off, size, link, info, al, es = struct.unpack(end + "10I", ko[o:o + 40])
        return dict(typ=t, off=off, size=size, link=link)

    S = [sh(i) for i in range(e_shnum)]
    symtab = next(s for s in S if s["typ"] == 2)
    strtab = S[symtab["link"]]

    def nm(x):
        s = ko[strtab["off"] + x:]
        return s[:s.find(b"\x00")].decode("ascii", "replace")

    syms = {}
    for o in range(symtab["off"], symtab["off"] + symtab["size"], 16):
        st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack(end + "IIIBBH", ko[o:o + 16])
        if st_name:
            syms[nm(st_name)] = (st_value, st_shndx)

    out = {}
    for sym in SYMS:
        if sym not in syms or sym + "_len" not in syms:
            continue
        lv, lsec = syms[sym + "_len"]
        ls = S[lsec]
        length = struct.unpack(end + "I", ko[ls["off"] + lv:ls["off"] + lv + 4])[0]
        v, sec = syms[sym]
        s = S[sec]
        out[sym.replace("athwlan_AR9888v2_", "").replace("_bin", "")] = ko[s["off"] + v:s["off"] + v + length]
    return out


def process(entry: dict, work: Path) -> dict | None:
    ver = entry["version"]
    tag = re.sub(r"[^A-Za-z0-9.\-]", "_", ver)
    rec = {"version": ver, "channel": entry.get("channel"), "created": str(entry.get("created"))[:10],
           "image_size": entry.get("file_size")}
    img = work / "images" / f"WA-{tag}.bin"
    img.parent.mkdir(parents=True, exist_ok=True)

    if not img.exists():
        url = entry.get("_links", {}).get("data", {}).get("href")
        if not url:
            return None
        try:
            img.write_bytes(get(url))
        except Exception as e:
            rec["error"] = f"download: {e}"
            return rec

    # changelog is small and directly answers "what changed"
    cl_url = entry.get("_links", {}).get("changelog", {}).get("href")
    if cl_url:
        cl = work / "changelogs" / f"WA-{tag}.txt"
        cl.parent.mkdir(parents=True, exist_ok=True)
        if not cl.exists():
            try:
                cl.write_bytes(get(cl_url, timeout=60))
            except Exception:
                pass

    try:
        parts = unpack_container(img.read_bytes())
    except Exception as e:
        rec["error"] = f"container: {e}"
        return rec
    if "rootfs" not in parts:
        rec["error"] = "no rootfs part"
        return rec

    rfs = work / "tmp" / f"{tag}-rootfs.bin"
    rfs.parent.mkdir(parents=True, exist_ok=True)
    rfs.write_bytes(parts["rootfs"])
    outdir = work / "tmp" / f"{tag}-x"
    if not (outdir / "lib/modules").exists():
        subprocess.run([SEVENZIP, "x", "-y", f"-o{outdir}", str(rfs)],
                       capture_output=True, text=True)

    kos = list(outdir.rglob("umac.ko"))
    if not kos:
        rec["error"] = "umac.ko not found (older builds may not have it)"
        return rec
    ko = kos[0].read_bytes()
    rec["umac_size"] = len(ko)
    try:
        blobs = carve_symbols(ko)
    except Exception as e:
        rec["error"] = f"carve: {e}"
        return rec

    for k, v in blobs.items():
        rec[f"{k}_size"] = len(v)
        rec[f"{k}_sha256"] = hashlib.sha256(v).hexdigest()
    # is Ubiquiti polling code present in the target firmware for this version?
    joined = b"".join(blobs.values())
    for marker in (b"UBNT_POLL_MEM_ALLOC", b"ubnt-poll", b"ubnt_set_power_range", b"_on_swbmiss"):
        rec[f"has_{marker.decode().strip('_')}"] = marker in joined
    return rec


def main() -> int:
    work = Path(sys.argv[1] if len(sys.argv) > 1 else "fw_sweep")
    work.mkdir(parents=True, exist_ok=True)
    cache = work / "airmax_api.json"
    if not cache.exists():
        cache.write_bytes(get(API))
    fw = json.loads(cache.read_text(encoding="utf-8"))["_embedded"]["firmware"]
    wa = [f for f in fw if f.get("product") == "WA" and f.get("channel") == "release"]
    wa.sort(key=lambda f: (f.get("version_major", 0), f.get("version_minor", 0), f.get("version_patch", 0)))
    if len(sys.argv) > 2:
        wa = wa[:int(sys.argv[2])]

    print(f"processing {len(wa)} WA release builds\n")
    results = []
    for e in wa:
        r = process(e, work)
        if not r:
            continue
        results.append(r)
        if "error" in r:
            print(f"  {r['version']:<12} {r['created']}  ERROR: {r['error']}")
        else:
            print(f"  {r['version']:<12} {r['created']}  umac={r.get('umac_size',0):>8}  "
                  f"ptp={r.get('ptp_size','-'):>7} ap={r.get('ptmp_ap_size','-'):>7} "
                  f"sta={r.get('ptmp_sta_size','-'):>7}  ubnt-poll={r.get('has_ubnt-poll')}")
    (work / "matrix.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"\nwrote {work/'matrix.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
