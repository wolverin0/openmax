"""Tests for PB-010: Static Firmware/Module Symbol, WMI/HTT Dispatch & rx_ppdu_end Strip-Site Map."""

from __future__ import annotations

import json
from tools.qca988x.wmi_htt_strip_site_mapper import (
    DEFAULT_OUTPUT_PATH,
    build_pb_010_strip_map_report,
)


def test_pb_010_wmi_opcodes_mapped_across_host_and_target() -> None:
    report = build_pb_010_strip_map_report()
    assert report["gate_id"] == "PB-010"
    assert report["status"] == "PASSED"

    opcodes = report["wmi_dispatch_map"]["opcodes"]
    for op in ("0x9064", "0x9070", "0x9044", "0x9045", "0x901f"):
        assert op in opcodes

    # Verify 0x9064 (WMI_UBNT_POLL_CMDID) in host & target
    op_9064 = opcodes["0x9064"]
    assert op_9064["symbolic_name"] == "WMI_UBNT_POLL_CMDID"
    assert op_9064["payload_size_bytes"] == 1024
    ap_9064 = op_9064["target_dispatch"]["athwlan_AR9888v2_ptmp_ap_bin"]
    assert ap_9064["target_virtual_address"] == "0x0040fbcc"
    assert ap_9064["has_ubnt_oui_002722_constant"] is True
    assert len(ap_9064["nearby_iram_handlers"]) >= 3

    # Verify 0x9044 (WMI_PEER_RATE_RETRY_SCHED_CMDID) in host & target
    op_9044 = opcodes["0x9044"]
    assert op_9044["symbolic_name"] == "WMI_PEER_RATE_RETRY_SCHED_CMDID"
    assert op_9044["payload_size_bytes"] == 188
    ap_9044 = op_9044["target_dispatch"]["athwlan_AR9888v2_ptmp_ap_bin"]
    assert ap_9044["target_virtual_address"] == "0x00980e1c"
    assert "0x009a974c" in ap_9044["nearby_iram_handlers"]


def test_pb_010_htt_rx_ring_offsets_and_strip_sites() -> None:
    report = build_pb_010_strip_map_report()
    htt = report["htt_rx_strip_pipeline"]
    cfg = htt["htt_rx_ring_cfg_function"]
    assert cfg["name"] == "htt_h2t_rx_ring_cfg_msg_ll"
    assert cfg["programmed_dword_offsets"]["rx_ppdu_start_dword"] == 46
    assert cfg["programmed_dword_offsets"]["rx_ppdu_end_dword"] == 62
    assert cfg["programmed_byte_offsets"]["rx_ppdu_end_byte_offset"] == 248

    strip_sites = htt["strip_sites"]
    assert len(strip_sites) == 3
    export_spec = htt["pre_strip_export_design"]
    assert export_spec["captured_size_bytes"] == 40
    field_names = [f["name"] for f in export_spec["captured_fields"]]
    assert "Word19_txbf_h_info_flags" in field_names
    assert "Word20_bb_captured_channel_flags" in field_names
    assert "Word21_bb_length_ppdu_done" in field_names


def test_pb_010_saved_json_artifact_matches_builder() -> None:
    assert DEFAULT_OUTPUT_PATH.exists()
    disk_data = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    assert disk_data["gate_id"] == "PB-010"
    assert "WMI_UBNT_POLL_CMDID" in disk_data["wmi_dispatch_map"]["rodata_wmi_labels"]
    assert "WMI_PEER_RATE_RETRY_SCHED_CMDID" in disk_data["wmi_dispatch_map"]["rodata_wmi_labels"]
