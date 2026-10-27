"""Unit and integration tests for Stage 12 Multi-Sector Tower Conflict-Graph & Pareto Optimizer."""

from __future__ import annotations

import json
from pathlib import Path

from controller.tower_conflict_graph_optimizer import (
    compute_pareto_front,
    compute_spatial_isolation_db,
    compute_spectral_rejection_db,
    compute_tdd_sync_isolation_db,
    evaluate_tower_configuration,
    optimize_tower_plan,
    select_prism_filter_entries,
)
from tools.sim.fmx_multi_sector_tower_pareto_sim import (
    build_6sector_high_density_specs,
    build_guarida_3sector_specs,
)


def test_umac_prism_hook_6entry_band_edge_selector() -> None:
    """Verify exact 6-entry umac.ko:ubnt_prism_hook GPIO 13..16 band-edge selection (Stage 11A F05)."""
    # 1. U-NII-3 5805 MHz / 20 MHz (5795..5815 MHz): Stage 1 -> Entry #1 (0x08000), Stage 2 -> Entry #3 (0x04000)
    u3_20 = select_prism_filter_entries(5805, 20)
    assert u3_20["stage1_entry"] == 1
    assert u3_20["stage2_entry"] == 3
    assert u3_20["stage1_gpio_val"] == 0x08000
    assert u3_20["stage2_gpio_val"] == 0x04000
    assert u3_20["is_narrow_high_q_passband"] is True

    # 2. Band-edge check (F05): 5240 MHz / 80 MHz spans 5200..5280 MHz (> 5250 MHz of Entry #0),
    # so Stage 1 must fall through to Entry #4 (Wideband Fallback 0x10000), while Stage 2 matches Entry #2 (5200..5300).
    f05_case = select_prism_filter_entries(5240, 80)
    assert f05_case["lower_edge_mhz"] == 5200
    assert f05_case["upper_edge_mhz"] == 5280
    assert f05_case["stage1_entry"] == 4
    assert f05_case["stage2_entry"] == 2
    assert f05_case["is_narrow_high_q_passband"] is False


def test_spatial_spectral_and_tdd_sync_isolation_monotonicity() -> None:
    """Verify spatial isolation, AirPrism vs WA spectral rejection, and GPS TDD sync isolation."""
    iso_60_wa = compute_spatial_isolation_db(0.0, 60.0, "WA_UNFILTERED_LAP", "WA_UNFILTERED_LAP")
    iso_120_wa = compute_spatial_isolation_db(0.0, 120.0, "WA_UNFILTERED_LAP", "WA_UNFILTERED_LAP")
    iso_180_wa = compute_spatial_isolation_db(0.0, 180.0, "WA_UNFILTERED_LAP", "WA_UNFILTERED_LAP")
    iso_120_xc = compute_spatial_isolation_db(0.0, 120.0, "XC_AIRPRISM_GEN2", "XC_AIRPRISM_GEN2")

    assert iso_60_wa < iso_120_wa < iso_180_wa
    assert iso_120_xc >= iso_120_wa + 6.9

    # Adjacent-channel spectral rejection at G=0 MHz (5735 vs 5755 @ 20 MHz) and G=30 MHz (5735 vs 5785 @ 20 MHz)
    rej_wa_g0 = compute_spectral_rejection_db(5735, 20, 5755, 20, "WA_UNFILTERED_LAP", "WA_UNFILTERED_LAP")
    rej_wa_g30 = compute_spectral_rejection_db(5735, 20, 5785, 20, "WA_UNFILTERED_LAP", "WA_UNFILTERED_LAP")
    rej_xc_g0 = compute_spectral_rejection_db(5735, 20, 5755, 20, "XC_AIRPRISM_GEN2", "WA_UNFILTERED_LAP")

    assert rej_wa_g30 > rej_wa_g0 + 15.0
    assert rej_xc_g0 >= rej_wa_g0 + 16.0

    # TDD sync isolation
    sync_csma = compute_tdd_sync_isolation_db("MODE_A_OPENWRT_CSMA_AQL", "MODE_B_AIRMAX_TDMA", 120.0)
    sync_unsync_tdma = compute_tdd_sync_isolation_db("MODE_B_AIRMAX_TDMA", "MODE_B_AIRMAX_TDMA", 120.0)
    sync_gps_120 = compute_tdd_sync_isolation_db("MODE_B_GPS_SYNC_TDMA", "MODE_B_GPS_SYNC_TDMA", 120.0)
    sync_gps_180 = compute_tdd_sync_isolation_db("MODE_B_GPS_SYNC_TDMA", "MODE_B_GPS_SYNC_TDMA", 180.0)

    assert sync_csma < sync_unsync_tdma < sync_gps_120 < sync_gps_180


def test_regulatory_eirp_and_mode_b_gate_constraints() -> None:
    """Verify EIRP cap and AGENTS.md Section 14 Rule #2 Mode B gate violations are caught."""
    specs = build_guarida_3sector_specs()

    # Valid baseline configuration is feasible
    base_res = evaluate_tower_configuration(
        sectors=specs,
        frequencies_mhz=[5735, 5805, 5755],
        widths_mhz=[20, 20, 20],
        tx_powers_dbm=[20, 20, 20],
        mac_modes=["MODE_A_OPENWRT_CSMA_AQL", "MODE_B_AIRMAX_TDMA", "MODE_B_AIRMAX_TDMA"],
    )
    assert base_res["is_feasible"] is True
    assert base_res["automatic_execution_allowed"] is False

    # Illegal Mode A on Panel2-Guarida (22 CPEs, canary_mode_a_eligible=False) must fail gate
    illegal_mode = evaluate_tower_configuration(
        sectors=specs,
        frequencies_mhz=[5735, 5805, 5755],
        widths_mhz=[20, 20, 20],
        tx_powers_dbm=[20, 20, 20],
        mac_modes=["MODE_A_OPENWRT_CSMA_AQL", "MODE_A_OPENWRT_CSMA_AQL", "MODE_B_AIRMAX_TDMA"],
    )
    assert illegal_mode["mode_gate_violations"] >= 1
    assert illegal_mode["is_feasible"] is False

    # Illegal EIRP (> 36 dBm with 16 dBi antenna -> TX > 20 dBm) must flag eirp_violations_db
    illegal_eirp = evaluate_tower_configuration(
        sectors=specs,
        frequencies_mhz=[5735, 5805, 5755],
        widths_mhz=[20, 20, 20],
        tx_powers_dbm=[20, 24, 20],
        mac_modes=["MODE_A_OPENWRT_CSMA_AQL", "MODE_B_AIRMAX_TDMA", "MODE_B_AIRMAX_TDMA"],
    )
    assert illegal_eirp["eirp_violations_db"] > 0.0
    assert illegal_eirp["is_feasible"] is False


def test_guarida_3sector_and_6sector_pareto_optimization() -> None:
    """Verify conflict-graph + NSGA-II Pareto optimization on Guarida 3-sector and 6-sector towers."""
    guarida_specs = build_guarida_3sector_specs()
    wa_opt = optimize_tower_plan(
        sectors=guarida_specs,
        hardware_overrides=["WA_UNFILTERED_LAP", "WA_UNFILTERED_LAP", "WA_UNFILTERED_LAP"],
        pop_size=32,
        n_gen=20,
        seed=20261024,
    )
    prism_opt = optimize_tower_plan(
        sectors=guarida_specs,
        hardware_overrides=["WA_UNFILTERED_LAP", "XC_AIRPRISM_GEN2", "WA_UNFILTERED_LAP"],
        pop_size=32,
        n_gen=20,
        seed=20261024,
    )

    base = wa_opt["baseline_evaluation"]
    wa_plan = wa_opt["recommended_knee_point_plan"]
    prism_plan = prism_opt["recommended_knee_point_plan"]

    assert wa_plan["is_feasible"] is True
    assert prism_plan["is_feasible"] is True
    assert wa_plan["total_tower_goodput_mbps"] > base["total_tower_goodput_mbps"] * 1.35
    assert wa_plan["worst_sector_p95_rtt_ms"] < base["worst_sector_p95_rtt_ms"] * 0.70
    assert prism_plan["total_tower_goodput_mbps"] > wa_plan["total_tower_goodput_mbps"]
    assert prism_plan["total_weak_starvation_penalty"] < wa_plan["total_weak_starvation_penalty"]


def test_saved_guarida_pareto_artifact_integrity() -> None:
    """Verify saved JSON artifact exists, contains non-dominated Pareto fronts, and enforces safety flags."""
    path = Path("artifacts/ptmp_sim/guarida_3sector_pareto_front_20261024.json")
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["study_id"] == "FMX-STAGE12-MULTI-SECTOR-TOWER-CONFLICT-GRAPH-PARETO-20261024"
    assert data["automatic_execution_allowed"] is False

    g = data["guarida_3sector_comparison"]
    assert len(g["wa_hybrid_pareto_front"]) >= 5
    assert len(g["prism_panel2_pareto_front"]) >= 5
    assert g["summary_deltas"]["wa_hybrid_vs_baseline_goodput_gain_pct"] > 40.0
    assert g["summary_deltas"]["prism_20mhz_vs_baseline_goodput_gain_pct"] > 55.0

    s6 = data["high_density_6sector_96cpe_comparison"]
    assert (
        s6["UPGRADED_6SECTOR_XC_AIRPRISM_GEN2_GPS_SYNC"]["total_tower_goodput_mbps"]
        > s6["OPTIMIZED_6SECTOR_WA_GPS_SYNC"]["total_tower_goodput_mbps"]
        > s6["BASELINE_6SECTOR_WA_UNSYNCED"]["total_tower_goodput_mbps"]
    )
