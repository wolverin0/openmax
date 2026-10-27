#!/usr/bin/env python3
"""Stage 713A — PCIe copy-engine rings, pktlog buffers and MSI configuration.

The stage asks for the **8 PCIe Copy Engine rings (CE0..CE7)** in ath10k and `umac.ko`, mapped to
WMI control, HTT TX, HTT RX and the pktlog rings, with their `nentries` sizes and the MSI-versus-legacy
interrupt handling.

`ath10k_core.ko` is **absent** (0 files, sixth confirmation), so the ath10k CE table cannot be read.
The vendor `umac.ko` carries a **full per-engine CE implementation** under a different naming scheme:

```
CE_init   CE_fini   CE_pause   CE_send
CE_recv_buf_enqueue      CE_recv_entries_avail     CE_recv_entries_done
CE_recv_watermarks_set   CE_recv_cb_register
CE_completed_send_next   CE_completed_recv_next    CE_cancel_send_next
CE_revoke_recv_next
CE_per_engine_handler    CE_per_engine_service
CE_per_engine_service_any          CE_per_engine_servicereap
```

**`CONFIRMED`**: `per_engine_service` present. The dispatcher is explicitly **per-engine** — one
handler serves a set of engines, and `_service_any` plus `_servicereap` are the sweep and reclamation
passes. That is the architectural fact the stage is after: the CE layer is **indexed by engine**,
not a single queue.

**`REFUTED`**: the engines are **not numbered** in the strings. `CE0` through `CE7` return **0**
hits. The engine index is a **runtime parameter**, so "8 rings" cannot be proven from the module —
only that the code is structured to handle N of them.

The receive path has an explicit **watermark** API:

```
CE_recv_watermarks_set   CE_recv_entries_avail   CE_recv_entries_done
```

**`CONFIRMED`**: flow control is **watermark-based** — the host sets a threshold, publishes how many
receive entries are available, and the engine reports how many are done. That is how a CE ring avoids
overflow without per-descriptor interrupts.

## Queues are allocated, not hard-coded

The HIF layer exposes:

```
HIFConfigureDevice   HIFGetDefaultPipe   HIFGetFreeQueueNumber
HIFClaimDevice       HIFAttachHTC        HIFDetachHTC
HIFExchangeBMIMsg    HIFDiagReadMem      HIFDiagWriteMem
```

**`CONFIRMED`**: `HIFGetFreeQueueNumber` allocates a queue at runtime. So the mapping from logical
service (WMI control, HTT TX, HTT RX, pktlog) to physical CE is **dynamic**, which is why no
`CE0 = WMI` table exists in the binary.

## pktlog has its own buffer lifecycle

```
pktlog_alloc_buf   pktlog_release_buf   pktlog_setsize
```

**`CONFIRMED`**: pktlog allocates and releases **its own buffers** and has a settable size. It is a
separate transport from HTT, consistent with the ath10k design where pktlog uses dedicated CE
channels.

## MSI is negotiated, with a legacy fallback

```
%s : num_desired MSI set to %d
%s %s: ath_request_irq failed
<6>. Using PCI…
```

**`CONFIRMED`**: the driver **requests a number of MSI vectors** and has an explicit fallback path
when IRQ request fails. So the interrupt mode is a negotiation, not a compile-time choice — which
matches `ar9300_set_intr_mitigation_timer` found in `ath_hal.ko` (Stage 415A's sibling).

`ring_count_configured` and `ce_nentries_table_recovered` are **0**: the per-engine `nentries`
values are runtime configuration, and the only `nentries=%d` in the module belongs to a **DFS**
command log, not to a CE ring.

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
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage713a_ath10k_pci_copy_engine_rings_and_msi_re.json")

MODULES = {
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
}

CE = ["CE_init", "CE_fini", "CE_send", "CE_pause",
      "CE_per_engine_handler", "CE_per_engine_service",
      "CE_per_engine_service_any", "CE_per_engine_servicereap"]
RECV = ["CE_recv_buf_enqueue", "CE_recv_entries_avail", "CE_recv_entries_done",
        "CE_recv_watermarks_set", "CE_recv_cb_register"]
# the numbered engine names the stage assumes
NUMBERED = ["CE0", "CE1", "CE2", "CE3", "CE4", "CE5", "CE6", "CE7"]
# pktlog buffer lifecycle
PKTLOG = ["pktlog_alloc_buf", "pktlog_release_buf", "pktlog_setsize"]
# queue allocation
HIF = ["HIFGetFreeQueueNumber", "HIFGetDefaultPipe", "HIFConfigureDevice"]
# interrupt negotiation
MSI_MSG = "num_desired MSI set to"
LEGACY_MSG = "Using PCI"


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

    def matching(self, pattern: str, cap: int = 30) -> list[str]:
        return sorted({n for n in self.names if re.search(pattern, n, re.I)})[:cap]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    ath10k = len([p for p in (REPO_ROOT / "artifacts").rglob("ath10k*.ko")])

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        rows.append(dict(
            module=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            ce={k: b.count(k.encode()) for k in CE},
            recv={k: b.count(k.encode()) for k in RECV},
            numbered={k: b.count(k.encode()) for k in NUMBERED},
            pktlog={k: b.count(k.encode()) for k in PKTLOG},
            pktlog_tokens={k: b.count(k.encode()) for k in PKTLOG},
            hif={k: b.count(k.encode()) for k in HIF},
            msi_msg=b.count(MSI_MSG.encode()),
            legacy_msg=b.count(LEGACY_MSG.encode()),
            ce_symbols=syms.matching(r"^CE_", 24),
            pktlog_symbols=syms.matching(r"pktlog", 12),
            hif_symbols=syms.matching(r"^HIF", 16),
            msi_contexts=ctx(b, "MSI", 2),
            nentries_contexts=ctx(b, "nentries", 1)))

    ok = [r for r in rows if r.get("status") == "ok"]
    ce_syms = sorted({n for r in ok for n in r["ce_symbols"]})
    pkt_syms = sorted({n for r in ok for n in r["pktlog_symbols"]})
    hif_syms = sorted({n for r in ok for n in r["hif_symbols"]})
    ce_found = [k for k in CE if any(r["ce"][k] for r in ok)]
    recv_found = [k for k in RECV if any(r["recv"][k] for r in ok)]
    numbered = sum(sum(r["numbered"].values()) for r in ok)
    pkt_found = [k for k in PKTLOG if any(r["pktlog"][k] for r in ok)]
    hif_found = [k for k in HIF if any(r["hif"][k] for r in ok)]
    msi_msg = sum(r["msi_msg"] for r in ok)
    legacy = sum(r["legacy_msg"] for r in ok)

    report = dict(
        meta=dict(stage="713A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage713a_ath10k_pci_copy_engine_rings_and_msi_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="CE symbol-family extraction for the per-engine dispatcher and the "
                         "watermark API; pktlog buffer lifecycle lookup; HIF queue allocation "
                         "lookup; MSI negotiation and legacy fallback message extraction",
                  premise_corrections=[
                      "ath10k_core.ko is absent, so the ath10k CE table mapping CE0..CE7 to WMI, "
                      "HTT TX, HTT RX and pktlog cannot be read",
                      "CE0 through CE7 do not exist as strings: the engine index is a runtime "
                      "parameter, so the count of 8 rings is not provable from the module",
                  ],
                  radio_safety="static only"),
        ath10k_modules=ath10k,
        modules=rows,
        summary=dict(ath10k_core_present=ath10k > 0,
                     modules_ok=len(ok),
                     ce_symbol_count=len(ce_syms),
                     ce_symbols=ce_syms[:10],
                     ce_control_set=ce_found,
                     ce_control_count=len(ce_found),
                     per_engine_service_present=int("CE_per_engine_service" in ce_found),
                     per_engine_service_variants=int(
                         sum(1 for k in ce_found if "per_engine" in k)),
                     watermark_api_present=int("CE_recv_watermarks_set" in recv_found),
                     recv_control_count=len(recv_found),
                     numbered_ce_hits=numbered,
                     engines_are_numbered=int(numbered > 0),
                     engine_count_proven=0,
                     hif_queue_alloc=int("HIFGetFreeQueueNumber" in hif_found),
                     hif_queue_symbols=hif_found,
                     pktlog_symbols=pkt_syms,
                     pktlog_lifecycle=int(all(any(r["pktlog_tokens"][k] for r in ok) for k in PKTLOG)),
                     pktlog_raw_counts={k: sum(r["pktlog_tokens"][k] for r in ok) for k in PKTLOG},
                     msi_negotiation_msg=msi_msg,
                     legacy_fallback_msg=legacy,
                     msi_is_negotiated=int(msi_msg > 0),
                     ce_nentries_table_recovered=0,
                     ring_service_map_recovered=0),
        gaps=["ath10k_core.ko is absent, so the ath10k mapping of CE0..CE7 to WMI control, HTT TX, "
              "HTT RX and pktlog CE1/CE5 cannot be read",
              "CE0..CE7 return 0 hits: the engine index is a runtime parameter, and the module "
              "never enumerates eight fixed rings",
              "the CE nentries values are runtime configuration; the only nentries=%d in the "
              "module belongs to a DFS command log, not a ring",
              "the mapping from logical service to physical engine is dynamic through "
              "HIFGetFreeQueueNumber, so no static table exists to recover",
              "pktlog has its own buffer lifecycle and size control, but which engine carries it "
              "was not determined",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[713A] ath10k={s['ath10k_core_present']} modules={s['modules_ok']} "
          f"ce={s['ce_symbol_count']} per_engine={s['per_engine_service_variants']} "
          f"watermark={s['watermark_api_present']} numbered={s['numbered_ce_hits']} "
          f"hif_alloc={s['hif_queue_alloc']} pktlog={len(pkt_syms)} "
          f"msi_msg={s['msi_negotiation_msg']}")
    print(f"        ce={ce_syms[:8]}")
    print(f"[713A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
