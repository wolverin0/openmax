#!/usr/bin/env python3
"""
Tests for Stage 70A (`T-S70A-UBNT-POLL-HOST-KO-AND-UPH-KO-FULLREA-DISSECTION`):
Verifies deterministic `/fullrea` binary dissection of `ubnt_poll_host.ko` (`WA` `AR9342`) and `uph.ko` (`XC` `QCA9558`),
`allow_80211=1` + `op_mode=0` TDMA poller bypass, `SyncFlex`/`fixed_frame`, `AtpcTarget`/`atpc`, `Timing`/`timing`,
`no_ack_rate`/`noack_mode`/`ro`, `UPH-BUG-01..08`, `ClosedLoopResearchReactor` integration, and `< 250` line doc hygiene.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.re.dissect_stage70a_ubnt_poll_and_uph_ko import (
    OUTPUT_ARTIFACT_JSON,
    REPO_ROOT,
    dissect_allow_80211_and_op_mode_bypass,
    dissect_sysctl_and_hook_control_plane,
    dissect_sysctl_state_variables,
    dissect_uph_bugs_and_suboptimal_constants,
    dissect_wa_vs_xc_binary_identity,
    run_stage70a_dissection_and_reactor,
)

DOC_PATH = REPO_ROOT / "docs" / "STAGE70A_UBNT_POLL_AND_UPH_FULLREA_BINARY_DISSECTION.md"
DISCOVERY_QUEUE_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "discovery_to_research_queue.json"


def test_stage70a_wa_vs_xc_binary_identity_and_5_instruction_diffs() -> None:
    identity = dissect_wa_vs_xc_binary_identity()
    assert identity["claim_status"] == "CONFIRMED"

    sec_id = identity["identical_sections_wa_vs_xc_8725"]
    assert sec_id[".text_size_bytes"] == 101072
    assert sec_id[".rodata_identical"] is True
    assert sec_id[".rodata_size_bytes"] == 26048
    assert sec_id[".rodata.str1.4_identical"] is True
    assert sec_id[".rodata.str1.4_size_bytes"] == 11580
    assert sec_id[".data_identical"] is True
    assert sec_id[".data_size_bytes"] == 832

    assert identity["wa_vs_xc_text_instruction_diffs_count"] == 5
    diff_offsets = [d["text_offset"] for d in identity["wa_vs_xc_text_instruction_diffs"]]
    assert diff_offsets == ["0x00cac", "0x010c0", "0x010f8", "0x18ab0", "0x18ac4"]

    # Verify STA patched module (3 instruction patches: 0x07800 bmiss nop + 0x07c08 timer panic bomb defuse + 0x0a3b8 is_ap_valid=1)
    sta_diffs = {d["text_offset"]: d for d in identity["xc_sta_patched_diffs"]}
    assert set(sta_diffs.keys()) == {"0x07800", "0x07c08", "0x0a3b8"}
    assert sta_diffs["0x07800"]["patched_hex"] == "00000000"
    assert sta_diffs["0x07c08"]["patched_hex"] == "10000006"
    assert sta_diffs["0x0a3b8"]["patched_hex"] == "24020001"

    # Verify AP patched module (5 functions patched: check_sta, on_sta_connect, on_assoc_req_rx, is_ap_valid, proto_insert_ie)
    ap_offsets = [d["text_offset"] for d in identity["xc_ap_patched_diffs"]]
    assert ap_offsets == [
        "0x01860",
        "0x01864",
        "0x08134",
        "0x08138",
        "0x09594",
        "0x09598",
        "0x0a3a4",
        "0x0a3a8",
        "0x0b950",
        "0x0b954",
    ]


def test_stage70a_control_plane_and_allow_80211_op_mode_bypass() -> None:
    cp = dissect_sysctl_and_hook_control_plane()
    assert cp["claim_status"] == "CONFIRMED"
    assert len(cp["rodata_ptmp_netconf_profiles"]) == 8
    for prof in cp["rodata_ptmp_netconf_profiles"]:
        assert prof["cms_bias_default"] == 0
        assert prof["voip_bias_default"] == 0
        assert prof["down_dur_us"] in {8000, 10000, 15000, 30000}

    bypass = dissect_allow_80211_and_op_mode_bypass()
    assert bypass["claim_status"] == "CONFIRMED"
    assert len(bypass["sta_5_gate_bypass_architecture"]) == 5
    assert len(bypass["ap_4_gate_bypass_architecture"]["xc_8725_uph_ap_patched_ko_5_surgical_patches"]) == 5


def test_stage70a_sysctl_state_variables_and_8_bugs() -> None:
    sv = dissect_sysctl_state_variables()
    assert sv["claim_status"] == "CONFIRMED"

    ff_map = sv["SyncFlex_and_fixed_frame"]["frame_duration_enum_mapping"]
    assert ff_map["0_Auto_Flexible"]["ff_frame_dur_us"] == 0
    assert ff_map["1_FF_4ms"]["ff_frame_dur_us"] == 4000
    assert ff_map["2_FF_8ms"]["ff_frame_dur_us"] == 8000
    assert ff_map["3_FF_2ms"]["ff_frame_dur_us"] == 2000
    assert ff_map["4_FF_5ms"]["ff_frame_dur_us"] == 5000
    assert ff_map["5_FF_10ms"]["ff_frame_dur_us"] == 10000
    assert len(sv["SyncFlex_and_fixed_frame"]["vector_10_int_state_map"]) == 10
    assert len(sv["AtpcTarget_and_atpc"]["vector_5_int_state_map"]) == 5
    assert len(sv["Timing_and_timing"]["vector_3_int_state_map"]) == 3

    bugs = dissect_uph_bugs_and_suboptimal_constants()
    assert len(bugs) == 8
    assert [b["bug_id"] for b in bugs] == [
        "UPH-BUG-01",
        "UPH-BUG-02",
        "UPH-BUG-03",
        "UPH-BUG-04",
        "UPH-BUG-05",
        "UPH-BUG-06",
        "UPH-BUG-07",
        "UPH-BUG-08",
    ]
    assert all(b["status"] == "CONFIRMED" for b in bugs)


def test_stage70a_reactor_integration_and_doc_hygiene() -> None:
    payload = run_stage70a_dissection_and_reactor()
    assert OUTPUT_ARTIFACT_JSON.exists()
    loaded = json.loads(OUTPUT_ARTIFACT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "70A"
    assert loaded["verdict"] == "CONFIRMED"

    ev = payload["closed_loop_reactor_event"]
    assert ev["round_id"] == "S70A-UPH-FULLREA"
    synth_ids = [m["mechanism_id"] for m in ev["synthesized_next_mechanisms"]]
    assert "UPH-M1" in synth_ids

    queue_data = json.loads(DISCOVERY_QUEUE_JSON.read_text(encoding="utf-8"))
    round_ids = [e["round_id"] for e in queue_data.get("events", [])]
    assert "S70A-UPH-FULLREA" in round_ids

    assert DOC_PATH.exists()
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    doc_lines = doc_text.splitlines()
    assert len(doc_lines) < 250, f"Expected < 250 lines, got {len(doc_lines)}"
    assert doc_text.count("<!-- doc-head:") == 1
    assert "CONFIRMED" in doc_text
    assert "UPH-BUG-01" in doc_text
    assert "UPH-BUG-08" in doc_text
