#!/usr/bin/env python3
"""Stage 668A — GPS 1PPS and the TDMA superframe clock in LTU.

The stage asks for GPS 1PPS synchronisation and the TDMA superframe clock in `ame_core.ko` and
`eab_driver.ko`.

`eab_driver.ko` is **absent** (twelfth confirmation), so `ame_core.ko` and `ame_dev.ko` carry the
answer. The **superframe clock is real and richly named** — 121 `SFN` and 80 `sfn` hits, with a
complete get/set/sync family:

```
ame_bbp_get_rx_sfn        ame_bbp_set_rx_sfn
ame_bbp_get_tx_sfn        ame_bbp_set_tx_sfn
ame_bbp_op_sync_sfn       ame_bbp_sync_SFN
ame_bbp_get_sync_sfn_count
ame_bbp_get_sync_mode     ame_bbp_set_sync_mode
ame_bbp_is_remote_SFN_synchronized    ame_bbp_set_remote_SFN
ame_bbp_reset_aes_sfn_ext
```

**`CONFIRMED`**: RX and TX superframe numbers are **separate counters with separate setters**. The
SFN is not one clock — each direction carries its own, and `is_remote_SFN_synchronized` is the
predicate that says whether the two ends agree.

**GPS is present but as a *requirement*, not a reader.** 38 `GPS` hits and the decisive message:

```
NxN needs GPS sync!
```

plus `cpeFsmNxN_OffGPS_OnCIR` — a state-machine transition that leaves GPS and switches to CIR-based
tracking. **`CONFIRMED`**: the NxN (MIMO) mode **requires** GPS sync and has an explicit fallback
path when GPS is absent.

**Two tokens are traps, and both are severe for this stage:**

| Token | Hits | Reality |
| :--- | :-: | :--- |
| **`pps`** | 2 | `ATX: (data=%u, bytes=%llu, pps=%u)` — **packets per second** |
| **`ptp`** | 25 | mostly `AME_Sched_PtP_master` / `_slave` — **Point-to-Point**, not Precision Time Protocol |

**`REFUTED`**: there is **no `1pps` token at all** (0 hits). The one-second pulse the stage asks for
is **not named** in these modules — the `pps` hits are throughput statistics.

That is consistent with Stage 416A: the GPS frame durations live in `ubnt_poll_host.ko`, the DCXO
sync lives here (`ame_bbp_rt_keep_dcxo_sync`, and `bbp_rf_dcxo_is_sync_by_gps` from Stage 486A), and
the 1PPS reader (`ubnt-gps-reader`) is a **zero-byte file**.

`one_pps_source_recovered = 0`; `superframe_clock_named = 1`.

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
       / "stage668a_ltu_ame_core_gps_1pps_and_frame_sync_re.json")

MODULES = {"ame_core.ko": LTU / "ame_core.ko", "ame_dev.ko": LTU / "ame_dev.ko"}

TOKENS = ["sfn", "SFN", "gps", "GPS", "pps", "1pps", "ptp", "superframe", "frame_sync"]
# the superframe counter family
SFN = ["ame_bbp_get_rx_sfn", "ame_bbp_set_rx_sfn", "ame_bbp_get_tx_sfn",
       "ame_bbp_set_tx_sfn", "ame_bbp_op_sync_sfn", "ame_bbp_sync_SFN"]
# the synchronisation predicates and counters
SYNC = ["ame_bbp_get_sync_sfn_count", "ame_bbp_is_remote_SFN_synchronized",
        "ame_bbp_set_remote_SFN", "ame_bbp_get_sync_mode", "ame_bbp_set_sync_mode"]
# the GPS requirement
GPS_MSG = "NxN needs GPS sync"
# the pps trap
PPS_TRAP = "pps=%u"
# the ptp trap
PTP_TRAP = "AME_Sched_PtP"


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
            sfn={k: b.count(k.encode()) for k in SFN},
            sync={k: b.count(k.encode()) for k in SYNC},
            gps_msg=b.count(GPS_MSG.encode()),
            pps_trap=b.count(PPS_TRAP.encode()),
            ptp_trap=b.count(PTP_TRAP.encode()),
            sfn_symbols=syms.matching(r"sfn", 24),
            gps_symbols=syms.matching(r"gps", 16),
            ptp_symbols=syms.matching(r"ptp", 16)))

    ok = [r for r in rows if r.get("status") == "ok"]
    sfn_syms = sorted({n for r in ok for n in r["sfn_symbols"]})
    gps_syms = sorted({n for r in ok for n in r["gps_symbols"]})
    ptp_syms = sorted({n for r in ok for n in r["ptp_symbols"]})
    sfn_found = [k for k in SFN if any(r["sfn"][k] for r in ok)]
    sync_found = [k for k in SYNC if any(r["sync"][k] for r in ok)]
    gps_msg = sum(r["gps_msg"] for r in ok)
    pps_trap = sum(r["pps_trap"] for r in ok)
    ptp_trap = sum(r["ptp_trap"] for r in ok)
    one_pps = sum(r["tokens"]["1pps"] for r in ok)
    sfn_tokens = sum(r["tokens"]["sfn"] + r["tokens"]["SFN"] for r in ok)
    gps_tokens = sum(r["tokens"]["gps"] + r["tokens"]["GPS"] for r in ok)
    ptp_tokens = sum(r["tokens"]["ptp"] for r in ok)

    report = dict(
        meta=dict(stage="668A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage668a_ltu_ame_core_gps_1pps_and_frame_sync_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census of the SFN, GPS, pps and ptp vocabularies; defined-symbol "
                         "lookup for the sfn counter and synchronisation families; explicit "
                         "context classification of the pps and ptp traps",
                  premise_corrections=[
                      "eab_driver.ko is absent, so the SFN and GPS analysis is ame_core.ko only",
                      "pps in these modules means packets per second (ATX/ARX statistics), and "
                      "1pps does not exist: the one-second pulse is not named here",
                  ],
                  radio_safety="static_only"),
        absence=dict(eab_driver=eab),
        modules=rows,
        summary=dict(eab_driver_present=eab > 0,
                     modules_ok=len(ok),
                     sfn_token_hits=sfn_tokens,
                     sfn_symbol_count=len(sfn_syms),
                     sfn_counter_symbols=sfn_found,
                     sfn_counter_count=len(sfn_found),
                     rx_tx_sfn_separate=int("ame_bbp_get_rx_sfn" in sfn_found
                                            and "ame_bbp_get_tx_sfn" in sfn_found),
                     sync_controls=sync_found,
                     sync_control_count=len(sync_found),
                     remote_sfn_synchronized=int(
                         any("is_remote_SFN_synchronized" in n for n in sfn_syms)),
                     gps_token_hits=gps_tokens,
                     gps_symbol_count=len(gps_syms),
                     gps_symbols=gps_syms[:6],
                     gps_sync_required=gps_msg,
                     gps_required_message=int(gps_msg > 0),
                     pps_trap_hits=pps_trap,
                     pps_is_packets_per_second=int(pps_trap > 0),
                     one_pps_hits=one_pps,
                     one_pps_absent=int(one_pps == 0),
                     ptp_token_hits=ptp_tokens,
                     ptp_trap_hits=ptp_trap,
                     ptp_symbols=ptp_syms[:6],
                     ptp_is_point_to_point=int(ptp_trap > 0),
                     superframe_clock_named=int(len(sfn_found) >= 4),
                     one_pps_source_recovered=0,
                     sfn_epoch_alignment_recovered=0),
        gaps=["eab_driver.ko is absent, so the stage's second module has no bytes",
              "1pps does not exist as a token and the two pps hits are packets-per-second "
              "throughput counters (ATX/ARX), not a one-second pulse",
              "ptp is dominated by AME_Sched_PtP_master/_slave, which is Point-to-Point link "
              "scheduling, not Precision Time Protocol",
              "the SFN counter family is named in full but the counter width and the epoch "
              "alignment to any external reference were not recovered",
              "GPS is present as a requirement (NxN needs GPS sync) and as a fallback state "
              "(cpeFsmNxN_OffGPS_OnCIR), not as a reader; Stage 416A showed ubnt-gps-reader is a "
              "zero-byte file",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[668A] eab={s['eab_driver_present']} modules={s['modules_ok']} "
          f"SFN={s['sfn_token_hits']}({s['sfn_symbol_count']}sym) "
          f"rx_tx_sep={s['rx_tx_sfn_separate']} sync={s['sync_control_count']} "
          f"GPS={s['gps_token_hits']} gps_req={s['gps_required_message']} "
          f"pps_trap={s['pps_trap_hits']} 1pps={s['one_pps_hits']} "
          f"ptp_trap={s['ptp_trap_hits']}")
    print(f"        sfn={sfn_found[:6]}")
    print(f"[668A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
