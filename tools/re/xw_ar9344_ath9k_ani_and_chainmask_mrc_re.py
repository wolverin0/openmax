#!/usr/bin/env python3
"""Stage 396A — XW AR9344 ANI, chainmask and the MRC / SIMO-TX path.

The stage names three modules on **XW/XM** and two registers plus one function:

  * `AR_PHY_MULTICHAIN_GAIN_CTL`
  * `AR_PHY_TIMING2`
  * `txchainmask` / `rxchainmask`, SIMO-TX with 2x2 MRC-RX
  * `ubnt_ewma_delegate_on`

Two premise corrections come out of the corpus before the analysis:

  * **there is no XM rootfs.** The M5 corpus holds `xw_614_rootfs` and `xw_636_rootfs`; no `xm_*`
    tree exists. The two data points are therefore XW 6.1.4 and XW 6.3.6.
  * **`AR_PHY_MULTICHAIN_GAIN_CTL` and `AR_PHY_TIMING2` are not strings.** They are macros on the
    ath9k side; the compiled module carries the register *values*, not the names. A name search
    returning zero is therefore expected and is **not** evidence that the registers are unused.

What the modules do carry, and what this tool measures:

  * the **chainmask vocabulary** — `txchainmask` and `rxchainmask` as real strings, which is how
    the SIMO-TX / MRC-RX configuration is exposed;
  * the **`ewma_delegate` / `delegate_on`** symbols in `ath_rate_atheros.ko`, which is the rate
    control delegation hook the stage asks about;
  * the **ANI** surface (`ANI`, `ani_`, `firstep`, `cycpwr`) so the noise-immunity path is not
    silently omitted.

`register_name_hits = 0` and `mrc_path_recovered = 0` are the honest outputs: the vocabulary is
recovered, the register semantics are not.

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
XW = REPO_ROOT / "artifacts" / "firmware_re_xw_m5"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage396a_xw_ar9344_ani_chainmask_mrc_re.json")

VERSIONS = {"XW.v6.1.4": "xw_614_rootfs", "XW.v6.3.6": "xw_636_rootfs"}
MODULES = ["ath_hal.ko", "ath_dev.ko", "ath_rate_atheros.ko", "ubnt_ewma_ht.ko"]

# registers the stage names: these are macros, not strings, and must be reported as absent
REGISTER_NAMES = ["AR_PHY_MULTICHAIN_GAIN_CTL", "MULTICHAIN_GAIN", "AR_PHY_TIMING2", "TIMING2"]
# the configuration vocabulary that IS present
CHAINMASK = ["txchainmask", "rxchainmask", "chainmask"]
EWMA = ["ewma_delegate", "delegate_on", "ubnt_ewma_delegate_on"]
ANI = ["ANI", "ani_", "firstep", "cycpwr", "MRC", "SIMO"]


def ctx(b: bytes, tok: str, n: int = 3, w: int = 70) -> list[str]:
    out: list[str] = []
    needle = tok.encode()
    i = b.find(needle)
    while i >= 0 and len(out) < n:
        out.append("".join(chr(c) if 32 <= c < 127 else "."
                           for c in b[max(0, i - w):i + len(needle) + w]))
        i = b.find(needle, i + 1)
    return out


class Syms:
    """Just enough ELF to list defined symbol names."""

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
        rx = re.compile(pattern, re.I)
        return sorted({n for n in self.names if rx.search(n)})[:cap]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    for ver, root in VERSIONS.items():
        base = XW / root / "lib/modules/2.6.32.71"
        for name in MODULES:
            p = base / name
            label = f"{ver}:{name}"
            if not p.exists():
                rows.append(dict(module=label, status="absent"))
                continue
            b = p.read_bytes()
            syms = Syms(p)
            proven = set(syms.names)
            rows.append(dict(
                module=label, status="ok", bytes=len(b),
                sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(proven),
                register_names={t: b.count(t.encode()) for t in REGISTER_NAMES},
                chainmask={t: b.count(t.encode()) for t in CHAINMASK},
                ewma={t: b.count(t.encode()) for t in EWMA},
                ani={t: b.count(t.encode()) for t in ANI},
                chainmask_contexts={t: ctx(b, t) for t in CHAINMASK if b.count(t.encode())},
                ewma_symbols=syms.matching(r"ewma|delegate", 24),
                chainmask_symbols=syms.matching(r"chainmask|txchain|rxchain", 24),
                ani_symbols=syms.matching(r"^ani|_ani_|-ani", 24)))

    ok = [r for r in rows if r.get("status") == "ok"]
    xm_roots = sorted(p.name for p in XW.iterdir()
                      if p.is_dir() and p.name.startswith("xm"))
    reg_hits = sum(sum(r["register_names"].values()) for r in ok)
    chain_hits = sum(sum(r["chainmask"].values()) for r in ok)
    ewma_hits = sum(sum(r["ewma"].values()) for r in ok)
    exact = sorted({n for r in ok for n in r["ewma_symbols"]
                    if n == "ubnt_ewma_delegate_on"})
    delegate_syms = sorted({n for r in ok for n in r["ewma_symbols"]})

    report = dict(
        meta=dict(stage="396A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/xw_ar9344_ath9k_ani_and_chainmask_mrc_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  premise_corrections=[
                      "there is no XM rootfs: the M5 corpus holds xw_614_rootfs and "
                      "xw_636_rootfs, so the two data points are XW 6.1.4 and XW 6.3.6",
                      "AR_PHY_MULTICHAIN_GAIN_CTL and AR_PHY_TIMING2 are compile-time macros on "
                      "the ath9k side and are not strings in any compiled module; their absence "
                      "from a string search is expected and is not evidence of disuse",
                  ],
                  radio_safety="static only"),
        xm_roots_found=xm_roots,
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     versions=len(VERSIONS),
                     xm_root_present=bool(xm_roots),
                     register_name_hits=reg_hits,
                     chainmask_hits=chain_hits,
                     ewma_hits=ewma_hits,
                     modules_with_txchainmask=sum(1 for r in ok if r["chainmask"]["txchainmask"]),
                     modules_with_rxchainmask=sum(1 for r in ok if r["chainmask"]["rxchainmask"]),
                     modules_with_ewma_symbols=sum(1 for r in ok if r["ewma_symbols"]),
                     exact_ubnt_ewma_delegate_on=len(exact),
                     delegate_symbols=delegate_syms,
                     ani_symbols=sorted({n for r in ok for n in r["ani_symbols"]})[:12],
                     register_names_recovered=0,
                     mrc_path_recovered=0),
        gaps=["AR_PHY_MULTICHAIN_GAIN_CTL and AR_PHY_TIMING2 do not exist as strings, so neither "
              "register offset nor bit layout was recovered",
              "no XM rootfs exists, so the XM half of the stage has no data",
              "txchainmask/rxchainmask are recovered as names; the 2x2-MRC-RX and 1x2 STBC/CDD "
              "behaviour they select was not traced",
              "the ewma delegate hook is recovered as a symbol family; the delegation condition "
              "was not decoded",
              "no register write site was bound to any ANI or chainmask parameter",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[396A] modules={s['modules_ok']} xm={s['xm_root_present']} "
          f"reg_names={s['register_name_hits']} chainmask={s['chainmask_hits']} "
          f"ewma={s['ewma_hits']} txcm={s['modules_with_txchainmask']} "
          f"exact={s['exact_ubnt_ewma_delegate_on']}")
    for r in ok:
        print(f"        {r['module']:<28} {r['bytes']:>7}B "
              f"cm={ {k: v for k, v in r['chainmask'].items() if v} } "
              f"ewma_syms={len(r['ewma_symbols'])}")
    print(f"[396A] delegate symbols: {delegate_syms[:6]}")
    print(f"[396A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
