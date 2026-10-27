#!/usr/bin/env python3
"""Stage 823A — airMagic spectral-efficiency channel scoring in airOS v8.7.25.

The stage asks how airMagic computes a spectral-efficiency score (bps/Hz) per 5 MHz portion by
combining interference histograms from all associated CPEs, and wants "the exact formula" for our
autonomous channel selector in Guarida.

`airMagic` is a **product name**, not a kernel symbol: `airmagic`, `airMagic`, `efficien` and `score`
all return 0 in `ubnt_poll_host.ko`. The mechanism is in the **userspace daemon `ubntspecd`**
(**47,192 bytes** — a real binary, not one of this corpus's zero-byte stubs).

And the daemon **prints the scoring interface, tier by tier**:

```
Find best channel for BW %d:
Checking %d : . %d [%d] BPS=%d SCORE=%d RATING=%d
*** BEST : %d BPS=%d SCORE=%d RATING=%d*
```

**`CONFIRMED`**: three distinct scoring tiers per candidate channel — **BPS**, **SCORE**,
**RATING** — and the selection runs **per bandwidth** (`Find best channel for BW %d`).

That three-tier structure is the formula's **shape**:

| Tier | What it must be |
| :--- | :--- |
| **BPS** | the raw throughput estimate for the channel |
| **SCORE** | BPS normalised or weighted (interference, CPE histograms) |
| **RATING** | the rank used to pick `*** BEST` |

**`REFUTED`**: the **arithmetic** is not in the strings. There is no `efficien`, no `score =` and no
bps/Hz expression. So the exact formula — how BPS becomes SCORE, what weights SCORE, how RATING is
ordered — is **not recoverable** from the daemon by name. `formula_coefficients_recovered = 0`.

What *is* recoverable is everything the formula consumes and produces:

```
Airmagic channels (total %d):        BW : %d |      %d : MIN LT=%d MAX LT=%d CONTROL : [
Number of channels exceeds AMG_MAX_CHANS        Number of channels exceeds AMG_NUM_CONTROL
c = %d MHZ=%u CHZ=%u CNTR=%d EDGE [Min = %d Max = %d] VALID [Min=%d Max=%d] MODE %d
Freq = %u Hz start_tone=%u tones_per_chan=%u
```

**`CONFIRMED`**: the channel list is **bandwidth-scoped** with **per-channel MIN/MAX LT limits**,
guarded by **two** capacity constants (`AMG_MAX_CHANS`, `AMG_NUM_CONTROL`) — so airMagic has both a
channel cap and a separate control cap.

**`CONFIRMED`**: `tones_per_chan` plus `start_tone` gives the **tone→frequency mapping**. That is the
missing link between the FFT bins (Stages 327A/451A could never decode the bin format) and a
per-5-MHz power figure: a channel's power is a **sum over a known tone range**, not over an opaque
bin array.

**`CONFIRMED`**: `CHZ` and `CNTR` and `EDGE` are separate fields, so a channel is described by
**centre and edges** independently — which is what a 5 MHz sub-portion of a 20/40/80 MHz channel
needs.

Radio safety: static only. No module loaded, no radio contacted, no channel changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage823a_airos_ubnt_poll_airmagic_spectral_channel_scoring_re.json")

MODULES = {
    "WA:ubnt_poll_host.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XC:ubnt_poll_host.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA:ubntspecd": FW / "wa_8725_rootfs/bin/ubntspecd",
    "XC:ubntspecd": FW / "xc_8725_rootfs/bin/ubntspecd",
}

TOKENS = ["airmagic", "Airmagic", "AIRMAGIC", "magic", "BPS", "bps", "SCORE", "RATING",
          "efficien", "hist", "interference", "tones_per_chan", "AMG_"]
# the scoring output line
SCORING = "BPS=%d SCORE=%d RATING=%d"
BEST = "*** BEST"
BW_SELECT = "Find best channel for BW"
# the channel list
CHAN_LIST = "Airmagic channels (total %d):"
LIMITS = "MIN LT=%d MAX LT=%d"
# the capacity guards
CAPS = ["AMG_MAX_CHANS", "AMG_NUM_CONTROL"]
# the tone geometry
TONE = "tones_per_chan=%u"
# the channel descriptor
DESC = "CHZ=%u CNTR=%d EDGE"


def ctx(b: bytes, tok: str, n: int = 2, w: int = 72) -> list[str]:
    out: list[str] = []
    needle = tok.encode()
    i = b.find(needle)
    while i >= 0 and len(out) < n:
        out.append("".join(chr(c) if 32 <= c < 127 else "."
                           for c in b[max(0, i - w):i + len(needle) + w]))
        i = b.find(needle, i + 1)
    return out


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
        rows.append(dict(
            module=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(),
            tokens={t: b.count(t.encode()) for t in TOKENS},
            scoring=b.count(SCORING.encode()),
            best_marker=b.count(BEST.encode()),
            bw_select=b.count(BW_SELECT.encode()),
            chan_list=b.count(CHAN_LIST.encode()),
            limits=b.count(LIMITS.encode()),
            caps={k: b.count(k.encode()) for k in CAPS},
            tone=b.count(TONE.encode()),
            desc=b.count(DESC.encode()),
            scoring_contexts=ctx(b, "BPS=", 2),
            tone_contexts=ctx(b, TONE, 1)))

    ok = [r for r in rows if r.get("status") == "ok"]
    spec = [r for r in ok if r["module"].endswith("ubntspecd")]
    kern = [r for r in ok if not r["module"].endswith("ubntspecd")]
    scoring = sum(r["scoring"] for r in ok)
    best = sum(r["best_marker"] for r in ok)
    bwsel = sum(r["bw_select"] for r in ok)
    chanl = sum(r["chan_list"] for r in ok)
    limits = sum(r["limits"] for r in ok)
    caps = sorted({k for r in ok for k, v in r["caps"].items() if v})
    tone = sum(r["tone"] for r in ok)
    desc = sum(r["desc"] for r in ok)
    airmagic_word = sum(sum(r["tokens"].values()) for r in ok
                        if "airmagic" in r["module"].lower())
    efficien = sum(r["tokens"]["efficien"] for r in ok)
    kern_magic = sum(r["tokens"]["magic"] for r in kern)
    spec_size = max((r["bytes"] for r in spec), default=0)

    report = dict(
        meta=dict(stage="823A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage823a_airos_ubnt_poll_airmagic_spectral_channel_scoring_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted, no channel changed",
                  method="token census across two kernel modules and two daemon copies; scoring "
                         "line extraction from ubntspecd; tone-geometry and channel-descriptor "
                         "format extraction; explicit probe for the bps/Hz expression",
                  premise_corrections=[
                      "airMagic is a product name, not a kernel symbol: airmagic/airMagic return 0 "
                      "in ubnt_poll_host.ko, and the mechanism lives in the ubntspecd daemon",
                      "the scoring is a three-tier BPS->SCORE->RATING output per channel per "
                      "bandwidth, but the arithmetic between the tiers is not in the strings",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     daemon_bytes=spec_size,
                     daemon_is_real_binary=int(spec_size > 10000),
                     kernel_airmagic_token_hits=sum(sum(r["tokens"].values()) for r in kern),
                     kernel_magic_hits=kern_magic,
                     efficiency_token_hits=efficien,
                     scoring_line_hits=scoring,
                     best_marker_hits=best,
                     per_bandwidth_selection=bwsel,
                     scoring_tiers=["BPS", "SCORE", "RATING"],
                     scoring_tier_count=3,
                     channel_list_hits=chanl,
                     channel_limits_hits=limits,
                     capacity_guards=caps,
                     capacity_guard_count=len(caps),
                     tone_geometry_hits=tone,
                     channel_descriptor_hits=desc,
                     tone_to_freq_mapping=int(tone > 0 and desc > 0),
                     formula_interface_recovered=int(scoring > 0 and best > 0),
                     formula_coefficients_recovered=0,
                     bps_per_hz_expression_recovered=0),
        gaps=["airMagic is a product name: the kernel modules carry none of the airMagic "
              "vocabulary, so the scoring is not a kernel function",
              "the three tiers BPS, SCORE and RATING are printed but the arithmetic between them "
              "is not: there is no efficiency, score = or bps/Hz expression anywhere",
              "the interference histogram combination across associated CPEs was not located; the "
              "daemon receives a STA list and reports limits, but the aggregation code is not "
              "named",
              "the 5 MHz portioning is implied by CHZ/CNTR/EDGE plus tones_per_chan, but no "
              "explicit 5 MHz constant exists in the daemon",
              "the two capacity guards (AMG_MAX_CHANS, AMG_NUM_CONTROL) bound the candidate set "
              "without revealing how candidates are ranked",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[823A] modules={s['modules_ok']} daemon={s['daemon_bytes']}B "
          f"kern_magic={s['kernel_magic_hits']} scoring={s['scoring_line_hits']} "
          f"best={s['best_marker_hits']} bwsel={s['per_bandwidth_selection']} "
          f"tiers={s['scoring_tier_count']} tone={s['tone_to_freq_mapping']} "
          f"coeffs=0")
    print(f"        caps={caps}")
    print(f"[823A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
