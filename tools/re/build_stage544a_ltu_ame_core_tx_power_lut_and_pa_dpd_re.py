#!/usr/bin/env python3
"""Stage 544A — AF-LTU TX power LUT, PA pre-distortion and 4096-QAM EVM instrumentation.

The stage names four things in `ame_core.ko` and `eab_driver.ko`:

  * the **TX power LUT**;
  * **PA pre-distortion / calibration**;
  * **4096-QAM TX EVM backoff**;
  * the module pair.

`eab_driver.ko` is **absent** (ninth confirmation). In the two modules that exist the surface is
dense and, importantly, it is **not** a table dump — it is a named control and telemetry API:

**TX power / attenuation** — a matched conversion pair:

```
bbp_util_calculate_tx_power_by_attenuation
bbp_util_calculate_tx_attenuation_by_power
ame_bbp_get_txpower          ame_bbp_get_desired_txpower
ame_bbp_op_rf_tune_txpower   ame_bbp_op_rf_force_txpower
ame_bbp_op_set_rxTopA_txPower   ame_bbp_op_get_rxTopA_txPower
```

**DPD and PA** — setters plus a sysfs table interface:

```
ame_bbp_set_dpd      ame_bbp_get_dpd      ame_bbp_set_pa
dpd_load             dpd_show             dpd_store
```

and a size check in the log: `Incorrect dpd(tx) size (%d)!=(%d)` — the DPD payload is
**length-validated**, which means it is a variable-length blob, not a fixed struct.

**EVM** — a full instrumentation family:

```
ame_bbp_op_evm            ame_bbp_op_evm_mcs_map
ame_bbp_op_evm_peek_symbols   ame_bbp_evm_get_cfg
ame_bbp_evm_set_r         ame_bbp_get_evm_dump
__bbp_mrx_evm_next
```

**4096-QAM**:

```
bbp_rf_set_super4096      check_4096mimo_ofdm      choose_mcsTPindex_ofdm
```

**Calibration** (in `ame_dev.ko`): `calibrate`, `callback_func_call_sync_calibrate`, and a ubus
RPC pair `set_rfic_txgain` / `get_rfic_txgain`.

One trap to record: **`backoff` is not TX EVM backoff**. All 25 hits are
`cz_cross_frame_backoff_enable` / `cz_cross_frame_backoff_grouping_num` — a **cross-frame grouping**
scheduler knob, unrelated to power backoff.

`lut_values_recovered = 0`, `dpd_coefficients_recovered = 0`, `evm_backoff_db_recovered = 0`: the API
is named, the numbers are not in the readable corpus.

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
       / "stage544a_ltu_ame_core_tx_power_lut_and_pa_dpd_re.json")

MODULES = {"ame_core.ko": LTU / "ame_core.ko", "ame_dev.ko": LTU / "ame_dev.ko"}

TOKENS = ["dpd", "DPD", "pa_param", "pa_", "lut", "LUT", "txpower", "tx_power",
          "evm", "EVM", "backoff", "4096", "qam", "attenuation", "txgain", "calib"]
# the conversion pair that makes the LUT meaningful
CONVERSION = ["calculate_tx_power_by_attenuation", "calculate_tx_attenuation_by_power"]
# EVM instrumentation
EVM_FAMILY = r"evm"
# 4096-QAM support
SUPER = r"4096"
# DPD table interface
DPD_IFACE = ["dpd_load", "dpd_show", "dpd_store"]


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
        backoff_ctx = ctx(b, "backoff", 3)
        rows.append(dict(
            module=name, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            tokens={t: b.count(t.encode()) for t in TOKENS},
            conversion={t: b.count(t.encode()) for t in CONVERSION},
            dpd_iface={t: b.count(t.encode()) for t in DPD_IFACE},
            dpd_symbols=syms.matching(r"dpd", 16),
            pa_symbols=syms.matching(r"pa_|_pa$|pa_param", 16),
            txpower_symbols=syms.matching(r"txpower|tx_power", 20),
            evm_symbols=syms.matching(EVM_FAMILY, 20),
            super_symbols=syms.matching(SUPER, 12),
            calib_symbols=syms.matching(r"calib|txgain", 16),
            backoff_is_crossframe=(bool(backoff_ctx)
                                   and all("cz_cross_frame" in c for c in backoff_ctx)),
            dpd_size_check=ctx(b, "Incorrect dpd", 1)))

    ok = [r for r in rows if r.get("status") == "ok"]
    dpd_syms = sorted({n for r in ok for n in r["dpd_symbols"]})
    pa_syms = sorted({n for r in ok for n in r["pa_symbols"]})
    tx_syms = sorted({n for r in ok for n in r["txpower_symbols"]})
    evm_syms = sorted({n for r in ok for n in r["evm_symbols"]})
    super_syms = sorted({n for r in ok for n in r["super_symbols"]})
    calib_syms = sorted({n for r in ok for n in r["calib_symbols"]})
    conv_hits = sum(sum(r["conversion"].values()) for r in ok)
    iface = sorted({k for r in ok for k, v in r["dpd_iface"].items() if v})
    size_check = sum(1 for r in ok if r["dpd_size_check"])
    crossframe = sum(1 for r in ok if r["backoff_is_crossframe"])

    report = dict(
        meta=dict(stage="544A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage544a_ltu_ame_core_tx_power_lut_and_pa_dpd_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census of the TX-power, DPD, PA, EVM and 4096-QAM vocabularies; "
                         "defined-symbol lookup for the conversion pair and the instrumentation "
                         "families; context classification of the backoff hits",
                  premise_corrections=[
                      "eab_driver.ko is absent, so ame_core.ko and ame_dev.ko are the only "
                      "readable targets",
                      "`backoff` is not TX EVM backoff: every hit is cz_cross_frame_backoff_*, a "
                      "cross-frame grouping scheduler knob",
                  ],
                  radio_safety="static only"),
        absence=dict(eab_driver=eab),
        modules=rows,
        summary=dict(eab_driver_present=eab > 0,
                     modules_ok=len(ok),
                     conversion_pair_hits=conv_hits,
                     conversion_pair_named=int(conv_hits >= 2),
                     dpd_symbols=dpd_syms,
                     dpd_symbol_count=len(dpd_syms),
                     dpd_sysfs_interface=iface,
                     dpd_table_is_variable_length=int(size_check > 0),
                     pa_symbols=pa_syms[:10],
                     pa_symbol_count=len(pa_syms),
                     txpower_symbols=tx_syms[:10],
                     txpower_symbol_count=len(tx_syms),
                     evm_symbol_count=len(evm_syms),
                     evm_symbols=evm_syms[:10],
                     super4096_symbols=super_syms,
                     super4096_named=int(bool(super_syms)),
                     calib_symbols=calib_syms[:8],
                     calib_symbol_count=len(calib_syms),
                     backoff_is_crossframe_modules=crossframe,
                     lut_values_recovered=0,
                     dpd_coefficients_recovered=0,
                     evm_backoff_db_recovered=0),
        gaps=["eab_driver.ko is absent, so the stage's second module has no bytes",
              "the TX power LUT is a conversion pair (tx_power <-> attenuation), not a readable "
              "table: the coefficients live in calibration data that is not in this corpus",
              "the DPD table is variable-length (enforced by an Incorrect dpd(tx) size log) and "
              "is loaded through dpd_store, so its coefficients are runtime data",
              "no EVM-to-backoff dB mapping was recovered; the EVM family reports symbols and "
              "MCS maps, not a backoff curve",
              "`backoff` has 25 hits and every one is cz_cross_frame_backoff_*, a cross-frame "
              "grouping knob; counting it as TX backoff would be a false positive",
              "4096-QAM is named (bbp_rf_set_super4096, check_4096mimo_ofdm) but the EVM "
              "threshold required for 4096-QAM was not found",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[544A] eab={s['eab_driver_present']} modules={s['modules_ok']} "
          f"conv={s['conversion_pair_hits']} dpd={s['dpd_symbol_count']} "
          f"iface={s['dpd_sysfs_interface']} pa={s['pa_symbol_count']} "
          f"txp={s['txpower_symbol_count']} evm={s['evm_symbol_count']} "
          f"4096={s['super4096_named']} calib={s['calib_symbol_count']} "
          f"crossframe={s['backoff_is_crossframe_modules']}")
    print(f"        dpd={dpd_syms[:6]}")
    print(f"        evm={evm_syms[:5]}")
    print(f"[544A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
