"""Unit and verification tests for `analysis/re_umac_and_airprism_callgraph.py` (`T-SUB-GEM3-03`)."""

from __future__ import annotations

import json

import pytest

from analysis.re_umac_and_airprism_callgraph import (
    DEFAULT_OUTPUT_JSON,
    DEFAULT_ROOTFS_DIR,
    generate_full_report,
)


@pytest.fixture(scope="module")
def re_report() -> dict:
    assert DEFAULT_OUTPUT_JSON.exists(), f"Missing generated receipt {DEFAULT_OUTPUT_JSON}"
    return json.loads(DEFAULT_OUTPUT_JSON.read_text(encoding="utf-8"))


def test_receipt_matches_generator(re_report: dict) -> None:
    fresh = generate_full_report(DEFAULT_ROOTFS_DIR)
    assert re_report == fresh
    assert re_report["task_id"] == "T-SUB-GEM3-03"
    assert re_report["schema_version"] == "1.0.0"


def test_module_identities_wa_vs_xc(re_report: dict) -> None:
    mods = re_report["module_identities"]
    umac = mods["umac.ko"]
    assert umac["wa_size_bytes"] == 2356432
    assert umac["xc_size_bytes"] == 2358768
    assert umac["size_delta_bytes"] == 2336
    assert umac["symbol_count_wa"] == 4766
    assert umac["symbol_count_xc"] == 4766
    assert umac["sections"][".text"]["size_delta"] == 0
    assert umac["sections"][".rodata"]["size_delta"] == 0
    assert umac["sections"][".bss"]["identical"] is True
    assert umac["sections"]["__param"]["identical"] is True
    assert umac["sections"][".data"]["size_delta"] == 2336

    blobs = umac["embedded_target_firmware_blobs"]
    total_blob_delta = sum(b["delta_bytes"] for b in blobs.values())
    assert total_blob_delta == 775 + 786 + 775 == 2336

    assert mods["ubnt_poll_host.ko"]["sections"][".rodata"]["identical"] is True
    assert mods["ubnt_poll_host.ko"]["sections"][".data"]["identical"] is True
    assert mods["ath_dev.ko"]["sections"][".rodata"]["identical"] is True
    assert mods["ath_dev.ko"]["sections"][".data"]["identical"] is True
    assert mods["wpad"]["byte_identical"] is True


def test_oui_split_and_vendor_ie_crypto(re_report: dict) -> None:
    oui = re_report["oui_and_vendor_ie_analysis"]
    s_156d = oui["oui_00_15_6d_summary"]
    assert s_156d["in_umac_ko"] == 0
    assert s_156d["in_ubnt_poll_host_ko"] == 0
    assert s_156d["in_wpad"] == 0
    assert s_156d["wa_rootfs_occurrences_by_file"]["lib/modules/2.6.32.68/urd.ko"] == 36
    assert s_156d["wa_rootfs_occurrences_by_file"]["bin/athbox"] == 36

    s_2722 = oui["oui_00_27_22_summary"]
    assert s_2722["oui_hex"] == "002722"
    assert s_2722["sub_header_0x2b0_hex"] == "ffffff"
    assert s_2722["hmac_sha1_seed_0x2b4_hex"] == "ffffffffffff"
    assert s_2722["bench_bssid_18e8297455a2_beacon_aes128_key_bcast_key"] == "5b333bd4f30fe7cdabd44e1b976b66e9"
    assert s_2722["bench_bssid_18e8297455a2_beacon_aes128_key_bssid_key"] == "f11244759c9737bff962c1b8ee6952bb"

    native = oui["umac_native_00_27_22_handlers"]
    parse_bcn = native["ieee80211_parse_beacon_csa_and_airmax_ie_checks"]
    assert parse_bcn["csa_oui_and_type_le_u32"] == "0x55222700"
    assert parse_bcn["csa_scan_params_store_offset"] == "0xf4"
    assert parse_bcn["airmax_oui_and_type_le_u32"] == "0xff222700"
    assert parse_bcn["airmax_scan_params_store_offset"] == "0xf8"

    csa_hdr = native["ieee80211_add_ubnt_csa"]["constructed_header"]
    assert csa_hdr["element_id"] == 0xDD
    assert csa_hdr["length"] == 0x0B
    assert (csa_hdr["oui_byte0"], csa_hdr["oui_byte1"], csa_hdr["oui_byte2"]) == (0x00, 0x27, 0x22)
    assert csa_hdr["sub_type"] == 0x55
    assert csa_hdr["version"] == 0x01

    radar_hdr = native["ieee80211_send_ubnt_action_radar"]["constructed_header"]
    assert radar_hdr["frame_len"] == 14
    assert radar_hdr["category"] == 0x7F
    assert (radar_hdr["oui_byte0"], radar_hdr["oui_byte1"], radar_hdr["oui_byte2"]) == (0x00, 0x27, 0x22)


def test_hook_host_ops_27_slots(re_report: dict) -> None:
    tbl = re_report["hook_host_ops_dispatch_table"]
    assert tbl["registration_function"]["umac_symbol"] == "ath_hook_host_register"
    assert tbl["registration_function"]["umac_text_offset"] == "0xd9f70"
    assert tbl["registration_function"]["umac_bss_offset"] == "0x1c360"
    assert tbl["registration_function"]["slot_count"] == 27
    assert tbl["total_umac_lo16_references"] == 54

    slots = {s["slot"]: s for s in tbl["slots"]}
    assert len(slots) == 27
    assert "ubnt_poll_host_data_create" in slots[0]["target_functions"]
    assert slots[0]["umac_caller_count"] == 1
    assert "ubnt_poll_host_data_destory" in slots[1]["target_functions"]
    assert slots[2]["umac_caller_count"] == 1
    assert "ubnt_poll_host_on_sta_destroy" in slots[3]["target_functions"]
    assert "ubnt_poll_host_on_beacon_tx" in slots[7]["target_functions"]
    assert "ubnt_poll_host_on_assoc_req_tx" in slots[8]["target_functions"]
    assert "ubnt_poll_host_on_assoc_resp_tx" in slots[9]["target_functions"]
    assert "ubnt_poll_host_on_beacon_rx" in slots[13]["target_functions"]
    assert slots[13]["umac_caller_count"] == 3
    assert "ubnt_poll_host_on_assoc_req_rx" in slots[14]["target_functions"]
    assert "ubnt_poll_host_on_assoc_resp_rx" in slots[15]["target_functions"]
    assert "ubnt_poll_host_on_sta_disconnect" in slots[18]["target_functions"]
    assert "ubnt_poll_host_on_sta_connect" in slots[19]["target_functions"]
    assert "ubnt_poll_host_is_ap_valid" in slots[22]["target_functions"]


def test_umac_state_machine_and_step_1c(re_report: dict) -> None:
    sm = re_report["umac_state_machine_and_step1c"]
    param_names = [p["name"] for p in sm["umac_module_parameters"]]
    assert len(param_names) == 15
    assert "ubnt_op_mode" in param_names
    assert "is_ubnt_ff" in param_names
    assert "is_ubnt_ptp" in param_names
    assert "host_80211_enable" in param_names

    ni_ext = sm["ieee80211_node_ubnt_extensions"]
    assert ni_ext["ni_ubnt_poll"]["struct_offset"] == "0x23e8"
    assert "0x23a4" in ni_ext["ni_ubnt_hostname"]["struct_offset"]

    gates = sm["sta_5_gate_association_state_machine"]
    assert gates["gate_1_beacon_rx_dual_list"]["offset"] == "0x8afc"
    assert "0x43176c" in gates["gate_2_userspace_wpad_filter"]["wpad_gate_check"]
    assert "0x450fc" in gates["gate_3_kernel_candidate_ap_match"]["umac_caller"]
    assert "0x92bc" in gates["gate_4_assoc_req_tx"]["uph_function"]
    assert "0xa05c" in gates["gate_5_assoc_resp_rx_and_sta_connect"]["uph_assoc_resp_function"]


def test_airprism_and_ath_dev_spectral_filter(re_report: dict) -> None:
    ap = re_report["airprism_and_ath_dev_callgraph"]
    prism = ap["umac_ubnt_prism_hook"]
    assert prism["text_offset"] == "0xac874"
    assert prism["size_bytes"] == 468
    assert len(prism["callers_in_umac"]) == 3
    assert prism["gpio_pins"] == {
        "stage1_bit0_gpio": 15,
        "stage1_bit1_gpio": 16,
        "stage2_bit0_gpio": 13,
        "stage2_bit1_gpio": 14,
    }
    ftable = prism["ubnt_prism_filters_table"]
    assert ftable["offset"] == "0x1510"
    assert ftable["size_bytes"] == 264
    assert ftable["entry_count"] == 6
    assert ftable["entries"][0]["stage"] == 1
    assert ftable["entries"][0]["freq_min_mhz"] == 5150
    assert ftable["entries"][0]["freq_max_mhz"] == 5250
    assert ftable["entries"][0]["gpio_stage_mask_hex"] == "0x00018000"
    assert ftable["entries"][2]["stage"] == 2
    assert ftable["entries"][2]["gpio_stage_mask_hex"] == "0x00006000"

    spec = ap["ath_dev_spectral_filter_subsystem"]
    assert spec["identical_in_wa_and_xc"] is True
    assert spec["gpio_pin"] == 21
    assert spec["irq_number"] == 64
    assert spec["irq_devname"] == "ath-spectral-filter"
    assert spec["functions"]["ath_spectral_filter_init"]["text_offset"] == "0x27c00"
    assert spec["functions"]["ath_spectral_filter_uninit"]["text_offset"] == "0x27c7c"
    assert spec["functions"]["ath_spectral_filter_start"]["text_offset"] == "0x27cac"
    assert spec["functions"]["ath_spectral_filter_stop"]["text_offset"] == "0x27cb4"
