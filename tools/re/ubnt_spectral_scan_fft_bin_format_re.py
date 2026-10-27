#!/usr/bin/env python3
"""Stage 327A — `ath_spectral.ko` FFT bin format, noise-floor calibration and ubntspecd shm.

`ath_spectral.ko` is the spectral-scan module of the airOS 8 AC images: MIPS32 big-endian
`ET_REL`, 37,656 bytes, in both WA and XC. `ath_dev.ko` is included because the spectral
sample plumbing is partly there.

The stage asks for three things:

  1. the FFT bin format;
  2. RSSI / noise-floor calibration;
  3. the shared-memory layout with `ubntspecd`.

What this tool establishes, and what it refuses to claim:

  * **symbol buckets** — fft/bin/spectr/sample/window, noise/nf/floor/calib/rssi,
    shm/shared/mmap/specd, radar/pulse/pri/width, chan/bw/freq.
  * **bin-count and calibration constants** — small immediates inside fft- and noise-named
    functions. A `64` or `128` inside an FFT function is a **candidate bin count**; the actual
    bin width in dB and the byte layout are not derived.
  * **shm evidence** — whether any symbol mentions `specd`/`shm`, and the string literals that
    name a shared path.

No bin descriptor was decoded and no shared-memory struct was laid out.

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
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage327a_ubnt_spectral_fft_re.json"

MODULES = {
    "WA.v8.7.25:ath_spectral.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_spectral.ko",
    "XC.v8.7.25:ath_spectral.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_spectral.ko",
    "WA.v8.7.25:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC.v8.7.25:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
}

PATTERNS = {
    "fft": re.compile(r"fft|bin|spectr|sample|window|dc_|tone", re.I),
    "noise": re.compile(r"noise|nf_|_nf|floor|calib|rssi|dbm", re.I),
    "shm": re.compile(r"shm|shared|mmap|specd|ubntspec|user_?space", re.I),
    "radar": re.compile(r"radar|pulse|chirp|pri|width|burst", re.I),
    "channel": re.compile(r"chan|bw|freq|band|fft_?size", re.I),
}

# candidate FFT bin counts for an 802.11 spectral scan
BIN_COUNTS = {32, 64, 128, 256, 512}


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

    def constants(self, names: set[str], limit: int = 0x800) -> dict[str, Any]:
        bins: Counter[int] = Counter()
        other: Counter[int] = Counter()
        for nm, val, sz, shndx, sn in self.syms:
            if nm not in names or sn not in (".text", ".text.unlikely", ".init.text"):
                continue
            for k in range(0, min(max(sz, 0x100), limit), 4):
                w = self.u32(val + k)
                if w is None:
                    continue
                op, rs, _rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, \
                                   (w >> 16) & 0x1F, w & 0xFFFF
                if op != 0x09 or rs != 0:
                    continue
                v = s16(imm)
                if v in BIN_COUNTS:
                    bins[v] += 1
                elif 0 < v <= 0x1000:
                    other[v] += 1
        return dict(bin_candidates={str(k): v for k, v in sorted(bins.items())},
                    bin_total=sum(bins.values()),
                    other_constants={str(k): v for k, v in other.most_common(20)})

    def strings(self, cap: int = 100) -> list[str]:
        out = set()
        for h in self.secs:
            if h["type"] != 1 or not h["name"].startswith(".rodata"):
                continue
            blob = self.data[h["off"]:h["off"] + h["size"]]
            for m in re.finditer(rb"[\x20-\x7e]{4,}", blob):
                s = m.group().decode("latin1")
                if 4 <= len(s) <= cap:
                    out.add(s)
        return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        ko = Ko(path)
        defined = sorted({s[0] for s in ko.syms if s[3] != 0 and s[0]})
        buckets: dict[str, Any] = {}
        for name, rx in PATTERNS.items():
            hits = sorted({s for s in defined if rx.search(s)})
            buckets[name] = dict(count=len(hits), symbols=hits[:60])
        strings = ko.strings()
        spectral_strings = sorted(s for s in strings
                                  if re.search(r"specd|spectral|fft|noise|radar", s, re.I))[:40]
        fft_names = set(buckets["fft"]["symbols"])
        noise_names = set(buckets["noise"]["symbols"])
        fft_c = ko.constants(fft_names)
        noise_c = ko.constants(noise_names)
        rows.append(dict(module=label, status="ok", bytes=len(ko.data),
                         sha256=hashlib.sha256(ko.data).hexdigest(),
                         defined=len(defined), buckets=buckets,
                         fft_bin_candidates=fft_c["bin_candidates"],
                         fft_bin_total=fft_c["bin_total"],
                         noise_constants=noise_c["other_constants"],
                         spectral_strings=spectral_strings))

    ok = [r for r in rows if r.get("status") == "ok"]
    spectral = [r for r in ok if "ath_spectral" in r["module"]]
    report = dict(
        meta=dict(stage="327A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/ubnt_spectral_scan_fft_bin_format_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method=".symtab classification into fft/noise/shm/radar/channel buckets; "
                         "addiu $zero,N histogram inside fft- and noise-named functions split "
                         "into 32/64/128/256/512 bin-count candidates; .rodata sweep for "
                         "specd/spectral/fft/noise/radar",
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     spectral_modules=len(spectral),
                     fft_symbols=max((r["buckets"]["fft"]["count"] for r in spectral),
                                     default=0),
                     noise_symbols=max((r["buckets"]["noise"]["count"] for r in spectral),
                                       default=0),
                     shm_symbols=max((r["buckets"]["shm"]["count"] for r in ok), default=0),
                     radar_symbols=max((r["buckets"]["radar"]["count"] for r in spectral),
                                       default=0),
                     channel_symbols=max((r["buckets"]["channel"]["count"] for r in spectral),
                                         default=0),
                     bin_candidate_values=max((len(r["fft_bin_candidates"]) for r in spectral),
                                              default=0),
                     bin_candidate_sites=max((r["fft_bin_total"] for r in spectral), default=0),
                     spectral_strings=max((len(r["spectral_strings"]) for r in ok), default=0)),
        gaps=["a 64/128/256 immediate inside an FFT-named function is a candidate bin count, "
              "not the bin width or the descriptor layout",
              "no FFT bin format was decoded: neither the dB encoding nor the byte stride",
              "no ubntspecd shared-memory struct was laid out; only symbol and string presence "
              "is reported",
              "noise-floor calibration constants are a histogram, not a calibration table",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[327A] modules={s['modules_ok']} spectral={s['spectral_modules']} "
          f"fft={s['fft_symbols']} noise={s['noise_symbols']} shm={s['shm_symbols']} "
          f"radar={s['radar_symbols']}")
    print(f"        bin_values={s['bin_candidate_values']} sites={s['bin_candidate_sites']} "
          f"strings={s['spectral_strings']}")
    for r in spectral:
        print(f"        {r['module']:<30} {r['bytes']:>6}B fft={r['buckets']['fft']['count']:<3} "
              f"bins={r['fft_bin_candidates']}")
    print(f"[327A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
