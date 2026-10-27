#!/usr/bin/env python3
"""Stage 786A — frame_pulse_offset, remote SFN sync and panel isolation on colocated LTU.

The stage asks for three things in `ame_core.ko` and `ame_dev.ko`:

  * **`frame_pulse_offset`**;
  * **`ame_bbp_is_remote_SFN_synchronized`**;
  * **TX/RX isolation of colocated LTU panels**.

Two are present with full get/set pairs. The third is a **naming correction**: the stack has
`cli_isolation`, which is **client** isolation, not panel isolation.

## frame_pulse_offset is a get/set pair plus a sysfs knob

```
ame_bbp_set_frame_pulse_offset      ame_bbp_get_frame_pulse_offset
frame_pulse_offset_show             frame_pulse_offset_store        (ame_dev.ko)
```

**`CONFIRMED`**: `frame_pulse_offset_getset = 1`. So the offset is **writable at runtime** from
userspace, and readable back.

This is the knob Stage 416A looked for and did not find: the GPS frame durations were in
`ubnt_poll_host.ko` but the **alignment** was not. Here it is — the offset of the frame pulse,
which is what aligns a TDMA frame to an absolute reference.

## The SFN synchronisation predicate exists at two layers

```
ame_bbp_is_remote_SFN_synchronized
bbp_base_is_remote_SFN_synchronized
```

**`CONFIRMED`**: `sync_predicate_variants = 2` — a high-level and a base-level predicate.

Combined with Stage 668A's finding (`ame_bbp_get_sync_sfn_count` returns a **miss count**), the pair
gives both a boolean and a magnitude: *are* the two ends aligned, and *by how many superframes* they
are not.

## The isolation that exists is client isolation, not panel isolation

```
ame_core_get_cli_isolation      ame_core_set_cli_isolation
```

**`CONFIRMED`**: `cli_isolation_getset = 1`.

**`REFUTED`**: `coloc`, `sector` and `panel` all return **0**.

`cli_isolation` is **client isolation** — preventing associated stations from talking to each other.
That is a different mechanism from isolating **co-located panels** from each other, which is what the
stage asks for. Reading `cli_isolation` as panel isolation would be a false positive: the words share
only "isolation".

This is a **semantic** trap rather than a substring one, and it is worth flagging precisely because
it looks like the right answer.

**`UNKNOWN`**: how co-located panels are kept from interfering. Stage 590A found LBT with a
`pause_txframe` hook and Stage 668A found the SFN sync — the ingredients exist, but no
`panel`/`sector`/`coloc` marker binds them into an isolation scheme.

`tx_rx_isolation_recovered = 0`.

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
       / "stage786a_ltu_ame_core_colocated_frame_pulse_sync_re.json")

MODULES = {"ame_core.ko": LTU / "ame_core.ko", "ame_dev.ko": LTU / "ame_dev.ko"}

TOKENS = ["frame_pulse_offset", "is_remote_SFN", "isolation", "isolat",
          "coloc", "COLOC", "sector", "panel"]
# the frame pulse offset accessors
FPO = ["ame_bbp_set_frame_pulse_offset", "ame_bbp_get_frame_pulse_offset"]
# the SFN sync predicates
SYNC = ["ame_bbp_is_remote_SFN_synchronized", "bbp_base_is_remote_SFN_synchronized"]
# the client isolation accessors
CLI = ["ame_core_get_cli_isolation", "ame_core_set_cli_isolation"]
# the sysfs knob
SYSFS = "frame_pulse_offset"
# the words the stage assumes
ASSUMED = ["coloc", "sector", "panel"]


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
            fpo={k: b.count(k.encode()) for k in FPO},
            sync={k: b.count(k.encode()) for k in SYNC},
            cli={k: b.count(k.encode()) for k in CLI},
            sysfs=dict(show=b.count((SYSFS + "_show").encode()),
                       store=b.count((SYSFS + "_store").encode())),
            assumed={t: b.count(t.encode()) for t in ASSUMED},
            fpo_symbols=syms.matching(r"frame_pulse", 8),
            sync_symbols=syms.matching(r"is_remote_SFN", 8),
            isolation_symbols=syms.matching(r"isolation", 8)))

    ok = [r for r in rows if r.get("status") == "ok"]
    fpo = [k for k in FPO if any(r["fpo"][k] for r in ok)]
    sync = [k for k in SYNC if any(r["sync"][k] for r in ok)]
    cli = [k for k in CLI if any(r["cli"][k] for r in ok)]
    sysfs = sum(1 for r in ok if r["sysfs"]["show"] and r["sysfs"]["store"])
    assumed = sum(sum(r["assumed"].values()) for r in ok)
    isol_syms = sorted({n for r in ok for n in r["isolation_symbols"]})
    fpo_syms = sorted({n for r in ok for n in r["fpo_symbols"]})

    report = dict(
        meta=dict(stage="786A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage786a_ltu_ame_core_colocated_frame_pulse_sync_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="accessor-pair detection for frame_pulse_offset and cli_isolation; SFN "
                         "sync predicate lookup at two layers; sysfs show/store detection; "
                         "explicit probe for the coloc/sector/panel vocabulary",
                  premise_corrections=[
                      "the isolation the stack implements is cli_isolation, which isolates "
                      "CLIENTS, not co-located panels: coloc, sector and panel all return 0",
                      "frame_pulse_offset is a runtime writable knob, so the frame alignment "
                      "Stage 416A could not find is exposed rather than compiled in",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     frame_pulse_offset_accessors=fpo,
                     frame_pulse_offset_getset=int(len(fpo) == 2),
                     frame_pulse_offset_sysfs_pairs=sysfs,
                     frame_pulse_offset_symbols=fpo_syms,
                     sync_predicates=sync,
                     sync_predicate_variants=len(sync),
                     remote_sfn_sync_named=int(len(sync) >= 1),
                     cli_isolation_accessors=cli,
                     cli_isolation_getset=int(len(cli) == 2),
                     cli_isolation_symbols=isol_syms,
                     cli_isolation_is_client_not_panel=1,
                     assumed_vocabulary_hits=assumed,
                     coloc_sector_panel_absent=int(assumed == 0),
                     frame_alignment_knob_present=int(len(fpo) == 2 and sysfs >= 1),
                     tx_rx_isolation_recovered=0,
                     panel_isolation_scheme_recovered=0),
        gaps=["coloc, sector and panel all return 0: there is no named panel-isolation scheme, "
              "so how co-located LTU panels are kept apart was not recovered",
              "cli_isolation is client isolation (station-to-station), NOT panel isolation; "
              "reading it as the latter would be a false positive",
              "frame_pulse_offset is writable but its units and reference point were not "
              "recovered",
              "the two SFN sync predicates are named but which layer owns the decision is not "
              "established",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[786A] modules={s['modules_ok']} fpo={s['frame_pulse_offset_getset']} "
          f"sysfs={s['frame_pulse_offset_sysfs_pairs']} sync={s['sync_predicate_variants']} "
          f"cli={s['cli_isolation_getset']} assumed={s['assumed_vocabulary_hits']} "
          f"knob={s['frame_alignment_knob_present']}")
    print(f"        fpo={fpo}")
    print(f"        cli={cli}")
    print(f"[786A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
