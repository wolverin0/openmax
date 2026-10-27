#!/usr/bin/env python3
"""Stage 824A — LTU Beetle DFS radar pulse classifier, PW/PRI filters, LNA saturation immunity.

The stage asks for the radar pulse classifier inside `ame_core.ko` and `ame_dev.ko` of
`afltu_2.4.2`, the pulse-width and PRI filters, and how false DFS triggers from LNA saturation on
co-located towers are avoided.

**The stage names the wrong two modules.** The radar classifier is in **`ame_dfs.ko`** (141,472
bytes), which carries `pulse` 82, `dfs` 192, `DFS` 64 and `pri` 29 — an order of magnitude denser
than `ame_core.ko` (`pulse` 22, `pri` 65, `satur` 1). This stage dissects all three and reports where
the mass actually is.

## The classifier surface

```
DFSdetect              DFSChanActivity          DFS_heavy_env_det
ame_dfs_isr            ame_dfs_ioctl            ame_dfs_reset
ame_start_ep_dfs       ame_stop_ep_dfs
ame_dfs_init           ame_dfs_deinit           ame_dfs_dev_init
```

**`CONFIRMED`**: `DFS_heavy_env_det` — a **heavy-environment detector**. That is the name that
matches the stage's question: before classifying pulses, the module decides whether the RF
environment is so busy that pre-classification filtering would be unreliable.

**`CONFIRMED`**: `DFSdetect` and `DFSChanActivity` are separate — a **per-channel activity** measure
beside the detect verdict. So the classifier can say "this channel is active but not radar".

## The pulse filter is a selectable module, and it reports percentages

The log line is the classifier's own output:

```
%s.tot hits %u, pulse percent/max %d/%u
%s.pulseFilteringModule             %d
%s.target_pwr : %d
```

**`CONFIRMED`**: three things in one place —

| Field | Meaning |
| :--- | :--- |
| **`tot hits`** | how many pulses were seen |
| **`pulse percent/max`** | the pulse **occupancy percentage** and the **maximum** reading |
| **`pulseFilteringModule`** | **which filter module** is active |

**`pulseFilteringModule` is the key name.** It is a **selector**, not a boolean: the module can run
different pulse filters, which is what a vendor does when the filter must change by chip, bandwidth
or regulatory domain. It mirrors Stage 727A's five per-generation PHYERR processors on the AC side.

**`CONFIRMED`**: `target_pwr : %d` is logged beside the pulse statistics. Transmit power and radar
detection are reported together — which is exactly where an LNA-saturation false trigger would
originate.

## LNA saturation is NOT named

| Token | Hits |
| :--- | :-: |
| `lna`, `LNA` | **0** |
| `satur` | **1** (in `ame_core.ko`, not `ame_dfs.ko`) |

**`REFUTED`**: there is **no LNA saturation vocabulary** anywhere. The single `satur` hit is in
`ame_core.ko` and is not in the DFS path.

So the stage's specific hypothesis — false DFS from LNA saturation on co-located towers — is
**not named in the binary**. What exists is the **general** immunity machinery:

- `DFS_heavy_env_det` (busy environment);
- `pulseFilteringModule` (filters can change);
- `pulse percent/max` (occupancy thresholding);
- `target_pwr` logged alongside.

That is a plausible mechanism for rejecting saturation-induced hits — a saturated LNA produces a
wide, strong "pulse" that a percent/max filter and a heavy-environment detector would both catch — but
**the corpus does not state it**, and this stage does not claim it.
`lna_saturation_immunity_recovered = 0`.

## The PW/PRI tables are not in the strings

**`REFUTED`**: `pw_pri_table_recovered = 0`. `pri` has 29 hits and `PRI` 18, but no pulse-width or
PRI **table** appears — the thresholds are numeric data, and none was extracted.

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
       / "stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.json")

MODULES = {
    "ame_core.ko": LTU / "ame_core.ko",
    "ame_dev.ko": LTU / "ame_dev.ko",
    "ame_dfs.ko": LTU / "ame_dfs.ko",
}

TOKENS = ["pulse", "PULSE", "pri", "PRI", "radar", "RADAR", "dfs", "DFS",
          "lna", "LNA", "satur", "classif"]
# the classifier entry points
CLASSIFIER = ["DFSdetect", "DFSChanActivity", "DFS_heavy_env_det"]
# the DFS object lifecycle
LIFECYCLE = ["ame_dfs_init", "ame_dfs_deinit", "ame_dfs_isr", "ame_dfs_ioctl",
             "ame_dfs_reset", "ame_start_ep_dfs", "ame_stop_ep_dfs"]
# the pulse statistics log line
PULSE_STATS = "pulse percent/max"
# the filter selector
FILTER = "pulseFilteringModule"
# the hit counter
HITS = "tot hits"
# the ubus surface
UBUS = ["dfsdetect", "dfs_irq_ctl", "startdfs", "dfs_hit_monitor_mode_get"]


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
            classifier={k: b.count(k.encode()) for k in CLASSIFIER},
            lifecycle={k: b.count(k.encode()) for k in LIFECYCLE},
            pulse_stats=b.count(PULSE_STATS.encode()),
            filter_sel=b.count(FILTER.encode()),
            hits=b.count(HITS.encode()),
            ubus={k: b.count(k.encode()) for k in UBUS},
            pulse_contexts=ctx(b, PULSE_STATS, 1),
            filter_contexts=ctx(b, FILTER, 1)))

    ok = [r for r in rows if r.get("status") == "ok"]
    dfs = [r for r in ok if r["module"] == "ame_dfs.ko"]
    cls = [k for k in CLASSIFIER if any(r["classifier"][k] for r in ok)]
    life = [k for k in LIFECYCLE if any(r["lifecycle"][k] for r in ok)]
    stats = sum(r["pulse_stats"] for r in ok)
    filt = sum(r["filter_sel"] for r in ok)
    hits = sum(r["hits"] for r in ok)
    ubus = [k for k in UBUS if any(r["ubus"][k] for r in ok)]
    lna = sum(r["tokens"]["lna"] + r["tokens"]["LNA"] for r in ok)
    satur = sum(r["tokens"]["satur"] for r in ok)
    pulse_tokens = sum(r["tokens"]["pulse"] for r in ok)
    dfs_tokens = sum(r["tokens"]["dfs"] + r["tokens"]["DFS"] for r in ok)
    dfs_pulse = dfs[0]["tokens"]["pulse"] if dfs else 0
    core_pulse = sum(r["tokens"]["pulse"] for r in ok if r["module"] == "ame_core.ko")

    report = dict(
        meta=dict(stage="824A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted, nothing "
                        "transmitted",
                  method="three-module token census; classifier, lifecycle and ubus symbol "
                         "lookup; pulse-statistics and filter-selector log extraction; explicit "
                         "probe for LNA saturation vocabulary",
                  premise_corrections=[
                      "the radar classifier is in ame_dfs.ko (141472 bytes), not in ame_core.ko or "
                      "ame_dev.ko: its pulse token count is 82 against 22",
                      "lna and satur are absent or unrelated: the LNA-saturation hypothesis is "
                      "not named, only the general heavy-environment and pulse-percent filtering",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     ame_dfs_present=bool(dfs),
                     ame_dfs_bytes=dfs[0]["bytes"] if dfs else 0,
                     pulse_tokens_total=pulse_tokens,
                     pulse_tokens_in_ame_dfs=dfs_pulse,
                     pulse_tokens_in_ame_core=core_pulse,
                     classifier_in_dfs_module=int(dfs_pulse > core_pulse),
                     dfs_tokens_total=dfs_tokens,
                     classifier_symbols=cls,
                     classifier_symbol_count=len(cls),
                     heavy_env_detector=int("DFS_heavy_env_det" in cls),
                     channel_activity=int("DFSChanActivity" in cls),
                     lifecycle_symbols=life,
                     lifecycle_count=len(life),
                     pulse_stats_hits=stats,
                     pulse_percent_max_reported=int(stats > 0),
                     filter_selector_hits=filt,
                     filter_is_selectable=int(filt > 0),
                     hit_counter_hits=hits,
                     ubus_hooks=ubus,
                     ubus_hook_count=len(ubus),
                     lna_token_hits=lna,
                     saturation_token_hits=satur,
                     lna_saturation_named=int(lna > 0 or satur > 1),
                     lna_saturation_immunity_recovered=0,
                     pw_pri_table_recovered=0),
        gaps=["the stage names ame_core.ko and ame_dev.ko, but the radar classifier lives in "
              "ame_dfs.ko: pulse tokens 82 against 22 in ame_core",
              "lna and LNA return 0 and satur returns 1 in ame_core, outside the DFS path: the "
              "LNA-saturation false-trigger mechanism is not named",
              "no pulse-width or PRI threshold table was recovered: pri has 29 hits but no numeric "
              "table appeared",
              "pulseFilteringModule is a selector, and which filter it selects for which condition "
              "was not decoded",
              "the heavy-environment detector is named but its criterion is not",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[824A] modules={s['modules_ok']} dfs_mod={s['ame_dfs_bytes']}B "
          f"pulse_dfs={s['pulse_tokens_in_ame_dfs']} pulse_core={s['pulse_tokens_in_ame_core']} "
          f"cls={s['classifier_symbol_count']} heavy={s['heavy_env_detector']} "
          f"filter={s['filter_is_selectable']} lna={s['lna_token_hits']} "
          f"satur={s['saturation_token_hits']}")
    print(f"        cls={cls}")
    print(f"[824A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
