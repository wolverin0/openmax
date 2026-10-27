#!/usr/bin/env python3
"""Stage 371A — QCA988x `rx_ppdu_end` 84-byte descriptor, EVM per spatial stream, ranging.

Two premises were checked before any analysis and both fail:

  * **`ath10k_core.ko` does not exist** anywhere under `artifacts/`. The airOS 8 AC images ship
    the vendor stack (`umac.ko` + `ath_dev.ko`), not the mainline `ath10k`. A glob for
    `ath10k*.ko` returns 0 files.
  * **the descriptor field names do not appear.** Exact-string counts in `umac.ko`:
    `rx_ppdu_end` 0, `evm_p0` 0, `locationing_timestamp` 0, `ppdu_end` 0. In `ath_dev.ko`: all 0.

So the `rx_ppdu_end_qca988x` layout described in the task is a **mainline ath10k** structure and
is not named in these binaries. Nothing is reported as if it were present.

What *is* present and does carry the discard point:

  * **`htt_rx_amsdu_pop` appears 4 times in `umac.ko`** — the function the task names as the
    place where `skb_pull` throws the descriptor away. That symbol is real.

The tool therefore reports: the absence of the ath10k module and of the field names, the presence
of the pop path, and the 84-byte / dword-18 constants if they are materialised in code. It does
**not** invent an EVM table.

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
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage371a_qca988x_rx_ppdu_end_evm_ranging_re.json"

MODULES = {
    "WA.v8.7.25:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA.v8.7.25:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC.v8.7.25:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC.v8.7.25:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
}

# field names the task expects the descriptor to carry
ATH10K_FIELDS = ["rx_ppdu_end", "evm_p0", "evm_p15", "locationing_timestamp",
                 "ppdu_end", "htt_rx_amsdu_pop"]

# descriptor geometry from the task: 84 bytes total, dword 18 at byte offset 72
DESC_BYTES = 84
DWORD18_OFF = 72
# 80 MHz sampling: 12.5 ns per sample, 1.87 m round-trip resolution
SAMPLE_NS_80MHZ = 12.5
RANGE_M_PER_NS = 0.299792458 / 2.0   # round trip, metres per nanosecond


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

    def geometry_constants(self, names: set[str]) -> dict[str, Any]:
        """Immediates equal to the 84-byte size, the 72-byte dword-18 offset, or 19 dwords."""
        found: Counter[str] = Counter()
        sites: list[dict[str, Any]] = []
        targets = {DESC_BYTES: "size_84", DWORD18_OFF: "dword18_off_72", 19: "dwords_19",
                   21: "dwords_21", 16: "evm_pairs_16"}
        for nm, val, sz, shndx, sn in self.syms:
            if nm not in names or sn not in (".text", ".text.unlikely", ".init.text"):
                continue
            for k in range(0, min(max(sz, 0x100), 0x600), 4):
                w = self.u32(val + k)
                if w is None:
                    continue
                op, rs, _rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, \
                                   (w >> 16) & 0x1F, w & 0xFFFF
                if op != 0x09 or rs != 0:
                    continue
                v = s16(imm)
                if v in targets:
                    found[targets[v]] += 1
                    if len(sites) < 40:
                        sites.append(dict(constant=targets[v], value=v,
                                          function=nm, at=f"0x{val + k:06x}"))
        return dict(histogram=dict(found), sites=sites)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    ath10k = sorted(str(p.relative_to(REPO_ROOT)).replace("\\", "/")
                    for p in REPO_ROOT.joinpath("artifacts").rglob("ath10k*.ko"))

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        ko = Ko(path)
        raw = ko.data
        field_hits = {f: raw.count(f.encode()) for f in ATH10K_FIELDS}
        defined = sorted({s[0] for s in ko.syms if s[3] != 0 and s[0]})
        pop_syms = sorted({s for s in defined if re.search(r"htt_rx_amsdu|amsdu_pop", s, re.I)})
        evm_syms = sorted({s for s in defined if re.search(r"evm|rssi|ppdu", s, re.I)})
        geo = ko.geometry_constants(set(pop_syms))
        rows.append(dict(module=label, status="ok", bytes=len(raw),
                         sha256=hashlib.sha256(raw).hexdigest(),
                         field_string_hits=field_hits,
                         defined=len(defined),
                         amsdu_pop_symbols=pop_syms,
                         evm_ppdu_symbols=evm_syms[:40],
                         geometry=geo))

    ok = [r for r in rows if r.get("status") == "ok"]
    report = dict(
        meta=dict(stage="371A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/qca988x_rx_ppdu_end_84byte_evm_ranging_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  premise_corrections=[
                      "ath10k_core.ko does not exist under artifacts/ (glob ath10k*.ko = 0); "
                      "the AC images ship the vendor umac.ko + ath_dev.ko",
                      "the descriptor field names are absent: rx_ppdu_end, evm_p0, evm_p15, "
                      "locationing_timestamp and ppdu_end all count 0 in every module",
                  ],
                  present_evidence="htt_rx_amsdu_pop is present in umac.ko (4 raw hits), so "
                                   "the discard path the task describes is real even though the "
                                   "descriptor is not the ath10k one",
                  radio_safety="static only"),
        ath10k_modules_found=ath10k,
        modules=rows,
        ranging_math=dict(sample_rate_mhz=80.0, sample_ns=SAMPLE_NS_80MHZ,
                          metres_per_ns=round(RANGE_M_PER_NS, 6),
                          round_trip_metres=round(SAMPLE_NS_80MHZ * RANGE_M_PER_NS, 4),
                          note="12.5 ns at c/2 gives 1.874 m; matches the 1.87 m in the task"),
        summary=dict(ath10k_core_present=bool(ath10k),
                     modules_ok=len(ok),
                     modules_with_field_names=sum(
                         1 for r in ok if any(v > 0 for v in r["field_string_hits"].values())),
                     modules_with_amsdu_pop=sum(1 for r in ok if r["amsdu_pop_symbols"]),
                     amsdu_pop_hits=max((r["field_string_hits"].get("htt_rx_amsdu_pop", 0)
                                         for r in ok), default=0),
                     evm_symbol_count=max((len(r["evm_ppdu_symbols"]) for r in ok), default=0),
                     geometry_constants=max((sum(r["geometry"]["histogram"].values())
                                             for r in ok), default=0),
                     evm_table_recovered=0),
        gaps=["the 84-byte rx_ppdu_end descriptor with evm_p0..evm_p15 is an ath10k structure "
              "and is not present in the vendor modules: zero field-name hits",
              "no EVM table was recovered and none is claimed",
              "the dword-18 locationing timestamp field was not located; the 72-byte offset "
              "constant may not exist in this stack",
              "the ranging arithmetic is reported as a constant, not as a decoded field",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[371A] ath10k={s['ath10k_core_present']} modules={s['modules_ok']} "
          f"field_names={s['modules_with_field_names']} amsdu_pop={s['modules_with_amsdu_pop']} "
          f"pop_hits={s['amsdu_pop_hits']} geo={s['geometry_constants']} evm_table=0")
    print(f"        ranging: {report['ranging_math']['round_trip_metres']} m per sample")
    for r in ok:
        print(f"        {r['module']:<24} {r['bytes']:>8}B "
              f"pop={r['amsdu_pop_symbols'][:1]} geo={r['geometry']['histogram']}")
    print(f"[371A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
