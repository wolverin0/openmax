#!/usr/bin/env python3
"""Stage 589A — peer phymode, VHT rates, SGI masks and retry-schedule descriptors.

The stage names four things across `umac.ko`, `ath_dev.ko` and `ubnt_poll_host.ko`:

  * `WMI_PEER_ASSOC_CMDID` **peer_phymode**;
  * **peer_vht_rates**;
  * **Short Guard Interval (SGI) masks**;
  * **retry-schedule descriptors**.

The first structural result is a **location correction**: the entire peer-rate vocabulary lives in
`umac.ko` and **nowhere else**. `ath_dev.ko` and `ubnt_poll_host.ko` return **zero** for every token
in the set. That is not a sampling artefact — it is the same for both AC images.

Inside `umac.ko` the mechanism is fully named:

```
wlan_get_current_phymode        wlan_set_desired_phymode
ieee80211_update_ht_vht_phymode wlan_channel_phymode
ieee80211_phymode_name          ieee80211_phymode_to_name
```

```
ieee80211_set_vht_rates         ieee80211_setup_vht_rates
ol_ath_vht_rate_setup           rate_init_peer_ratectxt
```

```
_RATE_GetSGIFlag                _RATE_SetSGIMasks
g_default_sgi_per_thresh
```

and both WMI command names are present in the name table:

```
...WMI_PEER_ASSOC_CMDID...      ...WMI_PEER_RATE_RETRY_SCHED_CMDID...
```

Two log lines make the descriptor **observable**, which is the most useful part of this stage:

```
RATE: ChainMask %d, phymode %d, ni_flags 0x%08x, vht_mcs_set 0x%04x, ht_mcs_set 0x%04x
SGI counts (0..9): …   NSS counts: 1x1 %u, 2x2 %u, 3x3 %u, 4x4 %u
```

The first carries **chainmask, phymode, vht_mcs_set and ht_mcs_set in one line** — that is the
per-peer rate descriptor rendered as text. The second prints **SGI counts per MCS 0..9** plus an NSS
histogram, so the SGI mask can be read off a live system.

`_RATE_SetSGIMasks` plus `g_default_sgi_per_thresh` is the write side: SGI eligibility is a **mask
per rate**, seeded from a per-threshold default, not a single boolean.

`retry_descriptor_values_recovered = 0`: `WMI_PEER_RATE_RETRY_SCHED_CMDID` is named but Stage 372A
already showed `series_bw` is absent, so the 4-series descriptor cannot be laid out from strings.

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
       / "stage589a_qca988x_wmi_peer_rate_retry_and_sgi_re.json")

MODULES = {
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "WA:ubnt_poll_host.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XC:ubnt_poll_host.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
}

TOKENS = ["PEER_ASSOC", "phymode", "vht_rates", "SGI", "sgi", "PEER_RATE_RETRY",
          "vht", "VHT"]
# the WMI command names this stage is about
WMI = ["WMI_PEER_ASSOC_CMDID", "WMI_PEER_RATE_RETRY_SCHED_CMDID"]
# the SGI machinery
SGI = ["_RATE_SetSGIMasks", "_RATE_GetSGIFlag", "g_default_sgi_per_thresh"]
# the log lines that make the descriptor observable
RATE_LINE = "RATE: ChainMask %d, phymode %d"
SGI_LINE = "SGI counts (0..9)"


def ctx(b: bytes, tok: str, n: int = 2, w: int = 70) -> list[str]:
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
            rows.append(dict(module=label, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        rows.append(dict(
            module=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            tokens={t: b.count(t.encode()) for t in TOKENS},
            wmi={k: b.count(k.encode()) for k in WMI},
            sgi={k: b.count(k.encode()) for k in SGI},
            wmi_names=[k for k in WMI if b.count(k.encode())],
            sgi_symbols=[k for k in SGI if b.count(k.encode())],
            phymode_symbols=syms.matching(r"phymode", 16),
            vht_symbols=syms.matching(r"vht_rate|vht_mcs", 16),
            rate_symbols=syms.matching(r"rate_init|peer_rate|sgi", 16),
            rate_line=ctx(b, RATE_LINE, 1),
            sgi_line=ctx(b, SGI_LINE, 1)))

    ok = [r for r in rows if r.get("status") == "ok"]
    total_tokens = {r["module"]: sum(r["tokens"].values()) for r in ok}
    umac = [r for r in ok if r["module"].endswith("umac.ko")]
    others = [r for r in ok if not r["module"].endswith("umac.ko")]
    others_zero = sum(1 for r in others if sum(r["tokens"].values()) == 0)
    wmi_found = sorted({k for r in ok for k in r["wmi_names"]})
    sgi_found = sorted({k for r in ok for k in r["sgi_symbols"]})
    phymode = sorted({n for r in ok for n in r["phymode_symbols"]})
    vht = sorted({n for r in ok for n in r["vht_symbols"]})
    rate = sorted({n for r in ok for n in r["rate_symbols"]})
    rate_line = any(r["rate_line"] for r in ok)
    sgi_line = any(r["sgi_line"] for r in ok)

    report = dict(
        meta=dict(stage="589A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage589a_qca988x_wmi_peer_rate_retry_and_sgi_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census across six modules on two lines; defined-symbol lookup "
                         "for the phymode, VHT-rate and SGI-mask families; log-line extraction for "
                         "the peer rate descriptor and the SGI count table",
                  premise_corrections=[
                      "the peer-rate vocabulary is umac.ko only: ath_dev.ko and "
                      "ubnt_poll_host.ko return zero for every token in the set",
                      "SGI is a per-rate mask (_RATE_SetSGIMasks, g_default_sgi_per_thresh), not "
                      "a single enable bit",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     token_totals=total_tokens,
                     umac_modules=len(umac),
                     non_umac_modules=len(others),
                     non_umac_modules_with_zero_tokens=others_zero,
                     vocab_is_umac_only=int(others_zero == len(others) and len(others) > 0),
                     wmi_command_names=wmi_found,
                     wmi_command_count=len(wmi_found),
                     sgi_machinery=sgi_found,
                     sgi_machinery_count=len(sgi_found),
                     sgi_is_per_rate_mask=int("_RATE_SetSGIMasks" in sgi_found),
                     sgi_default_present=int("g_default_sgi_per_thresh" in sgi_found),
                     phymode_symbol_count=len(phymode),
                     phymode_symbols=phymode[:8],
                     vht_rate_symbol_count=len(vht),
                     vht_rate_symbols=vht[:6],
                     peer_ratectxt_present=int(any("peer_ratectxt" in n for n in rate)),
                     rate_descriptor_line_present=int(rate_line),
                     sgi_count_line_present=int(sgi_line),
                     sgi_mask_values_recovered=0,
                     retry_descriptor_values_recovered=0),
        gaps=["ath_dev.ko and ubnt_poll_host.ko carry none of the peer-rate vocabulary, so the "
              "descriptor is built entirely in the UMAC",
              "the SGI mask bit layout is not recovered: the setter and the default threshold are "
              "named, the per-rate bitmap is runtime data",
              "WMI_PEER_RATE_RETRY_SCHED_CMDID is named but Stage 372A showed series_bw is absent, "
              "so the 4-series descriptor cannot be laid out",
              "the phymode enumeration values are not recovered; only the accessors are named",
              "the VHT rate tables are per-peer runtime data built by ieee80211_setup_vht_rates",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[589A] modules={s['modules_ok']} umac_only={s['vocab_is_umac_only']} "
          f"wmi={s['wmi_command_names']} sgi={s['sgi_machinery_count']} "
          f"per_rate={s['sgi_is_per_rate_mask']} phymode={s['phymode_symbol_count']} "
          f"rate_line={s['rate_descriptor_line_present']} "
          f"sgi_line={s['sgi_count_line_present']}")
    print(f"        tokens={total_tokens}")
    print(f"[589A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
