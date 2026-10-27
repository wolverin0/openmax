#!/usr/bin/env python3
"""Stage 486A — AD9361 FastLock profiles, TX quadrature calibration and split-frequency LO.

The stage names four things in `ame_core.ko` and `eab_driver.ko`:

  * **AD9361 FastLock** synthesizer profile registers;
  * **TX quadrature calibration** tables;
  * **split-frequency LO** programming;
  * the module pair.

`eab_driver.ko` is **absent** (eighth independent confirmation). In `ame_core.ko` the RFIC is
present, but only one of the three subsystems is:

| Token | Hits | Verdict |
| :--- | :-: | :--- |
| **`ad9361`** | **2** | real, but only in error/reset paths |
| **`dcxo`** | **43** | **the dominant RF subsystem** |
| `fastlock`, `fast_lock` | **0** | absent |
| `synth` | **0** | absent |
| `quad` | **0** | absent |
| `calib` | **0** | absent |
| `qec` | **0** | absent |
| `tx_lo`, `pll` | **0** | absent |
| `rx_lo` | 2 | **substring of `tpc_rx_log`** |
| `split` | 1 | **substring of `c_string_smart_split`** |

So the stage's three RF mechanisms are **absent by name**, and the two tokens that appear to
support them are **substring coincidences** — the same failure mode as `BE` in `PROBE` (452A),
`LQ` in a base64 table (438A) and `moder` in "modern" (460A). This is the fourth instance.

What is real is **DCXO**: the digitally controlled crystal oscillator, with a full named
subsystem — `ame_bbp_op_dcxo`, `ame_bbp_rt_keep_dcxo_sync`, `bbp_rf_dcxo_adj`,
`fty_rf_dcxo_sync_start` / `_track` / `_info_show`, `fty_rf_tcxo_cal_variation`.

**`INFERRED`**: on this hardware the frequency reference is disciplined through DCXO, not through
AD9361 FastLock profiles. That is consistent with an LTE-style SDR baseband that must hold an
absolute frequency reference across a TDMA frame.

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
LTU = (REPO_ROOT / "artifacts/firmware_re_xc_ltu/ltu_extracted/afltu_2.4.2"
       / "rootfs_extracted/lib/modules/3.14.65")
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage486a_ltu_ad9361_fastlock_and_cal_table_re.json")

# the RFIC and its named subsystems
RFIC = ["ad9361", "AD9361"]
# mechanisms the stage names: expected absent
MECHANISM = ["fastlock", "fast_lock", "synth", "quad", "calib", "qec", "tx_lo", "pll"]
# the subsystem that is actually present
DCXO = ["dcxo", "tcxo"]
# tokens that look like LO / split-frequency and are substrings
AMBIGUOUS = {"rx_lo": "tpc_rx_log", "split": "smart_split"}


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

    eab = len([p for p in (REPO_ROOT / "artifacts").rglob("eab_driver.ko")])
    p = LTU / "ame_core.ko"
    row: dict[str, Any] = dict(module="ame_core.ko", status="absent")
    if p.exists():
        b = p.read_bytes()
        syms = Syms(p)
        amb = {}
        for tok, inner in AMBIGUOUS.items():
            cs = ctx(b, tok)
            amb[tok] = dict(count=b.count(tok.encode()), contexts=cs,
                            all_coincidence=bool(cs) and all(inner in c for c in cs))
        row = dict(module="ame_core.ko", status="ok", bytes=len(b),
                   sha256=hashlib.sha256(b).hexdigest(),
                   defined_symbols=len(syms.names),
                   rfic={t: b.count(t.encode()) for t in RFIC},
                   mechanism={t: b.count(t.encode()) for t in MECHANISM},
                   dcxo={t: b.count(t.encode()) for t in DCXO},
                   ambiguous=amb,
                   ad9361_symbols=syms.matching(r"ad9361", 20),
                   ad9361_names=sorted({m.decode() for m in
                                        re.findall(rb"ame_ad9361_[a-z0-9_]+", b)}),
                   dcxo_symbols=syms.matching(r"dcxo|tcxo", 30),
                   dcxo_names=sorted({m.decode() for m in
                                      re.findall(rb"[a-z0-9_]*(?:dcxo|tcxo)[a-z0-9_]*", b)}),
                   rf_symbols=syms.matching(r"rf_(tune|cal|dcxo|err|reset)", 20))

    mech = row.get("mechanism", {})
    dcxo = row.get("dcxo", {})
    amb = row.get("ambiguous", {})
    ad_syms = row.get("ad9361_symbols", [])
    dcxo_syms = row.get("dcxo_symbols", [])

    report = dict(
        meta=dict(stage="486A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage486a_ltu_ad9361_fastlock_and_cal_table_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census of the AD9361 mechanism vocabulary; context classification "
                         "of the rx_lo and split look-alikes; defined-symbol lookup for the "
                         "ad9361, dcxo and rf_ families",
                  premise_corrections=[
                      "eab_driver.ko is absent, so ame_core.ko is the only readable target",
                      "rx_lo and split are substrings of tpc_rx_log and c_string_smart_split, not "
                      "LO or split-frequency vocabulary",
                  ],
                  radio_safety="static only"),
        absence=dict(eab_driver=eab),
        modules=[row],
        summary=dict(eab_driver_present=eab > 0,
                     module_ok=int(row.get("status") == "ok"),
                     ad9361_tokens=sum(row.get("rfic", {}).values()),
                     ad9361_symbol_count=len(ad_syms),
                     ad9361_symbols=ad_syms,
                     ad9361_names=row.get("ad9361_names", []),
                     ad9361_name_count=len(row.get("ad9361_names", [])),
                     dcxo_tokens=sum(dcxo.values()),
                     dcxo_symbol_count=len(dcxo_syms),
                     dcxo_symbols=dcxo_syms[:12],
                     dcxo_name_count=len(row.get("dcxo_names", [])),
                     dcxo_names=row.get("dcxo_names", [])[:24],
                     fastlock_tokens=mech.get("fastlock", 0) + mech.get("fast_lock", 0),
                     synth_tokens=mech.get("synth", 0),
                     quad_tokens=mech.get("quad", 0),
                     calib_tokens=mech.get("calib", 0),
                     qec_tokens=mech.get("qec", 0),
                     tx_lo_tokens=mech.get("tx_lo", 0),
                     pll_tokens=mech.get("pll", 0),
                     rx_lo_is_coincidence=int(amb.get("rx_lo", {}).get("all_coincidence", False)),
                     split_is_coincidence=int(amb.get("split", {}).get("all_coincidence", False)),
                     dcxo_subsystem_named=int(len(dcxo_syms) > 0),
                     fastlock_profile_recovered=0,
                     tx_quad_cal_table_recovered=0,
                     split_frequency_lo_recovered=0),
        gaps=["eab_driver.ko is absent, so the stage's second module has no bytes",
              "fastlock, fast_lock, synth, quad, calib, qec, tx_lo and pll all have 0 hits: no "
              "FastLock profile register set and no TX quadrature calibration table was found",
              "rx_lo is a substring of tpc_rx_log (two transmit-power log fields), and split is a "
              "substring of c_string_smart_split: neither is LO programming",
              "ad9361 appears in only two symbols, both error/reset (set_rf_err_skip, "
              "set_rf_reset_ongoing); the RFIC is named, its synthesis API is not",
              "the DCXO subsystem is the real frequency-reference surface, with 43 tokens and a "
              "named sync/adj/track family, but its conversion table was not recovered",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[486A] eab={s['eab_driver_present']} ok={s['module_ok']} "
          f"ad9361={s['ad9361_tokens']}({s['ad9361_symbol_count']}sym) "
          f"dcxo={s['dcxo_tokens']}({s['dcxo_symbol_count']}sym) "
          f"fastlock={s['fastlock_tokens']} synth={s['synth_tokens']} "
          f"quad={s['quad_tokens']} calib={s['calib_tokens']} "
          f"rx_lo_sub={s['rx_lo_is_coincidence']} split_sub={s['split_is_coincidence']}")
    print(f"        ad9361_syms={s['ad9361_symbols']} names={s['ad9361_names']}")
    print(f"        dcxo_syms={s['dcxo_symbols'][:6]}")
    print(f"[486A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
