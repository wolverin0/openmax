"""Stage 322A: Pytest Verification Suite for Stages 317A..321A QCA988x Xtensa Target Firmware & HT_COMM RE."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]

STAGE317A_JSON = ROOT / "artifacts/autoresearch/stage317a_xc_vs_wa_target_firmware_audit.json"
STAGE318A_JSON = ROOT / "artifacts/autoresearch/stage318a_qca988x_xtensa_rate_control_dissection.json"
STAGE319A_JSON = ROOT / "artifacts/autoresearch/stage319a_qca988x_target_full_polling_hooks_dissection.json"
STAGE320A_JSON = ROOT / "artifacts/autoresearch/stage320a_ubnt_poll_ht_comm_state_machine_dissection.json"
STAGE321A_DOC = ROOT / "docs/STAGE321A_QCA988X_XTENSA_TARGET_FIRMWARE_MASTER_DOSSIER.md"


def test_stage317a_xc_vs_wa_target_firmware_audit() -> None:
    assert STAGE317A_JSON.is_file(), f"Missing {STAGE317A_JSON}"
    data = json.loads(STAGE317A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "317A"
    assert data["status"] == "CONFIRMED"
    assert data["live_devices_touched"] is False
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    host_cmp = data["host_umac_comparison_xc25_vs_wa25"]
    assert host_cmp["text_size_bytes"] == 892816
    assert host_cmp["data_size_delta_bytes"] == 2336
    assert host_cmp["differing_functions_count"] == 234

    otp = data["otp_firmware_comparison"]
    assert (
        otp["XC.v8.7.25"]["compressed_sha256"]
        == otp["WA.v8.7.25"]["compressed_sha256"]
        == otp["WA.v8.7.11"]["compressed_sha256"]
    )

    deltas = data["comparative_deltas"]
    for fw_sym in (
        "athwlan_AR9888v2_ptp_bin",
        "athwlan_AR9888v2_ptmp_ap_bin",
        "athwlan_AR9888v2_ptmp_sta_bin",
    ):
        d = deltas[fw_sym]
        assert d["segment_length_deltas_xc25_minus_wa25"]["seg0"] == 0
        assert d["segment_length_deltas_xc25_minus_wa25"]["seg1"] == 36
        assert d["segment_length_deltas_xc25_minus_wa25"]["seg2"] == 3392
        assert d["hook_table_va_shift_xc25_minus_wa25_hex"] == "0xd60"
        assert d["initial_hooks_non_null_counts"]["XC.v8.7.25"] == 15
        assert d["initial_hooks_non_null_counts"]["WA.v8.7.25"] == 15
        assert d["initial_hooks_non_null_counts"]["WA.v8.7.11"] == 14


def test_stage318a_qca988x_xtensa_rate_control_dissection() -> None:
    assert STAGE318A_JSON.is_file(), f"Missing {STAGE318A_JSON}"
    data = json.loads(STAGE318A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "318A"
    assert data["status"] == "CONFIRMED"
    assert data["live_devices_touched"] is False
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    rc_globals = {g["symbol"]: g for g in data["target_rate_control_globals"]}
    assert rc_globals["g_rc_rate_max_per_thr"]["ram_va_ptp"] == "0x0040da7c"
    assert rc_globals["g_default_xretry_per_penalty"]["ram_va_ptp"] == "0x0040da78"
    assert rc_globals["g_default_no_ack_wifi_thr"]["ram_va_ptp"] == "0x0040da14"
    assert rc_globals["g_rc_probe_period_ms"]["ram_va_ptp"] == "0x0040d4e0"
    assert rc_globals["g_dbg_max_sw_retry"]["ram_va_ptp"] == "0x0040d364"

    wmi = data["wmi_parameter_dispatchers"]
    assert wmi["WMI_PDEV_SET_PARAM_CMDID_0x9006"]["jump_table"]["active_count"] == 29
    assert wmi["WMI_VDEV_SET_PARAM_CMDID_0x901a"]["jump_table_ptp"]["active_count"] == 28
    assert wmi["WMI_PEER_ASSOC_CMDID_0x901e"]["wal_peer_set_param_jump_table"]["active_count"] == 32


def test_stage319a_qca988x_target_full_polling_hooks_dissection() -> None:
    assert STAGE319A_JSON.is_file(), f"Missing {STAGE319A_JSON}"
    data = json.loads(STAGE319A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "319A"
    assert data["status"] == "CONFIRMED"
    assert data["live_devices_touched"] is False
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    tables = data["table_addresses_across_firmwares"]
    assert tables["WA.v8.7.25_ptp"]["initial_hooks_va"] == "0x0040f608"
    assert tables["WA.v8.7.25_ptp"]["full_polling_hooks_va"] == "0x0040f688"
    assert tables["WA.v8.7.25_ptmp_ap"]["full_polling_hooks_va"] == "0x0040fb48"
    assert tables["WA.v8.7.25_ptmp_sta"]["full_polling_hooks_va"] == "0x0040fbf8"
    assert tables["XC.v8.7.25_ptp"]["full_polling_hooks_va"] == "0x004103e8"
    assert tables["XC.v8.7.25_ptmp_ap"]["full_polling_hooks_va"] == "0x004108a8"
    assert tables["XC.v8.7.25_ptmp_sta"]["full_polling_hooks_va"] == "0x00410958"
    assert tables["WA.v8.7.11_ptp"]["full_polling_hooks_va"] == "0x0040f554"

    hooks = data["hooks_32_dissection"]
    assert len(hooks) == 32
    assert hooks[0]["addresses"]["WA.v8.7.25_ptp"] == "0x009afc94"
    assert hooks[0]["in_initial_hooks_v8_7_25"] is True
    assert hooks[0]["in_initial_hooks_v8_7_11"] is False
    assert hooks[19]["in_initial_hooks_v8_7_25"] is True
    assert hooks[31]["addresses"]["WA.v8.7.25_ptp"] == "0x009b0f64"


def test_stage320a_ubnt_poll_ht_comm_state_machine_dissection() -> None:
    assert STAGE320A_JSON.is_file(), f"Missing {STAGE320A_JSON}"
    data = json.loads(STAGE320A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "320A"
    assert data["status"] == "CONFIRMED"
    assert data["live_devices_touched"] is False
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    contract = data["wmi_transport_contract"]
    assert contract["active_wire_opcodes_per_mode"]["PtP_unpack"] == 24
    assert contract["active_wire_opcodes_per_mode"]["PtP_rx_dispatcher"] == 21
    assert contract["active_wire_opcodes_per_mode"]["PtMP_AP"] == 39
    assert contract["active_wire_opcodes_per_mode"]["PtMP_STA"] == 39
    assert contract["active_wire_opcodes_per_mode"]["union_across_all_modes"] == 42

    opcodes = {entry["opcode"]: entry for entry in data["opcodes_catalog"]}
    assert 13 in opcodes and opcodes[13]["name"] == "HT_COMM_OP_POLL_STATE_CTRL"
    assert 10 in opcodes and opcodes[10]["name"] == "HT_COMM_OP_RATE_OVERRIDE"
    assert 40 in opcodes and opcodes[40]["name"] == "HT_COMM_OP_EVM_CINR_REPORT"


def test_stage321a_master_dossier_budget_and_doc_head() -> None:
    assert STAGE321A_DOC.is_file(), f"Missing {STAGE321A_DOC}"
    text = STAGE321A_DOC.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"Dossier exceeds 220-line budget ({len(lines)} lines)"
    assert text.count("<!-- doc-head:") == 1
    assert text.count("<!-- /doc-head -->") == 1
    for token in ("317A", "318A", "319A", "320A", "0x0040da7c", "0x0040f688", "0x9065"):
        assert token in text
