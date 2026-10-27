#!/usr/bin/env python3
"""Stage 460A — LTU Beetle `ame_asic0` IRQ 52 coalescing, DMA rings and packet recycling.

The stage names four things in `ame_core.ko` and `eab_driver.ko`:

  * **IRQ 52 interrupt coalescing**;
  * **DMA descriptor rings**;
  * **packet buffer recycling**;
  * the `ame_asic0` / Beetle fabric identity.

`eab_driver.ko` is **absent** (seventh independent confirmation), so everything comes from
`ame_core.ko` — and the vocabulary splits cleanly between what the stage assumes and what the
module actually contains:

| Token | Hits | Verdict |
| :--- | :-: | :--- |
| `coalesc`, `coalesce` | **0** | absent |
| `dma_ring`, `desc` | **0** | absent |
| `recycl`, `buf_pool` | **0** | absent |
| `napi`, `asic0`, `beetle`, `irq52` | **0** | absent |
| `irq` | 12 | **real** — ISR entries |
| `ring` | 41 | **real** — `ring_init`, `ring_push`, `ring_pop` |
| `complet` | 10 | **real** — `Not completed yet (%u)` |

So **the mechanism exists and the stage's names do not**. The ring API is explicit:

```
ring_init    ring_push    ring_pop    pkt_pool_init    pkt_pool_get
```

and the interrupt entries are named `ap_sched_tx_isr`, `ap_sched_rx_isr`,
`ptp_sched_irq_entry`, `ame_core_freq_jump_check_irq` and `ame_core_dump_airq_info`.

**The IRQ number is not a string.** "52" is a routing constant, and no `irq52` literal exists — so
the specific-vector claim cannot be checked by name, only by the ISR names that exist.

`interrupt_coalescing_recovered = 0`: a ring with push/pop is not a coalescing scheme, and no
budget/credit/threshold parameter was found.

Radio safety: static only. No module loaded, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LTU = (REPO_ROOT / "artifacts/firmware_re_xc_ltu/ltu_extracted/afltu_2.4.2"
       / "rootfs_extracted/lib/modules/3.14.65")
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage460a_ltu_beetle_dma_ring_and_irq52_coalescing_re.json")

# ame_core.ko is the only readable target; eab_driver.ko is probed for absence
TARGETS = {"ame_core.ko": LTU / "ame_core.ko"}
ABSENT = ["eab_driver.ko"]

# coalescing vocabulary the stage names: expected absent
COALESCE = ["coalesc", "coalesce", "irq52", "napi"]
# tokens that look related but are not: scheduler budgets and "modern scanning"
INCIDENTAL = ["budget", "moder"]
# ring and pool vocabulary
RING = ["ring", "dma_ring", "desc", "ring_push", "ring_pop", "ring_init"]
RING_PRIMS = ["ring_init", "ring_push", "ring_pop"]
POOL = ["pkt_pool", "pkt_pool_get", "pkt_pool_init", "recycl", "buf_pool", "free_list"]
POOL_PRIMS = ["pkt_pool_init", "pkt_pool_get"]
# fabric identity
FABRIC = ["asic0", "beetle", "BEETLE", "ame_asic", "irq"]
# completion / liveness diagnostics
LIVENESS = ["complet", "Not completed yet", "timeout", "stall"]


def ctx(b: bytes, tok: str, n: int = 4, w: int = 66) -> list[str]:
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

    absent = {n: len([p for p in (REPO_ROOT / "artifacts").rglob(n)]) for n in ABSENT}

    rows = []
    for name, path in TARGETS.items():
        if not path.exists():
            rows.append(dict(module=name, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        rows.append(dict(
            module=name, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            coalesce={t: b.count(t.encode()) for t in COALESCE},
            incidental={t: b.count(t.encode()) for t in INCIDENTAL},
            ring_primitives={t: b.count(t.encode()) for t in RING_PRIMS},
            pool_primitives={t: b.count(t.encode()) for t in POOL_PRIMS},
            incidental_contexts={t: ctx(b, t, 2) for t in INCIDENTAL if b.count(t.encode())},
            ring={t: b.count(t.encode()) for t in RING},
            pool={t: b.count(t.encode()) for t in POOL},
            fabric={t: b.count(t.encode()) for t in FABRIC},
            liveness={t: b.count(t.encode()) for t in LIVENESS},
            irq_contexts=ctx(b, "irq", 5),
            ring_contexts=ctx(b, "ring", 5),
            completion_contexts=ctx(b, "Not completed yet", 2),
            ring_symbols=syms.matching(r"ring_(init|push|pop)|^ring", 20),
            pool_symbols=syms.matching(r"pkt_pool|pool_(get|put|init)", 20),
            isr_symbols=syms.matching(r"_isr|_irq|irq_entry", 24),
            dma_symbols=syms.matching(r"dma", 20)))

    ok = [r for r in rows if r.get("status") == "ok"]
    coalesce_total = sum(sum(r["coalesce"].values()) for r in ok)
    incidental_total = sum(sum(r["incidental"].values()) for r in ok)
    ring_prims = sorted({t for r in ok for t, v in r["ring_primitives"].items() if v})
    pool_prims = sorted({t for r in ok for t, v in r["pool_primitives"].items() if v})
    ring_syms = sorted({n for r in ok for n in r["ring_symbols"]})
    pool_syms = sorted({n for r in ok for n in r["pool_symbols"]})
    isr_syms = sorted({n for r in ok for n in r["isr_symbols"]})
    dma_syms = sorted({n for r in ok for n in r["dma_symbols"]})
    ring_hits = sum(r["ring"]["ring"] for r in ok)
    pool_hits = sum(r["pool"]["pkt_pool"] for r in ok)
    liveliness = sum(r["liveness"]["Not completed yet"] for r in ok)

    report = dict(
        meta=dict(stage="460A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage460a_ltu_beetle_dma_ring_and_irq52_coalescing_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census of the coalescing, ring, pool, fabric and liveness "
                         "vocabularies; context extraction of the irq and ring sites; "
                         "defined-symbol lookup for the ring/pool/ISR families",
                  premise_corrections=[
                      "eab_driver.ko is absent, so ame_core.ko is the only readable target",
                      "coalesc, dma_ring, desc, recycl, buf_pool, napi and asic0 all have 0 hits; "
                      "the module names ring_init/ring_push/ring_pop and pkt_pool_* instead",
                  ],
                  radio_safety="static only"),
        absence=absent,
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     eab_driver_present=absent["eab_driver.ko"] > 0,
                     coalescing_tokens=coalesce_total,
                     incidental_tokens=incidental_total,
                     ring_primitives=ring_prims,
                     pool_primitives=pool_prims,
                     irq52_literal=int(any(r["coalesce"]["irq52"] for r in ok)),
                     ring_token_hits=ring_hits,
                     pkt_pool_token_hits=pool_hits,
                     ring_symbols=ring_syms,
                     pool_symbols=pool_syms,
                     isr_symbols=isr_syms,
                     dma_symbols=dma_syms[:8],
                     completion_messages=liveliness,
                     dma_ring_named=int(bool(ring_prims)),
                     buffer_recycling_named=int(bool(pool_prims)),
                     beacon_irq_named=int(bool(isr_syms)),
                     interrupt_coalescing_recovered=0),
        gaps=["eab_driver.ko is absent, so the stage's second module has no bytes",
              "no coalescing token exists: coalesc, coalesce, irq52 and napi all have 0 hits, so "
              "no interrupt moderation parameter was recovered",
              "the incidental hits are not moderation: budget appears only as "
              "scheduler_budget_us / symbol_budget_us, and moder only inside 'modern atuo "
              "scanning'",
              "IRQ 52 is a routing constant, not a string; no irq52 literal exists, so the "
              "specific vector claim cannot be verified by name",
              "dma_ring, desc and recycl are absent; the ring is named ring_init/ring_push/"
              "ring_pop and the pool is pkt_pool_get/pkt_pool_init",
              "a ring with push/pop is a descriptor queue, not a demonstration of coalescing",
              "`Not completed yet (%u)` proves completion tracking, not a recycling policy",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[460A] modules={s['modules_ok']} eab={s['eab_driver_present']} "
          f"coalesce={s['coalescing_tokens']} incidental={s['incidental_tokens']} "
          f"irq52={s['irq52_literal']} ring={s['ring_token_hits']} "
          f"pool={s['pkt_pool_token_hits']} completion={s['completion_messages']}")
    print(f"        ring_prims={ring_prims} pool_prims={pool_prims}")
    print(f"        isr_syms={isr_syms[:8]}")
    print(f"[460A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
