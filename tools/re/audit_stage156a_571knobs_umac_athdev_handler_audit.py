#!/usr/bin/env python3
"""Stage 156A — the 571-knob catalogue audited against real `umac.ko` / `ath_dev.ko` strings.

The question is which of the 571 catalogue entries have a *real handler* in the wireless
driver modules, as opposed to being catalogue-only names. The honest way to answer it from
static evidence is:

  1. harvest every printable string from `umac.ko` and `ath_dev.ko` for WA, XC and XW;
  2. for each knob, look for its name (and its last dotted component) among those strings;
  3. classify the knob as `handler_name_present` or `no_handler_name`.

**A string match is a necessary condition, not a proof of effect.** A driver can carry a
command name and still no-op it, and a knob can be implemented without its catalogue name
appearing as a literal. So the tool reports a *coverage bound*, and every "effect on MAC/BB/
PCU registers" claim is left `UNKNOWN` unless a future pass traces the handler body into
register writes. That limit is stated in the receipt and enforced by a test.

Radio safety: static only. No module loaded, no radio contacted.

Read-only: the only write is the receipt JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
XW = REPO_ROOT / "artifacts" / "firmware_re_xw_m5"
SOURCE = REPO_ROOT / "orchestration" / "autoresearch" / "firmware_knob_candidates.json"
DEFAULT_OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage156a_571knobs_umac_athdev_handler_audit.json"

_spec = importlib.util.spec_from_file_location(
    "w4a", REPO_ROOT / "tools" / "re" / "audit_stage81a_w4a_wa_xc_ko_proc_ioctl.py")
w4a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w4a)


class Ko:
    """ET_REL reader with endianness detection (MIPS BE for these modules)."""

    def __init__(self, path: Path) -> None:
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


def find_modules() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for label, root in (("WA.v8.7.25", FW / "wa_8725_rootfs"),
                        ("XC.v8.7.25", FW / "xc_8725_rootfs")):
        for name in ("umac.ko", "ath_dev.ko"):
            hits = list(root.rglob(name))
            if hits:
                out[f"{label}:{name}"] = hits[0]
    for label in ("xw_614_rootfs", "xw_636_rootfs"):
        root = XW / label
        for name in ("umac.ko", "ath_dev.ko"):
            hits = list(root.rglob(name))
            if hits:
                tag = "XW.6.1.4" if "614" in label else "XW.6.3.6"
                out[f"{tag}:{name}"] = hits[0]
    return out


def knob_tokens(name: str) -> list[str]:
    """Candidate literals to look for: the full name and its last component."""
    toks = [name]
    if "." in name:
        toks.append(name.rsplit(".", 1)[-1])
    if " " in name:
        toks.extend(name.split())
    return [t for t in toks if len(t) >= 4]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    mods = find_modules()
    per_module: dict[str, Any] = {}
    union: set[str] = set()
    for key, path in sorted(mods.items()):
        ko = Ko(path)
        strs = ko.strings()
        union |= strs
        per_module[key] = dict(bytes=len(ko.data),
                               sha256=hashlib.sha256(ko.data).hexdigest(),
                               strings=len(strs))

    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    knobs = data["knobs"]

    rows = []
    by_boundary: dict[str, Counter] = defaultdict(Counter)
    for k in knobs:
        name = str(k.get("name") or "")
        toks = knob_tokens(name)
        hit = next((t for t in toks if t in union), None)
        boundary = str(k.get("boundary") or "unknown")
        rows.append(dict(
            id=k.get("id"), name=name, family=k.get("family"), boundary=boundary,
            classification=k.get("classification"),
            handler_name_present=hit is not None,
            matched_literal=hit,
            effect_on_registers="UNKNOWN",
        ))
        by_boundary[boundary]["present" if hit else "absent"] += 1

    present = [r for r in rows if r["handler_name_present"]]
    report = dict(
        meta=dict(
            stage="156A", phase="156A", generated_utc="2026-10-26T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/re/audit_stage156a_571knobs_umac_athdev_handler_audit.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(DEFAULT_OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            scope="offline static analysis; no module loaded, no radio contacted",
            source=str(SOURCE.relative_to(REPO_ROOT)).replace("\\", "/"),
            source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            method="printable-string harvest from every SHT_PROGBITS section of umac.ko and "
                   "ath_dev.ko (WA, XC, XW), then exact-literal lookup of each knob name and "
                   "its last dotted component",
            claim_limit="a string match is a NECESSARY condition, not proof of effect: a "
                        "driver can carry a command name and still no-op it, and a knob can "
                        "be implemented without its catalogue name appearing as a literal. "
                        "effect_on_registers is therefore UNKNOWN for every knob.",
            radio_safety="static only",
        ),
        modules=per_module,
        summary=dict(
            modules=len(per_module),
            knobs=len(rows),
            handler_name_present=len(present),
            no_handler_name=len(rows) - len(present),
            coverage_pct=round(100.0 * len(present) / len(rows), 2) if rows else 0.0,
            by_boundary={b: dict(c) for b, c in sorted(by_boundary.items())},
            distinct_literals_matched=len({r["matched_literal"] for r in present}),
            effect_on_registers_confirmed=0,
        ),
        knobs=rows,
        gaps=[
            "a string match does not prove the handler executes or that it writes a register",
            "effect_on_registers is UNKNOWN for all 571: proving MAC/BB/PCU effect needs the "
            "handler body traced into register writes, which this stage does not do",
            "names are matched as exact literals; a knob whose catalogue spelling differs "
            "from the driver string (case, underscore, abbreviation) is counted absent",
            "no dynamic validation: no module loaded, no radio contacted",
        ],
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[156A] modules={s['modules']} knobs={s['knobs']} "
          f"present={s['handler_name_present']} absent={s['no_handler_name']} "
          f"({s['coverage_pct']}%)")
    for b, c in s["by_boundary"].items():
        print(f"       {b:<22} {c}")
    print(f"[156A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
