#!/usr/bin/env python3
"""Stage 452A — airtime deficit quanta, WMM AC weights and low-MCS penalization in ubnt_poll_host.

The stage asserts four mechanisms in `ubnt_poll_host.ko` on WA and XC:

  * per-CPE **airtime deficit quantum** tables;
  * **4-AC WMM priority queue weights** (`AC_BE` / `AC_VI` / `AC_VO` / `AC_BK`);
  * **penalization thresholds for low-MCS stations**;
  * (implicitly) a weighted scheduler built on those.

What the module actually contains, tested one token at a time:

| Token | Hits | Verdict |
| :--- | :-: | :--- |
| `deficit` | **0** | absent |
| `quantum` | **0** | absent |
| `wmm`, `WMM` | **0** | absent |
| `AC_BE`, `AC_VI`, `AC_VO`, `AC_BK` | **0** | absent |
| `penal`, `weight`, `mcs` | **0** | absent |
| `airtime` | 2 | `ff_mcast_airtime_limit` — **multicast**, not per-CPE |
| `prio` | 6 | **real** — `sta_priority`, `set_ap_sta_priority` |
| `BE` | 3 | **not a token**: every hit is inside `PROBE` / `NEXT-PROBE` |

So the framing is refuted but a real configuration surface exists, and it is more specific than
the stage assumed. The knobs that actually appear, all in the same sysctl region:

```
cms_bias            voip_bias          ff_cap_rep
ff_mcast_airtime_limit                 daprot
ff_unit_shift       ff_guard_units     ff_sta_rx_rssi_th
dack_arbit_max
sta_priority
```

`ff_sta_rx_rssi_th` is the closest thing to a station penalization threshold; `daprot` is the
DAPR (TDMA) protocol selector; `ff_unit_shift` / `ff_guard_units` are the frame-unit geometry.
None of them is a deficit counter, and the tool says so.

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
       / "stage452a_ubnt_poll_airtime_deficit_and_priority_queues_re.json")

MODULES = {
    "WA.v8.7.25": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XC.v8.7.25": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
}

# the mechanism the stage names: expected absent
DEFICIT = ["deficit", "quantum", "credit", "surplus"]
# WMM access categories: expected absent
WMM = ["wmm", "WMM", "AC_BE", "AC_VI", "AC_VO", "AC_BK", "ac_be", "ac_vi", "ac_vo", "ac_bk"]
# penalization vocabulary: expected absent
PENAL = ["penal", "punish", "starve", "low_mcs", "mcs", "weight"]
# what is actually present
PRESENT = ["airtime", "prio", "sta_priority", "daprot", "ff_mcast_airtime_limit",
           "ff_sta_rx_rssi_th", "ff_unit_shift", "ff_guard_units", "dack_arbit_max",
           "cms_bias", "voip_bias", "ff_cap_rep"]
# short tokens that need context classification
AMBIGUOUS = ["BE", "VI", "VO", "BK"]


def ctx(b: bytes, tok: str, n: int = 4, w: int = 66) -> list[str]:
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
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(version=label, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        be_ctx = ctx(b, "BE")
        rows.append(dict(
            version=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            deficit={t: b.count(t.encode()) for t in DEFICIT},
            wmm={t: b.count(t.encode()) for t in WMM},
            penal={t: b.count(t.encode()) for t in PENAL},
            present={t: b.count(t.encode()) for t in PRESENT},
            ambiguous={t: b.count(t.encode()) for t in AMBIGUOUS},
            airtime_contexts=ctx(b, "airtime"),
            prio_contexts=ctx(b, "prio"),
            be_contexts=be_ctx,
            be_all_probe=bool(be_ctx) and all("PROBE" in c.upper() for c in be_ctx),
            priority_symbols=syms.matching(r"priority|airtime|dapr|ff_", 24),
            wmm_symbols=syms.matching(r"wmm|ac_(be|vi|vo|bk)|deficit|quantum", 24)))

    ok = [r for r in rows if r.get("status") == "ok"]
    deficit_total = sum(sum(r["deficit"].values()) for r in ok)
    wmm_total = sum(sum(r["wmm"].values()) for r in ok)
    penal_total = sum(sum(r["penal"].values()) for r in ok)
    airtime_total = sum(r["present"]["airtime"] for r in ok)
    prio_total = sum(r["present"]["prio"] for r in ok)
    be_total = sum(r["ambiguous"]["BE"] for r in ok)
    be_probe = sum(1 for r in ok if r["be_all_probe"])
    rssi_th = sum(r["present"]["ff_sta_rx_rssi_th"] for r in ok)
    mc_air = sum(r["present"]["ff_mcast_airtime_limit"] for r in ok)
    symbols = sorted({n for r in ok for n in r["priority_symbols"]})
    wmm_symbols = sorted({n for r in ok for n in r["wmm_symbols"]})

    report = dict(
        meta=dict(stage="452A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage452a_ubnt_poll_airtime_deficit_and_priority_queues_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census over the deficit, WMM and penalization vocabularies; "
                         "context classification of the ambiguous short tokens BE/VI/VO/BK; "
                         "defined-symbol lookup for the priority and ff_ configuration family",
                  premise_corrections=[
                      "deficit, quantum, WMM and AC_BE/VI/VO/BK do not exist in ubnt_poll_host.ko; "
                      "the framing of a 4-AC weighted queue with deficit counters is not supported",
                      "airtime refers to ff_mcast_airtime_limit (multicast), and BE is a substring "
                      "of PROBE / NEXT-PROBE in the rate-control debug output",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     deficit_tokens=deficit_total,
                     wmm_tokens=wmm_total,
                     penalization_tokens=penal_total,
                     airtime_tokens=airtime_total,
                     prio_tokens=prio_total,
                     be_tokens=be_total,
                     modules_where_be_is_probe=be_probe,
                     mcast_airtime_limit_tokens=mc_air,
                     rssi_threshold_tokens=rssi_th,
                     priority_symbols=symbols[:10],
                     wmm_symbols=wmm_symbols[:10],
                     deficit_table_recovered=0,
                     wmm_weights_recovered=0,
                     low_mcs_penalty_recovered=0,
                     rssi_threshold_knob_present=int(rssi_th > 0)),
        gaps=["deficit, quantum, credit and surplus do not exist: no per-CPE airtime deficit "
              "counter was located",
              "wmm, WMM and every AC_* name are absent: no 4-AC weight table exists in this "
              "module",
              "penal, weight, low_mcs and mcs are all absent, so no low-MCS penalization "
              "threshold was recovered",
              "airtime appears only as ff_mcast_airtime_limit, which limits multicast airtime, "
              "not a per-station quantum",
              "BE is not an access category here: all three hits sit inside PROBE / NEXT-PROBE "
              "in the rate-control debug line",
              "the real penalty-adjacent knob is ff_sta_rx_rssi_th, an RSSI threshold whose "
              "effect on scheduling was not traced",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[452A] modules={s['modules_ok']} deficit={s['deficit_tokens']} wmm={s['wmm_tokens']} "
          f"penal={s['penalization_tokens']} airtime={s['airtime_tokens']} "
          f"prio={s['prio_tokens']} BE={s['be_tokens']}/probe={s['modules_where_be_is_probe']} "
          f"rssi_th={s['rssi_threshold_tokens']} mc_air={s['mcast_airtime_limit_tokens']}")
    for r in ok:
        print(f"        {r['version']:<12} {r['bytes']:>7}B present={ {k: v for k, v in r['present'].items() if v} }")
        print(f"        {'':<12} symbols={r['priority_symbols'][:4]}")
    print(f"[452A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
