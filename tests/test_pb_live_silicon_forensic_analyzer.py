"""Unit tests for Live PB-021/031/050 Silicon Measurement Analyzer & Calibration-Table Forensic Verifier."""

from __future__ import annotations

from pathlib import Path

from analysis.pb_live_silicon_forensic_analyzer import (
    DEFAULT_OUTPUT_FORENSIC_PATH,
    generate_pb_live_silicon_forensic_report,
)


def test_pb_050_clock_and_coverage_class_formulas_bit_exact(tmp_path: Path) -> None:
    out_file = tmp_path / "forensic.json"
    rep = generate_pb_live_silicon_forensic_report(output_path=out_file)
    pb050 = rep["pb_050_clock_and_timing_forensics"]

    assert pb050["mac_core_clock_hz"] == 88000000
    assert pb050["formula_bit_exact_across_all_classes"] is True
    assert pb050["coverage_classes_verified"] == 7
    assert abs(pb050["silicon_clock_median_error_ppm"]) < 10.0
    assert pb050["sub_50us_host_tdma_feasible"] is False
    assert pb050["minimum_safe_host_hmac_epoch_us"] >= 1000


def test_pb_021_dual_chain_calibration_tables_decoded(tmp_path: Path) -> None:
    out_file = tmp_path / "forensic.json"
    rep = generate_pb_live_silicon_forensic_report(output_path=out_file)
    pb021 = rep["pb_021_chan_tab_and_chaninfo_forensics"]

    assert pb021["chaninfo_ctrl_0x2a370_hex"] == "0x000004c8"
    assert pb021["chaninfomem_s2_read_bank"] == 1
    assert pb021["chaninfo_20mhz_subband_select"] == 3
    assert pb021["non_zero_words_chain0"] == 16
    assert pb021["non_zero_words_chain1"] == 16
    assert len(pb021["subband_calibration_triplets"]) == 5
    assert pb021["pb_021_forensic_verdict"] == "CONFIRMED_ON_SILICON_NON_ZERO_DUAL_CHAIN_CALIBRATION_BANKS"


def test_pb_031_ldpc_and_ampdu_authority_and_determinism(tmp_path: Path) -> None:
    out_file = tmp_path / "forensic.json"
    r1 = generate_pb_live_silicon_forensic_report(output_path=out_file)
    r2 = generate_pb_live_silicon_forensic_report(output_path=out_file)

    assert r1["forensic_report_sha256"] == r2["forensic_report_sha256"]
    pb031 = r1["pb_031_ldpc_and_ampdu_forensics"]
    assert pb031["ldpc_decoder_budget_cycles_88mhz"] == 800
    assert pb031["htt_amsdu_ampdu_transitions_verified"] is True
    assert pb031["tested_ampdu_depths"] == [16, 32, 64]
    assert r1["restoration_verified_clean"] is True
    assert DEFAULT_OUTPUT_FORENSIC_PATH.exists()
