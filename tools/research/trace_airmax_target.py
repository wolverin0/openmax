"""Bounded offline instruction windows with explicit LITBASE hypotheses.

No execution or authoritative control-flow reconstruction. GNU ESP32 decoding
qualifies common instructions only, not the exact QCA core. Decoded firmware
bytes travel only through RAM/stdin/anonymous memfds, never payload files.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from tools.research.qualify_xtensa import MODULE_SHA256, REMOTE_SCRIPT, assess_window, memory_window, parse_disassembly
from tools.research.sgmt import decode_sgmt_memory


def l32r_addresses(instruction: bytes, pc: int, litbase: int | None) -> dict:
    """Common LE Xtensa model from QEMU uimm16x4/translate_l32r sources.

    Only call after an independently decoded L32R boundary. The caller's LITBASE
    value is a hypothesis, never inferred here from an attractive result.
    """
    if len(instruction) != 3 or instruction[0] & 15 != 1:
        raise ValueError("expected three-byte LE L32R encoding")
    if type(pc) is not int or not 0 <= pc <= 0xffffffff:
        raise ValueError("invalid instruction address")
    if litbase is not None and (type(litbase) is not int or not 0 <= litbase <= 0xffffffff or litbase & 0xfff != 1):
        raise ValueError("enabled LITBASE hypothesis requires aligned upper address plus bit 0")
    offset = (int.from_bytes(instruction[1:], "little") - 65536) * 4
    result = {"signed_offset": offset, "pc_relative_address": (((pc + 3) & ~3) + offset) & 0xffffffff}
    if litbase is not None:
        result["hypothesis_litbase_register"] = litbase
        result["hypothesis_literal_address"] = (litbase + offset - 1) & 0xffffffff
        result["status"] = "CONDITIONAL_ON_UNVERIFIED_LITBASE"
    return result


def load_image(module: Path, role: str):
    if module.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("module too large")
    raw = module.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MODULE_SHA256:
        raise ValueError("module differs from pinned profile")
    if role not in ("ptp", "ptmp_ap", "ptmp_sta"):
        raise ValueError("unknown role")
    elf = ELFFile(io.BytesIO(raw))
    symbol = next(s for s in elf.get_section_by_name(".symtab").iter_symbols()
                  if s.name == f"athwlan_AR9888v2_{role}_bin")
    section = elf.get_section(symbol["st_shndx"]).data()
    start, length = symbol["st_value"], symbol["st_size"]
    metadata, segments = decode_sgmt_memory(section[start:start + length])
    if any(r["kind"] == "EXEC" for r in metadata["records"]):
        raise ValueError("EXEC memory effects unsupported")
    return metadata, segments


def trace(module: Path, role: str, addresses: list[int], size: int, prefix: str,
          litbase: int | None) -> dict:
    if not 1 <= len(addresses) <= 32 or len(set(addresses)) != len(addresses):
        raise ValueError("expected 1..32 unique window addresses")
    metadata, segments = load_image(module, role)
    windows = []
    for address in addresses:
        data = memory_window(segments, address, size)
        windows.append({"role": role, "kind": "bounded_candidate_window", "address": address,
                        "size": size, "window_sha256": hashlib.sha256(data).hexdigest(),
                        "bytes_hex": data.hex()})
    request = {"tools": [{"name": "ESP32", "prefix": prefix}], "windows": windows}
    remote = REMOTE_SCRIPT.replace("request=REQUEST", "request=" + repr(request), 1)
    result = subprocess.run(["wsl", "-e", "python3", "-"], input=remote,
                            capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise ValueError("WSL decode failed: " + result.stderr)
    tool = json.loads(result.stdout)[0]
    for probe in tool["probes"]:
        instructions = parse_disassembly(probe.pop("disassembly", ""))
        if probe["returncode"] or probe.get("decode_returncode") or not any(i["mnemonic"] == probe["family"] for i in instructions):
            raise ValueError("instruction-family qualification failed")
        probe["instructions"] = instructions
    for window in tool["windows"]:
        window.update(assess_window(window.pop("disassembly", ""), window["address"], window["size"], window["returncode"]))
        rows = window["instructions"]
        usable_count = len(window["syntax_prefix_addresses"])
        window["decoded_row_bytes"] = sum(i["byte_length"] for i in rows)
        window["unknown_directive_addresses"] = [i["address"] for i in rows if i["mnemonic"].startswith(".") or i["mnemonic"] in ("ill", "excw")]
        for row_index, row in enumerate(rows):
            row["operands"] = re.sub(r"\s*<[^>]+>", "", row["operands"])
            if row["mnemonic"] == "l32r" and row_index < usable_count:
                model = l32r_addresses(memory_window(segments, row["address"], 3), row["address"], litbase)
                for kind in ("pc_relative", "hypothesis_literal"):
                    address = model.get(kind + "_address")
                    if address is None:
                        continue
                    try:
                        word = memory_window(segments, address, 4)
                        model[kind + "_mapped_word_le"] = int.from_bytes(word, "little")
                    except ValueError:
                        model[kind + "_unmapped"] = True
                row["literal_model"] = model
    return {"schema_version": 1, "module_sha256": MODULE_SHA256,
            "container_sha256": metadata["container_sha256"], "role": role, "tool": tool,
            "limits": ["Linear bounded windows, not proven function extents or control-flow coverage.",
                       "Stop semantic analysis at returns/unresolved edges; trailing rows can be data or misaligned.",
                       "ESP32 common ISA, not exact QCA core qualification.",
                       "Caller-supplied LITBASE hypothesis is NOT measured register state.",
                       "Synthetic ELF wrapper symbol names were removed; addresses retain original target VMAs."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument("--role", choices=("ptp", "ptmp_ap", "ptmp_sta"), required=True)
    parser.add_argument("--address", action="append", type=lambda x: int(x, 0), required=True)
    parser.add_argument("--size", type=int, default=128)
    parser.add_argument("--esp-prefix", required=True)
    parser.add_argument("--litbase-hypothesis", type=lambda x: int(x, 0))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = trace(args.module, args.role, args.address, args.size, args.esp_prefix, args.litbase_hypothesis)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
