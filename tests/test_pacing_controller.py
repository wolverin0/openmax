"""Unit tests for controller/pacing_controller.py and optimizer wire integrations.

Covers:
1. AggregationPolicy compiling into binary HTT Type 5 words and bytes.
2. RateMaskArm and ADRBanditRateController generating Subtype 0x1E rate override wire frames.
3. PacingController slow-loop optimization math under clean vs degraded link states.
4. Dynamic A-MPDU aggregation throttling under high bufferbloat latency.
5. Dead-MCS rate constraint enforcement on high-retry stations.
6. State persistence, dry-run safety, and rollback safeguard.
"""

import json
from pathlib import Path
import unittest

from controller.airmax_wire import (
    POLL_SUBTYPE_RATE_OVERRIDE,
    build_htt_type5_aggr_cfg,
    build_poll_subtype_1e_rate_override,
    decode_rate_byte,
    parse_htt_type5_aggr_cfg,
    parse_poll_subtype_1e_rate_override,
)
from controller.optimizer.aggregation_policy import AggregationPolicy
from controller.optimizer.rate_bandit import ADRBanditRateController, RateMaskArm
from controller.pacing_controller import (
    PacingAction,
    PacingConfig,
    PacingController,
    StationControlAction,
)


class TestOptimizerWireIntegration(unittest.TestCase):
    """Test wire protocol integration directly inside optimizer modules."""

    def test_aggregation_policy_to_htt_word(self):
        """Test AggregationPolicy compiles into binary HTT Type 5 word."""
        policy = AggregationPolicy(amsdu=3, ampdu=64)
        word = policy.to_htt_word()
        expected = build_htt_type5_aggr_cfg(max_ampdu=64, max_amsdu=3)

        self.assertEqual(word, expected)
        self.assertEqual(word, 5 | (64 << 8) | (3 << 16))
        self.assertEqual(policy.to_htt_hex(), "0x00034005")

        # Parse roundtrip
        ampdu, amsdu = parse_htt_type5_aggr_cfg(word)
        self.assertEqual(ampdu, 64)
        self.assertEqual(amsdu, 3)

    def test_aggregation_policy_to_htt_bytes(self):
        """Test AggregationPolicy compiles into 4-byte buffer with endian swap option."""
        policy = AggregationPolicy(amsdu=2, ampdu=32)
        raw_bytes = policy.to_htt_bytes(endian_swap=False)
        self.assertEqual(len(raw_bytes), 4)

        swapped = policy.to_htt_bytes(endian_swap=True)
        self.assertEqual(len(swapped), 4)
        self.assertEqual(swapped, raw_bytes[::-1])

    def test_rate_bandit_arm_to_rate_override_frame(self):
        """Test RateMaskArm converts directly into Subtype 0x1E rate override frame."""
        arm_mcs7 = RateMaskArm(2, "MCS0-7 (64-QAM Ceiling)", max_mcs=7, mask_hex="0x00ff")
        frame = arm_mcs7.to_rate_override_frame(bw=40, nss=2)

        self.assertEqual(len(frame), 16)
        expected = build_poll_subtype_1e_rate_override(mcs=7, bw=40, nss=2)
        self.assertEqual(frame, expected)

        # Parse frame and verify Xtensa deserializer fields
        parsed = parse_poll_subtype_1e_rate_override(frame)
        self.assertEqual(parsed["subtype"], POLL_SUBTYPE_RATE_OVERRIDE)
        self.assertEqual(parsed["primary_mcs"], 7)
        self.assertEqual(parsed["primary_bw"], 40)
        self.assertEqual(parsed["primary_nss"], 2)

    def test_rate_bandit_controller_recommend_rate(self):
        """Test ADRBanditRateController produces structured recommendation with wire frame."""
        bandit = ADRBanditRateController(cpe_id="CPE-Test-01")
        rec = bandit.recommend_rate(bw=80, nss=2)

        self.assertEqual(rec["cpe_id"], "CPE-Test-01")
        self.assertIn("max_mcs", rec)
        self.assertIn("rate_override_frame", rec)
        self.assertEqual(len(rec["rate_override_frame"]), 16)
        self.assertEqual(rec["rate_override_hex"], rec["rate_override_frame"].hex())


class TestPacingController(unittest.TestCase):
    """Test suite for slow-loop PacingController."""

    def setUp(self):
        self.config = PacingConfig(
            iface="eth0",
            latency_target_ms=25.0,
            bloat_threshold_ms=15.0,
            shaper_headroom_pct=0.90,
            baseline_ampdu=64,
            min_ampdu=8,
            baseline_amsdu=3,
            dry_run=True,
        )
        self.controller = PacingController(self.config)

    def test_optimal_link_evaluation(self):
        """Test pacing decision under healthy, low-latency link conditions."""
        stations = {
            "00:15:6d:aa:bb:01": {
                "mac": "00:15:6d:aa:bb:01",
                "tx_rate_mbps": 100.0,
                "snr_db": 30.0,
                "tx_retries": 1,
                "tx_packets": 200,
                "bandwidth_mhz": 40,
                "chain1_signal_dbm": -62,
            }
        }
        bufferbloat = {
            "p50_ms": 1.5,
            "p95_ms": 3.2,
            "p99_ms": 4.5,
            "bloat_p95_ms": 1.7,
            "goodput_mbps": 95.0,
            "loss_pct": 0.0,
        }

        action = self.controller.evaluate(stations, bufferbloat)

        self.assertIsInstance(action, PacingAction)
        self.assertFalse(action.is_throttled)
        self.assertFalse(action.is_rollback)
        self.assertEqual(len(action.safety_alerts), 0)

        # Shaper should be 90% of capacity (100.0 * 0.90 = 90.0 Mbps)
        self.assertEqual(action.shaper_bandwidth_mbps, 90.0)
        self.assertEqual(action.shaper_bandwidth_str, "90Mbit")

        # CAKE command contains diffserv4 and bandwidth
        cake_script = "\n".join(action.cake_commands)
        self.assertIn("cake bandwidth 90Mbit diffserv4", cake_script)

        # Station action: baseline aggregation (64 AMPDU / 3 AMSDU)
        sa = action.station_actions["00:15:6d:aa:bb:01"]
        self.assertEqual(sa.ampdu_limit, 64)
        self.assertEqual(sa.amsdu_limit, 3)
        self.assertEqual(sa.htt_aggr_word, 5 | (64 << 8) | (3 << 16))

        # Station action: wire override frame is valid 16 bytes
        self.assertEqual(len(sa.rate_override_frame), 16)
        parsed = parse_poll_subtype_1e_rate_override(sa.rate_override_frame)
        self.assertEqual(parsed["primary_bw"], 40)
        self.assertEqual(parsed["primary_nss"], 2)

    def test_moderate_bufferbloat_aggregation_throttling(self):
        """Test A-MPDU throttles to 16 and shaper backs off when bloat > 25ms."""
        stations = {
            "00:15:6d:aa:bb:02": {
                "mac": "00:15:6d:aa:bb:02",
                "tx_rate_mbps": 80.0,
                "snr_db": 28.0,
                "bandwidth_mhz": 20,
            }
        }
        bufferbloat = {
            "p50_ms": 2.0,
            "p95_ms": 32.0,
            "bloat_p95_ms": 30.0,  # > 25ms threshold
            "goodput_mbps": 75.0,
        }

        action = self.controller.evaluate(stations, bufferbloat)

        self.assertTrue(action.is_throttled)
        # Moderate backoff: 80% of shaper headroom (72.0 * 0.80 = 57.6 Mbps)
        self.assertEqual(action.shaper_bandwidth_mbps, 57.6)
        self.assertEqual(action.shaper_bandwidth_str, "57Mbit")

        sa = action.station_actions["00:15:6d:aa:bb:02"]
        # Aggregation throttled to 16
        self.assertEqual(sa.ampdu_limit, 16)
        self.assertEqual(sa.htt_aggr_word, 5 | (16 << 8) | (3 << 16))
        self.assertIn("30.0ms > 25ms", sa.throttle_reason)

    def test_severe_bufferbloat_aggregation_throttling(self):
        """Test A-MPDU throttles to minimum 8 and shaper backs off to 70% when bloat > 50ms."""
        stations = {
            "00:15:6d:aa:bb:03": {
                "mac": "00:15:6d:aa:bb:03",
                "tx_rate_mbps": 60.0,
                "snr_db": 26.0,
                "bandwidth_mhz": 20,
            }
        }
        bufferbloat = {
            "p50_ms": 3.0,
            "p95_ms": 68.0,
            "bloat_p95_ms": 65.0,  # > 50ms threshold
            "goodput_mbps": 50.0,
        }

        action = self.controller.evaluate(stations, bufferbloat)

        self.assertTrue(action.is_throttled)
        # Aggressive shaper backoff: 70% of 54.0 = 37.8 Mbps
        self.assertEqual(action.shaper_bandwidth_mbps, 37.8)

        sa = action.station_actions["00:15:6d:aa:bb:03"]
        # Aggregation throttled to minimum 8 subframes
        self.assertEqual(sa.ampdu_limit, 8)
        self.assertEqual(sa.htt_aggr_word, 5 | (8 << 8) | (3 << 16))

    def test_dead_mcs_avoidance_on_high_retries(self):
        """Test rate constraint is imposed on a station with excessive TX retries."""
        stations = {
            "00:15:6d:de:ad:01": {
                "mac": "00:15:6d:de:ad:01",
                "tx_rate_mbps": 40.0,
                "snr_db": 18.0,       # Low SNR
                "tx_retries": 15,
                "tx_packets": 100,    # 15% retries > 8% threshold
                "bandwidth_mhz": 20,
            }
        }
        bufferbloat = {
            "p50_ms": 2.0,
            "p95_ms": 4.0,
            "bloat_p95_ms": 2.0,
            "goodput_mbps": 38.0,
        }

        action = self.controller.evaluate(stations, bufferbloat)
        sa = action.station_actions["00:15:6d:de:ad:01"]

        # MCS must be capped to 5 or lower (256-QAM and high 64-QAM banned)
        self.assertLessEqual(sa.max_mcs, 5)
        parsed = parse_poll_subtype_1e_rate_override(sa.rate_override_frame)
        self.assertLessEqual(parsed["primary_mcs"], 5)
        self.assertIn("Retry/SNR constraint", sa.throttle_reason)

    def test_safety_alert_on_excessive_packet_loss(self):
        """Test safety alert is raised when packet loss exceeds threshold."""
        stations = {"00:15:6d:00:00:01": {"mac": "00:15:6d:00:00:01", "tx_rate_mbps": 50.0}}
        bufferbloat = {"p50_ms": 2.0, "p95_ms": 4.0, "loss_pct": 25.0}  # > 15% threshold

        action = self.controller.evaluate(stations, bufferbloat)
        self.assertTrue(any("Excessive packet loss" in alert for alert in action.safety_alerts))

    def test_dry_run_application(self):
        """Test that apply() in dry-run mode succeeds without modifying system."""
        stations = {"00:15:6d:aa:bb:05": {"mac": "00:15:6d:aa:bb:05", "tx_rate_mbps": 50.0}}
        action = self.controller.evaluate(stations)
        success = self.controller.apply(action)
        self.assertTrue(success)

    def test_rollback_safeguard(self):
        """Test rollback restores default baseline aggregation, shaper, and rate mask."""
        stations = {"00:15:6d:aa:bb:06": {"mac": "00:15:6d:aa:bb:06", "tx_rate_mbps": 50.0}}
        # Trigger throttled state first
        self.controller.evaluate(stations, {"p50_ms": 2.0, "p95_ms": 60.0, "bloat_p95_ms": 58.0})

        # Execute rollback
        rb_action = self.controller.rollback()

        self.assertTrue(rb_action.is_rollback)
        self.assertFalse(rb_action.is_throttled)
        self.assertEqual(rb_action.shaper_bandwidth_mbps, self.config.max_shaper_mbps)

        sa = rb_action.station_actions["00:15:6d:aa:bb:06"]
        self.assertEqual(sa.ampdu_limit, 64)
        self.assertEqual(sa.htt_aggr_word, 5 | (64 << 8) | (3 << 16))
        self.assertEqual(sa.max_mcs, 9)

    def test_state_persistence_and_loading(self, tmp_path=None):
        """Test state serialization and recovery from JSON."""
        state_file = Path("test_pacing_state.json")
        try:
            self.controller.config.state_file = str(state_file)
            stations = {"00:15:6d:aa:bb:07": {"mac": "00:15:6d:aa:bb:07", "tx_rate_mbps": 70.0}}
            action = self.controller.evaluate(stations)

            self.assertTrue(state_file.exists())
            loaded_data = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertIn("last_action", loaded_data)
            self.assertIn("bandits", loaded_data)

            # Create second controller and load state
            controller2 = PacingController(PacingConfig(state_file=str(state_file)))
            self.assertTrue(controller2.load_state(str(state_file)))
        finally:
            if state_file.exists():
                state_file.unlink()


if __name__ == "__main__":
    unittest.main()
