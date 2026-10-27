#!/usr/bin/env python3
"""Stage 543A — ANI state machines, spur immunity, firstep and PHY-error false alarms.

The stage asks for six things across `ath_hal.ko`, `ath_dev.ko` and `umac.ko` on WA, XC and XW:

  * the **Adaptive Noise Immunity (ANI)** state machine;
  * **spur** immunity;
  * **firstep**;
  * **ofdm_level**;
  * **PHY error false-alarm thresholds**.

All five exist, but they are **split across the three modules** in a way that matters: the HAL owns
the machine, the UMAC owns the knobs and the error rates, and the two lines instrument **different
variables**.

The HAL lifecycle, exactly named in WA and XC `ath_hal.ko`:

```
ar9300_ani_attach           ar9300_ani_detach
ar9300_ani_init_defaults    ar9300_ani_reset
ar9300_ani_control          ar9300_ani_ar_poll
ar9300_ani_get_current_state   ar9300_ani_get_current_stats
```

That is a **complete object lifecycle** (attach, defaults, reset, poll, control, detach) plus two
read-only accessors. ANI is not a flag; it is a polled state machine.

Spur immunity is its own family:

```
ar9300_is_ani_noise_spur        ar9300_set_immunity
ar9300_get_spur_info            ar9300_set_spur_info
ar9300_eeprom_get_spur_chans_ptr
ath_hal_enabledANI
```

`ar9300_eeprom_get_spur_chans_ptr` is the important one: the spur **channel list lives in EEPROM**,
so the immunity set is per-board calibration data, not a constant.

The UMAC side exposes the state to userspace as proc fields:

```
ani_poll_len    ani_listen_len    ani_ofdm_level    ani_cck_level    dyntxchain
```

and reports the false-alarm rate directly:

```
ofdm_phy_err_rate, cck_phy_err_rate, reg_ofdm_phy_error_cu, max_phy_e...
```

So `ofdm_level` and `cck_level` are **independently adjustable** and both are user-visible.

The AC/XW asymmetry, again:

| Variable | WA/XC `ath_hal.ko` | XW `ath_hal.ko` |
| :--- | :-: | :-: |
| `ar9300_ani_*` lifecycle | **8 symbols** | 0 |
| `spur` tokens | 4 | **5** (+1 `SPUR`) |
| `firstep` | 0 | **2** |
| `cycpwr` | 0 | **2** |

The AC HAL names the machine; the XW HAL names the **tuning variables** (`firstep`, `cycpwrThr1`)
and the INI override path found in Stage 373A. Two lines, two different views of the same loop.

`threshold_values_recovered = 0`: no numeric firstep, ofdm_level ceiling or spur threshold was read.

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
       / "stage543a_qca988x_ani_ofdm_cck_weak_signal_and_spur_re.json")

MODULES = {
    "WA:ath_hal.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "XC:ath_hal.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "XW:ath_hal.ko": XW / "ath_hal.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
}

TOKENS = ["ani", "ANI", "spur", "SPUR", "firstep", "ofdm_level", "cck_level",
          "phy_err", "immunity", "cycpwr"]
# the user-visible ANI knobs in umac.ko
KNOBS = ["ani_poll_len", "ani_listen_len", "ani_ofdm_level", "ani_cck_level", "dyntxchain"]
# the false-alarm rate fields
RATES = ["ofdm_phy_err_rate", "cck_phy_err_rate", "max_phy_err", "reg_ofdm_phy_error_cu"]


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
            knobs={k: b.count(k.encode()) for k in KNOBS},
            rates={k: b.count(k.encode()) for k in RATES},
            ani_symbols=syms.matching(r"ani", 24),
            gate=b.count(b"ath_hal_enabledANI"),
            spur_symbols=syms.matching(r"spur", 16),
            immun_symbols=syms.matching(r"immun", 8),
            knob_contexts=ctx(b, "ani_ofdm_level", 1),
            rate_contexts=ctx(b, "ofdm_phy_err_rate", 1)))

    ok = [r for r in rows if r.get("status") == "ok"]
    lifecycle = sorted({n for r in ok for n in r["ani_symbols"]
                        if n.startswith("ar9300_ani_")})
    all_ani = sorted({n for r in ok for n in r["ani_symbols"]})
    spur = sorted({n for r in ok for n in r["spur_symbols"]})
    immun = sorted({n for r in ok for n in r["immun_symbols"]})
    knobs = sorted({k for r in ok for k, v in r["knobs"].items() if v})
    rates = sorted({k for r in ok for k, v in r["rates"].items() if v})
    firstep_mods = [r["module"] for r in ok if r["tokens"]["firstep"]]
    cycpwr_mods = [r["module"] for r in ok if r["tokens"]["cycpwr"]]
    firstep_hal = [m for m in firstep_mods if "ath_hal" in m]
    firstep_umac = [m for m in firstep_mods if "umac" in m]
    lifecycle_complete = sum(1 for verb in ("attach", "detach", "init_defaults", "reset",
                                            "control", "ar_poll")
                             if any(verb in n for n in lifecycle))

    report = dict(
        meta=dict(stage="543A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage543a_qca988x_ani_ofdm_cck_weak_signal_and_spur_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census across seven modules on three lines; defined-symbol "
                         "lookup for the ar9300_ani lifecycle, the spur and immunity families; "
                         "proc-knob and phy-error-rate extraction from the UMAC",
                  premise_corrections=[
                      "the ANI state machine is not one module's property: the HAL owns the "
                      "lifecycle, the UMAC owns the knobs and the PHY-error rates",
                      "firstep is not XW-only: it is an INI override in the XW ath_hal.ko and an "
                      "ANI state variable in the AC umac.ko, so the split is HAL versus UMAC",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     ani_lifecycle=lifecycle,
                     ani_lifecycle_count=len(lifecycle),
                     ani_lifecycle_complete_of_6=lifecycle_complete,
                     ani_state_machine_named=int(lifecycle_complete >= 5),
                     spur_symbols=spur,
                     spur_symbol_count=len(spur),
                     spur_chans_in_eeprom=int(any("spur_chans" in n for n in spur)),
                     immunity_symbols=immun,
                     immunity_named=int(bool(immun)),
                     ani_enabled_symbol=int(any(r["gate"] for r in ok)),
                     proc_knobs=knobs,
                     proc_knob_count=len(knobs),
                     ofdm_and_cck_independent=int("ani_ofdm_level" in knobs
                                                  and "ani_cck_level" in knobs),
                     phy_error_rates=rates,
                     phy_error_rate_count=len(rates),
                     firstep_modules=firstep_mods,
                     cycpwr_modules=cycpwr_mods,
                     firstep_in_xw_hal=int(any(m.startswith("XW") for m in firstep_hal)),
                     firstep_in_ac_umac=int(bool(firstep_umac)),
                     firstep_hal_umac_split=int(bool(firstep_hal) and bool(firstep_umac)),
                     threshold_values_recovered=0,
                     ani_state_graph_recovered=0),
        gaps=["no numeric firstep, ofdm_level ceiling, cck_level ceiling or spur threshold was "
              "read; the symbols name the controls, not their values",
              "the ANI state graph was not decoded: attach/init/reset/poll/control are named but "
              "the transition conditions are not",
              "the spur channel list lives in EEPROM via ar9300_eeprom_get_spur_chans_ptr, and "
              "that per-board data is not in this corpus",
              "firstep appears in the XW HAL as an INI override and in the AC umac.ko as an ANI "
              "state variable; whether the two refer to the same register is unresolved",
              "the PHY-error false-alarm thresholds are reported as rates but the cut-off that "
              "triggers an ANI level change was not recovered",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[543A] modules={s['modules_ok']} lifecycle={s['ani_lifecycle_count']}"
          f"/{s['ani_lifecycle_complete_of_6']} spur={s['spur_symbol_count']} "
          f"immun={s['immunity_named']} knobs={s['proc_knob_count']} "
          f"rates={s['phy_error_rate_count']} "
          f"firstep_xw_hal={s['firstep_in_xw_hal']} firstep_ac_umac={s['firstep_in_ac_umac']}")
    print(f"        lifecycle={lifecycle}")
    print(f"        knobs={knobs}")
    print(f"[543A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
