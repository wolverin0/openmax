"""Tests for PB-011: QCA988x SGMT/Xtensa Container Parser, Load-Address/Checksum Verifier & Roundtrip Inspector."""

from __future__ import annotations

import json
from tools.qca988x.sgmt_container_inspector import (
    DEFAULT_OUTPUT_PATH,
    EMBEDDED_FIRMWARE_SYMBOLS,
    build_pb_011_sgmt_audit_report,
    build_valid_sgmt_container,
    parse_sgmt_container,
)


def test_pb_011_all_wa_and_xc_sgmt_containers_parse_with_exact_eof_match() -> None:
    report = build_pb_011_sgmt_audit_report()
    assert report["gate_id"] == "PB-011"
    assert report["status"] == "PASSED"

    for plat in ("WA.v8.7.25", "XC.v8.7.25"):
        plat_data = report["platforms"][plat]
        board = plat_data["board_raw_data_verification"]
        assert board["size_bytes"] == 2116
        assert board["header_length_field"] == 2116
        assert board["xor_16bit_accumulator_hex"] == "0xffff"
        assert board["passes_ol_transfer_bin_file_xor_gate"] is True

        for sym_name in EMBEDDED_FIRMWARE_SYMBOLS:
            sgmt = plat_data["sgmt_containers"][sym_name]
            assert sgmt["magic"] == "SGMT"
            assert sgmt["version"] == 1
            assert sgmt["exact_eof_match"] is True
            assert sgmt["trailing_unparsed_bytes"] == 0
            assert sgmt["entry_point_address"] == "0x00983c00"
            assert sgmt["has_end_sentinel"] is True
            assert sgmt["has_cryptographic_signature_trailer"] is False
            data_segs = [r for r in sgmt["records"] if r["record_type"] == "DATA_SEGMENT"]
            assert len(data_segs) == 4
            assert data_segs[0]["target_address"] == "0x00980000"
            assert data_segs[1]["target_address"] == "0x0040b000"
            assert data_segs[3]["target_address"] == "0x00983c00"


def test_pb_011_sgmt_roundtrip_builder_and_parser() -> None:
    seg_iram = b"\x00\x98\x2b\x40" * 64
    seg_dram = b"UBNT_POLL_MEM_ALLOC\x00" * 32
    container = build_valid_sgmt_container(
        segments=[(0x00980000, seg_iram), (0x0040B000, seg_dram)],
        entry_point=0x00983C00,
    )
    parsed = parse_sgmt_container(container)
    assert parsed["exact_eof_match"] is True
    assert parsed["entry_point_address"] == "0x00983c00"
    assert parsed["total_uncompressed_bytes"] == len(seg_iram) + len(seg_dram)


def test_pb_011_saved_json_artifact_exists_and_is_complete() -> None:
    assert DEFAULT_OUTPUT_PATH.exists()
    data = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    assert data["gate_id"] == "PB-011"
    assert "WA.v8.7.25" in data["platforms"]
    assert "XC.v8.7.25" in data["platforms"]
