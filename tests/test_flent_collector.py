#!/usr/bin/env python3
"""Unit tests for FuturaMAX Flent & Netperf Ingestion and Parser.

Verifies:
1. ExperimentMetric statistical calculation (p50, p90, p95, p99, loss %).
2. FlentDataset parsing from .flent.gz (gzip-compressed JSON) and uncompressed JSON.
3. Raw Netperf log parsing (TCP_STREAM, TCP_RR, interval time series, Omni format).
4. Conversion to standard FuturaMAX BufferbloatResult and grading.
5. Markdown formatting and JSON serialization.
6. Error handling for corrupt or missing files.
"""

from __future__ import annotations

import gzip
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.bench.flent_collector import (
    ExperimentMetric,
    FlentDataset,
    parse_flent_content,
    parse_flent_file,
    parse_netperf_file,
    parse_netperf_log,
)


class TestFlentCollector(unittest.TestCase):
    """Test suite for Flent and Netperf ingestion and normalization."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="fmx_flent_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_experiment_metric_stats(self):
        """Calculates accurate summary percentiles and statistics from samples."""
        samples = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0]
        metric = ExperimentMetric.from_samples("test_ping", "ms", samples)

        self.assertEqual(metric.name, "test_ping")
        self.assertEqual(metric.unit, "ms")
        self.assertEqual(metric.sample_count, 10)
        self.assertEqual(metric.min_val, 10.0)
        self.assertEqual(metric.max_val, 19.0)
        self.assertAlmostEqual(metric.mean_val, 14.5, places=1)
        self.assertAlmostEqual(metric.median_val, 14.5, places=1)
        self.assertEqual(metric.loss_pct, 0.0)
        self.assertGreater(metric.p95, metric.p50)

    def test_experiment_metric_with_loss_and_none(self):
        """Correctly accounts for None values and expected total for packet loss."""
        # 8 valid samples, 2 None values = 20% loss
        samples = [10.0, 12.0, None, 14.0, 16.0, 18.0, None, 20.0, 22.0, 24.0]
        metric = ExperimentMetric.from_samples(
            name="ping_loss",
            unit="ms",
            samples=samples,
            total_expected=10,
        )
        self.assertEqual(metric.sample_count, 8)
        self.assertEqual(metric.loss_pct, 20.0)

    def test_experiment_metric_empty(self):
        """Handles empty sample arrays gracefully."""
        metric = ExperimentMetric.from_samples("empty", "ms", [])
        self.assertEqual(metric.sample_count, 0)
        self.assertEqual(metric.min_val, 0.0)
        self.assertEqual(metric.loss_pct, 0.0)

    def test_parse_flent_json_uncompressed(self):
        """Parses standard uncompressed Flent JSON data structure."""
        flent_data = {
            "METADATA": {
                "TITLE": "RRUL Bufferbloat Test",
                "NAME": "rrul",
                "HOST": "10.99.0.2",
                "TOTAL_LENGTH": 30.0,
                "TIME": "2026-10-12T19:00:00",
            },
            "RAW_VALUES": {
                "ping_ipv4": [12.5, 14.2, 13.8, 15.1, 16.0],
                "TCP download BE": [48500000.0, 49200000.0, 50100000.0],  # in bits/sec
                "TCP upload BE": [24500000.0, 25100000.0, 24800000.0],
            },
        }
        dataset = parse_flent_content(json.dumps(flent_data))

        self.assertEqual(dataset.title, "RRUL Bufferbloat Test")
        self.assertEqual(dataset.target_host, "10.99.0.2")
        self.assertEqual(dataset.duration_seconds, 30.0)

        # Check ping metric
        ping = dataset.get_metric("ping_ipv4")
        self.assertIsNotNone(ping)
        self.assertEqual(ping.unit, "ms")
        self.assertEqual(ping.sample_count, 5)
        self.assertEqual(ping.min_val, 12.5)

        # Check throughput auto-conversion from bits/sec to Mbps
        dl = dataset.get_metric("TCP download BE")
        self.assertIsNotNone(dl)
        self.assertEqual(dl.unit, "Mbps")
        self.assertAlmostEqual(dl.mean_val, 49.27, places=1)

    def test_parse_flent_gz_file(self):
        """Reads and decompresses .flent.gz file directly from disk."""
        flent_data = {
            "METADATA": {
                "TITLE": "GZ Compressed RRUL",
                "NAME": "rrul",
                "HOST": "192.168.1.3",
                "DURATION": 15.0,
            },
            "RAW_VALUES": {
                "ping": [[0.0, 10.0], [0.1, 12.0], [0.2, 11.0]],
                "download": {"x": [0.0, 1.0, 2.0], "y": [45.0, 46.5, 48.0]},
            },
        }
        raw_bytes = gzip.compress(json.dumps(flent_data).encode("utf-8"))
        gz_path = Path(self.temp_dir) / "test_run.flent.gz"
        with open(gz_path, "wb") as f:
            f.write(raw_bytes)

        ds = parse_flent_file(gz_path)
        self.assertEqual(ds.title, "GZ Compressed RRUL")
        self.assertEqual(ds.target_host, "192.168.1.3")

        ping = ds.get_metric("ping")
        self.assertIsNotNone(ping)
        self.assertEqual(ping.sample_count, 3)

        dl = ds.get_metric("download")
        self.assertIsNotNone(dl)
        self.assertEqual(dl.sample_count, 3)
        self.assertAlmostEqual(dl.max_val, 48.0)

    def test_to_bufferbloat_result_conversion(self):
        """Converts FlentDataset into standard BufferbloatResult and assigns grade."""
        flent_data = {
            "METADATA": {
                "TITLE": "Bufferbloat Evaluation",
                "HOST": "10.99.0.2",
                "TOTAL_LENGTH": 10.0,
            },
            "RAW_VALUES": {
                "ping_ipv4": [15.0, 18.0, 22.0, 25.0, 28.0],
                "TCP download": [50.0, 52.0, 51.0],
            },
        }
        dataset = parse_flent_content(json.dumps(flent_data))
        bloat_res = dataset.to_bufferbloat_result(idle_baseline_ms=10.0)

        self.assertEqual(bloat_res.target, "10.99.0.2")
        self.assertEqual(bloat_res.direction, "download")
        self.assertAlmostEqual(bloat_res.goodput_mbps, 51.0, places=1)
        self.assertIsNotNone(bloat_res.bloat_p95_ms)
        self.assertIn(bloat_res.grade, ["A+", "A", "B", "C", "D", "F"])

        d = bloat_res.to_dict()
        self.assertEqual(d["target"], "10.99.0.2")
        self.assertIn("flent_title", d["metadata"])

    def test_parse_netperf_standard_tcp_stream(self):
        """Parses standard Netperf TCP_STREAM output banner."""
        netperf_output = """
MIGRATED TCP STREAM TEST from 0.0.0.0 (0.0.0.0) port 0 AF_INET to 192.168.1.1 () port 0 AF_INET : demo
Recv   Send    Send                          
Socket Socket  Message  Elapsed              
Size   Size    Size     Time     Throughput  
bytes  bytes   bytes    secs.    10^6bits/sec

 87380  16384  16384    10.00      48.52
"""
        metric = parse_netperf_log(netperf_output, metric_name="cpe_tcp_stream")
        self.assertEqual(metric.name, "cpe_tcp_stream")
        self.assertEqual(metric.unit, "Mbps")
        self.assertEqual(metric.sample_count, 1)
        self.assertAlmostEqual(metric.mean_val, 48.52)

    def test_parse_netperf_tcp_rr(self):
        """Parses Netperf TCP_RR output and converts transaction rate to RTT ms."""
        netperf_rr = """
MIGRATED TCP REQUEST/RESPONSE TEST from 0.0.0.0 (0.0.0.0) port 0 AF_INET to 192.168.1.1 () port 0 AF_INET : demo
Local /Remote
Socket Size   Request  Resp.   Elapsed  Trans.
Send   Recv   Size     Size    Time     Rate         
bytes  Bytes  bytes    bytes   secs.    per sec

16384  87380  1        1       10.00    100.00
"""
        metric = parse_netperf_log(netperf_rr)
        self.assertEqual(metric.name, "tcp_rr_rtt")
        self.assertEqual(metric.unit, "ms")
        self.assertEqual(metric.sample_count, 1)
        # 100 trans/sec = 10.0 ms avg RTT
        self.assertAlmostEqual(metric.mean_val, 10.0)

    def test_parse_netperf_time_series_file(self):
        """Parses Netperf interval demo time-series log file."""
        log_content = "0.50, 42.10\n1.00, 48.30\n1.50, 52.40\n2.00, 49.80\n"
        log_path = Path(self.temp_dir) / "netperf_ts.log"
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(log_content)

        metric = parse_netperf_file(log_path, metric_name="demo_stream")
        self.assertEqual(metric.sample_count, 4)
        self.assertEqual(metric.min_val, 42.1)
        self.assertEqual(metric.max_val, 52.4)
        self.assertEqual(metric.timestamps, [0.5, 1.0, 1.5, 2.0])

    def test_parse_netperf_omni_format(self):
        """Parses Netperf Omni output format."""
        omni = "THROUGHPUT=74.25\nELAPSED_TIME=10.00\n"
        metric = parse_netperf_log(omni, metric_name="omni_test")
        self.assertEqual(metric.sample_count, 1)
        self.assertAlmostEqual(metric.mean_val, 74.25)

    def test_missing_file_raises_error(self):
        """Attempting to parse a nonexistent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            parse_flent_file(Path(self.temp_dir) / "nonexistent.flent.gz")
        with self.assertRaises(FileNotFoundError):
            parse_netperf_file(Path(self.temp_dir) / "nonexistent.log")

    def test_format_summary_markdown(self):
        """Verifies markdown table generation for dataset."""
        dataset = FlentDataset(
            title="Summary Test",
            test_name="rrul",
            timestamp="2026-10-12T19:30:00",
            duration_seconds=10.0,
            target_host="192.168.1.3",
            metrics={
                "ping_ipv4": ExperimentMetric.from_samples("ping_ipv4", "ms", [12.0, 15.0, 18.0]),
            },
        )
        md = dataset.format_summary_markdown()
        self.assertIn("# Flent / RRUL Dataset: Summary Test", md)
        self.assertIn("| `ping_ipv4` | ms |", md)


if __name__ == "__main__":
    unittest.main()
