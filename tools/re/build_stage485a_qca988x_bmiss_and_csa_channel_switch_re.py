#!/usr/bin/env python3
"""Stage 485A — beacon-miss thresholds, the Roam state machine and CSA channel switch.

The stage asks for four things in `firmware-2.bin` / `firmware-5.bin` and `umac.ko`:

  * beacon-miss (**bmiss**) threshold counters;
  * the **Roam** state machine;
  * the **CSA** (Channel Switch Announcement) state machine;
  * `WMI_VDEV_PARAM_BMISS_COUNT_MAX`.

Both firmware images are **absent** (fifth confirmation in this series). Everything below is from
the vendor `umac.ko`, where all three mechanisms are named — but not in the form the stage guesses:

  * **bmiss is a software timer, not a counter.** The module carries the whole lifecycle:
    `ieee80211_mlme_sta_swbmiss_timer_alloc_id` / `_enable` / `_disable` / `_free_id` /
    `_print_status`. "swbmiss" = **software** beacon miss. The threshold is what that timer is
    armed with, and the timer is the mechanism.
  * **CSA has three variants, not one.** The log strings distinguish **CSA**, **E-CSA**
    (extended) and **UCSA** (Ubiquiti's own) — and the symbol table confirms them:
    `ieee80211_process_csa_ecsa_ie`, `ieee80211_add_ubnt_csa`, `ieee80211_scan_entry_ubntcsa`.
  * **Roam is a connection state machine.** `ieee80211_connection_sm_*` plus
    `connection_sm_roam_check_timer_handler` — roam is a timer inside a broader connection SM.
  * **`WMI_VDEV_PARAM_BMISS_COUNT_MAX` does not exist as a string** (0 hits, like every other
    `VDEV_PARAM` identifier). The threshold is a numeric parameter and cannot be read by name.

The threshold **values** are not recovered: the timer's arming argument was not traced.

Radio safety: static only. No firmware loaded, no module loaded, no radio contacted.
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
       / "stage485a_qca988x_bmiss_and_csa_channel_switch_re.json")

MODULES = {
    "WA.v8.7.25:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC.v8.7.25:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
}

BMISS = ["bmiss", "BMISS", "beacon_miss", "swbmiss"]
CSA = ["CSA", "csa_", "E-CSA", "UCSA", "chanswitch", "chan_switch", "channel_switch"]
ROAM = ["roam", "connection_sm"]
WMI_PARAM = ["WMI_VDEV_PARAM", "VDEV_PARAM", "BMISS_COUNT_MAX", "max_bmiss"]


def ctx(b: bytes, tok: str, n: int = 3, w: int = 68) -> list[str]:
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

    fw_images = {n: len([p for p in (REPO_ROOT / "artifacts").rglob(n) if p.is_file()])
                 for n in ("firmware-2.bin", "firmware-5.bin")}

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
            bmiss={t: b.count(t.encode()) for t in BMISS},
            csa={t: b.count(t.encode()) for t in CSA},
            roam={t: b.count(t.encode()) for t in ROAM},
            wmi_param={t: b.count(t.encode()) for t in WMI_PARAM},
            bmiss_symbols=syms.matching(r"bmiss|beacon_miss", 24),
            csa_symbols=syms.matching(r"csa|chanswitch|chan_switch", 24),
            roam_symbols=syms.matching(r"roam|connection_sm", 20),
            wmi_switch_symbols=syms.matching(r"wmi_unified.*(chan_switch|roam)", 12),
            csa_contexts=ctx(b, "CSA new channel", 2) + ctx(b, "UCSA new channel", 2),
            bmiss_contexts=ctx(b, "swbmiss", 2)))

    ok = [r for r in rows if r.get("status") == "ok"]
    bmiss_syms = sorted({n for r in ok for n in r["bmiss_symbols"]})
    csa_syms = sorted({n for r in ok for n in r["csa_symbols"]})
    roam_syms = sorted({n for r in ok for n in r["roam_symbols"]})
    wmi_syms = sorted({n for r in ok for n in r["wmi_switch_symbols"]})
    swb = [n for n in bmiss_syms if "swbmiss" in n]
    wmi_param_hits = sum(sum(r["wmi_param"].values()) for r in ok)
    csa_variants = sorted({t for r in ok for t in ("CSA", "E-CSA", "UCSA")
                           if r["csa"][t] > 0})

    report = dict(
        meta=dict(stage="485A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage485a_qca988x_bmiss_and_csa_channel_switch_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no firmware loaded, no module loaded, "
                        "no radio contacted",
                  method="token census of the bmiss, CSA and roam vocabularies; defined-symbol "
                         "lookup for the swbmiss timer lifecycle, the CSA/ECSA/UCSA handlers and "
                         "the connection-SM roam path; WMI chan-switch send/handler lookup",
                  premise_corrections=[
                      "firmware-2.bin and firmware-5.bin are absent, so no firmware-side bmiss "
                      "counter can be read",
                      "WMI_VDEV_PARAM_BMISS_COUNT_MAX does not exist as a string; VDEV param names "
                      "are macros, as in Stages 437A and 451A",
                  ],
                  radio_safety="static only"),
        firmware_images=fw_images,
        modules=rows,
        summary=dict(firmware_images_present=sum(fw_images.values()),
                     modules_ok=len(ok),
                     bmiss_token_hits=sum(sum(r["bmiss"].values()) for r in ok),
                     bmiss_symbol_count=len(bmiss_syms),
                     swbmiss_symbols=swb,
                     swbmiss_lifecycle_named=int(len(swb) >= 4),
                     bmiss_state_machine_named=int(bool(bmiss_syms)),
                     csa_token_hits=sum(sum(r["csa"].values()) for r in ok),
                     csa_variants=csa_variants,
                     csa_variant_count=len(csa_variants),
                     csa_symbol_count=len(csa_syms),
                     csa_symbols=csa_syms[:12],
                     csa_state_machine_named=int(bool(csa_syms)),
                     roam_token_hits=sum(sum(r["roam"].values()) for r in ok),
                     roam_symbol_count=len(roam_syms),
                     roam_symbols=roam_syms[:8],
                     roam_state_machine_named=int(bool(roam_syms)),
                     wmi_switch_symbols=wmi_syms,
                     wmi_param_name_hits=wmi_param_hits,
                     bmiss_count_max_present=int(wmi_param_hits > 0),
                     bmiss_threshold_recovered=0,
                     csa_switch_sequence_recovered=0),
        gaps=["firmware-2.bin and firmware-5.bin are absent, so the bmiss counter cannot be read "
              "from an image",
              "WMI_VDEV_PARAM_BMISS_COUNT_MAX is a macro: 0 hits, like every other VDEV param "
              "name in Stages 437A and 451A",
              "the swbmiss timer lifecycle is named but its arming argument was not traced, so "
              "the threshold value is unknown",
              "the three CSA variants are distinguished by name and by log string, but the "
              "channel-switch sequence (announce count, dwell, switch instant) was not decoded",
              "roam is a timer inside the connection state machine; the roam decision rule was "
              "not recovered",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[485A] fw={s['firmware_images_present']} modules={s['modules_ok']} "
          f"bmiss_syms={s['bmiss_symbol_count']} swb={len(swb)} "
          f"csa_variants={csa_variants} csa_syms={s['csa_symbol_count']} "
          f"roam_syms={s['roam_symbol_count']} wmi_param={s['wmi_param_name_hits']}")
    print(f"        swbmiss={swb[:5]}")
    print(f"        wmi={wmi_syms[:4]}")
    print(f"[485A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
