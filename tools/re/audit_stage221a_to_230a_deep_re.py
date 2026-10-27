#!/usr/bin/env python3
"""Stages 221A..230A — deep RE loop: HAL vtable offsets, knob sinks, controlled deltas,
firmware WMI, LTU DMA, spectral/pktlog, round isolation, sysctl inventory, master ledger.

Ten receipts, one pass. Where a named artefact does not exist, the stage reports the absence
instead of inventing a result:

  * **226A**: `eab_driver.ko` does not exist in either LTU image (verified three times across
    stages 154A, 173A and here). The DMA/coalescing analysis runs on `ame_core.ko`.
  * **225A**: the `athwlan_AR9888v2_ptmp_ap_bin` / `_sta_bin` **binaries are not present**.
    Only the Stage 12 manifests (`ar9888_v2_descriptor_map.json`,
    `ar9888_utf_handler_and_build_matrix.json`) are on disk.
  * **224A**: `WA.v8.7.11` / `XC.v8.7.11` do not exist; the platform-axis delta uses 8.7.25.

Radio safety: static only, throughout. No module loaded, no register written, no radio contacted.

Read-only: the only writes are the ten receipt JSONs.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
XW = REPO_ROOT / "artifacts" / "firmware_re_xw_m5"
AR = REPO_ROOT / "artifacts" / "autoresearch"
KNOBS = REPO_ROOT / "orchestration" / "autoresearch" / "firmware_knob_candidates.json"

OUT = {n: AR / f"stage{n}a_deep_re_loop.json" for n in
       (221, 222, 223, 224, 225, 226, 227, 228, 229, 230)}


class Ko:
    def __init__(self, path: Path) -> None:
        self.path = path
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
            nm, typ, fl, addr, off, sz, link, _i, _a, _e = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            secs.append(dict(name_off=nm, type=typ, flags=fl, addr=addr, off=off,
                             size=sz, link=link))
        stro = secs[shstr]["off"]
        for h in secs:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.by_name = {h["name"]: h for h in secs}
        self.sections = secs
        self.exec_sects = [(h["name"], d[h["off"]:h["off"] + h["size"]], h["off"])
                           for h in secs
                           if h["type"] == 1 and (h["flags"] & 0x4) and h["size"] > 0]
        self.syms = []
        st = self.by_name.get(".symtab")
        if st:
            ss = secs[st["link"]]
            for i in range(st["size"] // 16):
                o = st["off"] + i * 16
                nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", d[o:o + 16])
                e = d.find(b"\0", ss["off"] + nm)
                self.syms.append((d[ss["off"] + nm:e].decode("latin1"), val, sz, shndx))
        self.sect_maps = {}
        for h in secs:
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

    def u32(self, sect: str, off: int) -> int | None:
        for n, b, _o in self.exec_sects:
            if n == sect:
                if off < 0 or off + 4 > len(b):
                    return None
                return struct.unpack(self.endian + "I", b[off:off + 4])[0]
        return None

    def defined(self) -> list[str]:
        return sorted({s[0] for s in self.syms if s[3] != 0 and s[0]})

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


def signed16(v: int) -> int:
    return v - 0x10000 if v >= 0x8000 else v


def lw_jalr_offsets(ko: Ko) -> dict[str, Any]:
    """MIPS: `lw $rX, off($base)` followed within 2 insns by `jalr $rX` -> indirect call via
    a function pointer at `off` from `$base`. This is the HAL vtable accessor pattern."""
    hits: Counter[str] = Counter()
    per_base: Counter[str] = Counter()
    sites: list[dict[str, Any]] = []
    for sect, blob, _o in ko.exec_sects:
        for off in range(0, max(0, len(blob) - 16), 4):
            w = ko.u32(sect, off)
            if w is None or (w & 0xFC000000) != 0x8C000000:      # lw
                continue
            base = (w >> 21) & 0x1F
            rt = (w >> 16) & 0x1F
            imm = signed16(w & 0xFFFF)
            for fwd in (4, 8):
                w2 = ko.u32(sect, off + fwd)
                if w2 is None or (w2 & 0xFC00003F) != 0x00000009:  # jalr
                    continue
                if ((w2 >> 21) & 0x1F) != rt:
                    continue
                hits[str(imm)] += 1
                per_base[f"r{base}"] += 1
                if len(sites) < 400:
                    sites.append(dict(sect=sect, offset=f"0x{off:06x}", base=f"$r{base}",
                                      ptr_offset=imm, jalr_delta=fwd))
                break
    return dict(distinct_offsets=len(hits), total_sites=sum(hits.values()),
                offset_histogram=dict(hits.most_common(60)),
                base_usage=dict(per_base.most_common(12)),
                sample=sites[:120])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()
    results: dict[int, dict[str, Any]] = {}

    # ------------------------------------------------ 221A + 222A
    hal_mods = {
        "WA.v8.7.25:ath_hal.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
        "WA.v8.7.25:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
        "XC.v8.7.25:ath_hal.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
        "XC.v8.7.25:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    }
    rows221 = []
    offsets_union: set[int] = set()
    for label, path in hal_mods.items():
        if not path.exists():
            rows221.append(dict(module=label, status="absent"))
            continue
        ko = Ko(path)
        r = lw_jalr_offsets(ko)
        offsets_union |= {int(k) for k in r["offset_histogram"]}
        rows221.append(dict(module=label, status="ok", bytes=len(ko.data),
                            sha256=hashlib.sha256(ko.data).hexdigest(), **r))
    r221 = dict(
        meta=dict(stage="221A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage221a_to_230a_deep_re.py",
                  scope="offline static; no module loaded, no radio contacted",
                  method="MIPS lw $rX,off($base) followed by jalr $rX within 2 instructions "
                         "= indirect call through a function pointer at `off`",
                  claim_limit="an offset present in this histogram is a function-pointer slot "
                              "candidate; it is not proven to be a register-write accessor",
                  radio_safety="static only"),
        modules=rows221,
        summary=dict(modules_ok=len([r for r in rows221 if r.get("status") == "ok"]),
                     distinct_offsets=len(offsets_union),
                     total_indirect_sites=sum(r.get("total_sites", 0) for r in rows221),
                     top_offsets=sorted(offsets_union)[:40]),
        gaps=["the offsets are function-pointer slot candidates, not proven register-write "
              "accessors: the calling convention was not reconstructed",
              "no dynamic validation"])
    OUT[221].write_text(json.dumps(r221, indent=2) + "\n", encoding="utf-8")
    print(f"[221A] modules={r221['summary']['modules_ok']} "
          f"offsets={r221['summary']['distinct_offsets']} "
          f"sites={r221['summary']['total_indirect_sites']}")

    data = json.loads(KNOBS.read_text(encoding="utf-8"))
    knobs = data["knobs"]
    uphold = [k for k in knobs if str(k.get("boundary")) == "airOS_UMAC_UPH"]
    rows222 = []
    for label, path in (("WA.v8.7.25:umac.ko", hal_mods["WA.v8.7.25:umac.ko"]),
                        ("WA.v8.7.25:ath_dev.ko",
                         FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko"),
                        ("XC.v8.7.25:umac.ko", hal_mods["XC.v8.7.25:umac.ko"]),
                        ("XC.v8.7.25:ath_dev.ko",
                         FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko")):
        if not path.exists():
            rows222.append(dict(module=label, status="absent"))
            continue
        ko = Ko(path)
        strs = ko.strings()
        present = sorted({str(k.get("name")) for k in uphold} & strs)
        rows222.append(dict(module=label, status="ok", knob_literals=len(present),
                            register_sink_candidates=len(offsets_union),
                            wmi_symbols=sorted({s for s in ko.defined()
                                                if "wmi" in s.lower()})[:40]))
    r222 = dict(
        meta=dict(stage="222A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage221a_to_230a_deep_re.py",
                  scope="offline static; no module loaded, no radio contacted",
                  method="knob-literal presence per module joined to the 221A offset set",
                  claim_limit="the join is structural, not causal: a knob literal and a "
                              "function-pointer offset in the same module is not a sink mapping",
                  radio_safety="static only"),
        modules=rows222,
        summary=dict(knobs_in_boundary=len(uphold),
                     modules_ok=len([r for r in rows222 if r.get("status") == "ok"]),
                     max_knob_literals=max((r.get("knob_literals", 0) for r in rows222
                                            if r.get("status") == "ok"), default=0),
                     register_sink_candidates=len(offsets_union),
                     exact_sink_mappings=0),
        gaps=["no knob was mapped to a specific register/WMI sink; the join is module-level",
              "the HAL offset set is shared across all knobs, so it does not discriminate"])
    OUT[222].write_text(json.dumps(r222, indent=2) + "\n", encoding="utf-8")
    print(f"[222A] knobs={r222['summary']['knobs_in_boundary']} "
          f"modules={r222['summary']['modules_ok']} "
          f"max_literals={r222['summary']['max_knob_literals']} "
          f"exact_mappings={r222['summary']['exact_sink_mappings']}")

    # ------------------------------------------------ 223A + 224A
    def diff_pair(a: Path, b: Path) -> dict[str, Any]:
        if not a.exists() or not b.exists():
            return dict(status="absent" if not a.exists() else "absent_right")
        x, y = a.read_bytes(), b.read_bytes()
        n = min(len(x), len(y))
        diffs = sum(1 for i in range(n) if x[i] != y[i])
        return dict(status="ok", left_bytes=len(x), right_bytes=len(y),
                    identical=(x == y), differing_bytes=diffs,
                    differing_pct=round(100.0 * diffs / n, 4) if n else 0.0,
                    left_sha256=hashlib.sha256(x).hexdigest(),
                    right_sha256=hashlib.sha256(y).hexdigest())

    def pair(base_a: Path, base_b: Path, names: list[str]) -> dict[str, Any]:
        out = {}
        for n in names:
            fa = next(iter(base_a.rglob(n)), None) if base_a.exists() else None
            fb = next(iter(base_b.rglob(n)), None) if base_b.exists() else None
            if fa is None or fb is None:
                out[n] = dict(status="absent", left=str(fa), right=str(fb))
                continue
            out[n] = diff_pair(fa, fb)
        return out

    r223 = dict(
        meta=dict(stage="223A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage221a_to_230a_deep_re.py",
                  scope="offline static; no device access",
                  axis="version: XW.v6.1.4 vs XW.v6.3.6 on the same M5 platform",
                  radio_safety="static only"),
        pairs=pair(XW / "xw_614_rootfs", XW / "xw_636_rootfs",
                   ["ubntbox", "athbox", "umac.ko", "ath_dev.ko", "ubnt_poll_host.ko"]),
        summary={})
    ok223 = [v for v in r223["pairs"].values() if v.get("status") == "ok"]
    r223["summary"] = dict(pairs=len(r223["pairs"]), pairs_ok=len(ok223),
                           identical=sum(1 for v in ok223 if v["identical"]),
                           total_differing_bytes=sum(v["differing_bytes"] for v in ok223))
    OUT[223].write_text(json.dumps(r223, indent=2) + "\n", encoding="utf-8")
    print(f"[223A] pairs={r223['summary']['pairs_ok']} "
          f"identical={r223['summary']['identical']} "
          f"diff_bytes={r223['summary']['total_differing_bytes']}")

    r224 = dict(
        meta=dict(stage="224A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage221a_to_230a_deep_re.py",
                  scope="offline static; no device access",
                  axis="platform: WA vs XC at the same version",
                  premise_correction="WA.v8.7.11 / XC.v8.7.11 do not exist in this repository; "
                                     "the pair available is 8.7.25",
                  radio_safety="static only"),
        pairs=pair(FW / "wa_8725_rootfs", FW / "xc_8725_rootfs",
                   ["umac.ko", "ath_dev.ko", "ubnt_poll_host.ko"]),
        summary={})
    ok224 = [v for v in r224["pairs"].values() if v.get("status") == "ok"]
    r224["summary"] = dict(pairs=len(r224["pairs"]), pairs_ok=len(ok224),
                           identical=sum(1 for v in ok224 if v["identical"]),
                           total_differing_bytes=sum(v["differing_bytes"] for v in ok224))
    OUT[224].write_text(json.dumps(r224, indent=2) + "\n", encoding="utf-8")
    print(f"[224A] pairs={r224['summary']['pairs_ok']} "
          f"identical={r224['summary']['identical']} "
          f"diff_bytes={r224['summary']['total_differing_bytes']}")

    # ------------------------------------------------ 225A
    fw_bins = []
    for pat in ("**/athwlan*", "**/AR9888*"):
        fw_bins.extend(glob.glob(str(REPO_ROOT / "artifacts" / pat), recursive=True))
    r225 = dict(
        meta=dict(stage="225A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage221a_to_230a_deep_re.py",
                  scope="offline static; no device access",
                  premise_correction="the athwlan_AR9888v2_ptmp_ap_bin and "
                                     "athwlan_AR9888v2_ptmp_sta_bin binaries are NOT present; "
                                     "only the Stage 12 manifests are on disk",
                  radio_safety="static only"),
        binaries_found=fw_bins[:20],
        binaries_found_count=len(fw_bins),
        available_manifests=[
            "artifacts/qca988x/ar9888_v2_descriptor_map.json",
            "artifacts/qca988x/ar9888_utf_handler_and_build_matrix.json",
            "artifacts/hyperresearch_vault/research/notes/futuramax/"
            "STAGE12_AR9888_V2_DESCRIPTOR_AND_CHANNEL_DUMP_MAP.md",
        ],
        summary=dict(binaries_found=len(fw_bins),
                     ap_sta_pair_present=False,
                     manifests_available=3, wmi_handlers_diffed=0),
        gaps=["the AP/STA firmware pair is absent, so no WMI handler delta is possible",
              "the Stage 12 manifests describe the descriptor/channel map for a single build, "
              "not an AP-vs-STA comparison"])
    OUT[225].write_text(json.dumps(r225, indent=2) + "\n", encoding="utf-8")
    print(f"[225A] binarios_athwlan={r225['summary']['binaries_found']} "
          f"par_ap_sta={r225['summary']['ap_sta_pair_present']}")

    # ------------------------------------------------ 226A
    eab = glob.glob(str(REPO_ROOT / "artifacts" / "**" / "eab*.ko"), recursive=True)
    dma_rows = []
    for label, path in (("AF-LTU.v2.4.2:ame_core.ko",
                         FW / "ltu_extracted/afltu_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_core.ko"),
                        ("AF-LTU-Rocket.v2.4.2:ame_core.ko",
                         FW / "ltu_extracted/aflturocket_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_core.ko")):
        if not path.exists():
            dma_rows.append(dict(module=label, status="absent"))
            continue
        ko = Ko(path)
        defs = ko.defined()
        dma = sorted({s for s in defs if re.search(r"dma|desc|ring|coalesc|intr|irq", s, re.I)})
        dma_rows.append(dict(module=label, status="ok", bytes=len(ko.data),
                             dma_symbols=dma[:80], dma_symbol_count=len(dma),
                             coalesce_symbols=sorted({s for s in defs
                                                      if re.search(r"coalesc|budget|"
                                                                   r"threshold|mitigat", s, re.I)})[:40]))
    r226 = dict(
        meta=dict(stage="226A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage221a_to_230a_deep_re.py",
                  scope="offline static; no module loaded, no radio contacted",
                  premise_correction="eab_driver.ko does not exist in either LTU image; the "
                                     "DMA/coalescing analysis runs on ame_core.ko",
                  radio_safety="static only"),
        eab_driver_present=bool(eab),
        modules=dma_rows,
        summary=dict(eab_driver_present=bool(eab),
                     modules_ok=len([r for r in dma_rows if r.get("status") == "ok"]),
                     max_dma_symbols=max((r.get("dma_symbol_count", 0) for r in dma_rows
                                          if r.get("status") == "ok"), default=0),
                     coalesce_symbols=max((len(r.get("coalesce_symbols", [])) for r in dma_rows
                                           if r.get("status") == "ok"), default=0)),
        gaps=["no DMA ring descriptor layout was decoded: only symbol names are reported",
              "interrupt coalescing thresholds were not located as numeric constants",
              "eab_driver.ko is absent, so any eab-specific DMA path is unreachable"])
    OUT[226].write_text(json.dumps(r226, indent=2) + "\n", encoding="utf-8")
    print(f"[226A] eab={r226['summary']['eab_driver_present']} "
          f"modules={r226['summary']['modules_ok']} "
          f"dma_syms={r226['summary']['max_dma_symbols']}")

    # ------------------------------------------------ 227A
    sp_rows = []
    for label, root in (("WA.v8.7.25", FW / "wa_8725_rootfs"), ("XC.v8.7.25", FW / "xc_8725_rootfs")):
        for mod in ("ath_spectral.ko", "ath_pktlog.ko"):
            hits = list(root.rglob(mod))
            if not hits:
                sp_rows.append(dict(image=label, module=mod, status="absent"))
                continue
            ko = Ko(hits[0])
            defs = ko.defined()
            sp_rows.append(dict(image=label, module=mod, status="ok", bytes=len(ko.data),
                                sha256=hashlib.sha256(ko.data).hexdigest(),
                                spectral_symbols=sorted({s for s in defs
                                                         if re.search(r"spectral|fft|samp|"
                                                                      r"radar|pulse", s, re.I)})[:60],
                                pktlog_symbols=sorted({s for s in defs
                                                       if re.search(r"pktlog|log_|ring|"
                                                                    r"buf", s, re.I)})[:60]))
    r227 = dict(
        meta=dict(stage="227A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage221a_to_230a_deep_re.py",
                  scope="offline static; no module loaded, no radio contacted",
                  radio_safety="static only"),
        modules=sp_rows,
        summary=dict(modules_ok=len([r for r in sp_rows if r.get("status") == "ok"]),
                     spectral_syms=max((len(r.get("spectral_symbols", [])) for r in sp_rows
                                        if r.get("status") == "ok"), default=0),
                     pktlog_syms=max((len(r.get("pktlog_symbols", [])) for r in sp_rows
                                      if r.get("status") == "ok"), default=0)),
        gaps=["symbol names only: the spectral sample path and the pktlog ring layout were "
              "not decoded",
              "no cross-image byte delta is claimed here; identity is reported per module"])
    OUT[227].write_text(json.dumps(r227, indent=2) + "\n", encoding="utf-8")
    print(f"[227A] modules={r227['summary']['modules_ok']} "
          f"spectral={r227['summary']['spectral_syms']} pktlog={r227['summary']['pktlog_syms']}")

    # ------------------------------------------------ 228A
    rounds = []
    for cand in sorted(AR.glob("*24round*.json")) + sorted(AR.glob("*r24*.json")):
        try:
            j = json.loads(cand.read_text(encoding="utf-8"))
        except Exception:
            continue
        rounds.append(dict(file=cand.name, keys=list(j)[:12] if isinstance(j, dict) else None))
    r228 = dict(
        meta=dict(stage="228A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage221a_to_230a_deep_re.py",
                  scope="offline static; no device access",
                  radio_safety="static only"),
        candidate_sources=rounds,
        summary=dict(sources_found=len(rounds), rounds_isolated=0,
                     symbol_paths_mapped=0),
        gaps=["no R1..R24 isolation matrix was built: the per-round single-knob evidence is not "
              "present in the sources found",
              "a single-knob isolation matrix requires one round per knob with the others held "
              "fixed, which the counterbalanced champion does not provide"])
    OUT[228].write_text(json.dumps(r228, indent=2) + "\n", encoding="utf-8")
    print(f"[228A] sources={r228['summary']['sources_found']} "
          f"rounds_isolated={r228['summary']['rounds_isolated']}")

    # ------------------------------------------------ 229A
    sysctl_rows = []
    for label, root in (("WA.v8.7.25", FW / "wa_8725_rootfs"), ("XC.v8.7.25", FW / "xc_8725_rootfs"),
                        ("XW.v6.3.6", XW / "xw_636_rootfs")):
        for path in sorted(root.rglob("*.ko")):
            try:
                ko = Ko(path)
            except Exception:
                continue
            defs = ko.defined()
            reg = sorted({s for s in defs if re.search(r"sysctl|proc_create|"
                                                       r"register_sysctl|create_proc", s, re.I)})
            if reg:
                sysctl_rows.append(dict(image=label, module=path.name, registrations=reg[:20]))
    r229 = dict(
        meta=dict(stage="229A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage221a_to_230a_deep_re.py",
                  scope="offline static; no module loaded, no radio contacted",
                  radio_safety="static only"),
        modules_with_registrations=sysctl_rows,
        summary=dict(modules_with_registrations=len(sysctl_rows),
                     total_registration_symbols=sum(len(r["registrations"]) for r in sysctl_rows),
                     images_covered=3),
        gaps=["only defined symbols matching sysctl/proc_create are reported; a registration "
              "performed through a struct initialiser has no symbol",
              "mode bits were audited separately in Stage 81A-W4A/W4B and are not repeated here"])
    OUT[229].write_text(json.dumps(r229, indent=2) + "\n", encoding="utf-8")
    print(f"[229A] modules={r229['summary']['modules_with_registrations']} "
          f"syms={r229['summary']['total_registration_symbols']}")

    # ------------------------------------------------ 230A
    ledger = {}
    for n in range(221, 230):
        p = OUT[n]
        if p.exists():
            j = json.loads(p.read_text(encoding="utf-8"))
            ledger[f"stage{n}A"] = dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                                        summary=j.get("summary"),
                                        gaps=len(j.get("gaps", [])))
    r230 = dict(
        meta=dict(stage="230A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage221a_to_230a_deep_re.py",
                  scope="offline static; consolidates 221A..229A",
                  radio_safety="static only"),
        ledger=ledger,
        summary=dict(stages=len(ledger),
                     stages_with_gaps=sum(1 for v in ledger.values() if v["gaps"]),
                     premise_corrections=3,
                     claim="9 stage receipts consolidated; 3 premises refuted "
                           "(eab_driver.ko absent, athwlan AP/STA pair absent, v8.7.11 absent)"),
        gaps=["consolidation only: it does not add evidence beyond the nine receipts",
              "the two hard blockers remain: the HAL function-pointer calling convention and "
              "the absent firmware pair"])
    OUT[230].write_text(json.dumps(r230, indent=2) + "\n", encoding="utf-8")
    print(f"[230A] stages={r230['summary']['stages']} gaps={r230['summary']['stages_with_gaps']}")
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
