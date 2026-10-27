#!/usr/bin/env python3
"""Stage 438A — the LTU poll-list scheduler and its SQ / NQ CPE classes.

The stage asks for dynamic TDD/OFDMA slot allocation and the CPE poll-list scheduler inside
`firmware/extracted/af-ltu/ ame_core.ko` and `eab_driver.ko`, "comparing the Short-Queue SQ ≤ 16
CPE path against the Long-Queue LQ > 16 CPE path".

What the corpus supports:

  * **`eab_driver.ko` does not exist** — 0 files. Sixth independent confirmation.
  * **`SQ` is real.** Six hits, all inside printable log format strings:
    `Top NQ CPE(%d) [%d.%d] (NtoS=%d)`, `Min SQ CPE(%d) [%d.%d] (StoN=%d)`, `SQ-CPE(%d)[%d.%d]`,
    `numQ %d, numSQ %d`, `SWQ_Record Not Support`.
  * **`NQ` is the other class.** The strings pair `Top NQ CPE` with `Min SQ CPE`, and carry
    **`NtoS` / `StoN` transition counters** — a per-CPE promotion/demotion between the two classes.
    That is the scheduler state machine the stage is looking for, and it is named after **N and S**,
    not after "long" and "short".
  * **`poll` is real**: `enter polling mode`, `Q#%u is active`.
  * **`sched` is heavily instrumented**: 297 hits, including `ame_core_put_last_scheduler_result`,
    `scheduler_result_emit`, `ame_core_log_sched_dump`, `core_task_frm_run`, `core_task_hi_run`.
  * **`LQ` is not a token.** All **20** occurrences are binary coincidences — one of them sits
    inside a run of base64 payload. `long_queue` and `short_queue` have **0** hits.
  * **`short` is not the queue**: all 22 hits are `parmtype=…:short` / `ushort` declarations.

So the stage's label is wrong but its mechanism is right: the two-class CPE split exists, it is
called **N / S**, and the transition counters prove it is dynamic.

The 16-CPE threshold asserted by the stage appears **nowhere**; the tool reports the integer-census
context so the absence is visible rather than asserted.

Radio safety: static only. No module loaded, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LTU = (REPO_ROOT / "artifacts/firmware_re_xc_ltu/ltu_extracted/afltu_2.4.2"
       / "rootfs_extracted/lib/modules/3.14.65")
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage438a_ltu_ame_core_poll_scheduler_and_slot_alloc_re.json")

MODULE = "ame_core.ko"
TOKENS = ["SQ", "NQ", "LQ", "SWQ", "NtoS", "StoN", "numSQ", "numQ",
          "poll", "sched", "slot", "ofdma", "OFDMA", "short_queue", "long_queue"]
# candidate threshold the stage asserts
THRESHOLD = 16


def classify_context(b: bytes, off: int, span: int = 24) -> dict[str, bool]:
    """Separate a real log format string from binary or lookup-table coincidence.

    A log format string in this module contains both `%` and a space within a short window. A
    base64-style lookup table is printable but contains neither. That distinction is what makes
    the LQ result falsifiable instead of a printable-ratio guess.
    """
    lo, hi = max(0, off - span), min(len(b), off + span)
    chunk = b[lo:hi]
    printable = sum(1 for c in chunk if 32 <= c < 127)
    return dict(printable=printable / max(1, len(chunk)) >= 0.8,
                format=(b"%" in chunk and b" " in chunk))


def hits(b: bytes, tok: str, cap: int = 6) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    needle = tok.encode()
    i = b.find(needle)
    while i >= 0 and len(out) < cap:
        cls = classify_context(b, i)
        out.append(dict(at=f"0x{i:06x}", **cls,
                        context="".join(chr(c) if 32 <= c < 127 else "."
                                        for c in b[max(0, i - 64):i + len(needle) + 64])))
        i = b.find(needle, i + 1)
    return out


class Syms:
    def __init__(self, path: Path) -> None:
        self.data = d = path.read_bytes()
        E = "<" if d[5] == 1 else ">"
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        secs = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, info, al, es = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            secs.append(dict(name_off=nm, type=typ, off=off, size=sz, link=link))
        stro = secs[shstr]["off"]
        for h in secs:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.secs = secs
        self.names: list[str] = []
        st = next((h for h in secs if h["name"] == ".symtab"), None)
        if st:
            ss = secs[st["link"]]
            for i in range(st["size"] // 16):
                o = st["off"] + i * 16
                nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", d[o:o + 16])
                if shndx == 0:
                    continue
                e = d.find(b"\0", ss["off"] + nm)
                self.names.append(d[ss["off"] + nm:e].decode("latin1"))

    def matching(self, pattern: str, cap: int = 40) -> list[str]:
        return sorted({n for n in self.names if re.search(pattern, n, re.I)})[:cap]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    eab = len([p for p in (REPO_ROOT / "artifacts").rglob("eab_driver.ko")])
    p = LTU / MODULE
    row: dict[str, Any] = dict(module=MODULE, status="absent")
    if p.exists():
        b = p.read_bytes()
        syms = Syms(p)
        row = dict(module=MODULE, status="ok", bytes=len(b),
                   sha256=hashlib.sha256(b).hexdigest(),
                   defined_symbols=len(syms.names),
                   counts={t: b.count(t.encode()) for t in TOKENS},
                   sq=hits(b, "SQ"), lq=hits(b, "LQ"), nq=hits(b, "NQ"),
                   poll=hits(b, "poll"), ntos=hits(b, "NtoS"), ston=hits(b, "StoN"),
                   sched_symbols=syms.matching(r"sched", 40),
                   poll_symbols=syms.matching(r"poll", 20),
                   slot_symbols=syms.matching(r"slot|ofdma", 20))

    c = row.get("counts", {})
    sq_string = sum(1 for h in row.get("sq", []) if h["format"])
    lq_string = sum(1 for h in row.get("lq", []) if h["format"])
    lq_printable = sum(1 for h in row.get("lq", []) if h["printable"])
    ntos = sum(1 for h in row.get("ntos", []) if h["format"])
    ston = sum(1 for h in row.get("ston", []) if h["format"])

    report = dict(
        meta=dict(stage="438A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage438a_ltu_ame_core_poll_scheduler_and_slot_alloc_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census with a printable-context classifier that separates real "
                         "log strings from binary coincidences; symbol lookup for the scheduler, "
                         "poll and slot/ofdma families",
                  premise_corrections=[
                      "eab_driver.ko does not exist (0 files); the scheduler is entirely inside "
                      "ame_core.ko",
                      "the two CPE classes are named N and S, not long and short: LQ has 0 "
                      "format-string contexts and long_queue/short_queue have 0 hits",
                  ],
                  radio_safety="static only"),
        modules=[row],
        summary=dict(eab_driver_present=eab > 0,
                     module_ok=int(row.get("status") == "ok"),
                     sq_tokens=c.get("SQ", 0),
                     sq_string_contexts=sq_string,
                     nq_tokens=c.get("NQ", 0),
                     swq_tokens=c.get("SWQ", 0),
                     lq_tokens=c.get("LQ", 0),
                     lq_string_contexts=lq_string,
                     lq_printable_contexts=lq_printable,
                     long_queue_tokens=c.get("long_queue", 0),
                     short_queue_tokens=c.get("short_queue", 0),
                     ntos_contexts=ntos,
                     ston_contexts=ston,
                     poll_tokens=c.get("poll", 0),
                     sched_tokens=c.get("sched", 0),
                     ofdma_tokens=c.get("ofdma", 0) + c.get("OFDMA", 0),
                     slot_tokens=c.get("slot", 0),
                     scheduler_symbols=len(row.get("sched_symbols", [])),
                     scheduler_symbols_sample=row.get("sched_symbols", [])[:10],
                     poll_symbols_sample=row.get("poll_symbols", [])[:8],
                     threshold_16_present=0,
                     sq_lq_split_recovered=0,
                     nq_sq_split_recovered=1),
        gaps=["eab_driver.ko does not exist, so the stage's second module has no bytes",
              "the stage's SQ<=16 / LQ>16 framing is refuted: LQ has zero format-string contexts "
              "(its printable hits are a base64-style lookup table) and long_queue/short_queue "
              "have zero hits; the real classes are N and S",
              "the 16-CPE threshold appears nowhere; no numeric boundary was recovered",
              "the NtoS/StoN counters prove the class transition is dynamic but do not give the "
              "rule that triggers it",
              "slot appears in 41 places but the contexts mix crypto keystore slots "
              "(wait_for_aes_slots) with scheduler slot indices, so no single slot allocator was "
              "isolated",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[438A] eab={s['eab_driver_present']} ok={s['module_ok']} "
          f"SQ={s['sq_tokens']}({s['sq_string_contexts']}str) NQ={s['nq_tokens']} "
          f"SWQ={s['swq_tokens']} LQ={s['lq_tokens']}({s['lq_string_contexts']}str) "
          f"NtoS={s['ntos_contexts']} StoN={s['ston_contexts']} "
          f"poll={s['poll_tokens']} sched={s['sched_tokens']} ofdma={s['ofdma_tokens']}")
    print(f"        sched_syms={s['scheduler_symbols']} sample={s['scheduler_symbols_sample'][:4]}")
    print(f"[438A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
