"""Unit tests for FuturaMAX Closed-Loop Production Daemon.

Covers:
1. Daemon initialization and poller selection (airOS / OpenWrt / mock).
2. Telemetry ingestion, capacity forecasting, and bottleneck CPE diagnosis in tick cycle.
3. Station link auditing (chain imbalances, receiver overload) and RF advisory generation.
4. Closed-loop pacing adaptation: CAKE bandwidth adjustment and HTT Type 5 aggregation throttling.
5. Canary trial execution and automated evaluation:
   - Successful trial acceptance (KEEP / ACCEPTED) under improved performance.
   - Automatic rollback trigger (REVERT / REVERTED) when latency degrades >20% or goodput drops >10%.
6. Structured status snapshot export for CLI dashboards and monitoring.
7. Graceful start/stop background thread lifecycle.
"""

from __future__ import annotations

import json
import time
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock

from controller.advisory_mode import AuditSeverity, CanaryManager, SectorAdvisor
from controller.capacity_forecasting import SectorCapacityForecaster
from controller.futuramax_daemon import (
    DaemonConfig,
    DaemonCycleReport,
    FuturaMAXDaemon,
)
from controller.pacing_controller import PacingConfig, PacingController
from telemetry.station_monitor import StationSectorSummary, StationTelemetry


class MockTelemetryPoller:
    """Mock poller providing controllable station telemetry snapshots for testing."""

    def __init__(self, stations: Optional[Dict[str, StationTelemetry]] = None):
        self.stations = stations or {}
        self.connection_state = "CONNECTED"
        self.summary = None
        self.spectral_report = None

    def poll_cycle(self):
        return self


def create_healthy_mock_station(mac: str = "00:27:22:AA:01:01", name: str = "CPE-Clean") -> StationTelemetry:
    """Generate a clean, high-performance mock CPE."""
    return StationTelemetry(
        mac=mac,
        device_name=name,
        source="airos",
        signal_dbm=-62,
        noise_floor_dbm=-95,
        snr_db=33.0,
        chain0_signal_dbm=-62,
        chain1_signal_dbm=-63,
        chain_imbalance_db=1.0,
        tx_rate_mbps=130.0,
        rx_rate_mbps=130.0,
        mcs=8,
        nss=2,
        bandwidth_mhz=20,
        short_gi=False,
        tx_retries=2,
        tx_packets=500,
        airtime_total_pct=8.0,
    )


def create_degraded_mock_station(mac: str = "00:27:22:DD:02:02", name: str = "CPE-Degraded") -> StationTelemetry:
    """Generate a severely bottlenecked CPE with low MCS, high retries, and chain imbalance."""
    return StationTelemetry(
        mac=mac,
        device_name=name,
        source="airos",
        signal_dbm=-78,
        noise_floor_dbm=-95,
        snr_db=17.0,
        chain0_signal_dbm=-75,
        chain1_signal_dbm=-82,  # 7.0 dB imbalance -> CRITICAL
        chain_imbalance_db=7.0,
        tx_rate_mbps=13.0,  # MCS1 13 Mbps
        rx_rate_mbps=13.0,
        mcs=1,
        nss=1,
        bandwidth_mhz=20,
        short_gi=False,
        tx_retries=60,
        tx_packets=200,  # 30% retry rate -> CRITICAL
        airtime_total_pct=38.0,
    )


class TestFuturaMAXDaemonInitialization(unittest.TestCase):
    """Test daemon creation, configuration binding, and engine components."""

    def test_daemon_initialization_defaults(self):
        """Daemon initializes with sensible defaults and mock poller."""
        poller = MockTelemetryPoller()
        daemon = FuturaMAXDaemon(poller=poller)

        self.assertEqual(daemon.config.sector_id, "sector-ap-01")
        self.assertEqual(daemon.config.radio_type, "airos")
        self.assertEqual(daemon.cycle_count, 0)
        self.assertFalse(daemon.running)
        self.assertIsNotNone(daemon.capacity_forecaster)
        self.assertIsNotNone(daemon.sector_advisor)
        self.assertIsNotNone(daemon.pacing_controller)
        self.assertIsNotNone(daemon.canary_manager)

    def test_daemon_custom_configuration(self):
        """Custom DaemonConfig properties are correctly applied."""
        cfg = DaemonConfig(
            sector_id="Sector-West-Tower",
            radio_type="openwrt",
            channel_freq_mhz=5745,
            channel_width_mhz=40,
            airtime_limit_pct=80.0,
            canary_duration_ticks=3,
            dry_run=True,
        )
        poller = MockTelemetryPoller()
        daemon = FuturaMAXDaemon(config=cfg, poller=poller)

        self.assertEqual(daemon.config.sector_id, "Sector-West-Tower")
        self.assertEqual(daemon.config.channel_freq_mhz, 5745)
        self.assertEqual(daemon.config.channel_width_mhz, 40)
        self.assertEqual(daemon.capacity_forecaster.airtime_limit_pct, 80.0)


class TestFuturaMAXDaemonTickCycle(unittest.TestCase):
    """Test single and multi-tick closed-loop optimization execution."""

    def test_tick_cycle_clean_sector(self):
        """Single tick on a healthy sector produces clean forecast, audits, and pacing."""
        s1 = create_healthy_mock_station("00:27:22:01:00:01", "CPE-1")
        s2 = create_healthy_mock_station("00:27:22:01:00:02", "CPE-2")
        poller = MockTelemetryPoller({s1.mac: s1, s2.mac: s2})

        daemon = FuturaMAXDaemon(poller=poller)
        rep = daemon.tick()

        self.assertIsInstance(rep, DaemonCycleReport)
        self.assertEqual(rep.tick_index, 1)
        self.assertTrue(rep.poller_connected)
        self.assertEqual(rep.station_count, 2)
        self.assertFalse(rep.is_exhausted)
        self.assertEqual(rep.bottlenecks_detected, 0)
        self.assertEqual(rep.critical_stations_count, 0)
        self.assertFalse(rep.pacing_throttled)
        self.assertGreater(rep.shaper_bandwidth_mbps, 0.0)

    def test_tick_cycle_bottleneck_detection_and_airtime_cliff(self):
        """Severely degraded station triggers bottleneck alert and RF warning in tick."""
        s1 = create_healthy_mock_station("00:27:22:02:00:01", "CPE-Clean")
        s2 = create_degraded_mock_station("00:27:22:02:00:02", "CPE-Degraded")
        poller = MockTelemetryPoller({s1.mac: s1, s2.mac: s2})

        daemon = FuturaMAXDaemon(poller=poller)
        rep = daemon.tick()

        self.assertEqual(rep.station_count, 2)
        self.assertGreater(rep.bottlenecks_detected, 0)
        self.assertGreater(rep.critical_stations_count, 0)
        self.assertTrue(any("bottleneck" in a.lower() for a in rep.alerts))
        self.assertTrue(any("critical" in a.lower() for a in rep.alerts))

    def test_tick_cycle_pacing_aggregation_throttling(self):
        """High bufferbloat loaded latency triggers hardware A-MPDU aggregation throttling."""
        s1 = create_healthy_mock_station("00:27:22:03:00:01", "CPE-Fast")
        poller = MockTelemetryPoller({s1.mac: s1})
        # Simulate loaded bufferbloat in summary
        poller.summary = {
            "p50_latency_ms": 10.0,
            "p95_latency_ms": 45.0,  # 45 ms loaded latency > 15 ms bloat threshold
            "total_throughput_mbps": 75.0,
            "packet_loss_pct": 1.0,
        }

        daemon = FuturaMAXDaemon(poller=poller)
        rep = daemon.tick()

        self.assertTrue(rep.pacing_throttled)
        self.assertTrue(daemon.last_pacing_action.is_throttled)

        # Station action should throttle A-MPDU from baseline 64 down to <= 32
        sta_act = daemon.last_pacing_action.station_actions[s1.mac]
        self.assertLess(sta_act.ampdu_limit, 64)
        self.assertTrue(sta_act.htt_aggr_hex.startswith("0x"))


class TestFuturaMAXDaemonCanaryTrials(unittest.TestCase):
    """Test live canary change execution and automated causal rollback guards."""

    def test_canary_trial_successful_acceptance(self):
        """Canary trial that improves performance is ACCEPTED after duration ticks."""
        s1 = create_healthy_mock_station()
        poller = MockTelemetryPoller({s1.mac: s1})
        cfg = DaemonConfig(canary_duration_ticks=2)
        daemon = FuturaMAXDaemon(config=cfg, poller=poller)

        # 1. Establish baseline
        daemon.tick()

        # 2. Stage canary change: increase TX power from 18 to 21 dBm
        trial = daemon.start_canary_trial(
            parameter_name="tx_power",
            old_value=18,
            new_value=21,
            baseline_metrics={"goodput_mbps": 40.0, "latency_p95_ms": 12.0, "resets": 0},
        )
        self.assertEqual(trial.status, "TRIAL_ACTIVE")
        self.assertIsNotNone(daemon.active_canary_trial)

        # 3. Simulate improved conditions during canary ticks (goodput 55 Mbps, latency 10 ms)
        poller.summary = {
            "p50_latency_ms": 3.0,
            "p95_latency_ms": 10.0,
            "total_throughput_mbps": 55.0,
        }
        daemon.tick()  # Tick 1
        self.assertIsNotNone(daemon.active_canary_trial)

        daemon.tick()  # Tick 2 -> triggers completion evaluation!
        self.assertIsNone(daemon.active_canary_trial)
        self.assertEqual(len(daemon.completed_canary_trials), 1)

        completed = daemon.completed_canary_trials[0]
        self.assertEqual(completed.decision, "KEEP")
        self.assertEqual(completed.status, "ACCEPTED")
        self.assertGreater(completed.goodput_delta_pct, 10.0)

    def test_canary_trial_automatic_rollback_on_latency_spike(self):
        """Canary trial that spikes loaded latency > 20% triggers automatic rollback."""
        s1 = create_healthy_mock_station()
        poller = MockTelemetryPoller({s1.mac: s1})
        cfg = DaemonConfig(canary_duration_ticks=2)

        rollback_mock = MagicMock()
        daemon = FuturaMAXDaemon(config=cfg, poller=poller, rollback_hook=rollback_mock)

        # 1. Establish baseline
        daemon.tick()

        # 2. Stage risky canary change: expand channel width 20 -> 40 MHz in dirty spectrum
        trial = daemon.start_canary_trial(
            parameter_name="channel_width",
            old_value=20,
            new_value=40,
            baseline_metrics={"goodput_mbps": 50.0, "latency_p95_ms": 10.0, "resets": 0},
        )

        # 3. Simulate severe collision latency spike: p95 jumps to 30 ms (+200% spike)
        poller.summary = {
            "p50_latency_ms": 8.0,
            "p95_latency_ms": 30.0,
            "total_throughput_mbps": 48.0,
        }
        daemon.tick()  # Tick 1
        daemon.tick()  # Tick 2 -> evaluation triggers REVERT!

        self.assertIsNone(daemon.active_canary_trial)
        self.assertEqual(len(daemon.completed_canary_trials), 1)

        reverted = daemon.completed_canary_trials[0]
        self.assertEqual(reverted.decision, "REVERT")
        self.assertEqual(reverted.status, "REVERTED")
        self.assertTrue(any("ROLLBACK" in alert for alert in daemon.alerts))

        # Verify rollback hook was called with original parameter and value
        rollback_mock.assert_called_once_with("channel_width", 20)


class TestFuturaMAXDaemonStatusSnapshot(unittest.TestCase):
    """Test structured status snapshot generation for monitoring and CLI dashboard."""

    def test_status_snapshot_structure_and_json_serialization(self):
        """get_status_snapshot() returns all required fields and serializes to JSON cleanly."""
        s1 = create_healthy_mock_station("00:27:22:99:00:01", "CPE-Fast")
        s2 = create_degraded_mock_station("00:27:22:99:00:02", "CPE-Slow")
        poller = MockTelemetryPoller({s1.mac: s1, s2.mac: s2})

        daemon = FuturaMAXDaemon(poller=poller)
        daemon.tick()

        snapshot = daemon.get_status_snapshot()
        self.assertIsInstance(snapshot, dict)

        # Essential monitoring fields
        self.assertEqual(snapshot["sector_id"], "sector-ap-01")
        self.assertEqual(snapshot["cycle_count"], 1)
        self.assertEqual(snapshot["station_count"], 2)
        self.assertIn("airtime_demand_pct", snapshot)
        self.assertIn("airtime_headroom_pct", snapshot)
        self.assertIn("is_exhausted", snapshot)
        self.assertIn("bottlenecks", snapshot)
        self.assertIn("critical_stations", snapshot)
        self.assertIn("actionable_advisories_count", snapshot)
        self.assertIn("pacing", snapshot)

        # JSON roundtrip validation
        json_str = json.dumps(snapshot, indent=2)
        self.assertIsInstance(json_str, str)
        deserialized = json.loads(json_str)
        self.assertEqual(deserialized["sector_id"], "sector-ap-01")


class TestFuturaMAXDaemonLifecycle(unittest.TestCase):
    """Test daemon background thread start/stop lifecycle."""

    def test_background_thread_start_and_stop(self):
        """Daemon cleanly starts in background thread and stops on request."""
        poller = MockTelemetryPoller()
        cfg = DaemonConfig(poll_interval_s=0.05)
        daemon = FuturaMAXDaemon(config=cfg, poller=poller)

        self.assertFalse(daemon.running)
        daemon.start(background=True)
        self.assertTrue(daemon.running)

        # Allow daemon loop to execute at least 2 ticks
        time.sleep(0.15)
        self.assertGreaterEqual(daemon.cycle_count, 1)

        daemon.stop()
        self.assertFalse(daemon.running)


if __name__ == "__main__":
    unittest.main()
