#!/usr/bin/env python3
"""Stage 590A — LTU Listen-Before-Talk, interference detection and auto-frequency hooks.

The stage names three things in `ame_core.ko` and `ame_dev.ko`:

  * **Listen-Before-Talk (LBT)**;
  * **interference mitigation**;
  * **spectral scan / auto-frequency** hooks.

Two are present in full and one is a naming correction.

**LBT is a complete API with configurable windows**, not a flag:

```
ame_core_lbt_init        ame_core_lbt_enable      ame_core_lbt_is_enable
ame_core_lbt_set_cfg     ame_core_lbt_get_cfg     ame_core_is_lbt_required
ame_core_lbt_cfg_listen_window    ame_core_lbt_cfg_pause_txframe
ame_core_lbt_cfg_threshold        ame_core_lbt_cfg_reset
ame_core_lbt_incr_detect_cnt      ame_core_lbt_get_detect_cnt
ame_bbp_rt_lbt           bbp_mrx_printLBT         bbp_mrx_setLBT
```

Three of those deserve emphasis:

  * **`_cfg_listen_window`** — LBT listens for a *window*, so the deferral decision is
    time-bounded rather than instantaneous;
  * **`_cfg_pause_txframe`** — LBT can **pause the TX frame**, which means it is integrated with
    the TDD frame scheduler of Stage 564A, not layered above it;
  * **`_incr_detect_cnt` / `_get_detect_cnt`** — detections are **counted**, so an operator can see
    whether LBT is firing rather than guessing.

**Interference detection** is its own subsystem:

```
ame_core_interference_det_init      ame_core_interference_det_deinit
ame_core_get_rf_interference_avg    ame_core_get_rf_interference_curr
ame_rf_interference_det_fn
```

with an RX-power trigger visible in the log string `RX_POWER_HIGH_INTERF_S…`.

**"Mitigation" is the word that is not there.** `mitigat` has **0 hits** in either module. The
mechanism the stage calls interference mitigation is expressed as **detection plus LBT plus
auto-frequency**, and this stage reports it under those names rather than inventing a mitigation
module.

**Auto-frequency** is a sysfs configuration block in `ame_dev.ko`:

```
prefer_work_txfreq   prefer_work_rxfreq
freq_list_enabled    auto_freq_list      auto_freq_mode      smart_scan
reg_obey
```

plus `ame_freq_list` in the core, and seven LBT sysfs pairs:

```
lbt_cfg_show        lbt_cfg_window_store     lbt_cfg_threshold_store
lbt_cfg_pauselen_store   lbt_detects_show/store
lbt_enable_show/store    lbt_reset_show/store
```

`lbt_threshold_recovered = 0` and `auto_channel_policy_recovered = 0`: the knobs are named and
writable, the policy behind them is not in the readable corpus.

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
LTU = (REPO_ROOT / "artifacts/firmware_re_xc_ltu/ltu_extracted/afltu_2.4.2"
       / "rootfs_extracted/lib/modules/3.14.65")
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage590a_ltu_ame_core_interference_mitigation_and_auto_channel_re.json")

MODULES = {"ame_core.ko": LTU / "ame_core.ko", "ame_dev.ko": LTU / "ame_dev.ko"}

TOKENS = ["lbt", "LBT", "interference", "mitigat", "freq_list", "auto_freq",
          "smart_scan", "spectral", "noise", "dfs"]
# the LBT control surface
LBT_API = ["lbt_init", "lbt_enable", "lbt_is_enable", "lbt_set_cfg", "lbt_get_cfg",
           "is_lbt_required"]
# the four configurable LBT parameters
LBT_CFG = ["lbt_cfg_listen_window", "lbt_cfg_pause_txframe", "lbt_cfg_threshold",
           "lbt_cfg_reset"]
# the detection counter
LBT_COUNTER = ["lbt_incr_detect_cnt", "lbt_get_detect_cnt"]
# interference detection
INTERF = ["interference_det_init", "interference_det_deinit",
          "get_rf_interference_avg", "get_rf_interference_curr"]
# sysfs LBT pairs
SYSFS = ["lbt_cfg", "lbt_detects", "lbt_enable", "lbt_reset"]
# auto-channel configuration keys
AUTO = ["freq_list_enabled", "auto_freq_list", "auto_freq_mode", "smart_scan",
        "prefer_work_txfreq", "prefer_work_rxfreq", "reg_obey"]


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
            lbt_api={k: b.count(k.encode()) for k in LBT_API},
            lbt_cfg={k: b.count(k.encode()) for k in LBT_CFG},
            lbt_counter={k: b.count(k.encode()) for k in LBT_COUNTER},
            interf={k: b.count(k.encode()) for k in INTERF},
            sysfs={k: dict(show=b.count((k + "_show").encode()),
                           store=b.count((k + "_store").encode())) for k in SYSFS},
            auto={k: b.count(k.encode()) for k in AUTO},
            lbt_cfg_stores={s: b.count(("lbt_cfg_" + s + "_store").encode())
                            for s in ("window", "threshold", "pauselen")},
            lbt_symbols=syms.matching(r"lbt", 24),
            interf_symbols=syms.matching(r"interference", 12),
            freq_symbols=syms.matching(r"freq_list|auto_freq|smart_scan", 12),
            interf_contexts=ctx(b, "INTERF", 2)))

    ok = [r for r in rows if r.get("status") == "ok"]
    lbt_syms = sorted({n for r in ok for n in r["lbt_symbols"]})
    interf_syms = sorted({n for r in ok for n in r["interf_symbols"]})
    freq_syms = sorted({n for r in ok for n in r["freq_symbols"]})
    api = [k for k in LBT_API if any(r["lbt_api"][k] for r in ok)]
    cfg = [k for k in LBT_CFG if any(r["lbt_cfg"][k] for r in ok)]
    counters = [k for k in LBT_COUNTER if any(r["lbt_counter"][k] for r in ok)]
    interf = [k for k in INTERF if any(r["interf"][k] for r in ok)]
    sysfs = [k for k in SYSFS if any(r["sysfs"][k]["show"] and r["sysfs"][k]["store"]
                                     for r in ok)]
    auto = [k for k in AUTO if any(r["auto"][k] for r in ok)]
    mitigat = sum(r["tokens"]["mitigat"] for r in ok)

    report = dict(
        meta=dict(stage="590A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage590a_ltu_ame_core_interference_mitigation_and_auto_"
                       "channel_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted, nothing "
                        "transmitted",
                  method="token census of the LBT, interference and auto-frequency "
                         "vocabularies; defined-symbol lookup for the LBT API, the four config "
                         "parameters, the detection counters and the interference detectors; "
                         "sysfs show/store pair detection",
                  premise_corrections=[
                      "`mitigat` has 0 hits in either module: the mechanism is detection plus "
                      "LBT plus auto-frequency, and is reported under those names",
                      "LBT is integrated with the frame scheduler through lbt_cfg_pause_txframe, "
                      "not layered above it",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     lbt_symbol_count=len(lbt_syms),
                     lbt_symbols=lbt_syms[:12],
                     lbt_api_controls=api,
                     lbt_api_count=len(api),
                     lbt_cfg_params=cfg,
                     lbt_cfg_count=len(cfg),
                     lbt_counters=counters,
                     lbt_counter_count=len(counters),
                     lbt_has_listen_window=int("lbt_cfg_listen_window" in cfg),
                     lbt_has_pause_txframe=int("lbt_cfg_pause_txframe" in cfg),
                     lbt_has_detect_counter=int(len(counters) == 2),
                     interference_symbols=interf_syms,
                     interference_controls=interf,
                     interference_detection_named=int(len(interf) >= 2),
                     sysfs_lbt_pairs=sysfs,
                     sysfs_pair_count=len(sysfs),
                     lbt_cfg_store_variants=sorted({s for r in ok
                                                    for s, v in r["lbt_cfg_stores"].items()
                                                    if v}),
                     lbt_cfg_has_split_store=int(any(v for r in ok
                                                     for v in r["lbt_cfg_stores"].values())),
                     auto_channel_keys=auto,
                     auto_channel_key_count=len(auto),
                     auto_channel_hooks_named=int(len(auto) >= 4),
                     freq_list_symbols=freq_syms,
                     mitigation_word_hits=mitigat,
                     mitigation_word_absent=int(mitigat == 0),
                     lbt_threshold_recovered=0,
                     auto_channel_policy_recovered=0,
                     spectral_scan_hook_recovered=0),
        gaps=["`mitigat` does not exist as a token: the stage's interference mitigation is "
              "implemented as detection (interference_det_*) plus LBT plus auto-frequency",
              "the LBT threshold, listen-window and pause-frame values are runtime data behind "
              "sysfs; no defaults were recovered",
              "the interference detectors expose avg and curr RF interference but the decision "
              "that consumes them was not decoded",
              "auto_freq_mode and smart_scan are configuration keys; the selection policy behind "
              "them was not recovered",
              "no spectral-scan hook appears by that name in these two modules; Stage 327A found "
              "the spectral surface in ath_spectral.ko on the AC side",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[590A] modules={s['modules_ok']} lbt_syms={s['lbt_symbol_count']} "
          f"api={s['lbt_api_count']} cfg={s['lbt_cfg_count']} "
          f"counters={s['lbt_counter_count']} interf={s['interference_detection_named']} "
          f"sysfs={s['sysfs_pair_count']} auto={s['auto_channel_key_count']} "
          f"mitigat={s['mitigation_word_hits']}")
    print(f"        cfg={cfg}")
    print(f"        auto={auto}")
    print(f"[590A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
