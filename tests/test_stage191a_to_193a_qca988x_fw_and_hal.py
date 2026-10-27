"""Regression tests for Stages 191A, 192A, and 193A:
- Stage 191A: 4-Firmware QCA988x SGMT & Hook-Table Comparative Dissection
- Stage 192A: ath_hal / ath_dev / umac / ubnt_poll_host Register & WMI/HTT Sink Dissection (340 / 437 / 571 Knobs)
- Stage 193A: FMX-DISC-41 & FMX-DISC-42 Formalization and Line-Budget Gate
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

S191_JSON = ROOT / "artifacts" / "autoresearch" / "stage191a_qca988x_4firmware_comparative_dissection.json"
S191_MD = ROOT / "docs" / "STAGE191A_QCA988X_4FIRMWARE_COMPARATIVE_DISSECTION.md"
S192_JSON = ROOT / "artifacts" / "autoresearch" / "stage192a_hal_wmi_accessor_and_340knob_sinks.json"
S192_MD = ROOT / "docs" / "STAGE192A_HAL_WMI_ACCESSOR_AND_340KNOB_SINKS.md"
CURATED_MD = ROOT / "docs" / "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md"


def test_stage191a_4firmware_comparative_dissection() -> None:
    assert S191_JSON.is_file(), f"Missing {S191_JSON}"
    assert S191_MD.is_file(), f"Missing {S191_MD}"

    data = json.loads(S191_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "191A"
    assert data["claim_status"] == "CONFIRMED"
    assert data["live_devices_touched"] is False
    assert data["five_pillar_gate_audit"]["compliant"] is True

    fws = data["firmwares"]
    assert set(fws.keys()) == {
        "athwlan_AR9888v2_ptp_bin",
        "athwlan_AR9888v2_ptmp_ap_bin",
        "athwlan_AR9888v2_ptmp_sta_bin",
        "openwrt_qca988x_hw20_firmware_2_ct",
    }

    # Verify LITBASE invariant across all 4 firmwares
    for k in ("athwlan_AR9888v2_ptp_bin", "athwlan_AR9888v2_ptmp_ap_bin", "athwlan_AR9888v2_ptmp_sta_bin"):
        fw = fws[k]
        assert fw["entrypoint_beginaddr"] == "0x00983c00", k
        assert fw["xtensa_litbase_register"] == "0x009bb001", k
    owrt_main = fws["openwrt_qca988x_hw20_firmware_2_ct"]["main_sgmt"]
    assert owrt_main["entrypoint_beginaddr"] == "0x00983c00"
    assert owrt_main["xtensa_litbase_register"] == "0x009bb001"

    # Verify Ubiquiti 32-slot hook tables vs OpenWrt hook-free
    assert fws["athwlan_AR9888v2_ptp_bin"]["ubiquiti_polling_hook_tables"]["full_polling_hooks_va"] == "0x0040f688"
    assert fws["athwlan_AR9888v2_ptmp_ap_bin"]["ubiquiti_polling_hook_tables"]["full_polling_hooks_va"] == "0x0040fb48"
    assert fws["athwlan_AR9888v2_ptmp_sta_bin"]["ubiquiti_polling_hook_tables"]["full_polling_hooks_va"] == "0x0040fbf8"
    for k in ("athwlan_AR9888v2_ptp_bin", "athwlan_AR9888v2_ptmp_ap_bin", "athwlan_AR9888v2_ptmp_sta_bin"):
        ht = fws[k]["ubiquiti_polling_hook_tables"]
        assert ht["has_ubiquiti_polling_hooks"] is True
        assert ht["initial_hooks_active_slots"] == 15
        assert ht["initial_hooks_null_slots"] == 17
        assert ht["full_polling_hooks_active_slots"] == 32
        assert ht["full_polling_hooks_null_slots"] == 0
    assert owrt_main["ubiquiti_polling_hook_tables"]["has_ubiquiti_polling_hooks"] is False
    assert owrt_main["ubiquiti_polling_hook_tables"]["data_segment_reduction_bytes_vs_ubiquiti"] == 7844
    assert len(data["hook_table_32slot_side_by_side"]) == 32

    # Verify markdown line budget and doc-head
    md_text = S191_MD.read_text(encoding="utf-8")
    md_lines = md_text.splitlines()
    assert len(md_lines) < 220, f"S191_MD has {len(md_lines)} lines (>= 220)"
    assert md_text.count("<!-- doc-head:") == 1


def test_stage192a_hal_wmi_accessor_and_340knob_sinks() -> None:
    assert S192_JSON.is_file(), f"Missing {S192_JSON}"
    assert S192_MD.is_file(), f"Missing {S192_MD}"

    data = json.loads(S192_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "192A"
    assert data["claim_status"] == "CONFIRMED"
    assert data["live_devices_touched"] is False
    assert data["five_pillar_gate_audit"]["compliant"] is True

    # Verify ath_hal.ko register accessors and vtable
    hal = data["hal_and_wmi_accessor_dissection"]
    assert hal["ar9300_hal_template_vtable_count"] == 218
    assert hal["ath_hal_reg_rw_callsites_total"] == 1013

    # Verify ath_dev.ko & umac.ko jump tables
    jt = hal["jump_tables_summary"]
    assert jt["wlan_set_param_rodata_0x000300"]["active_cases"] == 99
    assert jt["ol_ath_vap_set_param_rodata_0x0c870"]["active_cases"] == 37
    assert jt["ol_ath_set_config_param_rodata_0x0d620"]["active_cases"] == 58
    assert jt["ath_set_config_rodata_0x000d60"]["total_slots"] == 217

    # Verify 340 / 437 / 438 knob sink mapping
    acct = data["knob_sink_mapping_summary"]
    assert acct["airos_ioctl_plus_hardware_knobs_count"] == 340
    assert acct["airos_umac_uph_total_knobs_count"] == 437
    assert acct["total_mapped_knobs_count"] == 438
    assert len(data["mapped_knobs"]) == 438
    assert all(k.get("sink_category") for k in data["mapped_knobs"])

    md_text = S192_MD.read_text(encoding="utf-8")
    md_lines = md_text.splitlines()
    assert len(md_lines) < 220, f"S192_MD has {len(md_lines)} lines (>= 220)"
    assert md_text.count("<!-- doc-head:") == 1


def test_stage193a_curated_discoveries_fmx_disc_41_and_42() -> None:
    assert CURATED_MD.is_file(), f"Missing {CURATED_MD}"
    text = CURATED_MD.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"CURATED_MD has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1
    assert "FMX-DISC-41" in text
    assert "FMX-DISC-42" in text
    assert "0x0d21e4" in text
    assert "0x0040f688" in text
    assert "ar9300_hal_template" in text
