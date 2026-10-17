"""Offline ELF metadata for airOS modules; never executes or exports firmware code.

Requires pyelftools. Reports embedded radio-image hashes and relocation references.
Relocations are references, NOT proof of calls, runtime timing, or hardware authority.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from pathlib import Path

from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
from elftools.elf.sections import SymbolTableSection

RADIO_NAME = re.compile(r"^athwlan_AR9888v2_(ptp|ptmp_ap|ptmp_sta)_bin$")
MARKERS = (b"UBNT_POLL_MEM_ALLOC", b"ubnt-poll", b"_on_swbmiss", b"ubnt_set_power_range")


def bounded_slice(data: bytes, offset: int, size: int) -> bytes:
    if offset < 0 or size <= 0 or offset > len(data) or size > len(data) - offset:
        raise ValueError("symbol range is outside its file-backed section")
    return data[offset:offset + size]


def describe_blob(data: bytes, declared_size: int) -> dict:
    if len(data) != declared_size:
        raise ValueError("embedded length disagrees with ELF symbol size")
    return {
        "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        "magic_hex": data[:4].hex(),
        "markers": {m.decode(): [x.start() for x in re.finditer(re.escape(m), data)]
                    for m in MARKERS},
    }


def inspect(path: Path, decode_mips: bool = False, analyze_sgmt: bool = False) -> dict:
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("module exceeds 64 MiB analysis limit")
    raw = path.read_bytes()
    elf = ELFFile(io.BytesIO(raw))
    if elf.header["e_type"] != "ET_REL":
        raise ValueError("expected a relocatable kernel module (ET_REL)")
    decoder = None
    if decode_mips:
        from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_BIG_ENDIAN, CS_MODE_LITTLE_ENDIAN
        if elf.header["e_machine"] != "EM_MIPS" or elf.elfclass != 32:
            raise ValueError("MIPS decoder requires ELF32 EM_MIPS")
        decoder = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 |
                     (CS_MODE_LITTLE_ENDIAN if elf.little_endian else CS_MODE_BIG_ENDIAN))
    table = elf.get_section_by_name(".symtab")
    if not isinstance(table, SymbolTableSection):
        raise ValueError("module has no symbol table")
    symbols = list(table.iter_symbols())
    named = {s.name: s for s in symbols if s.name}

    def symbol_bytes(symbol):
        index = symbol["st_shndx"]
        if not isinstance(index, int):
            raise ValueError("symbol is not defined in a section")
        section = elf.get_section(index)
        if section["sh_type"] == "SHT_NOBITS":
            raise ValueError("symbol has no file-backed bytes")
        # ET_REL st_value is section-relative, even when sh_addr is nonzero.
        offset = symbol["st_value"]
        return bounded_slice(section.data(), offset, symbol["st_size"])

    blobs = {}
    for name, symbol in named.items():
        if RADIO_NAME.fullmatch(name):
            length_symbol = named.get(name + "_len")
            if length_symbol is None or length_symbol["st_size"] != 4:
                raise ValueError("missing four-byte embedded length: " + name)
            length = int.from_bytes(symbol_bytes(length_symbol),
                                    "little" if elf.little_endian else "big")
            blob_data = symbol_bytes(symbol)
            blobs[name] = describe_blob(blob_data, length)
            if analyze_sgmt:
                if __package__:
                    from .sgmt import parse_sgmt
                else:
                    from sgmt import parse_sgmt
                blobs[name]["sgmt"] = parse_sgmt(blob_data)

    functions = [s for s in symbols if s["st_info"]["type"] == "STT_FUNC"
                 and isinstance(s["st_shndx"], int) and s["st_size"] > 0]
    refs = []
    for section in elf.iter_sections():
        if not isinstance(section, RelocationSection):
            continue
        linked = elf.get_section(section["sh_link"])
        owners = [s for s in functions if s["st_shndx"] == section["sh_info"]]
        for relocation in section.iter_relocations():
            target_symbol = linked.get_symbol(relocation["r_info_sym"])
            target = target_symbol.name
            offset = relocation["r_offset"]
            owner = next((s.name for s in owners
                          if s["st_value"] <= offset < s["st_value"] + s["st_size"]), None)
            if owner and ("poll" in owner.lower() or "poll" in target.lower()
                          or owner == "ol_transfer_bin_file"):
                reference = {"owner": owner, "target": target,
                             "target_symbol_type": target_symbol["st_info"]["type"],
                             "relocated_section": elf.get_section(section["sh_info"]).name,
                             "relocation_type": relocation["r_info_type"],
                             "section_offset": offset}
                if section.is_RELA():
                    reference["explicit_addend"] = relocation["r_addend"]
                if decoder is not None and relocation["r_info_type"] == 4:
                    code = elf.get_section(section["sh_info"]).data()
                    word = bounded_slice(code, offset, 4)
                    instruction = next(decoder.disasm(word, offset), None)
                    reference["instruction"] = instruction.mnemonic if instruction else "undecoded"
                    reference["encoded_target_field"] = (int.from_bytes(
                        word, "little" if elf.little_endian else "big") & 0x03ffffff) << 2
                    # This is not a complete MIPS linker/addend evaluation. A false
                    # value may still represent a tail jump rather than no call.
                    reference["named_jal_relocation"] = bool(target and instruction
                                                             and instruction.mnemonic == "jal")
                refs.append(reference)
    focus = []
    if decoder is not None:
        for symbol in functions:
            if symbol.name in {"ubnt_poll_host_ht_comm_tx", "ubnt_poll_ht_comm_send"}:
                instructions = list(decoder.disasm(symbol_bytes(symbol), symbol["st_value"]))
                focus.append({"name": symbol.name, "section_offset": symbol["st_value"],
                              "size": symbol["st_size"],
                              "decoded_bytes": sum(i.size for i in instructions),
                              "indirect_call_offsets": [i.address for i in instructions
                                                        if i.mnemonic == "jalr"]})
    return {
        "file": path.name, "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "machine": elf.header["e_machine"], "elf_class": elf.elfclass,
        "byte_order": "little" if elf.little_endian else "big",
        "embedded_radio_images": blobs,
        "poll_function_symbols": sorted({s.name for s in functions if "poll" in s.name.lower()}),
        "relocation_references": refs,
        "focused_transport_functions": focus,
        "limits": "Static symbols and optional call-opcode evidence only; no runtime execution, exact callee-entry or timing proof; no device operation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("modules", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--decode-mips", action="store_true", help="Verify call opcodes with installed Capstone")
    parser.add_argument("--sgmt", action="store_true", help="Decode bounded SGMT containers in memory; emit only metadata")
    args = parser.parse_args()
    result = {"schema_version": 1, "modules": [inspect(p, args.decode_mips, args.sgmt) for p in args.modules]}
    # Exclusive creation preserves prior evidence rather than silently replacing it.
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
