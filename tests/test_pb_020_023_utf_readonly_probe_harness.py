from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.qca988x.utf_readonly_probe_harness import (
    PB023CommandProbeAttempt,
    UTFBenchPreflightConfig,
    UTFReadOnlyCycleRecord,
    compute_iq_tone_correlation_and_snr,
    evaluate_pb020_readonly_cycles,
    evaluate_pb023_adccapture_and_genwaveform_probes,
    synthesize_adc_iq_tone_capture,
    validate_pb020_readonly_command_list,
    verify_utf_bench_preflight,
    write_pb_020_023_utf_probe_fixture_json,
)


def _valid_preflight() -> UTFBenchPreflightConfig:
    return UTFBenchPreflightConfig(
        unit_id="SACRIFICIAL-BENCH-LAP120-LAB",
        is_sacrificial_bench_unit=True,
        is_production_network_device=False,
        rf_ports_terminated_50ohm_or_attenuated_50db=True,
        serial_and_tftp_recovery_verified=True,
        board_data_sha256="a" * 64,
        utf_binary_sha256="b" * 64,
        production_fw_sha256="c" * 64,
    )


def test_preflight_blocks_production_or_unterminated_units() -> None:
    pf_ok = verify_utf_bench_preflight(_valid_preflight())
    assert pf_ok["preflight_passed"] is True
    assert pf_ok["automatic_execution_allowed"] is False

    pf_bad = verify_utf_bench_preflight(
        UTFBenchPreflightConfig(
            unit_id="Panel1-Guarida",
            is_sacrificial_bench_unit=False,
            is_production_network_device=True,
            rf_ports_terminated_50ohm_or_attenuated_50db=False,
            serial_and_tftp_recovery_verified=False,
            board_data_sha256="short",
            utf_binary_sha256="short",
            production_fw_sha256="short",
        )
    )
    assert pf_bad["preflight_passed"] is False
    assert "FORBIDDEN_PRODUCTION_DEVICE_TARGET" in pf_bad["violations"]


def test_pb020_command_allowlist_blocks_mutating_and_noisefloor_reset() -> None:
    validate_pb020_readonly_command_list([9, 15, 18, 42, 76])
    with pytest.raises(ValueError, match="forbidden in PB-020"):
        validate_pb020_readonly_command_list([9, 11])  # CMD_REGWRITE
    with pytest.raises(ValueError, match="forbidden in PB-020"):
        validate_pb020_readonly_command_list([9, 102])  # CMD_NOISEFLOORREAD calls whalReset


def test_pb020_watchdog_triggers_on_reload_gt_30s_or_cmd_timeout() -> None:
    pf = _valid_preflight()
    cycles_bad = [
        UTFReadOnlyCycleRecord(
            cycle_index=idx + 1,
            utf_boot_succeeded=True,
            commands_attempted=[9, 42],
            command_statuses={9: 0, 42: 0},
            max_command_latency_s=0.1,
            unexpected_rf_tx_detected=False,
            wlan_reload_succeeded=True,
            wlan_reload_recovery_time_s=34.5 if idx == 4 else 5.0,
        )
        for idx in range(5)
    ]
    res = evaluate_pb020_readonly_cycles(pf, cycles_bad)
    assert res["qualification_verdict"] == "FAIL"
    assert res["watchdog_rollback_triggered"] is True
    assert res["watchdog_action"] == "UNLOAD_TESTMODE_AND_COLD_POWER_CYCLE_RECOVERY"


def test_pb023_tone_correlation_and_fixture_generation(tmp_path: Path) -> None:
    data_i, data_q = synthesize_adc_iq_tone_capture(
        num_samples=2048, sample_rate_mhz=80.0, tone_freq_mhz=5.0, amplitude=350.0
    )
    stats_match = compute_iq_tone_correlation_and_snr(
        data_i, data_q, sample_rate_mhz=80.0, expected_tone_freq_mhz=5.0
    )
    assert stats_match["captured_iq_snr_tone_correlation"] > 0.99
    assert stats_match["captured_iq_snr_db"] > 40.0

    # Wrong frequency should have near-zero correlation
    stats_mismatch = compute_iq_tone_correlation_and_snr(
        data_i, data_q, sample_rate_mhz=80.0, expected_tone_freq_mhz=12.5
    )
    assert stats_mismatch["captured_iq_snr_tone_correlation"] < 0.05

    # Positive PB-023 probe simulation
    pos_probe = evaluate_pb023_adccapture_and_genwaveform_probes(
        [
            PB023CommandProbeAttempt(
                command_id=59,
                command_name="CMD_ADCCAPTURE",
                response_received=True,
                response_status=0,
                elapsed_s=0.12,
                sample_buffer_length_samples=2048,
                injected_tone_freq_mhz=5.0,
                injected_tone_amplitude_dbfs=-10.0,
                captured_iq_snr_db=stats_match["captured_iq_snr_db"],
                captured_iq_snr_tone_correlation=stats_match[
                    "captured_iq_snr_tone_correlation"
                ],
            )
        ]
    )
    assert pos_probe["outcome_classification"] == "VERIFIED_TONE_CORRELATED_SAMPLE_RAM"

    out_file = tmp_path / "pb_020_023_utf_probe_fixture.json"
    fix = write_pb_020_023_utf_probe_fixture_json(out_file)
    assert out_file.exists()
    loaded = json.loads(out_file.read_text(encoding="utf-8"))
    assert loaded["live_devices_touched"] is False
    assert loaded["automatic_execution_allowed"] is False
    assert loaded["pb_020_readonly_utf_qualification"]["qualification_verdict"] == "PASS"
    assert (
        loaded["pb_023_ar9888_expected_probe_evaluation"]["outcome_classification"]
        == "FALSIFIED_STANDARD_TLV2_ADC_ABI"
    )
    assert fix["task_id"] == "T-PB-GEM2-05"
