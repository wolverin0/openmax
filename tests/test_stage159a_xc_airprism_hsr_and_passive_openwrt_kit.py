#!/usr/bin/env python3
"""Unit & Binary Verification Suite for Stage 159A:
Passive XC 16-Board OpenWrt Kit & Active AirPrism/HSR Driver Audit (`ubnt_prism_hook` + `ubnt_prism_filters`
in `XC.v8.7.25` `umac.ko`, `ath_spectral_filter_init` in `ath_dev.ko`, `ubnt_poll_host_hsr_diag` in `ubnt_poll_host.ko`).
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage159a_xc_airprism_hsr_and_passive_openwrt_kit.json"
)


def test_stage159a_receipt_passes_5pillar_gate_and_binary_offsets():
    assert ARTIFACT_PATH.exists(), f"Missing {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "159A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_verification"]["pbe5ac_241_242_touched"] is False
    assert data["safety_verification"]["guarida_poe_switches_200_201_touched"] is False
    assert data["safety_verification"]["flash_writes_performed"] == 0

    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"

    bins = data["pillar_a_ground_up_re_and_knob_catalog"]["dissected_xc_binaries"]
    assert bins["umac_ko"]["ubnt_prism_hook_offset_hex"] == "0x0ac874"
    assert bins["umac_ko"]["ubnt_prism_hook_size_bytes"] == 468
    assert bins["umac_ko"]["ubnt_prism_filters_data_offset_hex"] == "0x001510"
    assert bins["umac_ko"]["ubnt_prism_filters_size_bytes"] == 264
    assert bins["ath_dev_ko"]["ath_spectral_filter_init_offset_hex"] == "0x027c00"
    assert bins["ubnt_poll_host_ko"]["ubnt_poll_host_hsr_diag_offset_hex"] == "0x007ebc"


def test_stage159a_ubnt_prism_filters_and_passive_16board_kit():
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    drv = data["pillar_a_ground_up_re_and_knob_catalog"]["active_airprism_driver_internals"]
    table = drv["ubnt_prism_filters_table"]

    assert len(table) == 6
    assert drv["gpio_filter_bank_control"]["bank_1_gpios"] == [15, 16]
    assert drv["gpio_filter_bank_control"]["bank_1_bitmask_hex"] == "0x18000"
    assert drv["gpio_filter_bank_control"]["bank_2_gpios"] == [13, 14]
    assert drv["gpio_filter_bank_control"]["bank_2_bitmask_hex"] == "0x06000"

    assert table[0]["freq_low_mhz"] == 5150 and table[0]["freq_high_mhz"] == 5250
    assert table[1]["freq_low_mhz"] == 5470 and table[1]["freq_high_mhz"] == 5860
    assert table[2]["freq_low_mhz"] == 5200 and table[2]["freq_high_mhz"] == 5300
    assert table[3]["freq_low_mhz"] == 5725 and table[3]["freq_high_mhz"] == 5860

    kit = data["passive_xc_16board_openwrt_kit"]
    assert set(kit.keys()) == {"0xe1f5", "0xe3d5", "0xe5f5", "0xe4f5", "0xe3d7", "0xe3d8"}
    assert sum(v["records_count"] for v in kit.values()) == 16
    for sid, info in kit.items():
        assert info["openmax_squashfs_compatible"] is True
        assert "qca9558_ubnt_" in info["openwrt_dts_file"]
