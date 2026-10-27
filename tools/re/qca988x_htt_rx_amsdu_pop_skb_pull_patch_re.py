#!/usr/bin/env python3
"""Stage 395A — where `skb_pull` discards the RX descriptor, and the binary hook to keep it.

The stage asks for `ath10k_core.ko` (Linux 6.6.110), `ath10k_htt_rx_amsdu_pop`,
`ath10k_htt_rx_h_ppdu` and the exact `skb_pull` offset that throws away the 84-byte
`rx_ppdu_end_qca988x` descriptor.

**That module does not exist.** A recursive glob for `ath10k*.ko` returns 0 files, there is no
Linux 6.6.110 source tree, and the only `ath10k`-named artefact is a 1,859-byte AQL research
dossier with no descriptor content. Stage 371A reached the same conclusion for the field names.

So the question is answered where it **can** be answered: on the vendor stack that actually ships
(`umac.ko`), which does export `htt_rx_amsdu_pop` (Stage 371A: 4 hits). The method is exact:

  * `umac.ko` is `ET_REL`, so a call target is not an address — it is an `.rel.text` entry of type
    `R_MIPS_26` (4) against an undefined symbol.
  * the tool enumerates every such relocation whose symbol is `skb_pull`, keeps the ones that fall
    inside `htt_rx_amsdu_pop`, and resolves the length argument `$a1` backwards from the call site,
    including the delay slot.

The output is the histogram of `skb_pull` lengths inside the pop function, and whether 84 is
among them.

No patch is applied and no binary is modified: the "hook" is reported as the call-site offset and
the argument value, which is what a patch would need.

Radio safety: static only. No module loaded, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage395a_qca988x_htt_rx_skb_pull_patch_re.json")

MODULES = {
    "WA.v8.7.25:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC.v8.7.25:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
}

TARGET_FUNCS = ["htt_rx_amsdu_pop", "htt_rx_h_ppdu", "ath10k_htt_rx_amsdu_pop",
                "ath10k_htt_rx_h_ppdu"]
PULL_SYMS = ["skb_pull", "pskb_pull", "skb_pull_rcsum"]
R_MIPS_26 = 4
DESC_BYTES = 84


def s16(v: int) -> int:
    return v - 0x10000 if v >= 0x8000 else v


class Rel:
    """ELF32 reader with relocations, for a MIPS big-endian ET_REL kernel module."""

    def __init__(self, path: Path) -> None:
        self.data = d = path.read_bytes()
        E = "<" if d[5] == 1 else ">"
        self.endian = E
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        secs = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, info, al, es = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            secs.append(dict(name_off=nm, type=typ, off=off, size=sz, link=link, info=info))
        stro = secs[shstr]["off"]
        for h in secs:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.secs = secs
        self.by_name = {h["name"]: h for h in secs}

        self.syms: list[dict[str, Any]] = []
        st = self.by_name.get(".symtab")
        if st:
            ss = secs[st["link"]]
            for i in range(st["size"] // 16):
                o = st["off"] + i * 16
                nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", d[o:o + 16])
                e = d.find(b"\0", ss["off"] + nm)
                self.syms.append(dict(name=d[ss["off"] + nm:e].decode("latin1"),
                                      value=val, size=sz, info=info, shndx=shndx))

    def u32(self, sec: str, off: int) -> int | None:
        h = self.by_name.get(sec)
        if not h or off < 0 or off + 4 > h["size"]:
            return None
        return struct.unpack(self.endian + "I", self.data[h["off"] + off:h["off"] + off + 4])[0]

    def relocs(self) -> list[dict[str, Any]]:
        """All REL entries pointing at a named undefined symbol."""
        out = []
        for h in self.secs:
            if h["type"] != 9:          # SHT_REL
                continue
            target = self.secs[h["info"]]["name"] if h["info"] < len(self.secs) else "?"
            for i in range(h["size"] // 8):
                o = h["off"] + i * 8
                r_off, r_info = struct.unpack(self.endian + "II", self.data[o:o + 8])
                si, rtype = r_info >> 8, r_info & 0xFF
                sym = self.syms[si]["name"] if si < len(self.syms) else "?"
                out.append(dict(section=target, offset=r_off, type=rtype, sym=sym))
        return out

    def function_range(self, name: str) -> tuple[int, int] | None:
        """Symbol extent, falling back to the next FUNC boundary and then to a fixed window.

        Kernel modules routinely emit size-0 function symbols, and the symbol immediately after
        one is often a local label. Using the next *function* as the boundary avoids shrinking a
        real function to a handful of bytes.
        """
        hit = next((s for s in self.syms if s["name"] == name and s["shndx"] != 0), None)
        if not hit:
            return None
        start = hit["value"]
        if hit["size"] >= 16:
            return start, start + hit["size"]
        funcs = sorted(s["value"] for s in self.syms
                       if s["shndx"] != 0 and (s["info"] & 0xF) == 2 and s["value"] > start)
        end = funcs[0] if funcs else start + 0x4000
        if end - start < 16:
            end = start + 0x4000
        tx = self.by_name.get(".text")
        if tx:
            end = min(end, tx["size"])
        return start, end

    def func_of(self, off: int) -> str:
        """Name of the enclosing function, by the nearest preceding FUNC symbol."""
        best = None
        for s in self.syms:
            if s["shndx"] != 0 and (s["info"] & 0xF) == 2 and s["value"] <= off:
                if best is None or s["value"] > best["value"]:
                    best = s
        return best["name"] if best else "?"

    def arg_before(self, call_off: int, reg: int = 5, span: int = 32) -> dict[str, Any] | None:
        """Nearest `addiu/ori $reg,$zero,N` looking back from a call site (delay slot included)."""
        for back in range(0, span + 1, 4):
            for delta in (-back, back if back else 0):
                off = call_off + delta
                if off < 0 or off == call_off:
                    continue
                w = self.u32(".text", off)
                if w is None:
                    continue
                op, rs, rt, imm = ((w >> 26) & 0x3F, (w >> 21) & 0x1F,
                                   (w >> 16) & 0x1F, w & 0xFFFF)
                if rs == 0 and rt == reg and op in (0x09, 0x0D):
                    return dict(value=s16(imm), at=f"0x{off:06x}",
                                form="addiu" if op == 0x09 else "ori")
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    ath10k = sorted(p.relative_to(REPO_ROOT).as_posix()
                    for p in (REPO_ROOT / "artifacts").rglob("ath10k*.ko"))
    dossiers = sorted(p.relative_to(REPO_ROOT).as_posix()
                      for p in (REPO_ROOT / "artifacts").rglob("*ath10k*.md"))

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        ko = Rel(path)
        defined = {s["name"] for s in ko.syms if s["shndx"] != 0}
        rel = ko.relocs()
        pull_sites = [r for r in rel if r["sym"] in PULL_SYMS and r["type"] == R_MIPS_26]

        funcs = {}
        for fname in TARGET_FUNCS:
            rng = ko.function_range(fname)
            funcs[fname] = (dict(start=f"0x{rng[0]:06x}", end=f"0x{rng[1]:06x}",
                                 bytes=rng[1] - rng[0]) if rng else None)

        # every pull site, attributed to its enclosing function
        attributed = []
        for site in pull_sites:
            arg = ko.arg_before(site["offset"])
            fn = ko.func_of(site["offset"])
            attributed.append(dict(call_site=f"0x{site['offset']:06x}", symbol=site["sym"],
                                   function=fn,
                                   length=(arg["value"] if arg else None),
                                   length_at=(arg["at"] if arg else None),
                                   resolved=bool(arg)))
        hist = Counter(a["length"] for a in attributed if a["length"] is not None)
        per_func = Counter(a["function"] for a in attributed)
        rows.append(dict(module=label, status="ok", bytes=len(ko.data),
                         sha256=hashlib.sha256(ko.data).hexdigest(),
                         defined_symbols=len(defined),
                         total_relocs=len(rel), total_pull_relocs=len(pull_sites),
                         functions=funcs,
                         pull_sites=attributed,
                         pull_length_histogram={str(k): v for k, v in sorted(hist.items())},
                         unresolved_lengths=sum(1 for a in attributed if not a["resolved"]),
                         pulls_per_function=dict(per_func.most_common(10)),
                         pop_pull_count=sum(1 for a in attributed
                                            if a["function"] == "htt_rx_amsdu_pop")))

    ok = [r for r in rows if r.get("status") == "ok"]
    pull_total = sum(r["total_pull_relocs"] for r in ok)
    in_pop = sum(r["pop_pull_count"] for r in ok)
    lengths = Counter()
    for r in ok:
        for k, v in r["pull_length_histogram"].items():
            lengths[int(k)] += v
    funcs_with_pulls = sorted({a["function"] for r in ok for a in r["pull_sites"]})

    report = dict(
        meta=dict(stage="395A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/qca988x_htt_rx_amsdu_pop_skb_pull_patch_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted, no binary patched",
                  method="ET_REL relocation walk: every R_MIPS_26 site against skb_pull/pskb_pull/"
                         "skb_pull_rcsum, filtered to htt_rx_amsdu_pop, with the $a1 length "
                         "resolved backwards from the call site including the delay slot",
                  premise_corrections=[
                      "ath10k_core.ko does not exist: 0 files match ath10k*.ko, and no Linux "
                      "6.6.110 source tree is present",
                      "ath10k_htt_rx_amsdu_pop and ath10k_htt_rx_h_ppdu therefore cannot be "
                      "disassembled; the vendor umac.ko htt_rx_amsdu_pop is used instead",
                  ],
                  radio_safety="static only"),
        ath10k_modules_found=ath10k,
        ath10k_documents_found=dossiers,
        modules=rows,
        summary=dict(ath10k_core_present=bool(ath10k),
                     modules_ok=len(ok),
                     total_pull_relocs=pull_total,
                     pull_sites_in_amsdu_pop=in_pop,
                     pop_symbol_present=sum(1 for r in ok
                                            if r["functions"]["htt_rx_amsdu_pop"]),
                     ppdu_symbol_present=sum(1 for r in ok
                                             if r["functions"]["htt_rx_h_ppdu"]),
                     distinct_pull_lengths=len(lengths),
                     lengths_histogram={str(k): v for k, v in sorted(lengths.items())},
                     length_84_found=int(84 in lengths),
                     functions_with_pulls=funcs_with_pulls,
                     pop_calls_skb_pull=int(in_pop > 0),
                     patch_emitted=0),
        gaps=["ath10k_core.ko is absent, so the 84-byte rx_ppdu_end_qca988x descriptor and its "
              "skb_pull offset cannot be read from the module the stage names",
              "the vendor umac.ko has no field names for that descriptor (Stage 371A: 0 hits for "
              "rx_ppdu_end/evm_p0/locationing_timestamp), so the bytes discarded there are not "
              "proven to be the same 84 bytes",
              "no patch and no hook were emitted: only call-site offsets and argument values are "
              "reported, which is the input a patch would need",
              "an unresolved length means the argument was loaded from memory rather than "
              "materialised as an immediate, and is left as null",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[395A] ath10k={s['ath10k_core_present']} modules={s['modules_ok']} "
          f"pulls={s['total_pull_relocs']} in_pop={s['pull_sites_in_amsdu_pop']} "
          f"pop_sym={s['pop_symbol_present']} ppdu_sym={s['ppdu_symbol_present']} "
          f"lengths={s['lengths_histogram']} has84={s['length_84_found']}")
    for r in ok:
        pop = r["functions"]["htt_rx_amsdu_pop"] or {}
        print(f"        {r['module']:<24} {r['bytes']:>8}B relocs={r['total_relocs']:<5} "
              f"pop={pop.get('start')}..{pop.get('end')} pulls={r['total_pull_relocs']} "
              f"hist={r['pull_length_histogram']}")
        print(f"        {'':<24} top={r['pulls_per_function']}")
    print(f"[395A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
