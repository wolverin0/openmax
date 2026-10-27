#!/usr/bin/env python3
"""Stage 459A — WAL TX TID pause/unpause, BAR failure handling, requeue and excess-retry counters.

The stage names four things:

  * **WAL TX TID pause / unpause**;
  * **BlockAckReq (BAR) failure handling**;
  * the **`mpdus_requed`** counter;
  * the **`excess_retries`** counter.

`firmware-2.bin` and `firmware-5.bin` are **absent** (Stages 423A, 437A, 451A), so everything here
comes from the vendor `umac.ko`, where all four are present in one form or another — but not always
in the form the stage spells.

  * **`mpdus_requed` is exact.** It sits in a TX statistics dump beside `phy underrun`, `tx_abort`
    and `last rc`.
  * **`excess_retries` is spelled with a space, not an underscore.** The dump line reads
    `excess retries : %u`. An underscore search returns **0**; the real string returns 2. That is
    the kind of detail that decides whether a grep "finds" a counter.
  * **BAR failures are a named taxonomy:** `WAL_DBGID_BAR_TX_FAIL` and `WAL_DBGID_BAR_ALLOC_FAIL`
    sit next to `WAL_DBGID_STA_KICKOUT` and `WAL_DBGID_LOCAL_DATA_TX_FAIL`.
  * **TID pause is a real pair of routines:** `ath_net80211_exist_pendingfrm_tidq` and
    `ath_net80211_reset_pasued_tid` — the latter carrying Ubiquiti's own `pasued` typo, which is
    why an exact `paused` search misses it.

The counters' **increment sites** are not visible: a `%u` in a printf format is the read side. The
tool reports the read side and says so.

Radio safety: static only. No firmware loaded, no module loaded, no radio contacted.
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
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage459a_qca988x_wal_tx_tid_pause_and_bar_recovery_re.json")

MODULES = {
    "WA.v8.7.25:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC.v8.7.25:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
}

# exact counter spellings, including the one the stage gets wrong
COUNTERS = ["mpdus_requed", "excess retries", "excess_retries", "tx_abort",
            "phy underrun", "last rc", "requeue", "requed"]
# WAL debug identifiers for BAR / kickout / local failure
BAR_IDS = ["WAL_DBGID_BAR_TX_FAIL", "WAL_DBGID_BAR_ALLOC_FAIL",
           "WAL_DBGID_STA_KICKOUT", "WAL_DBGID_LOCAL_DATA_TX_FAIL"]
# TID pause and retry-state vocabulary
TID = ["pause", "unpause", "pause_tid", "paused", "pasued", "tidq", "TID"]
# exact symbols that carry the mechanism
SYMBOL_PAT = r"wal|tid|pause|bar|reque|retry|xretry"


def ctx(b: bytes, tok: str, n: int = 3, w: int = 70) -> list[str]:
    out: list[str] = []
    needle = tok.encode()
    i = b.find(needle)
    while i >= 0 and len(out) < n:
        out.append("".join(chr(c) if 32 <= c < 127 else "."
                           for c in b[max(0, i - w):i + len(needle) + w]))
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

    def matching(self, pattern: str, cap: int = 30) -> list[str]:
        return sorted({n for n in self.names if re.search(pattern, n, re.I)})[:cap]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    fw_images = {n: len([p for p in (REPO_ROOT / "artifacts").rglob(n) if p.is_file()])
                 for n in ("firmware-2.bin", "firmware-5.bin")}

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        rows.append(dict(
            module=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            counters={t: b.count(t.encode()) for t in COUNTERS},
            bar_ids={t: b.count(t.encode()) for t in BAR_IDS},
            tid={t: b.count(t.encode()) for t in TID},
            counter_contexts={t: ctx(b, t) for t in ("mpdus_requed", "excess retries")
                              if b.count(t.encode())},
            bar_contexts=ctx(b, "WAL_DBGID_BAR_TX_FAIL", 2),
            tid_symbols=syms.matching(r"tid|pause_control|reset_pasued", 20),
            retry_symbols=syms.matching(r"retry|xretry|swretrystate", 20),
            wal_symbols=syms.matching(r"wal|bar", 20)))

    ok = [r for r in rows if r.get("status") == "ok"]
    mpdus = sum(r["counters"]["mpdus_requed"] for r in ok)
    excess_underscore = sum(r["counters"]["excess_retries"] for r in ok)
    excess_spaced = sum(r["counters"]["excess retries"] for r in ok)
    bar_total = sum(sum(r["bar_ids"].values()) for r in ok)
    tid_syms = sorted({n for r in ok for n in r["tid_symbols"]})
    retry_syms = sorted({n for r in ok for n in r["retry_symbols"]})
    wal_syms = sorted({n for r in ok for n in r["wal_symbols"]})
    pause_syms = [n for n in tid_syms if "pasued" in n or "pendingfrm_tidq" in n]

    report = dict(
        meta=dict(stage="459A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage459a_qca988x_wal_tx_tid_pause_and_bar_recovery_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no firmware loaded, no module loaded, "
                        "no radio contacted",
                  method="exact-string census of the counter spellings including the spaced "
                         "variant; WAL debug-id extraction; defined-symbol lookup for the TID "
                         "pause, retry-state and BAR families",
                  premise_corrections=[
                      "firmware-2.bin and firmware-5.bin are absent, so the firmware side of the "
                      "stage cannot be read",
                      "the counter is spelled `excess retries` with a space: an underscore search "
                      "returns 0 while the real string returns 2",
                  ],
                  radio_safety="static only"),
        firmware_images=fw_images,
        modules=rows,
        summary=dict(firmware_images_present=sum(fw_images.values()),
                     modules_ok=len(ok),
                     mpdus_requed_hits=mpdus,
                     excess_retries_underscore=excess_underscore,
                     excess_retries_spaced=excess_spaced,
                     excess_retries_spelling_refuted=int(excess_underscore == 0
                                                         and excess_spaced > 0),
                     bar_debug_id_hits=bar_total,
                     bar_failure_named=int(bar_total > 0),
                     tid_symbols=tid_syms,
                     pause_symbols=pause_syms,
                     tid_pause_named=int(len(pause_syms) > 0),
                     retry_symbols=retry_syms,
                     wal_symbols=wal_syms[:12],
                     stats_dump_present=int(mpdus > 0),
                     counter_increment_sites=0),
        gaps=["firmware-2.bin and firmware-5.bin are absent, so no WAL TX path can be read from "
              "an image",
              "the counters are visible only at their printf read side; the increment sites and "
              "the wrap/decay rules were not located",
              "`excess_retries` does not exist as a single token: the real string is "
              "`excess retries` with a space, which is why a naive grep reports zero",
              "the TID pause pair is named but not decoded: what queues a TID, and when it is "
              "released, is not established",
              "BAR recovery is present as a debug-id taxonomy (TX_FAIL, ALLOC_FAIL) with no "
              "state machine attached",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[459A] fw={s['firmware_images_present']} modules={s['modules_ok']} "
          f"mpdus_requed={s['mpdus_requed_hits']} "
          f"excess_us={s['excess_retries_underscore']} excess_sp={s['excess_retries_spaced']} "
          f"bar_ids={s['bar_debug_id_hits']} tid_pause={s['tid_pause_named']}")
    print(f"        pause_syms={pause_syms}")
    print(f"        retry_syms={retry_syms[:6]}")
    print(f"[459A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
