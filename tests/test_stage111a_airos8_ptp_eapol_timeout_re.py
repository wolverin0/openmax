#!/usr/bin/env python3
"""Pytest verification suite for Stage 111A
(`T-S111A-AIROS8-PTP-4ADDR-EAPOL-TIMEOUT-RE`).
"""

from __future__ import annotations

import pytest

from tools.re.dissect_stage111a_airos8_ptp_eapol_timeout import (
    OUT_RECEIPT_JSON,
    WA_UBNTBOX_PATH,
    WA_UMAC_PATH,
    WA_UPH_PATH,
    WA_WPAD_PATH,
    XC_UMAC_PATH,
    XC_UPH_8711_PATH,
    run_stage111a_dissection,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


@pytest.fixture(scope="module")
def stage111a_receipt() -> dict:
    return run_stage111a_dissection()


def test_stage111a_safety_boundary_and_binaries_exist(stage111a_receipt: dict) -> None:
    assert WA_WPAD_PATH.exists()
    assert WA_UBNTBOX_PATH.exists()
    assert WA_UMAC_PATH.exists()
    assert XC_UMAC_PATH.exists()
    assert WA_UPH_PATH.exists()
    assert XC_UPH_8711_PATH.exists()
    assert OUT_RECEIPT_JSON.exists()

    assert stage111a_receipt["stage"] == "Stage 111A"
    assert stage111a_receipt["claim_status"] == "CONFIRMED"
    assert stage111a_receipt["live_devices_touched"] is False
    assert stage111a_receipt["hardware_ips_touched"] == []
    assert stage111a_receipt["flash_writes"] == 0


def test_stage111a_wpad_eapol_timeout_and_did_not_ack_disassembly(
    stage111a_receipt: dict,
) -> None:
    wpad = stage111a_receipt["wpad_eapol_dissection"]
    b = wpad["binary"]
    assert b["size_bytes"] == 709880
    assert (
        b["sha256"]
        == "3359defe476bb4fc2104029cd4a90829cdb815e543e3fbe20e27d4e8adb6a281"
    )
    assert b["load_base_va_hex"] == "0x00400000"

    ro = wpad["rodata_strings_verified"]
    assert ro["0x004997d4"] == "uni"
    assert ro["0x004997d8"] == "broad"
    assert ro["0x004997e0"] == "did not Ack EAPOL-Key frame (%scast index=%d)"
    assert ro["0x0049a1a4"] == "sending 1/4 msg of 4-Way Handshake"
    assert ro["0x0049a628"] == "retransmitted EAPOL-Key 1/4"

    mech = wpad["authenticator_eapol_timeout_mechanics"]
    assert mech["pairwise_attempt_1_tx_status_1_timeout_us"] == 100000
    assert mech["pairwise_attempt_1_tx_status_1_timeout_ms"] == 100
    assert mech["pairwise_attempt_1_tx_status_0_timeout_s"] == 1
    assert mech["pairwise_attempt_1_tx_status_0_timeout_ms"] == 1000
    assert mech["pairwise_subsequent_retry_timeout_s"] == 1
    assert mech["pairwise_subsequent_retry_timeout_ms"] == 1000
    assert mech["max_pairwise_retries_slti_limit"] == 5
    assert mech["dot11RSNAConfigPairwiseUpdateCount"] == 4

    by_va = {r["addr_hex"]: r for r in mech["wpa_send_eapol_instructions"]}
    assert by_va["0x417a18"]["insn"] == "lw $v0, 0x7c($s2)"
    assert by_va["0x417a20"]["insn"] == "addiu $a0, $zero, 1"
    assert by_va["0x417a48"]["insn"] == "j 0x41d2d0"
    assert by_va["0x417a60"]["insn"] == "lui $a1, 1"
    assert by_va["0x417a64"]["insn"] == "ori $a1, $a1, 0x86a0"
    assert by_va["0x417a7c"]["insn"] == "sw $v0, 0x228($s0)"
    assert by_va["0x417aac"]["insn"] == "move $a1, $zero"
    assert by_va["0x417ab0"]["insn"] == "j 0x417a68"
    assert by_va["0x417ab4"]["insn"] == "addiu $a0, $zero, 1"

    ptk_by_va = {r["addr_hex"]: r for r in mech["sm_WPA_PTK_PTKSTART_Enter_instructions"]}
    assert ptk_by_va["0x417ad8"]["insn"] == "lw $v0, 0x30($a0)"
    assert ptk_by_va["0x417af4"]["insn"] == "slti $a0, $v0, 5"

    ack_by_va = {r["addr_hex"]: r for r in mech["tx_status_did_not_ack_instructions"]}
    assert ack_by_va["0x417e0c"]["insn"] == "addiu $a2, $zero, 0x1c8"
    assert ack_by_va["0x417e34"]["insn"] == "jal 0x4179a8"
    assert ack_by_va["0x417e40"]["insn"] == "move $a0, $s1"


def test_stage111a_umac_is_ubnt_ptp_and_4addr_foreign_eapol_drop(
    stage111a_receipt: dict,
) -> None:
    umac = stage111a_receipt["umac_ptp_4addr_eapol_dissection"]
    assert umac["wa_umac_ko"]["size_bytes"] == 2356432
    assert (
        umac["wa_umac_ko"]["sha256"]
        == "660435ed9c50f1390945535a975565d7234543e01933644bf99dd9deca1b2cd6"
    )
    assert umac["wa_umac_ko"]["athwlan_AR9888v2_ptp_bin_size_bytes"] == 214299

    assert umac["xc_umac_ko"]["size_bytes"] == 2358768
    assert (
        umac["xc_umac_ko"]["sha256"]
        == "ec1df9e62f0e766432323d225e4bc0e331c23b941594bb624992d937ca674e7a"
    )
    assert umac["xc_umac_ko"]["athwlan_AR9888v2_ptp_bin_size_bytes"] == 215074

    ro = umac["rodata_strings_verified"]
    assert (
        ro["foreign_eapol_drop"]["value"]
        == "Received foreign EAPOL (%02x:%02x:%02x:%02x:%02x:%02x) - drop it\n"
    )
    assert ro["four_way_pkt_iv_4eapol"]["value"] == "%s: 4Way pkt iv_4eapol=0x%x\n"
    assert (
        ro["pm4_completed_pending_ukey"]["value"]
        == "%s EAPOL PM4 completed, timer expired for pending ukey, iv_4eapol=0x%x\n"
    )
    assert (
        ro["pm4_completed_pending_gkey"]["value"]
        == "%s EAPOL PM4 completed, timer expired for pending gkey, iv_4eapol=0x%x\n"
    )

    m1 = umac["mechanism_1_is_ubnt_ptp_forces_host_80211_enable_zero"]
    attach_by_addr = {r["addr_hex"]: r for r in m1["ol_ath_attach_instructions"]}
    assert attach_by_addr["0x0bc0cc"]["relocations"][0]["symbol"] == "is_ubnt_ptp"
    assert attach_by_addr["0x0bc0f0"]["insn"] == "beqz $a0, 0xbc104"
    assert attach_by_addr["0x0bc0fc"]["insn"] == "move $v1, $zero"
    assert attach_by_addr["0x0bc140"]["insn"] == "sb $v1, -0x1ce4($v0)"

    m2 = umac["mechanism_2_4addr_wds_rx_decap_and_foreign_eapol_drop_gate"]
    rx_head = {r["addr_hex"]: r for r in m2["ol_rx_deliver_head_instructions"]}
    assert rx_head["0x0cd7c0"]["insn"] == "lbu $v0, 0x268($s0)"
    assert rx_head["0x0cd7f0"]["insn"] == "xori $t4, $t1, 3"
    assert rx_head["0x0cd7f4"]["insn"] == "addiu $a1, $zero, 0x20"

    osif_by_addr = {r["addr_hex"]: r for r in m2["osif_deliver_data_ol_instructions"]}
    assert osif_by_addr["0x09e158"]["relocations"][0]["symbol"] == "eth_type_trans"
    assert osif_by_addr["0x09e168"]["insn"] == "lw $v0, 0x84($s0)"
    assert osif_by_addr["0x09e1b4"]["relocations"][0]["symbol"] == "consume_skb"

    m3 = umac["mechanism_3_tx_iv_4eapol_and_1200ms_deferred_setkey_timer"]
    assert m3["iv_eapol_timer_delay_ms"] == 1200
    pm4_by_addr = {r["addr_hex"]: r for r in m3["pm4_sent_instructions"]}
    assert pm4_by_addr["0x0a5fb0"]["relocations"][0]["symbol"] == "msecs_to_jiffies"
    assert pm4_by_addr["0x0a5fb4"]["insn"] == "addiu $a0, $zero, 0x4b0"


def test_stage111a_uph_sta_connect_uninitialized_ht_comm_msg7(
    stage111a_receipt: dict,
) -> None:
    uph = stage111a_receipt["uph_ptp_allow80211_dissection"]
    assert uph["wa_ubnt_poll_host_ko"]["size_bytes"] == 189880
    assert (
        uph["wa_ubnt_poll_host_ko"]["sha256"]
        == "bfc3f499a086766917fcbbf1a52d0fac496ad237ae1671c4e640cccdd122c2b5"
    )
    assert uph["xc_ubnt_poll_host_ko_8711"]["size_bytes"] == 186560
    assert (
        uph["xc_ubnt_poll_host_ko_8711"]["sha256"]
        == "1829cf8e5a282fb143dbbea4e9542c3088a5296ff7055ab764647bffe95578ee"
    )

    ro = uph["rodata_strings_verified"]
    assert (
        ro["associating_with_normal_ap"]["value"]
        == "<7>ubnt_poll_host: Associating with normal AP %02X:%02X:%02X:%02X:%02X:%02X\n"
    )

    desync = uph["ptp_allow80211_target_state_desync"]
    sta_conn = {r["addr_hex"]: r for r in desync["on_sta_connect_sta_branch_instructions"]}
    assert sta_conn["0x0083c8"]["relocations"][0]["symbol"] == "ubnt_poll_host_sta_list_find"
    assert sta_conn["0x0083e4"]["insn"] == "beqz $v0, 0x859c"
    assert sta_conn["0x00861c"]["insn"] == "move $a0, $s0"
    assert sta_conn["0x008620"]["relocations"][0]["symbol"] == "ubnt_poll_host_ht_comm_tx"


def test_stage111a_simpy_and_pymoo_and_5pillar_gate(stage111a_receipt: dict) -> None:
    sim = stage111a_receipt["simulation_and_pareto_analysis"]
    reg_a = sim["simpy_regimes"]["regime_a_ptp_sta_uninit_ht_comm_or_foreign_eapol_drop"]
    assert reg_a["outcome"]["completed"] is False
    assert reg_a["outcome"]["attempts_used"] == 4
    assert any(
        "did not Ack EAPOL-Key frame" in e["event"] for e in reg_a["events"]
    )

    reg_b = sim["simpy_regimes"]["regime_b_4addr_eapol_m2_race_recovered_on_attempt_2"]
    assert reg_b["outcome"]["completed"] is True
    assert reg_b["outcome"]["attempts_used"] == 2
    assert reg_b["outcome"]["completion_time_ms"] == 102.55

    reg_c = sim["simpy_regimes"]["regime_c_step1_airos8_ap_to_openwrt_sta_hybrid"]
    assert reg_c["outcome"]["completed"] is True
    assert reg_c["outcome"]["attempts_used"] == 1
    assert reg_c["outcome"]["completion_time_ms"] == 2.55

    audit = audit_stage_receipt_5pillars(stage111a_receipt)
    assert audit["compliant"] is True
    assert audit["missing_pillars"] == []
