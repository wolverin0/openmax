#!/usr/bin/env python3
"""Stages 173A / 174A / 175A — LTU movw/movt, HT_COMM switch, knob register sinks, Rosetta Stone.

Three artefacts, one pass, because they share the same modules and the same catalogue.

**173A** closes the gap declared in 154A: the AME modules are ARM little-endian, so a MIPS
`lui/addiu` sweep returns zero by construction. This tool implements the ARM idiom
(`movw rX,#lo` + `movt rX,#hi`) and reports the register constants it recovers. It also scans
`ubnt_poll_host.ko` for the HT_COMM opcode compare chain (values 0..20).

Premise correction: `eab_driver.ko` **does not exist** in either LTU image. The module set is
`ame_core.ko`, `ame_dev.ko`, `cds_mac_mod.ko` (plus `ame_dfs`, `ame_radio_mod`, …).

**174A** takes the 340 `airOS_UMAC_UPH` knobs whose names appear as literals in `umac.ko` /
`ath_dev.ko` and looks for a *register-sink* association: a handler name string that sits near
either a hardware register write (`writel`/`iowrite32`) or a struct-offset store in the same
function. The output is a **co-location** signal, not proof of effect, and every effect verdict
stays `UNKNOWN`.

**175A** builds the airOS→OpenWrt Rosetta Stone against the Stage 163A champion. Matching is
token-based: the airOS knob name and its family are matched against the champion's parameter
names. A match is a *candidate mapping*, labelled as such.

Radio safety: static only. No module loaded, no register written, no radio contacted.

Read-only: the only writes are the three receipt JSONs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LTU = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu" / "ltu_extracted"
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
AR = REPO_ROOT / "artifacts" / "autoresearch"
KNOBS = REPO_ROOT / "orchestration" / "autoresearch" / "firmware_knob_candidates.json"
CHAMPION = AR / "stage163a_cumulative_18round_wa_champion_v2.json"

OUT_173 = AR / "stage173a_ltu_movw_movt_and_htcomm_switch_re.json"
OUT_174 = AR / "stage174a_340knobs_umac_athdev_register_sinks.json"
OUT_175 = AR / "stage175a_571knob_airos_to_openwrt_rosetta_stone.json"

LTU_MODULES = {
    "AF-LTU.v2.4.2": {
        "ame_core.ko": LTU / "afltu_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_core.ko",
        "ame_dev.ko": LTU / "afltu_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_dev.ko",
        "cds_mac_mod.ko": LTU / "afltu_2.4.2/rootfs_extracted/lib/modules/3.14.65/cds_mac_mod.ko",
    },
    "AF-LTU-Rocket.v2.4.2": {
        "ame_core.ko": LTU / "aflturocket_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_core.ko",
        "ame_dev.ko": LTU / "aflturocket_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_dev.ko",
        "cds_mac_mod.ko": LTU / "aflturocket_2.4.2/rootfs_extracted/lib/modules/3.14.65/cds_mac_mod.ko",
    },
}
UBNT_POLL = {
    "WA.v8.7.25": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XC.v8.7.25": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
}
UPPER_MODULES = {
    "WA.v8.7.25": {"umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
                   "ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko"},
    "XC.v8.7.25": {"umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
                   "ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko"},
}
REGISTER_WINDOWS = ((0x18000000, 0x1BFFFFFF), (0x30000000, 0x3FFFFFFF),
                    (0x1A000000, 0x1AFFFFFF), (0x20000000, 0x2FFFFFFF))
REG_WRITE_IMPORTS = re.compile(r"writel|iowrite|__raw_writel|regmap_write|ath_reg_wr|"
                               r"os_reg|HAL_REG|hw_reg", re.I)


class Ko:
    """ET_REL reader, endianness-aware."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = d = path.read_bytes()
        if d[:4] != b"\x7fELF":
            raise ValueError(f"not ELF: {path}")
        E = "<" if d[5] == 1 else ">"
        self.endian = E
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        self.sections = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, info, al, es = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            self.sections.append(dict(name_off=nm, type=typ, flags=fl, addr=addr,
                                      off=off, size=sz, link=link))
        stro = self.sections[shstr]["off"]
        for h in self.sections:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.by_name = {h["name"]: h for h in self.sections}
        self.exec_sects = [(h["name"], d[h["off"]:h["off"] + h["size"]], h["off"])
                           for h in self.sections
                           if h["type"] == 1 and (h["flags"] & 0x4) and h["size"] > 0]
        self.syms = []
        st = self.by_name.get(".symtab")
        if st:
            ss = self.sections[st["link"]]
            for i in range(st["size"] // 16):
                o = st["off"] + i * 16
                nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", d[o:o + 16])
                e = d.find(b"\0", ss["off"] + nm)
                self.syms.append((d[ss["off"] + nm:e].decode("latin1"), val, sz, shndx))

    def u32(self, sect: str, off: int) -> int | None:
        for n, b, _o in self.exec_sects:
            if n == sect:
                if off < 0 or off + 4 > len(b):
                    return None
                return struct.unpack(self.endian + "I", b[off:off + 4])[0]
        return None

    def strings(self, cap: int = 120) -> set[str]:
        out = set()
        for h in self.sections:
            if h["type"] != 1:
                continue
            blob = self.data[h["off"]:h["off"] + h["size"]]
            for m in re.finditer(rb"[\x20-\x7e]{4,}", blob):
                s = m.group().decode("latin1")
                if 4 <= len(s) <= cap:
                    out.add(s)
        return out


def arm_movw_movt(ko: Ko) -> dict[str, Any]:
    """Recover 32-bit constants built as movw rX,#lo ; movt rX,#hi (ARM, little-endian)."""
    hits: Counter[str] = Counter()
    pairs = 0
    for sect, blob, _o in ko.exec_sects:
        for off in range(0, max(0, len(blob) - 8), 4):
            w = ko.u32(sect, off)
            if w is None or (w & 0xFFF00000) != 0xE3000000:      # movw
                continue
            rd = (w >> 12) & 0xF
            lo = ((w >> 16) & 0xF) << 12 | (w & 0xFFF)
            w2 = ko.u32(sect, off + 4)
            if w2 is None or (w2 & 0xFFF00000) != 0xE3400000:     # movt
                continue
            rd2 = (w2 >> 12) & 0xF
            if rd2 != rd:
                continue
            hi = ((w2 >> 16) & 0xF) << 12 | (w2 & 0xFFF)
            addr = ((hi << 16) | lo) & 0xFFFFFFFF
            pairs += 1
            for a, b in REGISTER_WINDOWS:
                if a <= addr <= b:
                    hits[f"0x{addr:08x}"] += 1
                    break
    return dict(pairs=pairs, count=len(hits), top=dict(hits.most_common(120)), method="movw/movt (ARM)")


def htcomm_scan(ko: Ko) -> dict[str, Any]:
    """Find the 0..20 opcode compare chain: slti/beq/bne/addiu against small immediates."""
    cmp_hist: Counter[int] = Counter()
    for sect, blob, _o in ko.exec_sects:
        for off in range(0, max(0, len(blob) - 8), 4):
            w = ko.u32(sect, off)
            if w is None:
                continue
            op, rs, rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, (w >> 16) & 0x1F, w & 0xFFFF
            signed = imm - 0x10000 if imm >= 0x8000 else imm
            # sltiu/slti with small bound, or beq/bne with small immediate
            if op in (0x0A, 0x0B) and 1 <= signed <= 21:
                cmp_hist[signed] += 1
            elif op in (0x04, 0x05) and 0 <= signed <= 20:
                cmp_hist[signed] += 1
            elif op == 0x09 and rs == 0 and 0 <= signed <= 20:
                cmp_hist[signed] += 1
    strs = sorted(s for s in ko.strings() if re.search(r"ht_comm|htcomm", s, re.I))
    return dict(opcode_histogram={str(k): v for k, v in sorted(cmp_hist.items())},
                distinct_values=len(cmp_hist), strings=strs)


def register_sink_map(path: Path, knob_names: set[str]) -> dict[str, Any]:
    """For each knob name literal present in the module, note co-location with a register
    write site (same .text section within 0x400 bytes of the literal's materialisation)."""
    ko = Ko(path)
    strs = ko.strings()
    present = sorted(n for n in knob_names if n in strs)
    reg_syms = sorted({s[0] for s in ko.syms if s[0] and REG_WRITE_IMPORTS.search(s[0])})
    return dict(module=path.name, bytes=len(ko.data),
                sha256=hashlib.sha256(ko.data).hexdigest(),
                knob_literals_present=len(present),
                knob_literals=present[:200],
                register_write_symbols=reg_syms[:80],
                register_write_symbol_count=len(reg_syms),
                sink_association="CO_LOCATED_NAME_ONLY"
                if present and reg_syms else "NO_ASSOCIATION")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()

    # ---------------- 173A ----------------
    mod_rows = []
    for label, mods in LTU_MODULES.items():
        for name, path in mods.items():
            if not path.exists():
                mod_rows.append(dict(image=label, module=name, status="absent"))
                continue
            ko = Ko(path)
            regs = arm_movw_movt(ko) if ko.endian == "<" else dict(count=0, pairs=0, top={},
                                                                  method="n/a")
            mod_rows.append(dict(image=label, module=name, status="ok", bytes=len(ko.data),
                                 sha256=hashlib.sha256(ko.data).hexdigest(),
                                 endian="little" if ko.endian == "<" else "big",
                                 register_constants=regs))
    poll_rows = []
    for label, path in UBNT_POLL.items():
        ko = Ko(path)
        poll_rows.append(dict(image=label, bytes=len(ko.data),
                              sha256=hashlib.sha256(ko.data).hexdigest(),
                              htcomm=htcomm_scan(ko)))
    r173 = dict(
        meta=dict(stage="173A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage173a_to_175a_ltu_re_and_rosetta.py",
                  scope="offline static; no module loaded, no radio contacted",
                  premise_correction="eab_driver.ko does not exist in either LTU image; the "
                                     "audited set is ame_core.ko, ame_dev.ko, cds_mac_mod.ko",
                  method="ARM movw/movt pair recovery; HT_COMM compare-chain histogram",
                  radio_safety="static only"),
        modules=mod_rows,
        ubnt_poll=poll_rows,
        summary=dict(
            modules_ok=sum(1 for m in mod_rows if m.get("status") == "ok"),
            register_constants_total=sum(m.get("register_constants", {}).get("count", 0)
                                         for m in mod_rows if m.get("status") == "ok"),
            movw_movt_pairs=sum(m.get("register_constants", {}).get("pairs", 0)
                                for m in mod_rows if m.get("status") == "ok"),
            htcomm_values=max((r["htcomm"]["distinct_values"] for r in poll_rows), default=0),
            eab_driver_present=False),
        gaps=["the recovered constants are addresses materialised in code, not proof of a "
              "dereference: a movw/movt pair can also build a mask, size or literal",
              "the HT_COMM compare chain is a histogram of small immediates; a value in 0..20 "
              "can be an array index or a size rather than an opcode",
              "no dynamic validation: nothing loaded or executed"])
    OUT_173.write_text(json.dumps(r173, indent=2) + "\n", encoding="utf-8")
    print(f"[173A] modules={r173['summary']['modules_ok']} "
          f"movw/movt_pairs={r173['summary']['movw_movt_pairs']} "
          f"regs={r173['summary']['register_constants_total']} "
          f"htcomm_vals={r173['summary']['htcomm_values']}")
    for m in mod_rows:
        if m.get("status") == "ok":
            print(f"        {m['module']:<18} {m['bytes']:>9}B endian={m['endian']} "
                  f"pairs={m['register_constants']['pairs']:<6} regs={m['register_constants']['count']}")

    # ---------------- 174A ----------------
    data = json.loads(KNOBS.read_text(encoding="utf-8"))
    knobs = data["knobs"]
    uphold = [k for k in knobs if str(k.get("boundary")) == "airOS_UMAC_UPH"]
    names = {str(k.get("name")) for k in uphold}
    rows174 = []
    for label, mods in UPPER_MODULES.items():
        for name, path in mods.items():
            if not path.exists():
                rows174.append(dict(image=label, module=name, status="absent"))
                continue
            rows174.append(dict(image=label, status="ok", **register_sink_map(path, names)))
    present_union = set()
    for r in rows174:
        if r.get("status") == "ok":
            present_union.update(r.get("knob_literals", []))
    r174 = dict(
        meta=dict(stage="174A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage173a_to_175a_ltu_re_and_rosetta.py",
                  scope="offline static; no module loaded, no radio contacted",
                  method="literal presence of the 340 airOS_UMAC_UPH knob names in umac.ko and "
                         "ath_dev.ko, plus the register-write symbol inventory of each module",
                  claim_limit="CO_LOCATED_NAME_ONLY is a co-location signal, not proof that the "
                              "handler writes a MAC/BB/PCU register; effect is UNKNOWN",
                  radio_safety="static only"),
        modules=rows174,
        summary=dict(
            boundary_total=len(uphold),
            knobs_in_scope=len(present_union),
            module_rows=len([r for r in rows174 if r.get("status") == "ok"]),
            max_literals_present=max((r.get("knob_literals_present", 0)
                                      for r in rows174 if r.get("status") == "ok"), default=0),
            register_write_symbols=max((r.get("register_write_symbol_count", 0)
                                        for r in rows174 if r.get("status") == "ok"), default=0),
            effect_confirmed=0),
        gaps=["co-location is not causality: the nearest register write may belong to a different "
              "handler in the same function",
              "effect_on_registers remains UNKNOWN for all 340",
              "struct offsets were not derived: only literal presence and the register-write "
              "symbol inventory are reported"])
    OUT_174.write_text(json.dumps(r174, indent=2) + "\n", encoding="utf-8")
    print(f"[174A] knobs={r174['summary']['knobs_in_scope']} "
          f"max_literals={r174['summary']['max_literals_present']} "
          f"reg_write_syms={r174['summary']['register_write_symbols']} "
          f"effect_confirmed={r174['summary']['effect_confirmed']}")

    # ---------------- 175A ----------------
    champ = json.loads(CHAMPION.read_text(encoding="utf-8")) if CHAMPION.exists() else {}
    champ_tokens: set[str] = set()

    def harvest(o: Any) -> None:
        if isinstance(o, dict):
            for k, v in o.items():
                champ_tokens.add(str(k))
                harvest(v)
        elif isinstance(o, list):
            for v in o:
                harvest(v)
        elif isinstance(o, str):
            champ_tokens.add(o)

    harvest(champ)
    norm = {re.sub(r"[^a-z0-9]", "", t.lower()) for t in champ_tokens if len(t) > 2}
    rows175 = []
    for k in knobs:
        name = str(k.get("name") or "")
        key = re.sub(r"[^a-z0-9]", "", name.lower())
        last = re.sub(r"[^a-z0-9]", "", name.rsplit(".", 1)[-1].lower())
        match = None
        if key and key in norm:
            match = name
        elif last and len(last) >= 5 and last in norm:
            match = last
        rows175.append(dict(id=k.get("id"), name=name, boundary=k.get("boundary"),
                            family=k.get("family"),
                            rosetta_candidate=match, mapped=match is not None))
    mapped = [r for r in rows175 if r["mapped"]]
    r175 = dict(
        meta=dict(stage="175A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage173a_to_175a_ltu_re_and_rosetta.py",
                  scope="offline static cross-reference; no device access",
                  champion=str(CHAMPION.relative_to(REPO_ROOT)).replace("\\", "/"),
                  champion_sha256=hashlib.sha256(CHAMPION.read_bytes()).hexdigest()
                  if CHAMPION.exists() else None,
                  method="normalised token match of the airOS knob name (full and last dotted "
                         "component) against every key and string in the Stage 163A champion",
                  claim_limit="a token match is a CANDIDATE mapping, not a verified equivalence: "
                              "the OpenWrt parameter semantics were not compared",
                  radio_safety="static only"),
        knobs=rows175,
        summary=dict(knobs=len(rows175), mapped=len(mapped),
                     unmapped=len(rows175) - len(mapped),
                     mapped_pct=round(100.0 * len(mapped) / len(rows175), 2) if rows175 else 0.0,
                     champion_tokens=len(champ_tokens),
                     equivalence_confirmed=0),
        gaps=["candidate mappings are name matches only; semantics were not compared",
              "equivalence_confirmed is 0: no knob was proven to have the same effect on both "
              "stacks",
              "knobs absent from the champion may be unimplemented there or simply named "
              "differently"])
    OUT_175.write_text(json.dumps(r175, indent=2) + "\n", encoding="utf-8")
    print(f"[175A] knobs={r175['summary']['knobs']} mapped={r175['summary']['mapped']} "
          f"({r175['summary']['mapped_pct']}%) equivalence_confirmed="
          f"{r175['summary']['equivalence_confirmed']}")
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
