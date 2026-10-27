"""Network benchmark orchestrator for iperf3 and Flent / IRTT latency testing.

Summary: Orchestrates multi-station saturated throughput and loaded bufferbloat
measurements across 1 to 20 CPEs. Emits standardized RunSample inputs for the
RegressionGatekeeper and ReportGenerator.
Keywords: iperf3, flent, irtt, bufferbloat, loaded latency, Jain fairness, PtMP benchmark.
"""

from __future__ import annotations

import json
import hashlib
import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CpeStreamResult:
    station_host: str
    throughput_mbps: Optional[float] = None
    retransmits: Optional[int] = None
    packet_loss_pct: Optional[float] = None
    rtt_p50_ms: Optional[float] = None
    rtt_p95_ms: Optional[float] = None
    rtt_p99_ms: Optional[float] = None
    total_packets_sent: Optional[int] = None
    packets_requested: Optional[int] = None
    packets_received: Optional[int] = None
    duplicates: Optional[int] = None
    out_of_order: Optional[int] = None
    status: str = "INVALID"
    invalid_reasons: List[str] = field(default_factory=list)
    raw_sha256: Optional[str] = None
    session_id: Optional[str] = None
    observed_duration_seconds: Optional[float] = None


@dataclass
class FlentWorkloadConfig:
    server_host: str
    station_hosts: List[str]
    direction: str = "upload"  # "download", "upload", or "bidirectional"
    duration_seconds: float = 10.0
    streams_per_station: int = 1
    tcp_window_size: Optional[str] = None
    collect_irtt_latency: bool = True

    def __post_init__(self):
        if not self.station_hosts or len(set(self.station_hosts)) != len(self.station_hosts):
            raise ValueError("station_hosts must be nonempty and unique")
        if self.direction not in ("upload", "download", "bidirectional"):
            raise ValueError("unknown traffic direction")
        _finite(self.duration_seconds, "duration_seconds", positive=True)


@dataclass
class FlentWorkloadReport:
    config: FlentWorkloadConfig
    station_results: Dict[str, CpeStreamResult] = field(default_factory=dict)
    aggregate_goodput_mbps: Optional[float] = None
    jain_fairness_index: Optional[float] = None
    fleet_p50_latency_ms: Optional[float] = None
    fleet_p95_latency_ms: Optional[float] = None
    fleet_p99_latency_ms: Optional[float] = None
    total_retransmits: Optional[int] = None
    status: str = "INVALID"
    fairness_basis: str = "receiver goodputs across all configured stations"
    physical_acceptance: str = "UNKNOWN"


def _finite(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0 or (positive and value == 0):
        raise ValueError(f"{name} has invalid range")
    return value


def _count(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


class FlentWorkloadOrchestrator:
    """Orchestrates multi-CPE network benchmarks and parses output streams."""

    @classmethod
    def calculate_percentiles(cls, latencies_ms: List[float]) -> Dict[str, float]:
        """Calculates p50, p95, and p99 from a list of latencies in milliseconds."""
        if not latencies_ms:
            raise ValueError("No latency responses: percentiles are unavailable")
        for value in latencies_ms:
            _finite(value, "latency_ms")
        
        sorted_l = sorted(latencies_ms)
        n = len(sorted_l)

        def pct(p: float) -> float:
            idx = int(math.ceil(p * n)) - 1
            idx = max(0, min(n - 1, idx))
            return float(sorted_l[idx])

        return {
            "p50": pct(0.50),
            "p95": pct(0.95),
            "p99": pct(0.99),
        }

    @classmethod
    def calculate_jain_fairness(cls, values: List[float]) -> float:
        """Calculates Jain's Fairness Index."""
        if not values:
            raise ValueError("No stations: fairness is unavailable")
        for value in values:
            _finite(value, "receiver_goodput")
        n = len(values)
        sum_x = sum(values)
        sum_sq = sum(x * x for x in values)
        if sum_sq == 0:
            return None
        return round((sum_x ** 2) / (n * sum_sq), 4)

    @classmethod
    def parse_iperf3_json(cls, raw_json: str, *, expected_peer=None, expected_session=None) -> Dict[str, Any]:
        """Parses iperf3 JSON output, extracting throughput and retransmits."""
        data = json.loads(raw_json)
        if not isinstance(data, dict) or "error" in data:
            raise ValueError("Invalid iperf3 acquisition: error or nonobject response")
        end = data.get("end", {})
        if not isinstance(end,dict):raise ValueError('iperf3 end must be an object')
        
        # Check receiver or sender stats
        sum_sent = end.get("sum_sent", {})
        sum_received = end.get("sum_received", {})
        if not isinstance(sum_sent,dict):raise ValueError('iperf3 sum_sent must be an object')

        # Use received bps if available (goodput)
        if not isinstance(sum_received, dict) or "bits_per_second" not in sum_received:
            raise ValueError("Receiver sum_received is required; sum_sent is not received goodput")
        bits_per_sec = _finite(sum_received["bits_per_second"], "receiver bits_per_second")
        mbps = round(bits_per_sec / 1e6, 2)
        retransmits = sum_sent.get("retransmits")
        if retransmits is not None:
            _count(retransmits, "retransmits")
        sender_bps = sum_sent.get("bits_per_second")
        if sender_bps is not None:
            _finite(sender_bps, "sender bits_per_second")
        seconds, byte_count = sum_received.get("seconds"), sum_received.get("bytes")
        if seconds is not None:
            _finite(seconds, "receiver seconds", positive=True)
        if byte_count is not None:
            _count(byte_count, "receiver bytes")
        if seconds is not None and byte_count is not None and not math.isclose(
                bits_per_sec, byte_count * 8 / seconds, rel_tol=.02, abs_tol=1):
            raise ValueError("Receiver bytes/time and reported rate disagree")
        start = data.get("start", {})
        if not isinstance(start,dict) or not isinstance(start.get('connected',[]),list):
            raise ValueError('invalid iperf3 session/peer metadata')
        peers = {row.get("remote_host") for row in start.get("connected", []) if isinstance(row, dict)}
        session = start.get("cookie")
        if expected_peer is not None and expected_peer not in peers:
            raise ValueError("iperf3 peer mismatch")
        if expected_session is not None and session != expected_session:
            raise ValueError("iperf3 session mismatch")
        return {"goodput_mbps": mbps, "goodput_source": "sum_received", "retransmits": retransmits,
                "sender_mbps": sender_bps / 1e6 if sender_bps is not None else None,
                "received_bytes": byte_count, "duration_seconds": seconds,
                "raw_sha256": hashlib.sha256(raw_json.encode()).hexdigest(), "session_id": session,
                "status": "VALID_NUMERIC", "physical_acceptance": "UNKNOWN"}

    @classmethod
    def parse_ping_latencies(cls, stdout: str) -> List[float]:
        """Parses round-trip times from standard ping output."""
        latencies: List[float] = []
        for line in stdout.splitlines():
            m = re.search(r"time=\s*([0-9\.]+)\s*ms", line, re.IGNORECASE)
            if m and "DUP!" not in line:
                latencies.append(float(m.group(1)))
        return latencies

    @classmethod
    def parse_ping_output(cls, stdout: str) -> Dict[str, Any]:
        """Keep actual transmission counters; latency samples are not sent packets."""
        summary = re.search(r"(\d+) packets transmitted,\s*(\d+)\s+(?:packets )?received", stdout)
        if summary is None:
            raise ValueError("Missing ping transmission/receive summary")
        sent, received = map(int, summary.groups())
        duplicates = re.search(r"\+?(\d+) duplicates", stdout)
        return dict(sent=sent, received=received, requested=None,
                    duplicates=int(duplicates[1]) if duplicates else 0,
                    out_of_order=None, latencies_ms=cls.parse_ping_latencies(stdout))

    def __init__(self, config: FlentWorkloadConfig):
        self.config = config

    def synthesize_report(
        self,
        station_iperf_data: Dict[str, Dict[str, float]],
        station_ping_data: Dict[str, Any],
    ) -> FlentWorkloadReport:
        """Compiles individual CPE benchmark outputs into a unified fleet report."""
        results: Dict[str, CpeStreamResult] = {}
        all_fleet_latencies: List[float] = []

        for host in self.config.station_hosts:
            iperf = station_iperf_data.get(host, {})
            observation = station_ping_data.get(host, [])
            res = CpeStreamResult(station_host=host)
            try:
                if "error" in iperf:
                    raise ValueError("iperf error")
                if iperf.get('goodput_source')=='sum_sent':
                    raise ValueError('sender throughput is not receiver goodput')
                res.throughput_mbps = _finite(iperf.get("goodput_mbps"), "received goodput")
                if iperf.get("retransmits") is not None:
                    res.retransmits = _count(iperf['retransmits'], "retransmits")
                res.raw_sha256=iperf.get('raw_sha256');res.session_id=iperf.get('session_id')
                if iperf.get('duration_seconds') is not None:
                    observed=_finite(iperf['duration_seconds'],'observed duration',positive=True)
                    res.observed_duration_seconds=observed
                    if observed<.95*self.config.duration_seconds:
                        res.invalid_reasons.append('acquisition_duration_undercoverage')
            except (ValueError, TypeError):
                res.invalid_reasons.append("missing_or_invalid_receiver_goodput")
            pings = observation.get('latencies_ms', []) if isinstance(observation, dict) else observation
            try:
                pcts = self.calculate_percentiles(pings)
                res.rtt_p50_ms, res.rtt_p95_ms, res.rtt_p99_ms = pcts['p50'], pcts['p95'], pcts['p99']
                all_fleet_latencies.extend(pings)
            except (ValueError, TypeError):
                res.invalid_reasons.append("missing_or_invalid_latency_responses")
            try:
                if not isinstance(observation, dict):
                    raise ValueError("actual sent/receive counters unavailable")
                sent = _count(observation.get('sent'), 'sent')
                received = _count(observation.get('received'), 'received')
                if sent == 0 or received > sent:
                    raise ValueError("invalid ping counters")
                res.total_packets_sent, res.packets_received = sent, received
                res.packet_loss_pct = 100 * (sent - received) / sent
                for key, attribute in [('requested','packets_requested'),('duplicates','duplicates'),('out_of_order','out_of_order')]:
                    if observation.get(key) is not None:
                        setattr(res, attribute, _count(observation[key], key))
                if len(pings) != received or (res.packets_requested is not None and res.packets_requested < sent):
                    raise ValueError("latency/counter coverage mismatch")
            except (ValueError, TypeError):
                res.invalid_reasons.append("missing_or_invalid_ping_counter_coverage")
            res.status = 'INVALID' if res.invalid_reasons else 'VALID_NUMERIC'
            results[host] = res

        goodputs = [r.throughput_mbps for r in results.values()]
        all_goodput = all(value is not None for value in goodputs)
        agg_goodput = round(sum(goodputs), 2) if all_goodput else None
        jain = self.calculate_jain_fairness(goodputs) if all_goodput else None
        fleet_pcts = (self.calculate_percentiles(all_fleet_latencies)
                      if all(r.rtt_p99_ms is not None for r in results.values())
                      else dict(p50=None,p95=None,p99=None))
        total_ret = (sum(r.retransmits for r in results.values())
                     if all(r.retransmits is not None for r in results.values()) else None)

        return FlentWorkloadReport(
            config=self.config,
            station_results=results,
            aggregate_goodput_mbps=agg_goodput,
            jain_fairness_index=jain,
            fleet_p50_latency_ms=fleet_pcts["p50"],
            fleet_p95_latency_ms=fleet_pcts["p95"],
            fleet_p99_latency_ms=fleet_pcts["p99"],
            total_retransmits=total_ret,
            status='VALID_NUMERIC' if all(r.status == 'VALID_NUMERIC' for r in results.values()) else 'INVALID',
        )
