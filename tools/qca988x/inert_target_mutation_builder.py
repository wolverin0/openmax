#!/usr/bin/env python3
"""PB-040 Offline Preparation: Reversible Inert Target-Firmware SGMT Mutation Builder & Diff Verifier.

Implements the offline preparation and verification harness for Gate PB-040:
1. Loads an embedded QCA988x `SGMT` container (`athwlan_AR9888v2_ptmp_ap_bin`,
   `athwlan_AR9888v2_ptmp_sta_bin`, or `athwlan_AR9888v2_ptp_bin`) in memory.
2. Decompresses all 4 BCL-LZ77 segments via `sgmt_container_inspector.py`.
3. Applies a strictly bounded, 4-byte length-preserving inert debug string mutation in
   DRAM segment `0x0040b000` (`b"UBNT_POLL_MEM_ALLOC"` -> `b"OMAX_POLL_MEM_ALLOC"`),
   verifying that no `%` format specifiers, null terminators, segment lengths, or
   executable IRAM instructions (`0x00980000`, `0x00983c00`) are modified.
4. Re-packs the segments into a valid `SGMT` container using BCL LZ77 compression and
   verifies via independent decompression that:
   - All 3 non-target segments have 0 changed bytes (identical SHA-256).
   - Target DRAM segment `0x0040b000` differs at exactly the 4 mutated bytes (`diff_bytes == 4`).
   - Applying the inverse mutation (`b"OMAX_POLL_MEM_ALLOC"` -> `b"UBNT_POLL_MEM_ALLOC"`)
     restores 100% bit-identical uncompressed SHA-256 across all segments.
5. Enforces `automatic_execution_allowed = False` and `ram_only_target_load = True`.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Dict, List, Tuple

from analysis.re_ubnt_poll_and_ltu_4096qam import Elf32Image
from tools.qca988x.sgmt_container_inspector import (
    BMI_SGMT_BEGIN_ADDR,
    BMI_SGMT_END,
    SGMT_MAGIC,
    WA_UMAC_PATH,
    _read_bcl_varint,
    _write_bcl_varint,
    parse_sgmt_container,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_PATH = REPO_ROOT / "artifacts/qca988x/pb_040_inert_mutation_dryrun_receipt.json"

DEFAULT_SOURCE_ANCHOR = b"UBNT_POLL_MEM_ALLOC"
DEFAULT_MUTATED_ANCHOR = b"OMAX_POLL_MEM_ALLOC"


def decompress_sgmt_ordered_segments(blob: bytes) -> Tuple[List[Tuple[int, bytes]], int]:
    """Decompresses an SGMT container into an ordered list of (load_addr, raw_bytes) and entry_point."""
    if len(blob) < 16 or blob[:4] != SGMT_MAGIC:
        raise ValueError("Invalid SGMT magic header.")
    pos = 8
    segments: List[Tuple[int, bytes]] = []
    entry_point = 0x00983C00
    while pos + 8 <= len(blob):
        addr, length = struct.unpack_from("<2I", blob, pos)
        pos += 8
        if length == BMI_SGMT_END:
            break
        if length == BMI_SGMT_BEGIN_ADDR:
            entry_point = addr
            continue
        marker = blob[pos]
        pos += 1
        out = bytearray()
        while len(out) < length:
            sym = blob[pos]
            pos += 1
            if sym != marker:
                out.append(sym)
            elif blob[pos] == 0:
                pos += 1
                out.append(marker)
            else:
                rep_len, pos = _read_bcl_varint(blob, pos)
                offset, pos = _read_bcl_varint(blob, pos)
                for _ in range(rep_len):
                    out.append(out[-offset])
        segments.append((addr, bytes(out)))
    return segments, entry_point


def compress_bcl_lz77_segment(raw: bytes) -> bytes:
    """Compresses a segment using BCL LZ77 (1-byte least-frequent marker + 7-bit varint length/offset)."""
    counts = [0] * 256
    for b in raw:
        counts[b] += 1
    marker = min(range(256), key=lambda x: counts[x])

    out = bytearray([marker])
    n = len(raw)
    pos = 0
    # Fast hash-indexed 4-byte prefix match for compact BCL LZ77 output
    last_seen: Dict[bytes, int] = {}

    while pos < n:
        best_len = 0
        best_off = 0
        if pos + 4 <= n:
            key = raw[pos : pos + 4]
            prev = last_seen.get(key)
            last_seen[key] = pos
            if prev is not None and (pos - prev) <= 4095:
                offset = pos - prev
                max_len = min(255, n - pos)
                match_len = 4
                while match_len < max_len and raw[prev + match_len] == raw[pos + match_len]:
                    match_len += 1
                best_len = match_len
                best_off = offset

        if best_len >= 4:
            for step in range(1, best_len):
                if pos + step + 4 <= n:
                    last_seen[raw[pos + step : pos + step + 4]] = pos + step
            out.append(marker)
            out.extend(_write_bcl_varint(best_len))
            out.extend(_write_bcl_varint(best_off))
            pos += best_len
        else:
            b = raw[pos]
            if b == marker:
                out.extend((marker, 0))
            else:
                out.append(b)
            pos += 1

    return bytes(out)


def pack_sgmt_bcl_lz77(
    segments: List[Tuple[int, bytes]],
    entry_point: int = 0x00983C00,
) -> bytes:
    """Packs ordered (addr, raw_bytes) segments into a valid BCL-LZ77 SGMT container."""
    out = bytearray(SGMT_MAGIC)
    out.extend(struct.pack("<I", 1))
    for addr, raw in segments:
        comp = compress_bcl_lz77_segment(raw)
        out.extend(struct.pack("<2I", addr, len(raw)))
        out.extend(comp)
    out.extend(struct.pack("<2I", entry_point, BMI_SGMT_BEGIN_ADDR))
    out.extend(struct.pack("<2I", 0, BMI_SGMT_END))
    return bytes(out)


def validate_inert_string_mutation(source_anchor: bytes, mutated_anchor: bytes) -> None:
    """Ensures the mutation is strictly length-preserving, ASCII printable, and preserves % formatters."""
    if len(source_anchor) != len(mutated_anchor):
        raise ValueError(
            f"Inert mutation must preserve exact byte length: {len(source_anchor)} != {len(mutated_anchor)}"
        )
    if source_anchor == mutated_anchor:
        raise ValueError("Mutated anchor must differ from source anchor.")
    if b"\x00" in source_anchor or b"\x00" in mutated_anchor:
        raise ValueError("Inert mutation anchors must not contain null terminators.")
    if b"%" in source_anchor or b"%" in mutated_anchor:
        raise ValueError("Inert mutation anchors must not alter printf '%' format specifiers.")


def apply_and_verify_inert_mutation(
    original_sgmt_blob: bytes,
    source_anchor: bytes = DEFAULT_SOURCE_ANCHOR,
    mutated_anchor: bytes = DEFAULT_MUTATED_ANCHOR,
    target_dram_segment_addr: int = 0x0040B000,
) -> Dict[str, Any]:
    """Decompresses an SGMT image, applies a 1-site inert DRAM string mutation, repacks, and verifies diff."""
    validate_inert_string_mutation(source_anchor, mutated_anchor)

    orig_segments, orig_entry = decompress_sgmt_ordered_segments(original_sgmt_blob)
    mutated_segments: List[Tuple[int, bytes]] = []
    mutation_va: int | None = None
    mutation_offset_in_seg: int | None = None

    for addr, raw in orig_segments:
        if addr == target_dram_segment_addr:
            idx = raw.find(source_anchor)
            if idx == -1:
                raise ValueError(
                    f"Source anchor {source_anchor!r} not found in DRAM segment 0x{addr:08x}."
                )
            mut_raw = bytearray(raw)
            mut_raw[idx : idx + len(source_anchor)] = mutated_anchor
            mutated_segments.append((addr, bytes(mut_raw)))
            mutation_offset_in_seg = idx
            mutation_va = addr + idx
        else:
            mutated_segments.append((addr, raw))

    if mutation_va is None or mutation_offset_in_seg is None:
        raise ValueError(f"Target DRAM segment 0x{target_dram_segment_addr:08x} not found in SGMT.")

    # Pack mutated container using BCL LZ77 and re-parse from scratch
    mutated_container = pack_sgmt_bcl_lz77(mutated_segments, entry_point=orig_entry)
    parsed_mutated = parse_sgmt_container(mutated_container)
    re_decompressed, re_entry = decompress_sgmt_ordered_segments(mutated_container)

    # Compute exact per-segment and per-byte diffs
    segment_diffs: List[Dict[str, Any]] = []
    total_changed_bytes = 0
    changed_offsets: List[int] = []

    for (addr_o, raw_o), (addr_m, raw_m) in zip(orig_segments, re_decompressed):
        if addr_o != addr_m or len(raw_o) != len(raw_m):
            raise ValueError("Segment address or length changed during mutation!")
        diff_positions = [i for i, (bo, bm) in enumerate(zip(raw_o, raw_m)) if bo != bm]
        total_changed_bytes += len(diff_positions)
        if addr_o == target_dram_segment_addr:
            changed_offsets = diff_positions
        segment_diffs.append(
            {
                "segment_address": f"0x{addr_o:08x}",
                "uncompressed_size_bytes": len(raw_o),
                "changed_bytes_count": len(diff_positions),
                "original_sha256": hashlib.sha256(raw_o).hexdigest(),
                "mutated_sha256": hashlib.sha256(raw_m).hexdigest(),
                "identical": len(diff_positions) == 0,
            }
        )

    # Also verify exact reversibility (mutated -> restored)
    restored_segments: List[Tuple[int, bytes]] = []
    for addr, raw_m in re_decompressed:
        if addr == target_dram_segment_addr:
            idx = raw_m.find(mutated_anchor)
            rest_raw = bytearray(raw_m)
            rest_raw[idx : idx + len(mutated_anchor)] = source_anchor
            restored_segments.append((addr, bytes(rest_raw)))
        else:
            restored_segments.append((addr, raw_m))

    restored_matches_original = all(
        hashlib.sha256(ro).hexdigest() == hashlib.sha256(rr).hexdigest()
        for (_, ro), (_, rr) in zip(orig_segments, restored_segments)
    )

    expected_diff_bytes = sum(1 for a, b in zip(source_anchor, mutated_anchor) if a != b)

    return {
        "target_dram_segment": f"0x{target_dram_segment_addr:08x}",
        "mutation_offset_in_segment": mutation_offset_in_seg,
        "mutation_virtual_address": f"0x{mutation_va:08x}",
        "source_anchor_ascii": source_anchor.decode("ascii"),
        "mutated_anchor_ascii": mutated_anchor.decode("ascii"),
        "expected_diff_bytes": expected_diff_bytes,
        "observed_total_diff_bytes": total_changed_bytes,
        "changed_byte_offsets_in_dram": changed_offsets,
        "iram_code_segments_untouched": all(
            d["identical"] for d in segment_diffs if d["segment_address"] != f"0x{target_dram_segment_addr:08x}"
        ),
        "repacked_container_valid_sgmt": parsed_mutated["exact_eof_match"],
        "repacked_container_size_bytes": len(mutated_container),
        "repacked_container_sha256": hashlib.sha256(mutated_container).hexdigest(),
        "entry_point_preserved": (re_entry == orig_entry == 0x00983C00),
        "reversible_restoration_bit_exact": restored_matches_original,
        "segment_diffs": segment_diffs,
    }


def build_pb_040_dryrun_receipt() -> Dict[str, Any]:
    """Runs the offline PB-040 inert mutation dry-run across ptmp_ap, ptmp_sta, and ptp images."""
    elf = Elf32Image(WA_UMAC_PATH)
    data = elf.section_bytes(".data")
    sym_map = {s["name"]: s for s in elf.symbols}

    role_results: Dict[str, Any] = {}
    for sym_name in (
        "athwlan_AR9888v2_ptmp_ap_bin",
        "athwlan_AR9888v2_ptmp_sta_bin",
        "athwlan_AR9888v2_ptp_bin",
    ):
        sym = sym_map[sym_name]
        blob = data[sym["value"] : sym["value"] + sym["size"]]
        role_results[sym_name] = apply_and_verify_inert_mutation(blob)

    return {
        "gate_id": "PB-040",
        "phase": "OFFLINE_PREPARATION_DRYRUN_ONLY",
        "automatic_execution_allowed": False,
        "ram_only_target_load_required": True,
        "spi_flash_write_allowed": False,
        "operator_gate_required_for_bench": True,
        "roles_verified": role_results,
    }


def main() -> None:
    receipt = build_pb_040_dryrun_receipt()
    DEFAULT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT_PATH.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"Saved PB-040 offline dry-run receipt to {DEFAULT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
