#!/usr/bin/env python3
"""Stage 727A — spectral-scan FFT PHY errors and DFS radar PHY errors.

The stage asks for `ATH10K_PHYERR_SPECTRAL`, `ATH10K_PHYERR_RADAR` and
`WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID` across ath10k, `umac.ko` and `ath_dev.ko`.

`ath10k_core.ko` is **absent** (0 files, seventh confirmation), so the `ATH10K_PHYERR_*` enum
constants are unavailable — they are ath10k macros in any case. But the **vendor PHYERR dispatch is
fully named across four modules**, and it is more specific than the stage assumes.

## The handler lifecycle

```
ol_ath_phyerr_attach    ol_ath_phyerr_detach
ol_ath_phyerr_enable    ol_ath_phyerr_disable
```

**`CONFIRMED`**: `phyerr_lifecycle = 4`. The PHY-error path is an **object with attach/detach and
enable/disable**, not an inline switch. It can be turned off without tearing down the interface —
which is what a driver does when DFS is disabled.

## The spectral control surface

```
init_spectral_capability         ol_if_spectral_configure_params
ol_if_ic_start_spectral_scan     ol_if_ic_stop_spectral_scan
ol_if_is_spectral_active         ol_if_is_spectral_enabled
ol_if_spectral_enable            ol_if_spectral_detach
ol_if_spectral_get_capability    ol_if_spectral_get_current_channel
ol_if_spectral_get_chain_noise_floor    ol_if_spectral_get_ctl_noisefloor
```

**`CONFIRMED`**: `spectral_control_symbol_count = 12`, and `is_active` is **separate** from
`is_enabled` — enabled means configured, active means actually sampling. That distinction matters on
a bench: a scan can be enabled and still never start.

## The important finding: five PHYERR processors, one per chip generation

In `ath_dfs.ko`:

```
dfs_process_phyerr            dfs_process_phyerr_bb_tlv
dfs_process_phyerr_merlin     dfs_process_phyerr_owl
dfs_process_phyerr_sowl
```

**`CONFIRMED`**: `phyerr_processor_count = 5`, `per_chip_generations = 4` named variants.

`bb_tlv`, `merlin`, `owl` and `sowl` are **Atheros silicon generations**. The PHY-error payload
format differs between them, so the radar detector is **not one parser** — it is a family of parsers
selected by chip. That is why a radar finding on one generation does not transfer to another, and it
is the same lesson Stage 615A taught about TxBF and Stage 499A about bin detectors.

The dispatcher also carries:

```
dfs_init_radar_filters    dfs_process_radarevent
dfs_radar_enable          dfs_radar_disable        dfs_reset_radarq
```

## Regulatory radar tables are per domain

```
etsi_radartool_alow       fcc_radartool_alow
```

**`CONFIRMED`**: `regulatory_radar_tools = 2`. The radar tool's acceptance table is **per regulatory
domain** — ETSI and FCC have different pulse-shape tolerances, so the "allow" list differs by domain.

## Where spectral PHY errors are classified

The predicate `is_spectral_phyerr` lives in **`ath_spectral.ko`** (4 hits), not in `umac.ko` — the
first probe in this stage returned 0 for it in `umac.ko`, which is why the module sweep matters.

`WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID` and `..._ENABLE_CMDID` are present in `umac.ko` (Stage 451A
established them as **VDEV**-scoped, not PDEV).

`phyerr_code_table_recovered = 0`: the numeric PHY-error codes are an ath10k enum that does not exist
in the vendor stack, and no equivalent numeric table was located.

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
       / "stage727a_qca988x_spectral_scan_fft_and_radar_phyerr_re.json")

MODULES = {
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "WA:ath_spectral.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_spectral.ko",
    "XC:ath_spectral.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_spectral.ko",
    "WA:ath_dfs.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dfs.ko",
    "XC:ath_dfs.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dfs.ko",
}

TOKENS = ["PHYERR", "phyerr", "SPECTRAL", "spectral", "RADAR", "radar", "ATH10K"]
# the PHYERR handler lifecycle
LIFECYCLE = ["ol_ath_phyerr_attach", "ol_ath_phyerr_detach",
             "ol_ath_phyerr_enable", "ol_ath_phyerr_disable"]
# the per-chip-generation processors
PROCESSORS = ["dfs_process_phyerr", "dfs_process_phyerr_bb_tlv",
              "dfs_process_phyerr_merlin", "dfs_process_phyerr_owl",
              "dfs_process_phyerr_sowl"]
# the regulatory radar tools
REGULATORY = ["etsi_radartool_alow", "fcc_radartool_alow"]
# the spectral PHYERR predicate
PREDICATE = "is_spectral_phyerr"
# the VDEV-scoped spectral commands
WMI = ["WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID", "WMI_VDEV_SPECTRAL_SCAN_ENABLE_CMDID"]


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
            tokens={t: b.count(t.encode()) for t in TOKENS},
            lifecycle={k: b.count(k.encode()) for k in LIFECYCLE},
            processors={k: b.count(k.encode()) for k in PROCESSORS},
            regulatory={k: b.count(k.encode()) for k in REGULATORY},
            wmi={k: b.count(k.encode()) for k in WMI},
            predicate=b.count(PREDICATE.encode()),
            phyerr_symbols=syms.matching(r"phyerr", 16),
            spectral_symbols=syms.matching(r"spectral", 16),
            radar_symbols=syms.matching(r"radar", 16)))

    ok = [r for r in rows if r.get("status") == "ok"]
    life = [k for k in LIFECYCLE if any(r["lifecycle"][k] for r in ok)]
    procs = [k for k in PROCESSORS if any(r["processors"][k] for r in ok)]
    regs = [k for k in REGULATORY if any(r["regulatory"][k] for r in ok)]
    wmi = sorted({k for r in ok for k in r["wmi"] if r["wmi"][k]})
    pred_mods = [r["module"] for r in ok if r["predicate"]]
    phy_syms = sorted({n for r in ok for n in r["phyerr_symbols"]})
    spec_syms = sorted({n for r in ok for n in r["spectral_symbols"]})
    radar_syms = sorted({n for r in ok for n in r["radar_symbols"]})
    gens = [p.split("_")[-1] for p in procs if p != "dfs_process_phyerr"]

    report = dict(
        meta=dict(stage="727A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage727a_qca988x_spectral_scan_fft_and_radar_phyerr_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  message_method="token census across eight modules on two lines; PHYERR "
                                 "lifecycle, per-generation processor and regulatory tool "
                                 "extraction; spectral control surface enumeration",
                  premise_corrections=[
                      "ath10k_core.ko is absent, so ATH10K_PHYERR_SPECTRAL and ATH10K_PHYERR_RADAR "
                      "cannot be read; they are ath10k macros in any case",
                      "the PHYERR dispatch is not one parser: ath_dfs.ko carries five processors, "
                      "four of them named after Atheros silicon generations",
                  ],
                  radio_safety="static only"),
        ath10k_modules=ath10k,
        modules=rows,
        summary=dict(ath10k_core_present=ath10k > 0,
                     modules_ok=len(ok),
                     phyerr_lifecycle=life,
                     phyerr_lifecycle_count=len(life),
                     phyerr_handler_named=int(len(life) == 4),
                     phyerr_processor_count=len(procs),
                     phyerr_processors=procs,
                     chip_generations=gens,
                     chip_generation_count=len(gens),
                     per_generation_dispatch=int(len(gens) >= 3),
                     regulatory_radar_tools=regs,
                     regulatory_tool_count=len(regs),
                     spectral_predicate_modules=pred_mods,
                     spectral_predicate_present=int(bool(pred_mods)),
                     wmi_spectral_commands=wmi,
                     wmi_command_count=len(wmi),
                     phyerr_symbol_count=len(phy_syms),
                     spectral_symbol_count=len(spec_syms),
                     radar_symbol_count=len(radar_syms),
                     phyerr_code_table_recovered=0,
                     spectral_bin_format_recovered=0),
        gaps=["ath10k_core.ko is absent, so ATH10K_PHYERR_SPECTRAL and ATH10K_PHYERR_RADAR cannot "
              "be read; the vendor stack has no equivalent numeric PHY-error enum by name",
              "the PHYERR code table was not recovered: the processors are named, the codes they "
              "switch on are not",
              "the FFT bin format remains unrecovered (Stage 451A established the same limit)",
              "the per-generation processors are named but the payload format of each was not "
              "decoded",
              "is_spectral_phyerr lives in ath_spectral.ko, not umac.ko, so a single-module sweep "
              "would miss it",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[727A] ath10k={s['ath10k_core_present']} modules={s['modules_ok']} "
          f"lifecycle={s['phyerr_lifecycle_count']}/4 "
          f"processors={s['phyerr_processor_count']} gens={s['chip_generations']} "
          f"regulatory={s['regulatory_radar_tools']} "
          f"predicate={s['spectral_predicate_present']} wmi={s['wmi_command_count']}")
    print(f"        procs={procs}")
    print(f"[727A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
