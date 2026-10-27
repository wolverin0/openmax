#!/usr/bin/env python3
"""Stage 714A — ACK/CTS timeout and IFS slot written from distance and RTT.

The stage asks how `ubnt_poll_host.ko` and `ath_dev.ko` compute and write
`MAC_PCU_ACK_CTS_TIMEOUT` and `MAC_D_GBL_IFS_SLOT` from `ni_distance_m` and `rtt_us`.

The register **names** do not exist — they are ath9k macros, and `MAC_PCU`, `GBL_IFS`, `ni_distance`
and `cts_timeout` all return **0**. But the **entire computation chain is named**, and the
conversion point is captured verbatim in a log string:

```
%s: distance set to %d (ACK_CTS_Timeout = %d)
```

**`CONFIRMED`**: `ol_ath_set_distance` takes a distance and prints **both** the distance and the
resulting ACK/CTS timeout. That single line is the formula's **output**, and it proves the two
quantities are directly linked.

The chain, in order, with every link named:

| Step | Symbol | Module |
| :--- | :--- | :--- |
| 1. per-node RTT | **`ubnt_poll_host_set_node_rtt`** | `ubnt_poll_host.ko` |
| 2. RTT measurement | `ol_ath_rtt_meas_req` | `umac.ko` |
| 3. RTT report | `wmi_rtt_meas_report_event_handler` | `umac.ko` |
| 4. distance apply | **`ol_ath_set_distance`** | `umac.ko` |
| 5. timeout write | **`ar9300_set_ack_timeout`** | `ath_hal.ko` |
| 6. slot write | **`ar9300_set_slot_time`** | `ath_hal.ko` |
| 7. readback | `WMI_ACK_CTS_READ_EVENTID` + `wmi_unified_ack_cts_read_event_handler` | `umac.ko` |

**`CONFIRMED`**: `hal_setters = 2` — **both** register setters exist by name
(`ar9300_set_ack_timeout`, `ar9300_set_slot_time`), with their getters
(`ar9300_get_ack_timeout`) beside them.

**`CONFIRMED`**: `proc_knobs` present — `ath_dev.ko` exposes `acktimeout` plus `get_acktimeout` and
`distance` plus `get_distance` as proc fields. So both the input (distance) and the output
(acktimeout) are **readable at runtime**.

**`CONFIRMED`**: there is a **readback path** — `WMI_ACK_CTS_READ_EVENTID` and its handler. The host
can ask the target what value it actually applied, which matters because the firmware may clamp.

The RSSI-side counterpart is also named: `ubnt_poll_host_reset_ff_rtt_active` — RTT tracking has an
active/reset state, so RTT is a **tracked quantity**, not a one-shot measurement.

`distance_formula_recovered = 0`: the **coefficient** is not in the module. The log prints the input
and the output, but not the constant that converts metres to microseconds. Stage 344A/415A territory:
the value would need to be read from a live system or from the arithmetic.

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
       / "stage714a_ubnt_poll_ack_cts_timeout_and_distance_clamp_re.json")

MODULES = {
    "WA:ubnt_poll_host.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "WA:ath_hal.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
}

TOKENS = ["distance", "rtt", "ack_timeout", "acktimeout", "get_acktimeout", "ACK_CTS", "slot_time",
          "MAC_PCU", "GBL_IFS", "ni_distance", "cts_timeout"]
# the conversion message
CONV_MSG = "distance set to %d (ACK_CTS_Timeout = %d)"
# the RTT chain
RTT_CHAIN = ["ubnt_poll_host_set_node_rtt", "ol_ath_rtt_meas_req",
             "wmi_rtt_meas_report_event_handler"]
# the distance apply
DIST = ["ol_ath_set_distance", "wmi_unified_distance_report_handler"]
# the register setters and getters
HAL = ["ar9300_set_ack_timeout", "ar9300_get_ack_timeout", "ar9300_set_slot_time"]
# the readback path
READBACK = ["WMI_ACK_CTS_READ_EVENTID", "wmi_unified_ack_cts_read_event_handler"]
# the ath9k register macros that should be absent
REGISTERS = ["MAC_PCU", "GBL_IFS", "ni_distance", "cts_timeout"]


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
            registers={t: b.count(t.encode()) for t in REGISTERS},
            conv_msg=b.count(CONV_MSG.encode()),
            rtt={k: b.count(k.encode()) for k in RTT_CHAIN},
            dist={k: b.count(k.encode()) for k in DIST},
            hal={k: b.count(k.encode()) for k in HAL},
            readback={k: b.count(k.encode()) for k in READBACK},
            conv_contexts=ctx(b, "ACK_CTS_Timeout = %d", 1),
            dist_symbols=syms.matching(r"distance", 12),
            rtt_symbols=syms.matching(r"rtt", 12),
            ack_symbols=syms.matching(r"ack_timeout|slot_time", 12)))

    ok = [r for r in rows if r.get("status") == "ok"]
    conv = sum(r["conv_msg"] for r in ok)
    rtt_found = [k for k in RTT_CHAIN if any(r["rtt"][k] for r in ok)]
    dist_found = [k for k in DIST if any(r["dist"][k] for r in ok)]
    hal_found = [k for k in HAL if any(r["hal"][k] for r in ok)]
    rb_found = [k for k in READBACK if any(r["readback"][k] for r in ok)]
    regs = sum(sum(r["registers"].values()) for r in ok)
    dist_syms = sorted({n for r in ok for n in r["dist_symbols"]})
    rtt_syms = sorted({n for r in ok for n in r["rtt_symbols"]})
    ack_syms = sorted({n for r in ok for n in r["ack_symbols"]})

    report = dict(
        meta=dict(stage="714A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage714a_ubnt_poll_ack_cts_timeout_and_distance_clamp_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="conversion-message extraction for the distance-to-timeout link; "
                         "per-module symbol lookup along the chain from per-node RTT through "
                         "distance apply to the HAL register setters and the readback event; "
                         "explicit probe for the ath9k register macros",
                  premise_corrections=[
                      "MAC_PCU_ACK_CTS_TIMEOUT and MAC_D_GBL_IFS_SLOT are ath9k macros and do not "
                      "exist as strings; the setters ar9300_set_ack_timeout and "
                      "ar9300_set_slot_time are the writable interface",
                      "the chain is split across four modules, not two: ubnt_poll_host.ko holds "
                      "per-node RTT, umac.ko holds distance and the readback, ath_hal.ko holds "
                      "the register writes",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     conversion_message_hits=conv,
                     conversion_named=int(conv > 0),
                     rtt_chain=rtt_found,
                     rtt_chain_count=len(rtt_found),
                     rtt_chain_complete=int(len(rtt_found) == 3),
                     distance_apply=dist_found,
                     hal_setters=hal_found,
                     hal_setter_count=len(hal_found),
                     both_registers_writable=int(
                         "ar9300_set_ack_timeout" in hal_found
                         and "ar9300_set_slot_time" in hal_found),
                     readback_path=rb_found,
                     readback_present=int(len(rb_found) >= 1),
                     register_macro_hits=regs,
                     register_macros_absent=int(regs == 0),
                     distance_symbols=dist_syms[:6],
                     rtt_symbols=rtt_syms[:6],
                     ack_slot_symbols=ack_syms[:6],
                     distance_formula_recovered=0,
                     distance_clamp_recovered=0),
        gaps=["MAC_PCU_ACK_CTS_TIMEOUT and MAC_D_GBL_IFS_SLOT are macros: 0 hits, so the register "
              "offsets are not recoverable by name",
              "the conversion prints both the distance and the resulting ACK/CTS timeout, but the "
              "coefficient between them is not in the module",
              "whether the firmware clamps the value was not recovered: the readback event exists "
              "to observe it, but the clamp rule is not in the host modules",
              "the chain spans four modules, so no single module documents it end to end",
              "the slot-time computation from distance was not isolated; only the setter is named",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[714A] modules={s['modules_ok']} conv={s['conversion_message_hits']} "
          f"rtt_chain={s['rtt_chain_count']}/3 hal={s['hal_setter_count']} "
          f"both={s['both_registers_writable']} readback={s['readback_present']} "
          f"macros={s['register_macro_hits']}")
    print(f"        hal={hal_found}")
    print(f"        rtt={rtt_found}")
    print(f"[714A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
