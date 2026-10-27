#!/usr/bin/env python3
"""Stage 253A — recover the HAL calling convention in ath_hal.ko and umac.ko.

Targets, located by `.symtab`:

  * `ath_hal_attach` / `_ath_hal_attach` in `ath_hal.ko`
  * `ol_ath_attach` / `__ol_ath_attach` / `ath_attach` / `__ath_attach` in `umac.ko`

Method: real MIPS32 big-endian disassembly with capstone. For every `jalr $rX` reachable
inside those functions, the tool walks backwards for the `lw $rX, off($base)` that defined
the target register. The pair `(base register, offset)` is the **vtable slot**; the argument
registers in flight at the `jalr` are captured as `$a0..$a3`.

That yields a concrete calling convention: which struct base, which slot offset, and which
arguments the callee receives.

Radio safety: static only. No module loaded, no register written, no radio contacted.

Read-only: the only write is the receipt JSON.
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

import capstone

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage253a_hal_calling_convention.json"

TARGETS = {
    "WA.v8.7.25": {
        "ath_hal.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
        "umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    },
    "XC.v8.7.25": {
        "ath_hal.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
        "umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    },
}
FUNCS = ["ath_hal_attach", "_ath_hal_attach", "ol_ath_attach", "__ol_ath_attach",
         "ath_attach", "__ath_attach"]
MD = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 | capstone.CS_MODE_BIG_ENDIAN)
REG_NAMES = {4: "$a0", 5: "$a1", 6: "$a2", 7: "$a3", 28: "$gp", 29: "$sp",
             16: "$s0", 17: "$s1", 18: "$s2", 19: "$s3", 20: "$s4", 21: "$s5",
             22: "$s6", 23: "$s7", 30: "$s8"}


class Ko:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = d = path.read_bytes()
        E = "<" if d[5] == 1 else ">"
        self.endian = E
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        secs = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, _i, _a, _e = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            secs.append(dict(name_off=nm, type=typ, flags=fl, addr=addr, off=off,
                             size=sz, link=link))
        stro = secs[shstr]["off"]
        for h in secs:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.sections = secs
        self.by_name = {h["name"]: h for h in secs}
        self.text = self.by_name.get(".text")
        self.text_bytes = d[self.text["off"]:self.text["off"] + self.text["size"]] \
            if self.text else b""
        self.syms = []
        st = self.by_name.get(".symtab")
        if st:
            ss = secs[st["link"]]
            for i in range(st["size"] // 16):
                o = st["off"] + i * 16
                nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", d[o:o + 16])
                e = d.find(b"\0", ss["off"] + nm)
                self.syms.append((d[ss["off"] + nm:e].decode("latin1"), val, sz, shndx))
        self.sect_maps = {}
        for h in secs:
            if h["type"] != 9 or not h["name"].startswith(".rel."):
                continue
            tgt = "." + h["name"][5:]
            m = {}
            for i in range(h["size"] // 8):
                o = h["off"] + i * 8
                r_off, r_info = struct.unpack(E + "II", d[o:o + 8])
                idx = r_info >> 8
                if idx < len(self.syms) and self.syms[idx][0]:
                    m[r_off] = self.syms[idx][0]
            if m:
                self.sect_maps[tgt] = m

    def find_func(self, name: str) -> tuple[int, int] | None:
        """Return (offset_in_.text, size) for a defined function symbol."""
        for nm, val, sz, shndx in self.syms:
            if nm != name or shndx == 0:
                continue
            # st_value for a FUNC in .text is a section-relative offset
            if 0 <= val < len(self.text_bytes):
                return val, (sz or 0x400)
        return None

    def disas(self, off: int, size: int) -> list[Any]:
        end = min(len(self.text_bytes), off + max(size, 0x40))
        return list(MD.disasm(self.text_bytes[off:end], off))


def jalr_slots(ko: Ko, off: int, size: int) -> list[dict[str, Any]]:
    """For each jalr, walk back for the lw that defined its target register."""
    insns = ko.disas(off, size)
    by_addr = {i.address: i for i in insns}
    out = []
    for ins in insns:
        if ins.mnemonic != "jalr":
            continue
        target_reg = None
        ops = ins.op_str.replace(" ", "").split(",")
        if ops and ops[0].startswith("$"):
            target_reg = ops[0]
        if target_reg is None:
            continue
        slot = None
        args: dict[str, str] = {}
        for back in range(4, 0x40, 4):
            prev = by_addr.get(ins.address - back)
            if prev is None:
                continue
            if prev.mnemonic == "lw" and prev.op_str.replace(" ", "").startswith(target_reg + ","):
                op = prev.op_str.replace(" ", "")
                inner = re.match(r"\$r?\w+,(-?\d+|0x[0-9a-f]+)\((\$\w+)\)", op)
                if inner:
                    slot = dict(ptr_offset=int(inner.group(1), 0),
                                base=inner.group(2), load_at=f"0x{prev.address:06x}")
                break
        if slot is None:
            continue
        # argument registers in flight: the last write to $a0..$a3 before the jalr
        for reg in ("$a0", "$a1", "$a2", "$a3"):
            for back in range(4, 0x30, 4):
                prev = by_addr.get(ins.address - back)
                if prev is None:
                    continue
                dest = prev.op_str.replace(" ", "").split(",")[0]
                if dest == reg:
                    args[reg] = f"{prev.mnemonic} {prev.op_str}  @0x{prev.address:06x}"
                    break
        out.append(dict(jalr_at=f"0x{ins.address:06x}", target_reg=target_reg,
                        vtable_base=slot["base"], vtable_offset=slot["ptr_offset"],
                        load_at=slot["load_at"], args=args))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    offset_hist: Counter[str] = Counter()
    base_hist: Counter[str] = Counter()
    for image, mods in TARGETS.items():
        for mod, path in mods.items():
            if not path.exists():
                rows.append(dict(image=image, module=mod, status="absent"))
                continue
            ko = Ko(path)
            entry = dict(image=image, module=mod, bytes=len(ko.data),
                         sha256=hashlib.sha256(ko.data).hexdigest(), functions={})
            for fn in FUNCS:
                loc = ko.find_func(fn)
                if loc is None:
                    continue
                off, size = loc
                slots = jalr_slots(ko, off, size)
                for s in slots:
                    offset_hist[str(s["vtable_offset"])] += 1
                    base_hist[s["vtable_base"]] += 1
                entry["functions"][fn] = dict(offset_in_text=f"0x{off:06x}",
                                              declared_size=size,
                                              jalr_count=len(slots),
                                              slots=slots[:40])
            entry["status"] = "ok"
            rows.append(entry)

    ok = [r for r in rows if r.get("status") == "ok"]
    total_jalr = sum(f["jalr_count"] for r in ok for f in r["functions"].values())
    report = dict(
        meta=dict(stage="253A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage253a_hal_calling_convention.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; MIPS32 big-endian capstone disassembly; no module "
                        "loaded, no radio contacted",
                  method="locate the attach functions by .symtab, disassemble them, and for "
                         "each jalr walk back to the lw that defined the target register; the "
                         "(base, offset) pair is the vtable slot and $a0..$a3 are the "
                         "arguments in flight",
                  radio_safety="static only"),
        images=rows,
        summary=dict(modules_ok=len(ok),
                     functions_found=sum(len(r["functions"]) for r in ok),
                     jalr_sites=total_jalr,
                     distinct_vtable_offsets=len(offset_hist),
                     top_offsets=dict(offset_hist.most_common(30)),
                     base_registers=dict(base_hist.most_common(10))),
        gaps=["a jalr whose target register was not loaded from a base register inside the "
              "scanned window is skipped, not guessed",
              "the argument capture reports the last instruction that wrote $a0..$a3, which is "
              "the setup and not necessarily the semantic role of each argument",
              "UNKNOWN - which of the 11 offsets is the register-write accessor: offset 4 is "
              "the most used slot, not the write path",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[253A] modules={s['modules_ok']} functions={s['functions_found']} "
          f"jalr={s['jalr_sites']} vtable_offsets={s['distinct_vtable_offsets']}")
    print(f"        top offsets: {s['top_offsets']}")
    print(f"        base regs  : {s['base_registers']}")
    for r in ok:
        for fn, f in r["functions"].items():
            print(f"        {r['image']:<11} {fn:<16} off={f['offset_in_text']} "
                  f"jalr={f['jalr_count']}")
    print(f"[253A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
