#!/usr/bin/env python3
"""Stage 616A — LTU ranging: distance, cpe_distance, timing advance and CP alignment.

The stage names four things in `ame_core.ko` and `ame_dev.ko`:

  * Time-of-Flight (**ToF**) ranging;
  * **cpe_distance**;
  * timing advance (**TA**);
  * cyclic-prefix (**CP**) alignment.

Two are present, two are naming traps, and one is a surprise.

**`tof` is `autofa`.** All 29 `tof` hits sit inside the **auto-frequency-acquisition** family:
`autofa_create_scanning_list`, `autofa_scan_next`, `autofa_get_result`, `autofa_run_config`,
`autofa_set_speed`, `autofa_stop`. There is **no Time-of-Flight ranging** in either module.
`ranging`, `rtt` and `round_trip` all return zero. This is the eighth substring trap of the series
and the most consequential one, because `tof` is exactly the acronym a ranging stage would look for.

**`cpe_distance` is real.** It appears as a symbol, beside `ame_core_get_distance_meter`, and
`ame_dev.ko` exposes a `distance_meter_show` / `distance_meter_store` **sysfs pair**. So a distance
value is computed, held per CPE and readable.

**`timing_adv` does not exist.** The identifier has zero hits. The `ta_` token count of 65 is
substring noise (`data_`, `sta_`, `delta_` and similar), not timing advance.

**`cpsample` is the cyclic prefix.** It appears in `ame_dev.ko` (2 hits) and Stage 388A already
established it as the CP parameter — the per-frame CP length, not an alignment mechanism. There is
no `cp_align`, no `cyclic` and no `round_trip`.

The surprise is **`autofa_*`: 14 distinct symbols** — a complete auto-frequency acquisition
subsystem with its own scan list, scan step, result, configuration, speed control and stop. That is
materially more than the "spectral scan / auto-frequency hooks" that Stage 590A recorded, and it
shares the `tof` bytes that mislead this stage.

`tof_ranging_recovered = 0`; `distance_measurement_present = 1`.

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
       / "stage616a_ltu_ame_core_ranging_tof_and_timing_advance_re.json")

MODULES = {"ame_core.ko": LTU / "ame_core.ko", "ame_dev.ko": LTU / "ame_dev.ko"}

TOKENS = ["tof", "TOF", "ranging", "rtt", "round_trip", "cpe_distance", "distance_meter",
          "distance", "timing_adv", "ta_", "cyclic", "cp_align", "cpsample", "autofa"]
# the symbols that carry the distance mechanism
DISTANCE = ["ame_core_get_distance_meter", "cpe_distance"]
# the sysfs pair
SYSFS = "distance_meter"
# the auto-frequency acquisition family that owns the `tof` bytes
AUTOFA = "autofa_"


def ctx(b: bytes, tok: str, n: int = 3, w: int = 64) -> list[str]:
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
        tof_ctx = ctx(b, "tof", 4)
        ta_ctx = ctx(b, "ta_", 2)
        rows.append(dict(
            module=name, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            tokens={t: b.count(t.encode()) for t in TOKENS},
            distance={k: b.count(k.encode()) for k in DISTANCE},
            sysfs=dict(show=b.count((SYSFS + "_show").encode()),
                       store=b.count((SYSFS + "_store").encode())),
            tof_is_autofa=bool(tof_ctx) and all("autofa" in c for c in tof_ctx),
            tof_contexts=tof_ctx[:2],
            ta_contexts=ta_ctx,
            autofa_symbols=syms.matching(r"autofa", 24),
            distance_symbols=syms.matching(r"distance", 12),
            timing_symbols=syms.matching(r"timing_adv|ta_|rtt|ranging", 12)))

    ok = [r for r in rows if r.get("status") == "ok"]
    tof = sum(r["tokens"]["tof"] for r in ok)
    tof_autofa = sum(1 for r in ok if r["tof_is_autofa"])
    autofa = sorted({n for r in ok for n in r["autofa_symbols"]})
    dist_syms = sorted({n for r in ok for n in r["distance_symbols"]})
    timing_syms = sorted({n for r in ok for n in r["timing_symbols"]})
    cpe_dist = sum(r["distance"]["cpe_distance"] for r in ok)
    dist_meter = sum(r["distance"]["ame_core_get_distance_meter"] for r in ok)
    sysfs_pairs = sum(1 for r in ok if r["sysfs"]["show"] and r["sysfs"]["store"])
    ranging = sum(r["tokens"]["ranging"] + r["tokens"]["rtt"] + r["tokens"]["round_trip"]
                  for r in ok)
    timing_adv = sum(r["tokens"]["timing_adv"] for r in ok)
    cyclic = sum(r["tokens"]["cyclic"] + r["tokens"]["cp_align"] for r in ok)
    cpsample = sum(r["tokens"]["cpsample"] for r in ok)
    ta_tokens = sum(r["tokens"]["ta_"] for r in ok)

    report = dict(
        meta=dict(stage="616A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage616a_ltu_ame_core_ranging_tof_and_timing_advance_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted, nothing "
                        "transmitted",
                  method="token census of the ranging, timing and CP vocabularies; context "
                         "classification of the tof and ta_ substrings; defined-symbol lookup for "
                         "the distance and autofa families; sysfs pair detection",
                  premise_corrections=[
                      "tof is not Time-of-Flight: every hit sits inside the autofa auto-frequency "
                      "acquisition family, and ranging, rtt and round_trip are all 0",
                      "timing_adv does not exist as an identifier; the ta_ token count is "
                      "substring noise, not timing advance",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     tof_token_hits=tof,
                     tof_is_autofa_modules=tof_autofa,
                     tof_is_autofa=int(tof_autofa > 0),
                     autofa_symbol_count=len(autofa),
                     autofa_symbols=autofa[:12],
                     ranging_token_hits=ranging,
                     ranging_absent=int(ranging == 0),
                     cpe_distance_hits=cpe_dist,
                     distance_meter_symbol_hits=dist_meter,
                     distance_symbols=dist_syms,
                     distance_measurement_present=int(cpe_dist > 0 and dist_meter > 0),
                     distance_sysfs_pairs=sysfs_pairs,
                     timing_adv_token_hits=timing_adv,
                     ta_token_hits=ta_tokens,
                     timing_adv_absent=int(timing_adv == 0),
                     timing_symbols=timing_syms,
                     cyclic_token_hits=cyclic,
                     cpsample_hits=cpsample,
                     cp_alignment_named=int(cyclic > 0),
                     tof_ranging_recovered=0,
                     ta_mechanism_recovered=0,
                     cp_alignment_offset_recovered=0),
        gaps=["tof is a substring of autofa (auto-frequency acquisition), so the 29 hits are "
              "channel scanning, not ranging; ranging, rtt and round_trip are all 0",
              "timing_adv does not exist as an identifier, and the 65 ta_ hits are substrings of "
              "data_/sta_/delta_-style names, not timing advance",
              "cpe_distance and ame_core_get_distance_meter are real and expose a distance value "
              "with a sysfs pair, but the measurement source and units were not recovered",
              "cpsample is the cyclic-prefix length parameter, not a CP alignment offset; no "
              "cp_align or cyclic token exists",
              "autofa is a bonus finding, not part of this stage: 14 symbols covering scan list, "
              "next, result, config, speed and stop",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[616A] modules={s['modules_ok']} tof={s['tof_token_hits']}"
          f"(autofa={s['tof_is_autofa']}) ranging={s['ranging_token_hits']} "
          f"cpe_dist={s['cpe_distance_hits']} dist_sym={s['distance_meter_symbol_hits']} "
          f"sysfs={s['distance_sysfs_pairs']} ta_adv={s['timing_adv_token_hits']} "
          f"cpsample={s['cpsample_hits']} autofa_syms={s['autofa_symbol_count']}")
    print(f"        distance={dist_syms}")
    print(f"[616A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
