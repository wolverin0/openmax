#!/usr/bin/env python3
"""Stage 648A — LTU ARQ / HARQ, LDPC / FEC block-error counters and retry descriptors.

The stage names three things in `ame_core.ko` and `ame_dev.ko`:

  * **ARQ / HARQ** retransmission state machines;
  * **LDPC / FEC** block-error counters;
  * **TX/RX retry** descriptors.

The first is a clean negative and the other two are strong positives.

**There is no ARQ and no HARQ by name.** All four identifiers return zero:

| Token | Hits |
| :--- | :-: |
| `arq`, `ARQ` | **0** |
| `harq`, `HARQ` | **0** |
| `retrans`, `RETRANS` | **0** |
| `nack`, `NACK` | **0** |

**`REFUTED`**: neither an ARQ nor a HARQ state machine is named in these two modules. Whatever
retransmission exists is expressed through **BLER** (block error rate) and queue **retry**, both of
which are richly instrumented — but the state machine itself is not a named object.

**BLER is the real telemetry and it is per-CPE.** 34 hits across both modules, with a named family:

```
ame_bbp_get_bler        ame_bbp_get_bler_cz      ame_bbp_set_bler_clear
bbp_show_bler           bbp_show_bler_cz
autoMCS_get_each_bler   autoMCS_reset_each_bler
check_cbler_decode      fty_bbp_log_bler         fty_bbp_log_bler_cz
cpeRxBler               cpeTxBler
```

Two details matter:

  * **`cpeRxBler` and `cpeTxBler` are separate** — uplink and downlink block error are counted
    independently per CPE, which is what a PtMP AP needs to tell a local problem from a remote one;
  * **`_cz` is a second variant** (`get_bler_cz`, `show_bler_cz`, `log_bler_cz`) alongside the base
    BLER, and `check_cbler_decode` names a **coded** block error. Three distinct BLER surfaces.

**LDPC is controllable, not just readable.**

```
ame_bbp_op_get_rxTopB_ldpcIteration     ame_bbp_op_set_rxTopB_ldpcIteration
bbp_mrx_util_get_rxTopB_ldpcIteration   bbp_mrx_util_set_rxTopB_ldpcIteration
ame_check_hw_NoLDPC
```

**`CONFIRMED`**: the LDPC **iteration count is a settable parameter** (get and set, at two layers),
and there is a hardware capability check `ame_check_hw_NoLDPC` plus the runtime message
`No ldpc supported`. So LDPC effort is tunable, which is the lever a latency-versus-reliability
trade-off needs.

**The retry descriptor is visible in a queue-dump line.**

```
Q[%d] tail=%d, reIdx=%d, retry=%d
```

**`CONFIRMED`**: a transmit queue is described by `tail`, **`reIdx`** (retry index) and **`retry`**
(retry count). That is the TX retry descriptor the stage asks about — a per-queue triple, not a
per-packet struct.

**Four sysfs pairs** in `ame_dev.ko` make all of it readable and writable:

```
bler_show/store      c_bler_show/store
each_bler_show/store ldpc_iteration_show/store
```

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
       / "stage648a_ltu_ame_core_arq_retrans_and_fec_ldpc_re.json")

MODULES = {"ame_core.ko": LTU / "ame_core.ko", "ame_dev.ko": LTU / "ame_dev.ko"}

TOKENS = ["arq", "ARQ", "harq", "HARQ", "retrans", "RETRANS", "nack", "NACK",
          "bler", "BLER", "ldpc", "LDPC", "fec", "FEC", "retry"]
# the identifiers the stage assumes
ASSUMED = ["arq", "harq", "retrans", "nack", "retransmission"]
# the BLER family
BLER = ["ame_bbp_get_bler", "ame_bbp_set_bler_clear", "cpeRxBler", "cpeTxBler",
        "autoMCS_get_each_bler", "check_cbler_decode"]
# the LDPC iteration control
LDPC = ["ldpcIteration", "ame_check_hw_NoLDPC", "No ldpc supported"]
# the retry descriptor line
RETRY_LINE = "reIdx=%d, retry=%d"
# the sysfs pairs
SYSFS = ["bler", "c_bler", "each_bler", "ldpc_iteration"]


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
            assumed={t: b.count(t.encode()) for t in ASSUMED},
            bler={k: b.count(k.encode()) for k in BLER},
            ldpc={k: b.count(k.encode()) for k in LDPC},
            sysfs={k: dict(show=b.count((k + "_show").encode()),
                           store=b.count((k + "_store").encode())) for k in SYSFS},
            retry_line=b.count(RETRY_LINE.encode()),
            bler_symbols=[n for n in syms.matching(r"bler", 24)
                          if "enable" not in n and "disable" not in n],
            ldpc_symbols=syms.matching(r"ldpc", 16),
            retry_contexts=ctx(b, "reIdx", 2)))

    ok = [r for r in rows if r.get("status") == "ok"]
    assumed_hits = sum(sum(r["assumed"].values()) for r in ok)
    bler_syms = sorted({n for r in ok for n in r["bler_symbols"]})
    ldpc_syms = sorted({n for r in ok for n in r["ldpc_symbols"]})
    cpe_pair = sum(1 for r in ok if r["bler"]["cpeRxBler"] and r["bler"]["cpeTxBler"])
    each_bler = sum(1 for r in ok if r["bler"]["autoMCS_get_each_bler"])
    cbler = sum(1 for r in ok if r["bler"]["check_cbler_decode"])
    ldpc_iter = sum(r["ldpc"]["ldpcIteration"] for r in ok)
    noldpc = sum(r["ldpc"]["ame_check_hw_NoLDPC"] for r in ok)
    nomsg = sum(r["ldpc"]["No ldpc supported"] for r in ok)
    sysfs = [k for k in SYSFS if any(r["sysfs"][k]["show"] and r["sysfs"][k]["store"]
                                     for r in ok)]
    retry_lines = sum(r["retry_line"] for r in ok)
    bler_total = sum(r["tokens"]["bler"] + r["tokens"]["BLER"] for r in ok)
    ldpc_total = sum(r["tokens"]["ldpc"] + r["tokens"]["LDPC"] for r in ok)

    report = dict(
        meta=dict(stage="648A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage648a_ltu_ame_core_arq_retrans_and_fec_ldpc_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census of the ARQ/HARQ, BLER, LDPC and retry vocabularies; "
                         "defined-symbol lookup for the bler and ldpc families; retry-descriptor "
                         "log extraction; sysfs pair detection",
                  premise_corrections=[
                      "arq, harq, retrans and nack all return 0: no retransmission state machine "
                      "is named in these modules",
                      "the retransmission evidence that does exist is BLER telemetry plus a queue "
                      "retry descriptor, not an ARQ object",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     assumed_token_hits=assumed_hits,
                     arq_harq_absent=int(assumed_hits == 0),
                     bler_token_hits=bler_total,
                     bler_symbol_count=len(bler_syms),
                     bler_symbols=bler_syms[:10],
                     cpe_rx_tx_bler_pair=int(cpe_pair > 0),
                     each_bler_present=int(each_bler > 0),
                     coded_bler_present=int(cbler > 0),
                     ldpc_token_hits=ldpc_total,
                     ldpc_symbol_count=len(ldpc_syms),
                     ldpc_iteration_controls=ldpc_iter,
                     ldpc_capability_check=noldpc,
                     no_ldpc_message=nomsg,
                     ldpc_iteration_tunable=int(ldpc_iter > 0),
                     retry_descriptor_lines=retry_lines,
                     retry_descriptor_present=int(retry_lines > 0),
                     sysfs_pairs=sysfs,
                     sysfs_pair_count=len(sysfs),
                     arq_state_machine_recovered=0,
                     harq_combining_recovered=0,
                     fec_block_table_recovered=0),
        gaps=["arq, harq, retrans and nack do not exist as identifiers: the retransmission state "
              "machine is not a named object in these modules",
              "BLER is the retransmission evidence that exists, and it is per-CPE (cpeRxBler / "
              "cpeTxBler) with a coded variant (check_cbler_decode) and a per-MCS variant "
              "(autoMCS_get_each_bler)",
              "the LDPC iteration count is settable but the mapping from iterations to correction "
              "strength was not recovered",
              "the retry descriptor is a queue-level triple (tail, reIdx, retry), not a per-packet "
              "structure",
              "no HARQ soft-combining buffer or redundancy-version field was found",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[648A] modules={s['modules_ok']} arq_absent={s['arq_harq_absent']} "
          f"bler={s['bler_token_hits']}({s['bler_symbol_count']}sym) "
          f"cpe_pair={s['cpe_rx_tx_bler_pair']} ldpc={s['ldpc_token_hits']}"
          f"({s['ldpc_symbol_count']}sym) iter={s['ldpc_iteration_controls']} "
          f"retry_lines={s['retry_descriptor_lines']} sysfs={s['sysfs_pair_count']}")
    print(f"        bler_syms={bler_syms[:6]}")
    print(f"[648A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
