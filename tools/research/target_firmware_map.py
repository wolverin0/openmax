"""Offline target-image maps and literal-reference candidates; no firmware export.

String/word matches are search anchors, not functions, instructions or runtime
proof. Load-order overlays are applied before references are searched.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from pathlib import Path

from elftools.elf.elffile import ELFFile

from tools.research.inspect_radio_elf import RADIO_NAME, bounded_slice
from tools.research.sgmt import MAX_OUTPUT, MAX_RECORDS, decode_sgmt_memory

INTEREST = re.compile(rb"ubnt|poll|txq|netconf|wmi|rate_override", re.IGNORECASE)
STRINGS = re.compile(rb"[\x20-\x7e]{4,}")
MAX_ANCHORS = 512
MAX_MATCHES = 256


def loaded_regions(segments: list[tuple[int, bytes]]) -> list[tuple[int, bytes]]:
    """Apply ordered writes, with bounded storage, then merge adjacent intervals."""
    if len(segments) > MAX_RECORDS:
        raise ValueError("too many segments")
    total = 0
    regions = []
    for address, payload in segments:
        if type(address) is not int or not isinstance(payload, bytes) or not payload:
            raise ValueError("invalid segment")
        end = address + len(payload)
        total += len(payload)
        if address < 0 or end > 0x100000000 or total > MAX_OUTPUT:
            raise ValueError("segment bounds exceeded")
        remaining = []
        for old_address, old in regions:
            old_end = old_address + len(old)
            if old_end <= address or old_address >= end:
                remaining.append((old_address, old))
                continue
            if old_address < address:
                remaining.append((old_address, old[:address - old_address]))
            if old_end > end:
                remaining.append((end, old[end - old_address:]))
        regions = sorted(remaining + [(address, payload)])
    merged = []
    for address, payload in regions:
        if merged and merged[-1][0] + len(merged[-1][1]) == address:
            start, old = merged.pop()
            merged.append((start, old + payload))
        else:
            merged.append((address, payload))
    return merged


def map_target(segments: list[tuple[int, bytes]]) -> dict:
    regions = loaded_regions(segments)
    anchors = []
    total_anchors = 0
    for address, payload in regions:
        for match in STRINGS.finditer(payload):
            # Match maximal runs first: requiring NUL in the regex causes
            # quadratic backtracking on long unterminated printable input.
            if match.end() == len(payload) or payload[match.end()] != 0 or not INTEREST.search(match[0]):
                continue
            total_anchors += 1
            if len(anchors) < MAX_ANCHORS:
                text = match[0]
                anchors.append({"address": address + match.start(),
                                "text": text[:200].decode("ascii"),
                                "text_length": len(text), "text_truncated": len(text) > 200})
    references = {}
    for anchor in anchors:
        references.setdefault(anchor["address"], {"little": [], "big": [],
                                                  "little_count": 0, "big_count": 0})
    command = {"value": 0x9064, "little": [], "big": [],
               "little_count": 0, "big_count": 0}
    for address, payload in regions:
        for offset in range((-address) % 4, len(payload) - 3, 4):
            word = payload[offset:offset + 4]
            for endian in ("little", "big"):
                value = int.from_bytes(word, endian)
                target = command if value == 0x9064 else references.get(value)
                if target is not None:
                    target[endian + "_count"] += 1
                    if len(target[endian]) < MAX_MATCHES:
                        target[endian].append(address + offset)
    for anchor in anchors:
        anchor["aligned_word_matches"] = references[anchor["address"]]
    return {
        "schema_version": 1,
        "loaded_regions": [{"address": a, "size": len(p),
                            "sha256": hashlib.sha256(p).hexdigest()} for a, p in regions],
        "string_anchor_count": total_anchors, "anchors_truncated": total_anchors > MAX_ANCHORS,
        "string_anchors": anchors, "command_literal_candidate": command,
        "limits": "Aligned 32-bit exact-value matches only; not proven pointers, code, handlers or runtime behavior. No address aliases or split immediates inferred.",
    }


def preceding_address_runs(regions: list[tuple[int, bytes]], literal_addresses: list[int],
                           entrypoints: list[int]) -> list[dict]:
    """Search anchors only: consecutive words pointing into entry-containing regions."""
    destinations = [(a, a + len(p)) for a, p in regions
                    if any(a <= entry < a + len(p) for entry in entrypoints)]
    runs = []
    for literal in literal_addresses:
        containing = next(((a, p) for a, p in regions if a <= literal < a + len(p)), None)
        if containing is None or literal % 4:
            continue
        address, payload = containing
        end = literal - address
        start = end
        while start >= 4 and end - start < 4 * 128:
            value = int.from_bytes(payload[start - 4:start], "little")
            if not any(low <= value < high for low, high in destinations):
                break
            start -= 4
        if start == end:
            continue
        runs.append({"literal_address": literal, "start": address + start,
                     "word_count": (end - start) // 4,
                     "left_boundary_unproven": start < 4 or end - start == 4 * 128,
                     "entries": [{"index": (offset - start) // 4,
                                  "word_address": address + offset,
                                  "value": int.from_bytes(payload[offset:offset + 4], "little")}
                                 for offset in range(start, end, 4)],
                     "limits": "Candidate address run, not a proven dispatch table or subtype-to-handler mapping; entry-containing region is not entirely proven code."})
    return runs


def map_container(blob: bytes) -> dict:
    metadata, segments = decode_sgmt_memory(blob)
    if any(r["kind"] == "EXEC" for r in metadata["records"]):
        raise ValueError("EXEC can change loaded memory; static overlay mapping unsupported")
    entries = [r["destination"] for r in metadata["records"] if r["kind"] == "BEGINADDR"]
    mapped = map_target(segments)
    mapped["preceding_address_runs"] = preceding_address_runs(
        loaded_regions(segments), mapped["command_literal_candidate"]["little"], entries)
    return {"container_sha256": metadata["container_sha256"],
            "begin_addresses": entries, "map": mapped}


def analyze_module(path: Path) -> dict:
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("module exceeds 64 MiB limit")
    raw = path.read_bytes()
    elf = ELFFile(io.BytesIO(raw))
    if elf.header["e_type"] != "ET_REL":
        raise ValueError("expected ET_REL")
    symbols = elf.get_section_by_name(".symtab")
    if symbols is None:
        raise ValueError("missing symbol table")
    named = {s.name: s for s in symbols.iter_symbols() if s.name}

    def read_symbol(symbol):
        index = symbol["st_shndx"]
        if not isinstance(index, int):
            raise ValueError("undefined symbol")
        section = elf.get_section(index)
        if section["sh_type"] == "SHT_NOBITS":
            raise ValueError("symbol has no file bytes")
        return bounded_slice(section.data(), symbol["st_value"], symbol["st_size"])

    images = {}
    for name, symbol in named.items():
        if not RADIO_NAME.fullmatch(name):
            continue
        length = named.get(name + "_len")
        if length is None or length["st_size"] != 4:
            raise ValueError("missing embedded length")
        blob = read_symbol(symbol)
        if len(blob) != int.from_bytes(read_symbol(length), "little" if elf.little_endian else "big"):
            raise ValueError("embedded length mismatch")
        images[name] = map_container(blob)
    if not images:
        raise ValueError("no expected embedded radio images")
    return {"module_sha256": hashlib.sha256(raw).hexdigest(), "images": images}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze_module(args.module)
    # Refuse to overwrite earlier evidence, even on a deterministic re-run.
    with args.output.open("x", encoding="utf-8") as out:
        json.dump(result, out, indent=2, sort_keys=True)
        out.write("\n")


if __name__ == "__main__":
    main()
