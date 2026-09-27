"""Telemetry collector and parser for ath10k debugfs and mac80211 statistics.

Summary: Parses ath10k htt_tx_stats, mac80211 AQL queues, and station dumps into
structured metrics. Tracks per-station airtime deficits, retries, chain imbalances,
and AQL saturation status.
Keywords: ath10k, debugfs, htt_tx_stats, AQL, station dump, queue depth, telemetry.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AQLQueueState:
    ac_name: str          # "VO", "VI", "BE", "BK"
    pending_airtime_us: int
    limit_airtime_us: int
    is_throttled: bool = False


@dataclass
class HttTxStatsSnapshot:
    tx_packets: int = 0
    tx_bytes: int = 0
    tx_completions: int = 0
    tx_retries: int = 0
    msdu_discards: int = 0
    queue_depth: int = 0
    retry_rate: float = 0.0
    discard_rate: float = 0.0


@dataclass
class StationLinkStats:
    mac_address: str
    inactive_time_ms: int = 0
    rx_bytes: int = 0
    tx_bytes: int = 0
    rx_packets: int = 0
    tx_packets: int = 0
    tx_retries: int = 0
    tx_failed: int = 0
    signal_dbm: int = -95
    chain0_signal_dbm: Optional[int] = None
    chain1_signal_dbm: Optional[int] = None
    chain_imbalance_db: float = 0.0
    tx_rate_mbps: float = 0.0
    tx_mcs: int = 0
    tx_bandwidth_mhz: int = 20
    tx_nss: int = 1
    tx_short_gi: bool = False
    rx_rate_mbps: float = 0.0
    expected_throughput_kbps: int = 0
    airtime_us: int = 0


@dataclass
class Ath10kTelemetryReport:
    timestamp: float
    htt_stats: HttTxStatsSnapshot
    aql_queues: Dict[str, AQLQueueState] = field(default_factory=dict)
    stations: Dict[str, StationLinkStats] = field(default_factory=dict)
    total_active_stations: int = 0
    aggregate_tx_rate_mbps: float = 0.0
    highest_chain_imbalance_db: float = 0.0
    is_any_queue_throttled: bool = False


class Ath10kDebugfsCollector:
    """Parses ath10k and mac80211 telemetry artifacts."""

    @classmethod
    def parse_htt_tx_stats(cls, text: str) -> HttTxStatsSnapshot:
        """Parses /sys/kernel/debug/ieee80211/phyX/ath10k/htt_tx_stats."""
        stats = HttTxStatsSnapshot()

        def extract_int(pattern: str, src: str) -> Optional[int]:
            m = re.search(pattern, src, re.IGNORECASE)
            return int(m.group(1)) if m else None

        pkts = extract_int(r"tx[_\s]+pkts?[:=\s]+(\d+)", text)
        if pkts is not None:
            stats.tx_packets = pkts

        b = extract_int(r"tx[_\s]+bytes?[:=\s]+(\d+)", text)
        if b is not None:
            stats.tx_bytes = b

        comps = extract_int(r"tx[_\s]+completions?[:=\s]+(\d+)", text)
        if comps is not None:
            stats.tx_completions = comps

        retries = extract_int(r"(?:tx[_\s]+)?retries[:=\s]+(\d+)", text)
        if retries is not None:
            stats.tx_retries = retries

        discards = extract_int(r"(?:msdu[_\s]+)?discards?[:=\s]+(\d+)", text)
        if discards is not None:
            stats.msdu_discards = discards

        qdepth = extract_int(r"queue[_\s]+depth[:=\s]+(\d+)", text)
        if qdepth is not None:
            stats.queue_depth = qdepth

        # Calculate instantaneous error/retry ratios
        total_tx = stats.tx_packets + stats.tx_retries
        if total_tx > 0:
            stats.retry_rate = round(stats.tx_retries / total_tx, 4)

        total_offered = stats.tx_packets + stats.msdu_discards
        if total_offered > 0:
            stats.discard_rate = round(stats.msdu_discards / total_offered, 4)

        return stats

    @classmethod
    def parse_aql_queues(cls, text: str) -> Dict[str, AQLQueueState]:
        """Parses mac80211 AQL queue status per AC."""
        # Expected formats:
        # AC_BE: pending: 3450 us, limit: 6000 us
        # or BE pending_airtime: 3450 limit: 6000
        queues: Dict[str, AQLQueueState] = {}
        pattern = re.compile(
            r"(?:AC_)?(VO|VI|BE|BK)[\s:]+.*?pending(?:_airtime)?[:=\s]+(\d+).*?limit(?:_airtime)?[:=\s]+(\d+)",
            re.IGNORECASE
        )
        for line in text.splitlines():
            m = pattern.search(line)
            if m:
                ac = m.group(1).upper()
                pending = int(m.group(2))
                limit = int(m.group(3))
                is_throttled = pending >= limit
                queues[ac] = AQLQueueState(
                    ac_name=ac,
                    pending_airtime_us=pending,
                    limit_airtime_us=limit,
                    is_throttled=is_throttled,
                )
        return queues

    @classmethod
    def parse_station_dump(cls, text: str) -> Dict[str, StationLinkStats]:
        """Parses output from 'iw dev wlanX station dump'."""
        stations: Dict[str, StationLinkStats] = {}
        current_mac: Optional[str] = None
        current_stats: Optional[StationLinkStats] = None

        station_blocks = re.split(r"^Station\s+([0-9a-fA-F:]{17})", text, flags=re.MULTILINE)
        if len(station_blocks) > 1:
            for i in range(1, len(station_blocks), 2):
                mac = station_blocks[i].lower()
                body = station_blocks[i+1]
                stats = StationLinkStats(mac_address=mac)

                # Parse signal
                m_sig = re.search(r"signal:\s+(-?\d+)\s+dBm", body)
                if m_sig:
                    stats.signal_dbm = int(m_sig.group(1))

                # Parse per-chain signal
                m_chains = re.search(r"signal avg:\s+\[(-?\d+),\s*(-?\d+)\]\s+dBm", body)
                if not m_chains:
                    m_chains = re.search(r"signal:\s+\[(-?\d+),\s*(-?\d+)\]\s+dBm", body)
                if m_chains:
                    c0 = int(m_chains.group(1))
                    c1 = int(m_chains.group(2))
                    stats.chain0_signal_dbm = c0
                    stats.chain1_signal_dbm = c1
                    stats.chain_imbalance_db = round(abs(c0 - c1), 1)

                # Parse packets and bytes
                m_rx_b = re.search(r"rx bytes:\s+(\d+)", body)
                if m_rx_b:
                    stats.rx_bytes = int(m_rx_b.group(1))

                m_tx_b = re.search(r"tx bytes:\s+(\d+)", body)
                if m_tx_b:
                    stats.tx_bytes = int(m_tx_b.group(1))

                m_rx_p = re.search(r"rx packets:\s+(\d+)", body)
                if m_rx_p:
                    stats.rx_packets = int(m_rx_p.group(1))

                m_tx_p = re.search(r"tx packets:\s+(\d+)", body)
                if m_tx_p:
                    stats.tx_packets = int(m_tx_p.group(1))

                m_ret = re.search(r"tx retries:\s+(\d+)", body)
                if m_ret:
                    stats.tx_retries = int(m_ret.group(1))

                m_fail = re.search(r"tx failed:\s+(\d+)", body)
                if m_fail:
                    stats.tx_failed = int(m_fail.group(1))

                # Parse tx bitrate e.g. "86.7 MBit/s, 40MHz, MCS 8, VHT-NSS 1, short GI"
                m_rate = re.search(r"tx bitrate:\s+([0-9\.]+)\s+MBit/s", body)
                if m_rate:
                    stats.tx_rate_mbps = float(m_rate.group(1))

                m_mcs = re.search(r"MCS\s+(\d+)", body)
                if m_mcs:
                    stats.tx_mcs = int(m_mcs.group(1))

                m_bw = re.search(r"(\d+)MHz", body)
                if m_bw:
                    stats.tx_bandwidth_mhz = int(m_bw.group(1))

                m_nss = re.search(r"VHT-NSS\s+(\d+)", body)
                if m_nss:
                    stats.tx_nss = int(m_nss.group(1))

                if "short GI" in body:
                    stats.tx_short_gi = True

                m_exp = re.search(r"expected throughput:\s+([0-9\.]+)\s*([kKmMgG])bps", body)
                if m_exp:
                    val = float(m_exp.group(1))
                    unit = m_exp.group(2).lower()
                    if unit == "m":
                        val *= 1000
                    stats.expected_throughput_kbps = int(val)

                stations[mac] = stats

        return stations

    @classmethod
    def build_telemetry_report(
        cls,
        timestamp: float,
        htt_stats_raw: str,
        aql_raw: str,
        station_dump_raw: str,
    ) -> Ath10kTelemetryReport:
        """Assembles a unified Ath10kTelemetryReport."""
        htt = cls.parse_htt_tx_stats(htt_stats_raw)
        aql = cls.parse_aql_queues(aql_raw)
        stations = cls.parse_station_dump(station_dump_raw)

        agg_tx_rate = sum(s.tx_rate_mbps for s in stations.values())
        max_imbalance = max((s.chain_imbalance_db for s in stations.values()), default=0.0)
        is_throttled = any(q.is_throttled for q in aql.values())

        return Ath10kTelemetryReport(
            timestamp=timestamp,
            htt_stats=htt,
            aql_queues=aql,
            stations=stations,
            total_active_stations=len(stations),
            aggregate_tx_rate_mbps=round(agg_tx_rate, 2),
            highest_chain_imbalance_db=max_imbalance,
            is_any_queue_throttled=is_throttled,
        )
