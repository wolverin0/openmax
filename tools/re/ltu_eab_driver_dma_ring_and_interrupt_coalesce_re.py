#!/usr/bin/env python3
"""Stage 323A — LTU EAB/YOU DMA ring, IRQ coalescing and skb recycling.

**Premise refuted before analysis**: `eab_driver.ko` does **not exist** anywhere under
`artifacts/` (glob `eab*.ko` returns 0 files). It has been absent since Stage 154A and remains
absent here. The FPGA/PCIe-AXI driver the stage describes is not in the shipped LTU rootfs.

What *is* shipped and carries the DMA plumbing is `ame_core.ko` and `ame_dev.ko`. This stage
reports the DMA/IRQ/coalescing surface of those two modules, and states explicitly that no
`eab_driver.ko` evidence exists.

Surfaces, by symbol and string name only (no descriptor decoding is claimed):

  * DMA ring / descriptor symbols;
  * IRQ / coalescing / mitigation symbols and any small timers near them;
  * RX/TX watermark symbols;
  * skb recycle / free / napi symbols.

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
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage323a_ltu_eab_driver_dma_ring_re.json"

MODULES = {
    "AF-LTU.v2.4.2:ame_core.ko": LTU / "afltu_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_core.ko",
    "AF-LTU.v2.4.2:ame_dev.ko": LTU / "afltu_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_dev.ko",
}
PATTERNS = {
    "dma_ring": re.compile(r"dma|desc|ring|bd_|buffer_desc", re.I),
    "irq": re.compile(r"irq|isr|interrupt|napi", re.I),
    "coalesce": re.compile(r"coalesc|mitigat|budget|poll_|timer", re.I),
    "watermark": re.compile(r"watermark|wm_|threshold|hi_?mark|lo_?mark", re.I),
    "skb_recycle": re.compile(r"skb|recycle|free_|reuse|zero_?copy", re.I),
}


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

    def constants_in(self, names: set[str], limit: int = 0x800) -> Counter:
        hist: Counter[int] = Counter()
        for nm, val, sz, shndx, sn in self.syms:
            if nm not in names or sn not in (".text", ".text.unlikely", ".init.text"):
                continue
            for k in range(0, min(max(sz, 0x200), limit), 4):
                w = self.u32(val + k)
                if w is None:
                    continue
                op, rs, rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, \
                                  (w >> 16) & 0x1F, w & 0xFFFF
                if op == 0x09 and rs == 0 and 0 < s16(imm) <= 0x4000:
                    hist[s16(imm)] += 1
        return hist


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    eab = sorted(str(p.relative_to(REPO_ROOT)).replace("\\", "/")
                 for p in REPO_ROOT.joinpath("artifacts").rglob("eab*.ko"))
    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        ko = Ko(path)
        defined = sorted({s[0] for s in ko.syms if s[3] != 0 and s[0]})
        buckets = {}
        for name, rx in PATTERNS.items():
            hits = sorted({s for s in defined if rx.search(s)})
            buckets[name] = dict(count=len(hits), symbols=hits[:60])
        dma_names = set(buckets["dma_ring"]["symbols"])
        rows.append(dict(module=label, status="ok", bytes=len(ko.data),
                         sha256=hashlib.sha256(ko.data).hexdigest(),
                         defined=len(defined), buckets=buckets,
                         dma_constants=dict(ko.constants_in(dma_names).most_common(20))))

    ok = [r for r in rows if r.get("status") == "ok"]
    report = dict(
        meta=dict(stage="323A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/ltu_eab_driver_dma_ring_and_interrupt_coalesce_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  premise_correction="eab_driver.ko does not exist under artifacts/ (glob "
                                    "eab*.ko = 0 files). The DMA surface reported here belongs "
                                    "to ame_core.ko and ame_dev.ko, not to an EAB driver.",
                  radio_safety="static only"),
        eab_driver_files=eab,
        modules=rows,
        summary=dict(eab_driver_present=bool(eab),
                     modules_ok=len(ok),
                     dma_symbols=max((r["buckets"]["dma_ring"]["count"] for r in ok),
                                     default=0),
                     irq_symbols=max((r["buckets"]["irq"]["count"] for r in ok), default=0),
                     coalesce_symbols=max((r["buckets"]["coalesce"]["count"] for r in ok),
                                          default=0),
                     watermark_symbols=max((r["buckets"]["watermark"]["count"] for r in ok),
                                           default=0),
                     skb_symbols=max((r["buckets"]["skb_recycle"]["count"] for r in ok),
                                     default=0)),
        gaps=["no DMA ring descriptor was decoded: only symbol names and small constants",
              "IRQ coalescing timers were not located as numeric thresholds",
              "zero-copy skb recycling is reported as a symbol bucket, not as a dataflow",
              "eab_driver.ko is absent, so any FPGA/PCIe-AXI specific path is unreachable",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[323A] eab={s['eab_driver_present']} modules={s['modules_ok']} "
          f"dma={s['dma_symbols']} irq={s['irq_symbols']} coal={s['coalesce_symbols']} "
          f"wm={s['watermark_symbols']} skb={s['skb_symbols']}")
    for r in ok:
        print(f"        {r['module']:<32} {r['bytes']:>9}B "
              f"dma={r['buckets']['dma_ring']['count']} irq={r['buckets']['irq']['count']}")
    print(f"[323A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
