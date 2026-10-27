from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from tools.qca988x.channel_capture_and_sdr_correlator import (
    build_pb_021_022_024_qualification_fixture,
    build_rx_ppdu_end_bytes,
    compute_2x2_svd_metrics,
    evaluate_pb_021_qualification,
    evaluate_pb_022_and_pb_024_sdr_correlation,
    parse_rx_ppdu_end_bytes,
    summarize_2x2_subcarrier_matrices,
    synthesize_cabled_2x2_tone_matrices,
    write_pb_021_022_024_qualification_fixture_json,
)


def test_parse_rx_ppdu_end_bytes_extracts_exact_ar9888_flags() -> None:
    raw = build_rx_ppdu_end_bytes(
        tsf_timestamp_us=1234567,
        wb_timestamp_us=2345678,
        locationing_ticks=40,
        txbf_h_info=True,
        bb_captured_channel=True,
        ppdu_done=True,
        bb_length_bytes=448,
        rtt_corr_value=19500,
        stream0_evm_db=-30,
        stream1_evm_db=-25,
    )
    parsed = parse_rx_ppdu_end_bytes(raw)
    assert parsed.tsf_timestamp_us == 1234567
    assert parsed.wb_timestamp_us == 2345678
    assert parsed.locationing_timestamp_80mhz_ticks == 40
    assert parsed.locationing_sub_us_ns == 500.0
    assert parsed.txbf_h_info is True
    assert parsed.bb_captured_channel is True
    assert parsed.ppdu_done is True
    assert parsed.bb_length_bytes == 448
    assert parsed.rtt_corr_value == 19500
    assert parsed.mean_stream0_evm_db == -30.0
    assert parsed.mean_stream1_evm_db == -25.0


def test_pb_021_qualification_pass_and_rollback_triggers() -> None:
    descs = [
        parse_rx_ppdu_end_bytes(
            build_rx_ppdu_end_bytes(bb_captured_channel=True, bb_length_bytes=224)
        )
        for _ in range(8)
    ]
    res_pass = evaluate_pb_021_qualification(
        descriptors=descs,
        packet_correlated_memory_diff_bytes=224,
        packet_loss_pct=0.5,
    )
    assert res_pass["qualification_verdict"] == "PASS"
    assert res_pass["rollback_triggered"] is False

    res_fail_loss = evaluate_pb_021_qualification(
        descriptors=descs,
        packet_correlated_memory_diff_bytes=224,
        packet_loss_pct=6.5,
    )
    assert res_fail_loss["qualification_verdict"] == "FAIL"
    assert res_fail_loss["rollback_triggered"] is True
    assert res_fail_loss["rollback_action"] == "ROLLBACK_TO_UNPATCHED_ATH10K"


def test_compute_2x2_svd_metrics_orthogonal_vs_rank1() -> None:
    # Orthogonal 2x2 identity matrix: sigma1 == sigma2 == 1.0, cond_db == 0.0 dB
    svd_ortho = compute_2x2_svd_metrics(1.0 + 0j, 0.0 + 0j, 0.0 + 0j, 1.0 + 0j)
    assert math.isclose(svd_ortho.sigma1, 1.0, rel_tol=1e-4)
    assert math.isclose(svd_ortho.sigma2, 1.0, rel_tol=1e-4)
    assert math.isclose(svd_ortho.condition_number_linear, 1.0, rel_tol=1e-4)
    assert math.isclose(svd_ortho.condition_number_db, 0.0, abs_tol=1e-3)

    # Rank-1 keyhole matrix [[1, 1], [1, 1]]: sigma1 == 2.0, sigma2 == 0.0
    svd_rank1 = compute_2x2_svd_metrics(1.0 + 0j, 1.0 + 0j, 1.0 + 0j, 1.0 + 0j)
    assert math.isclose(svd_rank1.sigma1, 2.0, rel_tol=1e-4)
    assert math.isclose(svd_rank1.sigma2, 0.0, abs_tol=1e-6)
    assert svd_rank1.condition_number_db > 100.0
    assert svd_ortho.shannon_capacity_bits_per_s_hz > svd_rank1.shannon_capacity_bits_per_s_hz


def test_pb_022_and_024_sdr_correlation_and_fixture(tmp_path: Path) -> None:
    out_file = tmp_path / "pb_021_022_024_qualification_fixture.json"
    fixture = write_pb_021_022_024_qualification_fixture_json(out_file)
    assert out_file.exists()

    loaded = json.loads(out_file.read_text(encoding="utf-8"))
    assert loaded["live_devices_touched"] is False
    assert loaded["automatic_execution_allowed"] is False
    assert loaded["pb_021_channel_dump_qualification"]["qualification_verdict"] == "PASS"

    corr = loaded["pb_022_024_rank_and_sdr_correlation"]
    assert corr["cabled_states_evaluated"] == 5
    assert corr["singular_value_ratio_pearson_r"] >= 0.90
    assert corr["subcarrier_phase_slope_rmse_rad"] <= 0.05
    assert corr["pb_022_qualification_verdict"] == "PASS"
    assert corr["pb_024_qualification_verdict"] == "PASS"
    assert fixture["task_id"] == "T-PB-GEM2-04"
