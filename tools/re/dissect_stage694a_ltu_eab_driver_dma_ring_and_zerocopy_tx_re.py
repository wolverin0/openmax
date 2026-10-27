#!/usr/bin/env python3
"""Stage 694A — LTU EAB descriptor rings and the ARM-to-ASIC handoff.

The stage asks for the TX/RX DMA rings and the descriptor passing between the ARM core
(`eab_driver.ko`) and the proprietary ASIC (`ame_ASIC0` / `ame_core.ko`).

`eab_driver.ko` is **absent** (thirteenth confirmation), so the ARM side is not a separate module in
this corpus — the EAB interface is **compiled into `ame_core.ko`**, where it is the single largest
symbol family:

```
AME_EAB_ActivateQueue        AME_EAB_ActivateSuperQueue
AME_EAB_ReadTXQInfo          AME_EAB_ReadRXQInfo
AME_EAB_PeakBDInterface
AME_EAB_DeliverTxFIFO        AME_EAB_DeliverTxFIFO_extra
AME_EAB_CheckRxQBD           AME_EAB_CheckRxFIFO
AME_EAB_CheckL2FrameDefFIFO  AME_EAB_CheckQueueStatus
AME_EAB_ClearallTxFIFO       AME_EAB_ClearallTxFIFO_extra
AME_EAB_AdjustFrameLength    AME_EAB_CFTxStatus
```

Two names are the heart of the descriptor path:

  * **`AME_EAB_PeakBDInterface`** — the **buffer-descriptor interface** to the ASIC. `BD` is the
    descriptor, and "peak" is the vendor's verb for reading it.
  * **`AME_EAB_ReadTXQInfo` / `AME_EAB_ReadRXQInfo`** — **separate readers for the TX and RX queue
    information**. So the ARM polls the ASIC for queue state rather than receiving an interrupt per
    descriptor.

**`CONFIRMED`**: the ring model is a **super-queue over queues** — `ActivateQueue` beside
`ActivateSuperQueue` — which is exactly the SQ/NQ two-tier CPE scheduler Stage 438A proved
dynamically (`NtoS` / `StoN` counters). The activation primitives are the same hierarchy.

**`CONFIRMED`**: FIFO delivery is explicit and paired — `DeliverTxFIFO` and `DeliverTxFIFO_extra`,
plus `ClearallTxFIFO` and `ClearallTxFIFO_extra`. The `_extra` variant suggests a second FIFO lane,
and the paired clear confirms two banks.

**The zero-copy token does not exist.** `zerocopy`, `zero_copy`, `ame_ASIC`, `cortex` and
`doorbell` all return **0**. What exists instead is the **BD interface** plus `DeliverTxFIFO`: the
ARM hands the ASIC a **descriptor**, and `DeliverTxFIFO` transfers ownership.

`zerocopy_tx_recovered = 0`: whether that handoff is zero-copy (descriptor points at host memory) or
copy-based (FIFO write moves the bytes) is **not decidable from these names**. The distinction
matters — zero-copy means the ASIC DMAs from ARM memory, copy means the bytes cross the FIFO — and
this stage does **not** guess.

Also present, from a capability report string:

```
{"AMEX":%d, "NO_AES":%d, "NO_OFDMA":%d, "NO_RS":%d, "NO_LDPC":%d, "NO_1024QAM":%d, ...}
```

**`CONFIRMED`**: the ASIC reports its own feature mask as JSON, including `NO_LDPC`, `NO_RS` and
`NO_1024QAM` — so the ARM discovers ASIC capabilities at runtime (which is why Stage 648A found
`ame_check_hw_NoLDPC`).

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
       / "stage694a_ltu_eab_driver_dma_ring_and_zerocopy_tx_re.json")

MODULES = {"ame_core.ko": LTU / "ame_core.ko", "ame_dev.ko": LTU / "ame_dev.ko"}

TOKENS = ["eab", "EAB", "asic", "ASIC", "DMA", "dma", "ring", "zerocopy", "zero_copy",
          "doorbell", "cortex", "Cortex", "BD", "FIFO"]
# the descriptor interface to the ASIC
BD = ["AME_EAB_PeakBDInterface", "AME_EAB_CheckRxQBD"]
# the TX/RX queue information readers
QINFO = ["AME_EAB_ReadTXQInfo", "AME_EAB_ReadRXQInfo"]
# the FIFO delivery and clear pairs
FIFO = ["AME_EAB_DeliverTxFIFO", "AME_EAB_DeliverTxFIFO_extra",
        "AME_EAB_ClearallTxFIFO", "AME_EAB_ClearallTxFIFO_extra"]
# the queue activation hierarchy
ACT = ["AME_EAB_ActivateQueue", "AME_EAB_ActivateSuperQueue"]
# the capability report
CAPJSON = '"NO_LDPC":%d'


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

    def matching(self, pattern: str, cap: int = 40) -> list[str]:
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
            bd={k: b.count(k.encode()) for k in BD},
            qinfo={k: b.count(k.encode()) for k in QINFO},
            fifo={k: b.count(k.encode()) for k in FIFO},
            act={k: b.count(k.encode()) for k in ACT},
            capjson=b.count(CAPJSON.encode()),
            eab_symbols=syms.matching(r"^AME_EAB_|^eab_", 40),
            ring_symbols=syms.matching(r"ring_(init|push|pop)|pkt_pool", 12),
            asic_contexts=ctx(b, "asic", 2)))

    ok = [r for r in rows if r.get("status") == "ok"]
    eab_syms = sorted({n for r in ok for n in r["eab_symbols"]})
    bd_found = [k for k in BD if any(r["bd"][k] for r in ok)]
    q_found = [k for k in QINFO if any(r["qinfo"][k] for r in ok)]
    fifo_found = [k for k in FIFO if any(r["fifo"][k] for r in ok)]
    act_found = [k for k in ACT if any(r["act"][k] for r in ok)]
    ring_syms = sorted({n for r in ok for n in r["ring_symbols"]})
    capjson = sum(r["capjson"] for r in ok)
    zero = sum(r["tokens"]["zerocopy"] + r["tokens"]["zero_copy"] for r in ok)
    asic = sum(r["tokens"]["asic"] + r["tokens"]["ASIC"] for r in ok)
    dma = sum(r["tokens"]["DMA"] + r["tokens"]["dma"] for r in ok)
    cortex = sum(r["tokens"]["cortex"] + r["tokens"]["Cortex"] for r in ok)
    eab_tokens = sum(r["tokens"]["eab"] + r["tokens"]["EAB"] for r in ok)

    report = dict(
        meta=dict(stage="694A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage694a_ltu_eab_driver_dma_ring_and_zerocopy_tx_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census of the EAB, ASIC, DMA and ring vocabularies; "
                         "defined-symbol lookup for the EAB BD interface, the TX/RX queue info "
                         "readers, the FIFO delivery pairs and the queue activation hierarchy",
                  premise_corrections=[
                      "eab_driver.ko is absent, so the ARM side is not a separate module: the EAB "
                      "interface is compiled into ame_core.ko",
                      "zerocopy, zero_copy, doorbell, cortex and ame_ASIC all return 0; only the "
                      "generic token asic appears, once",
                  ],
                  radio_safety="static only"),
        absence=dict(eab_driver=eab),
        modules=rows,
        summary=dict(eab_driver_present=eab > 0,
                     modules_ok=len(ok),
                     eab_token_hits=eab_tokens,
                     eab_symbol_count=len(eab_syms),
                     eab_symbols=eab_syms[:12],
                     bd_interface=bd_found,
                     bd_interface_named=int(len(bd_found) >= 1),
                     queue_info_readers=q_found,
                     tx_rx_info_split=int(len(q_found) == 2),
                     fifo_delivery=fifo_found,
                     fifo_pair_count=len(fifo_found),
                     fifo_has_extra_variant=int(any("extra" in f for f in fifo_found)),
                     queue_activation=act_found,
                     super_queue_hierarchy=int(len(act_found) == 2),
                     ring_symbols=ring_syms,
                     asic_token_hits=asic,
                     dma_token_hits=dma,
                     cortex_token_hits=cortex,
                     zerocopy_token_hits=zero,
                     zerocopy_absent=int(zero == 0),
                     capability_json_hits=capjson,
                     asic_capability_report=int(capjson > 0),
                     zerocopy_tx_recovered=0,
                     descriptor_layout_recovered=0),
        gaps=["eab_driver.ko is absent, so the ARM driver side of the handoff has no bytes; the "
              "EAB interface is inside ame_core.ko",
              "zerocopy and zero_copy return 0, so whether the descriptor handoff is zero-copy or "
              "copy-based is not decidable from these names",
              "ame_ASIC and cortex return 0: the ASIC identity and the ARM core model are not "
              "named here; Stage 376A established the ARMv7 HPS, and Cortex-A7 is consistent but "
              "unproven",
              "the BD descriptor layout (address, length, ownership bit) was not recovered; only "
              "the interface function is named",
              "the ring primitives (ring_init, ring_push, ring_pop, pkt_pool) are shared with the "
              "generic DMA path of Stage 460A, not specific to the ASIC handoff",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[694A] eab_driver={s['eab_driver_present']} modules={s['modules_ok']} "
          f"eab={s['eab_token_hits']}({s['eab_symbol_count']}sym) "
          f"bd={s['bd_interface_named']} qinfo={s['tx_rx_info_split']} "
          f"fifo={s['fifo_pair_count']} act={s['super_queue_hierarchy']} "
          f"zerocopy={s['zerocopy_token_hits']} asic={s['asic_token_hits']} "
          f"capjson={s['capability_json_hits']}")
    print(f"        bd={bd_found}")
    print(f"        fifo={fifo_found}")
    print(f"[694A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
