"""RE1.6: bounded held-role survey and original host caller evidence; no device I/O."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_BIG_ENDIAN
from elftools.elf.elffile import ELFFile
from re1_pilot import HOST_HASH, RADIO_HASH, SGMT_DECODER_HASH, validate_window_bytes

VALUES = (0x4062DC, 0x406414, 0x406564, 0x406568)
OVERLAY_HASH = "8ef8405a4da382656ac425d4d96b08bb8112534ec73ecd2ded82fef6cecec463"
ELF_ORACLE_HASH = "3916c8c061f7c0c71aa2b62e6f409db8b7932f7bc6948fa702833bf45e9f4784"


def survey_regions(regions: list[tuple[int, bytes]]) -> dict:
    """Exact slot coverage and aligned literal candidates, never inferred pointers."""
    results = {}
    for value in VALUES:
        containing = next(((base, data) for base, data in regions
                           if base <= value and value + 4 <= base + len(data)), None)
        matches = []
        count = 0
        for base, data in regions:
            for offset in range((-base) % 4, len(data) - 3, 4):
                if int.from_bytes(data[offset:offset + 4], "little") == value:
                    count += 1
                    if len(matches) < 32:
                        matches.append(hex(base + offset))
        results[hex(value)] = {
            "four_byte_slot_covered": containing is not None,
            "slot_word_le": (hex(int.from_bytes(containing[1][value - containing[0]:
                                            value - containing[0] + 4], "little"))
                             if containing else None),
            "aligned_literal_addresses": matches,
            "aligned_literal_count": count,
            "matches_truncated": count > len(matches),
        }
    return results


def checked_bytes(path: Path, expected: str) -> bytes:
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("input size limit exceeded")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("original input hash mismatch")
    return raw


def analyze(source: Path, native_evidence: Path | None = None) -> dict:
    decoder_path = source / "tools/research/sgmt.py"
    checked_bytes(decoder_path, SGMT_DECODER_HASH)
    checked_bytes(source / "tools/research/target_firmware_map.py", OVERLAY_HASH)
    checked_bytes(source / "tools/research/inspect_radio_elf.py", ELF_ORACLE_HASH)
    sys.path.insert(0, str(source))
    from tools.research.sgmt import decode_sgmt_memory
    from tools.research.target_firmware_map import loaded_regions
    from tools.research.inspect_radio_elf import RADIO_NAME, bounded_slice

    modules = source / "firmware/build/codex-analysis-20261006/rootfs/lib/modules/2.6.32.68"
    raw = checked_bytes(modules / "umac.ko", RADIO_HASH)
    elf = ELFFile(io.BytesIO(raw))
    symbols = list(elf.get_section_by_name(".symtab").iter_symbols())
    named = {s.name: s for s in symbols if s.name}
    bmi_relocations = {"BMIWriteMemory": [], "BMIExecute": []}
    for relocation in elf.get_section_by_name(".rel.text").iter_relocations():
        name = symbols[relocation["r_info_sym"]].name
        if name in bmi_relocations and relocation["r_info_type"] == 4:
            bmi_relocations[name].append(hex(relocation["r_offset"]))
    images = {}
    for name, symbol in named.items():
        if not RADIO_NAME.fullmatch(name) and name != "otp_AR9888v2_bin":
            continue
        data = elf.get_section(symbol["st_shndx"]).data()
        blob = bounded_slice(data, symbol["st_value"], symbol["st_size"])
        length = named[name + "_len"]
        length_bytes = bounded_slice(elf.get_section(length["st_shndx"]).data(),
                                     length["st_value"], length["st_size"])
        if len(length_bytes) != 4 or int.from_bytes(length_bytes, "big") != len(blob):
            raise ValueError("embedded length mismatch")
        meta, segments = decode_sgmt_memory(blob)
        if any(r["kind"] == "EXEC" for r in meta["records"]):
            raise ValueError("EXEC prevents static overlay conclusion")
        regions = loaded_regions(segments)
        images[name] = {"container_sha256": meta["container_sha256"],
                        "container_size": meta["container_size"], "file_flags": meta["file_flags"],
                        "decoded_total": meta["decoded_total"],
                        "record_kinds": [r["kind"] for r in meta["records"]],
                        "kind": "bootstrap_blob" if name.startswith("otp_") else "radio_role",
                        "regions": [{"start": hex(a), "size": len(p),
                                     "sha256": hashlib.sha256(p).hexdigest()} for a, p in regions],
                        "survey": survey_regions(regions)}
    if set(images) != {"athwlan_AR9888v2_ptp_bin", "athwlan_AR9888v2_ptmp_sta_bin",
                      "athwlan_AR9888v2_ptmp_ap_bin", "otp_AR9888v2_bin"}:
        raise ValueError("expected three held roles and the discovered bootstrap blob")

    host = ELFFile(io.BytesIO(checked_bytes(modules / "ubnt_poll_host.ko", HOST_HASH)))
    text = host.get_section_by_name(".text").data()
    symtab = host.get_section_by_name(".symtab")
    # Compilation units reuse local $LC names; resolve the actual branch relocation.
    ro_reference = next(r for r in host.get_section_by_name(".rel.text").iter_relocations()
                        if r["r_offset"] == 0x2600 and r["r_info_type"] == 6)
    ro_symbol = symtab.get_symbol(ro_reference["r_info_sym"])
    ro_bytes = host.get_section(ro_symbol["st_shndx"]).data()[ro_symbol["st_value"]:
                                                            ro_symbol["st_value"] + 3]
    if ro_bytes != b"ro\x00":
        raise ValueError("original ro selector string changed")
    calls = [r["r_offset"] for r in host.get_section_by_name(".rel.text").iter_relocations()
             if symtab.get_symbol(r["r_info_sym"]).name == "ubnt_poll_host_set_rate_override"
             and r["r_info_type"] == 4]
    if len(calls) != 1 or not 0x1FC8 <= calls[0] < 0x31FC:
        raise ValueError("unexpected original caller relocation")
    at = calls[0]
    decoder = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_BIG_ENDIAN)
    instructions = list(decoder.disasm(text[at - 100:at + 8], at - 100))
    if len(instructions) != 27 or instructions[-2].mnemonic != "jal":
        raise ValueError("original caller window did not decode completely")
    result = {"experiment": "RE1.6", "host_sha256": HOST_HASH, "radio_sha256": RADIO_HASH,
              "original_direct_bmi_relocations": bmi_relocations,
              "sgmt_decoder_sha256": SGMT_DECODER_HASH,
              "overlay_oracle_sha256": hashlib.sha256((source / "tools/research/target_firmware_map.py").read_bytes()).hexdigest(),
              "elf_oracle_sha256": ELF_ORACLE_HASH,
              "register_context": {"LITBASE_hypothesis": "0x9bb001", "status": "UNKNOWN",
                                   "limit": "Register-value hypothesis, not a memory slot; no dereference or literal-absence inference."},
              "images": images,
              "host_rate_call": {"section_offset": hex(at), "ghidra_address": hex(0x10000 + at),
                                 "original_selector_symbol": "$LC5",
                                 "original_selector_symbol_index": ro_reference["r_info_sym"],
                                 "original_selector_section_offset": hex(ro_symbol["st_value"]),
                                 "original_selector_hex": ro_bytes.hex(),
                                 "original_window_sha256": hashlib.sha256(text[at - 100:at + 8]).hexdigest(),
                                 "instructions": [{"offset": hex(i.address), "hex": i.bytes.hex(),
                                                   "instruction": i.mnemonic + " " + i.op_str} for i in instructions]},
              "limits": "Static exact held-role coverage and aligned literals only. No code/data, initializer, exact core, runtime LITBASE, pointer validity or role-equivalent ABI inferred."}
    if native_evidence is not None:
        evidence_bytes = native_evidence.read_bytes()
        native = json.loads(evidence_bytes)
        relocations = {r["r_offset"]: {"elf_relocation_type": r["r_info_type"],
                                      "symbol": symtab.get_symbol(r["r_info_sym"]).name}
                       for r in host.get_section_by_name(".rel.text").iter_relocations()}
        checks = []
        for key, start, end in (("mapped_caller_window", at - 100, at + 8),
                                 ("mapped_ro_branch", 0x25E4, 0x2614),
                                 ("mapped_readback_window", 0x2124, 0x2164)):
            listing = native[key]
            if listing["program"] != "ubnt_poll_host.ko" or listing.get("truncated"):
                raise ValueError("wrong or truncated native listing")
            rows = {int(i["address"], 16) - 0x10000: {"hex": i["bytes"]}
                    for i in listing["instructions"]}
            changed = validate_window_bytes(text, rows, start, end, relocations)
            checks.append({"name": key, "start": hex(start), "end_exclusive": hex(end),
                           "original_window_sha256": hashlib.sha256(text[start:end]).hexdigest(),
                           "checked_instructions": (end - start) // 4,
                           "declared_changed_sites": changed})
        result["native_original_byte_checks"] = checks
        result["private_native_evidence_sha256"] = hashlib.sha256(evidence_bytes).hexdigest()
    for name, expected in (("umac.ko", RADIO_HASH), ("ubnt_poll_host.ko", HOST_HASH)):
        checked_bytes(modules / name, expected)
    result["original_hashes_preserved"] = True
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--native-evidence", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.source_root.resolve(), args.native_evidence), indent=2))
