"""Unit tests for PB-053 & PB-054 Hybrid hMAC Airtime Epoch Controller + Missed-Slot Recovery FSM."""

from __future__ import annotations

from controller.pb_053_054_hmac_epoch_controller import (
    HmacMissedSlotRecoveryFsm,
    build_pb_053_054_qualification_report,
    compute_hmac_epoch_allocation,
)


def test_compute_hmac_epoch_allocation_1km_to_14km() -> None:
    c1 = compute_hmac_epoch_allocation(1.0, 20)
    assert c1.coverage_class == 2
    assert c1.ap_vo_low_high_us == (500, 1100)
    assert c1.ap_be_low_high_us == (1550, 3100)
    assert c1.cpe_be_low_high_us == (2100, 4200)
    assert c1.fq_quantum_bytes == 1514
    assert c1.codel_target_ms == 8

    c14 = compute_hmac_epoch_allocation(14.0, 20)
    assert c14.coverage_class == 31
    assert c14.codel_target_ms == 16
    assert c14.codel_interval_ms == 80


def test_pb_054_missed_slot_recovery_fsm_transitions() -> None:
    fsm = HmacMissedSlotRecoveryFsm()
    assert fsm.state == "NOMINAL_EPOCH_ACTIVE"

    s1 = fsm.step(slot_missed_or_credit_stalled=True, mac_retry_rate_pct=8.0)
    assert s1.next_state == "PROBING_SINGLE_QUANTUM_RECOVERY"
    assert s1.applied_be_high_us == 1550
    assert s1.rts_threshold_bytes == 256
    assert s1.vo_slice_protected is True

    s2 = fsm.step(slot_missed_or_credit_stalled=True, mac_retry_rate_pct=14.0)
    assert s2.next_state == "PROBING_SINGLE_QUANTUM_RECOVERY"

    s3 = fsm.step(slot_missed_or_credit_stalled=True, mac_retry_rate_pct=16.0)
    assert s3.next_state == "SAFE_CSMA_FALLBACK_DRAIN"
    assert s3.consecutive_missed_epochs == 3

    # 3 clean epochs restore NOMINAL_EPOCH_ACTIVE
    fsm.step(False, 2.0)
    fsm.step(False, 1.5)
    s6 = fsm.step(False, 1.2)
    assert s6.next_state == "NOMINAL_EPOCH_ACTIVE"
    assert s6.applied_be_high_us == 3100
    assert s6.rts_threshold_bytes == 2347


def test_live_r135_to_r140_qualification_report() -> None:
    report = build_pb_053_054_qualification_report()
    assert report["automatic_execution_allowed"] is False
    assert report["all_6_distances_promoted"] is True
    assert report["zero_tid6_voip_drops_across_all_distances"] is True
    assert len(report["pb053_live_r135_to_r140_evaluations"]) == 6
    for row in report["pb053_live_r135_to_r140_evaluations"]:
        assert row["gate_decision"]["p99_delta_pct"] <= -70.0
        assert row["hmac_tid6_vo_drops_delta"] == 0
