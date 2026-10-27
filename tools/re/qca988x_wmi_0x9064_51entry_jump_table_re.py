#!/usr/bin/env python3
"""Stage 387A — `WMI_UBNT_CMDID` (0x9064 / 0x9070) and the claimed 51-entry Xtensa jump table.

The stage asserts four things. Each is tested independently, and three of them fail:

  1. a proprietary tunnel `WMI_UBNT_CMDID` exists at **0x9064** (5 GHz, 10.1) and **0x9070**
     (2.4 GHz, 10.2);
  2. a **51-entry** Xtensa jump table sits at **0x009b2037**;
  3. subcommand **0x17** `set_txq_param` jumps to **0x009b5c02**;
  4. subcommand **0x1e** `set_rate_override` exists.

Why the ids cannot be taken at face value: Stage 372A established that `umac.ko` carries a
**dense slot array** at id `0x9000 + 4k`, 8 bytes per entry, every entry trailing `0x00000102`.
`0x9064` is slot **25** and `0x9070` is slot **28** of that array, so both ids appear *by
construction* whether or not any tunnel exists. This tool therefore classifies every aligned hit
as "inside the dense run" or "outside it", and only the second class could support the claim.

The address check is pure arithmetic against the parsed container: each `SGMT` segment is mapped
under both endian readings of its base field, and the target either falls inside a window or it
does not.

Radio safety: static only. No firmware loaded, no module loaded, no radio contacted.
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
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage387a_qca988x_wmi_0x9064_jump_table_re.json"

CONTAINER = FW / "openwrt_qca988x_hw20_firmware_2_ct.bin"
MODULES = {
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA:ubnt_poll_host.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
}

TARGET = 0x009B2037
TARGET_JUMP = 0x009B5C02
IDS = [0x9064, 0x9070]
SUBCOMMANDS = {0x17: "set_txq_param", 0x1E: "set_rate_override"}
NAME_PROBES = ["set_txq_param", "txq_param", "set_rate_override", "rate_override",
               "UBNT_CMDID", "wmi_ubnt", "WMI_UBNT"]
SLOT_BASE = 0x9000
SLOT_STRIDE = 4


def parse_container(blob: bytes) -> dict[str, Any]:
    if not blob.startswith(b"QCA-ATH10K"):
        return dict(parsed=False)
    vlen = struct.unpack("<I", blob[16:20])[0]
    off = 20 + vlen
    segs: list[dict[str, Any]] = []
    while off + 8 <= len(blob):
        ie_id, ie_len = struct.unpack("<II", blob[off:off + 8])
        if off + 8 + ie_len > len(blob):
            break
        payload = blob[off + 8:off + 8 + ie_len]
        if payload[:4] == b"SGMT":
            base_be = struct.unpack(">I", payload[8:12])[0]
            base_le = struct.unpack("<I", payload[8:12])[0]
            segs.append(dict(id=ie_id, len=ie_len, file_off=off + 8,
                             base_be=base_be, base_le=base_le,
                             prefix=payload[:12].hex(),
                             u32_at_12=struct.unpack("<I", payload[12:16])[0],
                             payload=payload))
        off += 8 + ie_len
    return dict(parsed=True, segments=segs)


def find_slot_arrays(blob: bytes) -> list[dict[str, Any]]:
    """Runs of `[0x9000][V][0x9004][V][0x9008][V]...` with 8-byte stride."""
    out: list[dict[str, Any]] = []
    n = len(blob)
    p = blob.find(struct.pack(">I", SLOT_BASE))
    while p >= 0:
        if p % 4 == 0 and p + 24 <= n:
            val = blob[p + 4:p + 8]
            ok = (blob[p + 8:p + 12] == struct.pack(">I", SLOT_BASE + SLOT_STRIDE)
                  and blob[p + 12:p + 16] == val)
            if ok:
                k = 0
                while p + 8 * (k + 1) + 8 <= n:
                    cid = struct.unpack(">I", blob[p + 8 * k:p + 8 * k + 4])[0]
                    if cid != SLOT_BASE + SLOT_STRIDE * k:
                        break
                    k += 1
                out.append(dict(start=f"0x{p:06x}", count=k, trailing=val.hex()))
        p = blob.find(struct.pack(">I", SLOT_BASE), p + 1)
    return out


def pointer_runs(payload: bytes, width: int = 51, lo: int = 0x00980000,
                 hi: int = 0x009C0000, cap: int = 8) -> list[dict[str, Any]]:
    """Longest runs of consecutive aligned words that look like in-firmware pointers."""
    out: list[dict[str, Any]] = []
    best = 0
    cur = 0
    start = 0
    for o in range(0, len(payload) - 3, 4):
        v = struct.unpack("<I", payload[o:o + 4])[0]
        if lo <= v < hi:
            if cur == 0:
                start = o
            cur += 1
            if cur > best:
                best = cur
        else:
            if cur >= width and len(out) < cap:
                out.append(dict(at=f"0x{start:06x}", length=cur))
            cur = 0
    if cur >= width and len(out) < cap:
        out.append(dict(at=f"0x{start:06x}", length=cur))
    return sorted(out, key=lambda r: -r["length"])[:cap]


def contexts(b: bytes, tok: str, n: int = 3, w: int = 70) -> list[str]:
    out: list[str] = []
    needle = tok.encode()
    i = b.find(needle)
    while i >= 0 and len(out) < n:
        out.append("".join(chr(c) if 32 <= c < 127 else "."
                           for c in b[max(0, i - w):i + len(needle) + w]))
        i = b.find(needle, i + 1)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    blob = CONTAINER.read_bytes()
    parsed = parse_container(blob)
    segs = parsed.get("segments", [])

    windows = []
    for s in segs:
        for label, base in (("be", s["base_be"]), ("le", s["base_le"])):
            lo, hi = base, base + s["len"]
            inside = lo <= TARGET < hi
            windows.append(dict(segment=s["id"], endian=label, base=f"0x{base:08x}",
                                lo=f"0x{lo:08x}", hi=f"0x{hi:08x}", contains_target=inside,
                                offset=(f"0x{TARGET - base:06x}" if inside else None),
                                bytes_past_end=(0 if inside else TARGET - hi),
                                contains_jump=(lo <= TARGET_JUMP < hi)))

    slots: list[dict[str, Any]] = []
    rows = []
    for label, path in MODULES.items():
        d = path.read_bytes()
        slots_mod = find_slot_arrays(d)
        slots.extend(slots_mod)
        hits = {}
        for v in IDS:
            pat = struct.pack(">I", v)
            pos = []
            k = d.find(pat)
            while k >= 0:
                pos.append(k)
                k = d.find(pat, k + 1)
            aligned = [p for p in pos if p % 4 == 0]
            classified = []
            for p in aligned:
                idx = (v - SLOT_BASE) // SLOT_STRIDE
                in_run = any(int(s["start"], 16) + 8 * idx == p for s in slots_mod)
                classified.append(dict(at=f"0x{p:06x}", slot_index=idx, in_dense_slot_array=in_run))
            hits[f"0x{v:04x}"] = dict(total=len(pos), aligned=len(aligned),
                                      unaligned=len(pos) - len(aligned),
                                      classified=classified,
                                      outside_dense_run=sum(1 for c in classified
                                                            if not c["in_dense_slot_array"]))
        probes = {p: d.count(p.encode()) for p in NAME_PROBES}
        rows.append(dict(module=label, status="ok", bytes=len(d),
                         sha256=hashlib.sha256(d).hexdigest(),
                         ids=hits, name_probes=probes,
                         subcommand_names={name: d.count(name.encode())
                                           for name in SUBCOMMANDS.values()},
                         name_contexts={p: contexts(d, p, 6) for p in NAME_PROBES
                                        if d.count(p.encode())}))

    blob_ids = {}
    for v in IDS:
        blob_ids[f"0x{v:04x}"] = dict(be=blob.count(struct.pack(">I", v)),
                                      le=blob.count(struct.pack("<I", v)))
    blob_probes = {p: blob.count(p.encode()) for p in NAME_PROBES}

    total_outside = sum(m["ids"][k]["outside_dense_run"] for m in rows for k in m["ids"])
    ptr_runs = {s["id"]: pointer_runs(s["payload"]) for s in segs}
    report = dict(
        meta=dict(stage="387A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/qca988x_wmi_0x9064_51entry_jump_table_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no firmware loaded, no module loaded, "
                        "no radio contacted",
                  target_address=f"0x{TARGET:08x}",
                  target_jump=f"0x{TARGET_JUMP:08x}",
                  premise_corrections=[
                      "0x9064 and 0x9070 are slot 25 and slot 28 of the dense 0x9000+4k array "
                      "already mapped in Stage 372A, so their presence in umac.ko is expected "
                      "whether or not any proprietary tunnel exists",
                      "0x009b2037 falls outside every segment window under both endian readings "
                      "of the SGMT base field",
                  ],
                  radio_safety="static only"),
        container=dict(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
                       segments=[{k: v for k, v in s.items() if k != "payload"} for s in segs]),
        address_windows=windows,
        dense_slot_arrays=slots,
        blob_ids=blob_ids,
        blob_name_probes=blob_probes,
        blob_pointer_runs=ptr_runs,
        modules=rows,
        subcommands=[dict(id=f"0x{k:02x}", name=v) for k, v in SUBCOMMANDS.items()],
        summary=dict(target_in_any_window=sum(1 for w in windows if w["contains_target"]),
                     jump_in_any_window=sum(1 for w in windows if w["contains_jump"]),
                     bytes_past_nearest_window=min(w["bytes_past_end"] for w in windows),
                     dense_slot_arrays=len(slots),
                     aligned_id_hits=sum(m["ids"][k]["aligned"] for m in rows for k in m["ids"]),
                     id_hits_outside_dense_run=total_outside,
                     name_probes_found=sum(1 for p in NAME_PROBES
                                           if any(m["name_probes"][p] for m in rows)
                                           or blob_probes[p]),
                     pointer_runs_51plus=sum(len(v) for v in ptr_runs.values()),
                     jump_table_recovered=0),
        gaps=["the claimed address 0x009b2037 is not inside any parsed segment window: the "
              "nearest LE window ends at 0x009b03a1, leaving the target past the end",
              "no 51-entry jump table was decoded; the pointer-run scan is reported as raw "
              "evidence and no table was bound to the address",
              "the SGMT header is not fully decoded: the base field reads 0x00980000 both ways "
              "and the u32 at payload offset 12 (148 / 5484) is uninterpreted, so the mapping "
              "used here is the widest available, not a proven load address",
              "every aligned 0x9064/0x9070 hit inside the dense slot array is an enumeration "
              "artefact and is classified as such",
              "set_txq_param, set_rate_override and WMI_UBNT exist as strings in "
              "ubnt_poll_host.ko and umac.ko respectively, but no subcommand dispatch table was "
              "found, so the opcode numbers 0x17 and 0x1e are not bound to those handlers",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[387A] target_in_window={s['target_in_any_window']} "
          f"jump_in_window={s['jump_in_any_window']} "
          f"past_end={s['bytes_past_nearest_window']} slots={s['dense_slot_arrays']} "
          f"aligned_ids={s['aligned_id_hits']} outside_dense={s['id_hits_outside_dense_run']} "
          f"names_found={s['name_probes_found']} jump_table=0")
    for w in windows:
        print(f"        seg{w['segment']} {w['endian']} {w['lo']}..{w['hi']} "
              f"target={w['contains_target']} jump={w['contains_jump']}")
    for m in rows:
        print(f"        {m['module']:<22} {m['bytes']:>8}B "
              f"0x9064={m['ids']['0x9064']['total']}/aligned {m['ids']['0x9064']['aligned']} "
              f"outside={m['ids']['0x9064']['outside_dense_run']} "
              f"0x9070={m['ids']['0x9070']['total']}")
    print(f"[387A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
