#!/usr/bin/env python3
"""Stage 155A — `ubnt_poll_host.ko` TDMA scheduler dissection (PtMP/PtP, Fixed vs Flexible).

Premise correction, verified first: there is **no WA.v8.7.11 / XC.v8.7.11 pair** of this
module. What exists is:

  * `wa_8725_rootfs/.../ubnt_poll_host.ko`  189,880 B
  * `xc_8725_rootfs/.../ubnt_poll_host.ko`  189,880 B
  * `2xc_8711_modules/ubnt_poll_host.ko`    186,560 B  (single 8.7.11 build, no WA/XC pair)

So the "WA.v8.7.11 vs XC.v8.7.11" comparison is reported as **not possible**, and the tool
compares the three modules that do exist: WA 8.7.25, XC 8.7.25, and the lone 8.7.11 build.

What it extracts per module:

  * **scheduler symbols** — every defined symbol matching poll/sched/tdma/slot/frame/airtime/
    fairness, which is how the PtMP scheduler and the Fixed/Flexible modes are named;
  * **HT_COMM dispatch surface** — symbols and strings for the `HT_COMM` message family, plus
    the small integer constants (0..20) that can be opcodes of that family;
  * **PtP vs PtP mode markers** — strings and symbols for fixed-frame, flexible-frame,
    superframe, guard, and per-station slot accounting;
  * **airtime fairness surface** — symbols matching fair/airtime/deficit/quantum/credit.

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
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
DEFAULT_OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage155a_ubnt_poll_host_tdma_scheduler_re.json"

_spec = importlib.util.spec_from_file_location(
    "w4a", REPO_ROOT / "tools" / "re" / "audit_stage81a_w4a_wa_xc_ko_proc_ioctl.py")
w4a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w4a)

MODULES = {
    "WA.v8.7.25": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XC.v8.7.25": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "8.7.11 (single build, no WA/XC pair)": FW / "2xc_8711_modules/ubnt_poll_host.ko",
}

BUCKETS = {
    "scheduler": re.compile(r"poll|sched|tdma|cycle|beacon|superframe", re.I),
    "slot": re.compile(r"slot|timeslot|quantum|credit|deficit|quota", re.I),
    "frame_mode": re.compile(r"fixed|flex|flexible|dynamic|static", re.I),
    "airtime": re.compile(r"airtime|fair|weight|throttle|budget", re.I),
    "ht_comm": re.compile(r"ht_comm|htcomm|comm_|cmd_|msg_|opcode", re.I),
    "ptp": re.compile(r"ptp|ptmp|point_to|master|slave|station|sta_", re.I),
    "guard": re.compile(r"guard|gap|tail|headroom|margin", re.I),
}


def strings_of(ko: Any) -> list[str]:
    out = set()
    for sect in (".rodata", ".rodata.str1.4", ".data"):
        h = ko.by_name.get(sect)
        if not h:
            continue
        blob = ko.data[h["off"]:h["off"] + h["size"]]
        for m in re.finditer(rb"[\x20-\x7e]{4,}", blob):
            s = m.group().decode("latin1")
            if 4 <= len(s) <= 120:
                out.add(s)
    return sorted(out)


def small_constants(ko: Any) -> dict[str, int]:
    """Counts of the MIPS `addiu reg,$zero,N` immediates in 0..20 (opcode candidates)."""
    hist: Counter[int] = Counter()
    for sect, blob, _o in ko.exec_sects:
        for off in range(0, max(0, len(blob) - 4), 4):
            w = ko.u32(sect, off)
            if w is None:
                continue
            op, rs, _rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, (w >> 16) & 0x1F, w & 0xFFFF
            if op == 0x09 and rs == 0 and 0 <= imm <= 20:
                hist[imm] += 1
    return {str(k): v for k, v in sorted(hist.items())}


def bucketize(names: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for b, rx in BUCKETS.items():
        hits = sorted({n for n in names if rx.search(n)})
        if hits:
            out[b] = hits[:80]
    return out


def audit(path: Path) -> dict[str, Any]:
    ko = w4a.Ko(path)
    defined = sorted({s[0] for s in ko.syms if s[3] != 0 and s[0]})
    undefined = sorted({s[0] for s in ko.syms if s[3] == 0 and s[0]})
    strs = strings_of(ko)
    return dict(
        path=path.name, bytes=len(ko.data), sha256=hashlib.sha256(ko.data).hexdigest(),
        symbols_total=len(ko.syms), defined=len(defined), undefined=len(undefined),
        defined_buckets=bucketize(defined), undefined_buckets=bucketize(undefined),
        string_buckets={b: sorted({s for s in strs if rx.search(s)})[:60]
                        for b, rx in BUCKETS.items()
                        if any(rx.search(s) for s in strs)},
        small_constants=small_constants(ko),
        ht_comm_symbols=sorted({n for n in defined + undefined if re.search(r"ht_comm|htcomm", n, re.I)}),
        frame_mode_strings=sorted({s for s in strs
                                   if re.search(r"fixed|flex", s, re.I)})[:40],
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(image=label, path=path.name, status="absent"))
            continue
        rows.append(dict(image=label, status="ok", **audit(path)))

    ok = [r for r in rows if r.get("status") == "ok"]
    wa = next((r for r in ok if r["image"] == "WA.v8.7.25"), {})
    xc = next((r for r in ok if r["image"] == "XC.v8.7.25"), {})
    v8711 = next((r for r in ok if r["image"].startswith("8.7.11")), {})

    pair_diff = None
    if wa and xc:
        pair_diff = dict(
            identical=wa["sha256"] == xc["sha256"],
            wa_sha256=wa["sha256"], xc_sha256=xc["sha256"],
            wa_bytes=wa["bytes"], xc_bytes=xc["bytes"],
            diff_byte_count=None,
            note="full byte diff is computed by the WA/XC ubntbox tool; here only identity and "
                 "size are asserted",
        )

    report = dict(
        meta=dict(
            stage="155A", phase="155A", generated_utc="2026-10-26T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/re/audit_stage155a_ubnt_poll_host_tdma_scheduler_re.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(DEFAULT_OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            scope="offline static analysis of ET_REL MIPS32 modules; no module loaded, "
                  "no radio contacted",
            method=".symtab classification into scheduler / slot / frame_mode / airtime / "
                   "ht_comm / ptp / guard buckets; .rodata string sweep; addiu $zero,N "
                   "histogram for opcode-range constants",
            premise_correction="there is no WA.v8.7.11 / XC.v8.7.11 pair for this module; "
                               "8.7.11 exists as a single build and the WA/XC pair exists "
                               "only at 8.7.25",
            radio_safety="static only; nothing loaded or executed",
        ),
        modules=rows,
        pair_diff=pair_diff,
        summary=dict(
            modules_audited=len(ok),
            wa_xc_identical=(pair_diff or {}).get("identical"),
            scheduler_symbols_wa=len(wa.get("defined_buckets", {}).get("scheduler", [])),
            slot_symbols_wa=len(wa.get("defined_buckets", {}).get("slot", [])),
            frame_mode_strings_wa=len(wa.get("frame_mode_strings", [])),
            airtime_symbols_wa=len(wa.get("defined_buckets", {}).get("airtime", [])),
            ht_comm_symbols=len(wa.get("ht_comm_symbols", [])),
            opcode_constants_wa=len(wa.get("small_constants", {})),
            v8711_bytes=v8711.get("bytes"),
        ),
        gaps=[
            "Fixed vs Flexible frame mode is reported as named symbols and strings, not as a "
            "decoded state machine: the branch conditions that select the mode were not "
            "traced",
            "HT_COMM 0..20 is reported as an opcode-range immediate histogram plus symbol "
            "names, not as a verified message table: a constant in 0..20 can be an array "
            "index or a size, not an opcode",
            "airtime fairness is reported as named symbols only; the scheduling arithmetic "
            "was not reconstructed",
            "the 8.7.11 build has no WA/XC counterpart, so no 8.7.11 comparison is possible",
            "no dynamic validation: no module loaded, no radio contacted",
        ],
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[155A] modules={s['modules_audited']} wa_xc_identical={s['wa_xc_identical']}")
    for r in ok:
        db = r["defined_buckets"]
        print(f"       {r['image']:<36} {r['bytes']:>7}B syms={r['symbols_total']:<5} "
              f"sched={len(db.get('scheduler', [])):<3} slot={len(db.get('slot', [])):<3} "
              f"airtime={len(db.get('airtime', [])):<3} "
              f"frame_str={len(r['frame_mode_strings']):<3} "
              f"htcomm={len(r['ht_comm_symbols'])}")
    print(f"[155A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
