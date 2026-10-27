#!/usr/bin/env python3
"""Bufferbloat and Latency Under Load Measurement Suite for Arch Linux ("Omarchy").

Designed for automated benchmarking on an Arch Linux test station ("Omarchy")
connected to an airMAX AC CPE (NanoStation 5AC / LiteBeam 5AC Gen2).

Capabilities:
1. Automated traffic measurement:
   - Saturated iperf3 traffic: TCP DL, TCP UL, UDP 20M, UDP 50M, UDP 100M
   - Concurrent high-frequency ICMP ping sampling (default 0.02s interval)
   - Latency distribution statistics: p50, p90, p95, p99, min, max, avg, jitter, packet loss
   - Industry-standard bufferbloat grading (A+ to F)
   - Structured JSON receipts saved in research/raw/bench/
2. Linux tc qdisc command generation:
   - CAKE with DiffServ4 tin isolation, ACK filtering, wash, and pacing
   - HTB + FQ-CoDel with configurable target/interval and ECN
   - sch_fq pacing qdisc configuration
   - Ingress IFB redirection rules for ingress shaping
   - DiffServ4 / DSCP classification rules
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import statistics
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

DEFAULT_AP_MGMT = "192.168.1.2"
DEFAULT_AP_WLINK = "10.99.0.1"
DEFAULT_CPE_MGMT = "192.168.1.3"
DEFAULT_CPE_WLINK = "10.99.0.2"
DEFAULT_IFACE = "eth0"
DEFAULT_IFB = "ifb4eth0"


@dataclass
class LatencyStats:
    """Latency distribution statistics in milliseconds."""
    sample_count: int = 0
    min_ms: float = 0.0
    p50_ms: float = 0.0
    p90_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    max_ms: float = 0.0
    mean_ms: float = 0.0
    avg_ms: float = 0.0
    stddev_ms: float = 0.0
    jitter_ms: float = 0.0
    max_jitter_ms: float = 0.0
    rfc3550_jitter_ms: float = 0.0
    loss_pct: float = 0.0
    packet_loss_pct: float = 0.0
    packets_sent: int = 0
    packets_recv: int = 0

    def __post_init__(self):
        if self.avg_ms == 0.0 and self.mean_ms != 0.0:
            object.__setattr__(self, "avg_ms", self.mean_ms)
        elif self.mean_ms == 0.0 and self.avg_ms != 0.0:
            object.__setattr__(self, "mean_ms", self.avg_ms)

        if self.packet_loss_pct == 0.0 and self.loss_pct != 0.0:
            object.__setattr__(self, "packet_loss_pct", self.loss_pct)
        elif self.loss_pct == 0.0 and self.packet_loss_pct != 0.0:
            object.__setattr__(self, "loss_pct", self.packet_loss_pct)

        if self.jitter_ms == 0.0 and self.max_jitter_ms != 0.0:
            object.__setattr__(self, "jitter_ms", self.max_jitter_ms)
        elif self.max_jitter_ms == 0.0 and self.jitter_ms != 0.0:
            object.__setattr__(self, "max_jitter_ms", self.jitter_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestResult:
    """Result of an individual traffic load benchmark."""
    profile: str
    target: str
    duration_secs: float
    throughput_mbps: float
    retransmits: Optional[int] = None
    udp_loss_pct: Optional[float] = None
    udp_jitter_ms: Optional[float] = None
    latency: LatencyStats = field(default_factory=LatencyStats)
    raw_rtts: List[float] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BenchReceipt:
    """Complete bench receipt for a bufferbloat evaluation run."""
    run_id: str
    timestamp: str
    target: str
    platform: str
    ping_interval_secs: float
    results: Dict[str, TestResult] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "target": self.target,
            "platform": self.platform,
            "ping_interval_secs": self.ping_interval_secs,
            "results": {k: v.to_dict() for k, v in self.results.items()},
            "summary": self.summary,
        }


@dataclass
class BufferbloatResult:
    """Legacy individual bufferbloat benchmark result."""
    timestamp: str
    target: str
    iperf_server: str
    direction: str
    duration_s: float
    streams: int
    goodput_mbps: Optional[float]
    retransmits: Optional[int]
    idle_stats: Optional[LatencyStats]
    loaded_stats: Optional[LatencyStats]
    bloat_p50_ms: Optional[float]
    bloat_p95_ms: Optional[float]
    bloat_p99_ms: Optional[float]
    grade: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def calculate_percentile(sorted_data: List[float], percentile: float) -> float:
    """Calculate percentile using linear interpolation between nearest ranks."""
    if not sorted_data:
        return 0.0
    if len(sorted_data) == 1:
        return round(sorted_data[0], 3)
    k = (len(sorted_data) - 1) * (percentile / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return round(sorted_data[int(k)], 3)
    d0 = sorted_data[int(f)] * (c - k)
    d1 = sorted_data[int(c)] * (k - f)
    return round(d0 + d1, 3)


def calculate_percentiles(rtts: List[float], sent_count: Optional[int] = None) -> LatencyStats:
    """Calculate latency percentiles and jitter from a list of RTT measurements in milliseconds."""
    n = len(rtts)
    total_sent = sent_count if (sent_count is not None and sent_count >= n) else n
    return calculate_latency_stats(rtts, packets_sent=total_sent, packets_recv=n)


def calculate_latency_stats(
    rtts: List[float],
    packets_sent: int,
    packets_recv: int,
) -> LatencyStats:
    """Calculates comprehensive latency metrics from collected RTTs and packet counts."""
    stats = LatencyStats(
        sample_count=len(rtts),
        packets_sent=packets_sent,
        packets_recv=packets_recv,
    )

    if packets_sent > 0:
        lost = max(0, packets_sent - packets_recv)
        loss_pct = round((lost / packets_sent) * 100.0, 2)
        stats.loss_pct = loss_pct
        stats.packet_loss_pct = loss_pct
    elif rtts:
        stats.loss_pct = 0.0
        stats.packet_loss_pct = 0.0

    if not rtts:
        return stats

    sorted_rtts = sorted(rtts)
    n = len(sorted_rtts)

    stats.min_ms = round(sorted_rtts[0], 3)
    stats.max_ms = round(sorted_rtts[-1], 3)
    mean_val = round(sum(sorted_rtts) / n, 3)
    stats.mean_ms = mean_val
    stats.avg_ms = mean_val

    stats.p50_ms = calculate_percentile(sorted_rtts, 50.0)
    stats.p90_ms = calculate_percentile(sorted_rtts, 90.0)
    stats.p95_ms = calculate_percentile(sorted_rtts, 95.0)
    stats.p99_ms = calculate_percentile(sorted_rtts, 99.0)

    if n > 1:
        stats.stddev_ms = round(statistics.stdev(rtts), 3)

    max_consec_jitter = 0.0
    rfc_jitter = 0.0
    for i in range(1, len(rtts)):
        delta = abs(rtts[i] - rtts[i - 1])
        if delta > max_consec_jitter:
            max_consec_jitter = delta
        rfc_jitter += (delta - rfc_jitter) / 16.0

    stats.max_jitter_ms = round(max_consec_jitter, 3)
    stats.jitter_ms = round(max_consec_jitter, 3)
    stats.rfc3550_jitter_ms = round(rfc_jitter, 3)

    return stats


def grade_bufferbloat(delta_p95_ms: float) -> str:
    """Grade bufferbloat latency degradation according to industry standards.

    A+: < 5 ms delta
    A : < 15 ms delta
    B : < 30 ms delta
    C : < 60 ms delta
    D : < 150 ms delta
    F : >= 150 ms delta
    """
    if delta_p95_ms < 5.0:
        return "A+"
    elif delta_p95_ms < 15.0:
        return "A"
    elif delta_p95_ms < 30.0:
        return "B"
    elif delta_p95_ms < 60.0:
        return "C"
    elif delta_p95_ms < 150.0:
        return "D"
    else:
        return "F"


def parse_ping_output(output: str) -> Tuple[List[float], int, int]:
    """Parse ping output lines to extract individual RTT values, sent packet count, and received packet count."""
    rtts: List[float] = []
    sent_count = 0
    recv_count = 0

    for line in output.splitlines():
        m = re.search(r"time=([0-9\.]+)\s*ms", line)
        if m:
            try:
                rtts.append(float(m.group(1)))
            except ValueError:
                pass

        m_trans = re.search(r"(\d+)\s+packets transmitted,\s+(\d+)\s+(?:packets )?received", line)
        if m_trans:
            sent_count = int(m_trans.group(1))
            recv_count = int(m_trans.group(2))

    if sent_count == 0:
        m_sent = re.search(r"(\d+)\s+packets transmitted", output)
        if m_sent:
            sent_count = int(m_sent.group(1))
        elif rtts:
            sent_count = len(rtts)

    if recv_count == 0 and rtts:
        recv_count = len(rtts)

    return rtts, sent_count, recv_count


class Iperf3ResultDict(dict):
    """Dictionary that also unpacks cleanly as a 2-tuple (goodput_mbps, retransmits)."""
    def __iter__(self):
        # If someone iterates or unpacks `goodput, retrans = parse_iperf3_json(...)`
        return iter((self.get("throughput_mbps"), self.get("retransmits")))

    def __getitem__(self, key):
        return super().__getitem__(key)


def parse_iperf3_json(output: Union[str, dict]) -> Iperf3ResultDict:
    """Parse iperf3 JSON output to extract goodput, retransmits, or UDP loss/jitter."""
    if isinstance(output, str):
        idx = output.find("{")
        if idx == -1:
            return Iperf3ResultDict({"error": "Invalid JSON output from iperf3", "throughput_mbps": None, "retransmits": None})
        try:
            data = json.loads(output[idx:])
        except json.JSONDecodeError as err:
            return Iperf3ResultDict({"error": f"JSON decode error: {err}", "throughput_mbps": None, "retransmits": None})
    else:
        data = output

    if "error" in data:
        return Iperf3ResultDict({"error": str(data["error"]), "throughput_mbps": None, "retransmits": None})

    end = data.get("end", {})
    sum_sent = end.get("sum_sent", {})
    sum_recv = end.get("sum_received", {})
    sum_udp = end.get("sum", {})

    # Check for UDP results
    if "lost_percent" in sum_udp or "jitter_ms" in sum_udp:
        bps = sum_udp.get("bits_per_second", 0.0)
        return Iperf3ResultDict({
            "throughput_mbps": round(bps / 1e6, 2),
            "udp_loss_pct": round(sum_udp.get("lost_percent", 0.0), 2),
            "udp_jitter_ms": round(sum_udp.get("jitter_ms", 0.0), 3),
            "retransmits": None,
        })

    # TCP results
    bps = sum_recv.get("bits_per_second", sum_sent.get("bits_per_second", 0.0))
    retransmits = sum_sent.get("retransmits")
    return Iperf3ResultDict({
        "throughput_mbps": round(bps / 1e6, 2),
        "udp_loss_pct": None,
        "udp_jitter_ms": None,
        "retransmits": retransmits,
    })


def generate_cake_commands(
    iface: str = DEFAULT_IFACE,
    bandwidth: str = "50Mbit",
    diffserv: str = "diffserv4",
    rtt: str = "100ms",
    ack_filter: bool = True,
    nat: bool = False,
    wash: bool = True,
    ingress: bool = False,
    ifb_dev: str = DEFAULT_IFB,
) -> List[str]:
    """Generate Linux tc qdisc commands for CAKE queue discipline with DiffServ4."""
    options = [
        f"bandwidth {bandwidth}",
        diffserv,
        f"rtt {rtt}",
    ]
    if ack_filter:
        options.append("ack-filter")
    if nat:
        options.append("nat")
    if wash:
        options.append("wash")

    cake_opts = " ".join(options)
    cmds: List[str] = []

    if ingress:
        cmds.extend([
            f"modprobe ifb 2>/dev/null || true",
            f"ip link add dev {ifb_dev} type ifb 2>/dev/null || true",
            f"ip link set dev {ifb_dev} up",
            f"tc qdisc del dev {iface} ingress 2>/dev/null || true",
            f"tc qdisc add dev {iface} handle ffff: ingress",
            f"tc filter add dev {iface} parent ffff: protocol all u32 match u32 0 0 action mirred egress redirect dev {ifb_dev}",
            f"tc qdisc del dev {ifb_dev} root 2>/dev/null || true",
            f"tc qdisc replace dev {ifb_dev} root cake {cake_opts} autorate_ingress",
        ])
    else:
        cmds.extend([
            f"tc qdisc del dev {iface} root 2>/dev/null || true",
            f"tc qdisc replace dev {iface} root cake {cake_opts}",
        ])

    return cmds


def generate_fq_codel_commands(
    iface: str = DEFAULT_IFACE,
    bandwidth: str = "50Mbit",
    target: str = "5ms",
    interval: str = "100ms",
    limit: int = 1024,
    ecn: bool = True,
    ingress: bool = False,
    ifb_dev: str = DEFAULT_IFB,
) -> List[str]:
    """Generate Linux tc qdisc commands for HTB rate shaper with FQ-CoDel leaf."""
    ecn_opt = "ecn" if ecn else "noecn"
    cmds: List[str] = []
    dev = ifb_dev if ingress else iface

    if ingress:
        cmds.extend([
            f"modprobe ifb 2>/dev/null || true",
            f"ip link add dev {ifb_dev} type ifb 2>/dev/null || true",
            f"ip link set dev {ifb_dev} up",
            f"tc qdisc del dev {iface} ingress 2>/dev/null || true",
            f"tc qdisc add dev {iface} handle ffff: ingress",
            f"tc filter add dev {iface} parent ffff: protocol all u32 match u32 0 0 action mirred egress redirect dev {ifb_dev}",
        ])

    cmds.extend([
        f"tc qdisc del dev {dev} root 2>/dev/null || true",
        f"tc qdisc replace dev {dev} root handle 1: htb default 1",
        f"tc class add dev {dev} parent 1: classid 1:1 htb rate {bandwidth} ceil {bandwidth}",
        f"tc qdisc replace dev {dev} parent 1:1 handle 10: fq_codel limit {limit} target {target} interval {interval} {ecn_opt}",
    ])

    return cmds


def generate_pacing_commands(iface: str = DEFAULT_IFACE, maxrate: str = "50Mbit") -> List[str]:
    """Generate Linux sch_fq pacing qdisc commands."""
    return [
        f"tc qdisc del dev {iface} root 2>/dev/null || true",
        f"tc qdisc replace dev {iface} root fq maxrate {maxrate} pacing",
    ]


def generate_diffserv4_iptables_rules(iface: str = DEFAULT_IFACE) -> List[str]:
    """Generate iptables DSCP marking rules for DiffServ4 classes."""
    return [
        f"iptables -t mangle -A POSTROUTING -o {iface} -p udp --dport 5060 -j DSCP --set-dscp-class EF",
        f"iptables -t mangle -A POSTROUTING -o {iface} -p udp --dport 16384:32767 -j DSCP --set-dscp-class EF",
        f"iptables -t mangle -A POSTROUTING -o {iface} -p tcp --dport 554 -j DSCP --set-dscp-class AF41",
        f"iptables -t mangle -A POSTROUTING -o {iface} -p tcp --dport 20:21 -j DSCP --set-dscp-class CS1",
        f"iptables -t mangle -A POSTROUTING -o {iface} -p tcp --dport 6881:6889 -j DSCP --set-dscp-class CS1",
    ]


def generate_teardown_commands(iface: str = DEFAULT_IFACE, ifb_dev: str = DEFAULT_IFB) -> List[str]:
    """Generate teardown commands to cleanly remove all qdiscs and restore defaults."""
    return [
        f"tc qdisc del dev {iface} root 2>/dev/null || true",
        f"tc qdisc del dev {iface} ingress 2>/dev/null || true",
        f"tc qdisc del dev {ifb_dev} root 2>/dev/null || true",
        f"ip link set dev {ifb_dev} down 2>/dev/null || true",
        f"ip link del dev {ifb_dev} 2>/dev/null || true",
        f"iptables -t mangle -F POSTROUTING 2>/dev/null || true",
    ]


class BufferbloatSuite:
    """Executes traffic saturation and concurrent ping measurements across profiles."""

    SUPPORTED_MODES = [
        "tcp_dl",
        "tcp_ul",
        "udp_20m",
        "udp_50m",
        "udp_100m",
    ]

    def __init__(
        self,
        target_ip: str = DEFAULT_AP_WLINK,
        ping_interval: float = 0.02,
        duration: int = 10,
        streams: int = 1,
        out_dir: Optional[Union[str, Path]] = None,
        dry_run: bool = False,
    ):
        self.target_ip = target_ip
        self.ping_interval = ping_interval
        self.duration = duration
        self.streams = streams
        self.dry_run = dry_run

        if out_dir is None:
            today = dt.date.today().isoformat()
            self.out_dir = Path("research/raw/bench") / today
        else:
            self.out_dir = Path(out_dir)

    def _build_ping_cmd(self, count: int) -> List[str]:
        cmd = []
        is_linux = sys.platform.startswith("linux")
        if is_linux and self.ping_interval < 0.2 and os.geteuid() != 0:
            cmd.append("sudo")
        cmd.extend(["ping", "-c", str(count), "-i", str(self.ping_interval), "-W", "1", self.target_ip])
        return cmd

    def _build_iperf_cmd(self, profile: str) -> List[str]:
        cmd = ["iperf3", "-c", self.target_ip, "-t", str(self.duration), "-i", "0", "-J"]
        if profile == "tcp_dl":
            cmd.extend(["-R", "-P", str(self.streams)])
        elif profile == "tcp_ul":
            cmd.extend(["-P", str(self.streams)])
        elif profile == "udp_20m":
            cmd.extend(["-u", "-b", "20M", "-l", "1400"])
        elif profile == "udp_50m":
            cmd.extend(["-u", "-b", "50M", "-l", "1400"])
        elif profile == "udp_100m":
            cmd.extend(["-u", "-b", "100M", "-l", "1400"])
        else:
            raise ValueError(f"Unknown profile: {profile}")
        return cmd

    def run_single_measurement(self, profile: str) -> TestResult:
        """Runs saturation traffic with concurrent ping sampling."""
        if self.dry_run:
            sample_count = max(10, int(self.duration / self.ping_interval))
            synthetic_rtts = [1.5 + (i % 8) * 0.4 for i in range(sample_count)]
            stats = calculate_latency_stats(synthetic_rtts, len(synthetic_rtts), len(synthetic_rtts))
            return TestResult(
                profile=profile,
                target=self.target_ip,
                duration_secs=float(self.duration),
                throughput_mbps=85.5 if "tcp" in profile else 48.2,
                retransmits=0 if "tcp" in profile else None,
                udp_loss_pct=0.0 if "udp" in profile else None,
                latency=stats,
                raw_rtts=synthetic_rtts,
            )

        iperf_cmd = self._build_iperf_cmd(profile)
        ping_count = max(5, int(self.duration / self.ping_interval))
        ping_cmd = self._build_ping_cmd(ping_count)

        iperf_output = ""
        ping_output = ""
        iperf_err = ""
        ping_err = ""

        def exec_iperf():
            nonlocal iperf_output, iperf_err
            try:
                proc = subprocess.run(iperf_cmd, capture_output=True, text=True, timeout=self.duration + 30)
                iperf_output = proc.stdout
                iperf_err = proc.stderr
            except Exception as e:
                iperf_err = str(e)

        def exec_ping():
            nonlocal ping_output, ping_err
            time.sleep(0.5)
            try:
                proc = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=self.duration + 20)
                ping_output = proc.stdout
                ping_err = proc.stderr
            except Exception as e:
                ping_err = str(e)

        t_iperf = threading.Thread(target=exec_iperf)
        t_ping = threading.Thread(target=exec_ping)

        t_iperf.start()
        t_ping.start()

        t_iperf.join()
        t_ping.join()

        parsed_iperf = parse_iperf3_json(iperf_output)
        error = parsed_iperf.get("error")
        if error is None and iperf_err and "error" in iperf_err.lower():
            error = iperf_err

        rtts, sent, recv = parse_ping_output(ping_output)
        stats = calculate_latency_stats(rtts, sent, recv)

        return TestResult(
            profile=profile,
            target=self.target_ip,
            duration_secs=float(self.duration),
            throughput_mbps=parsed_iperf.get("throughput_mbps") or 0.0,
            retransmits=parsed_iperf.get("retransmits"),
            udp_loss_pct=parsed_iperf.get("udp_loss_pct"),
            udp_jitter_ms=parsed_iperf.get("udp_jitter_ms"),
            latency=stats,
            raw_rtts=rtts,
            error=error,
        )

    def run_suite(self, profiles: Optional[List[str]] = None) -> BenchReceipt:
        """Runs the complete suite across all requested traffic profiles."""
        if profiles is None:
            profiles = list(self.SUPPORTED_MODES)

        run_id = f"bb-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        receipt = BenchReceipt(
            run_id=run_id,
            timestamp=dt.datetime.now().isoformat(),
            target=self.target_ip,
            platform=sys.platform,
            ping_interval_secs=self.ping_interval,
        )

        for prof in profiles:
            result = self.run_single_measurement(prof)
            receipt.results[prof] = result

        p95_values = [
            r.latency.p95_ms
            for r in receipt.results.values()
            if r.latency.sample_count > 0 and r.latency.p95_ms > 0
        ]
        avg_p95 = statistics.mean(p95_values) if p95_values else 0.0
        max_p95 = max(p95_values) if p95_values else 0.0

        if max_p95 == 0.0:
            grade = "INCONCLUSIVE"
        elif max_p95 < 10.0:
            grade = "A+"
        elif max_p95 < 25.0:
            grade = "A"
        elif max_p95 < 50.0:
            grade = "B"
        elif max_p95 < 100.0:
            grade = "C"
        else:
            grade = "F"

        receipt.summary = {
            "total_profiles_tested": len(receipt.results),
            "avg_loaded_p95_ms": round(avg_p95, 3),
            "max_loaded_p95_ms": round(max_p95, 3),
            "bufferbloat_grade": grade,
        }

        return receipt

    def save_receipt(self, receipt: BenchReceipt) -> Path:
        """Saves structured JSON receipt to disk in research/raw/bench/."""
        self.out_dir.mkdir(parents=True, exist_ok=True)
        out_file = self.out_dir / f"{receipt.run_id}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(receipt.to_dict(), f, indent=2)
        return out_file


def run_bufferbloat_measurement(
    target: str = DEFAULT_AP_WLINK,
    iperf_server: str = DEFAULT_AP_WLINK,
    duration: int = 10,
    streams: int = 4,
    direction: str = "down",
    dry_run: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> BufferbloatResult:
    """Run an automated bufferbloat measurement test."""
    ts = dt.datetime.now(dt.timezone.utc).isoformat()
    meta = metadata or {}

    if dry_run:
        idle_rtts = [1.2, 1.4, 1.3, 1.5, 1.4, 1.6, 1.3, 1.5, 1.4, 1.3]
        idle_stats = calculate_percentiles(idle_rtts, len(idle_rtts))
        loaded_rtts = [12.5, 14.2, 13.8, 15.1, 14.7, 16.3, 15.0, 18.2, 14.9, 15.5]
        loaded_stats = calculate_percentiles(loaded_rtts, len(loaded_rtts))

        goodput_mbps = 85.4
        retransmits = 2
        bloat_p50 = round(loaded_stats.p50_ms - idle_stats.p50_ms, 2)
        bloat_p95 = round(loaded_stats.p95_ms - idle_stats.p50_ms, 2)
        bloat_p99 = round(loaded_stats.p99_ms - idle_stats.p50_ms, 2)
        grade = grade_bufferbloat(bloat_p95)

        return BufferbloatResult(
            timestamp=ts,
            target=target,
            iperf_server=iperf_server,
            direction=direction,
            duration_s=float(duration),
            streams=streams,
            goodput_mbps=goodput_mbps,
            retransmits=retransmits,
            idle_stats=idle_stats,
            loaded_stats=loaded_stats,
            bloat_p50_ms=bloat_p50,
            bloat_p95_ms=bloat_p95,
            bloat_p99_ms=bloat_p99,
            grade=grade,
            metadata=meta,
        )

    # Live measurement
    idle_cmd = ["ping", "-c", "10", "-i", "0.2", "-W", "1", target]
    try:
        res_idle = subprocess.run(idle_cmd, capture_output=True, text=True, timeout=15)
        idle_rtts, idle_sent, _ = parse_ping_output(res_idle.stdout)
    except Exception:
        idle_rtts, idle_sent = [], 10

    idle_stats = calculate_percentiles(idle_rtts, idle_sent)

    iperf_flags = ["-c", iperf_server, "-t", str(duration), "-P", str(streams), "-J"]
    if direction == "down":
        iperf_flags.append("-R")

    iperf_proc = subprocess.Popen(["iperf3"] + iperf_flags, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.5)

    ping_count = max(5, int((duration - 1) / 0.02))
    load_cmd = ["ping", "-c", str(ping_count), "-i", "0.02", "-W", "1", target]
    try:
        res_loaded = subprocess.run(load_cmd, capture_output=True, text=True, timeout=duration + 10)
        loaded_rtts, loaded_sent, _ = parse_ping_output(res_loaded.stdout)
    except Exception:
        loaded_rtts, loaded_sent = [], ping_count

    loaded_stats = calculate_percentiles(loaded_rtts, loaded_sent)

    try:
        iperf_out, _ = iperf_proc.communicate(timeout=duration + 15)
        parsed_res = parse_iperf3_json(iperf_out)
        goodput_mbps, retransmits = parsed_res.get("throughput_mbps"), parsed_res.get("retransmits")
    except Exception:
        goodput_mbps, retransmits = None, None

    bloat_p50 = round(loaded_stats.p50_ms - idle_stats.p50_ms, 2) if (loaded_stats and idle_stats) else None
    bloat_p95 = round(loaded_stats.p95_ms - idle_stats.p50_ms, 2) if (loaded_stats and idle_stats) else None
    bloat_p99 = round(loaded_stats.p99_ms - idle_stats.p50_ms, 2) if (loaded_stats and idle_stats) else None
    grade = grade_bufferbloat(bloat_p95 if bloat_p95 is not None else 999.0)

    return BufferbloatResult(
        timestamp=ts,
        target=target,
        iperf_server=iperf_server,
        direction=direction,
        duration_s=float(duration),
        streams=streams,
        goodput_mbps=goodput_mbps,
        retransmits=retransmits,
        idle_stats=idle_stats,
        loaded_stats=loaded_stats,
        bloat_p50_ms=bloat_p50,
        bloat_p95_ms=bloat_p95,
        bloat_p99_ms=bloat_p99,
        grade=grade,
        metadata=meta,
    )


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FuturaMAX Bufferbloat & Latency Benchmark Suite")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    tc_parser = subparsers.add_parser("generate-tc", help="Generate Linux tc qdisc commands")
    tc_parser.add_argument("--qdisc", choices=["cake", "fq_codel", "pacing", "diffserv4-rules", "teardown"], default="cake")
    tc_parser.add_argument("--iface", default=DEFAULT_IFACE)
    tc_parser.add_argument("--bandwidth", default="50Mbit")
    tc_parser.add_argument("--diffserv", default="diffserv4")
    tc_parser.add_argument("--rtt", default="100ms")
    tc_parser.add_argument("--ingress", action="store_true")
    tc_parser.add_argument("--target", default="5ms")
    tc_parser.add_argument("--interval", default="100ms")

    bench_parser = subparsers.add_parser("bench", help="Run traffic saturation and bufferbloat measurement")
    bench_parser.add_argument("--target", default=DEFAULT_AP_WLINK)
    bench_parser.add_argument("--server", default=DEFAULT_AP_WLINK)
    bench_parser.add_argument("--duration", type=int, default=10)
    bench_parser.add_argument("--ping-interval", type=float, default=0.02)
    bench_parser.add_argument("--streams", type=int, default=1)
    bench_parser.add_argument("--profiles", nargs="+", choices=BufferbloatSuite.SUPPORTED_MODES, default=BufferbloatSuite.SUPPORTED_MODES)
    bench_parser.add_argument("--out-dir", type=str, default=None)
    bench_parser.add_argument("--dry-run", action="store_true")
    bench_parser.add_argument("--json", action="store_true")

    return parser


def main() -> None:
    parser = build_cli()
    args = parser.parse_args()

    if args.command == "generate-tc":
        if args.qdisc == "cake":
            cmds = generate_cake_commands(iface=args.iface, bandwidth=args.bandwidth, diffserv=args.diffserv, rtt=args.rtt, ingress=args.ingress)
        elif args.qdisc == "fq_codel":
            cmds = generate_fq_codel_commands(iface=args.iface, bandwidth=args.bandwidth, target=args.target, interval=args.interval, ingress=args.ingress)
        elif args.qdisc == "pacing":
            cmds = generate_pacing_commands(iface=args.iface, maxrate=args.bandwidth)
        elif args.qdisc == "diffserv4-rules":
            cmds = generate_diffserv4_iptables_rules(iface=args.iface)
        elif args.qdisc == "teardown":
            cmds = generate_teardown_commands(iface=args.iface)
        else:
            cmds = []

        print("#!/bin/bash\n# Generated by FuturaMAX Bufferbloat Suite")
        for cmd in cmds:
            print(cmd)

    elif args.command == "bench":
        suite = BufferbloatSuite(
            target_ip=args.target,
            ping_interval=args.ping_interval,
            duration=args.duration,
            streams=args.streams,
            out_dir=args.out_dir,
            dry_run=args.dry_run,
        )
        print(f"[*] Starting Bufferbloat Suite against {args.target} ({len(args.profiles)} profiles)...")
        receipt = suite.run_suite(args.profiles)
        out_path = suite.save_receipt(receipt)
        if args.json:
            print(json.dumps(receipt.to_dict(), indent=2))
        else:
            print(f"[+] Completed! Grade: {receipt.summary.get('bufferbloat_grade')}, Max p95: {receipt.summary.get('max_loaded_p95_ms')} ms")
            print(f"[+] Receipt saved: {out_path}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
