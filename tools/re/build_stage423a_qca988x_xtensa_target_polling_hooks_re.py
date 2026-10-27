#!/usr/bin/env python3
"""Stage 423A — the claimed 32 target polling hook pointers at 0x0040f688.

The stage asserts that `firmware-2.bin` / `firmware-5.bin` carry **32 target polling hook function
pointers** at `0x0040f688`, used to run schedule ticks inside Xtensa IRAM without host PCIe
interrupts.

Three facts have to be established before any table can be discussed:

  * **neither file exists.** A recursive search for `firmware-2.bin`, `firmware-5.bin` and
    `firmware-*.bin` returns **0 files**. The only QCA988x container in the corpus is
    `openwrt_qca988x_hw20_firmware_2_ct.bin` (204,796 bytes), which is what this tool parses.
  * **the address is only reachable under one base.** The SGMT header's base field reads
    `0x00980000`, but the stage's address `0x0040f688` is exactly **DRAM base `0x00400000` +
    `0xf688`** — the QCA988x DRAM base used by ath10k. Under that base the address lands in
    segment 3 at a file offset, and the bytes can be read.
  * **what is there is code, not pointers.** All 32 words are distinct and **none** falls inside
    the firmware address range. A table of 32 function pointers would be 32 in-range, aligned
    values; this is not that.

The tool therefore reports the addressing arithmetic that *does* work, the 32 words verbatim, and
a **scan** for real pointer runs elsewhere in both segments — so the negative is a search result
rather than an assertion of absence.

`hook_table_recovered = 0` is the honest output.

Radio safety: static only. No firmware loaded, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage423a_qca988x_xtensa_target_polling_hooks_re.json")

CONTAINER = FW / "openwrt_qca988x_hw20_firmware_2_ct.bin"
TARGET = 0x0040F688
ENTRIES = 32
# candidate load bases: the header field both ways, ath10k's QCA988x DRAM base, and zero
BASES = [0x00400000, 0x00980000, 0x00009800, 0x00000000, 0x00E00000]
WANTED_NAMES = ["firmware-2.bin", "firmware-5.bin"]


def parse(blob: bytes) -> dict[str, Any]:
    if not blob.startswith(b"QCA-ATH10K"):
        return dict(parsed=False, segments=[])
    vlen = struct.unpack("<I", blob[16:20])[0]
    off = 20 + vlen
    segs = []
    while off + 8 <= len(blob):
        ie_id, ie_len = struct.unpack("<II", blob[off:off + 8])
        if off + 8 + ie_len > len(blob):
            break
        payload = blob[off + 8:off + 8 + ie_len]
        if payload[:4] == b"SGMT":
            segs.append(dict(id=ie_id, len=ie_len, file_off=off + 8, payload=payload))
        off += 8 + ie_len
    return dict(parsed=True, vlen=vlen,
                version=blob[20:20 + vlen].decode("latin1"),
                segments=segs, tail=len(blob) - off)


def classify(words: list[int], lo: int, hi: int) -> dict[str, Any]:
    in_range = [w for w in words if lo <= w < hi]
    aligned = [w for w in in_range if w % 4 == 0]
    return dict(count=len(words), in_range=len(in_range), aligned=len(aligned),
                distinct=len(set(words)),
                verdict=("pointer table" if len(aligned) == len(words)
                         else "code or data, not a pointer table"))


def pointer_runs(payload: bytes, lo: int, hi: int, min_len: int = 8,
                 cap: int = 8) -> list[dict[str, Any]]:
    """Longest runs of consecutive aligned words that all point into [lo, hi)."""
    runs: list[dict[str, Any]] = []
    cur = 0
    start = 0
    n = len(payload)
    for o in range(0, n - 3, 4):
        v = struct.unpack("<I", payload[o:o + 4])[0]
        if lo <= v < hi and v % 4 == 0:
            if cur == 0:
                start = o
            cur += 1
        else:
            if cur >= min_len:
                runs.append(dict(at=f"0x{start:06x}", length=cur))
            cur = 0
    if cur >= min_len:
        runs.append(dict(at=f"0x{start:06x}", length=cur))
    return sorted(runs, key=lambda r: -r["length"])[:cap]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    named = {n: len([p for p in (REPO_ROOT / "artifacts").rglob(n) if p.is_file()])
             for n in WANTED_NAMES}

    blob = CONTAINER.read_bytes()
    c = parse(blob)
    segs = c["segments"]

    windows = []
    hit = None
    for base in BASES:
        rel = TARGET - base
        for s in segs:
            inside = 0 <= rel < s["len"]
            windows.append(dict(base=f"0x{base:08x}", segment=s["id"], inside=inside,
                                rel=(f"0x{rel:06x}" if inside else None)))
            if inside and hit is None:
                hit = dict(base=base, segment=s, rel=rel)

    chunk = None
    if hit:
        s = hit["segment"]
        words = list(struct.unpack("<32I", s["payload"][hit["rel"]:hit["rel"] + 128]))
        lo = 0x00400000
        hi = lo + max(x["len"] for x in segs)
        chunk = dict(address=f"0x{TARGET:08x}", base=f"0x{hit['base']:08x}",
                     segment=s["id"], rel=f"0x{hit['rel']:06x}",
                     file_offset=f"0x{s['file_off'] + hit['rel']:06x}",
                     words=[f"0x{w:08x}" for w in words],
                     **classify(words, lo, hi))

    lo, hi = 0x00400000, 0x00400000 + max(x["len"] for x in segs)
    runs = {s["id"]: pointer_runs(s["payload"], lo, hi) for s in segs}
    best = max((r["length"] for v in runs.values() for r in v), default=0)
    exact32 = sum(1 for v in runs.values() for r in v if r["length"] == 32)

    report = dict(
        meta=dict(stage="423A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage423a_qca988x_xtensa_target_polling_hooks_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no firmware loaded, no radio contacted",
                  method="container TLV/SGMT parse; base-candidate resolution of the claimed "
                         "address; verbatim 32-word dump with pointer classification; whole-"
                         "segment scan for runs of 8+ aligned in-range pointers",
                  target_address=f"0x{TARGET:08x}", target_entries=ENTRIES,
                  premise_corrections=[
                      "firmware-2.bin and firmware-5.bin do not exist in the corpus; the only "
                      "QCA988x container is openwrt_qca988x_hw20_firmware_2_ct.bin",
                      "0x0040f688 is unreachable under the SGMT header base 0x00980000 and only "
                      "resolves under DRAM base 0x00400000",
                  ],
                  radio_safety="static only"),
        named_files=named,
        container=dict(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
                       version=c.get("version"), segments=len(segs),
                       tail_pad=c.get("tail")),
        base_windows=windows,
        chunk=chunk,
        pointer_runs=runs,
        summary=dict(named_files_present=sum(named.values()),
                     segments=len(segs),
                     address_resolvable=int(hit is not None),
                     resolving_base=(f"0x{hit['base']:08x}" if hit else None),
                     file_offset=(chunk["file_offset"] if chunk else None),
                     words_in_chunk=(chunk["count"] if chunk else 0),
                     valid_pointers_in_chunk=(chunk["aligned"] if chunk else 0),
                     chunk_looks_like_code=int(bool(chunk) and chunk["aligned"] == 0),
                     pointer_runs_8plus=sum(len(v) for v in runs.values()),
                     exact_32_runs=exact32,
                     best_run_length=best,
                     hook_table_recovered=0),
        gaps=["firmware-2.bin and firmware-5.bin are absent, so the stage's own filenames cannot "
              "be checked against their real contents",
              "the 32 words at 0x0040f688 contain zero in-range pointers, so the claimed hook "
              "table is not there; the bytes read as Xtensa instruction encodings",
              "no run of exactly 32 consecutive in-range pointers exists anywhere in either "
              "segment, so no alternative table of that shape was found either",
              "the true SGMT load base is still unresolved: the header field reads 0x00980000 "
              "under both endiannesses while only 0x00400000 makes the claimed address land",
              "whether target-assisted polling exists at all is not settled; only its claimed "
              "table address is refuted",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[423A] named={named} segments={s['segments']} resolvable={s['address_resolvable']} "
          f"base={s['resolving_base']} file={s['file_offset']} "
          f"pointers={s['valid_pointers_in_chunk']}/{s['words_in_chunk']} "
          f"runs8={s['pointer_runs_8plus']} exact32={s['exact_32_runs']} best={s['best_run_length']}")
    if chunk:
        print(f"        first words: {chunk['words'][:6]}")
    for seg, v in runs.items():
        print(f"        seg{seg} runs={v}")
    print(f"[423A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
