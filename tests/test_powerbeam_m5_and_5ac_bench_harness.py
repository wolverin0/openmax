"""Unit tests for PowerBeam M5 300 (XW.v6.3.2) & PowerBeam 5AC (WA.v8.7.25) PtP/PtMP Bench Harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from controller.powerbeam_m5_and_5ac_bench_harness import (
    POWERBEAM_SUPPORTED_WIDTHS_MHZ,
    WA_5AC_SUPPORTED_WIDTHS_MHZ,
    XW_M5_SUPPORTED_WIDTHS_MHZ,
    PowerBeamBlockSample,
    RollbackWatchdogSpec,
    build_powerbeam_bench_battery,
    build_powerbeam_inventory,
    evaluate_rollback_watchdog,
    validate_powerbeam_channel_width_mhz,
    write_powerbeam_bench_plan_json,
)


def test_explicit_channel_width_schema_5_10_20_30_40_80() -> None:
    assert POWERBEAM_SUPPORTED_WIDTHS_MHZ == (5, 10, 20, 30, 40, 80)
    assert XW_M5_SUPPORTED_WIDTHS_MHZ == (5, 10, 20, 30, 40)
    assert WA_5AC_SUPPORTED_WIDTHS_MHZ == (5, 10, 20, 30, 40, 80)

    for w in (5, 10, 20, 30, 40):
        assert validate_powerbeam_channel_width_mhz(w, family="XW") == w
    for w in (5, 10, 20, 30, 40, 80):
        assert validate_powerbeam_channel_width_mhz(w, family="WA") == w

    # 80 MHz must be rejected for XW (802.11n PowerBeam M5 300)
    with pytest.raises(ValueError, match="XW"):
        validate_powerbeam_channel_width_mhz(80, family="XW")

    # Missing, boolean, or unsupported widths must be rejected
    with pytest.raises(ValueError):
        validate_powerbeam_channel_width_mhz(None, family="WA")
    with pytest.raises(ValueError):
        validate_powerbeam_channel_width_mhz(True, family="WA")
    with pytest.raises(ValueError):
        validate_powerbeam_channel_width_mhz(60, family="WA")


def test_30mhz_sample_goodput_per_mhz_and_gatekeeper_bridge() -> None:
    sample_30 = PowerBeamBlockSample(
        run_id="pbe_m5_30mhz_b0_B",
        arm="B",
        block_index=0,
        channel_width_mhz=30,
        goodput_mbps=121.5,
        p50_lat_ms=4.8,
        p95_lat_ms=10.2,
        p99_lat_ms=16.1,
        loss_pct=0.1,
        jain_fairness=0.996,
        worst_peer_goodput_mbps=59.5,
        family="XW",
    )
    assert sample_30.goodput_per_mhz == pytest.approx(4.05, abs=1e-4)
    gk_metric = sample_30.to_gatekeeper_run_metrics()
    assert gk_metric.goodput_per_mhz == pytest.approx(4.05, abs=1e-4)

    # Inconsistent goodput_per_mhz must fail validation
    with pytest.raises(ValueError, match="Inconsistent goodput_per_mhz"):
        PowerBeamBlockSample(
            run_id="bad_gpm",
            arm="A",
            block_index=0,
            channel_width_mhz=30,
            goodput_mbps=120.0,
            p50_lat_ms=5.0,
            p95_lat_ms=10.0,
            p99_lat_ms=15.0,
            loss_pct=0.1,
            jain_fairness=0.99,
            worst_peer_goodput_mbps=55.0,
            family="XW",
            goodput_per_mhz=3.0,  # Wrong (120 / 40 instead of 120 / 30 = 4.0)
        )


def test_rollback_watchdog_triggers_on_reset_loss_latency_and_bridge() -> None:
    healthy = PowerBeamBlockSample(
        run_id="ok_B",
        arm="B",
        block_index=0,
        channel_width_mhz=20,
        goodput_mbps=135.0,
        p50_lat_ms=3.2,
        p95_lat_ms=7.2,
        p99_lat_ms=11.1,
        loss_pct=0.1,
        jain_fairness=0.996,
        worst_peer_goodput_mbps=66.0,
        firmware_resets=0,
        reassociation_time_s=3.2,
        family="WA",
    )
    res_ok = evaluate_rollback_watchdog([healthy], RollbackWatchdogSpec(), l2_4addr_bridge_alive=True)
    assert res_ok["rollback_triggered"] is False
    assert res_ok["action"] == "HOLD_CANDIDATE"

    faulty = PowerBeamBlockSample(
        run_id="bad_B",
        arm="B",
        block_index=1,
        channel_width_mhz=20,
        goodput_mbps=40.0,
        p50_lat_ms=25.0,
        p95_lat_ms=65.0,
        p99_lat_ms=115.0,
        loss_pct=8.5,
        jain_fairness=0.70,
        worst_peer_goodput_mbps=12.0,
        firmware_resets=1,
        reassociation_time_s=28.0,
        family="WA",
    )
    res_bad = evaluate_rollback_watchdog([faulty], RollbackWatchdogSpec(), l2_4addr_bridge_alive=False)
    assert res_bad["rollback_triggered"] is True
    assert res_bad["action"] == "IMMEDIATE_ROLLBACK_TO_ARM_A_STOCK_PROFILE"
    assert len(res_bad["triggers"]) == 5


def test_powerbeam_bench_battery_and_artifact_receipt(tmp_path: Path) -> None:
    units = build_powerbeam_inventory()
    assert len(units) == 4
    assert [u.family for u in units] == ["XW", "XW", "WA", "WA"]

    plan = build_powerbeam_bench_battery()
    assert plan["safety_and_execution_policy"]["automatic_execution_allowed"] is False
    assert plan["safety_and_execution_policy"]["live_ssh_allowed"] is False
    assert plan["safety_and_execution_policy"]["auto_flash_allowed"] is False
    assert plan["summary"]["total_experiments"] == 6
    assert plan["summary"]["promoted_count"] == 6
    assert plan["summary"]["rollback_triggered_count"] == 0
    assert plan["summary"]["aa_null_calibration_pass"] is True

    # Verify artifact file on disk matches deterministic output
    out_file = tmp_path / "powerbeam_m5_5ac_bench_plan_20261024.json"
    written = write_powerbeam_bench_plan_json(out_file)
    loaded = json.loads(out_file.read_text(encoding="utf-8"))
    assert loaded["plan_sha256"] == written["plan_sha256"]

    repo_artifact = Path("artifacts/qca988x/powerbeam_m5_5ac_bench_plan_20261024.json")
    assert repo_artifact.is_file()
    repo_loaded = json.loads(repo_artifact.read_text(encoding="utf-8"))
    assert repo_loaded["plan_sha256"] == written["plan_sha256"]
