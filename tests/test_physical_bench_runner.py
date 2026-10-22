#!/usr/bin/env python3
"""Unit tests for FuturaMAX Physical Bench Test Runner.

Verifies:
1. PhysicalBenchConfig defaults and dictionary serialization.
2. MockSSHExecutor command recording and custom response overrides.
3. Pre-flight endpoint probe reachability (pass and failure cases).
4. Pre-test baseline capture from Linux iw and airOS wstalist formats.
5. Qdisc treatment setup (baseline, CAKE diffserv4 ack-filter, fq_pacing).
6. Workload generation and concurrent ping sampling (downlink/uplink, TCP/UDP).
7. Post-test telemetry delta math (packets, retries, drops).
8. Safety and restoration guarantee: cleanup_and_restore is called even upon workload failure.
9. Receipt and markdown persistence to disk.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.bench.physical_bench_runner import (
    BaselineTelemetry,
    MockSSHExecutor,
    PhysicalBenchConfig,
    PhysicalBenchResult,
    PhysicalBenchRunner,
)


class TestPhysicalBenchRunner(unittest.TestCase):
    """Test suite for PhysicalBenchRunner lifecycle and safety guarantees."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="fmx_bench_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_defaults_and_to_dict(self):
        """Verifies default bench configuration and dictionary serialization."""
        cfg = PhysicalBenchConfig(
            experiment_id="FMX-0006",
            ap_ip="192.168.1.20",
            cpe_ip="192.168.1.3",
            treatment="cake",
            cake_bandwidth="60Mbit",
            duration_seconds=5,
            out_dir=Path(self.temp_dir),
        )
        d = cfg.to_dict()
        self.assertEqual(d["experiment_id"], "FMX-0006")
        self.assertEqual(d["treatment"], "cake")
        self.assertEqual(d["cake_bandwidth"], "60Mbit")
        self.assertEqual(d["duration_seconds"], 5)
        self.assertIsInstance(d["out_dir"], str)

    def test_mock_ssh_executor_custom_responses(self):
        """Verifies MockSSHExecutor history tracking and pattern responses."""
        executor = MockSSHExecutor(failure_hosts=["10.0.0.99"])
        out, err, rc = executor.exec_cmd("192.168.1.20", "echo PONG")
        self.assertEqual(rc, 0)
        self.assertIn("PONG", out)

        # Custom response
        executor.set_response("custom_tool", "CUSTOM_OUTPUT", "NO_ERROR", 0)
        out2, err2, rc2 = executor.exec_cmd("192.168.1.20", "run custom_tool --flag")
        self.assertEqual(rc2, 0)
        self.assertEqual(out2, "CUSTOM_OUTPUT")

        # Failure host
        out3, err3, rc3 = executor.exec_cmd("10.0.0.99", "echo PONG")
        self.assertEqual(rc3, 255)
        self.assertIn("failed", err3)

        self.assertEqual(len(executor.history), 3)

    def test_pre_flight_probe_success_and_failure(self):
        """Pre-flight probe checks all endpoints and flags unreachable hosts."""
        executor_ok = MockSSHExecutor()
        cfg_ok = PhysicalBenchConfig(out_dir=self.temp_dir, dry_run=True)
        runner_ok = PhysicalBenchRunner(cfg_ok, executor=executor_ok)
        probe_res = runner_ok.probe_endpoints()
        self.assertTrue(probe_res.get("ap_ssh"))
        self.assertTrue(probe_res.get("cpe_ssh"))
        self.assertTrue(probe_res.get("client_ssh"))

        # Test failure on CPE
        executor_fail = MockSSHExecutor(failure_hosts=[cfg_ok.cpe_ip])
        runner_fail = PhysicalBenchRunner(cfg_ok, executor=executor_fail)
        probe_fail = runner_fail.probe_endpoints()
        self.assertTrue(probe_fail.get("ap_ssh"))
        self.assertFalse(probe_fail.get("cpe_ssh"))

    def test_capture_baseline_linux_iw(self):
        """Parses Linux iw station dump output into BaselineTelemetry."""
        executor = MockSSHExecutor()
        runner = PhysicalBenchRunner(PhysicalBenchConfig(out_dir=self.temp_dir), executor=executor)
        telemetry = runner.capture_baseline()

        self.assertEqual(telemetry.signal_dbm, -62)
        self.assertEqual(telemetry.tx_mcs, 6)
        self.assertEqual(telemetry.tx_nss, 2)
        self.assertEqual(telemetry.tx_retries, 15)
        self.assertEqual(telemetry.tx_failed, 1)
        self.assertEqual(telemetry.tx_packets, 4096)
        self.assertEqual(telemetry.rx_packets, 2048)

    def test_capture_baseline_airos_wstalist(self):
        """Parses airOS wstalist JSON into BaselineTelemetry."""
        executor = MockSSHExecutor()
        raw_wstalist = json.dumps([{
            "mac": "F0:9F:C2:11:22:33",
            "signal": -58,
            "noisefloor": -96,
            "tx_rate": 200.0,
            "tx_mcs": 8,
            "tx_nss": 2,
            "tx_retries": 22,
            "tx_failed": 0,
            "tx_pkts": 8192,
            "rx_pkts": 4096,
            "tx_bytes": 10485760,
            "rx_bytes": 2097152,
        }])
        executor.set_response("wstalist", raw_wstalist)
        runner = PhysicalBenchRunner(PhysicalBenchConfig(out_dir=self.temp_dir), executor=executor)
        telemetry = runner.capture_baseline()

        self.assertEqual(telemetry.signal_dbm, -58)
        self.assertEqual(telemetry.noise_floor_dbm, -96)
        self.assertEqual(telemetry.snr_db, 38.0)
        self.assertEqual(telemetry.tx_mcs, 8)
        self.assertEqual(telemetry.tx_rate_mbps, 200.0)
        self.assertEqual(telemetry.tx_packets, 8192)

    def test_qdisc_treatments(self):
        """Verifies proper tc commands executed for baseline, cake, and fq_pacing."""
        # 1. Baseline
        exec_base = MockSSHExecutor()
        runner_base = PhysicalBenchRunner(
            PhysicalBenchConfig(treatment="baseline", out_dir=self.temp_dir),
            executor=exec_base,
        )
        runner_base.setup_qdisc()
        self.assertTrue(any("tc qdisc del" in cmd for _, cmd in exec_base.history))

        # 2. CAKE
        exec_cake = MockSSHExecutor()
        runner_cake = PhysicalBenchRunner(
            PhysicalBenchConfig(treatment="cake", cake_bandwidth="75Mbit", out_dir=self.temp_dir),
            executor=exec_cake,
        )
        runner_cake.setup_qdisc()
        self.assertTrue(any("cake bandwidth 75Mbit" in cmd and "diffserv4" in cmd for _, cmd in exec_cake.history))

        # 3. FQ Pacing
        exec_fq = MockSSHExecutor()
        runner_fq = PhysicalBenchRunner(
            PhysicalBenchConfig(treatment="fq_pacing", out_dir=self.temp_dir),
            executor=exec_fq,
        )
        runner_fq.setup_qdisc()
        self.assertTrue(any("root fq pacing" in cmd for _, cmd in exec_fq.history))

    def test_full_experiment_lifecycle_dry_run(self):
        """Executes full 9-stage lifecycle hermetically with dry-run."""
        cfg = PhysicalBenchConfig(
            experiment_id="FMX-0006-T1",
            treatment="cake",
            cake_bandwidth="50Mbit",
            duration_seconds=3,
            ping_interval_seconds=0.1,
            out_dir=self.temp_dir,
            dry_run=True,
        )
        runner = PhysicalBenchRunner(cfg)
        res = runner.execute_experiment()

        self.assertEqual(res.experiment_id, "FMX-0006-T1")
        self.assertEqual(res.restoration_status, "CLEAN_RESTORED")
        self.assertIsNone(res.error)
        self.assertGreater(res.goodput_mbps, 40.0)
        self.assertGreater(res.latency_stats.p50_ms, 0.0)
        self.assertIn(res.bufferbloat_grade, ["A+", "A", "B", "C", "D", "F"])

        # Check receipt files written
        json_files = list(Path(self.temp_dir).glob("*.json"))
        md_files = list(Path(self.temp_dir).glob("*.md"))
        self.assertEqual(len(json_files), 1)
        self.assertEqual(len(md_files), 1)

        with open(json_files[0], "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["experiment_id"], "FMX-0006-T1")
            self.assertEqual(data["restoration_status"], "CLEAN_RESTORED")

    def test_safety_restoration_guarantee_on_error(self):
        """Ensures cleanup_and_restore is ALWAYS executed even if workload fails."""
        cfg = PhysicalBenchConfig(
            experiment_id="FMX-0006-ERR",
            treatment="cake",
            out_dir=self.temp_dir,
            dry_run=False,
        )
        executor = MockSSHExecutor()
        runner = PhysicalBenchRunner(cfg, executor=executor)

        # Force run_workload_and_ping to raise an unhandled exception
        def blow_up():
            raise RuntimeError("Physical link disconnected during test")

        runner.run_workload_and_ping = blow_up  # type: ignore

        res = runner.execute_experiment()

        # Check that error was caught and restoration executed
        self.assertIn("Physical link disconnected", str(res.error))
        self.assertEqual(res.restoration_status, "CLEAN_RESTORED")

        # Verify cleanup commands were issued
        kill_cmds = [cmd for _, cmd in executor.history if "killall -9 iperf3" in cmd]
        self.assertGreater(len(kill_cmds), 0)
        qdisc_del_cmds = [cmd for _, cmd in executor.history if "tc qdisc del" in cmd]
        self.assertGreater(len(qdisc_del_cmds), 0)

    def test_pre_flight_probe_abort(self):
        """When pre-flight probe fails, the runner records error and restores."""
        cfg = PhysicalBenchConfig(
            experiment_id="FMX-0006-FAIL",
            ap_ip="10.254.254.1",  # Will fail
            out_dir=self.temp_dir,
            dry_run=False,
        )
        executor = MockSSHExecutor(failure_hosts=["10.254.254.1"])
        runner = PhysicalBenchRunner(cfg, executor=executor)
        res = runner.execute_experiment()

        self.assertIsNotNone(res.error)
        self.assertIn("Pre-flight probe failed", res.error)
        self.assertEqual(res.restoration_status, "CLEAN_RESTORED")


if __name__ == "__main__":
    unittest.main()
