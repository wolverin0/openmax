#!/usr/bin/env python3
"""Stage 259A — `ath_rate_atheros.ko` in XW.v6.3.6 (M5): rate tables, PER thresholds, retries.

The module is at `lib/modules/2.6.32.71/ath_rate_atheros.ko` (139,128 B), MIPS32 big-endian
`ET_REL`.

Three surfaces, each recovered from relocations and symbols rather than guessed:

  1. **rate tables (HT20 / HT40)** — `.rel.data` entries pointing at arrays of rate descriptors.
     The tool reports the arrays whose relocation cluster size is consistent with a per-MCS
     table, plus every symbol name mentioning rate/ht/mcs.
  2. **PER up/down thresholds** — small integer constants materialised near symbols whose names
     mention per/up/down/thresh/ewma. Reported as a constant histogram with the enclosing
     symbol, not as a claimed threshold table.
  3. **retry handling** — symbols and constants matching retry/retries/rc_/try.

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
XW = REPO_ROOT / "artifacts" / "firmware_re_xw_m5"
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage259a_xw_ath_rate_atheros_re.json"
MODULE = XW / "xw_636_rootfs/lib/modules/2.6.32.71/ath_rate_atheros.ko"

RATE_RX = re.compile(r"rate|ht20|ht40|mcs|vht|legacy|rix|txrate", re.I)
PER_RX = re.compile(r"per\b|per_|_per|ewma|thresh|up_?th|down_?th|hyster", re.I)
RETRY_RX = re.compile(r"retry|retries|rc_|try|fail", re.I)


def s16(v: int) -> int:
    return v - 0x10000 if v >= 0x8000 else v


class Ko:
    def __init__(self, path: Path) -> None:
        self.data = d = path.read_bytes()
        E = "<" if d[5] == 1 else ">"
        self.endian = E
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        secs = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, info, al, es = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            secs.append(dict(name_off=nm, type=typ, flags=fl, addr=addr, off=off, size=sz,
                             link=link, info=info))
        stro = secs[shstr]["off"]
        for h in secs:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.secs = secs
        self.by_name = {h["name"]: h for h in secs}
        tx = self.by_name.get(".text")
        self.text = d[tx["off"]:tx["off"] + tx["size"]] if tx else b""
        self.syms = []
        st = self.by_name.get(".symtab")
        if st:
            ss = secs[st["link"]]
            for i in range(st["size"] // 16):
                o = st["off"] + i * 16
                nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", d[o:o + 16])
                e = d.find(b"\0", ss["off"] + nm)
                sn = secs[shndx]["name"] if 0 < shndx < len(secs) else ""
                self.syms.append((d[ss["off"] + nm:e].decode("latin1"), val, sz, shndx, sn))

    def u32(self, off: int) -> int | None:
        if off < 0 or off + 4 > len(self.text):
            return None
        return struct.unpack(self.endian + "I", self.text[off:off + 4])[0]

    def relocs(self, sect: str) -> list[tuple[int, int, int]]:
        h = self.by_name.get(".rel" + sect)
        if not h:
            return []
        out = []
        for i in range(h["size"] // 8):
            o = h["off"] + i * 8
            r_off, r_info = struct.unpack(self.endian + "II", self.data[o:o + 8])
            out.append((r_off, r_info & 0xFF, r_info >> 8))
        return out

    def enclosing(self, off: int, span: int = 0x2000) -> int | None:
        for back in range(0, span, 4):
            w = self.u32(off - back)
            if w is None:
                continue
            if (w & 0xFFFF0000) == 0x27BD0000 and (w & 0xFFFF) >= 0x8000:
                return off - back
        return None

    def sym_at(self, off: int) -> str | None:
        for nm, val, sz, shndx, sn in self.syms:
            if sn in (".text", ".text.unlikely") and val <= off < val + max(sz, 4):
                return nm
        return None


def data_arrays(ko: Ko) -> list[dict[str, Any]]:
    """Cluster .rel.data R_MIPS_32 entries into candidate rate tables."""
    rel = ko.relocs(".data") + ko.relocs(".rodata")
    offs = sorted({r for r, t, _i in rel if t == 2})
    clusters = []
    cur: list[int] = []
    for o in offs:
        if cur and o - cur[-1] > 8:
            clusters.append(cur)
            cur = []
        cur.append(o)
    if cur:
        clusters.append(cur)
    out = []
    for c in clusters:
        if len(c) < 4:
            continue
        out.append(dict(first=f"0x{c[0]:06x}", last=f"0x{c[-1]:06x}", entries=len(c),
                        span=(c[-1] - c[0]) // 4 + 1))
    out.sort(key=lambda x: -x["entries"])
    return out[:40]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    if not MODULE.exists():
        report = dict(meta=dict(stage="259A", generated_utc="2026-10-26T00:00:00Z",
                                tool="tools/re/dissect_stage259a_xw_ath_rate_atheros_re.py",
                                scope="offline static",
                                premise_correction="ath_rate_atheros.ko not found"),
                      summary=dict(module_present=False), gaps=["module absent"],
                      module=dict(status="absent"))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("[259A] module absent")
        return 0

    ko = Ko(MODULE)
    defined = sorted({s[0] for s in ko.syms if s[3] != 0 and s[0]})

    rate_syms = sorted({s for s in defined if RATE_RX.search(s)})
    per_syms = sorted({s for s in defined if PER_RX.search(s)})
    retry_syms = sorted({s for s in defined if RETRY_RX.search(s)})

    # constants inside PER-related functions
    per_consts: Counter[int] = Counter()
    for nm, val, sz, shndx, sn in ko.syms:
        if nm not in per_syms or sn not in (".text", ".text.unlikely"):
            continue
        for k in range(0, min(max(sz, 0x200), 0x800), 4):
            w = ko.u32(val + k)
            if w is None:
                continue
            op, rs, rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, (w >> 16) & 0x1F, w & 0xFFFF
            if op == 0x09 and rs == 0 and 0 < s16(imm) <= 100:
                per_consts[s16(imm)] += 1

    retry_consts: Counter[int] = Counter()
    for nm, val, sz, shndx, sn in ko.syms:
        if nm not in retry_syms or sn not in (".text", ".text.unlikely"):
            continue
        for k in range(0, min(max(sz, 0x200), 0x800), 4):
            w = ko.u32(val + k)
            if w is None:
                continue
            op, rs, rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, (w >> 16) & 0x1F, w & 0xFFFF
            if op == 0x09 and rs == 0 and 0 < s16(imm) <= 32:
                retry_consts[s16(imm)] += 1

    arrays = data_arrays(ko)
    report = dict(
        meta=dict(stage="259A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage259a_xw_ath_rate_atheros_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  module=str(MODULE.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method=".rel.data R_MIPS_32 clustering for candidate rate tables; .symtab "
                         "name classification for rate/PER/retry; addiu $zero,N histogram "
                         "inside PER and retry functions",
                  radio_safety="static only"),
        module=dict(status="ok", bytes=len(ko.data),
                    sha256=hashlib.sha256(ko.data).hexdigest(),
                    symbols_total=len(ko.syms), defined=len(defined)),
        rate=dict(symbols=rate_syms[:80], count=len(rate_syms)),
        per=dict(symbols=per_syms[:80], count=len(per_syms),
                 constant_histogram=dict(per_consts.most_common(20))),
        retry=dict(symbols=retry_syms[:80], count=len(retry_syms),
                   constant_histogram=dict(retry_consts.most_common(12))),
        data_arrays=arrays,
        summary=dict(module_present=True, symbols=len(defined),
                     rate_symbols=len(rate_syms), per_symbols=len(per_syms),
                     retry_symbols=len(retry_syms),
                     per_constants=len(per_consts), retry_constants=len(retry_consts),
                     data_arrays=len(arrays),
                     largest_array_entries=arrays[0]["entries"] if arrays else 0),
        gaps=["the rate tables are reported as relocation clusters, not as decoded descriptors: "
              "the MCS/rate field layout was not reconstructed",
              "PER thresholds are a constant histogram inside PER-named functions, not a "
              "verified up/down pair",
              "retry constants are likewise a histogram, not a retry ladder",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[259A] module={s['module_present']} syms={s['symbols']} rate={s['rate_symbols']} "
          f"per={s['per_symbols']} retry={s['retry_symbols']} arrays={s['data_arrays']} "
          f"largest={s['largest_array_entries']}")
    print(f"        per consts: {report['per']['constant_histogram']}")
    print(f"        retry consts: {report['retry']['constant_histogram']}")
    print(f"[259A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
