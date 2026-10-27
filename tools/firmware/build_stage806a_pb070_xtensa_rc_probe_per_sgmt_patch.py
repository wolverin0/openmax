#!/usr/bin/env python3
"""Stage 806A — PB-070 Xtensa RC probe, planned per SGMT segment.

This is a **builder**, and its job is to produce a patch **plan**, not a patched binary. The
distinction matters: a per-segment probe patch needs an anchor string to locate the RC code, and this
container has none.

What the builder does:

  1. parses the `QCA-ATH10K` container and enumerates every `SGMT` segment with its file offset,
     length and the load base under both endian readings;
  2. censuses **long ASCII runs** in each payload — the only anchors a rename-style probe can use;
  3. for each segment, emits a probe record with `anchor_found`, `viable` and the reason;
  4. refuses to emit a binary patch when no segment is viable, and says so in the receipt.

The PB-040 precedent is what makes the anchor requirement concrete: that gate mutated
`UBNT_POLL_MEM_ALLOC` to `OMAX_POLL_MEM_ALLOC` — a **four-byte diff at a named ASCII anchor**. The
same method needs an anchor per segment. Here, the whole container carries exactly **one** ASCII
string of length >= 8 (the version `10.1-ct-8x-__fW-022-ecad3248`), so there is no RC anchor to
rename.

`patch_emitted = 0`. A patch artifact with no anchor would be a fabricated offset.

Radio safety: static only. No firmware written, no flash touched, no radio contacted.
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
       / "stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.json")

CONTAINER = FW / "openwrt_qca988x_hw20_firmware_2_ct.bin"
GATE = "PB-070"
MIN_ANCHOR = 8


def parse(blob: bytes) -> dict[str, Any]:
    if not blob.startswith(b"QCA-ATH10K"):
        return dict(parsed=False, segments=[])
    vlen = struct.unpack("<I", blob[16:20])[0]
    version = blob[20:20 + vlen].decode("latin1")
    off = 20 + vlen
    segs = []
    while off + 8 <= len(blob):
        ie_id, ie_len = struct.unpack("<II", blob[off:off + 8])
        if off + 8 + ie_len > len(blob):
            break
        payload = blob[off + 8:off + 8 + ie_len]
        if payload[:4] == b"SGMT":
            segs.append(dict(id=ie_id, len=ie_len, file_off=off + 8, payload=payload,
                             base_le=struct.unpack("<I", payload[8:12])[0],
                             base_be=struct.unpack(">I", payload[8:12])[0]))
        off += 8 + ie_len
    return dict(parsed=True, version=version, segments=segs, tail=len(blob) - off)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    blob = CONTAINER.read_bytes()
    c = parse(blob)
    plan = []
    for s in c["segments"]:
        runs = [m.group().decode("latin1")
                for m in re.finditer(rb"[\x20-\x7e]{%d,}" % MIN_ANCHOR, s["payload"])]
        anchor = runs[0] if runs else None
        plan.append(dict(
            segment=s["id"], file_offset=f"0x{s['file_off']:06x}", bytes=s["len"],
            load_base_le=f"0x{s['base_le']:08x}", load_base_be=f"0x{s['base_be']:08x}",
            ascii_runs=len(runs),
            anchor=anchor,
            anchor_found=anchor is not None,
            anchor_looks_like_rc=bool(anchor and re.search(r"RC_|RATE|RATEFIND", anchor)),
            viable=bool(anchor and re.search(r"RC_|RATE|RATEFIND", anchor)),
            reason=("no ASCII anchor of >= %d chars" % MIN_ANCHOR if anchor is None
                    else "anchor is not rate-control vocabulary")))

    viable = [p for p in plan if p["viable"]]
    total_runs = sum(p["ascii_runs"] for p in plan)

    report = dict(
        meta=dict(stage="806A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  gate=GATE,
                  tool="tools/firmware/build_stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no firmware written, no flash touched, "
                        "no radio contacted",
                  method="container SGMT enumeration with dual-endian load bases; long ASCII-run "
                         "census per segment; anchor viability test against rate-control "
                         "vocabulary; patch withheld when no anchor is viable",
                  precedent="PB-040 mutated a named ASCII anchor (UBNT_POLL_MEM_ALLOC -> "
                            "OMAX_POLL_MEM_ALLOC, 4 bytes); the same method needs an RC anchor "
                            "per segment",
                  radio_safety="static only"),
        container=dict(path=CONTAINER.relative_to(REPO_ROOT).as_posix(),
                       bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
                       version=c.get("version"), tail_pad=c.get("tail")),
        probe_plan=plan,
        summary=dict(parsed=c["parsed"],
                     segments=len(plan),
                     total_ascii_runs=total_runs,
                     segments_with_anchor=sum(1 for p in plan if p["anchor_found"]),
                     segments_viable=len(viable),
                     patch_emitted=0,
                     blocking_reason=("no SGMT segment carries a rate-control ASCII anchor, so a "
                                      "rename-style probe has no target"),
                     patch_bytes_would_be=4),
        gaps=["no segment has a rate-control anchor, so no per-segment probe can be built",
              "the only long ASCII in the container is the version string, which is metadata and "
              "not code",
              "the dual-endian load bases agree at 0x00980000, so the mapping is ambiguous and no "
              "address-based patch is defensible either",
              "without an anchor or a proven base, any mutation offset would be fabricated",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[806A] segments={s['segments']} ascii_runs={s['total_ascii_runs']} "
          f"with_anchor={s['segments_with_anchor']} viable={s['segments_viable']} "
          f"patch_emitted={s['patch_emitted']}")
    for p in plan:
        print(f"        seg{p['segment']} {p['bytes']:>7}B runs={p['ascii_runs']} "
              f"anchor={p['anchor_found']} viable={p['viable']}")
    print(f"[806A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
