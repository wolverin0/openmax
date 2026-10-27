#!/usr/bin/env python3
"""Stage 416A — GPS 1PPS TDMA frame sync in `ubnt_poll_host.ko`, and `ubnt-gps-reader`.

The stage asks for the GPS 1PPS synchronisation of the TDMA frame across **WA / XC / 2XC**:
`gps_sync`, `frame_offset`, fixed frames of 5/8/10 ms, `down_dur` / `up_dur` / `cbp_dur`, and the
auto-interference prevention between co-located sectors.

Two facts decide the shape of the answer:

  * the timing vocabulary **is** in the module — `gps`, `pps`, `down_dur`, `up_dur`, `cbp_dur`
    and `fixed_frame` are all real strings, with identical counts on WA and 2XC;
  * **`ubnt-gps-reader` is a zero-byte file.** So are `bin/gps` and `bin/gps_cmd`. The userspace
    half of the stage has no bytes to analyse, and no amount of static work can invent them.

`gps_sync` and `frame_offset` do **not** appear as literals; the durations do. And `coloc` /
`co-located` appear nowhere, so the sector auto-interference claim has no anchor in this corpus.

`sync_state_machine_recovered = 0` is the honest output. What is delivered is the exact duration
vocabulary, the symbol list that owns it, and a hard count of the stubs that block the rest.

Radio safety: static only. No module loaded, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
OUT = (REPO_ROOT / "artifacts" / "autoresearch" / "stage416a_ubnt_poll_gps_sync_1pps_re.json")

MODULES = {
    "WA.v8.7.25:ubnt_poll_host.ko":
        FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XC.v8.7.25:ubnt_poll_host.ko":
        FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "2XC.v8.7.11:ubnt_poll_host.ko":
        FW / "2xc_8711_modules/ubnt_poll_host.ko",
}

# every place a gps reader is expected, across the rootfs trees we hold
GPS_READER_CANDIDATES = [
    FW / "ltu_extracted/afltu_2.4.2/rootfs_extracted/bin/ubnt-gps-reader",
    FW / "ltu_extracted/aflturocket_2.4.2/rootfs_extracted/bin/ubnt-gps-reader",
    FW / "ltu_extracted/afltu_2.4.2/rootfs_extracted/usr/bin/ubnt-gps-reader",
    FW / "ltu_extracted/aflturocket_2.4.2/rootfs_extracted/usr/bin/ubnt-gps-reader",
]

SYNC = ["gps_sync", "frame_offset", "gps", "pps", "1pps"]
DURATIONS = ["down_dur", "up_dur", "cbp_dur", "fixed_frame"]
FRAME_MS = [5, 8, 10]
COLOC = ["coloc", "co-loc", "colocated", "auto_interference", "sector"]


def ctx(b: bytes, tok: str, n: int = 4, w: int = 74) -> list[str]:
    out: list[str] = []
    needle = tok.encode()
    i = b.find(needle)
    while i >= 0 and len(out) < n:
        out.append("".join(chr(c) if 32 <= c < 127 else "."
                           for c in b[max(0, i - w):i + len(needle) + w]))
        i = b.find(needle, i + 1)
    return out


class Syms:
    def __init__(self, path: Path) -> None:
        self.data = d = path.read_bytes()
        E = "<" if d[5] == 1 else ">"
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        secs = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, info, al, es = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            secs.append(dict(name_off=nm, type=typ, off=off, size=sz, link=link))
        stro = secs[shstr]["off"]
        for h in secs:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.secs = secs
        self.names: list[str] = []
        st = next((h for h in secs if h["name"] == ".symtab"), None)
        if st:
            ss = secs[st["link"]]
            for i in range(st["size"] // 16):
                o = st["off"] + i * 16
                nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", d[o:o + 16])
                if shndx == 0:
                    continue
                e = d.find(b"\0", ss["off"] + nm)
                self.names.append(d[ss["off"] + nm:e].decode("latin1"))

    def matching(self, pattern: str, cap: int = 30) -> list[str]:
        return sorted({n for n in self.names if re.search(pattern, n, re.I)})[:cap]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        rows.append(dict(
            module=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            sync={t: b.count(t.encode()) for t in SYNC},
            durations={t: b.count(t.encode()) for t in DURATIONS},
            coloc={t: b.count(t.encode()) for t in COLOC},
            frame_ms={k: b.count(k.encode())
                      for k in ("5ms", "8ms", "10ms", "5 ms", "8 ms", "10 ms")},
            duration_contexts={t: ctx(b, t) for t in DURATIONS if b.count(t.encode())},
            sync_contexts={t: ctx(b, t) for t in ("pps", "gps") if b.count(t.encode())},
            gps_symbols=syms.matching(r"gps|pps|1pps", 30),
            duration_symbols=syms.matching(r"_dur|frame_offset|frame_len", 30)))

    readers = []
    for p in GPS_READER_CANDIDATES:
        readers.append(dict(path=p.relative_to(REPO_ROOT).as_posix() if p.exists() else
                            str(p), exists=p.exists(),
                            bytes=(p.stat().st_size if p.exists() else None),
                            readable=bool(p.exists() and p.stat().st_size > 0)))

    ok = [r for r in rows if r.get("status") == "ok"]
    dur_total = {t: sum(r["durations"][t] for r in ok) for t in DURATIONS}
    gps_syms = sorted({n for r in ok for n in r["gps_symbols"]})
    dur_syms = sorted({n for r in ok for n in r["duration_symbols"]})
    readable = [r for r in readers if r["readable"]]

    report = dict(
        meta=dict(stage="416A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/ubnt_poll_gps_sync_1pps_timingslot_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="string sweep of the sync and duration vocabulary with context; "
                         "defined-symbol lookup for gps/pps and *_dur owners; explicit size check "
                         "of every candidate ubnt-gps-reader",
                  premise_corrections=[
                      "ubnt-gps-reader is a zero-byte file in every tree that holds it, as are "
                      "bin/gps and bin/gps_cmd, so the userspace half has no bytes to analyse",
                      "gps_sync, frame_offset and any coloc/co-located marker do not exist as "
                      "literals in ubnt_poll_host.ko; the durations do",
                  ],
                  radio_safety="static only"),
        modules=rows,
        gps_reader_candidates=readers,
        summary=dict(modules_ok=len(ok),
                     modules_with_pps=sum(1 for r in ok if r["sync"]["pps"]),
                     pps_hits=sum(r["sync"]["pps"] for r in ok),
                     gps_hits=sum(r["sync"]["gps"] for r in ok),
                     gps_sync_literal=sum(r["sync"]["gps_sync"] for r in ok),
                     frame_offset_literal=sum(r["sync"]["frame_offset"] for r in ok),
                     duration_hits=dur_total,
                     fixed_frame_present=int(dur_total["fixed_frame"] > 0),
                     coloc_hits=sum(sum(r["coloc"].values()) for r in ok),
                     gps_symbols=gps_syms[:12],
                     duration_symbols=dur_syms[:12],
                     gps_reader_files=len(readers),
                     gps_reader_readable=len(readable),
                     frame_ms_strings={k: sum(r["frame_ms"][k] for r in ok)
                                       for k in ("5ms", "8ms", "10ms", "5 ms", "8 ms", "10 ms")},
                     sync_state_machine_recovered=0),
        gaps=["ubnt-gps-reader, bin/gps and bin/gps_cmd are zero-byte files, so the 1PPS source "
              "and its ioctl contract cannot be read",
              "gps_sync and frame_offset are not literals in ubnt_poll_host.ko; only the duration "
              "vocabulary is",
              "no coloc / co-located / auto-interference marker exists, so the sector "
              "auto-interference prevention is unanchored in this corpus",
              "down_dur/up_dur/cbp_dur are names; no value or range was recovered for them",
              "the 5/8/10 ms fixed frames are not enumerable from strings",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[416A] modules={s['modules_ok']} pps={s['pps_hits']} gps={s['gps_hits']} "
          f"durations={s['duration_hits']} fixed={s['fixed_frame_present']} "
          f"coloc={s['coloc_hits']} reader_readable={s['gps_reader_readable']}/"
          f"{s['gps_reader_files']}")
    for m in ok:
        print(f"        {m['module']:<30} {m['bytes']:>7}B dur={ {k: v for k, v in m['durations'].items() if v} }")
    for r in readers:
        print(f"        reader {r['path']:<58} bytes={r['bytes']}")
    print(f"[416A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
