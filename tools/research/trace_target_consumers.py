"""Pinned, offline AP consumer tracing; candidate scans are not CFG evidence.

No target execution, writes, or API compatibility claims. Common Xtensa ISA
formulas are independently checked against GNU decoding at known boundaries.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from tools.research.qualify_xtensa import memory_window
from tools.research.trace_airmax_target import l32r_addresses, load_image, trace

PARSER = 0x9B546C
CALLER = 0x9B1FF4
LITBASE_HYPOTHESIS = 0x9BB001
WINDOWS = [CALLER, 0x9B2578, 0x9B24C5, 0x9B7264, 0x9B77C4, 0x9B68CC]


def call8_target(instruction: bytes, pc: int) -> int:
    """LE common CALL8 encoding, QEMU dc233c soffsetx4 semantics.

    Matching bytes alone never establish an instruction boundary.
    """
    if len(instruction) != 3 or instruction[0] & 0x3F != 0x25:
        raise ValueError("expected three-byte LE CALL8 candidate")
    if type(pc) is not int or not 0 <= pc <= 0xFFFFFFFF:
        raise ValueError("invalid instruction address")
    value = int.from_bytes(instruction, "little") >> 6
    if value & (1 << 17):
        value -= 1 << 18
    return ((pc & ~3) + 4 + value * 4) & 0xFFFFFFFF


def scan_call8_candidates(data: bytes, base: int, targets: set[int]) -> list[dict]:
    """Bounded byte scan; all returned edges remain unverified candidates."""
    if not data or len(data) > 1024 * 1024:
        raise ValueError("expected nonempty segment no larger than 1 MiB")
    if type(base) is not int or not 0 <= base <= 0xFFFFFFFF or base + len(data) > 1 << 32:
        raise ValueError("invalid segment address range")
    if not 1 <= len(targets) <= 32 or any(type(t) is not int or not 0 <= t <= 0xFFFFFFFF for t in targets):
        raise ValueError("expected 1..32 target addresses")
    candidates = []
    for offset in range(len(data) - 2):
        if data[offset] & 0x3F != 0x25:
            continue
        address = base + offset
        target = call8_target(data[offset:offset + 3], address)
        if target in targets:
            if len(candidates) >= 64:
                raise ValueError("candidate limit exceeded")
            candidates.append({"address": address, "target": target,
                               "status": "BYTE_PATTERN_CANDIDATE_NOT_BOUNDARY_PROOF"})
    return candidates


def branch_table(instructions: list[dict], base: int, count: int) -> list[dict]:
    """Require exact three-byte J rows at every proposed branch-table slot."""
    if type(count) is not int or not 1 <= count <= 64:
        raise ValueError("invalid branch-table count")
    rows = {row["address"]: row for row in instructions}
    if len(rows) != len(instructions):
        raise ValueError("duplicate instruction addresses")
    result = []
    for index in range(count):
        row = rows.get(base + 3 * index)
        if not row or row["mnemonic"] != "j" or row["byte_length"] != 3:
            raise ValueError("branch table is not contiguous decoded three-byte J rows")
        # This pinned image's GNU address spelling starts with a decimal digit;
        # reject register-looking/unresolved text rather than guessing.
        if not re.fullmatch(r"[0-9][0-9a-fA-F]{0,7}", row["operands"].strip()):
            raise ValueError("unresolved branch target")
        try:
            target = int(row["operands"].strip(), 16)
        except ValueError as error:
            raise ValueError("unresolved branch target") from error
        if not 0 <= target <= 0xFFFFFFFF:
            raise ValueError("invalid branch target")
        result.append({"index": index, "branch_address": row["address"], "target": target})
    return result


def validated_block(window: dict, last_address: int) -> list[dict]:
    """Require a contiguous successful syntax prefix through a selected edge.

    Does not establish reachability; discards every row beyond this block.
    Prefix validation is positional, never address-set membership.
    """
    if window.get("returncode") != 0 or window.get("unparsed_instruction_line_count") != 0:
        raise ValueError("decoder failure or unparsed rows")
    rows = window["instructions"]
    prefix = window["syntax_prefix_addresses"]
    selected = rows[:len(prefix)]
    if [row["address"] for row in selected] != prefix or len(prefix) != len(set(prefix)):
        raise ValueError("prefix is not unique positional instruction sequence")
    expected = window["address"]
    for row in selected:
        if row["address"] != expected or row["byte_length"] not in (2, 3):
            raise ValueError("noncontiguous common-ISA prefix")
        if row["mnemonic"].startswith(".") or row["mnemonic"] in ("excw", "ill"):
            raise ValueError("illegal instruction in selected prefix")
        expected += row["byte_length"]
        if row["address"] == last_address:
            return selected[:selected.index(row) + 1]
    raise ValueError("selected block extends past validated prefix")


def collect(module: Path, prefix: str) -> dict:
    metadata, segments = load_image(module, "ptmp_ap")
    code = [(base, data) for base, data in segments if base <= 0x983C00 < base + len(data)]
    if len(code) != 1:
        raise ValueError("expected one pinned entry-containing code segment")
    base, data = code[0]
    candidates = scan_call8_candidates(data, base, {PARSER, 0x9B03FC})
    traced = trace(module, "ptmp_ap", WINDOWS, 256, prefix, LITBASE_HYPOTHESIS)
    caller = traced["tool"]["windows"][0]
    block_ends = [0x9B20D0, 0x9B258E, 0x9B24DB, 0x9B72A8, 0x9B7826, 0x9B6980]
    blocks = [validated_block(window, end) for window, end in zip(traced["tool"]["windows"], block_ends)]
    for rows in blocks[:-1]:
        if rows[-1]["mnemonic"] != "retw.n":
            raise ValueError("selected block does not end at expected return")
    if blocks[-1][-1]["mnemonic"] != "j" or int(blocks[-1][-1]["operands"], 16) != 0x9B68FD:
        raise ValueError("lookup selected block does not end at expected back edge")
    call = next(row for row in blocks[0] if row["address"] == 0x9B2005)
    if call["mnemonic"] != "call8" or int(call["operands"], 16) != PARSER:
        raise ValueError("known parser call did not independently decode")
    if call8_target(memory_window(segments, call["address"], 3), call["address"]) != PARSER:
        raise ValueError("independent call target formula differs from decoder")
    slots = branch_table(blocks[0], 0x9B2037, 51)
    entry_literals = []
    for address in [0x983C03, 0x983C06, 0x983C0B]:
        model = l32r_addresses(memory_window(segments, address, 3), address, LITBASE_HYPOTHESIS)
        model["instruction_address"] = address
        model["conditional_word_le"] = int.from_bytes(memory_window(segments, model["hypothesis_literal_address"], 4), "little")
        entry_literals.append(model)
    unresolved_slots = []
    for offset in [0x138, 0x288, 0x28C]:
        address = 0x4062DC + offset
        try:
            word = int.from_bytes(memory_window(segments, address, 4), "little")
            unresolved_slots.append({"address": address, "mapped_word": word})
        except ValueError:
            unresolved_slots.append({"address": address, "status": "UNMAPPED_IN_DOWNLOADED_SEGMENTS"})
    return {"schema_version": 1, "role": "ptmp_ap", "module_sha256": traced["module_sha256"],
            "container_sha256": metadata["container_sha256"],
            "entry_containing_segment": {"address": base, "length": len(data), "sha256": hashlib.sha256(data).hexdigest()},
            "call8_candidates": candidates, "verified_parser_call": {"address": 0x9B2005, "target": PARSER},
            "validated_blocks": [{"entry": rows[0]["address"], "last_instruction": rows[-1]["address"],
                                  "instruction_count": len(rows), "status": "VALIDATED_SYNTAX_NOT_REACHABILITY"} for rows in blocks],
            "caller_branch_table": {"base": 0x9B2037, "status": "CONDITIONAL_ON_UNVERIFIED_LITBASE", "entries": slots},
            "entry_literal_models": entry_literals, "conditional_indirect_slots": unresolved_slots,
            "consumer_observations": {
                "status": "STATIC_COMMON_ISA_CONDITIONAL_ON_UNVERIFIED_LITBASE_AND_INDIRECT_ABI",
                "subtype_0x17": {
                    "entry": 0x9B7264, "return": 0x9B72A8,
                    "positional_inputs": ["B -> a3", "H0 -> a4", "H1 -> a5", "H2 -> a6", "I -> a7"],
                    "observed_operations": [
                        "ROM-like slot 0x400000+244 receives (sp,0,56); zero-initialization inference only.",
                        "Conditional base 0x4062dc+0x288 indirect call receives (B,sp).",
                        "H0,H1,H2 stored as 32-bit values at sp+20,+24,+28.",
                        "sp+8 updated to (old & 0xffffc5ef) | (I & 0x3a10).",
                        "Conditional base 0x4062dc+0x28c indirect call receives (B,sp,1)."],
                    "unresolved": "Indirect pointer slots lie outside supplied segments; their target values are UNKNOWN. EDCA/CW/TXOP semantics not established."},
                "subtype_0x1e": {
                    "entry": 0x9B77C4, "return": 0x9B7826,
                    "positional_inputs": ["context -> a2", "B0 -> a3", "B1 -> a4", "B2 -> a5", "B3 -> a6", "B4 -> a7"],
                    "observed_operations": [
                        "Conditional base 0x4062dc+0x138 indirect call receives first argument 13; returned a10 retained as opaque value.",
                        "If B0 !=0, context+0x491 stores B1; if B1==0, branch directly to final flag store.",
                        "If B0 and B1 nonzero, 0x9b68cc receives (context,opaque,B2,context+0x494,0,0,stack0=0).",
                        "Then context+0x498 stores B3; if B3!=0, 0x9b68cc receives analogous arguments with B4 and context+0x49a.",
                        "context+0x490 stores 1 when B0 and B1 nonzero, else 0."],
                    "unresolved": "Opaque indirect result remains unresolved; lookup encoding is positional, not a verified rate-control ABI."},
                "lookup_0x9b68cc": {
                    "entry": 0x9B68CC, "bounded_last_branch": 0x9B6980,
                    "returns": [0x9B6940, 0x9B6958],
                    "positional_inputs": ["opaque -> a3", "B2 or B4 -> a4", "16-bit output pointer -> a5", "a6=0", "a7=0", "stack argument0=0"],
                    "observed_operations": [
                        "Reads byte bits1..4 into index-like a8, bits5..6 into class-like a9; bit0 selects comparison mask1 or2.",
                        "Class branches select internal a6 value1,4,5,6 for bits5..6=3,0,1,2 respectively with these zero optional arguments.",
                        "For class3, caps index-like a8 at6. Bit0 adds8 only when internal a6 is2or3; neither occurs with these zero optional arguments.",
                        "Reads count from opaque+0; initializes16-bit output0; loops over records by incrementing pointer40bytes and candidateindex1.",
                        "Filters record+12 nonzero and record+16 matching internal class; class1 compares recordbyte38 with twice the byte from conditional literal table0x40bb40+index.",
                        "Other classes require record+20 bitmap matching bit0-derived mask and recordbyte38 matching index.",
                        "On match stores candidateindex as16bits; optional nonzeroa7 would receive record+24word, but both traced callers pass0."],
                    "unresolved": "No calls in this bounded branch subgraph; input object provenance stops at unmapped indirectslot0x406414."}},
            "trace": traced, "sources": [
                "https://raw.githubusercontent.com/qemu/qemu/master/target/xtensa/core-dc233c/xtensa-modules.c.inc",
                "https://raw.githubusercontent.com/qemu/qemu/master/target/xtensa/translate.c"],
            "limits": ["Byte scanning can match data or misaligned bytes; only parser call independently boundary-verified here.",
                       "LITBASE 0x9bb001 is a mathematical hypothesis, not runtime register evidence.",
                       "Consumer table: subtype23 ->9b2578 ->9b7264; subtype30 ->9b24c5 ->9b77c4.",
                       "Linear windows after returns are not semantic evidence; unresolved indirect calls stop authoritative tracing.",
                       "No exact QCA core qualification, execution, RF result, or airOS/ath10k ABI compatibility established."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument("--esp-prefix", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = collect(args.module, args.esp_prefix)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
