#!/usr/bin/env python3
"""Stage 563A — PAPRD, TPC/CTL target power and thermal calibration.

The stage asks for five things across `ath_hal.ko`, `ath_dev.ko` and `umac.ko` on WA, XC and XW:

  * **PAPRD** (PA pre-distortion);
  * **open-loop** and **closed-loop** TX power control;
  * **CTL / target power** tables;
  * **thermal** TPC calibration.

Four of the five are present by name. One is not, and the distinction matters:

**`olpc` and `clpc` do not exist as tokens anywhere (0 hits).** The open/closed loop distinction in
this stack is carried by **`tpc`** (transmit power control, with `enable_tpc`) and **`ctl`**
(closed-loop target, with `get_ctl_chan_nf` and `update_loc_ctl_reg`). A grep for `olpc` returns
nothing and would be misread as "open-loop control does not exist".

PAPRD is a **production pipeline**, not a flag. In WA/XC `ath_hal.ko`:

```
ar9300_paprd_create_curve        ar9300_paprd_init_table
ar9300_populate_paprd_single_table   ar9300_swizzle_paprd_entries
ar9300_paprd_setup_gain_table    ar9300_set_paprd_tx_desc
ar9300_paprd_is_done             ar9300_paprd_dec_tx_pwr
ar9300_enable_paprd              ar9300_is_skip_paprd_by_greentx
ar9300_paprd_thermal_send
```

and the device side drives it:

```
ath_paprd_cal      ath_paprd_send      ath_sendpaprd_single
ath_paprd_set_enable / _get_enable     ath_paprd_setrate / _getrate
ath_apply_paprd_table
ath_tx_paprd_init / _complete / _draintxq / _cleanup
```

That is a **training loop with a transmit path**: `set_tx_desc` sends a calibration frame,
`is_done` polls for completion, `create_curve` builds the correction, `apply_paprd_table` installs
it, and the `_tx_paprd_*` family manages the queue around it.

Three interactions worth naming:

  * **`ar9300_paprd_thermal_send`** — PAPRD and thermal calibration share a path. On this silicon
    they are not independent.
  * **`ar9300_is_skip_paprd_by_greentx`** — **GreenTX can skip PAPRD entirely.** A unit with
    GreenTX active may run with **no** pre-distortion correction, which is an EVM question.
  * **`ar9300_set_target_power_from_eeprom`** — the target power is **per-unit EEPROM data**, not a
    constant, so target power differs board to board.

`paprd_table_values_recovered = 0` and `tpc_tables_recovered = 0`: the pipeline is named, the
coefficients are not in the readable corpus.

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
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
XW = REPO_ROOT / "artifacts" / "firmware_re_xw_m5" / "xw_636_rootfs" / "lib" / "modules" / "2.6.32.71"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage563a_qca988x_paprd_and_olpc_tx_power_control_re.json")

MODULES = {
    "WA:ath_hal.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "XC:ath_hal.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "XW:ath_hal.ko": XW / "ath_hal.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
}

TOKENS = ["paprd", "PAPRD", "olpc", "OLPC", "clpc", "CLPC", "tpc", "TPC",
          "ctl_", "CTL_", "target_power", "thermal", "greentx",
          "target_power_from_eeprom", "txctl_cap", "get_ctl_by_country"]
# the ordered PAPRD pipeline the stage describes
PIPELINE = ["create_curve", "init_table", "populate_paprd", "swizzle",
            "setup_gain_table", "set_paprd_tx_desc", "is_done"]
# the loop-control vocabulary that actually exists
LOOP = ["enable_tpc", "get_tpc_tables", "get_ctl_chan_nf", "update_loc_ctl_reg",
        "get_rate_tpc", "get_ctl_by_country"]
# the loop names the stage assumes
ASSUMED = ["olpc", "clpc", "open_loop", "closed_loop"]


def ctx(b: bytes, tok: str, n: int = 2, w: int = 68) -> list[str]:
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
            tokens={t: b.count(t.encode()) for t in TOKENS},
            loop={k: b.count(k.encode()) for k in LOOP},
            assumed={k: b.count(k.encode()) for k in ASSUMED},
            paprd_symbols=syms.matching(r"paprd", 30),
            tpc_symbols=syms.matching(r"tpc", 16),
            ctl_symbols=syms.matching(r"ctl", 16),
            thermal_symbols=syms.matching(r"thermal", 8),
            greentx_symbols=syms.matching(r"greentx", 6)))

    ok = [r for r in rows if r.get("status") == "ok"]
    paprd = sorted({n for r in ok for n in r["paprd_symbols"]})
    tpc = sorted({n for r in ok for n in r["tpc_symbols"]})
    ctl = sorted({n for r in ok for n in r["ctl_symbols"]})
    therm = sorted({n for r in ok for n in r["thermal_symbols"]})
    green = sorted({n for r in ok for n in r["greentx_symbols"]})
    stages = [s for s in PIPELINE if any(s in n for n in paprd)]
    loop_found = sorted({k for r in ok for k, v in r["loop"].items() if v})
    assumed_hits = sum(sum(r["assumed"].values()) for r in ok)

    report = dict(
        meta=dict(stage="563A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage563a_qca988x_paprd_and_olpc_tx_power_control_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted, nothing "
                        "transmitted",
                  method="token census across seven modules on three lines; defined-symbol "
                         "lookup for the PAPRD pipeline stages, the TPC/CTL loop controls and the "
                         "thermal/greentx interactions",
                  premise_corrections=[
                      "olpc, clpc, open_loop and closed_loop do not exist as tokens; the loop "
                      "distinction is carried by tpc (enable_tpc) and ctl (ctl_chan_nf)",
                      "the PAPRD pipeline is split between ath_hal.ko (curve and table) and "
                      "ath_dev.ko (transmit, completion, queue management)",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     paprd_symbol_count=len(paprd),
                     paprd_symbols=paprd,
                     paprd_pipeline_stages=stages,
                     paprd_pipeline_complete_of_7=len(stages),
                     paprd_pipeline_named=int(len(stages) >= 5),
                     paprd_has_transmit_path=int(any("set_paprd_tx_desc" in n for n in paprd)),
                     paprd_dev_side=int(any(n.startswith("ath_paprd") or "paprd" in n
                                            and "ath_" in n for n in paprd)),
                     thermal_link=int(any("thermal" in n for n in paprd + therm)),
                     green_tx_skips_paprd=int(any("greentx" in n for n in paprd + green)),
                     target_power_from_eeprom=int(any(
                         r["tokens"]["target_power_from_eeprom"] for r in ok)),
                     tpc_symbol_count=len(tpc),
                     tpc_symbols=tpc[:10],
                     ctl_symbol_count=len(ctl),
                     ctl_symbols=ctl[:10],
                     loop_controls_present=loop_found,
                     loop_control_count=len(loop_found),
                     assumed_loop_token_hits=assumed_hits,
                     olpc_clpc_literals_absent=int(assumed_hits == 0),
                     ctl_by_country=int(any(r["tokens"]["get_ctl_by_country"] for r in ok)),
                     txctl_cap=int(any(r["tokens"]["txctl_cap"] for r in ok)),
                     paprd_table_values_recovered=0,
                     tpc_tables_recovered=0,
                     thermal_curve_recovered=0),
        gaps=["olpc and clpc do not exist as tokens: the open/closed-loop distinction is tpc and "
              "ctl, so a grep for the stage's names returns zero and must not be read as absence "
              "of the mechanism",
              "the PAPRD calibration curve and the per-rate correction table are runtime "
              "artefacts built by create_curve during a training transmit; no coefficients are in "
              "the module",
              "the TPC tables are per-rate and per-country (get_rate_tpc, ctl_by_country) and were "
              "not extracted",
              "target power comes from EEPROM (set_target_power_from_eeprom), so it is per-unit "
              "calibration data",
              "the thermal link is named (paprd_thermal_send) but the compensation curve was not "
              "recovered",
              "GreenTX can skip PAPRD entirely (is_skip_paprd_by_greentx); the condition was not "
              "decoded",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[563A] modules={s['modules_ok']} paprd={s['paprd_symbol_count']} "
          f"pipeline={s['paprd_pipeline_complete_of_7']}/7 tpc={s['tpc_symbol_count']} "
          f"ctl={s['ctl_symbol_count']} thermal={s['thermal_link']} "
          f"green_skip={s['green_tx_skips_paprd']} olpc_lit={s['assumed_loop_token_hits']}")
    print(f"        stages={stages}")
    print(f"        loop={loop_found}")
    print(f"[563A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
