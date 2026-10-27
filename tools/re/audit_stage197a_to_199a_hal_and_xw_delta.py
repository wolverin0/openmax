#!/usr/bin/env python3
"""Stages 197A / 198A / 199A — HAL accessor reality, 18-effect Rosetta, XW-vs-WA applet delta.

**197A** was scoped as "resolve the indirect HAL vtable (`ah_reg_write`, `OS_REG_WRITE`,
`wmi_unified_cmd_send`)". Verified before analysis:

  * `ah_reg_write` and `OS_REG_WRITE` **do not exist as symbols** in `ath_hal.ko` (0 raw hits
    each). The premise is refuted for those two names.
  * `wmi_unified_cmd_send` **does exist** in `umac.ko` (3 raw hits, 110 `wmi_unified` strings).

So the stage reports which accessors are real, which are absent, and what the register-write
indirection actually looks like in symbol terms.

**198A** builds the effect-driven Rosetta Stone: each of the 18 champion rounds is parsed for
the parameters it tuned, and each parameter is matched to catalogue knobs. Match is by
parameter token, and every mapping stays a candidate.

**199A** compares the `ubntbox` / `athbox` applet tables of `XW.v6.3.6` (airOS 6 M5) against
`WA.v8.7.25`. Premise correction: `WA.v8.7.11` does not exist in this repository.

Radio safety: static only. No module loaded, no register written, no radio contacted.

Read-only: the only writes are the three receipt JSONs.
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
AR = REPO_ROOT / "artifacts" / "autoresearch"
KNOBS = REPO_ROOT / "orchestration" / "autoresearch" / "firmware_knob_candidates.json"
CHAMPION = AR / "stage163a_cumulative_18round_wa_champion_v2.json"

OUT_197 = AR / "stage197a_ath_hal_vtable_and_wmi_accessor_re.json"
OUT_198 = AR / "stage198a_18effect_empirical_rosetta_stone.json"
OUT_199 = AR / "stage199a_xw_vs_wa_ubntbox_athbox_delta_re.json"

HAL_MODULES = {
    "WA.v8.7.25:ath_hal.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "WA.v8.7.25:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC.v8.7.25:ath_hal.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "XC.v8.7.25:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
}
ACCESSORS = ["ah_reg_write", "OS_REG_WRITE", "os_reg_write", "ah_write",
             "wmi_unified_cmd_send", "wmi_unified", "ath_hal_write", "reg_write"]

BINARIES = {
    "WA.v8.7.25": {"ubntbox": FW / "wa_8725_rootfs/bin/ubntbox",
                   "athbox": FW / "wa_8725_rootfs/bin/athbox"},
    "XW.v6.3.6": {"ubntbox": XW / "xw_636_rootfs/bin/ubntbox",
                  "athbox": XW / "xw_636_rootfs/bin/athbox"},
}


class Ko:
    def __init__(self, path: Path) -> None:
        self.data = d = path.read_bytes()
        E = "<" if d[5] == 1 else ">"
        self.endian = E
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        secs = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, _i, _a, _e = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            secs.append(dict(name_off=nm, type=typ, flags=fl, off=off, size=sz, link=link))
        stro = secs[shstr]["off"]
        for h in secs:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.by_name = {h["name"]: h for h in secs}
        self.sections = secs
        self.syms = []
        st = self.by_name.get(".symtab")
        if st:
            ss = secs[st["link"]]
            for i in range(st["size"] // 16):
                o = st["off"] + i * 16
                nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", d[o:o + 16])
                e = d.find(b"\0", ss["off"] + nm)
                self.syms.append((d[ss["off"] + nm:e].decode("latin1"), val, sz, shndx))

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


def elf_imports(blob: bytes) -> tuple[list[str], int]:
    d = blob
    E = ">" if d[5] == 2 else "<"
    phoff = struct.unpack(E + "I", d[28:32])[0]
    phent, phnum = struct.unpack(E + "HH", d[42:46])
    dyn = None
    for i in range(phnum):
        o = phoff + i * phent
        typ, off = struct.unpack(E + "II", d[o:o + 8])
        if typ == 2:
            dyn = off
    tags: dict[int, list[int]] = {}
    if dyn is not None:
        j = 0
        while True:
            tg, val = struct.unpack(E + "II", d[dyn + j * 8:dyn + j * 8 + 8])
            if tg == 0:
                break
            tags.setdefault(tg, []).append(val)
            j += 1
    if not all(k in tags for k in (5, 6, 11)):
        return [], 0
    strtab, symtab, syment = tags[5][0], tags[6][0], tags[11][0]

    def off_of(va: int) -> int | None:
        for i in range(phnum):
            o = phoff + i * phent
            typ, off, vaddr, _pa, fsz, _msz, _fl, _al = struct.unpack(E + "IIIIIIII", d[o:o + 32])
            if typ == 1 and vaddr <= va < vaddr + fsz:
                return off + (va - vaddr)
        return None

    def cstr(va: int) -> str | None:
        o = off_of(va)
        if o is None:
            return None
        e = d.find(b"\0", o, o + 200)
        return d[o:e].decode("latin1") if e > o else None

    names = set()
    for base, size in ([(tags[23][0], tags.get(2, [0])[0])] +
                       ([(tags[17][0], tags.get(18, [0])[0])] if 17 in tags else [])):
        for i in range(size // 8):
            o = off_of(base + i * 8)
            if o is None:
                break
            _r, info = struct.unpack(E + "II", d[o:o + 8])
            so = off_of(symtab + (info >> 8) * syment)
            if so is None:
                continue
            nm = struct.unpack(E + "I", d[so:so + 4])[0]
            s = cstr(strtab + nm) if nm else None
            if s:
                names.add(s)
    return sorted(names), len(names)


def applets_of(blob: bytes) -> dict[str, Any]:
    """{name, fn} runs referenced by code, same rule as the 81A/113A/118A tools."""
    e = w4d_Elf(blob)
    groups = e.applets()
    names = [a["name"] for g in groups for a in g["applets"]]
    return dict(count=len(names), names=sorted(names),
                plt=len(e.plt), jal=len(e.calls),
                jal_resolved=sum(1 for c in e.calls if c[2]))


# reuse the W4D ELF reader for ET_EXEC binaries
_spec = __import__("importlib").util.spec_from_file_location(
    "w4d", REPO_ROOT / "tools" / "re" / "audit_stage81a_w4d_wa_xc_standalone_elfs.py")
_w4d = __import__("importlib").util.module_from_spec(_spec)
_spec.loader.exec_module(_w4d)
w4d_Elf = _w4d.Elf


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()

    # ------------------------------- 197A
    acc_rows = []
    for label, path in HAL_MODULES.items():
        if not path.exists():
            acc_rows.append(dict(module=label, status="absent"))
            continue
        raw = path.read_bytes()
        ko = Ko(path)
        defined = sorted({s[0] for s in ko.syms if s[3] != 0 and s[0]})
        counts = {a: raw.count(a.encode()) for a in ACCESSORS}
        hits = {a: [s for s in defined if a.lower() in s.lower()] for a in ACCESSORS}
        acc_rows.append(dict(
            module=label, status="ok", bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
            raw_string_counts=counts,
            symbol_hits={k: v[:20] for k, v in hits.items() if v},
            symbol_hit_counts={k: len(v) for k, v in hits.items() if v},
            present_accessors=[a for a, c in counts.items() if c > 0],
            absent_accessors=[a for a, c in counts.items() if c == 0],
            reg_write_symbols=sorted({s for s in defined
                                      if re.search(r"reg.*write|write.*reg", s, re.I)})[:40],
            hal_vtable_symbols=sorted({s for s in defined
                                       if re.search(r"hal.*(func|tbl|table|vtable|ops)|"
                                                    r"ah_func|hal_funcs", s, re.I)})[:40],
        ))
    r197 = dict(
        meta=dict(stage="197A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage197a_to_199a_hal_and_xw_delta.py",
                  scope="offline static; no module loaded, no register written, no radio contacted",
                  premise_correction="ah_reg_write and OS_REG_WRITE do not exist as symbols in "
                                     "ath_hal.ko (0 raw hits each); wmi_unified_cmd_send does "
                                     "exist in umac.ko (3 raw hits)",
                  radio_safety="static only"),
        modules=acc_rows,
        summary=dict(
            modules=len([r for r in acc_rows if r.get("status") == "ok"]),
            ah_reg_write_present=any(r.get("raw_string_counts", {}).get("ah_reg_write")
                                     for r in acc_rows),
            os_reg_write_present=any(r.get("raw_string_counts", {}).get("OS_REG_WRITE")
                                     for r in acc_rows),
            wmi_unified_cmd_send_present=any(
                r.get("raw_string_counts", {}).get("wmi_unified_cmd_send") for r in acc_rows),
            reg_write_symbols=max((len(r.get("reg_write_symbols", [])) for r in acc_rows),
                                  default=0),
            hal_vtable_symbols=max((len(r.get("hal_vtable_symbols", [])) for r in acc_rows),
                                   default=0)),
        gaps=["the register-write indirection was not traced to a concrete vtable slot: only "
              "the presence/absence of the named accessors and the symbol inventory are reported",
              "wmi_unified_cmd_send is located as a string/symbol but its call graph into the "
              "firmware command path was not reconstructed",
              "no dynamic validation"])
    OUT_197.write_text(json.dumps(r197, indent=2) + "\n", encoding="utf-8")
    s = r197["summary"]
    print(f"[197A] modules={s['modules']} ah_reg_write={s['ah_reg_write_present']} "
          f"OS_REG_WRITE={s['os_reg_write_present']} wmi_send={s['wmi_unified_cmd_send_present']} "
          f"reg_syms={s['reg_write_symbols']} vtable_syms={s['hal_vtable_symbols']}")

    # ------------------------------- 198A
    data = json.loads(KNOBS.read_text(encoding="utf-8"))
    knobs = data["knobs"]
    knob_tokens = {}
    for k in knobs:
        n = str(k.get("name") or "")
        knob_tokens[n] = set(re.findall(r"[a-z0-9]{4,}", n.lower()))
    champ = json.loads(CHAMPION.read_text(encoding="utf-8")) if CHAMPION.exists() else {}
    rounds = champ.get("rounds_r1_to_r18_ledger", [])
    rows198 = []
    for r in rounds:
        title = str(r.get("title") or "")
        toks = set(re.findall(r"[a-z0-9]{4,}", title.lower()))
        cands = []
        for name, kt in knob_tokens.items():
            if kt and len(kt & toks) >= max(1, min(2, len(kt))):
                cands.append(name)
        rows198.append(dict(
            round_id=r.get("round_id"), title=title, decision=r.get("decision"),
            arm_b_goodput=r.get("arm_b_mean_goodput_mbps"),
            arm_b_p95=r.get("arm_b_mean_p95_rtt_ms"),
            pareto_delta_pct=r.get("pareto_score_delta_pct"),
            token_overlap=sorted(toks)[:20],
            airoa_candidates=cands[:12], candidate_count=len(cands)))
    r198 = dict(
        meta=dict(stage="198A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage197a_to_199a_hal_and_xw_delta.py",
                  scope="offline static cross-reference; no device access",
                  champion=str(CHAMPION.relative_to(REPO_ROOT)).replace("\\", "/"),
                  method="per-round parameter tokens from the champion title matched against "
                         "catalogue knob-name tokens; each match is a candidate",
                  claim_limit="candidate mappings only; airOS-side effect was not measured, so "
                              "the equivalence is unproven in both directions",
                  radio_safety="static only"),
        rounds=rows198,
        summary=dict(rounds=len(rows198),
                     rounds_with_candidates=sum(1 for r in rows198 if r["candidate_count"]),
                     total_candidates=sum(r["candidate_count"] for r in rows198),
                     equivalence_confirmed=0,
                     champion_rounds_declared=champ.get("total_counterbalanced_rounds")),
        gaps=["the champion records outcomes per round, not per knob: a candidate set is not a "
              "mapping",
              "no airOS-side measurement was performed to confirm any equivalence",
              "the 18 questions are answered with candidates, not proofs"])
    OUT_198.write_text(json.dumps(r198, indent=2) + "\n", encoding="utf-8")
    s = r198["summary"]
    print(f"[198A] rounds={s['rounds']} with_candidates={s['rounds_with_candidates']} "
          f"candidates={s['total_candidates']} equivalence={s['equivalence_confirmed']}")

    # ------------------------------- 199A
    tables = {}
    for label, bins in BINARIES.items():
        tables[label] = {}
        for name, path in bins.items():
            if not path.exists():
                tables[label][name] = dict(status="absent")
                continue
            blob = path.read_bytes()
            a = applets_of(blob)
            tables[label][name] = dict(status="ok", bytes=len(blob),
                                       sha256=hashlib.sha256(blob).hexdigest(), **a)
    wa = tables.get("WA.v8.7.25", {})
    xw = tables.get("XW.v6.3.6", {})
    delta = {}
    for b in ("ubntbox", "athbox"):
        wn = set(wa.get(b, {}).get("names", []))
        xn = set(xw.get(b, {}).get("names", []))
        delta[b] = dict(wa_count=len(wn), xw_count=len(xn),
                        only_in_wa=sorted(wn - xn), only_in_xw=sorted(xn - wn),
                        common=sorted(wn & xn), common_count=len(wn & xn))
    r199 = dict(
        meta=dict(stage="199A", generated_utc="2026-10-26T00:00:00Z",
                  tool="tools/re/audit_stage197a_to_199a_hal_and_xw_delta.py",
                  scope="offline static; no device access",
                  premise_correction="WA.v8.7.11 does not exist in this repository; the "
                                     "comparison uses WA.v8.7.25 against XW.v6.3.6",
                  radio_safety="static only"),
        tables=tables, delta=delta,
        summary=dict(
            ubntbox_wa=delta["ubntbox"]["wa_count"],
            ubntbox_xw=delta["ubntbox"]["xw_count"],
            ubntbox_only_wa=len(delta["ubntbox"]["only_in_wa"]),
            ubntbox_only_xw=len(delta["ubntbox"]["only_in_xw"]),
            athbox_wa=delta["athbox"]["wa_count"],
            athbox_xw=delta["athbox"]["xw_count"],
            athbox_only_wa=len(delta["athbox"]["only_in_wa"]),
            athbox_only_xw=len(delta["athbox"]["only_in_xw"])),
        gaps=["applet presence is not applet behaviour: a name present in both builds may be "
              "implemented differently",
              "XW.v6.3.6 is airOS 6 and WA.v8.7.25 is airOS 8, so the delta conflates versions "
              "and product lines",
              "no dynamic validation"])
    OUT_199.write_text(json.dumps(r199, indent=2) + "\n", encoding="utf-8")
    s = r199["summary"]
    print(f"[199A] ubntbox WA={s['ubntbox_wa']} XW={s['ubntbox_xw']} "
          f"onlyWA={s['ubntbox_only_wa']} onlyXW={s['ubntbox_only_xw']} | "
          f"athbox WA={s['athbox_wa']} XW={s['athbox_xw']} "
          f"onlyWA={s['athbox_only_wa']} onlyXW={s['athbox_only_xw']}")
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
