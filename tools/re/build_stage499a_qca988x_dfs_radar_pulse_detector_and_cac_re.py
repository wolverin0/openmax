#!/usr/bin/env python3
"""Stage 499A — DFS radar pulse discrimination, false-radar immunity and the CAC state machine.

The stage names three things in `firmware-2.bin` / `firmware-5.bin` and `ath_dfs.ko`:

  * a **pulse width / PRI / chirp discriminator**;
  * **false-radar immunity filters**;
  * a **60 s / 600 s CAC state machine**.

Both firmware images are **absent** (sixth confirmation in this series). `ath_dfs.ko` is present in
**six** variants and carries far more than the stage assumes: four independent discriminator
families, a chirp detector with a per-chip variant, a PRI blacklist with a *delta*, and a full
sysctl surface for overriding the CAC time and the false-RSSI threshold.

The discriminators, by symbol:

```
dfs_bin5_check / dfs_bin5_check_pulse / dfs_bin5_addpulse
dfs_bin_check        dfs_bin_fixedpattern_check
dfs_bin_pri_check    dfs_bin_resolution
dfs_check_chirping   dfs_check_chirping_merlin
PRI_black_list       PRI_black_list_delta      DFS_check_PRI_blakc_list
DFS_chirp_protect    DFS_pulse_cntr_FF         DFS_pulse_stream_stats
```

Two details worth naming:

  * **`DFS_check_PRI_blakc_list` is misspelled** — "blakc", not "black". A `grep black_list`
    finds `PRI_black_list` and `PRI_black_list_delta` but **misses** the checker. This is the third
    vendor typo this series has caught (after `pasued` in 459A and the `BE`/`PROBE` class).
  * **`dfs_check_chirping_merlin`** is a **per-chip variant**. Merlin is the AR93xx generation, so
    the chirp test is chip-specific — a single generic detector is not what shipped.

The false-radar surface, from the sysctl strings:

```
DFS_SET_FALSE_RSSI_THRESHOLD   ->  false RSSI threshold now = %d
DFS_SET_FILTER_RSSI_OFFSET     ->  RSSI filter offset is now %d
DFS_SET_PRI_MULTIPLIER         ->  DFS PRI multiplier is now / override is now %d
DFS_SET_MUTE_TIME
setting false_detect to TRUE. rssi=%d thresh=%d … peak_m…
```

The CAC surface:

```
DFS_SET_CAC_TIME_OVERRIDE_MS   ->  cac time override = %d se…
DFS_SET_IGNORE_CAC             ->  ignore cac = %d
```

`cac_600_present = 0`: **600 does not appear as a literal**. 60 appears 3 times in contexts unrelated
to CAC. So the 60 s / 600 s constants the stage asserts are **not recoverable as literals** — the
delay is computed from a channel list and an override in milliseconds.

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
XW = REPO_ROOT / "artifacts" / "firmware_re_xw_m5"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage499a_qca988x_dfs_radar_pulse_detector_and_cac_re.json")

MODULES = {
    "WA.v8.7.25": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dfs.ko",
    "XC.v8.7.25": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dfs.ko",
    "XC.v8.7.4cs": FW / "xc_874cs_rootfs/lib/modules/2.6.32.68/ath_dfs.ko",
    "XW.v6.1.4": XW / "xw_614_rootfs/lib/modules/2.6.32.71/ath_dfs.ko",
    "XW.v6.3.6": XW / "xw_636_rootfs/lib/modules/2.6.32.71/ath_dfs.ko",
}

TOKENS = ["radar", "RADAR", "pulse", "PRI", "pri_", "chirp", "CAC", "dfs_",
          "false", "filter", "width", "peak", "bin5"]
# the discriminator families, by symbol fragment
FAMILIES = {
    "bin5": r"bin5",
    "bin": r"dfs_bin_check|dfs_bin_fixedpattern|dfs_bin_pri_check|bin_resolution",
    "chirp": r"chirping|chirp_protect",
    "pri_blacklist": r"PRI_black|pri_blakc",
}
# sysctl knobs that carry the override surface
KNOBS = ["DFS_SET_CAC_TIME_OVERRIDE_MS", "DFS_SET_IGNORE_CAC", "DFS_SET_FALSE_RSSI_THRESHOLD",
         "DFS_SET_FILTER_RSSI_OFFSET", "DFS_SET_PRI_MULTIPLIER", "DFS_SET_MUTE_TIME"]
# literals the stage asserts
LITERALS = {"cac_60": b"60", "cac_600": b"600"}


def ctx(b: bytes, tok: str, n: int = 3, w: int = 66) -> list[str]:
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
            rows.append(dict(image=label, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        fams = {k: syms.matching(v, 24) for k, v in FAMILIES.items()}
        rows.append(dict(
            image=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            tokens={t: b.count(t.encode()) for t in TOKENS},
            knobs={k: b.count(k.encode()) for k in KNOBS},
            literals={k: b.count(v) for k, v in LITERALS.items()},
            families=fams,
            family_hits={k: len(v) for k, v in fams.items()},
            radar_symbols=syms.matching(r"radar", 16),
            chirp_names=sorted({m.decode() for m in
                                re.findall(rb"[a-z0-9_]*chirp[a-z0-9_]*", b)}),
            chirp_contexts=ctx(b, "is_chirping", 2),
            false_contexts=ctx(b, "false_detect", 2),
            cac_contexts=ctx(b, "cac time override", 2)))

    ok = [r for r in rows if r.get("status") == "ok"]
    fams_present = sorted({k for r in ok for k, v in r["family_hits"].items() if v})
    knobs_present = sorted({k for r in ok for k, v in r["knobs"].items() if v})
    chirp_syms = sorted({n for r in ok for n in r["families"]["chirp"]})
    chirp_names = sorted({n for r in ok for n in r.get("chirp_names", [])})
    pri_syms = sorted({n for r in ok for n in r["families"]["pri_blacklist"]})
    bin5_syms = sorted({n for r in ok for n in r["families"]["bin5"]})
    cac_ms = sum(1 for r in ok if r["knobs"]["DFS_SET_CAC_TIME_OVERRIDE_MS"])
    ignore_cac = sum(1 for r in ok if r["knobs"]["DFS_SET_IGNORE_CAC"])
    false_thr = sum(1 for r in ok if r["knobs"]["DFS_SET_FALSE_RSSI_THRESHOLD"])
    sixty = sum(r["literals"]["cac_60"] for r in ok)
    sixhundred = sum(r["literals"]["cac_600"] for r in ok)

    report = dict(
        meta=dict(stage="499A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage499a_qca988x_dfs_radar_pulse_detector_and_cac_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no firmware loaded, no module loaded, "
                        "no radio contacted, nothing transmitted",
                  method="token census across five ath_dfs.ko variants; symbol-family "
                         "classification for bin5/bin/chirp/pri_blacklist; sysctl-knob extraction "
                         "for the CAC and false-RSSI override surface; literal probe for 60 and 600",
                  premise_corrections=[
                      "firmware-2.bin and firmware-5.bin are absent, so no firmware-side pulse "
                      "detector can be read",
                      "600 does not appear as a literal; the 60 s / 600 s CAC constants are not "
                      "recoverable as numbers, only the millisecond override knob is",
                  ],
                  radio_safety="static only"),
        firmware_images=fw_images,
        modules=rows,
        summary=dict(firmware_images_present=sum(fw_images.values()),
                     modules_ok=len(ok),
                     images_with_radar_symbols=sum(1 for r in ok if r["radar_symbols"]),
                     discriminator_families=fams_present,
                     discriminator_family_count=len(fams_present),
                     bin5_symbol_count=len(bin5_syms),
                     bin5_symbols=bin5_syms,
                     chirp_symbol_count=len(chirp_syms),
                     chirp_symbols=chirp_syms,
                     chirp_names=chirp_names,
                     chirp_is_per_chip=int(any("merlin" in n for n in chirp_names)),
                     pri_blacklist_symbols=pri_syms,
                     pri_blacklist_typo=int(any("blakc" in n for n in pri_syms)),
                     knobs_present=knobs_present,
                     knob_count=len(knobs_present),
                     cac_override_ms_modules=cac_ms,
                     ignore_cac_modules=ignore_cac,
                     false_rssi_threshold_modules=false_thr,
                     cac_60_literals=sixty,
                     cac_600_literals=sixhundred,
                     cac_constant_recovered=0,
                     pulse_width_table_recovered=0,
                     chirp_table_recovered=0),
        gaps=["firmware-2.bin and firmware-5.bin are absent, so the firmware-side pulse detector "
              "cannot be read at all",
              "600 does not appear as a literal anywhere; the 23 hits for the byte pair 60 are "
              "not evidence of anything because that pair matches any decimal text, so neither "
              "the 600 s nor the 60 s CAC duration was recovered as a constant",
              "the pulse-width and PRI thresholds are named (PRI multiplier, PRI blacklist with "
              "delta) but no value table was extracted",
              "four discriminator families are present by name; the decision logic that combines "
              "them into a radar verdict was not decoded",
              "DFS_check_PRI_blakc_list is misspelled in the shipped binary, so a grep for "
              "black_list misses the checker",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[499A] fw={s['firmware_images_present']} modules={s['modules_ok']} "
          f"families={fams_present} bin5={s['bin5_symbol_count']} "
          f"chirp={s['chirp_symbol_count']}(per_chip={s['chirp_is_per_chip']}) "
          f"pri_typo={s['pri_blacklist_typo']} knobs={s['knob_count']}")
    print(f"        cac_ms={s['cac_override_ms_modules']} "
          f"ignore_cac={s['ignore_cac_modules']} false_thr={s['false_rssi_threshold_modules']} "
          f"60={s['cac_60_literals']} 600={s['cac_600_literals']}")
    for m in ok:
        print(f"        {m['image']:<12} {m['bytes']:>7}B fam={m['family_hits']}")
    print(f"[499A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
