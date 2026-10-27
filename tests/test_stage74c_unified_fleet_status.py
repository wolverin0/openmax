"""Unit tests for Stage 74C Unified Fleet Status Snapshot & Command Center v20 Sync."""
from __future__ import annotations

import json
from pathlib import Path

from tools.telemetry.build_stage74c_unified_fleet_status_snapshot import (
    DEFAULT_STAGE74C_OUTPUT_PATH,
    LTU_8BUG_CATALOG,
    REPO_ROOT,
    build_stage74c_unified_fleet_status_snapshot,
    export_stage74c_unified_fleet_status_snapshot,
    load_stage74c_source_artifacts,
)


def test_load_stage74c_source_artifacts_and_sha256() -> None:
    sources = load_stage74c_source_artifacts()
    assert sources["stage69c"]["stage"] == "69C"
    assert sources["stage71b"]["stage_id"] == "Stage 71B"
    assert sources["stage72a"]["stage"] == "72A"
    assert sources["stage73a"]["stage"] == "Stage 73A"
    for key in ("stage69c", "stage71b", "stage72a", "stage73a"):
        assert len(sources["sha256"][key]) == 64


def test_build_stage74c_unifies_all_four_hardware_families() -> None:
    snap = build_stage74c_unified_fleet_status_snapshot()
    assert snap["stage"] == "74C"
    assert snap["safety_contract"]["automatic_execution_allowed"] is False
    assert snap["safety_contract"]["live_devices_touched"] is False
    assert snap["safety_contract"]["flash_writes"] == 0
    assert snap["safety_contract"]["forbidden_poe_interface"] == "ether2-sw-poe200"
    assert snap["summary_kpis"]["hardware_families_unified"] == 4

    fams = snap["hardware_families"]
    assert len(fams) == 4

    # 1. OpenWrt Champion v20
    owrt = fams["family_1_openwrt_ath10k_mac80211"]["active_ptmp_champion"]
    assert owrt["champion_id"] == "STAGE72A_COUPLED_AP_V19_AND_XC_S70C_CHAMPION_V20"
    assert owrt["goodput_delta_pct"] == 7.886
    assert owrt["p95_rtt_delta_pct"] == -2.348
    assert owrt["pareto_score_delta_pct"] == 8.7076
    assert owrt["key_parameters"]["hostapd_oom_score_adj"] == -900
    assert owrt["key_parameters"]["ap_aqm"]["fq_memory_limit_bytes"] == 4194304

    # 2. airOS 8 PtP Champion v6
    airos_ptp = fams["family_2_airos8_wa_xc_ptp_and_ptmp"]["active_ptp_champion"]
    assert airos_ptp["champion_id"] == "STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6"
    assert airos_ptp["round_id"] == "S73A-R1"
    assert airos_ptp["key_parameters"]["uph_wifi0_ptp_xmit"] == 1
    assert airos_ptp["key_parameters"]["uph_wifi0_daprot"] == 2
    assert airos_ptp["key_parameters"]["uph_wifi0_ff_mcast_airtime_limit"] == 5
    assert airos_ptp["key_parameters"]["ff_mcast_written_last_fmx_disc_11"] is True
    assert airos_ptp["metrics"]["loaded_p50_rtt_delta_pct"] == -15.51
    assert airos_ptp["metrics"]["loaded_p95_rtt_delta_pct"] == -8.49
    assert airos_ptp["discarded_rounds_in_stage73a"][0]["round_id"] == "S73A-R2"

    # 3. LTU 8-Bug Fix & 4096-QAM Champion
    ltu = fams["family_3_ltu_beetle_arria10_ame"]
    assert ltu["eight_bug_count"] == 8
    assert len(LTU_8BUG_CATALOG) == 8
    assert (
        ltu["active_champion"]["stage64a_fullrea_binary_patch_loader"][
            "total_overlapped_relocations"
        ]
        == 0
    )

    # 4. airOS 6 M5 XW Cross-Gen Champion
    m5 = fams["family_4_airos6_m5_xw_xm_crossgen"]["active_champion"]
    assert m5["key_parameters"]["netdev_budget_400mhz_ar934x"] == 300
    assert m5["key_parameters"]["br0_txqueuelen"] == 256
    assert m5["key_parameters"]["ubnt_ewma_delegate_on"] == 1


def test_guarida_3panel_32cpe_readiness_and_export(tmp_path: Path) -> None:
    out_path = tmp_path / "stage74c_snapshot.json"
    snap = export_stage74c_unified_fleet_status_snapshot(
        output_path=out_path, refresh_command_center_html=False
    )
    assert out_path.exists()
    loaded = json.loads(out_path.read_text(encoding="utf-8"))

    guarida = loaded["guarida_3panel_32cpe_readiness"]
    assert guarida["panel_count"] == 3
    assert guarida["total_cpes"] == 32
    assert guarida["panel1_cpes"] == 4
    assert guarida["panel2_cpes"] == 22
    assert guarida["panel3_cpes"] == 6
    assert guarida["colocation_rf_summary"]["min_guard_band_mhz"] == 225
    assert guarida["colocation_rf_summary"]["pareto_delta_pct"] == 96.43
    assert guarida["preflight_validation"]["valid"] is True
    assert len(guarida["preflight_validation"]["gates_checked"]) == 14

    assert DEFAULT_STAGE74C_OUTPUT_PATH.exists()
    doc_path = REPO_ROOT / "docs" / "STAGE74C_UNIFIED_FLEET_AND_COMMAND_CENTER_V20_SYNC.md"
    assert doc_path.exists()
    doc_text = doc_path.read_text(encoding="utf-8")
    doc_lines = doc_text.splitlines()
    assert len(doc_lines) < 200
    assert doc_lines[0].startswith("<!-- doc-head:")
    assert doc_text.count("<!-- doc-head:") == 1
