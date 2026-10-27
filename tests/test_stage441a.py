#!/usr/bin/env python3
"""Pytest suite for Stage 441A — Xtensa WMI 0x9064 Jump Table & Polling Hook Composer."""

from __future__ import annotations

import json

from tools.firmware.build_stage441a_xtensa_wmi_0x9064_polling_hook_composer import (
    ARTIFACT_OUT,
    DOC_OUT,
    build_stage441a,
)


def test_stage441a_wmi_0x9064_and_iram_composer() -> None:
    report = build_stage441a()
    assert ARTIFACT_OUT.exists()
    assert DOC_OUT.exists()
    loaded = json.loads(ARTIFACT_OUT.read_text(encoding="utf-8"))
    assert loaded["stage"] == "441A"
    assert loaded["memory_master_claim_id"] == "mm-831f"
    val = loaded["decompressed_sgmt_validation"]
    assert val["openwrt_qca988x_hw20_firmware_2_ct_bin"]["ie3_contains_0x009b2037"] is True
    assert val["openwrt_qca988x_hw20_firmware_2_ct_bin"]["ie3_contains_0x009b5c02"] is True
    assert val["openwrt_qca988x_hw20_firmware_2_ct_bin"]["ie4_contains_0x0040f688"] is True
    assert val["athwlan_AR9888v2_ptmp_ap_bin"]["wmi_0x9064_opcode_value_hex"] == "0x00009064"
    assert val["athwlan_AR9888v2_ptmp_ap_bin"]["words_at_0x0040f688_count"] == 32
    ring = report["iram_station_queue_telemetry_descriptors"]
    assert ring["station_slots"] == 32
    assert ring["total_ring_bytes"] == 512
    assert len(ring["descriptors"]) == 32
