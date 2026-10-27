"""Stage 74B Tests: Champion v20, XW Rate-Warmup Guard & FMX-DISC-18..20 Promotion (`tests/test_stage74b_champion_v20_promotion.py`)."""

from __future__ import annotations

from pathlib import Path

from tools.deploy.guarida_stage29b_deploy_packager import (
    STAGE55A_CHAMPION_V19,
    STAGE72A_CHAMPION_V20,
    STAGE72A_XC_PTMP_STATION_V20_COMMANDS,
    STAGE72A_XW_RATE_WARMUP_GUARD_SPEC,
    STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6,
    STAGE74B_RECEIPT_PATH,
    build_guarida_stage29b_and_stage48b_deploy_bundle,
    build_stage66a_curated_all_champions_deploy_package,
    export_stage74b_champion_v20_receipt,
    render_stage72a_xc_ptmp_station_v20_script,
)

ROOT_DIR = Path(__file__).resolve().parents[1]


def test_stage74b_champion_v20_profile_and_xw_warmup_guard_exported() -> None:
    """Verify STAGE72A_CHAMPION_V20 and STAGE72A_XW_RATE_WARMUP_GUARD_SPEC are exported with all invariants."""
    assert STAGE72A_CHAMPION_V20["champion_id"] == "STAGE72A_CHAMPION_V20"
    assert STAGE72A_CHAMPION_V20["profile_id"] == "S72A-R4-WARMED-AP-V19-XC-S70C-CHAMPION-V20"
    assert STAGE72A_CHAMPION_V20["supersedes_champion_id"] == "STAGE55A_CHAMPION_V19"
    assert STAGE72A_CHAMPION_V20["openwrt_ap_and_wa_cpe_profile"] == STAGE55A_CHAMPION_V19

    aql_inv = STAGE72A_CHAMPION_V20["openwrt_ap_ac_be_aql_invariant"]
    assert aql_inv["discovery_id"] == "FMX-DISC-19"
    assert aql_inv["ac_be_low_us"] == 1500
    assert aql_inv["ac_be_high_us"] == 3000
    assert aql_inv["aql_threshold_us"] == 5000

    xc_params = STAGE72A_CHAMPION_V20["xc_ptmp_station_s70c_parameters"]
    assert xc_params["wifi0_AMPDUFrames"] == 24
    assert xc_params["wifi0_aggr_swretry"] == 4
    assert xc_params["wifi0_nonaggr_swretry"] == 4
    assert xc_params["ath0_set_multiq"] == 1
    assert xc_params["umac_enable_tx_tcp_cksum"] == 1
    assert xc_params["netdev_budget"] == 800
    assert xc_params["tcp_limit_output_bytes"] == 98304
    assert xc_params["uph_wifi0_daprot"] == 2
    assert xc_params["uph_wifi0_ff_mcast_airtime_limit"] == 5
    assert xc_params["ff_mcast_written_last_fmx_disc_11"] is True

    assert STAGE72A_XW_RATE_WARMUP_GUARD_SPEC["discovery_id"] == "FMX-DISC-18"
    assert STAGE72A_XW_RATE_WARMUP_GUARD_SPEC["icmp_packet_count_per_station"] == 10
    assert STAGE72A_XW_RATE_WARMUP_GUARD_SPEC["icmp_payload_bytes"] == 1200

    script = render_stage72a_xc_ptmp_station_v20_script()
    assert script.startswith("#!/bin/sh\n")
    assert "iwpriv wifi0 AMPDUFrames 24" in script
    assert "iwpriv ath0 set_multiq 1" in script
    assert "echo 2 > /proc/sys/dev/uph_wifi0/daprot" in script
    assert STAGE72A_XC_PTMP_STATION_V20_COMMANDS[-1].endswith(
        "echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit 2>/dev/null || true"
    )


def test_stage74b_receipt_and_bundles_preserve_all_champions() -> None:
    """Verify Stage 74B receipt and bundles preserve STAGE55A_CHAMPION_V19, STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6, and STAGE72A_CHAMPION_V20."""
    receipt = export_stage74b_champion_v20_receipt()
    assert STAGE74B_RECEIPT_PATH.exists()
    assert receipt["stage"] == "74B"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["stage72a_champion_v20"]["champion_id"] == "STAGE72A_CHAMPION_V20"
    assert (
        receipt["stage73a_pbe5ac_lbe5ac_airos8_ptp_champion_v6"]["champion_id"]
        == STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6["champion_id"]
    )
    assert "stage72a_xc_ptmp_station_v20_script_sha256" in receipt["scripts"]

    s66a_pkg = build_stage66a_curated_all_champions_deploy_package()
    assert "stage72a_champion_v20" in s66a_pkg
    assert "stage55a_champion_v19" in s66a_pkg
    assert s66a_pkg["validation_gate"]["stage72a_champion_v20_verified"] is True

    full_bundle = build_guarida_stage29b_and_stage48b_deploy_bundle()
    assert "stage72a_champion_v20" in full_bundle
    assert full_bundle["safety_invariants_verified"]["all_safety_checks_passed"] is True
    assert full_bundle["safety_invariants_verified"]["protects_ether2_sw_poe200"] is True


def test_stage74b_curated_docs_respect_line_budget_and_include_fmx_disc_18_to_20() -> None:
    """Verify the 3 curated docs stay strictly < 250 lines with <= 1 doc-head and document FMX-DISC-18..20 & Champion v20."""
    curated_paths = [
        ROOT_DIR / "docs" / "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md",
        ROOT_DIR / "docs" / "MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md",
        ROOT_DIR / "docs" / "CURRENT_STATE.md",
    ]
    for path in curated_paths:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) < 250, f"{path.name} has {len(lines)} lines (must be < 250)"
        assert text.count("<!-- doc-head:") <= 1, f"{path.name} has multiple doc-head blocks"
        for token in ("FMX-DISC-18", "FMX-DISC-19", "FMX-DISC-20", "v20"):
            assert token in text, f"{path.name} missing required token '{token}'"
