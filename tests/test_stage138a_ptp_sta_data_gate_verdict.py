#!/usr/bin/env python3
"""Tests for Stage 138A (`T-S138A-UBNT-POLL-HOST-PTP-STA-DATA-GATE-AND-SYNTHETIC-POLL-DISSECTION`)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
VERDICT_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage138a_ptp_sta_data_gate_verdict.json"


def _load() -> dict:
    assert VERDICT_JSON.exists(), f"Missing {VERDICT_JSON}"
    return json.loads(VERDICT_JSON.read_text(encoding="utf-8"))


def test_stage138a_safety_and_5pillar_compliance() -> None:
    data = _load()
    assert data["stage"] == "138A"
    assert data["task_id"] == "T-S138A-UBNT-POLL-HOST-PTP-STA-DATA-GATE-AND-SYNTHETIC-POLL-DISSECTION"
    assert data["live_devices_touched"] is False
    assert data["claim_status"] == "CONFIRMED"
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True


def test_stage138a_question_a_and_b_verdicts() -> None:
    data = _load()
    verdicts = data["verdicts"]
    qa = verdicts["question_a_verdict"]
    qb = verdicts["question_b_verdict"]

    assert qa["status"] == "CONFIRMED"
    assert qa["short_answer"].startswith("NO")
    assert "host_80211_enable" in qa["proof_branch_1_scan_ap_null_polling_0"]
    assert "0x0cd7c0" in qa["proof_branch_1_scan_ap_null_polling_0"]
    assert "0x0083e4" in qa["proof_branch_1_scan_ap_null_polling_0"]
    assert "polling_enabled=1" in qa["proof_branch_2_scan_ap_non_null_polling_1"]
    assert "subtype==3" in qa["proof_branch_2_scan_ap_non_null_polling_1"]

    assert qb["status"] == "CONFIRMED"
    assert "STRICTLY REQUIRES airOS 8 AP ON .241" in qb["short_answer"]
    assert len(qb["mandatory_remote_ota_migration_order"]) == 3


def test_stage138a_ubnt_poll_host_hooks_and_crypto() -> None:
    data = _load()
    uph = data["ubnt_poll_host_dissection"]
    assert uph["claim_status"] == "CONFIRMED"
    assert uph["sha256"] == "bfc3f499a086766917fcbbf1a52d0fac496ad237ae1671c4e640cccdd122c2b5"

    crypto = uph["ubiquiti_ie_crypto_protocol"]
    assert crypto["oui_hex_at_data_0x2bc"] == "002722"
    assert "HMAC-SHA1" in crypto["key_derivation"]
    assert "AES-128-ECB" in crypto["key_derivation"]

    hooks = uph["hooks_dissection"]
    assoc_tx = hooks["ubnt_poll_host_on_assoc_req_tx"]
    assert assoc_tx["range"] == "0x009234..0x009594"
    insns_tx = {i["address"]: (i["mnemonic"], i["op_str"]) for i in assoc_tx["ptp_polling_enable_branch_insn"]}
    assert insns_tx["0x0092d4"] == ("sw", "$zero, 0x3c($sp)")
    assert insns_tx["0x009364"] == ("addiu", "$a0, $zero, 1")
    assert insns_tx["0x00936c"] == ("sw", "$a0, 0x3c($sp)")

    sta_conn = hooks["ubnt_poll_host_on_sta_connect"]
    insns_conn = {i["address"]: (i["mnemonic"], i["op_str"]) for i in sta_conn["sta_mode_scan_ap_gate_insn"]}
    assert insns_conn["0x0083e4"] == ("beqz", "$v0, 0x859c")

    sta_auth = hooks["ubnt_poll_host_on_sta_authorize_and_timer"]
    insns_auth = {i["address"]: (i["mnemonic"], i["op_str"]) for i in sta_auth["authorize_sta_branch_insn"]}
    assert insns_auth["0x0080a4"] == ("beqz", "$v0, 0x8120")


def test_stage138a_umac_host_80211_enable_and_ptp_bin_hooks() -> None:
    data = _load()
    umac = data["umac_and_target_dissection"]
    assert umac["claim_status"] == "CONFIRMED"
    assert umac["sha256"] == "660435ed9c50f1390945535a975565d7234543e01933644bf99dd9deca1b2cd6"

    rx_insns = {
        i["address"]: (i["mnemonic"], i["op_str"])
        for i in umac["host_umac_ptp_data_gates"]["ol_rx_deliver_skips_80211_decap_when_host_80211_zero"]["disassembly_entry"]
    }
    assert rx_insns["0x0cd7c0"] == ("lbu", "$v0, 0x268($s0)")
    assert rx_insns["0x0cd7c4"] == ("beqz", "$v0, 0xcdb50")

    target = umac["target_firmware_athwlan_AR9888v2_ptp_bin"]
    assert target["xtensa_litbase_register"].startswith("0x009bb001")
    assert len(target["sgmt_segments"]) == 5
    full_hooks = target["hook_tables_in_seg2"]["full_polling_hooks_0x0040f688"]["hooks"]
    assert full_hooks[0] == "0x009afc94"
    assert full_hooks[2] == "0x009afcc8"
    assert full_hooks[12] == "0x009aff58"


def test_stage138a_simpy_and_pymoo_models() -> None:
    data = _load()
    sim = data["simpy_ptp_data_gate_simulation"]
    assert sim["openwrt_ap_ie_cleared_normal_ap"]["arp_ipv4_rx_delivered"] == 0
    assert sim["openwrt_ap_ie_cleared_normal_ap"]["arp_ipv4_rx_dropped_bad_ethertype"] == 50
    assert sim["openwrt_ap_re_enable_beacon_ie_before_assoc"]["arp_ipv4_rx_delivered"] == 0
    assert sim["openwrt_ap_forged_subtype1_and_subtype3_ies"]["arp_ipv4_rx_delivered"] == 0
    assert sim["airos8_ptp_ap_on_241_flash_242_first"]["arp_ipv4_rx_delivered"] == 50
    assert sim["airos8_ptp_ap_on_241_flash_242_first"]["arp_ipv4_tx_delivered"] == 50

    pareto = data["pymoo_pareto_ota_sequence"]
    assert len(pareto) >= 1
    assert any(p["keep_241_airos8_until_242_migrated"] is True and p["ota_unreachability_risk"] <= 0.01 for p in pareto)
