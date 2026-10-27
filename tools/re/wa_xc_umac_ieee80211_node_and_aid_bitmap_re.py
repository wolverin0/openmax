#!/usr/bin/env python3
"""Stage 325A — WA/XC `umac.ko` ieee80211_node lifecycle, AID bitmap and PS-Poll/U-APSD.

`umac.ko` is the upper-MAC module of the airOS 8 AC images: MIPS32 big-endian `ET_REL`,
2.36 MB (WA) / 2.36 MB (XC), ~4.8 k symbols.

The stage asks for four things:

  1. the `ieee80211_node` lifecycle;
  2. AID bitmap scaling to 64 / 128 CPEs;
  3. PS-Poll / U-APSD handling;
  4. inactivity timers.

What this tool establishes, and what it explicitly does not:

  * **symbol buckets** — every defined symbol matching node/peer/sta, aid/bitmap/assoc,
    pspoll/uapsd/sleep/power_save, inactivity/idle/timeout/age, auth/acl.
  * **AID ceiling constants** — the small powers of two (32, 64, 128, 256) materialised as
    immediates inside AID-named functions. A value being present is a **candidate ceiling**,
    not proof of the bitmap width.
  * **string evidence** — `.rodata` literals mentioning aid/assoc/pspoll/uapsd/inactiv.

No node state machine is decoded: the transition graph is not traced.

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
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage325a_wa_xc_umac_node_aid_re.json"

MODULES = {
    "WA.v8.7.25:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC.v8.7.25:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
}

PATTERNS = {
    "node": re.compile(r"ieee80211_node|node_|peer|sta_|_sta\b|vap", re.I),
    "aid": re.compile(r"\baid\b|aid_|bitmap|assoc|max_sta|maxsta", re.I),
    "pspoll": re.compile(r"pspoll|ps_poll|uapsd|u_apsd|power_save|sleep|ps_", re.I),
    "inactivity": re.compile(r"inactiv|idle|timeout|age_|expire|stale", re.I),
    "auth": re.compile(r"auth|acl|deny|allow|acl_", re.I),
}

# candidate AID ceilings for a 64 / 128 CPE deployment
AID_CEILINGS = {32, 64, 128, 256}


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

    def aid_constants(self, names: set[str], limit: int = 0x800) -> dict[str, Any]:
        """MIPS `addiu $zero,N` immediates inside AID-named functions."""
        ceil: Counter[int] = Counter()
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
                if v in AID_CEILINGS:
                    ceil[v] += 1
                elif 0 < v <= 0x1000:
                    other[v] += 1
        return dict(ceiling_candidates={str(k): v for k, v in sorted(ceil.items())},
                    ceiling_total=sum(ceil.values()),
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
        aid_strings = sorted(s for s in strings
                             if re.search(r"\baid\b|assoc|pspoll|uapsd|inactiv", s, re.I))[:40]
        aid_names = set(buckets["aid"]["symbols"])
        consts = ko.aid_constants(aid_names)
        rows.append(dict(module=label, status="ok", bytes=len(ko.data),
                         sha256=hashlib.sha256(ko.data).hexdigest(),
                         endian="little" if ko.endian == "<" else "big",
                         defined=len(defined), buckets=buckets,
                         aid_ceilings=consts["ceiling_candidates"],
                         aid_ceiling_total=consts["ceiling_total"],
                         other_constants=consts["other_constants"],
                         aid_strings=aid_strings))

    ok = [r for r in rows if r.get("status") == "ok"]
    report = dict(
        meta=dict(stage="325A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/wa_xc_umac_ieee80211_node_and_aid_bitmap_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method=".symtab name classification into node/aid/pspoll/inactivity/auth "
                         "buckets; addiu $zero,N histogram inside AID-named functions split "
                         "into the 32/64/128/256 ceiling candidates; .rodata string sweep for "
                         "aid/assoc/pspoll/uapsd/inactiv",
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     node_symbols=max((r["buckets"]["node"]["count"] for r in ok), default=0),
                     aid_symbols=max((r["buckets"]["aid"]["count"] for r in ok), default=0),
                     pspoll_symbols=max((r["buckets"]["pspoll"]["count"] for r in ok),
                                         default=0),
                     inactivity_symbols=max((r["buckets"]["inactivity"]["count"] for r in ok),
                                            default=0),
                     auth_symbols=max((r["buckets"]["auth"]["count"] for r in ok), default=0),
                     aid_ceiling_values=max((len(r["aid_ceilings"]) for r in ok), default=0),
                     aid_ceiling_sites=max((r["aid_ceiling_total"] for r in ok), default=0),
                     aid_strings=max((len(r["aid_strings"]) for r in ok), default=0)),
        gaps=["the AID ceilings are immediates inside AID-named functions, not proof of the "
              "bitmap width: 64 and 128 could be a count, a mask or a loop bound",
              "no ieee80211_node lifecycle state machine was decoded",
              "PS-Poll and U-APSD are a symbol bucket, not a handshake trace",
              "inactivity timers were not resolved to numeric seconds or ticks",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[325A] modules={s['modules_ok']} node={s['node_symbols']} aid={s['aid_symbols']} "
          f"pspoll={s['pspoll_symbols']} inact={s['inactivity_symbols']} "
          f"auth={s['auth_symbols']}")
    print(f"        aid_ceilings={s['aid_ceiling_values']} sites={s['aid_ceiling_sites']} "
          f"strings={s['aid_strings']}")
    for r in ok:
        print(f"        {r['module']:<24} {r['bytes']:>9}B ceilings={r['aid_ceilings']}")
    print(f"[325A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
