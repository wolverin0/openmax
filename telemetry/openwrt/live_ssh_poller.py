"""Resilient Live SSH Telemetry Poller for OpenWrt ath10k Radios.

Periodically queries OpenWrt / Linux 802.11ac hardware over SSH:
- `iw dev <iface> station dump` (station link metrics, MCS, NSS, retries, RSSI)
- ath10k htt_tx_stats and TXQ / AQL queue depths (/sys/kernel/debug/ieee80211/phyX/ath10k/htt_tx_stats)
- Baseband spectral scan relay (/sys/kernel/debug/ieee80211/phyX/ath10k/spectral_scan0)

Features:
- Structured parsing into StationTelemetry, SectorSummary, Ath10kTelemetryReport, and SpectralAnalysisReport
- Resilient connection management with exponential backoff on transient errors
- Support for injected mock SSH executors for hermetic offline testing
"""

from __future__ import annotations

import argparse
import datetime as dt
import enum
import json
import logging
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Ensure repo root is available in sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from telemetry.station_monitor import (
    StationMonitor,
    StationSectorSummary,
    StationTelemetry,
)
from telemetry.ath10k.debugfs_collector import (
    Ath10kDebugfsCollector,
    Ath10kTelemetryReport,
)
from telemetry.spectral_fft.parser import (
    SpectralParser,
    SpectralSample,
    SpectralAnalysisReport,
    analyze_spectral_sample,
)

logger = logging.getLogger("openwrt_poller")


class ConnectionState(str, enum.Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DEGRADED = "DEGRADED"
    ERROR = "ERROR"


@dataclass
class OpenWrtPollerConfig:
    """Configuration for OpenWrt SSH poller."""
    host: str = "10.99.0.1"
    port: int = 22
    username: str = "root"
    key_file: Optional[str] = None
    iface: str = "phy0-ap0"
    phy: str = "phy0"
    poll_interval_s: float = 2.0
    timeout_s: float = 5.0
    max_consecutive_errors: int = 3
    initial_backoff_s: float = 1.0
    max_backoff_s: float = 30.0
    enable_spectral: bool = True
    enable_txq: bool = True


@dataclass
class OpenWrtTelemetrySnapshot:
    """Unified telemetry snapshot from OpenWrt / ath10k polling cycle."""
    timestamp: float
    host: str
    iface: str
    connection_state: ConnectionState
    stations: Dict[str, StationTelemetry] = field(default_factory=dict)
    summary: Optional[StationSectorSummary] = None
    ath10k_report: Optional[Ath10kTelemetryReport] = None
    spectral_report: Optional[SpectralAnalysisReport] = None
    spectral_samples: List[SpectralSample] = field(default_factory=list)
    poll_duration_s: float = 0.0
    consecutive_errors: int = 0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "host": self.host,
            "iface": self.iface,
            "connection_state": self.connection_state.value,
            "stations": {k: v.to_dict() for k, v in self.stations.items()},
            "summary": self.summary.to_dict() if self.summary else None,
            "ath10k_report": asdict(self.ath10k_report) if self.ath10k_report else None,
            "spectral_report": self.spectral_report.to_dict() if self.spectral_report else None,
            "spectral_sample_count": len(self.spectral_samples),
            "poll_duration_s": round(self.poll_duration_s, 4),
            "consecutive_errors": self.consecutive_errors,
            "error_message": self.error_message,
        }


class OpenWrtLiveSSHPoller:
    """Manages continuous polling of OpenWrt ath10k radios over SSH."""

    def __init__(
        self,
        config: Optional[OpenWrtPollerConfig] = None,
        ssh_executor: Optional[Callable[[str, float], Tuple[str, str, int]]] = None,
    ):
        self.config = config or OpenWrtPollerConfig()
        self._custom_executor = ssh_executor
        self.state = ConnectionState.DISCONNECTED
        self.consecutive_errors = 0
        self.current_backoff = self.config.initial_backoff_s
        self.total_polls = 0
        self.successful_polls = 0
        self.last_poll_time: Optional[float] = None
        self._spectral_parser = SpectralParser()

    def _exec_ssh(self, command: str, timeout: Optional[float] = None) -> Tuple[str, str, int]:
        """Executes a command via SSH or through the injected executor."""
        t_out = timeout or self.config.timeout_s
        if self._custom_executor:
            return self._custom_executor(command, t_out)

        ssh_cmd = [
            "ssh",
            "-p", str(self.config.port),
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "BatchMode=yes",
            "-o", f"ConnectTimeout={int(t_out)}",
            "-o", "LogLevel=ERROR",
        ]
        if self.config.key_file:
            ssh_cmd.extend(["-i", self.config.key_file])

        target = f"{self.config.username}@{self.config.host}"
        ssh_cmd.extend([target, command])

        try:
            res = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=t_out + 2.0,
            )
            return res.stdout, res.stderr, res.returncode
        except subprocess.TimeoutExpired:
            return "", "SSH connection timed out", 124
        except Exception as e:
            return "", str(e), 1

    def poll_cycle(self) -> OpenWrtTelemetrySnapshot:
        """Executes a single polling iteration against the OpenWrt radio."""
        t_start = time.perf_counter()
        now = time.time()
        self.total_polls += 1
        self.last_poll_time = now

        phy = self.config.phy
        iface = self.config.iface
        debugfs_base = f"/sys/kernel/debug/ieee80211/{phy}"
        delimiter = "---FMX_DELIM---"

        # Compound SSH command to retrieve station dump, htt_stats, and AQL/TXQ stats
        cmd = f"iw dev {iface} station dump 2>/dev/null; echo '{delimiter}'; " \
              f"cat {debugfs_base}/ath10k/htt_tx_stats 2>/dev/null || cat {debugfs_base}/htt_tx_stats 2>/dev/null; echo '{delimiter}'; " \
              f"cat {debugfs_base}/txq 2>/dev/null || cat {debugfs_base}/aql_enable 2>/dev/null"

        if self.config.enable_spectral:
            # Query if any spectral scan file is buffered in /tmp or debugfs
            cmd += f"; echo '{delimiter}'; [ -f /tmp/spec.bin ] && head -c 2000 /tmp/spec.bin 2>/dev/null || true"

        stdout, stderr, rc = self._exec_ssh(cmd)
        duration = time.perf_counter() - t_start

        if rc != 0 or not stdout.strip():
            self.consecutive_errors += 1
            err_msg = stderr.strip() or f"SSH returned non-zero code {rc}"
            if self.consecutive_errors >= self.config.max_consecutive_errors:
                self.state = ConnectionState.ERROR
            else:
                self.state = ConnectionState.DEGRADED

            self.current_backoff = min(
                self.config.max_backoff_s,
                self.current_backoff * 1.5,
            )

            return OpenWrtTelemetrySnapshot(
                timestamp=now,
                host=self.config.host,
                iface=self.config.iface,
                connection_state=self.state,
                poll_duration_s=duration,
                consecutive_errors=self.consecutive_errors,
                error_message=err_msg,
            )

        # Connection healthy
        self.consecutive_errors = 0
        self.current_backoff = self.config.initial_backoff_s
        self.successful_polls += 1
        self.state = ConnectionState.CONNECTED

        sections = stdout.split(delimiter)
        iw_raw = sections[0].strip() if len(sections) > 0 else ""
        htt_raw = sections[1].strip() if len(sections) > 1 else ""
        txq_raw = sections[2].strip() if len(sections) > 2 else ""
        spectral_raw = sections[3] if len(sections) > 3 else ""

        # 1. Parse Stations via StationMonitor
        stations: Dict[str, StationTelemetry] = {}
        if iw_raw:
            try:
                stations = StationMonitor.parse_iw_station_dump(iw_raw)
            except Exception as e:
                logger.warning("Failed to parse iw station dump: %s", e)

        # 2. Sector Summary
        summary = StationMonitor.summarize(stations, source="openwrt")

        # 3. Ath10k Telemetry Report
        ath10k_report: Optional[Ath10kTelemetryReport] = None
        try:
            ath10k_report = Ath10kDebugfsCollector.build_telemetry_report(
                timestamp=now,
                htt_stats_raw=htt_raw,
                aql_raw=txq_raw,
                station_dump_raw=iw_raw,
            )
        except Exception as e:
            logger.debug("Could not build ath10k report: %s", e)

        # 4. Spectral Report
        spectral_report: Optional[SpectralAnalysisReport] = None
        spectral_samples: List[SpectralSample] = []
        if spectral_raw:
            try:
                # Convert string or bytes
                raw_bytes = spectral_raw.encode("latin-1") if isinstance(spectral_raw, str) else spectral_raw
                spectral_samples = list(self._spectral_parser.feed(raw_bytes))
                if spectral_samples:
                    spectral_report = analyze_spectral_sample(spectral_samples[-1])
            except Exception as e:
                logger.debug("Could not parse spectral binary data: %s", e)

        return OpenWrtTelemetrySnapshot(
            timestamp=now,
            host=self.config.host,
            iface=self.config.iface,
            connection_state=self.state,
            stations=stations,
            summary=summary,
            ath10k_report=ath10k_report,
            spectral_report=spectral_report,
            spectral_samples=spectral_samples,
            poll_duration_s=duration,
            consecutive_errors=0,
            error_message=None,
        )

    def run_loop(
        self,
        callback: Optional[Callable[[OpenWrtTelemetrySnapshot], None]] = None,
        max_iterations: Optional[int] = None,
    ) -> None:
        """Continuous execution loop with error handling and backoff."""
        iterations = 0
        try:
            while max_iterations is None or iterations < max_iterations:
                iterations += 1
                snapshot = self.poll_cycle()

                if callback:
                    callback(snapshot)

                if snapshot.connection_state in (ConnectionState.ERROR, ConnectionState.DEGRADED):
                    time.sleep(self.current_backoff)
                else:
                    time.sleep(self.config.poll_interval_s)

        except KeyboardInterrupt:
            logger.info("OpenWrt poller stopped by user.")


def main():
    parser = argparse.ArgumentParser(description="OpenWrt ath10k Resilient Live Telemetry Poller")
    parser.add_argument("--host", default="10.99.0.1", help="OpenWrt device IP (default: 10.99.0.1)")
    parser.add_argument("--user", default="root", help="SSH username (default: root)")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("--iface", default="phy0-ap0", help="Wireless interface (default: phy0-ap0)")
    parser.add_argument("--key", default=None, help="SSH private key path")
    parser.add_argument("--interval", type=float, default=2.0, help="Polling interval in seconds (default: 2.0)")
    parser.add_argument("--once", action="store_true", help="Perform a single poll and exit")
    parser.add_argument("--json", action="store_true", help="Output full JSON snapshot")

    args = parser.parse_args()

    cfg = OpenWrtPollerConfig(
        host=args.host,
        port=args.port,
        username=args.user,
        iface=args.iface,
        key_file=args.key,
        poll_interval_s=args.interval,
    )
    poller = OpenWrtLiveSSHPoller(cfg)

    if args.once:
        snap = poller.poll_cycle()
        if args.json:
            print(json.dumps(snap.to_dict(), indent=2))
        else:
            print(f"OpenWrt Snapshot [{snap.host} / {snap.iface}] - State: {snap.connection_state.value} ({snap.poll_duration_s*1000:.1f}ms)")
            if snap.error_message:
                print(f"  Error: {snap.error_message}")
            if snap.summary:
                print(f"  Stations: {snap.summary.station_count} | Avg SNR: {snap.summary.avg_snr_db} dB | Avg Rate: {snap.summary.avg_tx_rate_mbps} Mbps")
                for mac, st in snap.stations.items():
                    print(f"  -> {mac}: Signal={st.signal_dbm} dBm, Imbalance={st.chain_imbalance_db} dB, MCS={st.mcs}, NSS={st.nss}, Rate={st.tx_rate_mbps}M")
            if snap.ath10k_report:
                htt = snap.ath10k_report.htt_stats
                print(f"  HTT Stats: TxPkts={htt.tx_packets}, Retries={htt.tx_retries}, QDepth={htt.queue_depth}")
    else:
        def on_snap(s: OpenWrtTelemetrySnapshot):
            now = dt.datetime.fromtimestamp(s.timestamp).strftime("%H:%M:%S")
            print(f"[{now}] {s.host} | State={s.connection_state.value} | Stations={len(s.stations)} | Poll={s.poll_duration_s*1000:.1f}ms")

        poller.run_loop(callback=on_snap)


if __name__ == "__main__":
    main()
