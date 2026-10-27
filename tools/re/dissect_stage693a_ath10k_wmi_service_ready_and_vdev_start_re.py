#!/usr/bin/env python3
"""Stage 693A — WMI service-ready, vdev start/up, and phymode negotiation.

The stage asks for three WMI identifiers and the phymode negotiation behind them:

  * `WMI_SERVICE_READY_EVENTID`
  * `WMI_VDEV_START_REQUEST_CMDID`
  * `WMI_VDEV_UP_CMDID`

`ath10k_core.ko` is **absent** (0 files, fifth confirmation), so the ath10k side cannot be read.
The **vendor `umac.ko` name table contains all three**, plus three neighbours the stage does not name
and which matter for the sequence:

```
WMI_SERVICE_READY_EVENTID          WMI_VDEV_CREATE_CMDID
WMI_VDEV_START_REQUEST_CMDID       WMI_VDEV_RESTART_REQUEST_CMDID
WMI_VDEV_UP_CMDID                  WMI_VDEV_START_RESP_EVENTID
WMI_VDEV_STOPPED_EVENTID
```

**`CONFIRMED`**: the vdev lifecycle is a **paired request/response** flow — start-request answered by
start-response, and up/stopped as separate events. `RESTART_REQUEST` is a distinct command, which is
what a channel switch (Stage 485A's CSA) needs.

The host-side send functions are named per direction:

```
ol_ath_service_ready_event        wmi_service_ready_event_rx
wmi_ready_event_rx                wmi_unified_event_rx
wmi_unified_vdev_start_send       wmi_unified_vdev_start_chan_send
wmi_unified_vdev_restart_send     wmi_unified_vdev_up_send
```

Note `vdev_start_chan_send` — a **channel-specific** start variant beside the generic one.

**The phymode enumeration is explicit and directional:**

```
11ACVHT20   11ACVHT40PLUS   11ACVHT40MINUS   11ACVHT40   11ACVHT80
```

**`CONFIRMED`**: **VHT40 has PLUS and MINUS variants.** That is the detail that makes bandwidth
negotiation real: a 40 MHz channel is above or below its primary 20 MHz, and the two cases are
separate enum values, not a flag.

The capability name table carries the same set beside CDD, STBC and TXBF:

```
CDD  .STBC.TXBF..CCK  .OFDM .HT20 .HT40 .VHT20.VHT40.VHT80.HTDUP
```

`resource_limits_recovered = 0`: the target's actual limits (peer count, vdev count, ring depth) are
carried in the service-ready **payload**, which is runtime data — the module names the message, not
its content.

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
       / "stage693a_ath10k_wmi_service_ready_and_vdev_start_re.json")

MODULES = {
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
}

# the three identifiers the stage names, plus the neighbours that complete the sequence
WMI = ["WMI_SERVICE_READY_EVENTID", "WMI_VDEV_START_REQUEST_CMDID", "WMI_VDEV_UP_CMDID",
       "WMI_VDEV_RESTART_REQUEST_CMDID", "WMI_VDEV_START_RESP_EVENTID",
       "WMI_VDEV_STOPPED_EVENTID", "WMI_VDEV_CREATE_CMDID"]
# the host-side send and receive entry points
PATH = ["ol_ath_service_ready_event", "wmi_service_ready_event_rx", "wmi_ready_event_rx",
        "wmi_unified_vdev_start_send", "wmi_unified_vdev_start_chan_send",
        "wmi_unified_vdev_restart_send", "wmi_unified_vdev_up_send"]
# the phymode enumeration
PHYMODE = ["11ACVHT20", "11ACVHT40PLUS", "11ACVHT40MINUS", "11ACVHT40", "11ACVHT80"]
# the capability name table neighbours
CAP = ["HT20", "HT40", "VHT20", "VHT40", "VHT80", "HTDUP"]


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
            wmi={k: b.count(k.encode()) for k in WMI},
            path_syms={k: b.count(k.encode()) for k in PATH},
            phymode={k: b.count(k.encode()) for k in PHYMODE},
            cap={k: b.count(k.encode()) for k in CAP},
            wmi_names=[k for k in WMI if b.count(k.encode())],
            path_found=[k for k in PATH if b.count(k.encode())],
            phymode_found=[k for k in PHYMODE if b.count(k.encode())],
            send_symbols=syms.matching(r"service_ready|vdev_start|vdev_up|vdev_restart", 20),
            ready_contexts=ctx(b, "WMI_SERVICE_READY", 1),
            vht_contexts=ctx(b, "11ACVHT", 1)))

    ok = [r for r in rows if r.get("status") == "ok"]
    names = sorted({k for r in ok for k in r["wmi_names"]})
    paths = sorted({k for r in ok for k in r["path_found"]})
    phy = sorted({k for r in ok for k in r["phymode_found"]})
    syms_found = sorted({n for r in ok for n in r["send_symbols"]})
    vht40_dir = int(any("PLUS" in p for p in phy) and any("MINUS" in p for p in phy))
    required = {"WMI_SERVICE_READY_EVENTID", "WMI_VDEV_START_REQUEST_CMDID",
                "WMI_VDEV_UP_CMDID"}

    report = dict(
        meta=dict(stage="693A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage693a_ath10k_wmi_service_ready_and_vdev_start_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="WMI name-table extraction for the three identifiers and their "
                         "neighbours; host-side send/receive symbol lookup; phymode enumeration "
                         "extraction from the ioctl name strings",
                  premise_corrections=[
                      "ath10k_core.ko is absent, so the ath10k side of the WMI sequence cannot be "
                      "read; the vendor umac.ko carries all three identifiers",
                      "the phymode enum has a directional 40 MHz pair (11ACVHT40PLUS and "
                      "11ACVHT40MINUS), not a single VHT40 value",
                  ],
                  radio_safety="static only"),
        ath10k_modules=ath10k,
        modules=rows,
        summary=dict(ath10k_core_present=ath10k > 0,
                     modules_ok=len(ok),
                     wmi_names=names,
                     wmi_name_count=len(names),
                     required_three_present=int(required <= set(names)),
                     vdev_sequence_complete=int(
                         "WMI_VDEV_START_RESP_EVENTID" in names
                         and "WMI_VDEV_STOPPED_EVENTID" in names),
                     restart_variant_present=int("WMI_VDEV_RESTART_REQUEST_CMDID" in names),
                     host_path_symbols=paths,
                     host_path_count=len(paths),
                     channel_start_variant=int("wmi_unified_vdev_start_chan_send" in paths),
                     phymode_strings=phy,
                     phymode_count=len(phy),
                     vht40_directional=vht40_dir,
                     capability_table_neighbours=[k for k in CAP
                                                  if any(r["cap"][k] for r in ok)],
                     send_symbol_count=len(syms_found),
                     resource_limits_recovered=0,
                     service_ready_payload_recovered=0),
        gaps=["ath10k_core.ko is absent, so the ath10k WMI implementation cannot be compared to "
              "the vendor one",
              "the three identifiers are present as strings but their CMDID values were not "
              "recovered; no numeric id table was located",
              "the target resource limits the stage asks about are carried in the service-ready "
              "payload, which is runtime data; the module names the message, not its content",
              "the phymode enum is recovered from ioctl name strings, not from the WMI payload "
              "field, so the wire encoding of the phymode remains unknown",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[693A] ath10k={s['ath10k_core_present']} modules={s['modules_ok']} "
          f"wmi={s['wmi_name_count']} req3={s['required_three_present']} "
          f"seq={s['vdev_sequence_complete']} path={s['host_path_count']} "
          f"phy={s['phymode_count']} vht40dir={s['vht40_directional']}")
    print(f"        wmi={names}")
    print(f"        phy={phy}")
    print(f"[693A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
