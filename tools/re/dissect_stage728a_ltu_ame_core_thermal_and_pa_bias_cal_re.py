#!/usr/bin/env python3
"""Stage 728A — thermal calibration, PA temperature compensation and TX gain control.

The stage asks for three things in `ame_core.ko` and `ame_dev.ko`:

  * **thermal calibration**;
  * **PA temperature compensation**;
  * **TX gain control**.

Two are strong positives and one is a naming correction.

**The word `thermal` does not exist.** It returns **0**, as do `pa_bias` and `bias`. So the stage's
vocabulary is not the module's. What exists instead is **temperature** and **tx_gain**, both named:

```
bbp_rf_get_temperature      fty_rf_get_temperature
```

**`CONFIRMED`**: `temperature_reader_count = 2` — **two** temperature readers, one on the BBP/RF
path and one in the factory (fty) test path. Two readers means the value is read both during normal
operation and during factory calibration.

**TX gain has a complete control surface:**

```
ame_bbp_get_tx_gain         ame_bbp_set_tx_gain
bbp_rf_fetch_tx_gain        bbp_rf_apply_tx_gain
ame_bbp_obs_set_txgain
```

**`CONFIRMED`**: `tx_gain_controls = 5`. Note the **fetch / apply** split: `fetch` and `apply` are
separate verbs, which is the signature of a **staged** update — read the current gain, compute, then
apply. That is what a temperature-compensating loop needs.

**The autotune loop is named, with a step:**

```
fty_rf_autotune_txgain      fty_rf_adjust_step_txgain
```

**`CONFIRMED`**: `autotune_present = 1`. `autotune_txgain` is the loop and `adjust_step_txgain` is
its **step size** — so the gain is walked toward a target rather than set in one jump. A stepping
controller is exactly what you would use for thermal drift, which is slow and monotonic.

**The calibration compensation is named:**

```
bbp_ulpwr_fftpwr_cal_compensate
```

**`CONFIRMED`**: a power-calibration compensation routine exists. `ulpwr`/`fftpwr` are uplink and
full-frame power — the two domains that need separate calibration because they are measured
differently.

**A temperature buffer exists for loopback:**

```
AME_EAB_GetLoopbackTempBuf
```

**`CONFIRMED`**: the EAB layer (Stage 694A) provides a **loopback temperature buffer**, so a
calibration run can capture temperature samples through the ASIC loopback path rather than polling a
sensor register.

**Factory access is over ubus** (`ame_dev.ko`):

```
calibrate      callback_func_call_sync_calibrate
set_rfic_txgain / get_rfic_txgain   obs_txgain_show / obs_txgain_store
```

**`CONFIRMED`**: calibration and RFIC gain are **externally triggered** through ubus — the same
finding as Stage 544A's DPD path. Nothing here runs on an internal timer.

## The `compensat` trap

`compensat` has 2 hits and **neither is thermal**:

```
sched_airtime_compensate_by_l2bps      <- airtime scheduling
bbp_ulpwr_fftpwr_cal_compensate        <- power calibration
```

**`REFUTED`**: a `compensat` search would find the power-calibration routine and, one line away, an
**airtime** compensator. Reading them as one thermal mechanism would be wrong — the ninth distinct
substring trap of the series.

`temp_to_gain_curve_recovered = 0`: the mapping from a temperature reading to a gain step is not in
the module. Both ends are named; the curve between them is the missing piece.

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
       / "stage728a_ltu_ame_core_thermal_and_pa_bias_cal_re.json")

MODULES = {"ame_core.ko": LTU / "ame_core.ko", "ame_dev.ko": LTU / "ame_dev.ko"}

TOKENS = ["thermal", "THERMAL", "temp", "TEMP", "temperature", "pa_bias", "bias",
          "BIAS", "txgain", "tx_gain", "calib", "compensat"]
# the temperature readers
TEMPS = ["bbp_rf_get_temperature", "fty_rf_get_temperature"]
# the TX gain control surface
GAIN = ["ame_bbp_get_tx_gain", "ame_bbp_set_tx_gain",
        "bbp_rf_fetch_tx_gain", "bbp_rf_apply_tx_gain",
        "ame_bbp_obs_set_txgain"]
# the autotune loop and its step
AUTOTUNE = ["fty_rf_autotune_txgain", "fty_rf_adjust_step_txgain"]
# the power calibration compensation
POWCAL = "bbp_ulpwr_fftpwr_cal_compensate"
# the loopback temperature buffer
LOOPBACK = "AME_EAB_GetLoopbackTempBuf"
# the ubus calibration and RFIC gain hooks
UBUS = ["calibrate", "set_rfic_txgain", "get_rfic_txgain"]
# the trap: compensate is airtime, not temperature
AIRTIME = "sched_airtime_compensate_by_l2bps"


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

    def matching(self, pattern: str, cap: int = 24) -> list[str]:
        return sorted({n for n in self.names if re.search(pattern, n, re.I)})[:cap]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

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
            temps={k: b.count(k.encode()) for k in TEMPS},
            gain={k: b.count(k.encode()) for k in GAIN},
            autotune={k: b.count(k.encode()) for k in AUTOTUNE},
            powcal=b.count(POWCAL.encode()),
            loopback=b.count(LOOPBACK.encode()),
            ubus={k: b.count(k.encode()) for k in UBUS},
            airtime=b.count(AIRTIME.encode()),
            temp_symbols=syms.matching(r"temp", 16),
            gain_symbols=syms.matching(r"tx_gain|txgain", 16),
            calib_symbols=syms.matching(r"calib|compensat", 16)))

    ok = [r for r in rows if r.get("status") == "ok"]
    temps = [k for k in TEMPS if any(r["temps"][k] for r in ok)]
    gain = [k for k in GAIN if any(r["gain"][k] for r in ok)]
    auto = [k for k in AUTOTUNE if any(r["autotune"][k] for r in ok)]
    powcal = sum(r["powcal"] for r in ok)
    loopback = sum(r["loopback"] for r in ok)
    ubus = [k for k in UBUS if any(r["ubus"][k] for r in ok)]
    airtime = sum(r["airtime"] for r in ok)
    thermal_hits = sum(r["tokens"]["thermal"] + r["tokens"]["THERMAL"] for r in ok)
    bias_hits = sum(r["tokens"]["pa_bias"] + r["tokens"]["bias"] + r["tokens"]["BIAS"]
                    for r in ok)
    temp_tokens = sum(r["tokens"]["temp"] + r["tokens"]["TEMP"]
                      + r["tokens"]["temperature"] for r in ok)
    txgain_tokens = sum(r["tokens"]["txgain"] + r["tokens"]["tx_gain"] for r in ok)
    temp_syms = sorted({n for r in ok for n in r["temp_symbols"]})
    gain_syms = sorted({n for r in ok for n in r["gain_symbols"]})

    report = dict(
        meta=dict(stage="728A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage728a_ltu_ame_core_thermal_and_pa_bias_cal_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census of the thermal, bias, tx-gain and calibration "
                         "vocabularies; defined-symbol lookup for the temperature readers, the "
                         "fetch/apply gain pair, the autotune step and the power-cal compensation; "
                         "context classification of the compensate hits",
                  premise_corrections=[
                      "thermal, pa_bias and bias all return 0: the mechanism is named with "
                      "temperature and tx_gain, not with the stage's vocabulary",
                      "compensat is a trap: one hit is sched_airtime_compensate_by_l2bps (airtime "
                      "scheduling) and the other is the power-calibration routine",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     thermal_word_hits=thermal_hits,
                     thermal_word_absent=int(thermal_hits == 0),
                     pa_bias_hits=bias_hits,
                     pa_bias_absent=int(bias_hits == 0),
                     temperature_tokens=temp_tokens,
                     temperature_readers=temps,
                     temperature_reader_count=len(temps),
                     two_temperature_paths=int(len(temps) == 2),
                     txgain_tokens=txgain_tokens,
                     tx_gain_controls=gain,
                     tx_gain_control_count=len(gain),
                     fetch_apply_split=int("bbp_rf_fetch_tx_gain" in gain
                                           and "bbp_rf_apply_tx_gain" in gain),
                     autotune_controls=auto,
                     autotune_present=int("fty_rf_autotune_txgain" in auto),
                     autotune_has_step=int("fty_rf_adjust_step_txgain" in auto),
                     power_cal_compensate=int(powcal > 0),
                     loopback_temp_buf=int(loopback > 0),
                     ubus_hooks=ubus,
                     ubus_calibration=int("calibrate" in ubus),
                     compensate_is_airtime=int(airtime > 0),
                     temp_to_gain_curve_recovered=0,
                     pa_bias_value_recovered=0),
        gaps=["thermal, pa_bias and bias do not exist as identifiers: the module names the "
              "mechanism with temperature and tx_gain instead",
              "the temperature-to-gain curve was not recovered: two readers and an autotune step "
              "are named, the mapping between them is not",
              "compensat is ambiguous: sched_airtime_compensate_by_l2bps is airtime, "
              "bbp_ulpwr_fftpwr_cal_compensate is power calibration; neither is thermal",
              "the PA bias value and its temperature coefficient were not found",
              "factory calibration is externally triggered over ubus, so no internal schedule was "
              "recovered",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[728A] modules={s['modules_ok']} thermal={s['thermal_word_hits']} "
          f"bias={s['pa_bias_hits']} temp={s['temperature_reader_count']} "
          f"txgain={s['tx_gain_control_count']} fetch_apply={s['fetch_apply_split']} "
          f"autotune={s['autotune_present']} step={s['autotune_has_step']} "
          f"powcal={s['power_cal_compensate']} ubus={s['ubus_hooks']}")
    print(f"        temps={temps}")
    print(f"        gain={gain}")
    print(f"[728A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
