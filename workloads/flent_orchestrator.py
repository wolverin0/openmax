"""Network benchmark orchestrator for iperf3 and Flent / IRTT latency testing.

Summary: Orchestrates multi-station saturated throughput and loaded bufferbloat
measurements across 1 to 20 CPEs. Emits standardized RunSample inputs for the
RegressionGatekeeper and ReportGenerator.
Keywords: iperf3, flent, irtt, bufferbloat, loaded latency, Jain fairness, PtMP benchmark.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class CpeStreamResult:
    station_host: str
    throughput_mbps: float = 0.0
    retransmits: int = 0
    packet_loss_pct: float = 0.0
    rtt_p50_ms: float = 0.0
    rtt_p95_ms: float = 0.0
    rtt_p99_ms: float = 0.0
    total_packets_sent: int = 0


@dataclass
class FlentWorkloadConfig:
    server_host: str
    station_hosts: List[str]
    direction: str = "upload"  # "download", "upload", or "bidirectional"
    duration_seconds: float = 10.0
    streams_per_station: int = 1
    tcp_window_size: Optional[str] = None
    collect_irtt_latency: bool = True


@dataclass
class FlentWorkloadReport:
    config: FlentWorkloadConfig
    station_results: Dict[str, CpeStreamResult] = field(default_factory=dict)
    aggregate_goodput_mbps: float = 0.0
    jain_fairness_index: float = 1.0
    fleet_p50_latency_ms: float = 0.0
    fleet_p95_latency_ms: float = 0.0
    fleet_p99_latency_ms: float = 0.0
    total_retransmits: int = 0


class FlentWorkloadOrchestrator:
    """Orchestrates multi-CPE network benchmarks and parses output streams."""

    @classmethod
    def calculate_percentiles(cls, latencies_ms: List[float]) -> Dict[str, float]:
        """Calculates p50, p95, and p99 from a list of latencies in milliseconds."""
        if not latencies_ms:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        
        sorted_l = sorted(latencies_ms)
        n = len(sorted_l)

        def pct(p: float) -> float:
            idx = int(math.ceil(p * n)) - 1
            idx = max(0, min(n - 1, idx))
            return round(sorted_l[idx], 2)

        return {
            "p50": pct(0.50),
            "p95": pct(0.95),
            "p99": pct(0.99),
        }

    @classmethod
    def calculate_jain_fairness(cls, values: List[float]) -> float:
        """Calculates Jain's Fairness Index."""
        if not values or len(values) == 0:
            return 1.0
        n = len(values)
        sum_x = sum(values)
        sum_sq = sum(x * x for x in values)
        if sum_sq == 0:
            return 1.0
        return round((sum_x ** 2) / (n * sum_sq), 4)

    @classmethod
    def parse_iperf3_json(cls, raw_json: str) -> Dict[str, float]:
        """Parses iperf3 JSON output, extracting throughput and retransmits."""
        data = json.loads(raw_json)
        end = data.get("end", {})
        
        # Check receiver or sender stats
        sum_sent = end.get("sum_sent", {})
        sum_received = end.get("sum_received", {})

        # Use received bps if available (goodput)
        bits_per_sec = sum_received.get("bits_per_second", sum_sent.get("bits_per_second", 0.0))
        mbps = round(bits_per_sec / 1e6, 2)
        retransmits = sum_sent.get("retransmits", 0)

        return {"goodput_mbps": mbps, "retransmits": retransmits}

    @classmethod
    def parse_ping_latencies(cls, stdout: str) -> List[float]:
        """Parses round-trip times from standard ping output."""
        latencies: List[float] = []
        for line in stdout.splitlines():
            m = re.search(r"time[=<]\s*([0-9\.]+)\s*ms", line, re.IGNORECASE)
            if m:
                latencies.append(float(m.group(1)))
        return latencies

    def __init__(self, config: FlentWorkloadConfig):
        self.config = config

    def synthesize_report(
        self,
        station_iperf_data: Dict[str, Dict[str, float]],
        station_ping_data: Dict[str, List[float]],
    ) -> FlentWorkloadReport:
        """Compiles individual CPE benchmark outputs into a unified fleet report."""
        results: Dict[str, CpeStreamResult] = {}
        all_fleet_latencies: List[float] = []

        for host in self.config.station_hosts:
            iperf = station_iperf_data.get(host, {"goodput_mbps": 0.0, "retransmits": 0})
            pings = station_ping_data.get(host, [])
            all_fleet_latencies.extend(pings)

            pcts = self.calculate_percentiles(pings)

            res = CpeStreamResult(
                station_host=host,
                throughput_mbps=iperf.get("goodput_mbps", 0.0),
                retransmits=int(iperf.get("retransmits", 0)),
                rtt_p50_ms=pcts["p50"],
                rtt_p95_ms=pcts["p95"],
                rtt_p99_ms=pcts["p99"],
                total_packets_sent=len(pings),
            )
            results[host] = res

        goodputs = [r.throughput_mbps for r in results.values()]
        agg_goodput = round(sum(goodputs), 2)
        jain = self.calculate_jain_fairness(goodputs)
        fleet_pcts = self.calculate_percentiles(all_fleet_latencies)
        total_ret = sum(r.retransmits for r in results.values())

        return FlentWorkloadReport(
            config=self.config,
            station_results=results,
            aggregate_goodput_mbps=agg_goodput,
            jain_fairness_index=jain,
            fleet_p50_latency_ms=fleet_pcts["p50"],
            fleet_p95_latency_ms=fleet_pcts["p95"],
            fleet_p99_latency_ms=fleet_pcts["p99"],
            total_retransmits=total_ret,
        )
