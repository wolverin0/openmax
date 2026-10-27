#!/usr/bin/env python3
"""Stage 615A — TxBF, sounding, STBC and LDPC capability and knobs.

The stage names four things across `umac.ko`, `ath_dev.ko` and `ath_hal.ko`:

  * Transmit Beamforming (**TxBF**, SU-BF, sounding);
  * **STBC**;
  * **LDPC** capability;
  * the WMI / proc knobs for them.

Three results shape the answer.

**1. `TXBF` exists, but as capability text and per-rate-group power, not as a beamforming engine.**
The token appears in a **capability name table** alongside its neighbours:

```
CDD  .STBC.TXBF..CCK  .OFDM .HT20 .HT40 .VHT20.VHT40.VHT80.HTDUP
```

and in a **runtime rejection** message `%s : TXBF not supported`, plus per-rate-group power limits
`MaxRegPwrAGTXBF0/0` and `MaxRegPwrAGSTBC1/0`. There is **no `sounding` token** and no `SU-BF`
identifier anywhere — sounding is not named in these modules.

**2. `bf_` in `ath_dev.ko` is not beamforming.** All 14 hits are the TX **buffer**: `bf_node`,
`bf_q`, `bf_lastfrm`, `bf_lastbf`. The only two symbols matching are `ath_print_tbf_usage` and
`ath_tx_uapsdqnulbf_complete`, where `tbf` is `t`+`bf` and `nulbf` is `nul`+`bf`. This is the
seventh substring trap of the series.

**3. XW `umac.ko` has none of it.** Zero hits for every token, in a module that is **884,988 bytes**
against the AC's 2,356,432. The M5 UMAC carries no TxBF, STBC or LDPC vocabulary at all.

What *is* well instrumented on AC is the **runtime getter block**:

```
Getting LDPC: %x     Getting TX STBC: %x     Getting RX STBC: %x
Getting VHT MCS MAP set: %x
```

plus the proc field `LDPC` with `getLDPC`. So the negotiated capabilities are **readable per
station** even though the beamforming engine is not named.

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
XW = REPO_ROOT / "artifacts" / "firmware_re_xw_m5" / "xw_636_rootfs" / "lib" / "modules" / "2.6.32.71"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage615a_qca988x_txbf_beamforming_and_stbc_ldpc_re.json")

MODULES = {
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XW:umac.ko": XW / "umac.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "WA:ath_hal.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "XC:ath_hal.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
}

TOKENS = ["TXBF", "txbf", "beamform", "sounding", "SU-BF", "SU_BF",
          "stbc", "STBC", "ldpc", "LDPC", "mu_mimo"]
# the runtime getters that make the negotiated capability observable
GETTERS = ["Getting LDPC", "Getting TX STBC", "Getting RX STBC", "Getting VHT MCS MAP"]
# the capability name table is a byte run with non-printable separators, so detect it by the
# co-presence of its distinctive neighbours rather than by a literal string
CAP_NEIGHBOURS = ["TXBF", "VHT80", "HTDUP"]
# markers that prove `bf_` is a TX buffer, not beamforming
BUFFER_MARKERS = ("bf_node", "bf_q", "bf_lastfrm", "bf_lastbf")
# proc knob for LDPC
PROC = ["LDPC", "getLDPC"]


def ctx(b: bytes, tok: str, n: int = 3, w: int = 66) -> list[str]:
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

    def matching(self, pattern: str, cap: int = 24) -> list[str]:
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
        bf_ctx = ctx(b, "bf_", 3)
        rows.append(dict(
            module=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            tokens={t: b.count(t.encode()) for t in TOKENS},
            getters={k: b.count(k.encode()) for k in GETTERS},
            proc={k: b.count(k.encode()) for k in PROC},
            cap_table=int(all(b.count(n.encode()) for n in CAP_NEIGHBOURS)),
            bf_underscore=b.count(b"bf_"),
            bf_buffer_ids=sum(b.count(m.encode()) for m in BUFFER_MARKERS),
            bf_is_buffer=sum(b.count(m.encode()) for m in BUFFER_MARKERS) >= 2,
            bf_contexts=bf_ctx[:2],
            txbf_not_supported=b.count(b"TXBF not supported"),
            maxregpwr_txbf=b.count(b"MaxRegPwrAGTXBF"),
            feature_symbols=syms.matching(r"txbf|stbc|ldpc|sounding|beamform", 20)))

    ok = [r for r in rows if r.get("status") == "ok"]
    umac = [r for r in ok if r["module"].endswith("umac.ko")]
    xw = [r for r in umac if r["module"].startswith("XW")]
    txbf = sum(r["tokens"]["TXBF"] for r in ok)
    stbc = sum(r["tokens"]["STBC"] + r["tokens"]["stbc"] for r in ok)
    ldpc = sum(r["tokens"]["LDPC"] + r["tokens"]["ldpc"] for r in ok)
    sounding = sum(r["tokens"]["sounding"] + r["tokens"]["SU-BF"] + r["tokens"]["SU_BF"]
                   for r in ok)
    getters = sorted({k for r in ok for k, v in r["getters"].items() if v})
    proc = sorted({k for r in ok for k, v in r["proc"].items() if v})
    cap_tables = sum(1 for r in ok if r["cap_table"])
    bf_buffer = sum(1 for r in ok if r["bf_is_buffer"])
    feats = sorted({n for r in ok for n in r["feature_symbols"]})
    xw_tokens = sum(sum(r["tokens"].values()) for r in xw)

    report = dict(
        meta=dict(stage="615A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage615a_qca988x_txbf_beamforming_and_stbc_ldpc_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census across seven modules on two lines; capability-table and "
                         "runtime-getter extraction; context classification of the bf_ substring "
                         "to separate TX buffers from beamforming",
                  premise_corrections=[
                      "bf_ in ath_dev.ko is the TX buffer (bf_node, bf_q, bf_lastfrm), not "
                      "beamforming: no beamforming symbol exists there",
                      "XW umac.ko carries zero TxBF, STBC and LDPC tokens, in a module less than "
                      "half the size of the AC one",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     txbf_tokens=txbf,
                     stbc_tokens=stbc,
                     ldpc_tokens=ldpc,
                     txbf_named=int(txbf > 0),
                     capability_table_modules=cap_tables,
                     capability_table_named=int(cap_tables > 0),
                     txbf_not_supported_modules=sum(1 for r in ok if r["txbf_not_supported"]),
                     maxregpwr_txbf_modules=sum(1 for r in ok if r["maxregpwr_txbf"]),
                     runtime_getters=getters,
                     runtime_getter_count=len(getters),
                     capability_readable=int(len(getters) >= 3),
                     proc_knobs=proc,
                     feature_symbols=feats,
                     sounding_token_hits=sounding,
                     sounding_absent=int(sounding == 0),
                     bf_underscore_modules=bf_buffer,
                     bf_buffer_marker_hits=sum(r["bf_buffer_ids"] for r in ok),
                     bf_means_buffer=int(bf_buffer > 0),
                     xw_umac_token_total=xw_tokens,
                     xw_umac_feature_free=int(xw_tokens == 0 and bool(xw)),
                     txbf_engine_recovered=0,
                     sounding_sequence_recovered=0),
        gaps=["no sounding and no SU-BF identifier exists in any of the seven modules: the "
              "beamforming training sequence the stage asks about is not named",
              "TXBF appears as capability text and per-rate-group power, not as a beamforming "
              "engine; the engine is not in these modules",
              "bf_ in ath_dev.ko is the TX buffer struct, so any search for beamforming there "
              "returns the wrong object",
              "XW umac.ko has zero tokens from the set, so the M5 line carries none of this "
              "vocabulary",
              "the negotiated LDPC and STBC values are printed by the runtime getters but the "
              "per-peer bit layout was not recovered",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[615A] modules={s['modules_ok']} TXBF={s['txbf_tokens']} STBC={s['stbc_tokens']} "
          f"LDPC={s['ldpc_tokens']} sounding={s['sounding_token_hits']} "
          f"cap_table={s['capability_table_modules']} getters={s['runtime_getter_count']} "
          f"bf_buffer={s['bf_means_buffer']} xw_tokens={s['xw_umac_token_total']}")
    print(f"        getters={getters}")
    print(f"[615A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
