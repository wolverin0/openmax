"""Offline common-Xtensa decoder qualification; proprietary bytes remain in RAM.

Uses local WSL tools with anonymous memfd files. Never executes target code,
installs tools, contacts a radio, or equates ESP32 configuration with QCA988x.
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
from tools.research.sgmt import decode_sgmt_memory

ESP_ARCHIVE_SHA256 = "8ef14e0409c2011b41e504a30f70d3e35287313a795d1f2462ad2cd0e2052d37"
ESP_ARCHIVE_URL = "https://github.com/espressif/crosstool-NG/releases/download/esp-2021r2-patch5/xtensa-esp32-elf-gcc8_4_0-esp-2021r2-patch5-linux-amd64.tar.gz"
MANIFEST_URL = "https://raw.githubusercontent.com/espressif/esp-idf/v4.4.8/tools/tools.json"
MODULE_SHA256 = "46525dc6f8b789bf820f0713841a2a9ecdcba833300ddb1ab1ef06fc4ab6a9c5"
CANDIDATES = {"ptmp_ap": 0x9B0620, "ptmp_sta": 0x9B064C, "ptp": 0x9AFE18}
INDEX_CANDIDATES = {"ptmp_ap": {23: 0x9B1604, 30: 0x9B1EEC},
                    "ptmp_sta": {23: 0x9B1694, 30: 0x9B2068},
                    "ptp": {23: 0x9B0884, 30: 0x9B10DC}}


def memory_window(segments: list[tuple[int, bytes]], address: int, size: int) -> bytes:
    """Bounded, exact last-write-wins lookup; never fill unmapped gaps."""
    if type(address) is not int or type(size) is not int or not 1 <= size <= 256:
        raise ValueError("expected address and 1..256-byte window")
    if address < 0 or address + size > 0x100000000:
        raise ValueError("address range overflow")
    result = bytearray()
    for current in range(address, address + size):
        for start, data in reversed(segments):
            if start <= current < start + len(data):
                result.append(data[current - start])
                break
        else:
            raise ValueError(f"unmapped address {current:#x}")
    return bytes(result)


def parse_disassembly(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        match = re.match(r"\s*([0-9a-f]+):\s+([0-9a-f]+)\s+([a-z.][a-z0-9_.]*)(?:\s+(.*))?$", line)
        if match:
            rows.append({"address": int(match[1], 16), "mnemonic": match[3],
                         "byte_length": len(match[2]) // 2,
                         "operands": (match[4] or "").strip()})
    return rows


def assess_window(text: str, address: int, size: int, returncode: int) -> dict:
    """Validate syntax coverage, never function boundaries or execution semantics.

    Unknown/unparsed/gapped output prevents enrichment beyond its valid prefix.
    Any unparsed address line invalidates the whole prefix because its position
    in the parsed list is not reliable. Failure receipts remain available.
    """
    rows = parse_disassembly(text)
    lines = [line for line in text.splitlines() if re.match(r"\s*[0-9a-f]+:\s", line)]
    unparsed = len(lines) - len(rows)
    cursor = address
    valid_prefix = []
    stop_reason = "decoder_failed" if returncode else "unparsed_rows" if unparsed else None
    for row in rows:
        if stop_reason is not None:
            break
        if row["address"] != cursor or row["byte_length"] <= 0 or cursor + row["byte_length"] > address + size:
            stop_reason = "noncontiguous_or_out_of_range"
            break
        if row["mnemonic"].startswith(".") or row["mnemonic"] in ("ill", "excw"):
            stop_reason = "unknown_or_illegal_instruction"
            break
        valid_prefix.append(row["address"])
        cursor += row["byte_length"]
    if stop_reason is None and cursor != address + size:
        stop_reason = "incomplete_window"
    return {"instructions": rows, "unparsed_instruction_line_count": unparsed,
            "syntax_prefix_addresses": valid_prefix, "syntax_prefix_end": cursor,
            "syntax_coverage_only": stop_reason is None,
            "syntax_stop_reason": stop_reason,
            "limits": "Syntax only, not control-flow reachability or semantic qualification."}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_windows(module: Path) -> list[dict]:
    if module.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("module exceeds 64 MiB limit")
    raw = module.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MODULE_SHA256:
        raise ValueError("module differs from pinned airOS 8.5.12 profile")
    elf = ELFFile(io.BytesIO(raw))
    table = elf.get_section_by_name(".symtab")
    if table is None or elf.header["e_type"] != "ET_REL":
        raise ValueError("expected symbol-bearing ET_REL module")
    symbols = {symbol.name: symbol for symbol in table.iter_symbols()}
    windows = []
    for role, candidate in CANDIDATES.items():
        symbol = symbols[f"athwlan_AR9888v2_{role}_bin"]
        section = elf.get_section(symbol["st_shndx"])
        start, size = symbol["st_value"], symbol["st_size"]
        if section["sh_type"] == "SHT_NOBITS" or start + size > len(section.data()):
            raise ValueError("embedded blob is not file-backed")
        blob = section.data()[start:start + size]
        metadata, segments = decode_sgmt_memory(blob)
        if any(record["kind"] == "EXEC" for record in metadata["records"]):
            raise ValueError("EXEC records require explicit intermediate-load context")
        anchors = [("beginaddr", 0x983C00), ("command_adjacent_pointer_candidate", candidate)]
        anchors.extend((f"subtype_index_{index}_pointer_candidate", address)
                       for index, address in INDEX_CANDIDATES[role].items())
        for kind, address in anchors:
            data = memory_window(segments, address, 128)
            windows.append({"role": role, "kind": kind, "address": address,
                            "window_size": len(data),
                            "container_sha256": metadata["container_sha256"],
                            "window_sha256": hashlib.sha256(data).hexdigest(),
                            "bytes_hex": data.hex()})
    return windows


# This script is fed to WSL Python via stdin, never saved. Anonymous file
# descriptors hold synthetic objects and bounded proprietary input windows.
REMOTE_SCRIPT = r'''
import hashlib,json,os,subprocess
request=REQUEST
def run(args, **kwargs):
    p=subprocess.run(args,capture_output=True,text=True,timeout=20,**kwargs)
    return p
def anon(data=b''):
    fd=os.memfd_create('fmx-decoder');os.write(fd,data);return fd
tools=[]
for tool in request['tools']:
    objdump=tool['prefix']+'objdump';assembler=tool['prefix']+'as';objcopy=tool['prefix']+'objcopy'
    metadata={'name':tool['name'],'objdump_sha256':hashlib.sha256(open(objdump,'rb').read()).hexdigest(),
              'assembler_sha256':hashlib.sha256(open(assembler,'rb').read()).hexdigest(),
              'version':run([objdump,'--version']).stdout.splitlines()[0],'probes':[],'windows':[]}
    for family,source in [('entry','entry a1,48'),('callx8','callx8 a8'),('loopnez','loopnez a11,1f\nnop\n1: nop')]:
        fd=anon()
        try:
            p=run([assembler,'-o','/proc/self/fd/'+str(fd)],input='.begin no-transform\n'+source+'\n.end no-transform\n',pass_fds=(fd,))
            row={'family':family,'returncode':p.returncode,'error':p.stderr.strip()}
            if p.returncode==0:
                d=run([objdump,'-d','/proc/self/fd/'+str(fd)],pass_fds=(fd,))
                row['disassembly']=d.stdout;row['decode_returncode']=d.returncode
            metadata['probes'].append(row)
        finally: os.close(fd)
    for window in request['windows']:
        fd=anon(bytes.fromhex(window['bytes_hex']))
        wrapper=anon()
        try:
            row={k:v for k,v in window.items() if k!='bytes_hex'}
            if tool['name']=='ESP32':
                wrapping=run([objcopy,'-I','binary','-O','elf32-xtensa-le','-B','xtensa',
                              '--change-section-vma','.data='+hex(window['address']),
                              '--set-section-flags','.data=alloc,load,readonly,code,contents',
                              '/proc/self/fd/'+str(fd),'/proc/self/fd/'+str(wrapper)],pass_fds=(fd,wrapper))
                if wrapping.returncode:
                    raise RuntimeError('ELF wrapper failed: '+wrapping.stderr)
                row['decode_route']='anonymous ELF32 little-endian wrapper; not original ELF metadata'
                p=run([objdump,'-d','/proc/self/fd/'+str(wrapper)],pass_fds=(wrapper,))
            else:
                row['decode_route']='anonymous raw binary'
                p=run([objdump,'-D','-b','binary','-m','xtensa','--adjust-vma='+hex(window['address']),'/proc/self/fd/'+str(fd)],pass_fds=(fd,))
            row.update({'returncode':p.returncode,'error':p.stderr.strip(),'disassembly':p.stdout})
            metadata['windows'].append(row)
        finally: os.close(fd);os.close(wrapper)
    tools.append(metadata)
print(json.dumps(tools))
'''


def qualify(module: Path, archive: Path, lx_prefix: str, esp_prefix: str) -> dict:
    if file_hash(archive) != ESP_ARCHIVE_SHA256:
        raise ValueError("official tool archive hash mismatch")
    request = {"tools": [{"name": "LX106", "prefix": lx_prefix},
                         {"name": "ESP32", "prefix": esp_prefix}],
               "windows": source_windows(module)}
    remote = REMOTE_SCRIPT.replace("request=REQUEST", "request=" + repr(request), 1)
    result = subprocess.run(["wsl", "-e", "python3", "-"], input=remote,
                            capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise ValueError("WSL qualification failed: " + result.stderr)
    tools = json.loads(result.stdout)
    for tool in tools:
        for probe in tool["probes"]:
            if "disassembly" in probe:
                probe["instructions"] = parse_disassembly(probe.pop("disassembly"))
            probe["family_roundtrip"] = (probe["returncode"] == 0
                                          and probe.get("decode_returncode") == 0
                                          and any(i["mnemonic"] == probe["family"]
                                                  for i in probe.get("instructions", [])))
        for window in tool["windows"]:
            disassembly = window.pop("disassembly")
            window.update(assess_window(disassembly, window["address"], window["window_size"], window["returncode"]))
            window["parsed_bytes"] = sum(i["byte_length"] for i in window["instructions"])
            window["unknown_directive_addresses"] = [i["address"] for i in window["instructions"]
                                                     if i["mnemonic"].startswith(".")]
            window["excw_addresses"] = [i["address"] for i in window["instructions"]
                                         if i["mnemonic"] == "excw"]
    result = {"schema_version": 1, "status": "COMMON_ISA_ONLY_EXACT_CORE_UNQUALIFIED",
            "module_sha256": MODULE_SHA256, "archive_sha256": ESP_ARCHIVE_SHA256,
            "archive_url": ESP_ARCHIVE_URL, "manifest_url": MANIFEST_URL, "tools": tools,
            "limits": ["Synthetic family probes are not hardware execution.",
                       "ESP32 ISA is not the QCA988x configuration or custom extensions; syntactic coverage is not semantic qualification.",
                       "Adjacent command/pointer values do not prove a command handler.",
                       "L32R targets require LITBASE/ROM/alias context; printed PC-relative values are candidates.",
                       "No execution, control-flow completeness, timing or ath10k compatibility proof."]}
    prior = Path("research/raw/xtensa-qualification-20261006.json")
    if prior.exists():
        result["failed_raw_route_evidence"] = {
            "path": prior.as_posix(), "sha256": file_hash(prior),
            "limits": "Original ESP32 raw-binary route returned -11; retained, not rerun by the ELF route."}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", required=True, type=Path)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--lx-prefix", required=True)
    parser.add_argument("--esp-prefix", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = qualify(args.module, args.archive, args.lx_prefix, args.esp_prefix)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
