"""Unit tests for workloads.flent_orchestrator (FlentWorkloadOrchestrator)."""

import unittest
from workloads.flent_orchestrator import (
    FlentWorkloadOrchestrator,
    FlentWorkloadConfig,
)


SAMPLE_IPERF3_JSON = """{
  "start": {"timestamp": {"time": "Sun, 27 Sep 2026 00:00:00 GMT"}},
  "end": {
    "sum_sent": {
      "seconds": 10.0001,
      "bytes": 52428800,
      "bits_per_second": 41942621.0,
      "retransmits": 14
    },
    "sum_received": {
      "seconds": 10.0001,
      "bytes": 51200000,
      "bits_per_second": 40959590.0
    }
  }
}"""

SAMPLE_PING_OUTPUT = """
PING 192.168.1.1 (192.168.1.1): 56 data bytes
64 bytes from 192.168.1.1: seq=0 ttl=64 time=4.12 ms
64 bytes from 192.168.1.1: seq=1 ttl=64 time=5.84 ms
64 bytes from 192.168.1.1: seq=2 ttl=64 time=12.50 ms
64 bytes from 192.168.1.1: seq=3 ttl=64 time=8.20 ms
64 bytes from 192.168.1.1: seq=4 ttl=64 time=25.40 ms
"""


class TestFlentWorkloadOrchestrator(unittest.TestCase):
    def test_parse_iperf3_json(self):
        res = FlentWorkloadOrchestrator.parse_iperf3_json(SAMPLE_IPERF3_JSON)
        self.assertAlmostEqual(res["goodput_mbps"], 40.96, places=2)
        self.assertEqual(res["retransmits"], 14)

    def test_parse_ping_latencies(self):
        times = FlentWorkloadOrchestrator.parse_ping_latencies(SAMPLE_PING_OUTPUT)
        self.assertEqual(len(times), 5)
        self.assertEqual(times[0], 4.12)
        self.assertEqual(times[-1], 25.40)

    def test_calculate_percentiles(self):
        latencies = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        pcts = FlentWorkloadOrchestrator.calculate_percentiles(latencies)
        self.assertEqual(pcts["p50"], 5.0)
        self.assertEqual(pcts["p95"], 10.0)
        self.assertEqual(pcts["p99"], 10.0)

    def test_synthesize_report(self):
        cfg = FlentWorkloadConfig(
            server_host="192.168.1.1",
            station_hosts=["192.168.1.101", "192.168.1.102"],
            direction="upload",
        )
        orch = FlentWorkloadOrchestrator(cfg)

        iperf_data = {
            "192.168.1.101": {"goodput_mbps": 30.0, "retransmits": 5},
            "192.168.1.102": {"goodput_mbps": 30.0, "retransmits": 3},
        }
        ping_data = {
            "192.168.1.101": [5.0, 6.0, 10.0, 15.0],
            "192.168.1.102": [4.0, 7.0, 9.0, 18.0],
        }

        report = orch.synthesize_report(iperf_data, ping_data)

        self.assertEqual(report.aggregate_goodput_mbps, 60.0)
        self.assertEqual(report.jain_fairness_index, 1.0)  # equal throughput
        self.assertEqual(report.total_retransmits, 8)
        self.assertGreater(report.fleet_p99_latency_ms, 15.0)


if __name__ == "__main__":
    unittest.main()
