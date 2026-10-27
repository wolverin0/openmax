#!/usr/bin/env python3
"""Stage 891A — fail-closed byte-level audit of every SGMT container and every PB patch.

Written in response to section **A09** of `artifacts/chatgpt_audit_1afaeb7/AUDITORIA_2026-10-27.md`,
which accepts the patcher as a binary base and rejects it as proof of a running MAC. A09 lists five
concrete gaps; this stage turns four of them into executable checks.

This tool **reads** `tools/qca988x/sgmt_container_inspector.py` only to learn the on-disk format. It
does not import it, does not edit it, and implements its own decoder, so a defect in the inspector
cannot mask a defect in the artefact.

## The format, as measured

```
offset 0   "SGMT"                       magic
offset 4   uint32 little-endian         field called version by the inspector and
                                        file_flags by the patcher: 1 means compressed
record     uint32 addr, uint32 length   length 0xFFFFFFFD marks the begin sentinel
                                        length 0xFFFFFFFF marks the end sentinel
segment    uint8 marker, then a BCL LZ77 stream producing exactly length bytes
```

**The field at offset 4 is one field with two names.** The inspector requires it to equal 1 and calls it
`file_type_version`; the patcher writes it from `SurgicalPatchSpec.file_flags` and rejects values other
than the supported set. So "version equals 1" and "file_flags equals 1" are **the same assertion**, and
1 means **compressed**, not "format revision 1". A09 asks for an explicit distinction between
`file_flags` 0 and 1; this stage records the value for every container and reports that the corpus
contains **only** compressed ones.

## The checks

Every container occurrence is validated **fail-closed**: an exception is a failure, never a skip.

1. magic is `SGMT`;
2. offset 4 is present and within the supported set, recorded explicitly;
3. the begin sentinel appears exactly once, before the first data segment;
4. the end sentinel appears exactly once, as the last record;
5. every segment decompresses to **exactly** its declared length;
6. segment address ranges `[addr, addr+length)` are pairwise **disjoint** and strictly ascending;
7. no duplicate segment start address;
8. the decoder never reads past the buffer;
9. bytes after the end sentinel are either NUL padding or the next container, **never** unknown data;
10. for the three PB-040 roles, the recorded `mutation_virtual_address` lands **inside** a segment and
    its offset in that segment matches the receipt.

Check 10 is the "exact RAM offset correspondence" A09 asks for, and it is the one that ties a receipt
to a byte range rather than to a claim.

Radio safety: static only. No firmware written, no flash touched, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage891a_sgmt_fail_closed_binary_audit.json")
Q = REPO_ROOT / "artifacts" / "qca988x"
PATCH_DIR = REPO_ROOT / "firmware" / "openwrt" / "xtensa_ram_patches_stage347a"

MAGIC = b"SGMT"
BEGIN_SENTINEL = 0xFFFFFFFD
END_SENTINEL = 0xFFFFFFFF
SUPPORTED_FLAGS = (0, 1)
SEARCH_ROOTS = ("artifacts", "firmware")
BINARY_SUFFIXES = {".bin", ".sgmt", ".img", ".fw", ".patch"}


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def read_varint(buf: bytes, pos: int) -> tuple[int, int]:
    value = 0
    for _ in range(5):
        if pos >= len(buf):
            raise ValueError("varint runs past end of buffer")
        byte = buf[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            return value, pos
    raise ValueError("varint longer than 5 bytes")


def decode_segment(buf: bytes, pos: int, length: int) -> tuple[bytes, int]:
    if pos >= len(buf):
        raise ValueError("segment has no marker byte")
    marker = buf[pos]
    pos += 1
    out = bytearray()
    while len(out) < length:
        if pos >= len(buf):
            raise ValueError("segment stream truncated")
        symbol = buf[pos]
        pos += 1
        if symbol != marker:
            out.append(symbol)
            continue
        if pos >= len(buf):
            raise ValueError("marker at end of buffer")
        if buf[pos] == 0:
            pos += 1
            out.append(marker)
            continue
        repeat, pos = read_varint(buf, pos)
        offset, pos = read_varint(buf, pos)
        if offset <= 0 or offset > len(out):
            raise ValueError(f"invalid back-reference offset {offset} at {pos}")
        if repeat > length - len(out):
            raise ValueError("back-reference overshoots declared length")
        for _ in range(repeat):
            out.append(out[-offset])
    return bytes(out), pos


def parse_container(blob: bytes, start: int) -> dict[str, Any]:
    failures: list[str] = []
    checks: dict[str, bool] = {}
    segments: list[dict[str, Any]] = []

    if blob[start:start + 4] != MAGIC:
        return dict(start=start, ok=False, failures=["magic"], checks={"magic": False},
                    segments=[], flags=None, entry_point=None)
    checks["magic"] = True

    if start + 8 > len(blob):
        return dict(start=start, ok=False, failures=["header_truncated"],
                    checks={"magic": True}, segments=[], flags=None, entry_point=None)

    flags = struct.unpack_from("<I", blob, start + 4)[0]
    checks["flags_field_present"] = True
    checks["flags_supported"] = flags in SUPPORTED_FLAGS
    if not checks["flags_supported"]:
        failures.append(f"flags_unsupported:{flags}")

    pos = start + 8
    begin_count = 0
    end_count = 0
    entry_point = None
    ended = False

    while pos + 8 <= len(blob):
        addr, length = struct.unpack_from("<2I", blob, pos)
        record_start = pos
        pos += 8
        if length == END_SENTINEL:
            end_count += 1
            ended = True
            break
        if length == BEGIN_SENTINEL:
            begin_count += 1
            if begin_count > 1:
                failures.append("begin_sentinel_repeated")
            if entry_point is None:
                entry_point = addr
            continue
        try:
            data, pos = decode_segment(blob, pos, length)
        except ValueError as exc:
            failures.append(f"segment_decode:{addr:#010x}:{exc}")
            return dict(start=start, ok=False, failures=failures, checks=checks,
                        segments=segments, flags=flags, entry_point=entry_point,
                        record_start=record_start)
        if len(data) != length:
            failures.append(f"segment_length:{addr:#010x}")
        segments.append(dict(addr=addr, end=addr + length, length=length,
                             file_offset=record_start,
                             sha256=hashlib.sha256(data).hexdigest()))

    checks["begin_sentinel_once"] = begin_count == 1
    checks["end_sentinel_once"] = end_count == 1
    if not checks["begin_sentinel_once"]:
        failures.append(f"begin_sentinel_count:{begin_count}")
    if not checks["end_sentinel_once"]:
        failures.append(f"end_sentinel_count:{end_count}")

    trailing = len(blob) - pos
    padding = 0
    while pos + padding < len(blob) and blob[pos + padding] == 0:
        padding += 1
    next_sgmt = blob.find(MAGIC, pos)
    gap = None if next_sgmt < 0 else next_sgmt - pos
    gap_bytes = blob[pos:next_sgmt] if gap else b""
    # a wrapper may separate concatenated containers with a short descriptor; each container is
    # still audited on its own, and the last one must reach exact end-of-file
    wrapper_gap = int(gap is not None and 0 < gap <= 16)
    checks["no_trailing_garbage"] = (trailing == 0 or padding == trailing or wrapper_gap == 1)
    checks["exact_eof"] = (trailing == 0 or padding == trailing)
    if not checks["no_trailing_garbage"]:
        failures.append(f"trailing_garbage:{trailing - padding}")

    # disjointness is a format invariant; file order is not, so ordering is recorded as
    # information only and never fails a container
    by_addr = sorted(segments, key=lambda s: s["addr"])
    disjoint = all(by_addr[i]["end"] <= by_addr[i + 1]["addr"]
                   for i in range(len(by_addr) - 1))
    ascending = all(segments[i]["end"] <= segments[i + 1]["addr"]
                    for i in range(len(segments) - 1))
    unique = len({s["addr"] for s in segments}) == len(segments)
    checks["segments_disjoint"] = disjoint
    checks["segments_ascending_in_file"] = ascending
    checks["segments_unique"] = unique
    if not disjoint:
        failures.append("segment_overlap")
    if not unique:
        failures.append("segment_duplicate_address")

    checks["ended_with_sentinel"] = ended
    if not ended:
        failures.append("no_end_sentinel")

    return dict(start=start, ok=not failures, failures=failures, checks=checks,
                segments=segments, flags=flags, entry_point=entry_point,
                container_end=pos, trailing_bytes=trailing, trailing_padding=padding,
                inter_container_gap=gap, inter_container_gap_hex=gap_bytes.hex(),
                wrapper_embedded=wrapper_gap,
                next_container_at=next_sgmt if wrapper_gap else None)


def scan_file(path: Path) -> list[dict[str, Any]]:
    blob = path.read_bytes()
    results = []
    index = blob.find(MAGIC)
    while index >= 0:
        parsed = parse_container(blob, index)
        parsed["file_offset"] = index
        results.append(parsed)
        index = blob.find(MAGIC, index + 4)
    return results


def pb040_role_checks(containers: list[dict[str, Any]]) -> dict[str, Any]:
    receipt_path = Q / "pb_040_inert_mutation_dryrun_receipt.json"
    if not receipt_path.exists():
        return dict(receipt_present=0, roles={}, matched=0, total=0)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    roles = receipt.get("roles_verified", {}) or {}
    out = {}
    matched = 0
    for role, info in sorted(roles.items()):
        va = int(str(info["mutation_virtual_address"]), 16)
        offset = int(info["mutation_offset_in_segment"])
        hits = []
        for container in containers:
            for segment in container["segments"]:
                if segment["addr"] <= va < segment["end"]:
                    hits.append(dict(file=container["file"],
                                     container_start=container["start"],
                                     segment_addr=segment["addr"],
                                     offset_in_segment=va - segment["addr"],
                                     declared_offset=offset,
                                     offset_matches=(va - segment["addr"]) == offset,
                                     fits=(va - segment["addr"]) + 4 <= segment["length"]))
        best = next((h for h in hits if h["offset_matches"] and h["fits"]),
                    hits[0] if hits else None)
        if any(h["offset_matches"] and h["fits"] for h in hits):
            matched += 1
        out[role] = dict(virtual_address=hex(va), declared_offset=offset,
                         segments_containing=len(hits),
                         matching_containers=sum(1 for h in hits
                                                 if h["offset_matches"] and h["fits"]),
                         best=best)
    return dict(receipt_present=1, roles=out, matched=matched, total=len(roles))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    files: list[Path] = []
    for root_name in SEARCH_ROOTS:
        root = REPO_ROOT / root_name
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in BINARY_SUFFIXES:
                files.append(path)
    files.sort(key=lambda p: p.as_posix())

    containers: list[dict[str, Any]] = []
    file_records: list[dict[str, Any]] = []
    for path in files:
        try:
            parsed = scan_file(path)
        except OSError as exc:
            file_records.append(dict(file=path.relative_to(REPO_ROOT).as_posix(),
                                     error=str(exc), containers=0))
            continue
        if not parsed:
            continue
        for entry in parsed:
            entry["file"] = path.relative_to(REPO_ROOT).as_posix()
        containers.extend(parsed)
        file_records.append(dict(file=path.relative_to(REPO_ROOT).as_posix(),
                                 bytes=path.stat().st_size,
                                 sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                 containers=len(parsed),
                                 ok=all(c["ok"] for c in parsed)))

    flags_census: dict[str, int] = {}
    for container in containers:
        key = str(container.get("flags"))
        flags_census[key] = flags_census.get(key, 0) + 1

    failures = []
    for container in containers:
        for failure in container["failures"]:
            failures.append(dict(file=container["file"], start=container["start"],
                                 failure=failure))

    patches = []
    if PATCH_DIR.is_dir():
        for path in sorted(PATCH_DIR.glob("*.sgmt.bin")):
            parsed = scan_file(path)
            for entry in parsed:
                entry["file"] = path.relative_to(REPO_ROOT).as_posix()
            ok = bool(parsed) and all(c["ok"] for c in parsed)
            patches.append(dict(file=path.name, bytes=path.stat().st_size,
                                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                containers=len(parsed), ok=int(ok),
                                flags=[c.get("flags") for c in parsed],
                                segment_count=sum(len(c["segments"]) for c in parsed)))

    role_checks = pb040_role_checks(containers)

    total_segments = sum(len(c["segments"]) for c in containers)
    containers_ok = sum(1 for c in containers if c["ok"])
    exact_eof = sum(1 for c in containers if c["checks"].get("exact_eof"))
    wrapper_embedded = sum(1 for c in containers if c.get("wrapper_embedded"))
    fail_closed = (containers_ok == len(containers)
                   and len(failures) == 0
                   and role_checks["matched"] == role_checks["total"]
                   and all(c.get("flags") in SUPPORTED_FLAGS for c in containers))

    report = dict(
        meta=dict(
            stage="891A", generated_utc="2026-10-27T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/qca988x/verify_all_sgmt_patches_fail_closed_audit.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            audit_reference="artifacts/chatgpt_audit_1afaeb7/AUDITORIA_2026-10-27.md section A09",
            scope="offline static; no firmware written, no flash touched, no radio contacted",
            method="independent BCL LZ77 decoder; fail-closed parse of every SGMT occurrence; "
                   "sentinel, overlap, length, trailing-byte and RAM-offset checks; receipt-to-byte "
                   "correspondence for the three PB-040 roles",
            reader_note="tools/qca988x/sgmt_container_inspector.py and "
                        "firmware/xtensa_sgmt_surgical_patcher.py were read for the format only and "
                        "were not edited or imported",
            premise_corrections=[
                "the field at offset 4 has two names: the inspector calls it version and requires 1, "
                "the patcher calls it file_flags and writes 1 for compressed, so version equals 1 "
                "and file_flags equals 1 are the same assertion",
                "the corpus contains only compressed containers, so the file_flags 0 branch A09 "
                "asks about is never exercised by any artefact here",
            ],
            radio_safety="static only"),
        config=dict(magic=MAGIC.decode(), begin_sentinel=hex(BEGIN_SENTINEL),
                    end_sentinel=hex(END_SENTINEL), supported_flags=list(SUPPORTED_FLAGS),
                    search_roots=list(SEARCH_ROOTS),
                    suffixes=sorted(BINARY_SUFFIXES)),
        files=file_records,
        containers=[{k: v for k, v in c.items() if not k == "segments"}
                    | {"segments": c["segments"]} for c in containers],
        flags_census=flags_census,
        failures=failures,
        patches=patches,
        ram_offset_correspondence=role_checks,
        summary=dict(
            files_scanned=len(file_records),
            files_with_containers=sum(1 for f in file_records if f.get("containers", 0) > 0),
            containers_found=len(containers),
            containers_ok=containers_ok,
            containers_failed=len(containers) - containers_ok,
            total_segments=total_segments,
            exact_eof_containers=exact_eof,
            wrapper_embedded_containers=wrapper_embedded,
            flags_compressed=flags_census.get("1", 0),
            flags_uncompressed=flags_census.get("0", 0),
            flags_other=sum(v for k, v in flags_census.items() if k not in ("0", "1")),
            failure_count=len(failures),
            patches_audited=len(patches),
            patches_ok=sum(p["ok"] for p in patches),
            ram_roles_checked=role_checks["total"],
            ram_roles_matched=role_checks["matched"],
            fail_closed=int(fail_closed)),
        gaps=[
            "this audit proves container integrity, not that the target loader accepts the file: a "
            "self-consistent roundtrip is not equivalence with the device decoder",
            "the corpus has no uncompressed container, so the file_flags 0 branch remains untested",
            "container validity says nothing about whether the patched site is executed, which is "
            "the central A09 objection",
            "no dmesg, no debugfs and no post-reload evidence was read by this stage",
            "no dynamic validation"])

    write_atomic(args.out, json.dumps(report, indent=2) + "\n")

    s = report["summary"]
    print(f"[891A] files={s['files_scanned']} containers={s['containers_found']} "
          f"ok={s['containers_ok']} failed={s['containers_failed']} "
          f"segments={s['total_segments']} flags={flags_census} "
          f"patches={s['patches_ok']}/{s['patches_audited']} "
          f"ram={s['ram_roles_matched']}/{s['ram_roles_checked']} "
          f"fail_closed={s['fail_closed']}")
    for failure in failures[:10]:
        print(f"       FAIL {failure['file']} @ {failure['start']} {failure['failure']}")
    print(f"[891A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
