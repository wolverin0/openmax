"""Bounded offline RE1 byte qualification; artifacts stay in an ignored runtime."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import subprocess
import importlib.metadata
from pathlib import Path

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_BIG_ENDIAN
from elftools.elf.elffile import ELFFile

HOST_HASH = "19f379b1a776603634e367d547eaabed20f705865cacaaef06193ac04bb70e14"
RADIO_HASH = "46525dc6f8b789bf820f0713841a2a9ecdcba833300ddb1ab1ef06fc4ab6a9c5"
PRIOR_DECODER_HASH = "0b5fbcb47d8502a40c198b9c6d80689e9de7a12941af94bfb79d6f418e166e24"
SGMT_DECODER_HASH = "f6e8a73fa2277a26901469a825373dba512262464015e8772a4acf6a1f47dec8"


def validate_window_bytes(text: bytes, rows: dict, start: int, end: int, relocations: dict) -> list:
    """Require original bytes except at explicitly declared ELF relocation sites."""
    changed = []
    for at in range(start, end, 4):
        original = text[at:at + 4].hex()
        mapped = rows[at]["hex"]
        if mapped == original:
            continue
        if at not in relocations:
            raise ValueError(f"Undeclared original/Ghidra byte mismatch at {at:#x}")
        masks = {4: 0xFC000000, 5: 0xFFFF0000, 6: 0xFFFF0000}
        kind = relocations[at]["elf_relocation_type"]
        if kind not in masks or ((int(original, 16) ^ int(mapped, 16)) & masks[kind]):
            raise ValueError(f"Relocation changed opcode/register bits at {at:#x}")
        changed.append({"section_offset": hex(at), "original_hex": original, "ghidra_hex": mapped,
                        **relocations[at], "status": "Declared relocation; not runtime address proof"})
    return changed


def compare_xtensa(source: Path, runtime: Path, segments: list) -> dict:
    """Fresh Ghidra syntax vs explicitly reused, hash-bound prior ESP32 decoder output."""
    prior_path = source / "research/raw/xtensa-qualification-20261006-elf.json"
    prior_bytes = prior_path.read_bytes()
    if hashlib.sha256(prior_bytes).hexdigest() != PRIOR_DECODER_HASH:
        raise ValueError("Prior independent decoder receipt changed")
    prior = json.loads(prior_bytes)
    tool = next(t for t in prior["tools"] if t["name"] == "ESP32")
    fresh = json.loads((runtime / "ap-ghidra.json").read_text())
    required = {"0x983c00", "0x9b0620", "0x9b1604", "0x9b1eec"}
    if fresh["language"] != "Xtensa:LE:32:default" or not required.issubset({w["start"] for w in fresh["windows"]}):
        raise ValueError("Required fresh Xtensa profile/windows missing")
    checks = []
    fresh_only = []
    for window in fresh["windows"]:
        start = int(window["start"], 16)
        oracle = next((w for w in tool["windows"] if w["role"] == "ptmp_ap" and w["address"] == start), None)
        if oracle is None:
            fresh_only.append({"start": window["start"], "instructions": len(window["instructions"]),
                               "status": "Fresh common-ISA listing only; independent operand/core qualification pending"})
            continue
        payload = next(data[start - base:start - base + 128] for base, data in reversed(segments)
                       if base <= start and start + 128 <= base + len(data))
        if hashlib.sha256(payload).hexdigest() != oracle["window_sha256"]:
            raise ValueError("Prior Xtensa window hash differs from original SGMT bytes")
        originals = {r["address"]: r for r in oracle["instructions"]}
        for row in window["instructions"]:
            at = int(row["address"], 16)
            other = originals[at]
            if row["length"] != other["byte_length"] or row["instruction"].split()[0] != other["mnemonic"]:
                raise ValueError(f"Xtensa syntax disagreement at {at:#x}")
            if row["hex"] != payload[at - start:at - start + row["length"]].hex():
                raise ValueError(f"Ghidra Xtensa bytes differ at {at:#x}")
        checks.append({"start": window["start"], "window_sha256": oracle["window_sha256"],
                       "matched_mnemonics_and_lengths": len(window["instructions"]),
                       "ghidra_stop": window.get("stop_address"), "complete_128_byte_semantics": False})
    return {"fresh_decoder": fresh["language"], "reused_decoder": "ESP32 objdump, 2026-10-06",
            "reused_receipt_sha256": hashlib.sha256(prior_bytes).hexdigest(), "windows": checks,
            "additional_consumer_windows": fresh_only,
            "limits": ["Mnemonic/length and original-byte agreement, not full operand or core semantics",
                       "Default L32R addressing agrees with prior decoder but LITBASE remains unqualified",
                       "Reused ESP32 decoder is also not the exact QCA core",
                       "A listing gap after return is not necessarily a decoder failure"]}


def qualify(source: Path, runtime: Path, require_ap: bool = True) -> dict:
    allowed = (Path(__file__).resolve().parents[3] / "firmware/build").resolve()
    if not runtime.is_relative_to(allowed) or runtime == allowed:
        raise ValueError("Runtime must be a private directory under this checkout's firmware/build")
    runtime.mkdir(parents=True, exist_ok=True)
    modules = source / "firmware/build/codex-analysis-20261006/rootfs/lib/modules/2.6.32.68"
    raw = (modules / "ubnt_poll_host.ko").read_bytes()
    if hashlib.sha256(raw).hexdigest() != HOST_HASH:
        raise ValueError("Host module does not match the prior byte-level oracle")
    elf = ELFFile(io.BytesIO(raw))
    if (elf.elfclass, elf.little_endian, elf.header["e_type"]) != (32, False, "ET_REL"):
        raise ValueError("Expected ELF32 big-endian relocatable module")
    text = elf.get_section_by_name(".text").data()
    symtab = elf.get_section_by_name(".symtab")
    relocations = {r["r_offset"]: {"elf_relocation_type": r["r_info_type"],
                                   "symbol": symtab.get_symbol(r["r_info_sym"]).name}
                   for r in elf.get_section_by_name(".rel.text").iter_relocations()}
    ghidra = json.loads((runtime / "host-ghidra.json").read_text())
    if ghidra["executable_sha256"] != HOST_HASH or ghidra["language"] != "MIPS:BE:32:default":
        raise ValueError("Ghidra input/profile mismatch")
    decoder = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_BIG_ENDIAN)
    anchors = {0x108C: "24420003", 0x1090: "2403fffc", 0x1094: "00439024", 0x10B4: "34079064"}
    rows = {int(r["section_offset"], 16): r for r in ghidra["instruction_windows"]}
    checked = []
    for at, expected in anchors.items():
        original = text[at:at + 4]
        if original.hex() != expected or rows[at]["hex"] != expected:
            raise ValueError(f"Original/Ghidra anchor mismatch at {at:#x}")
        insn = next(decoder.disasm(original, at))
        checked.append({"section_offset": hex(at), "original_hex": expected,
                        "capstone": f"{insn.mnemonic} {insn.op_str}", "ghidra": rows[at]["instruction"]})
    bounded = []
    changed_relocations = []
    for start, end, label in [(0xFE4, 0x1020, "word_transform"), (0x1020, 0x10E0, "transport"),
                               (0x13950, 0x139F0, "header"),
                               (0x13D50, 0x13D80, "subtype_1e"), (0x13DF0, 0x13E44, "subtype_17"),
                               (0xAE90, 0xAFC0, "rate_override_packing")]:
        changed_relocations.extend(validate_window_bytes(text, rows, start, end, relocations))
        decoded = list(decoder.disasm(text[start:end], start))
        if len(decoded) != (end - start) // 4:
            raise ValueError(f"Incomplete independent MIPS window {label}")
        bounded.append({"label": label, "section": ".text", "start": hex(start),
                        "instructions": [{"offset": hex(i.address), "hex": i.bytes.hex(),
                                          "instruction": f"{i.mnemonic} {i.op_str}"}
                                         for i in decoded]})
    functions = {r["name"]: {"entry": r["entry"], "completed": r["completed"]}
                 for r in ghidra["functions"]}
    if len(functions) != 5 or not all(f["completed"] for f in functions.values()):
        raise ValueError("Required host functions failed decompilation")
    text_base = int(next(b["start"] for b in ghidra["blocks"] if b["name"] == ".text"), 16)
    jump_checks = []
    rodata = elf.get_section_by_name(".rodata").data()
    mapped_entries = {int(r["section_offset"], 16): r["hex"] for r in ghidra["jump_table_entries"]}
    for at, expected in [(0x5EAC, 0x13DF0), (0x5EC8, 0x13D50)]:
        original = int.from_bytes(rodata[at:at + 4], "big")
        mapped = int(mapped_entries[at], 16)
        if original != expected or mapped != original + text_base:
            raise ValueError("Serializer jump-table original/relocated target mismatch")
        jump_checks.append({"rodata_offset": hex(at), "original_text_offset": hex(original), "mapped": hex(mapped)})
    radio = (modules / "umac.ko").read_bytes()
    if hashlib.sha256(radio).hexdigest() != RADIO_HASH:
        raise ValueError("Radio-bearing module hash differs from prior qualified input")
    radio_elf = ELFFile(io.BytesIO(radio))
    symbol = next(s for s in radio_elf.get_section_by_name(".symtab").iter_symbols()
                  if s.name == "athwlan_AR9888v2_ptmp_ap_bin")
    section = radio_elf.get_section(symbol["st_shndx"]).data()
    blob = section[symbol["st_value"]:symbol["st_value"] + symbol["st_size"]]
    decoder_path = source / "tools/research/sgmt.py"
    if hashlib.sha256(decoder_path.read_bytes()).hexdigest() != SGMT_DECODER_HASH:
        raise ValueError("Existing qualified SGMT decoder changed")
    spec = importlib.util.spec_from_file_location("re1_existing_sgmt", decoder_path)
    sgmt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sgmt)
    metadata, segments = sgmt.decode_sgmt_memory(blob)
    if any(r["kind"] == "EXEC" for r in metadata["records"]):
        raise ValueError("Intermediate EXEC context not qualified")
    boundaries = sorted({a for a, d in segments} | {a + len(d) for a, d in segments})
    final_map = []
    for start, end in zip(boundaries, boundaries[1:]):
        for order in range(len(segments) - 1, -1, -1):
            base, data = segments[order]
            if base <= start and end <= base + len(data):
                payload = data[start - base:end - base]
                name = f"ap-segment-{len(final_map):02d}.bin"
                (runtime / name).write_bytes(payload)
                final_map.append({"start": start, "size": len(payload), "file": name,
                                  "sha256": hashlib.sha256(payload).hexdigest(), "source_load_order": order})
                break
    (runtime / "ap-import-manifest.json").write_text(json.dumps(final_map, indent=2))
    missing = [hex(a) for a in (0x406414, 0x406564, 0x406568)
               if not any(base <= a and a + 4 <= base + len(data) for base, data in segments)]
    receipt = {"schema_version": 1, "evidence_level": "static-build-specific",
               "host_sha256": HOST_HASH, "radio_module_sha256": RADIO_HASH,
               "ghidra_profile": ghidra["language"], "relocations": ghidra["relocations"],
               "checked_transport_anchors": checked, "selected_functions": functions,
               "changed_declared_relocations": changed_relocations,
               "jump_table_checks": jump_checks,
               "source_root_git_head": subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip(),
               "sgmt_decoder_sha256": SGMT_DECODER_HASH,
               "python_tools": {"capstone": importlib.metadata.version("capstone"), "pyelftools": importlib.metadata.version("pyelftools")},
               "independent_original_instructions": bounded,
               "ap_container_sha256": metadata["container_sha256"],
               "ap_final_map": final_map, "unmapped_indirect_pointer_slots": missing,
               "limits": ["No firmware execution or radio contact", "No performance claim",
                          "Generic Xtensa is not an exact QCA-core qualification",
                          "Unmapped slots are not zero-filled or invented"]}
    if require_ap:
        receipt["xtensa_comparison"] = compare_xtensa(source, runtime, segments)
    after = {"host": hashlib.sha256((modules / "ubnt_poll_host.ko").read_bytes()).hexdigest(),
             "radio": hashlib.sha256((modules / "umac.ko").read_bytes()).hexdigest()}
    if after["host"] != HOST_HASH or after["radio"] != RADIO_HASH:
        raise ValueError("Original module changed during qualification")
    receipt["original_module_hashes_before"] = {"host": hashlib.sha256(raw).hexdigest(), "radio": hashlib.sha256(radio).hexdigest()}
    receipt["original_module_hashes_after"] = after
    receipt["original_module_hashes_preserved"] = True
    (runtime / "byte-qualification.json").write_text(json.dumps(receipt, indent=2))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--prepare-only", action="store_true", help="Prepare AP import, not final acceptance")
    args = parser.parse_args()
    result = qualify(args.source_root.resolve(), args.runtime.resolve(), require_ap=not args.prepare_only)
    print(json.dumps({"anchors_checked": len(result["checked_transport_anchors"]),
                      "private_ap_segments": len(result["ap_final_map"]),
                      "unmapped_slots": result["unmapped_indirect_pointer_slots"]}))
