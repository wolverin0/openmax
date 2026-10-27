#!/usr/bin/env python3
"""Stage 324A — LTU `ame_core.ko` TDD frame scheduler, UL/DL duty cycle and grant allocation.

`ame_core.ko` is the LTU radio core: ARM little-endian `ET_REL`, ~3.2 MB, with ~9.8 k symbols.
The stage asks for four things:

  1. the TDD frame scheduler;
  2. the frame durations (1 / 2 / 2.5 / 4 / 5 ms);
  3. the fixed-vs-flexible UL/DL duty-cycle state machine;
  4. contention versus scheduled grant allocation.

What this tool can establish from the module alone, and what it cannot:

  * **symbol buckets** — every defined symbol matching frame/tdd/dl/ul/guard, duration/tick,
    duty/flex/fixed, grant/alloc/sched, qam/mcs. That is a real, countable surface.
  * **duration constants** — the `addiu $zero,N` and `movw`-style immediates in the
    microsecond range that the 1/2/2.5/4/5 ms ladder would produce (1000, 2000, 2500, 4000,
    5000, and the 5000-based frame period). A constant being present is **not** proof it is a
    frame duration.
  * **string evidence** — `.rodata` literals mentioning ms/usec/frame/tdd.

No state machine is decoded. A branch graph over the duty-cycle selector would need the
enclosing function and its comparison chain, and that is not attempted here.

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
LTU = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu" / "ltu_extracted"
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage324a_ltu_ame_core_scheduler_re.json"

MODULES = {
    "AF-LTU.v2.4.2:ame_core.ko":
        LTU / "afltu_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_core.ko",
    "AF-LTU-Rocket.v2.4.2:ame_core.ko":
        LTU / "aflturocket_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_core.ko",
}

PATTERNS = {
    "frame": re.compile(r"frame|tdd|superframe|guard|gp_|_gp", re.I),
    "duration": re.compile(r"duration|interval|period|tick|usec|_us\b|slot_?time", re.I),
    "duty": re.compile(r"duty|ratio|split|flex|fixed|dynamic|dl_ul|ul_dl", re.I),
    "grant": re.compile(r"grant|alloc|contention|sched|slot|queue", re.I),
    "modulation": re.compile(r"qam|mcs|modul|nss|rate_|txpower", re.I),
}

# the 1/2/2.5/4/5 ms ladder in microseconds, plus the common 5 ms frame period
FRAME_US = {1000, 2000, 2500, 4000, 5000}


def s16(v: int) -> int:
    return v - 0x10000 if v >= 0x8000 else v


class Ko:
    """ET_REL reader, endianness-aware (these modules are ARM little-endian)."""

    def __init__(self, path: Path) -> None:
        self.data = d = path.read_bytes()
        if d[:4] != b"\x7fELF":
            raise ValueError(f"not ELF: {path}")
        E = "<" if d[5] == 1 else ">"
        self.endian = E
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        secs = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, info, al, es = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            secs.append(dict(name_off=nm, type=typ, flags=fl, addr=addr, off=off,
                             size=sz, link=link, info=info))
        stro = secs[shstr]["off"]
        for h in secs:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.secs = secs
        self.by_name = {h["name"]: h for h in secs}
        tx = self.by_name.get(".text")
        self.text = d[tx["off"]:tx["off"] + tx["size"]] if tx else b""
        self.syms: list[tuple[str, int, int, int, str]] = []
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

    def constants_in(self, names: set[str], limit: int = 0x1000) -> dict[str, Any]:
        """Small immediates inside the named functions, split by plausible range."""
        us: Counter[int] = Counter()
        other: Counter[int] = Counter()
        for nm, val, sz, shndx, sn in self.syms:
            if nm not in names or sn not in (".text", ".text.unlikely", ".init.text"):
                continue
            for k in range(0, min(max(sz, 0x200), limit), 4):
                w = self.u32(val + k)
                if w is None:
                    continue
                # ARM: movw rd,#imm16 is 0xE30?0000 with imm4 in bits 19-16 and imm12 in 11-0
                if (w & 0x0FF00000) == 0x03000000:
                    v = (((w >> 16) & 0xF) << 12) | (w & 0xFFF)
                    if v in FRAME_US:
                        us[v] += 1
                    elif 0 < v <= 0x4000:
                        other[v] += 1
                    continue
                # ARM: mov rd,#imm8 (rotated) covers the small values
                if (w & 0x0FE00000) == 0x03A00000:
                    imm8 = w & 0xFF
                    rot = ((w >> 8) & 0xF) * 2
                    v = ((imm8 >> rot) | (imm8 << (32 - rot))) & 0xFFFFFFFF if rot else imm8
                    if v in FRAME_US:
                        us[v] += 1
                    elif 0 < v <= 0x4000:
                        other[v] += 1
        return dict(frame_us_candidates=dict(sorted(us.items())),
                    frame_us_total=sum(us.values()),
                    other_constants=dict(other.most_common(20)))

    def strings(self, cap: int = 100) -> list[str]:
        out = set()
        for h in self.secs:
            if h["type"] != 1 or not h["name"].startswith(".rodata"):
                continue
            blob = self.data[h["off"]:h["off"] + h["size"]]
            for m in re.finditer(rb"[\x20-\x7e]{4,}", blob):
                s = m.group().decode("latin1")
                if 4 <= len(s) <= cap:
                    out.add(s)
        return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        ko = Ko(path)
        defined = sorted({s[0] for s in ko.syms if s[3] != 0 and s[0]})
        buckets: dict[str, Any] = {}
        for name, rx in PATTERNS.items():
            hits = sorted({s for s in defined if rx.search(s)})
            buckets[name] = dict(count=len(hits), symbols=hits[:60])
        strings = ko.strings()
        frame_strings = sorted(s for s in strings
                               if re.search(r"\b(ms|usec|us)\b|frame|tdd", s, re.I))[:40]
        dur_names = set(buckets["duration"]["symbols"])
        consts = ko.constants_in(dur_names)
        rows.append(dict(module=label, status="ok", bytes=len(ko.data),
                         sha256=hashlib.sha256(ko.data).hexdigest(),
                         endian="little" if ko.endian == "<" else "big",
                         defined=len(defined), buckets=buckets,
                         frame_us=consts["frame_us_candidates"],
                         frame_us_total=consts["frame_us_total"],
                         other_constants=consts["other_constants"],
                         frame_strings=frame_strings))

    ok = [r for r in rows if r.get("status") == "ok"]
    report = dict(
        meta=dict(stage="324A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/ltu_ame_core_scheduler_and_ul_dl_ratio_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method=".symtab name classification into frame/duration/duty/grant/modulation "
                         "buckets; addiu $zero,N histogram inside duration-named functions, "
                         "split into the 1/2/2.5/4/5 ms microsecond ladder and other constants; "
                         ".rodata string sweep for ms/usec/frame/tdd",
                  modules_are_arm=True,
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     frame_symbols=max((r["buckets"]["frame"]["count"] for r in ok), default=0),
                     duration_symbols=max((r["buckets"]["duration"]["count"] for r in ok),
                                          default=0),
                     duty_symbols=max((r["buckets"]["duty"]["count"] for r in ok), default=0),
                     grant_symbols=max((r["buckets"]["grant"]["count"] for r in ok), default=0),
                     modulation_symbols=max((r["buckets"]["modulation"]["count"] for r in ok),
                                            default=0),
                     frame_us_values=max((len(r["frame_us"]) for r in ok), default=0),
                     frame_us_sites=max((r["frame_us_total"] for r in ok), default=0),
                     frame_strings=max((len(r["frame_strings"]) for r in ok), default=0)),
        gaps=["the 1/2/2.5/4/5 ms constants are counted, not attributed: a value of 1000 us "
              "inside a duration-named function is a candidate frame duration, not proof",
              "no UL/DL duty-cycle state machine was decoded: the branch graph over the "
              "flexible/fixed selector is not traced",
              "contention versus scheduled grant is a symbol bucket, not an allocation policy",
              "the modules are ARM little-endian and the sweep reads ARM movw and rotated mov immediates; movt halves "
              "of wider constants are not joined here (see Stage 173A)",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[324A] modules={s['modules_ok']} frame={s['frame_symbols']} "
          f"dur={s['duration_symbols']} duty={s['duty_symbols']} "
          f"grant={s['grant_symbols']} mod={s['modulation_symbols']}")
    print(f"        frame_us_values={s['frame_us_values']} sites={s['frame_us_sites']} "
          f"strings={s['frame_strings']}")
    for r in ok:
        print(f"        {r['module']:<32} {r['bytes']:>9}B arm={r['endian']} "
              f"us={r['frame_us']}")
    print(f"[324A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
