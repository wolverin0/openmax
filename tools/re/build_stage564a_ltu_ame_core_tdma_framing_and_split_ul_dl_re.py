#!/usr/bin/env python3
"""Stage 564A — LTU TDMA frame geometry, split TX/RX frequency and the UL/DL ratio.

The stage asks for three things in `ame_core.ko` and `eab_driver.ko`:

  * **TDMA frame duration**;
  * **split TX/RX frequency** synthesizer control;
  * **UL/DL duty ratio** scheduling symbols.

`eab_driver.ko` is **absent** (tenth confirmation). In the two modules that exist, all three are
present, but expressed as **runtime get/set pairs plus sysfs attributes**, not as constants:

**Frame geometry** — a matched accessor pair per quantity:

```
ame_bbp_get_frame_len        ame_bbp_set_frame_len
ame_bbp_get_duty_cycle       ame_bbp_set_duty_cycle
ame_core_get_bc_dl_symbols   ame_core_set_bc_dl_symbols
bbp_get_tx_sub_frame_length  bbp_get_rx_sub_frame_length
bbp_get_ul_subframe_length_forDFS
```

**UL symbol assignment** — a record-keeping subsystem, not a single counter:

```
ame_core_fill_ul_sym_asgmt_record   ame_core_dump_ul_sym_asgmt
ame_core_print_ul_sym_asgmt_record  ul_sym_asgmt_open
```

**Sysfs surface** in `ame_dev.ko`, every one a show/store pair:

```
duty_cycle           frame_len            bc_dl_symbols
frame_pulse_offset   obs_txgain
```

**Split TX/RX frequency** appears where the frame is described:

```
Replaced channel info, [%3d:%s] duty_cycle:%d framelen:%d, rx/tx freq: %d/%d
```

The `rx/tx freq: %d/%d` pair is the split: receive and transmit are programmed on **separate**
frequencies, which is what a split-band TDD link needs.

One trap to record: **`split` is not the split-frequency token.** Its single hit is
`c_string_smart_split`, a string helper. And **`tdma` does not appear at all**; the only `TDD` hit
is inside the mangled symbol `bbp_mrx_foe_TDDeRotCFO`.

`duty_ratio_values_recovered = 0`: no 75/25, 67/33 or 50/50 ratio exists as a literal (Stage 388A
already established that), and the ratio is derived from `dl_symbols` / `ul_symbols`.

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
       / "stage564a_ltu_ame_core_tdma_framing_and_split_ul_dl_re.json")

MODULES = {"ame_core.ko": LTU / "ame_core.ko", "ame_dev.ko": LTU / "ame_dev.ko"}

TOKENS = ["tdma", "TDMA", "tdd", "TDD", "frame_len", "frame_period", "duty_cycle",
          "dl_symbols", "ul_symbols", "gap0", "split", "sub_frame", "frame_pulse_offset"]
# the accessor pairs that make a quantity settable
PAIRS = {
    "frame_len": ("ame_bbp_get_frame_len", "ame_bbp_set_frame_len"),
    "duty_cycle": ("ame_bbp_get_duty_cycle", "ame_bbp_set_duty_cycle"),
    "bc_dl_symbols": ("ame_core_get_bc_dl_symbols", "ame_core_set_bc_dl_symbols"),
}
# the sysfs show/store pairs
SYSFS = ["duty_cycle", "frame_len", "bc_dl_symbols", "frame_pulse_offset"]
# the sub-frame length getters
SUBFRAME = ["bbp_get_tx_sub_frame_length", "bbp_get_rx_sub_frame_length",
            "bbp_get_ul_subframe_length_forDFS"]


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
            pairs={k: dict(get=b.count(g.encode()), set=b.count(s.encode()))
                   for k, (g, s) in PAIRS.items()},
            sysfs={k: dict(show=b.count((k + "_show").encode()),
                           store=b.count((k + "_store").encode())) for k in SYSFS},
            subframe={k: b.count(k.encode()) for k in SUBFRAME},
            frame_symbols=syms.matching(r"frame_len|duty|bc_dl_symbols|sub_frame", 20),
            uldl_symbols=syms.matching(r"dl_sym|ul_sym|sub_frame", 20),
            ratio_contexts=ctx(b, "duty_cycle:%d framelen", 1),
            split_context=ctx(b, "split", 2),
            tdd_context=ctx(b, "TDD", 2)))

    ok = [r for r in rows if r.get("status") == "ok"]
    all_names = sorted({n for r in ok for n in r["frame_symbols"] + r["uldl_symbols"]})
    pairs_ok = sorted({k for r in ok for k, v in r["pairs"].items()
                       if v["get"] and v["set"]})
    sysfs_ok = sorted({k for r in ok for k, v in r["sysfs"].items()
                       if v["show"] and v["store"]})
    subframe_ok = sorted({k for r in ok for k, v in r["subframe"].items() if v})
    freq_pair = any("rx/tx freq" in c for r in ok for c in r["ratio_contexts"])
    split_coinc = all("smart_split" in c for r in ok for c in r["split_context"]) \
        and any(r["split_context"] for r in ok)
    tdd_hits = sum(r["tokens"]["tdd"] + r["tokens"]["TDD"] for r in ok)
    tdma_hits = sum(r["tokens"]["tdma"] + r["tokens"]["TDMA"] for r in ok)

    report = dict(
        meta=dict(stage="564A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage564a_ltu_ame_core_tdma_framing_and_split_ul_dl_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census of the frame-geometry vocabulary; get/set accessor pair "
                         "detection; sysfs show/store pair detection; context classification of "
                         "the split and TDD tokens",
                  premise_corrections=[
                      "eab_driver.ko is absent, so ame_core.ko and ame_dev.ko are the only "
                      "readable targets",
                      "`split` is not the split-frequency token: its hit is c_string_smart_split; "
                      "the split frequency appears as the rx/tx freq pair in the frame log",
                  ],
                  radio_safety="static only"),
        absence=dict(eab_driver=eab),
        modules=rows,
        summary=dict(eab_driver_present=eab > 0,
                     modules_ok=len(ok),
                     frame_symbol_count=len(all_names),
                     get_set_pairs=pairs_ok,
                     get_set_pair_count=len(pairs_ok),
                     sysfs_knobs=sysfs_ok,
                     sysfs_knob_count=len(sysfs_ok),
                     subframe_getters=subframe_ok,
                     subframe_getter_count=len(subframe_ok),
                     rx_tx_freq_pair=int(freq_pair),
                     split_is_coincidence=int(split_coinc),
                     tdma_literal_hits=tdma_hits,
                     tdd_literal_hits=tdd_hits,
                     duty_ratio_values_recovered=0,
                     ul_symbol_schedule_decoded=0,
                     synthesizer_programming_recovered=0),
        gaps=["eab_driver.ko is absent, so the stage's second module has no bytes",
              "tdma does not exist as a token; the single TDD hit is inside the mangled symbol "
              "bbp_mrx_foe_TDDeRotCFO, not a frame control",
              "`split` is c_string_smart_split, a string helper: the split frequency is the "
              "rx/tx freq pair in the frame log, not this token",
              "no named ratio (75/25, 67/33, 50/50) exists; the duty ratio is derived at runtime "
              "from dl_symbols and ul_symbols, and that derivation was not decoded",
              "the UL symbol assignment is a record subsystem (fill/dump/print), not a scheduler; "
              "the allocation rule was not recovered",
              "the synthesizer programming for the rx/tx frequency split was not located; only the "
              "log line that prints the pair was found",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[564A] eab={s['eab_driver_present']} modules={s['modules_ok']} "
          f"frame_syms={s['frame_symbol_count']} pairs={s['get_set_pairs']} "
          f"sysfs={s['sysfs_knobs']} subframe={s['subframe_getter_count']} "
          f"rx_tx_freq={s['rx_tx_freq_pair']} split_coinc={s['split_is_coincidence']} "
          f"tdma={s['tdma_literal_hits']} tdd={s['tdd_literal_hits']}")
    print(f"        subframe={subframe_ok}")
    print(f"[564A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
