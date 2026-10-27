from __future__ import annotations

import json
import math
import struct
from pathlib import Path

import pytest

from tools.qca988x.memory_diff_analyzer import (
    QCA988X_DRAM_ADDR,
    QCA988X_HOST_INTEREST_ADDR,
    analyze_memory_snapshots,
    build_synthetic_dram_and_channel_dump_fixture_report,
    decode_host_interest_table,
    evaluate_channel_dump_packing_hypotheses,
    is_target_dram_pointer,
    is_target_rom_pointer,
    synthesize_10bit_channel_dump_blob,
    validate_four_byte_alignment,
    write_memory_diff_fixture_report_json,
)


def test_four_byte_alignment_validation() -> None:
    validate_four_byte_alignment(0x00400000, b"\x00" * 16)
    with pytest.raises(ValueError, match="4-byte CE diagnostic alignment"):
        validate_four_byte_alignment(0x00400002, b"\x00" * 16)
    with pytest.raises(ValueError, match="multiple of 4 bytes"):
        validate_four_byte_alignment(0x00400000, b"\x00" * 14)


def test_target_dram_and_rom_pointer_classifiers() -> None:
    assert is_target_dram_pointer(0x00400800) is True
    assert is_target_dram_pointer(0x0044FFFC) is True
    assert is_target_dram_pointer(0x00400802) is False  # unaligned
    assert is_target_dram_pointer(0x00450000) is False  # out of range

    assert is_target_rom_pointer(0x00940100) is True
    assert is_target_rom_pointer(0x00400800) is False


def test_host_interest_table_decoder() -> None:
    buf = bytearray(0x1000)
    hi_off = QCA988X_HOST_INTEREST_ADDR - QCA988X_DRAM_ADDR
    struct.pack_into("<I", buf, hi_off + 0x1C, 0x00404000)  # hi_board_data
    struct.pack_into("<I", buf, hi_off + 0x20, 1)           # hi_board_data_initialized
    decoded = decode_host_interest_table(bytes(buf), base_address=QCA988X_DRAM_ADDR)
    assert decoded["covered_by_snapshot"] is True
    assert decoded["fields"]["hi_board_data"]["value_hex"] == "0x00404000"
    assert decoded["fields"]["hi_board_data"]["is_dram_pointer"] is True
    assert decoded["fields"]["hi_board_data_initialized"]["value_int"] == 1


def test_channel_dump_packing_hypotheses_discriminate_10bit_vs_12bit() -> None:
    # 1. Test 10-bit signed I/Q 56-tone VHT20 synthetic dump
    blob_10 = synthesize_10bit_channel_dump_blob(num_tones=56)
    res_10 = evaluate_channel_dump_packing_hypotheses(blob_10)
    assert res_10["winning_hypothesis_id"] == "H_10BIT_IQ_WORD32"
    assert res_10["matched_ofdm_bandwidth_mode"] == "HT20_VHT20_56"
    assert res_10["winning_confidence_score"] > 0.90

    # 2. Synthesize a 12-bit signed I/Q 114-tone VHT40 dump with amplitudes > 512 (exceeding 10-bit)
    words_12 = []
    for k in range(114):
        amp = 1400.0
        phi = 0.1 + k * 0.15
        i_val = int(round(amp * math.cos(phi)))
        q_val = int(round(amp * math.sin(phi)))
        w = (i_val & 0xFFF) | ((q_val & 0xFFF) << 12)
        words_12.append(w)
    blob_12 = struct.pack(f"<{len(words_12)}I", *words_12)
    res_12 = evaluate_channel_dump_packing_hypotheses(blob_12)
    assert res_12["winning_hypothesis_id"] == "H_12BIT_IQ_WORD32"
    assert res_12["matched_ofdm_bandwidth_mode"] == "VHT40_114"
    assert res_12["winning_confidence_score"] > 0.90


def test_full_synthetic_dram_and_channel_dump_fixture_report(tmp_path: Path) -> None:
    out_file = tmp_path / "memory_diff_fixture_report.json"
    rep = write_memory_diff_fixture_report_json(out_file)
    assert out_file.exists()

    loaded = json.loads(out_file.read_text(encoding="utf-8"))
    assert loaded["live_devices_touched"] is False
    assert loaded["task_id"] == "T-PB-GEM2-03"

    regions = loaded["memory_diff_analysis"]["regions"]
    assert len(regions) == 4
    classifications = [r["classification"] for r in regions]
    assert classifications == [
        "HOST_INTEREST_TABLE",
        "MONOTONIC_COUNTER_BLOCK",
        "TARGET_DRAM_POINTER_RING",
        "PACKET_CORRELATED_DESCRIPTOR_OR_CSI_BUFFER",
    ]
    assert rep["channel_dump_packing_analysis"]["winning_hypothesis_id"] == "H_10BIT_IQ_WORD32"
