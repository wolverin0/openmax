"""Offline decoder for two statically observed airOS 8.5.12 host message layouts.

Not an over-air decoder, packet generator, ath10k adapter, or device control tool.
Input is either the serializer buffer or its dword-swapped host WMI buffer.
Field meanings not established from code are deliberately positional.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

MODULE_SHA256 = "19f379b1a776603634e367d547eaabed20f705865cacaaef06193ac04bb70e14"
COMMAND_ID = 0x9064
LAYOUT_LENGTHS = {0x17: 20, 0x1E: 14}


def decode(data: bytes, *, command_id: int, buffer_stage: str) -> dict:
    if command_id != COMMAND_ID:
        raise ValueError("not the observed airOS command ID; do not translate ath10k IDs")
    if not 9 <= len(data) <= 1024:
        raise ValueError("buffer length must be 9..1024 bytes")
    if buffer_stage == "host-wmi-buffer":
        if len(data) % 4:
            raise ValueError("host WMI buffer must be dword aligned")
        payload = b"".join(data[i:i + 4][::-1] for i in range(0, len(data), 4))
    elif buffer_stage == "serializer-buffer":
        payload = data
    else:
        raise ValueError("explicit known buffer stage required")
    word, opaque_byte, message_type, opaque_halfword = struct.unpack(">IBHH", payload[:9])
    if word != 1:
        raise ValueError("unsupported header word; this decoder is build-specific")
    if message_type not in LAYOUT_LENGTHS:
        raise ValueError("message type not yet verified")
    logical_length = LAYOUT_LENGTHS[message_type]
    expected_length = ((logical_length + 3) & ~3
                       if buffer_stage == "host-wmi-buffer" else logical_length)
    if len(payload) != expected_length:
        raise ValueError("length disagrees with verified message layout")
    if any(payload[logical_length:]):
        raise ValueError("nonzero alignment padding")
    body = payload[9:logical_length]
    if message_type == 0x17:
        values = struct.unpack(">BHHHI", body)
        fields = dict(zip(("u8_0", "u16_0", "u16_1", "u16_2", "u32_0"), values))
    else:
        fields = {f"u8_{index}": value for index, value in enumerate(body)}
    return {
        "schema_version": 1,
        "profile_module_sha256": MODULE_SHA256,
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "buffer_stage": buffer_stage, "command_id": command_id,
        "message_type": message_type, "logical_length": logical_length,
        "header_word": word, "opaque_header_byte": opaque_byte,
        "opaque_header_halfword": opaque_halfword, "fields": fields,
        "limits": "Build-specific static layout; field semantics and target behavior unverified; no ath10k compatibility implied.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--command-id", type=lambda s: int(s, 0), required=True)
    parser.add_argument("--buffer-stage", choices=("serializer-buffer", "host-wmi-buffer"), required=True)
    args = parser.parse_args()
    if args.input.stat().st_size > 1024:
        parser.error("input exceeds 1024 bytes")
    print(json.dumps(decode(args.input.read_bytes(), command_id=args.command_id,
                            buffer_stage=args.buffer_stage), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
