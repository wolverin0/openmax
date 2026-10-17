"""Bounded offline SGMT parser; metadata by default, optional in-memory analysis.

Format: https://android.googlesource.com/kernel/msm/+/android-7.1.0_r0.2/drivers/staging/qcacld-2.0/CORE/SERVICES/COMMON/bmi_msg.h
Codec ancestor: https://raw.githubusercontent.com/mbitsnbites/bcl/master/src/lz.c
The independently implemented marker/base128 hypothesis matches three observed
airOS 8.5.12 containers structurally; this is NOT proof of ROM implementation,
code/data classification, execution, hardware behavior or timing authority.
"""
from __future__ import annotations

import hashlib
import struct

MAGIC = 0x544D4753
MAX_OUTPUT = 8 * 1024 * 1024
MAX_INPUT = 16 * 1024 * 1024
MAX_RECORDS = 128
SPECIALS = {0xFFFFFFFF: "DONE", 0xFFFFFFFD: "BEGINADDR", 0xFFFFFFFC: "EXEC"}


def _fail(reason: str, offset: int) -> None:
    raise ValueError(f"{reason}; offset={offset}")


def _varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    for _ in range(5):
        if offset >= len(data):
            _fail("truncated varint", offset)
        byte = data[offset]
        offset += 1
        value = (value << 7) | (byte & 127)
        if value > 0xFFFFFFFF:
            _fail("varint overflow", offset - 1)
        if not byte & 128:
            return value, offset
    _fail("varint too long", offset)


def _decode_segment(data: bytes, offset: int, size: int) -> tuple[int, bytes]:
    if offset >= len(data):
        _fail("missing marker", offset)
    marker = data[offset]
    offset += 1
    output = bytearray()
    while len(output) < size:
        token_offset = offset
        if offset >= len(data):
            _fail("truncated token", offset)
        byte = data[offset]
        offset += 1
        if byte != marker:
            output.append(byte)
            continue
        if offset >= len(data):
            _fail("truncated escape", offset)
        if data[offset] == 0:
            output.append(marker)
            offset += 1
            continue
        length, offset = _varint(data, offset)
        distance, offset = _varint(data, offset)
        if not length or not 0 < distance <= len(output):
            _fail("invalid back-reference", token_offset)
        if length > size - len(output):
            _fail("decoded length overrun", token_offset)
        # Bytewise copying deliberately allows overlapping LZ back-references.
        for _ in range(length):
            output.append(output[-distance])
    return offset, bytes(output)


def parse_sgmt(data: bytes) -> dict:
    """Return hashes/maps only, with exact DONE/full-consumption validation.

    Unknown flags and board-data records are rejected. Destination overlap is
    not rejected: SGMT may represent sequential patches, not disjoint sections.
    No decoded bytes are returned, saved, executed or transmitted.
    """
    return _parse_sgmt(data, keep_payloads=False)[0]


def decode_sgmt_memory(data: bytes) -> tuple[dict, list[tuple[int, bytes]]]:
    """Return validated metadata and ordered (destination, payload) pairs in RAM.

    Full container validation completes before any result is returned. Overlapping
    destinations preserve load order. This API performs no file or device I/O.
    Callers must not serialize proprietary payloads into research reports.
    """
    return _parse_sgmt(data, keep_payloads=True)


def _parse_sgmt(data: bytes, keep_payloads: bool) -> tuple[dict, list[tuple[int, bytes]]]:
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    if len(data) > MAX_INPUT:
        _fail("input limit exceeded", 0)
    if len(data) < 8:
        _fail("truncated file header", 0)
    magic, flags = struct.unpack_from("<II", data)
    if magic != MAGIC:
        _fail("invalid SGMT magic", 0)
    if flags not in (0, 1):
        _fail("unknown flags", 4)
    offset = 8
    total = 0
    records = []
    payloads = []
    for _ in range(MAX_RECORDS):
        metadata_offset = offset
        if offset + 8 > len(data):
            _fail("missing DONE or truncated metadata", offset)
        address, length = struct.unpack_from("<II", data, offset)
        offset += 8
        if length in SPECIALS:
            kind = SPECIALS[length]
            records.append({"metadata_offset": metadata_offset,
                            "destination": address, "kind": kind})
            if kind == "DONE":
                if offset != len(data):
                    _fail("trailing bytes", offset)
                return {"schema_version": 1, "file_flags": flags,
                        "container_size": len(data), "consumed_bytes": offset,
                        "container_sha256": hashlib.sha256(data).hexdigest(),
                        "decoded_total": total, "records": records,
                        "limits": "Observed codec compatibility only; no ROM, execution, code/data or hardware proof."}, payloads
            continue
        if length >= 0x80000000:
            _fail("unsupported special record (including BDDATA)", metadata_offset)
        if not length:
            _fail("zero-length payload unsupported", metadata_offset)
        if length > MAX_OUTPUT - total:
            _fail("decoded output limit exceeded", metadata_offset)
        if address + length > 0x100000000:
            _fail("destination range overflow", metadata_offset)
        input_offset = offset
        if flags == 1:
            offset, decoded = _decode_segment(data, offset, length)
        else:
            if length > len(data) - offset:
                _fail("truncated uncompressed payload", offset)
            decoded = data[offset:offset + length]
            offset += length
        digest = hashlib.sha256(decoded).hexdigest()
        if keep_payloads:
            payloads.append((address, decoded))
        total += length
        records.append({"metadata_offset": metadata_offset,
                        "input_offset": input_offset, "destination": address,
                        "kind": "PAYLOAD", "decoded_size": length,
                        "compressed_bytes": offset - input_offset if flags else 0,
                        "stored_bytes": offset - input_offset,
                        "decoded_sha256": digest})
    _fail("record count limit exceeded", offset)
