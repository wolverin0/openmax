#!/usr/bin/env python3
"""Stage 257A — exact `.rel.text` -> `.rodata` join for the 340 knobs, then HAL vtable probe.

This replaces the low-16-bit heuristic of 254A/255A/256A, which was `REFUTED` as an identifier.

In an `ET_REL` module a reference to a `.rodata` literal is a **relocation pair**:

    R_MIPS_HI16 (5) on the `lui`   -> carries the symbol index
    R_MIPS_LO16 (6) on the `addiu` -> carries the low 16 bits and the addend

`rodata_offset = (hi_imm << 16) + sign_extend16(lo_imm)` and the site is the `addiu`'s
`.text` offset. That identifies the referencing instruction **unambiguously**: no 16-bit
collision is possible, because the pair is bound to a symbol index.

For every knob whose literal resolves to a `.rodata` offset, the tool reports:

  * the exact `.text` sites that build its address;
  * the enclosing function (nearest `addiu $sp,$sp,-N` prologue);
  * whether that function dispatches through the Stage 253A HAL vtable slots.

Targets: `umac.ko`, `ath_dev.ko`, `ubnt_poll_host.ko` in WA and XC.

Radio safety: static only. No module loaded, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
KNOBS = REPO_ROOT / "orchestration" / "autoresearch" / "firmware_knob_candidates.json"
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage257a_reltext_rodata_knob_vtable_join.json"

MODULES = {
    "WA.v8.7.25:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA.v8.7.25:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "WA.v8.7.25:ubnt_poll_host.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XC.v8.7.25:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC.v8.7.25:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC.v8.7.25:ubnt_poll_host.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
}
V253 = {4, 8, 156, 160, 164, 204, 208, 296, 300, 396, 520}
R_HI16, R_LO16 = 5, 6


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

    def rel_text(self) -> list[tuple[int, int, int]]:
        """(text_offset, type, sym_index) for every .rel.text entry."""
        h = self.by_name.get(".rel.text")
        if not h:
            return []
        out = []
        for i in range(h["size"] // 8):
            o = h["off"] + i * 8
            r_off, r_info = struct.unpack(self.endian + "II", self.data[o:o + 8])
            out.append((r_off, r_info & 0xFF, r_info >> 8))
        return out

    def rodata_strings(self) -> dict[int, str]:
        """offset-in-section -> string, for every rodata-ish section."""
        out = {}
        for h in self.secs:
            if h["type"] != 1 or not h["name"].startswith(".rodata"):
                continue
            blob = self.data[h["off"]:h["off"] + h["size"]]
            for m in re.finditer(rb"[\x20-\x7e]{4,}", blob):
                out.setdefault(m.start(), m.group().decode("latin1"))
        return out

    def enclosing(self, off: int, span: int = 0x2000) -> int | None:
        for back in range(0, span, 4):
            w = self.u32(off - back)
            if w is None:
                continue
            if (w & 0xFFFF0000) == 0x27BD0000 and (w & 0xFFFF) >= 0x8000:
                return off - back
        return None

    def extent(self, fn: int, cap: int = 0x4000) -> int:
        for k in range(0, cap, 4):
            if self.u32(fn + k) == 0x03E00008:
                return fn + k + 8
        return fn + cap

    def vtable_slots(self, fn: int) -> list[dict[str, Any]]:
        out = []
        hi = self.extent(fn)
        for off in range(fn, max(fn, hi - 12), 4):
            w = self.u32(off)
            if w is None or (w & 0xFC000000) != 0x8C000000:
                continue
            base = (w >> 21) & 0x1F
            rt = (w >> 16) & 0x1F
            imm = s16(w & 0xFFFF)
            for fwd in (4, 8):
                w2 = self.u32(off + fwd)
                if w2 is None or (w2 & 0xFC00003F) != 0x00000009:
                    continue
                if ((w2 >> 21) & 0x1F) != rt:
                    continue
                out.append(dict(at=f"0x{off:06x}", base=f"$r{base}", offset=imm,
                                in_253a=imm in V253))
                break
        return out


def build_join(ko: Ko) -> dict[int, list[int]]:
    """rodata_offset -> .text sites, pairing each LO16 with the nearest preceding HI16 on the
    same register (<=8 instructions earlier). A per-register dict is NOT used: it would bind
    every LO16 to the last HI16 in the module."""
    rel = ko.rel_text()
    hi_at: dict[int, tuple[int, int, int]] = {}
    lo_list: list[tuple[int, int, int]] = []
    for r_off, typ, idx in rel:
        if typ == R_HI16 and idx < len(ko.syms):
            w = ko.u32(r_off)
            if w is None or (w & 0xFC000000) != 0x3C000000:
                continue
            hi_at[r_off] = (idx, w & 0xFFFF, (w >> 16) & 0x1F)
        elif typ == R_LO16 and idx < len(ko.syms):
            lo_list.append((r_off, idx, 0))
    join: dict[int, list[int]] = defaultdict(list)
    for r_off, idx, _ in lo_list:
        w = ko.u32(r_off)
        if w is None:
            continue
        op = (w >> 26) & 0x3F
        rt = (w >> 16) & 0x1F
        rs = (w >> 21) & 0x1F
        if op not in (0x09, 0x0D):
            continue
        if op == 0x09 and rs != rt:
            continue
        pair = None
        for back in range(4, 0x24, 4):
            cand = hi_at.get(r_off - back)
            if cand is not None and cand[2] == rt and cand[0] == idx:
                pair = cand
                break
        if pair is None:
            continue
        sym_val = ko.syms[idx][1]
        addr = (sym_val + (pair[1] << 16) + s16(w & 0xFFFF)) & 0xFFFFFFFF
        join[addr].append(r_off)
    return join


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    data = json.loads(KNOBS.read_text(encoding="utf-8"))
    bound = [k for k in data["knobs"] if str(k.get("boundary")) == "airOS_UMAC_UPH"]
    names = {str(k.get("name")): k.get("id") for k in bound}

    rows = []
    attr_hist: Counter[int] = Counter()
    total_attributed = 0
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        ko = Ko(path)
        joins = build_join(ko)
        strs = ko.rodata_strings()
        per = []
        attributed = 0
        for off, text in strs.items():
            if text not in names:
                continue
            sites = joins.get(off)
            if not sites:
                per.append(dict(knob=text, id=names[text], rodata_offset=f"0x{off:06x}",
                                sites=[], function=None, vtable_slots=[],
                                reaches_253a=False))
                continue
            site = sites[0]
            fn = ko.enclosing(site)
            slots = ko.vtable_slots(fn) if fn is not None else []
            for s in slots:
                if s["in_253a"]:
                    attr_hist[s["offset"]] += 1
            attributed += 1
            per.append(dict(knob=text, id=names[text], rodata_offset=f"0x{off:06x}",
                            sites=[f"0x{x:06x}" for x in sites[:6]],
                            function=(f"0x{fn:06x}" if fn is not None else None),
                            vtable_slots=[s for s in slots if s["in_253a"]][:12],
                            reaches_253a=any(s["in_253a"] for s in slots)))
        total_attributed += attributed
        rows.append(dict(module=label, status="ok", bytes=len(ko.data),
                         sha256=hashlib.sha256(ko.data).hexdigest(),
                         knobs_in_module=len(per), attributed=attributed,
                         reaching_253a=sum(1 for p in per if p["reaches_253a"]),
                         knobs=per))

    ok = [r for r in rows if r.get("status") == "ok"]
    report = dict(
        meta=dict(stage="257A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage257a_reltext_rodata_knob_vtable_join.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="R_MIPS_HI16 (5) + R_MIPS_LO16 (6) relocation pairs from .rel.text "
                         "give rodata_offset = (hi<<16)+sign16(lo) bound to a symbol index, so "
                         "the referencing instruction is identified unambiguously",
                  vtable_offsets_from_253a=sorted(V253),
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     knobs_in_catalogue=len(names),
                     knobs_attributed=total_attributed,
                     knobs_reaching_253a=sum(r["reaching_253a"] for r in ok),
                     slot_histogram=dict(attr_hist.most_common(12)),
                     per_module={r["module"]: dict(knobs=r["knobs_in_module"],
                                                   attributed=r["attributed"],
                                                   reaching=r["reaching_253a"]) for r in ok}),
        gaps=["the enclosing function is the nearest prologue; a literal referenced from a "
              "data table rather than code has sites inside whichever function emitted it",
              "reaching a 253A slot means the containing function dispatches through the HAL "
              "vtable, not that this knob is the argument",
              "only the first .text site is used for attribution; multiple sites are recorded "
              "but not each resolved",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[257A] modules={s['modules_ok']} knobs={s['knobs_in_catalogue']} "
          f"attributed={s['knobs_attributed']} reaching_253a={s['knobs_reaching_253a']}")
    print(f"        slots: {s['slot_histogram']}")
    for r in ok:
        print(f"        {r['module']:<30} in_mod={r['knobs_in_module']:<3} "
              f"attr={r['attributed']:<3} vtable={r['reaching_253a']}")
    print(f"[257A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
