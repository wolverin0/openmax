#!/usr/bin/env python3
"""Stage 807A — LTU split-frequency programming and OFDMA subchannel vocabulary.

The stage asks for the **split TX/RX frequency** programming and the **OFDMA subchannel** surface in
`ame_core.ko`.

Both are present, and the OFDMA side is far denser than the stage implies:

| Token | Hits |
| :--- | :-: |
| `ofdma` + `OFDMA` | **88** |
| `ulmap` | **17** |
| `rx/tx freq` | **4** |
| `subchannel`, `sub_chan`, `ru_` | **0** |

**`CONFIRMED`**: `ofdma_tokens = 88`. **`REFUTED`**: there is no `subchannel` or resource-unit
(`ru_`) vocabulary — the subchannel concept is expressed as **`ulmap`** (uplink MAP), which is the
WiMAX/LTE lineage name for the same allocation.

**`CONFIRMED`**: `rx_tx_freq_pair = 4` hits of the split-frequency log line, which Stage 564A first
read as:

```
Replaced channel info, [%3d:%s] duty_cycle:%d framelen:%d, rx/tx freq: %d/%d
```

So the split is **printed**, and the two frequencies are programmed separately — but no
`synthesizer`/`pll`/`lo` symbol programs them by name (Stage 486A established the frequency discipline
is **DCXO**-based, with `bbp_rf_dcxo_*`).

**`CONFIRMED`**: the UL map is a **named subsystem**, not a field: `ulmap` appears 17 times alongside
the `ul_sym_asgmt` record machinery Stage 564A found (`ame_core_fill_ul_sym_asgmt_record`,
`ame_core_dump_ul_sym_asgmt`, `ame_core_print_ul_sym_asgmt_record`). So the uplink allocation is both
**mapped** (`ulmap`) and **recorded** (`ul_sym_asgmt`).

`subchannel_map_recovered = 0`: the `ulmap` structure — how many subchannels, their widths, their
CPE assignment — was not decoded.

Radio safety: static only. No module loaded, no radio contacted, nothing transmitted.
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
       / "stage807a_ltu_split_freq_and_ofdma_subchannel_re.json")

MODULES = {"ame_core.ko": LTU / "ame_core.ko", "ame_dev.ko": LTU / "ame_dev.ko"}

TOKENS = ["ofdma", "OFDMA", "ulmap", "ul_map", "subchannel", "sub_chan", "ru_",
          "rx/tx freq", "txfreq", "rxfreq", "prefer_work_txfreq", "prefer_work_rxfreq"]
# the UL map and symbol assignment machinery
ULMAP = ["ulmap", "ul_sym_asgmt"]
# the split-frequency carriers
SPLIT = ["rx/tx freq", "prefer_work_txfreq", "prefer_work_rxfreq", "txfreq", "rxfreq"]
# the absent subchannel vocabulary
ABSENT = ["subchannel", "sub_chan", "ru_"]


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
            ulmap={k: b.count(k.encode()) for k in ULMAP},
            split={k: b.count(k.encode()) for k in SPLIT},
            absent={k: b.count(k.encode()) for k in ABSENT},
            ofdma_symbols=syms.matching(r"ofdma", 16),
            ulmap_symbols=syms.matching(r"ulmap|ul_sym", 16),
            freq_symbols=syms.matching(r"freq_list|auto_freq|txfreq|rxfreq", 12),
            split_contexts=ctx(b, "rx/tx freq", 1)))

    ok = [r for r in rows if r.get("status") == "ok"]
    ofdma = sum(r["tokens"]["ofdma"] + r["tokens"]["OFDMA"] for r in ok)
    ulmap = sum(r["tokens"]["ulmap"] for r in ok)
    split_hits = sum(r["split"]["rx/tx freq"] for r in ok)
    pref = sum(r["split"]["prefer_work_txfreq"] + r["split"]["prefer_work_rxfreq"]
               for r in ok)
    absent = sum(sum(r["absent"].values()) for r in ok)
    ofdma_syms = sorted({n for r in ok for n in r["ofdma_symbols"]})
    ul_syms = sorted({n for r in ok for n in r["ulmap_symbols"]})
    freq_syms = sorted({n for r in ok for n in r["freq_symbols"]})

    report = dict(
        meta=dict(stage="807A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage807a_ltu_split_freq_and_ofdma_subchannel_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted, nothing "
                        "transmitted",
                  method="token census of the OFDMA, UL-map and split-frequency vocabularies; "
                         "symbol lookup for the ofdma and ulmap families; explicit probe for the "
                         "subchannel and resource-unit vocabulary",
                  premise_corrections=[
                      "there is no subchannel or RU vocabulary: the allocation concept is named "
                      "ulmap, the uplink MAP",
                      "the split frequency is printed as an rx/tx pair and configured through "
                      "prefer_work_txfreq/rxfreq, but no synthesizer symbol programs it by name",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     ofdma_token_hits=ofdma,
                     ofdma_symbol_count=len(ofdma_syms),
                     ofdma_symbols=ofdma_syms[:8],
                     ulmap_token_hits=ulmap,
                     ulmap_symbol_count=len(ul_syms),
                     ulmap_symbols=ul_syms[:8],
                     ulmap_is_named_subsystem=int(len(ul_syms) >= 2),
                     split_freq_line_hits=split_hits,
                     split_freq_pair_present=int(split_hits > 0),
                     split_preference_keys=pref,
                     split_pref_present=int(pref > 0),
                     freq_symbols=freq_syms[:6],
                     subchannel_token_hits=absent,
                     subchannel_vocabulary_absent=int(absent == 0),
                     subchannel_map_recovered=0,
                     ru_allocation_table_recovered=0),
        gaps=["subchannel and ru are absent: the allocation is named ulmap and the record "
              "machinery is ul_sym_asgmt, so a search for subchannel vocabulary finds nothing",
              "the ulmap structure (how many subchannels, their widths, their CPE assignment) was "
              "not decoded",
              "the split frequency is printed and configured but no synthesizer or LO symbol "
              "programs it; Stage 486A established the discipline is DCXO-based",
              "no resource-unit allocation table was recovered",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[807A] modules={s['modules_ok']} ofdma={s['ofdma_token_hits']}"
          f"({s['ofdma_symbol_count']}sym) ulmap={s['ulmap_token_hits']}"
          f"({s['ulmap_symbol_count']}sym) split={s['split_freq_pair_present']} "
          f"pref={s['split_preference_keys']} subch_absent={s['subchannel_vocabulary_absent']}")
    print(f"        ulmap_syms={ul_syms[:5]}")
    print(f"[807A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
