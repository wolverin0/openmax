#!/usr/bin/env python3
"""Stage 256A — knobs 171..255 against the HAL vtable slots recovered in 253A.

For each of the third 85 `airOS_UMAC_UPH` knobs, and for each of `umac.ko` and `ath_dev.ko`:

  1. locate the knob name as a `.rodata` literal and recover the `.text` address where it is
     materialised;
  2. find the enclosing function by walking back to the `addiu $sp,$sp,-N` prologue;
  3. scan that function for `lw $t9, off($base)` + `jalr $t9` pairs and record which of the
     Stage 253A vtable offsets it reaches.

The output answers exactly one question per knob: **does the function that references this
knob dispatch through the recovered HAL vtable, and at which slot?**

MIPS32 big-endian, capstone-free (raw word decode) so the script has no disassembler dependency.

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
KNOBS = REPO_ROOT / "orchestration" / "autoresearch" / "firmware_knob_candidates.json"
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage256a_knobs_171_255_hal_vtable.json"

MODULES = {
    "WA.v8.7.25:ubnt_poll_host.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "WA.v8.7.25:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC.v8.7.25:ubnt_poll_host.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XC.v8.7.25:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
}
# vtable offsets recovered in 253A
V253 = {4, 8, 156, 160, 164, 204, 208, 296, 300, 396, 520}
LO, HI = 170, 255


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
        tx = self.by_name.get(".text")
        self.text = d[tx["off"]:tx["off"] + tx["size"]] if tx else b""
        # address -> file offset helper for .rodata literal lookup
        self.rodata = {}
        for h in secs:
            if h["type"] == 1 and h["name"].startswith(".rodata"):
                self.rodata[h["name"]] = d[h["off"]:h["off"] + h["size"]]

    def u32(self, off: int) -> int | None:
        if off < 0 or off + 4 > len(self.text):
            return None
        return struct.unpack(self.endian + "I", self.text[off:off + 4])[0]

    def str_offsets(self, needle: str) -> list[int]:
        """.text offsets where a lui/addiu pair materialises `needle`'s address."""
        target = needle.encode()
        found = []
        for sec, blob in self.rodata.items():
            idx = blob.find(target + b"\0")
            while idx >= 0:
                # the literal's section offset; the code builds the address, so match by
                # searching for the string then verifying via the low-16 constant
                found.append((sec, idx))
                idx = blob.find(target + b"\0", idx + 1)
                if len(found) > 8:
                    break
        return found

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
            w = self.u32(fn + k)
            if w == 0x03E00008:
                return fn + k + 8
        return fn + cap

    def jalr_slots(self, fn: int) -> list[dict[str, Any]]:
        out = []
        hi = self.extent(fn)
        for off in range(fn, max(fn, hi - 16), 4):
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
                                in_253a=(imm in V253)))
                break
        return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    data = json.loads(KNOBS.read_text(encoding="utf-8"))
    bound = [k for k in data["knobs"] if str(k.get("boundary")) == "airOS_UMAC_UPH"]
    bound.sort(key=lambda k: (str(k.get("family")), str(k.get("id"))))
    slice85 = bound[LO:HI]

    rows = []
    slot_hist: Counter[int] = Counter()
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        ko = Ko(path)
        per = []
        for k in slice85:
            name = str(k.get("name"))
            ro = ko.str_offsets(name)
            if not ro:
                per.append(dict(id=k.get("id"), name=name, literal_present=False))
                continue
            # find a .text site that loads the low 16 bits of the literal offset
            sec, idx = ro[0]
            lo16 = idx & 0xFFFF
            sites = []
            for off in range(0, max(0, len(ko.text) - 12), 4):
                w = ko.u32(off)
                if w is None or (w & 0xFFFF0000) not in (0x24040000, 0x24050000,
                                                        0x24060000, 0x24070000,
                                                        0x3C040000, 0x3C050000,
                                                        0x3C060000, 0x3C070000):
                    continue
                if (w & 0xFFFF) == lo16:
                    sites.append(off)
                if len(sites) >= 4:
                    break
            fn = ko.enclosing(sites[0]) if sites else None
            slots = ko.jalr_slots(fn) if fn is not None else []
            for s in slots:
                if s["in_253a"]:
                    slot_hist[s["offset"]] += 1
            per.append(dict(id=k.get("id"), name=name, literal_present=True,
                            rodata_section=sec, rodata_offset=f"0x{idx:06x}",
                            text_sites=[f"0x{x:06x}" for x in sites[:4]],
                            function=(f"0x{fn:06x}" if fn is not None else None),
                            vtable_slots=[s for s in slots if s["in_253a"]][:12],
                            reaches_253a_vtable=any(s["in_253a"] for s in slots)))
        rows.append(dict(module=label, status="ok", bytes=len(ko.data),
                         sha256=hashlib.sha256(ko.data).hexdigest(),
                         knobs=per,
                         knobs_with_literal=sum(1 for p in per if p["literal_present"]),
                         knobs_reaching_vtable=sum(1 for p in per
                                                   if p.get("reaches_253a_vtable"))))

    ok = [r for r in rows if r.get("status") == "ok"]
    report = dict(
        meta=dict(stage="256A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage256a_knobs_171_255_hal_vtable.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  slice=dict(boundary="airOS_UMAC_UPH", lo=LO, hi=HI,
                             count=len(slice85)),
                  method="knob literal -> .rodata hit -> lui/addiu materialisation site -> "
                         "enclosing prologue -> lw+jalr slots inside that function",
                  vtable_offsets_from_253a=sorted(V253),
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     knobs=len(slice85),
                     knobs_with_literal=max((r["knobs_with_literal"] for r in ok), default=0),
                     knobs_reaching_vtable=max((r["knobs_reaching_vtable"] for r in ok),
                                               default=0),
                     slot_histogram=dict(slot_hist.most_common(12))),
        gaps=["a knob whose literal was not found in .rodata is reported absent, not guessed",
              "the function is attributed from the first lui/addiu match; a knob referenced "
              "from several functions is represented by one",
              "reaching a 253A slot means the enclosing function dispatches through the HAL "
              "vtable, not that this knob is the argument",
              "the low-half literal-to-site join is unsound as an identifier, so zero "
              "attribution is a method limit and not evidence about the knob",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[256A] modules={s['modules_ok']} knobs={s['knobs']} "
          f"literal={s['knobs_with_literal']} reaching_vtable={s['knobs_reaching_vtable']}")
    print(f"        slots: {s['slot_histogram']}")
    for r in ok:
        print(f"        {r['module']:<26} lit={r['knobs_with_literal']:<3} "
              f"vtable={r['knobs_reaching_vtable']}")
    print(f"[256A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
