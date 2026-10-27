"""Unit tests for controller/guarida_closed_loop_rollout_verifier.py (T-ORCA-GEM2-03)."""

from __future__ import annotations

import pytest

from controller.guarida_closed_loop_rollout_verifier import (
    AlmafuerteCakeTreeConfig,
    Panel2ModeBTuningConfig,
    Panel3ModeASoftTdmaConfig,
    RollbackProbeTick,
    RolloutWatchdogThresholdSpec,
    compute_harmonic_downlink_rate,
    compute_mann_whitney_u,
    compute_paired_bootstrap_ci,
    compute_weighted_harmonic_downlink_rate,
    evaluate_15s_rollback_watchdog,
    generate_guarida_closed_loop_rollout_report,
)


def test_almafuerte_46mbps_cake_tree_invariants() -> None:
    cfg = AlmafuerteCakeTreeConfig()
    val = cfg.validate_invariants()
    assert val["valid"] is True
    assert val["guaranteed_min_sum_mbps"] == pytest.approx(46.0)
    assert cfg.panel1_min_mbps + cfg.panel2_min_mbps + cfg.panel3_min_mbps == pytest.approx(46.0)
    assert cfg.protected_poe_interface == "ether2-sw-poe200"
    assert cfg.automatic_execution_allowed is False
    assert "diffserv4" in cfg.cake_flags
    assert "ack-filter" in cfg.cake_flags


def test_panel2_mode_b_rodata_cms_bias6_and_voip_bias6_tables() -> None:
    cfg = Panel2ModeBTuningConfig(cms_bias=6, voip_bias=6, daprot=1)
    diff = cfg.get_rodata_profile_diff()
    assert diff["cms_bias_before"] == 0
    assert diff["cms_bias_after"] == 6
    assert diff["retr_suppression_before"]["ul_per_thresh_nr_pct"] == 100
    assert diff["retr_suppression_before"]["txop_qual_thresh_nr_nb_pct"] == 20
    assert diff["retr_suppression_after"]["dl_rate_ratio_thresh_nr"] == 26
    assert diff["retr_suppression_after"]["dl_per_thresh_nr_pct"] == 70
    assert diff["retr_suppression_after"]["ul_rate_ratio_thresh_nr"] == 34
    assert diff["retr_suppression_after"]["ul_per_thresh_nr_pct"] == 65
    assert diff["retr_suppression_after"]["txop_qual_thresh_nr_nb_pct"] == 70

    assert diff["voip_duration_before"]["high_contention_sta_count"] == 4
    assert diff["voip_duration_before"]["high_contention_min_down_dur_us"] == 8000
    assert diff["voip_duration_before"]["high_contention_min_up_dur_us"] == 2000
    assert diff["voip_duration_after"]["high_contention_sta_count"] == 5
    assert diff["voip_duration_after"]["high_contention_min_down_dur_us"] == 15000
    assert diff["voip_duration_after"]["high_contention_min_up_dur_us"] == 7500


def test_panel3_mode_a_soft_tdma_k3_effective_contenders() -> None:
    cfg = Panel3ModeASoftTdmaConfig()
    assert cfg.rts_threshold_bytes == 256
    assert cfg.phase_count_k == 3
    assert cfg.epoch_duration_ms == pytest.approx(7.5)
    assert cfg.phase_slot_width_us == 2500
    # N=6, K=3, alpha=0.92 -> 1 + 5*(0.92/3 + 0.08) = 2.933
    assert cfg.effective_contenders_per_phase == pytest.approx(2.933, abs=1e-3)
    assert cfg.zero_touch_stock_airos_bench_gate_required is True
    assert cfg.barrios_countrycode_511_prereq_required is True
    assert cfg.automatic_execution_allowed is False


def test_harmonic_downlink_rate_and_franco_debora_remediation() -> None:
    # Confirmed 7-CPE Panel2 DL capacities from guarida_72h_interim_audit_20261024.json
    panel2_7cpe = [10.1, 79.0, 86.3, 90.5, 104.1, 109.2, 142.0]
    h_unweighted = compute_harmonic_downlink_rate(panel2_7cpe)
    assert h_unweighted == pytest.approx(43.72, abs=0.05)

    # Capping FRANCO_Debora's TDMA airtime weight to 0.35 via cms_bias=6 + BNG CAKE
    h_weighted = compute_weighted_harmonic_downlink_rate(
        panel2_7cpe, [0.35, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    )
    assert h_weighted > 65.0

    # Post physical dish realignment of FRANCO_Debora (10.1 -> 79.0 Mbps)
    realigned = [79.0, 79.0, 86.3, 90.5, 104.1, 109.2, 142.0]
    h_realigned = compute_harmonic_downlink_rate(realigned)
    assert h_realigned == pytest.approx(94.90, abs=0.05)


def test_mann_whitney_u_and_paired_bootstrap_ci_accuracy() -> None:
    pre = [32.0, 35.0, 41.0, 29.0, 38.0, 44.0, 52.0, 60.0, 33.0, 37.0, 48.0, 55.0]
    post = [11.0, 12.5, 14.0, 10.5, 13.0, 15.0, 16.5, 18.0, 11.5, 12.0, 14.5, 17.0]

    mw = compute_mann_whitney_u(pre, post, metric_name="test_rtt_ms")
    assert mw.u_statistic == pytest.approx(0.0)
    assert mw.z_score < -3.5
    assert mw.p_value_two_sided < 0.001
    assert mw.rank_biserial_r == pytest.approx(-1.0)
    assert mw.hodges_lehmann_shift < -20.0
    assert mw.statistically_significant_alpha_0_05 is True

    ci_p50 = compute_paired_bootstrap_ci(pre, post, metric_name="test_rtt_ms", statistic="p50", n_bootstrap=1000)
    ci_p95 = compute_paired_bootstrap_ci(pre, post, metric_name="test_rtt_ms", statistic="p95", n_bootstrap=1000)
    ci_p99 = compute_paired_bootstrap_ci(pre, post, metric_name="test_rtt_ms", statistic="p99", n_bootstrap=1000)
    assert ci_p50.observed_delta < -20.0
    assert ci_p50.ci_upper_95 < -15.0
    assert ci_p50.zero_excluded_from_ci is True
    assert ci_p95.ci_upper_95 < -25.0
    assert ci_p99.ci_upper_95 < -30.0


def test_15_second_watchdog_sustained_breach_vs_transient_and_backhaul_isolation() -> None:
    thresholds = RolloutWatchdogThresholdSpec()

    # 1. Sustained 15-second (3 x 5s ticks) RF p95 & harmonic DL regression -> automatic rollback at t=15.0s
    sustained_stream = [
        RollbackProbeTick(
            tick_index=i,
            elapsed_seconds=(i + 1) * 5.0,
            treatment_stage="Stage3_Panel3_ModeA_RTS256B_SoftTDMA_K3",
            pure_rf_p50_rtt_ms=26.0,
            pure_rf_p95_rtt_ms=49.0,  # > 35.0 ms
            pure_rf_p99_rtt_ms=70.0,  # > 55.0 ms
            pure_rf_loss_pct=2.1,  # > 1.0%
            core_backhaul_p95_rtt_ms=9.5,
            core_backhaul_loss_pct=0.1,
            harmonic_dl_rate_mbps=60.0,  # < 0.90 * 74.5
            baseline_harmonic_dl_rate_mbps=74.5,
            min_cpe_ccq_pct=72.0,
            associated_cpe_count=6,
            expected_cpe_count=6,
        )
        for i in range(4)
    ]
    v_sustained = evaluate_15s_rollback_watchdog(sustained_stream, thresholds=thresholds)
    assert v_sustained.rollback_triggered is True
    assert v_sustained.decision == "AUTOMATIC_15S_ROLLBACK_TRIGGERED"
    assert v_sustained.trigger_time_seconds == pytest.approx(15.0)
    assert v_sustained.consecutive_breach_seconds == pytest.approx(15.0)
    assert len(v_sustained.rollback_commands_to_execute) > 0

    # 2. Single 5-second transient spike followed by recovery -> NO rollback
    transient_stream = [
        RollbackProbeTick(
            tick_index=0,
            elapsed_seconds=5.0,
            treatment_stage="Stage2_Panel2_ModeB_cms_bias6_voip_bias6",
            pure_rf_p50_rtt_ms=24.0,
            pure_rf_p95_rtt_ms=41.0,  # single tick breach
            pure_rf_p99_rtt_ms=50.0,
            pure_rf_loss_pct=0.3,
            core_backhaul_p95_rtt_ms=9.5,
            core_backhaul_loss_pct=0.1,
            harmonic_dl_rate_mbps=70.0,
            baseline_harmonic_dl_rate_mbps=43.72,
            min_cpe_ccq_pct=84.0,
            associated_cpe_count=22,
            expected_cpe_count=22,
        ),
        RollbackProbeTick(
            tick_index=1,
            elapsed_seconds=10.0,
            treatment_stage="Stage2_Panel2_ModeB_cms_bias6_voip_bias6",
            pure_rf_p50_rtt_ms=16.0,
            pure_rf_p95_rtt_ms=27.0,  # recovered
            pure_rf_p99_rtt_ms=34.0,
            pure_rf_loss_pct=0.2,
            core_backhaul_p95_rtt_ms=9.5,
            core_backhaul_loss_pct=0.1,
            harmonic_dl_rate_mbps=71.8,
            baseline_harmonic_dl_rate_mbps=43.72,
            min_cpe_ccq_pct=85.0,
            associated_cpe_count=22,
            expected_cpe_count=22,
        ),
    ]
    v_transient = evaluate_15s_rollback_watchdog(transient_stream, thresholds=thresholds)
    assert v_transient.rollback_triggered is False
    assert v_transient.decision == "KEEP_TREATMENT_VERIFIED"

    # 3. External core backhaul congestion while sector RF is healthy -> isolate backhaul, no false sector rollback
    backhaul_only_stream = [
        RollbackProbeTick(
            tick_index=i,
            elapsed_seconds=(i + 1) * 5.0,
            treatment_stage="Stage2_Panel2_ModeB_cms_bias6_voip_bias6",
            pure_rf_p50_rtt_ms=15.5,
            pure_rf_p95_rtt_ms=25.0,
            pure_rf_p99_rtt_ms=32.0,
            pure_rf_loss_pct=0.15,
            core_backhaul_p95_rtt_ms=48.0,
            core_backhaul_loss_pct=6.18,
            harmonic_dl_rate_mbps=71.85,
            baseline_harmonic_dl_rate_mbps=43.72,
            min_cpe_ccq_pct=84.0,
            associated_cpe_count=22,
            expected_cpe_count=22,
        )
        for i in range(4)
    ]
    v_isolated = evaluate_15s_rollback_watchdog(backhaul_only_stream, thresholds=thresholds)
    assert v_isolated.rollback_triggered is False
    assert v_isolated.decision == "ISOLATE_EXTERNAL_BACKHAUL_KEEP_SECTOR_TREATMENT"
    assert v_isolated.root_cause_classification == "EXTERNAL_CORE_BACKHAUL_CONGESTION_ISOLATED"


def test_full_guarida_closed_loop_rollout_report_passes_all_stages() -> None:
    report = generate_guarida_closed_loop_rollout_report()
    assert report["task_id"] == "T-ORCA-GEM2-03"
    assert report["automatic_execution_allowed"] is False
    assert report["safety_boundaries"]["live_devices_touched"] is False

    verifications = report["causal_verifications"]
    for stage_key in (
        "stage1_almafuerte_46mbps_cake",
        "stage2_panel2_mode_b_cms6_voip6",
        "stage3_panel3_mode_a_rts256b_soft_tdma_k3",
    ):
        stage_res = verifications[stage_key]
        assert stage_res["causal_verification_passed"] is True
        assert stage_res["watchdog_15s_verdict"]["rollback_triggered"] is False
        assert stage_res["paired_bootstrap_95ci"]["rtt_p95_ms"]["ci_upper_95"] < 0.0
        assert stage_res["paired_bootstrap_95ci"]["packet_loss_pct"]["ci_upper_95"] < 0.0
        assert stage_res["paired_bootstrap_95ci"]["harmonic_dl_mbps"]["ci_lower_95"] > 0.0
