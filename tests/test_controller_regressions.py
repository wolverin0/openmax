"""Offline safety and circular-geometry regressions; no target access."""
from dataclasses import replace
import math

import pytest

from controller.cooperative_sensor import (
    ANGULAR_RF_INTERFERENCE_CLUSTER, SECTOR_WIDE_OR_BACKHAUL_FAULT,
    CpeTelemetrySample, evaluate_relay_feasibility, localize_sector_faults,
)
from controller.distributed_compute import (
    CPETelemetrySnapshot, create_signed_job_manifest, evaluate_cpe_eligibility,
    verify_signed_job_manifest,
)


def test_interference_bearing_crosses_north():
    samples = [CpeTelemetrySample(str(i), str(i), azimuth_deg=a, cinr_db=c)
               for i, (a, c) in enumerate([(355, 10), (5, 10), (140, 25)])]
    report = localize_sector_faults(samples)
    assert report.sector_classification == ANGULAR_RF_INTERFERENCE_CLUSTER
    assert report.angular_cluster_center_deg == pytest.approx(0, abs=1e-6)


def test_half_sector_is_not_seventy_percent():
    samples = [CpeTelemetrySample(str(i), str(i), azimuth_deg=i * 50,
               rtt_p95_ms=40 if i < 2 else 5) for i in range(4)]
    assert localize_sector_faults(samples).sector_classification != SECTOR_WIDE_OR_BACKHAUL_FAULT


def test_same_bearing_is_a_zero_width_cluster():
    samples = [CpeTelemetrySample(str(i), str(i), azimuth_deg=a, cinr_db=c)
               for i, (a, c) in enumerate([(45, 10), (45, 10), (140, 25)])]
    report = localize_sector_faults(samples)
    assert report.sector_classification == ANGULAR_RF_INTERFERENCE_CLUSTER
    assert report.evidence['wedge_span_deg'] == 0


@pytest.mark.parametrize('rssi', [float('nan'), float('inf')])
def test_relay_unknown_rssi_cannot_approve(rssi):
    assert not evaluate_relay_feasibility(6.5, 100, 150, rssi).approved


def test_relay_requires_strict_airtime_improvement():
    assert not evaluate_relay_feasibility(50, 100, 100, -40,
        overhead_factor=1, min_airtime_savings_pct=0).approved


def healthy_snapshot():
    return CPETelemetrySnapshot('fixture', 'CPE', 3, 20000, 0, 10, 5,
        lease_issued_at_epoch=1000, lease_ttl_sec=90, now_epoch=1040)


@pytest.mark.parametrize('field,value', [('customer_kbps', math.nan),
    ('rtt_p95_ms', math.nan), ('free_ram_kb', math.nan),
    ('active_sector_workers', -1), ('lease_ttl_sec', 0),
    ('lease_issued_at_epoch', 1050), ('now_epoch', None)])
def test_missing_or_invalid_safety_measurements_preempt(field, value):
    result = evaluate_cpe_eligibility(replace(healthy_snapshot(), **{field: value}))
    assert not result.eligible
    assert result.preemption_required


def manifest():
    return create_signed_job_manifest(job_id='fixture', shard_id=1, cpe_id='fixture',
        opcode=1, seed=123, iterations=1024, secret_key=b'fixture-only', issued_at_epoch=1000)


def test_canonical_integer_coercion_cannot_authenticate_different_values():
    original = manifest()
    changed = replace(original, duty_pct=5.9)
    assert not verify_signed_job_manifest(changed, b'fixture-only', now_epoch=1040)[0]


def test_future_signed_manifest_is_not_executable():
    assert not verify_signed_job_manifest(manifest(), b'fixture-only', now_epoch=999)[0]


@pytest.mark.parametrize('signature', [None, 'é' * 64, 'z' * 64, ''])
def test_malformed_signature_fails_without_exception(signature):
    assert not verify_signed_job_manifest(replace(manifest(), signature_hex=signature),
                                          b'fixture-only', now_epoch=1040)[0]
