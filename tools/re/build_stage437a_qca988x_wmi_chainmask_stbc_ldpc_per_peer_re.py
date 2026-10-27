#!/usr/bin/env python3
"""Stage 437A — chainmask, fixed rate, and per-peer STBC / LDPC / NSS indexing.

The stage names four things:

  * `WMI_PDEV_PARAM_TX_CHAIN_MASK` (**0x43**)
  * `WMI_PDEV_PARAM_RX_CHAIN_MASK` (**0x44**)
  * `WMI_VDEV_PARAM_FIXED_RATE`
  * per-peer STBC / LDPC / NSS indexing, correlated with **FMX-DISC-40** (`nss=0` is 1x1
    VHT-NSS1, `nss=1` is 2x2 VHT-NSS2)

Two of the three sources do not exist: `firmware-2.bin` / `firmware-5.bin` (**0 files**, Stage
423A) and `ath10k_core.ko` (**0 files**, Stages 371A / 395A). The vendor `umac.ko` and `ath_dev.ko`
are analysed instead.

What the strings show, and what they refuse to show:

  * **the WMI parameter names are macros.** `PDEV_PARAM`, `VDEV_PARAM`, `TX_CHAIN_MASK`,
    `RX_CHAIN_MASK`, `CHAIN_MASK`, `FIXED_RATE` and `spatial` are all **absent** as strings. The
    numeric ids 0x43 / 0x44 are enum values compiled to immediates; a string search cannot see
    them and this tool does not pretend otherwise.
  * **the per-peer knobs are real and readable.** `nss`, `stbc` and `ldpc` exist, and they sit in a
    proc/sysctl table as `nss … get_nss … ldpc … get_ldpc … vhtmcs … get_vhtmcs` — a name plus a
    getter per field.
  * **`NSS greater than 3!` is a real bounds check.** It caps the value at **3**. That is the only
    hard numeric fact about NSS indexing in the corpus, and it is analysed carefully below because
    it does **not** settle FMX-DISC-40 on its own.

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
       / "stage437a_qca988x_wmi_chainmask_stbc_ldpc_per_peer_re.json")

MODULES = {
    "WA.v8.7.25:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC.v8.7.25:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA.v8.7.25:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC.v8.7.25:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
}

# WMI parameter identifiers: macros, expected absent
WMI_NAMES = ["PDEV_PARAM", "VDEV_PARAM", "TX_CHAIN_MASK", "RX_CHAIN_MASK", "CHAIN_MASK",
             "FIXED_RATE", "WMI_PDEV_PARAM", "WMI_VDEV_PARAM", "spatial"]
# per-peer rate vocabulary: expected present
PEER = ["nss", "NSS", "stbc", "ldpc", "vhtmcs", "1x1", "2x2"]
# the getters that make a knob readable at runtime
GETTERS = ["get_nss", "get_ldpc", "get_vhtmcs", "get_stbc"]
# the bounds-check string found in umac.ko
NSS_BOUND = "NSS greater than 3"

WMI_IDS = {"TX_CHAIN_MASK": 0x43, "RX_CHAIN_MASK": 0x44}


def ctx(b: bytes, tok: str, n: int = 3, w: int = 74) -> list[str]:
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

    named = {n: len([p for p in (REPO_ROOT / "artifacts").rglob(n) if p.is_file()])
             for n in ("firmware-2.bin", "firmware-5.bin", "ath10k_core.ko")}

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        rows.append(dict(
            module=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(),
            wmi_names={t: b.count(t.encode()) for t in WMI_NAMES},
            peer={t: b.count(t.encode()) for t in PEER},
            getters={t: b.count(t.encode()) for t in GETTERS},
            nss_bound_present=bool(b.count(NSS_BOUND.encode())),
            nss_bound_context=ctx(b, NSS_BOUND, 2),
            peer_contexts={t: ctx(b, t) for t in ("nss", "ldpc", "1x1", "2x2")
                           if b.count(t.encode())},
            peer_symbols=syms.matching(r"nss|stbc|ldpc|chainmask|fixed_rate", 24)))

    ok = [r for r in rows if r.get("status") == "ok"]
    umac = [r for r in ok if r["module"].endswith("umac.ko")]
    wmi_total = sum(sum(r["wmi_names"].values()) for r in ok)
    nss = sum(r["peer"]["NSS"] for r in ok)
    stbc = sum(r["peer"]["stbc"] for r in ok)
    ldpc = sum(r["peer"]["ldpc"] for r in ok)
    getter_total = sum(sum(r["getters"].values()) for r in ok)
    bound = sum(1 for r in ok if r["nss_bound_present"])
    one_x_one = sum(r["peer"]["1x1"] for r in ok)
    two_x_two = sum(r["peer"]["2x2"] for r in ok)
    symbols = sorted({n for r in ok for n in r["peer_symbols"]})

    report = dict(
        meta=dict(stage="437A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage437a_qca988x_wmi_chainmask_stbc_ldpc_per_peer_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no firmware loaded, no module loaded, "
                        "no radio contacted",
                  method="string sweep for the WMI parameter identifiers and the per-peer rate "
                         "vocabulary; bounds-check string extraction; proc/getter table "
                         "detection; defined-symbol lookup for nss/stbc/ldpc/chainmask",
                  wmi_ids={k: f"0x{v:02x}" for k, v in WMI_IDS.items()},
                  premise_corrections=[
                      "firmware-2.bin and firmware-5.bin are absent (0 files), so the firmware "
                      "side of the stage cannot be read",
                      "ath10k_core.ko is absent (0 files); the vendor umac.ko and ath_dev.ko are "
                      "used instead, as in Stages 371A and 395A",
                  ],
                  radio_safety="static only"),
        named_files=named,
        modules=rows,
        summary=dict(named_files_present=sum(named.values()),
                     modules_ok=len(ok),
                     wmi_name_hits=wmi_total,
                     wmi_names_absent=wmi_total == 0,
                     nss_hits=nss, stbc_hits=stbc, ldpc_hits=ldpc,
                     getter_hits=getter_total,
                     modules_with_getters=sum(1 for r in ok
                                              if any(r["getters"].values())),
                     nss_bound_modules=bound,
                     nss_bound_value=3,
                     one_x_one_strings=one_x_one,
                     two_x_two_strings=two_x_two,
                     peer_symbols=symbols[:10],
                     disc40_verdict=("consistent with 0-based indexing, not proven"
                                     if bound and one_x_one and two_x_two
                                     else "not assessable"),
                     per_peer_table_recovered=0,
                     wmi_id_to_name_map=0),
        gaps=["WMI_PDEV_PARAM_TX_CHAIN_MASK, WMI_PDEV_PARAM_RX_CHAIN_MASK and "
              "WMI_VDEV_PARAM_FIXED_RATE are enum macros; none exists as a string, so 0x43 and "
              "0x44 were not bound to any handler",
              "firmware-2.bin and firmware-5.bin are absent, so the firmware side of the NSS "
              "indexing cannot be checked at all",
              "ath10k_core.ko is absent; only the vendor stack was read",
              "`NSS greater than 3!` bounds the value at 3 but does not settle 0-based versus "
              "1-based indexing: on a 3x3 part a 0-based reading would allow a fourth stream",
              "no per-peer STBC/LDPC/NSS struct was laid out; the fields are named, not ordered",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[437A] named={named} modules={s['modules_ok']} wmi_names={s['wmi_name_hits']} "
          f"nss={s['nss_hits']} stbc={s['stbc_hits']} ldpc={s['ldpc_hits']} "
          f"getters={s['getter_hits']} bound={s['nss_bound_modules']} "
          f"1x1={s['one_x_one_strings']} 2x2={s['two_x_two_strings']}")
    print(f"        disc40: {s['disc40_verdict']}")
    for m in ok:
        print(f"        {m['module']:<24} {m['bytes']:>7}B peer={ {k: v for k, v in m['peer'].items() if v} }")
    print(f"[437A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
