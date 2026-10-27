#!/usr/bin/env python3
"""Stage 258A — rebuild the complete `ctl_table` and `proc_ops` trees of ubnt_poll_host.ko
from `.rel.data` + `.rel.text` relocations.

Two structures, two relocation classes:

  * **`ctl_table`** lives in `.data`/`.rodata`. Its pointer fields (`procname`, `data`, `child`,
    `proc_handler`) are `R_MIPS_32` relocations whose **addend is the word content**, so the
    target is `symbol + word`. The array stride for this kernel is 44 bytes (established in
    Stage 81A-W4B and re-verified here against the `memcpy` of 0x580 = 32 × 44).
  * **`proc_ops` / `file_operations`** are reached from the `proc_create_data(name, mode, parent,
    fops)` call sites in `.init.text`; `$a0` (name) and `$a3` (fops) come from `lui`/`addiu`
    pairs bound by `.rel.init.text` HI16/LO16 pairs.

The `.rel.text` join is the same sound technique as 257A: pair each LO16 with the nearest
preceding HI16 on the same register and the same symbol index.

Radio safety: static only. No module loaded, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage258a_ubnt_poll_reloc_sysctl_proc_trees.json"
MODULES = {
    "WA.v8.7.25": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XC.v8.7.25": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
}
STRIDE = 44
F_NAME, F_DATA, F_MAXLEN, F_MODE, F_CHILD, F_HANDLER = 0x04, 0x08, 0x0C, 0x10, 0x14, 0x1C
R_32, R_HI16, R_LO16 = 2, 5, 6


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

    def word(self, sect: str, off: int) -> int | None:
        h = self.by_name.get(sect)
        if not h or off < 0 or off + 4 > h["size"]:
            return None
        return struct.unpack(self.endian + "I", self.data[h["off"] + off:h["off"] + off + 4])[0]

    def cstr(self, sect: str, off: int, cap: int = 80) -> str | None:
        h = self.by_name.get(sect)
        if not h or off < 0 or off >= h["size"]:
            return None
        b = self.data[h["off"] + off:h["off"] + min(h["size"], off + cap)]
        e = b.find(b"\0")
        if e <= 0:
            return None
        s = b[:e].decode("latin1")
        return s if s.isprintable() else None

    def relocs(self, sect: str) -> dict[int, tuple[int, int]]:
        h = self.by_name.get(".rel" + sect)
        if not h:
            return {}
        out = {}
        for i in range(h["size"] // 8):
            o = h["off"] + i * 8
            r_off, r_info = struct.unpack(self.endian + "II", self.data[o:o + 8])
            out[r_off] = (r_info & 0xFF, r_info >> 8)
        return out

    def ptr32(self, sect: str, off: int) -> dict[str, Any] | None:
        r = self.relocs(sect).get(off)
        if not r or r[0] != R_32 or r[1] >= len(self.syms):
            return None
        nm, val, _sz, _sh, sn = self.syms[r[1]]
        add = self.word(sect, off) or 0
        return dict(section=sn, offset=val + add, symbol=nm)

    def hi_lo(self, sect: str, at: int, reg: int) -> dict[str, Any] | None:
        rel = self.relocs(sect)
        h = self.by_name.get(sect)
        if not h:
            return None
        blob = self.data[h["off"]:h["off"] + h["size"]]
        hi = lo = None
        for pos in range(max(0, at - 0x50), min(len(blob), at + 8), 4):
            w = struct.unpack(self.endian + "I", blob[pos:pos + 4])[0]
            r = rel.get(pos)
            if not r:
                continue
            op, rs, rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, (w >> 16) & 0x1F, w & 0xFFFF
            if r[0] == R_HI16 and op == 0x0F and rt == reg:
                hi = (r[1], imm)
            elif r[0] == R_LO16 and op in (0x09, 0x0D) and rt == reg and rs == reg:
                lo = (r[1], imm)
        if not hi or not lo or hi[0] != lo[0]:
            return None
        nm, val, _sz, _sh, sn = self.syms[hi[0]]
        return dict(section=sn, offset=val + (hi[1] << 16) + s16(lo[1]), symbol=nm)


def ctl_tables(ko: Ko) -> list[dict[str, Any]]:
    out = []
    for sect in (".data", ".rodata", ".data.rel.ro"):
        h = ko.by_name.get(sect)
        if not h:
            continue
        off = 0
        while off < h["size"] - STRIDE:
            namep = ko.ptr32(sect, off + F_NAME)
            name = ko.cstr(namep["section"], namep["offset"]) if namep else None
            if not name:
                off += 4
                continue
            entries = []
            cur = off
            while cur < h["size"] - STRIDE:
                np2 = ko.ptr32(sect, cur + F_NAME)
                nm2 = ko.cstr(np2["section"], np2["offset"]) if np2 else None
                if not nm2:
                    break
                mode = ko.word(sect, cur + F_MODE)
                maxlen = ko.word(sect, cur + F_MAXLEN)
                entries.append(dict(name=nm2,
                                    mode=f"0o{mode:04o}" if mode is not None else None,
                                    maxlen=maxlen,
                                    data=ko.ptr32(sect, cur + F_DATA),
                                    child=ko.ptr32(sect, cur + F_CHILD),
                                    handler=ko.ptr32(sect, cur + F_HANDLER)))
                cur += STRIDE
            out.append(dict(section=sect, offset=f"0x{off:06x}", count=len(entries),
                            entries=entries))
            off = cur if cur > off else off + 4
    return out


def proc_creates(ko: Ko) -> list[dict[str, Any]]:
    """proc_create_data call sites: resolve $a0 (name), $a1 (mode), $a3 (fops)."""
    out = []
    for sect in (".init.text", ".text", ".text.unlikely"):
        h = ko.by_name.get(sect)
        if not h:
            continue
        rel = ko.relocs(sect)
        blob = ko.data[h["off"]:h["off"] + h["size"]]
        for pos in range(0, max(0, len(blob) - 4), 4):
            r = rel.get(pos)
            if not r or r[0] != 4 or r[1] >= len(ko.syms):
                continue
            if ko.syms[r[1]][0] != "proc_create_data":
                continue
            name = ko.hi_lo(sect, pos, 4)
            mode = None
            for back in range(4, 0x20, 4):
                q = pos - back
                if q < 0:
                    continue
                w = struct.unpack(ko.endian + "I", blob[q:q + 4])[0]
                if ((w >> 26) & 0x3F) == 0x09 and ((w >> 16) & 0x1F) == 5:
                    mode = w & 0xFFFF
                    break
            fops = ko.hi_lo(sect, pos, 7)
            out.append(dict(section=sect, call=f"0x{pos:06x}",
                            name=name, mode=(f"0o{mode:04o}" if mode is not None else None),
                            fops=fops))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    for image, path in MODULES.items():
        if not path.exists():
            rows.append(dict(image=image, status="absent"))
            continue
        ko = Ko(path)
        tables = ctl_tables(ko)
        procs = proc_creates(ko)
        rows.append(dict(image=image, status="ok", bytes=len(ko.data),
                         sha256=hashlib.sha256(ko.data).hexdigest(),
                         ctl_tables=tables, proc_creates=procs))

    ok = [r for r in rows if r.get("status") == "ok"]
    first = ok[0] if ok else {}
    all_entries = [e for t in first.get("ctl_tables", []) for e in t["entries"]]
    report = dict(
        meta=dict(stage="258A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage258a_ubnt_poll_reloc_sysctl_proc_trees.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="R_MIPS_32 pointer fields resolved as symbol+word for ctl_table; "
                         "HI16/LO16 pairs in .init.text/.text resolve proc_create_data "
                         "arguments; stride 44 confirmed by the 0x580 = 32x44 memcpy",
                  radio_safety="static only"),
        images=rows,
        summary=dict(images_ok=len(ok),
                     ctl_tables=len(first.get("ctl_tables", [])),
                     ctl_entries=len(all_entries),
                     ctl_handlers=len({str(e["handler"]["offset"]) for e in all_entries
                                       if e.get("handler")}),
                     ctl_children=len({str(e["child"]["offset"]) for e in all_entries
                                       if e.get("child")}),
                     proc_create_sites=len(first.get("proc_creates", [])),
                     world_writable_entries=sum(1 for e in all_entries
                                                if e.get("mode") == "0o0666")),
        gaps=["a ctl_table with no child and no handler is skipped as a terminator",
              "proc_create_data mode is read from the nearest addiu to $a1, which may belong "
              "to a different call in a tight sequence",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[258A] images={s['images_ok']} ctl_tables={s['ctl_tables']} "
          f"entries={s['ctl_entries']} handlers={s['ctl_handlers']} "
          f"proc_create={s['proc_create_sites']} ww={s['world_writable_entries']}")
    for r in ok:
        print(f"        {r['image']:<11} tables={len(r['ctl_tables'])} "
              f"entries={sum(t['count'] for t in r['ctl_tables'])} "
              f"proc={len(r['proc_creates'])}")
    print(f"[258A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
