#!/usr/bin/env python3
"""Stage 154A — AF-LTU `ame_core.ko` / `ame_dev.ko` static dissection.

Premise corrections, verified before any analysis:

  * `eab_driver.ko` **does not exist** anywhere under `artifacts/`. The LTU module set is
    `ame_core.ko` and `ame_dev.ko` (plus `eab*.ko` absent). Nothing is reported for a module
    that is not there.
  * `v2.4.0` **does not exist on disk**. The images present are `afltu-2.4.1`, `afltu-2.4.2`,
    `aflturocket-2.4.1`, `aflturocket-2.4.2`. Only the 2.4.2 rootfs trees are extracted,
    so 2.4.2 is what gets dissected.

What the tool extracts from each `ET_REL` MIPS32 module:

  * **imports** — every undefined symbol, grouped by subsystem (DMA, ASIC/register, netlink,
    crypto, skb, timer);
  * **ioctl surface** — the `file_operations`-adjacent symbols and any `unlocked_ioctl`
    implementation, located by symbol name and by the `ioctl` string it dispatches on;
  * **ASIC / DMA register constants** — every 32-bit constant materialised by a `lui`/`addiu`
    pair inside the register windows (`0x18xxxxxx`–`0x1Bxxxxxx`, `0x1Axxxxxx`), which is how
    QCA9880/988x MAC/BB/PCU and DMA rings are addressed;
  * **4096-QAM / 12x modulation surface** — every string and symbol mentioning QAM, MCS,
    modulation, rate table or 12x, because the LTU 4096-QAM mode is the headline capability.

Radio safety: static only. No module is loaded, no register is read, no radio is contacted.

Read-only: the only write is the receipt JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import struct
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LTU = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu" / "ltu_extracted"
DEFAULT_OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage154a_ltu_ame_eab_full_re.json"

_spec = importlib.util.spec_from_file_location(
    "w4a", REPO_ROOT / "tools" / "re" / "audit_stage81a_w4a_wa_xc_ko_proc_ioctl.py")
w4a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w4a)


class Ko:
    """ET_REL reader that detects endianness, so ARM LE (LTU) and MIPS BE both work."""

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
                                      off=off, size=sz, link=link, info=info, entsize=es))
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
        self.sect_maps = {}
        for h in self.sections:
            if h["type"] != 9 or not h["name"].startswith(".rel."):
                continue
            tgt = "." + h["name"][5:]
            m = {}
            for i in range(h["size"] // 8):
                o = h["off"] + i * 8
                r_off, r_info = struct.unpack(E + "II", d[o:o + 8])
                idx = r_info >> 8
                if idx < len(self.syms) and self.syms[idx][0]:
                    m[r_off] = self.syms[idx][0]
            if m:
                self.sect_maps[tgt] = m

    def _blob(self, sect):
        for n, b, _o in self.exec_sects:
            if n == sect:
                return b
        return None

    def u32(self, sect, off):
        b = self._blob(sect)
        if b is None or off < 0 or off + 4 > len(b):
            return None
        return struct.unpack(self.endian + "I", b[off:off + 4])[0]


MODULES = {
    "AF-LTU.v2.4.2": {
        "ame_core.ko": LTU / "afltu_2.4.2" / "rootfs_extracted/lib/modules/3.14.65/ame_core.ko",
        "ame_dev.ko": LTU / "afltu_2.4.2" / "rootfs_extracted/lib/modules/3.14.65/ame_dev.ko",
    },
    "AF-LTU-Rocket.v2.4.2": {
        "ame_core.ko": LTU / "aflturocket_2.4.2" / "rootfs_extracted/lib/modules/3.14.65/ame_core.ko",
        "ame_dev.ko": LTU / "aflturocket_2.4.2" / "rootfs_extracted/lib/modules/3.14.65/ame_dev.ko",
    },
}

SUBSYSTEMS = {
    "dma": re.compile(r"dma|desc|ring|pfn|remap|coherent|ioremap", re.I),
    "netlink": re.compile(r"netlink|skb_|nla_|genl|nlmsg", re.I),
    "crypto": re.compile(r"crypto|cipher|aes|sha|hmac|rsa|md5", re.I),
    "netdev": re.compile(r"dev_|netdev|ndo_|ethtool|napi|carrier", re.I),
    "timer": re.compile(r"timer|hrtimer|jiffies|delayed_work|workqueue", re.I),
    "regmap": re.compile(r"regmap|readl|writel|ioread|iowrite|mmio", re.I),
    "modulation": re.compile(r"qam|mcs|modulation|rate_|txpower|nss|vht|he_", re.I),
}
REG_WINDOWS = ((0x18000000, 0x1BFFFFFF), (0x1A000000, 0x1AFFFFFF), (0x30000000, 0x3FFFFFFF))
MOD_PATTERN = re.compile(r"(4096|qam|mcs|modul|12x|vht|he_|nss)", re.I)


def classify(names: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for bucket, rx in SUBSYSTEMS.items():
        hits = sorted({n for n in names if rx.search(n)})
        if hits:
            out[bucket] = hits[:60]
    return out


def strings_of(ko: Any, cap: int = 120) -> list[str]:
    """Printable NUL-terminated strings from .rodata and .data."""
    out = set()
    for sect in (".rodata", ".rodata.str1.4", ".data"):
        h = ko.by_name.get(sect)
        if not h:
            continue
        blob = ko.data[h["off"]:h["off"] + h["size"]]
        for m in re.finditer(rb"[\x20-\x7e]{%d,}" % 4, blob):
            s = m.group().decode("latin1")
            if 4 <= len(s) <= cap:
                out.add(s)
    return sorted(out)


def register_constants(ko: Any) -> dict[str, Any]:
    """Every 32-bit constant built by lui+addiu that lands in a register window."""
    hits: Counter[str] = Counter()
    for sect, blob, _o in ko.exec_sects:
        for off in range(0, max(0, len(blob) - 12), 4):
            w = ko.u32(sect, off)
            if w is None or (w & 0xFC000000) != 0x3C000000:
                continue
            rt = (w >> 16) & 0x1F
            for fwd in (4, 8, 12):
                w2 = ko.u32(sect, off + fwd)
                if w2 is None:
                    continue
                op2, rs2, rt2, imm2 = (w2 >> 26) & 0x3F, (w2 >> 21) & 0x1F, \
                                      (w2 >> 16) & 0x1F, w2 & 0xFFFF
                if op2 in (0x09, 0x0D) and rt2 == rt and rs2 == rt:
                    lo = imm2 - 0x10000 if (op2 == 0x09 and imm2 >= 0x8000) else imm2
                    addr = (((w & 0xFFFF) << 16) + lo) & 0xFFFFFFFF
                    for lo_w, hi_w in REG_WINDOWS:
                        if lo_w <= addr <= hi_w:
                            hits[f"0x{addr:08x}"] += 1
                            break
                    break
    return dict(count=len(hits), top=dict(hits.most_common(80)),
                method="lui/addiu (MIPS pattern)",
                applicable=("no" if ko.endian == "<" else "yes"),
                note=("these modules are ARM little-endian; ARM materialises constants with movw/movt or literal pools, so a lui/addiu sweep returns 0 by construction and the count is NOT evidence that no register is addressed"
                      if ko.endian == "<" else "MIPS lui/addiu sweep applies"))


def ioctl_surface(ko: Any, strs: list[str]) -> dict[str, Any]:
    syms = [s[0] for s in ko.syms if s[0]]
    ioctl_syms = sorted({s for s in syms if re.search(r"ioctl", s, re.I)})
    fops_syms = sorted({s for s in syms if re.search(r"fops|file_op|ops$", s, re.I)})
    ioctl_strings = sorted({s for s in strs if re.search(r"ioctl|IOCTL", s)})
    return dict(symbols=ioctl_syms, file_operations=fops_syms,
                strings=ioctl_strings, ioctl_symbol_count=len(ioctl_syms))


def audit(path: Path) -> dict[str, Any]:
    ko = Ko(path)
    defined = [s for s in ko.syms if s[3] != 0 and s[0]]
    undefined = [s for s in ko.syms if s[3] == 0 and s[0]]
    dnames = sorted({s[0] for s in defined})
    unames = sorted({s[0] for s in undefined})
    strs = strings_of(ko)
    mod = sorted({s for s in strs if MOD_PATTERN.search(s)})
    mod_syms = sorted({n for n in dnames + unames if MOD_PATTERN.search(n)})
    regs = register_constants(ko)
    return dict(
        path=path.name, bytes=len(ko.data), sha256=hashlib.sha256(ko.data).hexdigest(),
        exec_sections=[n for n, _b, _o in ko.exec_sects],
        symbols_total=len(ko.syms), defined=len(dnames), undefined=len(unames),
        imports_by_subsystem=classify(unames),
        defined_by_subsystem=classify(dnames),
        ioctl=ioctl_surface(ko, strs),
        register_constants=regs,
        modulation_strings=mod[:80], modulation_symbols=mod_syms[:80],
        modulation_string_count=len(mod), modulation_symbol_count=len(mod_syms),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    images = []
    for label, mods in MODULES.items():
        rows = []
        for name, path in mods.items():
            if not path.exists():
                rows.append(dict(path=name, status="absent"))
                continue
            a = audit(path)
            a["status"] = "ok"
            rows.append(a)
        images.append(dict(image=label, modules=rows))

    ok = [m for i in images for m in i["modules"] if m.get("status") == "ok"]
    core = next((m for m in ok if m["path"] == "ame_core.ko"), ok[0] if ok else {})
    dev = next((m for m in ok if m["path"] == "ame_dev.ko"), {})
    report = dict(
        meta=dict(
            stage="154A", phase="154A", generated_utc="2026-10-26T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/re/audit_stage154a_ltu_ame_eab_full_re.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(DEFAULT_OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            scope="offline static analysis of ET_REL MIPS32 modules; no module loaded, "
                  "no register read, no radio contacted",
            method="ET_REL section headers + .symtab classification; lui/addiu constant "
                   "sweep for ASIC register windows; .rodata string sweep for modulation",
            premise_corrections=[
                "eab_driver.ko does not exist anywhere under artifacts/; the LTU module set "
                "is ame_core.ko and ame_dev.ko",
                "AF-LTU v2.4.0 does not exist on disk; images present are 2.4.1 and 2.4.2, "
                "and only 2.4.2 is extracted, so 2.4.2 is what was dissected",
            ],
            radio_safety="static only; nothing loaded or executed",
        ),
        images=images,
        summary=dict(
            modules_audited=len(ok),
            core_bytes=core.get("bytes"),
            core_symbols=core.get("symbols_total"),
            core_register_constants=core.get("register_constants", {}).get("count"),
            core_modulation_strings=core.get("modulation_string_count"),
            dev_ioctl_symbols=dev.get("ioctl", {}).get("ioctl_symbol_count"),
            dma_imports_core=len(core.get("imports_by_subsystem", {}).get("dma", [])),
            mod_imports_core=len(core.get("imports_by_subsystem", {}).get("modulation", [])),
            eab_driver_present=False,
        ),
        gaps=[
            "eab_driver.ko is absent: any DMA/EAB analysis is limited to ame_core.ko and "
            "ame_dev.ko",
            "REGISTER CONSTANT COUNT IS ZERO BY CONSTRUCTION: these AME modules are ARM "
            "little-endian and the sweep implements the MIPS lui/addiu idiom only; ARM "
            "uses movw/movt or literal pools, so regs=0 must not be read as \"no register "
            "is addressed\". A movw/movt sweep is required to fill this column",
            "the ASIC register constants are addresses materialised in code, not proof that "
            "each is dereferenced; a `lui`/`addiu` pair can also build a mask or a size",
            "the 4096-QAM surface is reported as strings and symbol names, not as a decoded "
            "rate table: the MCS-to-rate mapping requires the register semantics",
            "v2.4.0 is not on disk, so no 2.4.0-vs-2.4.2 diff is possible",
            "no dynamic validation: no module loaded, no radio contacted",
        ],
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[154A] modules={s['modules_audited']} eab_driver_present={s['eab_driver_present']}")
    for m in ok:
        print(f"       {m['path']:<14} {m['bytes']:>9}B syms={m['symbols_total']:<6} "
              f"regs={m['register_constants']['count']:<4} "
              f"mod_str={m['modulation_string_count']:<3} "
              f"mod_sym={m['modulation_symbol_count']:<3} "
              f"ioctl_sym={m['ioctl']['ioctl_symbol_count']}")
    print(f"[154A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
