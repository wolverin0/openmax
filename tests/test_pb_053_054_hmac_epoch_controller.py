"""Unit tests for PB-053 & PB-054 Hybrid hMAC Airtime Epoch Controller + Missed-Slot Recovery FSM."""

from __future__ import annotations
import json
import pytest

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


def test_live_r135_to_r140_qualification_report(tmp_path) -> None:
    files = []
    for index, distance in enumerate((1, 3, 6, 9, 12, 14)):
        iterations = []
        for arm in ('A', 'B'):
            observation = dict(goodput_rx_mbps=100.0, p95_rtt_ms=15.0 if arm == 'A' else 2.0,
                p99_rtt_ms=20.0 if arm == 'A' else 3.0, packet_loss_pct=0.0, jain_fairness=1.0)
            iterations.append(dict(observation=observation,
                repetition_blocks=[dict(observation=observation,dl_goodput_mbps=50.0) for _ in range(16)],
                tid0_be_tx_pkts_delta=100,tid6_vo_tx_pkts_delta=100,tid6_vo_drops_delta=0))
        filename = f'fixture_{index}.json'
        (tmp_path / filename).write_text(json.dumps(dict(evidence_state='SYNTHETIC',
            experiment_id=f'synthetic_hmac_{index}',distance_m=distance*1000,
            coverage_class=2,slot_time_us=9,ack_timeout_us=64,iterations=iterations)))
        files.append((f'R{135+index}', filename))
    report = build_pb_053_054_qualification_report(evidence_root=tmp_path, receipt_files=files)
    assert report["automatic_execution_allowed"] is False
    assert report["all_6_distances_promoted"] is False
    assert report["zero_tid6_voip_drops_across_all_distances"] is True
    assert len(report["pb053_live_r135_to_r140_evaluations"]) == 6
    for row in report["pb053_live_r135_to_r140_evaluations"]:
        assert row["gate_decision"]["p99_delta_pct"] <= -70.0
        assert row["hmac_tid6_vo_drops_delta"] == 0
        assert row['gate_decision']['verdict'] == 'SYNTHETIC_PASS'
        assert row['latency_floor_promoted'] is False
        assert row['historical_latency_criterion_met'] is True
        assert row['restoration_verified'] is None


def test_missing_saved_receipts_and_empty_inputs_never_pass(tmp_path):
    report = build_pb_053_054_qualification_report(evidence_root=tmp_path)
    assert not report['all_6_distances_promoted']
    assert not report['zero_tid6_voip_drops_across_all_distances']
    assert all(row['source_status'] == 'UNAVAILABLE_TO_THIS_REVIEW'
               for row in report['pb053_live_r135_to_r140_evaluations'])
    empty = build_pb_053_054_qualification_report(evidence_root=tmp_path, receipt_files=())
    assert not empty['all_6_distances_promoted']


@pytest.mark.parametrize('distance', [float('nan'), float('inf'), True])
def test_invalid_distance_cannot_create_hmac_config(distance):
    with pytest.raises(ValueError):
        compute_hmac_epoch_allocation(distance)


@pytest.mark.parametrize('retry', [None, float('nan'), float('inf'), -1, 101, True])
def test_missing_or_invalid_retry_is_not_a_clean_recovery_epoch(retry):
    fsm = HmacMissedSlotRecoveryFsm()
    fsm.step(True, 20)
    with pytest.raises(ValueError):
        fsm.step(False, retry)
    assert fsm.clean_recovery_epochs == 0
