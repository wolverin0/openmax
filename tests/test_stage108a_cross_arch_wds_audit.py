#!/usr/bin/env python3
"""Pytest verification suite for Stage 108A
(`T-S108A-CROSS-VERSION-MAC80211-6693-VS-66110-WDS-EAPOL-AUDIT`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage108a_cross_arch_wds_audit import (
    OUT_RECEIPT_JSON,
    PANEL1_TEB_KO,
    PBE5AC_ROM_KO,
    PBE5AC_TEB_KO,
    run_stage108a_cross_arch_wds_audit,
)


@pytest.fixture(scope="module")
def stage108a_receipt() -> dict:
    return run_stage108a_cross_arch_wds_audit()


def test_stage108a_safety_and_binaries_exist(stage108a_receipt: dict) -> None:
    assert PANEL1_TEB_KO.exists()
    assert PBE5AC_TEB_KO.exists()
    assert PBE5AC_ROM_KO.exists()
    assert OUT_RECEIPT_JSON.exists()
    assert stage108a_receipt["live_devices_touched"] is False
    assert stage108a_receipt["flash_writes"] == 0
    assert stage108a_receipt["claim_status"] == "CONFIRMED"


def test_stage108a_elf_layout_and_this_module_abi(stage108a_receipt: dict) -> None:
    b = stage108a_receipt["binaries_audited"]
    p1 = b["panel1_mac80211_teb_ko"]
    pbe = b["pbe5ac_66110_mac80211_teb_ko"]
    rom = b["pbe5ac_66110_mac80211_rom_ko"]
    h93 = b["historical_6_6_93_reference"]

    assert p1["size_bytes"] == 829464
    assert (
        p1["sha256"]
        == "19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416"
    )
    assert p1["this_module_size_bytes"] == 384

    assert pbe["size_bytes"] == 815640
    assert (
        pbe["sha256"]
        == "3e3d812ff0d4a2fd1a1f9c1257a9356058ac439108e3c27ef6b11d944b696868"
    )
    assert pbe["this_module_size_bytes"] == 352

    assert rom["size_bytes"] == 815640
    assert (
        rom["sha256"]
        == "8566fb1c104b61bdb645fc17ba28d6c0ea1bd738e2d05dc8a935464d872a1ce5"
    )
    assert rom["this_module_size_bytes"] == 352

    assert h93["size_bytes"] == 816748
    assert h93["kernel_version"] == "6.6.93"
    assert h93["skb_data_offset_hex"] == "0xa4"

    abi = stage108a_receipt["cross_version_abi_summary"]
    assert abi["text_section_file_offset_hex"] == "0x70"
    assert abi["text_section_size_bytes"] == 564672
    assert abi["total_text_32bit_word_diffs_panel1_vs_pbe5ac_teb"] == 1661
    assert abi["skb_data_offset_panel1_hex"] == "0xa4"
    assert abi["skb_data_offset_pbe5ac_66110_hex"] == "0xa8"
    assert abi["skb_data_offset_delta_bytes"] == 4


def test_stage108a_ieee80211_rx_mesh_check_teb_diff(stage108a_receipt: dict) -> None:
    fn1 = stage108a_receipt["function_1_ieee80211_rx_mesh_check_audit"]
    assert fn1["patch_window_file_range_hex"] == "0x033c88..0x033cdc"
    assert fn1["patch_window_text_range_hex"] == "0x033c18..0x033c6c"
    assert fn1["total_patched_instructions"] == 21
    assert fn1["panel1_vs_pbe5ac_66110_diff_count"] == 2

    diffs = fn1["panel1_vs_pbe5ac_66110_exact_diffs"]
    assert diffs[0]["file_offset_hex"] == "0x033ca4"
    assert diffs[0]["text_offset_hex"] == "0x033c34"
    assert diffs[0]["panel1_teb_word_hex"] == "0x8cc900a4"
    assert diffs[0]["panel1_teb_insn"] == "lw $t1, 0xa4($a2)"
    assert diffs[0]["pbe5ac_66110_teb_word_hex"] == "0x8cc900a8"
    assert diffs[0]["pbe5ac_66110_teb_insn"] == "lw $t1, 0xa8($a2)"
    assert diffs[0]["pbe5ac_66110_rom_word_hex"] == "0xa7a00046"

    assert diffs[1]["file_offset_hex"] == "0x033ccc"
    assert diffs[1]["text_offset_hex"] == "0x033c5c"
    assert diffs[1]["panel1_teb_word_hex"] == "0xacc900a4"
    assert diffs[1]["panel1_teb_insn"] == "sw $t1, 0xa4($a2)"
    assert diffs[1]["pbe5ac_66110_teb_word_hex"] == "0xacc900a8"
    assert diffs[1]["pbe5ac_66110_teb_insn"] == "sw $t1, 0xa8($a2)"

    by_file = {r["file_offset_hex"]: r for r in fn1["instructions"]}
    assert by_file["0x033cb8"]["pbe5ac_66110_teb_word_hex"] == "0x394a6558"
    assert by_file["0x033cb8"]["pbe5ac_66110_teb_insn"] == "xori $t2, $t2, 0x6558"
    assert by_file["0x033cd4"]["pbe5ac_66110_teb_word_hex"] == "0x7c0a1044"


def test_stage108a_ieee80211_rx_h_sta_process_and_4addr_eapol_audit(
    stage108a_receipt: dict,
) -> None:
    fn2 = stage108a_receipt["function_2_ieee80211_rx_h_sta_process_and_rx_handlers_audit"]
    assert fn2["file_range_hex"] == "0x0357d0..0x0375f0"
    assert fn2["total_word_diffs_in_range"] == 30

    cs1 = fn2["unexpected_4addr_callsites"]["callsite_1_unassociated_or_no_sta"]
    assert cs1["jal_file_offset_hex"] == "0x035f08"
    assert cs1["jal_text_offset_hex"] == "0x035e98"
    assert cs1["identical_across_6693_panel1_and_66110"] is True
    cs1_by_file = {r["file_offset_hex"]: r for r in cs1["instructions"]}
    assert (
        cs1_by_file["0x035f08"]["relocations_pbe5ac"][0]["symbol_name"]
        == "cfg80211_rx_unexpected_4addr_frame"
    )
    assert cs1_by_file["0x035f0c"]["pbe5ac_66110_teb_word_hex"] == "0x3c140002"
    assert cs1_by_file["0x035f14"]["pbe5ac_66110_teb_word_hex"] == "0x26940001"

    cs2 = fn2["unexpected_4addr_callsites"][
        "callsite_2_associated_sta_before_ap_vlan_bind_fmx_disc_38"
    ]
    assert cs2["jal_file_offset_hex"] == "0x0375ac"
    assert cs2["jal_text_offset_hex"] == "0x03753c"
    assert cs2["identical_across_6693_panel1_and_66110"] is True
    cs2_by_file = {r["file_offset_hex"]: r for r in cs2["instructions"]}
    assert (
        cs2_by_file["0x0375ac"]["relocations_pbe5ac"][0]["symbol_name"]
        == "cfg80211_rx_unexpected_4addr_frame"
    )
    assert cs2_by_file["0x0375b0"]["pbe5ac_66110_teb_word_hex"] == "0x24a5076c"
    assert cs2_by_file["0x0375b4"]["pbe5ac_66110_teb_word_hex"] == "0x1000f819"
    assert cs2_by_file["0x0375b8"]["pbe5ac_66110_teb_word_hex"] == "0x3c140002"


def test_stage108a_data_to_8023_pae_and_teb_dispatch(stage108a_receipt: dict) -> None:
    fn3 = stage108a_receipt["function_3_ieee80211_data_to_8023_audit"]
    ca = fn3["callsite_a_rx_h_amsdu"]
    assert ca["jal_data_to_8023_exthdr_file_hex"] == "0x03501c"
    assert ca["jal_amsdu_to_8023s_file_hex"] == "0x035068"

    cb = fn3["callsite_b_rx_h_data_pae_and_teb_dispatch"]
    assert cb["jal_data_to_8023_exthdr_file_hex"] == "0x035a3c"
    assert cb["skb_data_load_at_file_0x035a54"]["panel1_word_hex"] == "0x8cc200a4"
    assert cb["skb_data_load_at_file_0x035a54"]["pbe5ac_66110_word_hex"] == "0x8cc200a8"

    cb_by_file = {r["file_offset_hex"]: r for r in cb["instructions"]}
    assert (
        cb_by_file["0x035a3c"]["relocations_pbe5ac"][0]["symbol_name"]
        == "ieee80211_data_to_8023_exthdr"
    )
    assert cb_by_file["0x035a58"]["pbe5ac_66110_teb_word_hex"] == "0x9485051c"
    assert cb_by_file["0x035a6c"]["pbe5ac_66110_teb_word_hex"] == "0x10a202cc"
    assert cb_by_file["0x035a7c"]["pbe5ac_66110_teb_word_hex"] == "0x0c00cefb"


def test_stage108a_five_pillar_gate_compliance(stage108a_receipt: dict) -> None:
    audit = audit_stage_receipt_5pillars(stage108a_receipt)
    assert audit["compliant"] is True
    assert stage108a_receipt["five_pillar_gate_audit"]["compliant"] is True
