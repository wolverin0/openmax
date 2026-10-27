from __future__ import annotations

import json
from pathlib import Path

from tools.qca988x.extract_descriptor_map import (
    build_ar9888_v2_descriptor_map_report,
    build_bb_lc_reg_fields,
    build_rx_ppdu_end_fields,
    build_series_bw_fields,
    build_tx_ppdu_start_fields,
    parse_descriptor_header_text,
    unpack_evm_pilot_dword,
    write_ar9888_v2_descriptor_map_json,
)
from tools.qca988x.fetch_pinned_sources import (
    PINNED_SOURCE_CATALOG,
    build_pinned_source_manifest,
    get_pinned_source_by_id,
)


def test_pinned_sources_manifest_has_20_entries_and_exact_metadata() -> None:
    assert len(PINNED_SOURCE_CATALOG) == 20
    manifest = build_pinned_source_manifest(allow_network=False)
    assert manifest["total_sources"] == 20
    assert manifest["all_hashes_verified"] is True

    q11 = get_pinned_source_by_id("Q11")
    assert q11.path == "dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h"
    assert q11.expected_byte_length == 18324
    assert q11.expected_sha256 == "361640290ee3baea12a191c31d30394d70ab256bf558b3ed6b79bd56e6acbe8d"

    q12 = get_pinned_source_by_id("Q12")
    assert q12.path == "dl/include/AR9888/v2/hw/mac_descriptors/tx_ppdu_start.h"
    assert q12.expected_byte_length == 68192
    assert q12.expected_sha256 == "195f0c021ff639e5be4adc4727dfe1ea44ac4aaeb9ecfabf6d85a35f62c53d73"

    q13 = get_pinned_source_by_id("Q13")
    assert q13.path == "dl/include/AR9888/v2/hw/mac_descriptors/series_bw.h"
    assert q13.expected_byte_length == 20120
    assert q13.expected_sha256 == "49f8859e56320a902f9d5ae1e56a8fc16281659e1fedb8dc59a3883f354ff51b"

    q14 = get_pinned_source_by_id("Q14")
    assert q14.path == "dl/include/AR9888/v2/extra/hw/bb_lc_reg.h"
    assert q14.expected_byte_length == 869235
    assert q14.expected_sha256 == "5fbc077b66771a8865abdfe5eacb76e39451565b6208340bd2754101d793391f"


def test_parse_descriptor_header_defines_from_snippet() -> None:
    snippet = """
#define RX_PPDU_END_19_BB_CAPTURED_CHANNEL_OFFSET                    0x0000004c
#define RX_PPDU_END_19_BB_CAPTURED_CHANNEL_LSB                       25
#define RX_PPDU_END_19_BB_CAPTURED_CHANNEL_MASK                      0x02000000
"""
    parsed = parse_descriptor_header_text(
        header_text=snippet,
        descriptor_name="rx_ppdu_end",
        source_id="Q11",
        header_path="dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h",
    )
    assert len(parsed) == 1
    assert parsed[0].field_name == "bb_captured_channel"
    assert parsed[0].dword_index == 19
    assert parsed[0].byte_offset == 0x4C
    assert parsed[0].lsb == 25
    assert parsed[0].msb == 25
    assert parsed[0].mask_hex == "0x02000000"

    evm_unpacked = unpack_evm_pilot_dword(0xFEFD141E)
    assert evm_unpacked["stream0_signed_db"] == 30
    assert evm_unpacked["stream1_signed_db"] == 20
    assert evm_unpacked["stream2_signed_db"] == -3
    assert evm_unpacked["stream3_signed_db"] == -2


def test_rx_ppdu_end_exact_offsets_and_masks() -> None:
    payload = build_ar9888_v2_descriptor_map_report()
    rx_fields = {f["field_name"]: f for f in payload["descriptors"]["rx_ppdu_end"]["fields"]}
    assert payload["descriptors"]["rx_ppdu_end"]["num_dwords"] == 21
    assert payload["descriptors"]["rx_ppdu_end"]["size_bytes"] == 84
    assert len(rx_fields) == len(build_rx_ppdu_end_fields())

    # Check EVM pilot words 0..15
    for idx in range(16):
        evm = rx_fields[f"evm_p{idx}"]
        assert evm["dword_index"] == idx
        assert evm["byte_offset"] == idx * 4
        assert evm["mask_hex"] == "0xffffffff"

    # Check timestamps and locationing
    assert rx_fields["tsf_timestamp"]["byte_offset_hex"] == "0x00000040"
    assert rx_fields["wb_timestamp"]["byte_offset_hex"] == "0x00000044"

    loc_ts = rx_fields["locationing_timestamp"]
    assert loc_ts["byte_offset_hex"] == "0x00000048"
    assert loc_ts["lsb"] == 0
    assert loc_ts["msb"] == 7
    assert loc_ts["mask_hex"] == "0x000000ff"

    # Check txbf_h_info and bb_captured_channel and bb_length
    txbf = rx_fields["txbf_h_info"]
    assert txbf["dword_index"] == 18
    assert txbf["byte_offset_hex"] == "0x00000048"
    assert txbf["lsb"] == 18
    assert txbf["msb"] == 18
    assert txbf["mask_hex"] == "0x00040000"

    bb_cap = rx_fields["bb_captured_channel"]
    assert bb_cap["dword_index"] == 19
    assert bb_cap["byte_offset_hex"] == "0x0000004c"
    assert bb_cap["lsb"] == 25
    assert bb_cap["msb"] == 25
    assert bb_cap["mask_hex"] == "0x02000000"

    bb_len = rx_fields["bb_length"]
    assert bb_len["dword_index"] == 20
    assert bb_len["byte_offset_hex"] == "0x00000050"
    assert bb_len["lsb"] == 0
    assert bb_len["msb"] == 15
    assert bb_len["mask_hex"] == "0x0000ffff"


def test_tx_ppdu_start_and_series_bw_exact_offsets_and_masks() -> None:
    payload = build_ar9888_v2_descriptor_map_report()
    tx_fields = {f["field_name"]: f for f in payload["descriptors"]["tx_ppdu_start"]["fields"]}
    assert payload["descriptors"]["tx_ppdu_start"]["num_dwords"] == 55
    assert payload["descriptors"]["tx_ppdu_start"]["size_bytes"] == 220
    assert len(tx_fields) == len(build_tx_ppdu_start_fields())

    cv_ptr = tx_fields["cv_ptr"]
    assert cv_ptr["dword_index"] == 17
    assert cv_ptr["byte_offset_hex"] == "0x00000044"
    assert cv_ptr["mask_hex"] == "0xffffffff"

    bb_cap_tx = tx_fields["bb_capture_channel"]
    assert bb_cap_tx["dword_index"] == 19
    assert bb_cap_tx["byte_offset_hex"] == "0x0000004c"
    assert bb_cap_tx["lsb"] == 30
    assert bb_cap_tx["msb"] == 30
    assert bb_cap_tx["mask_hex"] == "0x40000000"

    cv_len = tx_fields["cv_len"]
    assert cv_len["dword_index"] == 20
    assert cv_len["byte_offset_hex"] == "0x00000050"
    assert cv_len["mask_hex"] == "0x0000ffff"

    sbw_fields = {f["field_name"]: f for f in payload["descriptors"]["series_bw"]["fields"]}
    assert payload["descriptors"]["series_bw"]["num_dwords"] == 4
    assert len(sbw_fields) == len(build_series_bw_fields())

    rate = sbw_fields["rate"]
    assert rate["dword_index"] == 1
    assert rate["byte_offset_hex"] == "0x00000004"
    assert rate["lsb"] == 24
    assert rate["msb"] == 27
    assert rate["mask_hex"] == "0x0f000000"
    assert "<legal:0-9>" in rate["legal_values"]


def test_bb_lc_reg_channel_dump_and_phy_registers(tmp_path: Path) -> None:
    out_file = tmp_path / "ar9888_v2_descriptor_map.json"
    write_ar9888_v2_descriptor_map_json(out_file)
    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["live_devices_touched"] is False
    regs = {
        f"{r['register_name']}.{r['field_name']}": r
        for r in data["baseband_registers"]["registers"]
    }
    assert len(regs) == len(build_bb_lc_reg_fields())

    b0 = regs["PHY_BB_CHAN_INFO_CHAN_TAB_B0.CHANINFO_WORD"]
    assert b0["address_hex"] == "0x00009b00"
    assert b0["mask_hex"] == "0xffffffff"

    b1 = regs["PHY_BB_CHAN_INFO_CHAN_TAB_B1.CHANINFO_WORD"]
    assert b1["address_hex"] == "0x0000ab00"
    assert b1["mask_hex"] == "0xffffffff"

    ctrl_cap = regs["PHY_BB_CHANINFO_CTRL.CAPTURE_CHAN_INFO"]
    assert ctrl_cap["address_hex"] == "0x0000a370"
    assert ctrl_cap["mask_hex"] == "0x00000001"

    ctrl_s2 = regs["PHY_BB_CHANINFO_CTRL.CHANINFOMEM_S2_READ"]
    assert ctrl_s2["address_hex"] == "0x0000a370"
    assert ctrl_s2["mask_hex"] == "0x00000008"

    prepend = regs["PHY_BB_FRAME_CONTROL.PREPEND_CHAN_INFO"]
    assert prepend["address_hex"] == "0x0000a238"
    assert prepend["mask_hex"] == "0x00010000"
