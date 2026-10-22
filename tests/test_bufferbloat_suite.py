"""Unit tests for tools/bench/bufferbloat_suite.py."""

import json
import unittest

from tools.bench.bufferbloat_suite import (
    BufferbloatResult,
    BufferbloatSuite,
    LatencyStats,
    build_cli,
    calculate_latency_stats,
    calculate_percentile,
    generate_cake_commands,
    generate_diffserv4_iptables_rules,
    generate_fq_codel_commands,
    generate_pacing_commands,
    generate_teardown_commands,
    grade_bufferbloat,
    parse_iperf3_json,
    parse_ping_output,
    run_bufferbloat_measurement,
)


class TestBufferbloatSuite(unittest.TestCase):
    """Test suite for bufferbloat measurement and tc qdisc generation."""

    def test_calculate_percentiles_basic(self):
        """Test statistical percentile calculation."""
        rtts = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0]
        stats = calculate_latency_stats(rtts, packets_sent=10, packets_recv=10)

        self.assertEqual(stats.sample_count, 10)
        self.assertEqual(stats.min_ms, 10.0)
        self.assertEqual(stats.max_ms, 28.0)
        self.assertEqual(stats.loss_pct, 0.0)
        self.assertGreater(stats.p95_ms, stats.p50_ms)
        self.assertGreaterEqual(stats.p99_ms, stats.p95_ms)
        self.assertEqual(stats.avg_ms, 19.0)

    def test_calculate_percentiles_with_loss(self):
        """Test calculation when packets are lost."""
        rtts = [15.0, 16.0, 17.0]
        stats = calculate_latency_stats(rtts, packets_sent=10, packets_recv=3)
        self.assertEqual(stats.sample_count, 3)
        self.assertEqual(stats.loss_pct, 70.0)

    def test_calculate_percentiles_empty(self):
        """Test handling of empty sample lists."""
        stats = calculate_latency_stats([], packets_sent=10, packets_recv=0)
        self.assertEqual(stats.sample_count, 0)
        self.assertEqual(stats.p50_ms, 0.0)
        self.assertEqual(stats.loss_pct, 100.0)

    def test_grade_bufferbloat(self):
        """Test grading tiers."""
        self.assertEqual(grade_bufferbloat(3.0), "A+")
        self.assertEqual(grade_bufferbloat(10.0), "A")
        self.assertEqual(grade_bufferbloat(25.0), "B")
        self.assertEqual(grade_bufferbloat(45.0), "C")
        self.assertEqual(grade_bufferbloat(100.0), "D")
        self.assertEqual(grade_bufferbloat(250.0), "F")

    def test_parse_ping_output(self):
        """Test parsing Linux ping command output."""
        sample_output = """PING 10.99.0.1 (10.99.0.1) 56(84) bytes of data.
64 bytes from 10.99.0.1: icmp_seq=1 ttl=64 time=1.24 ms
64 bytes from 10.99.0.1: icmp_seq=2 ttl=64 time=1.85 ms
64 bytes from 10.99.0.1: icmp_seq=3 ttl=64 time=1.42 ms

--- 10.99.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 1.240/1.503/1.850/0.256 ms
"""
        rtts, sent, recv = parse_ping_output(sample_output)
        self.assertEqual(len(rtts), 3)
        self.assertEqual(rtts, [1.24, 1.85, 1.42])
        self.assertEqual(sent, 3)
        self.assertEqual(recv, 3)

    def test_parse_iperf3_json(self):
        """Test parsing iperf3 JSON output."""
        sample_json = json.dumps({
            "end": {
                "sum_received": {
                    "bits_per_second": 94500000.0,
                },
                "sum_sent": {
                    "bits_per_second": 95000000.0,
                    "retransmits": 5,
                },
            }
        })
        res = parse_iperf3_json(sample_json)
        self.assertEqual(res["throughput_mbps"], 94.5)
        self.assertEqual(res["retransmits"], 5)

    def test_generate_cake_commands_egress(self):
        """Test generating CAKE tc commands for egress."""
        cmds = generate_cake_commands(iface="eth0", bandwidth="50Mbit", diffserv="diffserv4")
        joined = "\n".join(cmds)
        self.assertIn("tc qdisc replace dev eth0 root cake bandwidth 50Mbit diffserv4", joined)
        self.assertIn("ack-filter", joined)
        self.assertIn("wash", joined)

    def test_generate_cake_commands_ingress(self):
        """Test generating CAKE tc commands for ingress via IFB."""
        cmds = generate_cake_commands(iface="eth0", bandwidth="40Mbit", ingress=True, ifb_dev="ifb4eth0")
        joined = "\n".join(cmds)
        self.assertIn("modprobe ifb", joined)
        self.assertIn("ip link add dev ifb4eth0 type ifb", joined)
        self.assertIn("action mirred egress redirect dev ifb4eth0", joined)
        self.assertIn("tc qdisc replace dev ifb4eth0 root cake bandwidth 40Mbit diffserv4", joined)
        self.assertIn("autorate_ingress", joined)

    def test_generate_fq_codel_commands(self):
        """Test generating FQ-CoDel tc commands."""
        cmds = generate_fq_codel_commands(iface="eth0", bandwidth="30Mbit", target="5ms", interval="100ms")
        joined = "\n".join(cmds)
        self.assertIn("tc qdisc replace dev eth0 root handle 1: htb default 1", joined)
        self.assertIn("tc class add dev eth0 parent 1: classid 1:1 htb rate 30Mbit ceil 30Mbit", joined)
        self.assertIn("tc qdisc replace dev eth0 parent 1:1 handle 10: fq_codel limit 1024 target 5ms interval 100ms ecn", joined)

    def test_generate_pacing_commands(self):
        """Test generating sch_fq pacing tc commands."""
        cmds = generate_pacing_commands(iface="eth0", maxrate="50Mbit")
        joined = "\n".join(cmds)
        self.assertIn("tc qdisc replace dev eth0 root fq maxrate 50Mbit pacing", joined)

    def test_generate_diffserv4_iptables_rules(self):
        """Test generating DiffServ4 DSCP classification iptables rules."""
        rules = generate_diffserv4_iptables_rules(iface="eth0")
        joined = "\n".join(rules)
        self.assertIn("--set-dscp-class EF", joined)
        self.assertIn("--set-dscp-class AF41", joined)
        self.assertIn("--set-dscp-class CS1", joined)

    def test_generate_teardown_commands(self):
        """Test generating teardown commands."""
        cmds = generate_teardown_commands(iface="eth0", ifb_dev="ifb4eth0")
        joined = "\n".join(cmds)
        self.assertIn("tc qdisc del dev eth0 root", joined)
        self.assertIn("tc qdisc del dev eth0 ingress", joined)
        self.assertIn("ip link del dev ifb4eth0", joined)

    def test_dry_run_bufferbloat_measurement(self):
        """Test hermetic dry-run bufferbloat measurement."""
        res = run_bufferbloat_measurement(
            target="10.99.0.1",
            iperf_server="10.99.0.1",
            duration=5,
            streams=2,
            direction="down",
            dry_run=True,
        )
        self.assertIsInstance(res, BufferbloatResult)
        self.assertEqual(res.target, "10.99.0.1")
        self.assertEqual(res.direction, "down")
        self.assertIsNotNone(res.goodput_mbps)
        self.assertIsNotNone(res.idle_stats)
        self.assertIsNotNone(res.loaded_stats)
        self.assertIsNotNone(res.bloat_p95_ms)
        self.assertIn(res.grade, ["A+", "A", "B", "C", "D", "F"])

        d = res.to_dict()
        self.assertIn("idle_stats", d)
        self.assertIn("loaded_stats", d)
        self.assertIn("grade", d)

    def test_cli_parsing(self):
        """Test CLI argument parsing."""
        parser = build_cli()
        args = parser.parse_args(["generate-tc", "--qdisc", "cake", "--bandwidth", "60Mbit"])
        self.assertEqual(args.command, "generate-tc")
        self.assertEqual(args.qdisc, "cake")
        self.assertEqual(args.bandwidth, "60Mbit")

        bench_args = parser.parse_args(["bench", "--target", "10.99.0.1", "--dry-run", "--duration", "5"])
        self.assertEqual(bench_args.command, "bench")
        self.assertEqual(bench_args.target, "10.99.0.1")
        self.assertTrue(bench_args.dry_run)


if __name__ == "__main__":
    unittest.main()
