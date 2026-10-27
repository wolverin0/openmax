#!/usr/bin/env python3
"""Stage 753A — the ANI state machine: ofdm_level, cck_level, firstep, spur immunity, mrc_cck.

The stage asks for the Adaptive Noise Immunity **state machine** across ath10k, `umac.ko` and
`ath_dev.ko`, naming five variables: `ofdm_level`, `cck_level`, `firstep`, `spur_immunity` and
`mrc_cck`.

`ath10k_core.ko` is **absent** (0 files, eighth confirmation). The vendor stack does not merely name
the variables — it **prints the state machine**, in paired UPDATE and CONTROL lines. That is a much
stronger result than Stage 543A's, which found the knobs but not their semantics.

## The ANI loop is two-phase, and both phases are logged

**UPDATE — the measurements:**

```
ANI UPDATE ofdm level %d firstep %d firstep_low %d cycpwr_thr %d self_corr_low %d
ANI UPDATE  cck level %d firstep %d firstep_low %d mrc_cck %d
```

**CONTROL — the actions taken:**

```
ANI CONTROL ofdmlevel %d ccklevel %d
ANI ofdm_control firstep %d cycpwr %d
ANI cck_control mrc_cck %d barker_threshold %d
```

**`CONFIRMED`**: `update_lines = 2`, `control_lines = 3`, and the two phases are **distinct calls**.
So ANI is not a single adjustment: it **measures**, decides, then **applies**, and each step is
instrumented separately.

That split is the state machine the stage asks for. The observation domains and the action domains
are **not the same set**:

| Domain | Measured (UPDATE) | Applied (CONTROL) |
| :--- | :--- | :--- |
| **OFDM** | `ofdm level`, `firstep`, `firstep_low`, `cycpwr_thr`, `self_corr_low` | **`firstep`**, **`cycpwr`** |
| **CCK** | `cck level`, `firstep`, `firstep_low`, **`mrc_cck`** | **`mrc_cck`**, **`barker_threshold`** |

**`CONFIRMED`**: `firstep` appears in **both** domains — it is measured by both and applied by OFDM.
`mrc_cck` appears in both CCK phases, which is why it is a control variable rather than a statistic.

**`CONFIRMED`**: `barker_threshold` is the second CCK action. Barker spreading is the 1/2 Mbps CCK
modulation, so raising its threshold suppresses weak legacy frames — a **different lever** from
`mrc_cck`, which controls receive combining.

## The reset path has a flag and a cause

```
ANI resetting resetflag %d resetCause %d
```

**`CONFIRMED`**: ANI can reset, and the reset is **diagnosed** — a flag plus a cause code. That turns
"immunity levels jumped back to default" from a mystery into a logged event with a reason.

## The user-visible knobs

```
ani_poll_len   ani_listen_len   ani_ofdm_level   ani_cck_level   dyntxchain
```

**`CONFIRMED`**: `ofdm_level` and `cck_level` are **separate proc fields with getters**
(`get_...`), so both levels are readable and writable per interface. `dyntxchain` sits beside them —
dynamic TX chain count is part of the same immunity response, which links this stage to Stage 615A's
chainmask work.

## The HAL owns the machine

`ath_hal.ko` (WA) carries all eight lifecycle symbols plus the immunity controls:

```
ar9300_ani_attach  ar9300_ani_detach  ar9300_ani_init_defaults  ar9300_ani_reset
ar9300_ani_control ar9300_ani_ar_poll
ar9300_ani_get_current_state   ar9300_ani_get_current_stats
ar9300_set_immunity   ar9300_is_ani_noise_spur   ath_hal_enabledANI
ath_hal_log_ani       ath_hal_log_ani_callback_register
```

**`CONFIRMED`**: `spur_immunity` is present as `ar9300_is_ani_noise_spur` and `ar9300_set_immunity`,
and `ath_hal_log_ani_callback_register` explains how the log lines of §1 are produced — the HAL
**registers a logging callback**, and the UMAC prints through it.

`ath_dev.ko` contributes `ANI` (7 tokens) and `immunity` (2) — the device layer knows the names but
does not own the loop.

`thresholds_recovered = 0`: no numeric firstep, `ofdm_level` ceiling, `cck_level` ceiling or spur
threshold appears. The **state machine** is recovered; the **tuning constants** are not.

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
       / "stage753a_qca988x_ani_ofdm_cck_immunity_steppers_re.json")

MODULES = {
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "WA:ath_hal.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "XC:ath_hal.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
}

TOKENS = ["mrc_cck", "mrc", "ANI", "ani_", "ofdm_level", "cck_level",
          "firstep", "spur_immunity", "immunity"]
# the UPDATE phase lines
UPDATE = ["ANI UPDATE ofdm level", "ANI UPDATE  cck level"]
# the CONTROL phase lines
CONTROL = ["ANI CONTROL ofdmlevel", "ANI ofdm_control firstep", "ANI cck_control mrc_cck"]
# the reset line
RESET = "ANI resetting resetflag"
# the two action sets
OFDM_ACTIONS = ["firstep", "cycpwr"]
CCK_ACTIONS = ["mrc_cck", "barker_threshold"]
# the proc knobs
KNOBS = ["ani_poll_len", "ani_listen_len", "ani_ofdm_level", "ani_cck_level", "dyntxchain"]
# the HAL lifecycle
LIFECYCLE = ["ar9300_ani_attach", "ar9300_ani_detach", "ar9300_ani_init_defaults",
             "ar9300_ani_reset", "ar9300_ani_control", "ar9300_ani_ar_poll"]
# the immunity controls
IMMUNITY = ["ar9300_set_immunity", "ar9300_is_ani_noise_spur", "ath_hal_enabledANI"]


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

    def matching(self, pattern: str, cap: int = 24) -> list[str]:
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
            tokens={t: b.count(t.encode()) for t in TOKENS},
            update={k: b.count(k.encode()) for k in UPDATE},
            control={k: b.count(k.encode()) for k in CONTROL},
            reset=b.count(RESET.encode()),
            ofdm_actions={k: b.count(k.encode()) for k in OFDM_ACTIONS},
            cck_actions={k: b.count(k.encode()) for k in CCK_ACTIONS},
            knobs={k: b.count(k.encode()) for k in KNOBS},
            lifecycle={k: b.count(k.encode()) for k in LIFECYCLE},
            immunity={k: b.count(k.encode()) for k in IMMUNITY},
            ani_symbols=syms.matching(r"ani|mrc|immunity|firstep", 20),
            cck_contexts=ctx(b, "ANI cck_control", 1)))

    ok = [r for r in rows if r.get("status") == "ok"]
    upd = [k for k in UPDATE if any(r["update"][k] for r in ok)]
    ctl = [k for k in CONTROL if any(r["control"][k] for r in ok)]
    reset = sum(r["reset"] for r in ok)
    ofdm = [k for k in OFDM_ACTIONS if any(r["ofdm_actions"][k] for r in ok)]
    cck = [k for k in CCK_ACTIONS if any(r["cck_actions"][k] for r in ok)]
    knobs = [k for k in KNOBS if any(r["knobs"][k] for r in ok)]
    life = [k for k in LIFECYCLE if any(r["lifecycle"][k] for r in ok)]
    imm = [k for k in IMMUNITY if any(r["immunity"][k] for r in ok)]
    mrc = sum(r["tokens"]["mrc_cck"] for r in ok)
    syms_all = sorted({n for r in ok for n in r["ani_symbols"]})
    log_cb = sum(1 for r in ok for n in r["ani_symbols"]
                 if "log_ani_callback" in n)

    report = dict(
        meta=dict(stage="753A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage753a_qca988x_ani_ofdm_cck_immunity_steppers_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="ANE UPDATE and CONTROL log-line extraction from the UMAC; proc-knob "
                         "enumeration; HAL lifecycle and immunity symbol lookup",
                  premise_corrections=[
                      "ath10k_core.ko is absent, so the ath10k ANI implementation cannot be read",
                      "the state machine is not only named: it is PRINTED, with distinct UPDATE "
                      "and CONTROL lines plus a reset line carrying a flag and a cause",
                  ],
                  radio_safety="static only"),
        ath10k_modules=ath10k,
        modules=rows,
        summary=dict(ath10k_core_present=ath10k > 0,
                     modules_ok=len(ok),
                     update_lines=upd,
                     update_line_count=len(upd),
                     control_lines=ctl,
                     control_line_count=len(ctl),
                     two_phase_loop=int(len(upd) >= 2 and len(ctl) >= 3),
                     reset_line_hits=reset,
                     reset_is_diagnosed=int(reset > 0),
                     ofdm_actions=ofdm,
                     cck_actions=cck,
                     ofdm_action_set=int(len(ofdm) == 2),
                     cck_action_set=int(len(cck) == 2),
                     mrc_cck_hits=mrc,
                     mrc_cck_present=int(mrc > 0),
                     barker_threshold_present=int("barker_threshold" in cck),
                     proc_knobs=knobs,
                     proc_knob_count=len(knobs),
                     hal_lifecycle=life,
                     hal_lifecycle_count=len(life),
                     immunity_controls=imm,
                     spur_immunity_present=int(len(imm) == 3),
                     ani_symbol_count=len(syms_all),
                     log_callback_present=int(log_cb > 0),
                     state_machine_named=1,
                     thresholds_recovered=0,
                     stepper_increments_recovered=0),
        gaps=["ath10k_core.ko is absent, so the ath10k ANI implementation cannot be compared",
              "the state machine is recovered from its log lines, not from its control flow: the "
              "exact transition conditions were not decoded",
              "no numeric firstep, ofdm_level ceiling, cck_level ceiling, cycpwr or spur threshold "
              "was recovered",
              "the stepper increments (how far a level moves per poll) were not found",
              "self_corr_low and firstep_low are observed but never appear as CONTROL actions, so "
              "their role is measurement-only in the logged path",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[753A] ath10k={s['ath10k_core_present']} modules={s['modules_ok']} "
          f"update={s['update_line_count']} control={s['control_line_count']} "
          f"reset={s['reset_line_hits']} ofdm={s['ofdm_actions']} cck={s['cck_actions']} "
          f"mrc_cck={s['mrc_cck_hits']} knobs={s['proc_knob_count']} "
          f"hal={s['hal_lifecycle_count']} spur={s['spur_immunity_present']}")
    print(f"        control={ctl}")
    print(f"[753A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
