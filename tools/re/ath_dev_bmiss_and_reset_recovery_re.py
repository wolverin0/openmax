#!/usr/bin/env python3
"""Stage 326A — `ath_dev.ko` beacon miss, stuck-beacon recovery, BB/MAC hang and deaf reset.

Three images, three kernel ABIs:

| Image | Path | ABI |
| :--- | :--- | :--- |
| `WA.v8.7.25` (AC) | `lib/modules/2.6.32.68/ath_dev.ko` | 2.6.32.68 |
| `XC.v8.7.25` (AC) | `lib/modules/2.6.32.68/ath_dev.ko` | 2.6.32.68 |
| `XW.v6.3.6` (M5) | `lib/modules/2.6.32.71/ath_dev.ko` | **2.6.32.71** |

The stage asks for four behaviours:

  1. beacon miss (`bmiss`);
  2. stuck-beacon recovery;
  3. BB/MAC hang detection (`ath_hw_hang_check`);
  4. deaf-state reset paths.

What this tool establishes, and what it refuses to claim:

  * **symbol buckets** — every defined symbol matching bmiss/beacon_miss, hang/stuck/deaf,
    reset/recover/reinit, bb_/mac_/pcu, watchdog/timeout.
  * **the named entry point** — whether a symbol literally called `ath_hw_hang_check` (or the
    closest named equivalent) exists in each image.
  * **threshold constants** — small immediates inside bmiss- and watchdog-named functions,
    reported as a histogram. A value being present is a **candidate threshold**, not proof it
    is the miss count or the hang timer.

No recovery state machine is decoded.

Radio safety: static only. No module loaded, no radio contacted.
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
XW = REPO_ROOT / "artifacts" / "firmware_re_xw_m5"
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage326a_ath_dev_bmiss_hang_recovery_re.json"

MODULES = {
    "WA.v8.7.25": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC.v8.7.25": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XW.v6.3.6": XW / "xw_636_rootfs/lib/modules/2.6.32.71/ath_dev.ko",
}

PATTERNS = {
    "bmiss": re.compile(r"bmiss|beacon_miss|missed_beacon|beacon", re.I),
    "hang": re.compile(r"hang|stuck|deaf|stall|wedge|stuck_beacon", re.I),
    "reset": re.compile(r"reset|recover|restart|reinit|warm|restart_hw", re.I),
    "bbmac": re.compile(r"bb_|mac_|pcu|phy_err|mib", re.I),
    "watchdog": re.compile(r"watchdog|timeout|timer|panic|assert", re.I),
}

# the specific entry point the stage names
HANG_CHECK = re.compile(r"ath_hw_hang_check|hw_hang_check|hang_check", re.I)


def s16(v: int) -> int:
    return v - 0x10000 if v >= 0x8000 else v


class Ko:
    """ET_REL reader for MIPS32 big-endian modules."""

    def __init__(self, path: Path) -> None:
        self.data = d = path.read_bytes()
        if d[:4] != b"\x7fELF":
            raise ValueError(f"not ELF: {path}")
        E = "<" if d[5] == 1 else ">"
        self.endian = E
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        secs = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, info, al, es = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            secs.append(dict(name_off=nm, type=typ, flags=fl, addr=addr, off=off,
                             size=sz, link=link, info=info))
        stro = secs[shstr]["off"]
        for h in secs:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.secs = secs
        self.by_name = {h["name"]: h for h in secs}
        tx = self.by_name.get(".text")
        self.text = d[tx["off"]:tx["off"] + tx["size"]] if tx else b""
        self.syms: list[tuple[str, int, int, int, str]] = []
        st = self.by_name.get(".symtab")
        if st:
            ss = secs[st["link"]]
            for i in range(st["size"] // 16):
                o = st["off"] + i * 16
                nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", d[o:o + 16])
                e = d.find(b"\0", ss["off"] + nm)
                sn = secs[shndx]["name"] if 0 < shndx < len(secs) else ""
                self.syms.append((d[ss["off"] + nm:e].decode("latin1"), val, sz, shndx, sn))

    def u32(self, off: int) -> int | None:
        if off < 0 or off + 4 > len(self.text):
            return None
        return struct.unpack(self.endian + "I", self.text[off:off + 4])[0]

    def thresholds(self, names: set[str], limit: int = 0x800) -> dict[str, Any]:
        """MIPS `addiu $zero,N` immediates inside the named functions."""
        hist: Counter[int] = Counter()
        for nm, val, sz, shndx, sn in self.syms:
            if nm not in names or sn not in (".text", ".text.unlikely", ".init.text"):
                continue
            for k in range(0, min(max(sz, 0x100), limit), 4):
                w = self.u32(val + k)
                if w is None:
                    continue
                op, rs, _rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, \
                                   (w >> 16) & 0x1F, w & 0xFFFF
                if op == 0x09 and rs == 0 and 0 < s16(imm) <= 0x400:
                    hist[s16(imm)] += 1
        return dict(histogram={str(k): v for k, v in sorted(hist.items())},
                    distinct=len(hist), total=sum(hist.values()))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(image=label, status="absent"))
            continue
        ko = Ko(path)
        defined = sorted({s[0] for s in ko.syms if s[3] != 0 and s[0]})
        buckets: dict[str, Any] = {}
        for name, rx in PATTERNS.items():
            hits = sorted({s for s in defined if rx.search(s)})
            buckets[name] = dict(count=len(hits), symbols=hits[:60])
        hang_syms = sorted({s for s in defined if HANG_CHECK.search(s)})
        bmiss_names = set(buckets["bmiss"]["symbols"])
        wd_names = set(buckets["watchdog"]["symbols"])
        bmiss_c = ko.thresholds(bmiss_names)
        wd_c = ko.thresholds(wd_names)
        rows.append(dict(image=label, status="ok", bytes=len(ko.data),
                         sha256=hashlib.sha256(ko.data).hexdigest(),
                         abi=path.parent.name, defined=len(defined),
                         buckets=buckets, hang_check_symbols=hang_syms,
                         bmiss_thresholds=bmiss_c, watchdog_thresholds=wd_c))

    ok = [r for r in rows if r.get("status") == "ok"]
    report = dict(
        meta=dict(stage="326A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/ath_dev_bmiss_and_reset_recovery_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method=".symtab classification into bmiss/hang/reset/bbmac/watchdog "
                         "buckets; direct lookup of the ath_hw_hang_check family; "
                         "addiu $zero,N histogram inside bmiss- and watchdog-named functions",
                  note="XW.v6.3.6 uses kernel ABI 2.6.32.71, the AC images use 2.6.32.68",
                  radio_safety="static only"),
        modules=rows,
        summary=dict(images_ok=len(ok),
                     bmiss_symbols=max((r["buckets"]["bmiss"]["count"] for r in ok),
                                       default=0),
                     hang_symbols=max((r["buckets"]["hang"]["count"] for r in ok), default=0),
                     reset_symbols=max((r["buckets"]["reset"]["count"] for r in ok), default=0),
                     bbmac_symbols=max((r["buckets"]["bbmac"]["count"] for r in ok), default=0),
                     watchdog_symbols=max((r["buckets"]["watchdog"]["count"] for r in ok),
                                          default=0),
                     hang_check_found=sum(1 for r in ok if r["hang_check_symbols"]),
                     bmiss_threshold_values=max((r["bmiss_thresholds"]["distinct"] for r in ok),
                                                default=0),
                     watchdog_threshold_values=max((r["watchdog_thresholds"]["distinct"]
                                                    for r in ok), default=0)),
        gaps=["a named ath_hw_hang_check may be absent while the behaviour exists under another "
              "name; absence is reported, not interpreted as no hang detection",
              "bmiss and watchdog immediates are candidate thresholds, not verified miss counts "
              "or timer values",
              "no BB/MAC hang recovery state machine was decoded",
              "the deaf-state reset path was not traced",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[326A] images={s['images_ok']} bmiss={s['bmiss_symbols']} hang={s['hang_symbols']} "
          f"reset={s['reset_symbols']} bbmac={s['bbmac_symbols']} "
          f"wd={s['watchdog_symbols']} hang_check={s['hang_check_found']}")
    for r in ok:
        print(f"        {r['image']:<11} abi={r['abi']:<10} {r['bytes']:>7}B "
              f"bmiss={r['buckets']['bmiss']['count']:<3} "
              f"hang_check={r['hang_check_symbols'][:2]}")
    print(f"[326A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
