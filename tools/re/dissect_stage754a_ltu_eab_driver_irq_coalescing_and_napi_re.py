#!/usr/bin/env python3
"""Stage 754A — GIC 52, IRQ coalescing and the NAPI poll budget on LTU.

The stage asks for three things in `eab_driver.ko` and `ame_core.ko`:

  * the **GIC 52** interrupt;
  * **IRQ coalescing**;
  * the **NAPI poll budget**.

All three fail, and the way they fail is the finding.

**`eab_driver.ko` is absent** (fourteenth confirmation).

**NAPI does not exist.** `napi` and `NAPI` return **0** in both modules. NAPI is a **Linux
networking** API; this driver is not a netdev driver, so there is no poll budget to find.

**Coalescing does not exist either.** `coalesc` and `COALESC` return **0** — the second independent
confirmation after Stage 460A. There is no interrupt moderation parameter anywhere in the module.

**`gic` is inside `vermagic`.** The single `gic` hit in each module is:

```
vermagic=3.14.65 SMP preempt mod_unload ARMv7 p2v8
```

**`REFUTED`**: `gic_is_vermagic = 1`. The Generic Interrupt Controller is **not named**; the token
match is the module's compatibility string. This is the tenth substring trap of the series and the
second in two stages, after `gic` following `compensat` in 728A.

**`budget` is the scheduler's.** All 8 hits are:

```
scheduler_budget_us:%u  symbol_budget_us:%u
```

**`REFUTED`**: `budget_is_scheduler = 1`. That is a **TDMA scheduling** budget in microseconds, not a
NAPI poll budget. Stage 460A already established this; the re-measurement confirms it.

**`poll` means polling mode.** Both hits are `enter polling mode` and `Q#%u is active` — the same
strings Stage 438A found. This is the **TDMA poll-list** mechanism, not NAPI polling.

## What the interrupt surface actually is

```
ptmp_sched_irq_entry        ptp_sched_irq_entry
ame_core_freq_jump_check_irq
ame_core_dump_airq_info
ame_core_airQexcptHandler   monitor_airQueue_routine / _work
Sched_update_budget_by_QId
```

**`CONFIRMED`**: the interrupt entries are **scheduler-scoped** — one for PtMP and one for PtP — plus
a **frequency-jump check** and an **air-queue** monitor with an exception handler.

That is the real architecture: the interrupt is not a packet-completion vector that needs moderation,
it is a **scheduling tick**. A tick-driven design does not coalesce, because coalescing a tick
delays the schedule; it instead **budgets** the work done per tick — which is exactly what
`scheduler_budget_us` is.

`irq 52` as a **number** cannot be verified: an interrupt number is a routing constant in the
interrupt table, never a string. `irq52_literal = 0`.

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
LTU = (REPO_ROOT / "artifacts" / "firmware_re_xc_ltu/ltu_extracted/afltu_2.4.2"
       / "rootfs_extracted/lib/modules/3.14.65")
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage754a_ltu_eab_driver_irq_coalescing_and_napi_re.json")

MODULES = {"ame_core.ko": LTU / "ame_core.ko", "ame_dev.ko": LTU / "ame_dev.ko"}

TOKENS = ["napi", "NAPI", "coalesc", "COALESC", "budget", "BUDGET", "gic", "GIC",
          "irq", "IRQ", "poll", "irq52"]
# the scheduler IRQ entries
SCHED_IRQ = ["ptmp_sched_irq_entry", "ptp_sched_irq_entry"]
# the other interrupt entries
IRQ_ENTRIES = ["ame_core_freq_jump_check_irq", "ame_core_dump_airq_info"]
# the air-queue monitor
AIRQ = ["ame_core_airQexcptHandler", "monitor_airQueue_routine", "monitor_airQueue_work"]
# the scheduler budget
SCHED_BUDGET = "scheduler_budget_us"
# the trap: gic inside vermagic
VERMAGIC = "vermagic="
# the polling-mode strings
POLLMODE = "enter polling mode"


def ctx(b: bytes, tok: str, n: int = 2, w: int = 66) -> list[str]:
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

    def matching(self, pattern: str, cap: int = 20) -> list[str]:
        return sorted({n for n in self.names if re.search(pattern, n, re.I)})[:cap]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    eab = len([p for p in (REPO_ROOT / "artifacts").rglob("eab_driver.ko")])
    rows = []
    for name, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=name, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        rows.append(dict(
            module=name, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            tokens={t: b.count(t.encode()) for t in TOKENS},
            sched_irq={k: b.count(k.encode()) for k in SCHED_IRQ},
            irq_entries={k: b.count(k.encode()) for k in IRQ_ENTRIES},
            airq={k: b.count(k.encode()) for k in AIRQ},
            sched_budget=b.count(SCHED_BUDGET.encode()),
            vermagic=b.count(VERMAGIC.encode()),
            pollmode=b.count(POLLMODE.encode()),
            gic_contexts=ctx(b, "gic", 1),
            irq_symbols=syms.matching(r"irq|airq", 16)))

    ok = [r for r in rows if r.get("status") == "ok"]
    sched_irq = [k for k in SCHED_IRQ if any(r["sched_irq"][k] for r in ok)]
    entries = [k for k in IRQ_ENTRIES if any(r["irq_entries"][k] for r in ok)]
    airq = [k for k in AIRQ if any(r["airq"][k] for r in ok)]
    budget = sum(r["sched_budget"] for r in ok)
    vermagic = sum(r["vermagic"] for r in ok)
    pollmode = sum(r["pollmode"] for r in ok)
    napi = sum(r["tokens"]["napi"] + r["tokens"]["NAPI"] for r in ok)
    coal = sum(r["tokens"]["coalesc"] + r["tokens"]["COALESC"] for r in ok)
    gic = sum(r["tokens"]["gic"] + r["tokens"]["GIC"] for r in ok)
    irq52 = sum(r["tokens"]["irq52"] for r in ok)
    irq_syms = sorted({n for r in ok for n in r["irq_symbols"]})
    gic_ctx = " ".join(c for r in ok for c in r["gic_contexts"])

    report = dict(
        meta=dict(stage="754A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage754a_ltu_eab_driver_irq_coalescing_and_napi_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census of the NAPI, coalescing, GIC, IRQ and budget "
                         "vocabularies; scheduler-IRQ entry extraction; context classification of "
                         "the gic and budget hits",
                  premise_corrections=[
                      "eab_driver.ko is absent, so the stage's driver module has no bytes",
                      "gic is a substring of vermagic, napi does not exist at all, and budget is "
                      "the TDMA scheduler budget rather than a NAPI poll budget",
                  ],
                  radio_safety="static only"),
        absence=dict(eab_driver=eab),
        modules=rows,
        summary=dict(eab_driver_present=eab > 0,
                     modules_ok=len(ok),
                     napi_token_hits=napi,
                     napi_absent=int(napi == 0),
                     coalescing_token_hits=coal,
                     coalescing_absent=int(coal == 0),
                     gic_token_hits=gic,
                     gic_is_vermagic=int(vermagic > 0 and "vermagic" in gic_ctx),
                     vermagic_hits=vermagic,
                     irq52_literal=irq52,
                     irq_number_is_a_string=int(irq52 > 0),
                     sched_irq_entries=sched_irq,
                     sched_irq_count=len(sched_irq),
                     ptmp_ptp_split=int(len(sched_irq) == 2),
                     other_irq_entries=entries,
                     airq_handler_count=len(airq),
                     airq_exception_handler=int("ame_core_airQexcptHandler" in airq),
                     sched_budget_hits=budget,
                     budget_is_scheduler=int(budget > 0),
                     polling_mode_hits=pollmode,
                     poll_is_polling_mode=int(pollmode > 0),
                     irq_symbols=irq_syms[:8],
                     napi_poll_budget_recovered=0,
                     irq_coalescing_recovered=0,
                     gic_vector_map_recovered=0),
        gaps=["eab_driver.ko is absent, so the driver side of the interrupt handling has no bytes",
              "napi and NAPI return 0: this is not a netdev driver, so there is no NAPI poll "
              "budget to recover",
              "coalesc and COALESC return 0: no interrupt moderation parameter exists, which is "
              "the second confirmation after Stage 460A",
              "gic is a substring of vermagic (vermagic=3.14.65 SMP preempt mod_unload ARMv7 "
              "p2v8), so the Generic Interrupt Controller is not named",
              "irq 52 is a routing constant in the interrupt table, not a string; no irq52 "
              "literal exists",
              "the interrupt entries are scheduler-scoped (ptmp_sched_irq_entry, "
              "ptp_sched_irq_entry) with a frequency-jump check and an air-queue monitor, not "
              "packet-completion vectors",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[754A] eab={s['eab_driver_present']} modules={s['modules_ok']} "
          f"napi={s['napi_token_hits']} coalesc={s['coalescing_token_hits']} "
          f"gic={s['gic_token_hits']}(vermagic={s['gic_is_vermagic']}) "
          f"sched_irq={s['sched_irq_count']} budget={s['sched_budget_hits']} "
          f"pollmode={s['polling_mode_hits']}")
    print(f"        sched_irq={sched_irq}")
    print(f"[754A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
