"""Unit tests for Stage 17 PB-010 & PB-011 Xtensa Target Binary, BMI Segment/Signature,
and WMI/HTT + Hardware Descriptor Extractor (`T-PB-010-011-XTENSA-WMI-HTT-MAP`).
"""

from __future__ import annotations

import json
from pathlib import Path

from analysis.pb010_011_xtensa_wmi_htt_extractor import (
    DEFAULT_ARTIFACT_OUT,
    build_pb010_011_report,
    extract_ground_up_target_bypass_variables,
    extract_pb010_wmi_htt_dispatch_map,
    extract_pb011_xtensa_sgmt_bmi_boundary,
)


def test_pb011_sgmt_and_bmi_signature_boundary() -> None:
    pb011 = extract_pb011_xtensa_sgmt_bmi_boundary()
    assert pb011["boundary_id"] == "PB-011"
    assert pb011["certainty"] == "CONFIRMED"

    sig_assess = pb011["bmi_protocol_and_signature_boundary"]["cryptographic_signature_assessment"]
    assert sig_assess["classification"] == "PLAIN_BMI_LZ_LOAD_NO_CRYPTO_SIGNATURE_IN_SGMT_CONTAINER"

    images = pb011["target_images"]
    assert set(images.keys()) == {
        "athwlan_AR9888v2_ptmp_ap_bin",
        "athwlan_AR9888v2_ptmp_sta_bin",
        "athwlan_AR9888v2_ptp_bin",
    }

    ap = images["athwlan_AR9888v2_ptmp_ap_bin"]
    assert ap["container_size_bytes"] == 251681
    assert ap["consumed_bytes"] == 251681
    assert ap["trailing_unconsumed_signature_bytes"] == 0
    assert ap["entry_point_beginaddr_hex"] == "0x00983c00"
    assert ap["done_record_present"] is True
    assert ap["payload_segment_count"] == 4
    assert ap["total_decoded_bytes"] == 309464
    assert ap["wmi_0x9064_literal_hits"][0]["target_addr_hex"] == "0x0040fb54"

    dests = [seg["destination_hex"] for seg in ap["payload_segments"]]
    assert dests == ["0x00980000", "0x0040b000", "0x0040d140", "0x00983c00"]


def test_pb010_wmi_and_htt_dispatch_boundary() -> None:
    pb010 = extract_pb010_wmi_htt_dispatch_map()
    assert pb010["boundary_id"] == "PB-010"
    assert pb010["certainty"] == "CONFIRMED"

    wmi = pb010["wmi_dispatch_boundary"]
    assert "0x9064" in wmi["wmi_10x_core_command_opcodes"]["WMI_UBNT_POLL_HT_COMM_CMDID"]
    assert "0x9044" in wmi["wmi_10x_core_command_opcodes"]["WMI_10X_PEER_RATE_RETRY_SCHED_CMDID"]

    ubnt_tunnel = wmi["ubiquiti_proprietary_wmi_tunnel"]
    consumer = ubnt_tunnel["target_xtensa_consumer_ptmp_ap"]
    assert consumer["command_literal_addr_hex"] == "0x0040fb54"
    assert consumer["branch_table_base_addr_hex"] == "0x009b2037"
    assert consumer["branch_table_entries"] == 51
    assert (
        consumer["representative_submessage_handlers"]["type_0x17_set_txq_param"][
            "target_handler_addr_hex"
        ]
        == "0x009b5c02"
    )

    htt = pb010["htt_and_hw_descriptor_boundary"]
    assert htt["htt_10x_t2h_msg_types"]["HTT_10X_T2H_MSG_TYPE_RX_IND"] == "0x01"
    rx_end = htt["rx_ppdu_end_qca988x_descriptor"]
    assert rx_end["total_bytes"] == 84
    assert "bb_captured_channel" in rx_end["fields"]
    assert "txbf_h_info" in rx_end["fields"]
    assert "locationing_timestamp" in rx_end["fields"]

    tx_start = htt["tx_ppdu_start_qca988x_descriptor"]
    assert tx_start["total_bytes"] == 84
    assert "bb_capture_channel" in tx_start["fields"]
    assert "cv_ptr" in tx_start["fields"]

    series_bw = htt["series_bw_hardware_rate_table"]
    assert series_bw["total_bytes"] == 16
    assert "ldpc" in series_bw["fields"]
    assert "stbc" in series_bw["fields"]
    assert "sgi" in series_bw["fields"]


def test_ground_up_target_bypass_variables_and_artifact() -> None:
    vars_list = extract_ground_up_target_bypass_variables()
    pb_ids = [v["pb_id"] for v in vars_list]
    assert pb_ids == ["PB-021", "PB-030", "PB-031", "PB-050"]

    assert DEFAULT_ARTIFACT_OUT.exists()
    persisted = json.loads(DEFAULT_ARTIFACT_OUT.read_text(encoding="utf-8"))
    report = build_pb010_011_report()
    assert persisted["summary_verdict"] == report["summary_verdict"]
    assert (
        persisted["summary_verdict"]["total_Trailing_signature_bytes_across_all_sgmt_images"] == 0
    )
    assert Path("docs/STAGE17_PB010_011_XTENSA_TARGET_AND_WMI_MAP.md").exists()
