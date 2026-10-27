"""Unit tests for Stage 29B AF-4X Invictus & PowerBeam M5 AR934x Theoretical Models."""

from __future__ import annotations

import json
from pathlib import Path

from controller.af4x_invictus_and_m5_airmax_optimizer import (
    AF4XInvictusMimoAndQueueModel,
    AF4XInvictusTddSymbolModel,
    M5AirMaxMimoRankAndChainModel,
    M5AirMaxTdmaAndQueuePacingModel,
    OUTPUT_DOC_PATH,
    OUTPUT_JSON_PATH,
    build_stage29b_models_and_docs,
)


def test_af4x_invictus_tdd_symbol_budget_and_cp_model() -> None:
    model = AF4XInvictusTddSymbolModel()
    stock = model.evaluate_frame_and_cp(
        frame_length_ms=2.0,
        cyclic_prefix_samples=24,
        short_cp_enabled=False,
        strict_timing_enabled=False,
        duty_cycle_dl_pct=50.0,
    )
    champ = model.evaluate_frame_and_cp(
        frame_length_ms=2.5,
        cyclic_prefix_samples=8,
        short_cp_enabled=True,
        strict_timing_enabled=True,
        duty_cycle_dl_pct=50.0,
    )

    assert stock.tdd_frame_irq140_hz == 500.0
    assert champ.tdd_frame_irq140_hz == 400.0
    assert champ.am1808_irq_cpu_utilization_pct < stock.am1808_irq_cpu_utilization_pct
    assert stock.cyclic_prefix_duration_us == 1.05
    assert champ.cyclic_prefix_duration_us == 0.35
    assert champ.total_symbol_duration_us < stock.total_symbol_duration_us
    assert champ.payload_symbols_per_frame > stock.payload_symbols_per_frame
    assert champ.symbol_packing_efficiency_pct > stock.symbol_packing_efficiency_pct
    assert champ.projected_p95_rtt_ms < stock.projected_p95_rtt_ms


def test_af4x_invictus_mimo_rank_and_queue_pacing() -> None:
    model = AF4XInvictusMimoAndQueueModel()
    stock_q = model.evaluate(
        rxpower0_dbm=-72.0,
        rxpower1_dbm=-73.0,
        noise_floor_dbm=-98.0,
        target_ber_exponent=6,
        txqueuelen_packets=1000,
        flowcntl_enabled=False,
    )
    champ_q = model.evaluate(
        rxpower0_dbm=-72.0,
        rxpower1_dbm=-73.0,
        noise_floor_dbm=-98.0,
        target_ber_exponent=5,
        txqueuelen_packets=256,
        flowcntl_enabled=True,
    )
    assert champ_q.mimo_rank2_supported is True
    assert champ_q.mimo_condition_number_db == 1.0
    assert champ_q.snr_margin_gain_from_ber5_db == 0.85
    assert champ_q.max_queue_drain_delay_ms < stock_q.max_queue_drain_delay_ms


def test_m5_ar934x_mimo_rank_and_asymmetric_chainmask() -> None:
    mimo_model = M5AirMaxMimoRankAndChainModel(imbalance_threshold_db=5.0)
    res = mimo_model.evaluate_mimo_and_chainmask(
        chain0_rssi_db=9.0,
        chain1_rssi_db=16.5,
        stbc_enabled=True,
        ewma_delegate_enabled=True,
    )
    assert res.chain_imbalance_condition_db == 7.5
    assert res.symmetric_2x2_mcs11_15_per_pct > 35.0
    assert res.asymmetric_simo_tx_chainmask == 2
    assert res.asymmetric_mrc_rx_chainmask == 3
    assert res.pa_power_concentration_gain_db == 3.01
    assert res.effective_remote_rssi_gain_db == 5.0
    assert res.mrc_2chain_rx_diversity_gain_db > 0.7
    assert res.post_rescue_per_pct < 6.0


def test_m5_ar934x_tdma_txop_and_ampdu_serialization() -> None:
    tdma_model = M5AirMaxTdmaAndQueuePacingModel()
    stock = tdma_model.evaluate_tdma_and_queue(
        txop_limit_ms=25,
        txop_min_slot_ms=5,
        ampdu_max_frames=32,
        ampdu_max_bytes=50000,
        phy_rate_mbps=27.0,
        per_pct=32.0,
        txqueuelen_packets=1000,
        no_auto_prio=0,
        no_ack_rate=0,
        burst_enabled=False,
    )
    champ = tdma_model.evaluate_tdma_and_queue(
        txop_limit_ms=15,
        txop_min_slot_ms=5,
        ampdu_max_frames=16,
        ampdu_max_bytes=16384,
        phy_rate_mbps=40.5,
        per_pct=5.5,
        txqueuelen_packets=256,
        no_auto_prio=1,
        no_ack_rate=1,
        burst_enabled=True,
    )

    assert stock.ampdu_airtime_serialization_ms > 20.0
    assert stock.fits_within_tdma_txop_slot is False
    assert stock.slot_truncation_risk is True

    assert champ.ampdu_airtime_serialization_ms < 4.5
    assert champ.fits_within_tdma_txop_slot is True
    assert champ.slot_truncation_risk is False
    assert champ.atpc_ap_mode_panic_guarded is True
    assert champ.projected_goodput_mbps == 15.22
    assert champ.projected_1400b_p95_rtt_ms == 6.41
    for cmd in champ.recommended_commands:
        assert "/proc/sys/dev/ubnt_poll/atpc" not in cmd


def test_stage29b_artifact_and_doc_generation(tmp_path: Path) -> None:
    json_out = tmp_path / "stage29b_test.json"
    doc_out = tmp_path / "STAGE29B_TEST.md"
    payload = build_stage29b_models_and_docs(output_json_path=json_out, output_doc_path=doc_out)

    assert json_out.exists()
    assert doc_out.exists()
    assert payload["stage"] == "STAGE29B"
    assert payload["task_id"] == "T-S29B-GEM2-AF4X-INVICTUS-AND-M5-AR934X-THEORETICAL-MODELS"
    assert OUTPUT_JSON_PATH.exists()
    assert OUTPUT_DOC_PATH.exists()
    saved = json.loads(OUTPUT_JSON_PATH.read_text(encoding="utf-8"))
    assert saved["af4x_invictus_models"]["tdd_symbol_budget_comparison"]["champion_2_5ms_cp8_strict"]["tdd_frame_irq140_hz"] == 400.0
    assert saved["m5_ar934x_airmax_models"]["tdma_slot_and_queue_pacing_comparison"]["champion_txop15_ampdu16_16kb"]["projected_goodput_mbps"] == 15.22
