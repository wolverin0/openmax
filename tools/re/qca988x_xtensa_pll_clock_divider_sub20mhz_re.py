#!/usr/bin/env python3
"""Stage 415A — QCA988x PLL programming, clock dividers and sub-20 MHz timing.

The stage asks for four things:

  1. PLL programming functions;
  2. bandwidth dividers for **5 MHz quarter-rate**, **10 MHz half-rate**, and 20/40/80 MHz;
  3. `mac_clock`, `adc_clock`, `dac_clock`;
  4. SIFS / slot / ACK timing.

What the corpus supports, and what it refuses:

  * **two named HAL entry points exist**: `ar9300_init_pll` and `ar9300_set_power_mode`. Those are
    real defined symbols in WA and XC `ath_hal.ko` — the PLL path is named.
  * **`mac_clock`, `adc_clock`, `dac_clock` are absent as strings.** So are `quarter_rate`,
    `half_rate` and `clkdiv`. A missing name is not a missing divider; these are macros and
    register writes on the ath9k side, so the numeric divisors are not recoverable by name.
  * **`slot_time` and `ack_timeout` do exist** as strings in `ath_hal.ko`, and `slot_time`,
    `chan_width` and `bw_` in `umac.ko` — the timing vocabulary is present even though the clock
    names are not.
  * the **SGMT payloads carry no identifiers at all**. They are censused for the specific values
    5/10/20/40/80, reported as a count, and **not** interpreted as a divider table. A number
    appearing 40 times in firmware is not a table.

`pll_table_recovered = 0` and `divider_table_recovered = 0` are the honest outputs.

Radio safety: static only. No firmware loaded, no module loaded, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
XW = REPO_ROOT / "artifacts" / "firmware_re_xw_m5" / "xw_636_rootfs" / "lib" / "modules" / "2.6.32.71"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage415a_qca988x_xtensa_pll_sub20mhz_re.json")

CONTAINER = FW / "openwrt_qca988x_hw20_firmware_2_ct.bin"

MODULES = {
    "WA.v8.7.25:ath_hal.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "XC.v8.7.25:ath_hal.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "XW.v6.3.6:ath_hal.ko": XW / "ath_hal.ko",
    "WA.v8.7.25:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC.v8.7.25:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
}

# the clock and divider identifiers the stage names
CLOCK_NAMES = ["mac_clock", "adc_clock", "dac_clock", "clkdiv", "clock_div",
               "quarter_rate", "half_rate"]
# the PLL / power entry points we expect as symbols
PLL_SYMBOLS = ["ar9300_init_pll", "ar9300_set_power_mode", "ar9300_set_pll", "ar9300_pll"]
# timing vocabulary
TIMING = ["sifs", "SIFS", "slot_time", "ack_timeout", "quarter", "chan_width", "bw_", "pll"]

# bandwidths the dividers would serve, in MHz
BANDWIDTHS = [5, 10, 20, 40, 80]


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

    def matching(self, pattern: str, cap: int = 30) -> list[str]:
        rx = re.compile(pattern)
        return sorted({n for n in self.names if rx.search(n)})[:cap]


def parse_sgmt(blob: bytes) -> list[dict[str, Any]]:
    if not blob.startswith(b"QCA-ATH10K"):
        return []
    vlen = struct.unpack("<I", blob[16:20])[0]
    off = 20 + vlen
    segs = []
    while off + 8 <= len(blob):
        ie_id, ie_len = struct.unpack("<II", blob[off:off + 8])
        if off + 8 + ie_len > len(blob):
            break
        payload = blob[off + 8:off + 8 + ie_len]
        if payload[:4] == b"SGMT":
            segs.append(dict(id=ie_id, len=ie_len, payload=payload))
        off += 8 + ie_len
    return segs


def census(payload: bytes) -> dict[str, Any]:
    """Count how often each bandwidth appears as u32 and as u16. Census, not a table."""
    u32 = Counter(struct.unpack("<I", payload[o:o + 4])[0]
                  for o in range(0, len(payload) - 3, 4))
    u16 = Counter(struct.unpack("<H", payload[o:o + 2])[0]
                  for o in range(0, len(payload) - 1, 2))
    return dict(as_u32={str(b): u32.get(b, 0) for b in BANDWIDTHS},
                as_u16={str(b): u16.get(b, 0) for b in BANDWIDTHS},
                distinct_u32=len(u32))


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
        proven = set(syms.names)
        rows.append(dict(module=label, status="ok", bytes=len(b),
                         sha256=hashlib.sha256(b).hexdigest(),
                         defined_symbols=len(proven),
                         clock_names={t: b.count(t.encode()) for t in CLOCK_NAMES},
                         pll_symbols_present={t: (t in proven) for t in PLL_SYMBOLS},
                         pll_symbol_matches=syms.matching(r"pll|power_mode|clock|clkdiv", 20),
                         timing={t: b.count(t.encode()) for t in TIMING},
                         timing_contexts={t: ctx(b, t) for t in TIMING if b.count(t.encode())}))

    segs = parse_sgmt(CONTAINER.read_bytes()) if CONTAINER.exists() else []
    sgmt = [dict(id=s["id"], len=s["len"], **census(s["payload"])) for s in segs]

    ok = [r for r in rows if r.get("status") == "ok"]
    clock_hits = sum(sum(r["clock_names"].values()) for r in ok)
    pll_present = sorted({t for r in ok for t, v in r["pll_symbols_present"].items() if v})
    timing_hits = sum(sum(r["timing"].values()) for r in ok)

    report = dict(
        meta=dict(stage="415A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/qca988x_xtensa_pll_clock_divider_sub20mhz_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no firmware loaded, no module loaded, "
                        "no radio contacted",
                  method="defined-symbol lookup for the PLL/power entry points; string sweep for "
                         "the clock and timing vocabulary with context; SGMT payload census of "
                         "the five bandwidths as u32 and u16, explicitly not read as a table",
                  radio_safety="static only"),
        modules=rows,
        sgmt_segments=sgmt,
        summary=dict(modules_ok=len(ok),
                     pll_symbols_present=pll_present,
                     init_pll_present=int("ar9300_init_pll" in pll_present),
                     set_power_mode_present=int("ar9300_set_power_mode" in pll_present),
                     clock_name_hits=clock_hits,
                     clock_names_absent=all(r["clock_names"][t] == 0
                                            for r in ok for t in CLOCK_NAMES[:3]),
                     timing_token_hits=timing_hits,
                     modules_with_slot_time=sum(1 for r in ok if r["timing"]["slot_time"]),
                     modules_with_ack_timeout=sum(1 for r in ok if r["timing"]["ack_timeout"]),
                     sgmt_segments=len(sgmt),
                     sgmt_bandwidth_u32={str(b): sum(s["as_u32"][str(b)] for s in sgmt)
                                         for b in BANDWIDTHS},
                     pll_table_recovered=0,
                     divider_table_recovered=0),
        gaps=["mac_clock, adc_clock and dac_clock do not exist as strings, so no clock divider "
              "was recovered by name",
              "quarter_rate and half_rate do not exist as strings either; 5 and 10 MHz dividers "
              "are therefore not identifiable by identifier",
              "the SGMT census counts the values 5/10/20/40/80 but no table was bound to them: a "
              "value appearing N times in firmware is not a divider table",
              "ar9300_init_pll is a symbol, not a decoded routine: its register sequence was not "
              "read",
              "SIFS appears in no module; slot_time and ack_timeout exist as strings but their "
              "values were not resolved",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[415A] modules={s['modules_ok']} pll={s['pll_symbols_present']} "
          f"clock_hits={s['clock_name_hits']} timing={s['timing_token_hits']} "
          f"slot_time={s['modules_with_slot_time']} ack={s['modules_with_ack_timeout']} "
          f"sgmt={s['sgmt_segments']}")
    print(f"        bandwidth census u32={s['sgmt_bandwidth_u32']} table=0")
    for m in ok:
        print(f"        {m['module']:<24} {m['bytes']:>7}B timing={sorted(m['timing_contexts'])}")
    print(f"[415A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
