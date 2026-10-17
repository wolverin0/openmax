"""Resilient Live SSH Telemetry Poller for Stock Ubiquiti airOS AC Radios.

Periodically queries airOS 8.x AP / CPE devices over SSH:
- wstalist and /status.cgi (per-station TDMA priority, quality, capacity, airtime, SNR, chains)
- /proc/net/wireless and interface statistics
- Spectral FFT output from ubntspecd / airview (when active)

Features:
- Structured parsing into StationTelemetry and StationSectorSummary models
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
from telemetry.spectral_fft.parser import (
    AirOSSpectralParser,
    SpectralAnalysisReport,
    SpectralSample,
    analyze_spectral_sample,
)

logger = logging.getLogger("airos_poller")


class ConnectionState(str, enum.Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DEGRADED = "DEGRADED"
    ERROR = "ERROR"


@dataclass
class AirOSPollerConfig:
    """Configuration for airOS SSH poller."""
    host: str = "192.168.1.2"
    port: int = 22
    username: str = "ubnt"
    key_file: Optional[str] = None
    poll_interval_s: float = 2.0
    timeout_s: float = 5.0
    max_consecutive_errors: int = 3
    initial_backoff_s: float = 1.0
    max_backoff_s: float = 30.0
    enable_spectral: bool = True
    wireless_iface: str = "ath0"


@dataclass
class WirelessInterfaceStats:
    """Metrics from /proc/net/wireless and /proc/net/dev."""
    interface: str
    status: int = 0
    link_quality: int = 0
    signal_level_dbm: int = -95
    noise_level_dbm: int = -95
    rx_bytes: int = 0
    tx_bytes: int = 0
    rx_packets: int = 0
    tx_packets: int = 0
    rx_errors: int = 0
    tx_errors: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AirOSTelemetrySnapshot:
    """Unified telemetry snapshot from a single polling cycle."""
    timestamp: float
    host: str
    connection_state: ConnectionState
    stations: Dict[str, StationTelemetry] = field(default_factory=dict)
    summary: Optional[StationSectorSummary] = None
    interface_stats: Dict[str, WirelessInterfaceStats] = field(default_factory=dict)
    spectral_report: Optional[SpectralAnalysisReport] = None
    poll_duration_s: float = 0.0
    consecutive_errors: int = 0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "host": self.host,
            "connection_state": self.connection_state.value,
            "stations": {k: v.to_dict() for k, v in self.stations.items()},
            "summary": self.summary.to_dict() if self.summary else None,
            "interface_stats": {k: v.to_dict() for k, v in self.interface_stats.items()},
            "spectral_report": self.spectral_report.to_dict() if self.spectral_report else None,
            "poll_duration_s": round(self.poll_duration_s, 4),
            "consecutive_errors": self.consecutive_errors,
            "error_message": self.error_message,
        }


class AirOSLiveSSHPoller:
    """Manages continuous polling of airOS AC hardware over SSH."""

    def __init__(
        self,
        config: Optional[AirOSPollerConfig] = None,
        ssh_executor: Optional[Callable[[str, float], Tuple[str, str, int]]] = None,
    ):
        self.config = config or AirOSPollerConfig()
        self._custom_executor = ssh_executor
        self.state = ConnectionState.DISCONNECTED
        self.consecutive_errors = 0
        self.current_backoff = self.config.initial_backoff_s
        self.total_polls = 0
        self.successful_polls = 0
        self.last_poll_time: Optional[float] = None

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

    @classmethod
    def parse_proc_net_wireless(cls, text: str) -> Dict[str, WirelessInterfaceStats]:
        """Parses Linux /proc/net/wireless into structured interface stats."""
        stats: Dict[str, WirelessInterfaceStats] = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or ":" not in line or "Inter-|" in line or "face |" in line:
                continue

            parts = line.split(":")
            if len(parts) < 2:
                continue

            iface = parts[0].strip()
            fields = parts[1].split()
            if len(fields) >= 4:
                try:
                    status = int(fields[0], 16) if "0x" in fields[0] else int(fields[0])
                    quality = int(float(fields[1].rstrip(".")))
                    signal = int(float(fields[2].rstrip(".")))
                    noise = int(float(fields[3].rstrip(".")))

                    stats[iface] = WirelessInterfaceStats(
                        interface=iface,
                        status=status,
                        link_quality=quality,
                        signal_level_dbm=signal,
                        noise_level_dbm=noise,
                    )
                except ValueError:
                    continue
        return stats

    @classmethod
    def parse_proc_net_dev(cls, text: str, existing_stats: Dict[str, WirelessInterfaceStats]) -> None:
        """Enriches existing interface stats with RX/TX bytes and error counters from /proc/net/dev."""
        for line in text.splitlines():
            line = line.strip()
            if ":" not in line:
                continue
            parts = line.split(":")
            iface = parts[0].strip()
            if iface in existing_stats:
                cols = parts[1].split()
                if len(cols) >= 16:
                    try:
                        st = existing_stats[iface]
                        st.rx_bytes = int(cols[0])
                        st.rx_packets = int(cols[1])
                        st.rx_errors = int(cols[2])
                        st.tx_bytes = int(cols[8])
                        st.tx_packets = int(cols[9])
                        st.tx_errors = int(cols[10])
                    except (ValueError, IndexError):
                        pass

    def poll_cycle(self) -> AirOSTelemetrySnapshot:
        """Executes a single polling iteration against the airOS radio."""
        t_start = time.perf_counter()
        now = time.time()
        self.total_polls += 1
        self.last_poll_time = now

        # Compound SSH command to minimize SSH handshake roundtrips:
        # 1. wstalist
        # 2. delimiter
        # 3. cat /proc/net/wireless
        # 4. delimiter
        # 5. cat /proc/net/dev
        # 6. delimiter
        # 7. check spectral if enabled
        delimiter = "---FMX_DELIM---"
        cmd = f"wstalist 2>/dev/null; echo '{delimiter}'; cat /proc/net/wireless 2>/dev/null; echo '{delimiter}'; cat /proc/net/dev 2>/dev/null"
        if self.config.enable_spectral:
            cmd += f"; echo '{delimiter}'; [ -f /tmp/spectral.json ] && cat /tmp/spectral.json 2>/dev/null || true"

        stdout, stderr, rc = self._exec_ssh(cmd)
        duration = time.perf_counter() - t_start

        if rc != 0 or not stdout.strip():
            self.consecutive_errors += 1
            err_msg = stderr.strip() or f"SSH returned non-zero code {rc}"
            if self.consecutive_errors >= self.config.max_consecutive_errors:
                self.state = ConnectionState.ERROR
            else:
                self.state = ConnectionState.DEGRADED

            # Exponential backoff update
            self.current_backoff = min(
                self.config.max_backoff_s,
                self.current_backoff * 1.5,
            )

            return AirOSTelemetrySnapshot(
                timestamp=now,
                host=self.config.host,
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
        wsta_raw = sections[0].strip() if len(sections) > 0 else ""
        wireless_raw = sections[1].strip() if len(sections) > 1 else ""
        net_dev_raw = sections[2].strip() if len(sections) > 2 else ""
        spectral_raw = sections[3].strip() if len(sections) > 3 else ""

        # 1. Parse Stations
        stations: Dict[str, StationTelemetry] = {}
        if wsta_raw:
            try:
                stations = StationMonitor.parse_airos_telemetry(wsta_raw)
            except Exception as e:
                logger.warning("Failed to parse wstalist: %s", e)

        # 2. Sector Summary
        summary = StationMonitor.summarize(stations, source="airos")

        # 3. Wireless & Net interface stats
        iface_stats = self.parse_proc_net_wireless(wireless_raw)
        if net_dev_raw and iface_stats:
            self.parse_proc_net_dev(net_dev_raw, iface_stats)

        # 4. Spectral Report (if present in /tmp/spectral.json)
        spectral_report: Optional[SpectralAnalysisReport] = None
        if spectral_raw:
            try:
                samples = AirOSSpectralParser.parse_json(spectral_raw)
                if samples:
                    spectral_report = analyze_spectral_sample(samples[0])
            except Exception as e:
                logger.debug("No active spectral FFT report available: %s", e)

        return AirOSTelemetrySnapshot(
            timestamp=now,
            host=self.config.host,
            connection_state=self.state,
            stations=stations,
            summary=summary,
            interface_stats=iface_stats,
            spectral_report=spectral_report,
            poll_duration_s=duration,
            consecutive_errors=0,
            error_message=None,
        )

    def run_loop(
        self,
        callback: Optional[Callable[[AirOSTelemetrySnapshot], None]] = None,
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
            logger.info("AirOS poller stopped by user.")


def main():
    parser = argparse.ArgumentParser(description="Ubiquiti airOS Resilient Live Telemetry Poller")
    parser.add_argument("--host", default="192.168.1.2", help="airOS device IP address (default: 192.168.1.2)")
    parser.add_argument("--user", default="ubnt", help="SSH username (default: ubnt)")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("--key", default=None, help="SSH private key path")
    parser.add_argument("--interval", type=float, default=2.0, help="Polling interval in seconds (default: 2.0)")
    parser.add_argument("--once", action="store_true", help="Perform a single poll and exit")
    parser.add_argument("--json", action="store_true", help="Output full JSON snapshot")

    args = parser.parse_args()

    cfg = AirOSPollerConfig(
        host=args.host,
        port=args.port,
        username=args.user,
        key_file=args.key,
        poll_interval_s=args.interval,
    )
    poller = AirOSLiveSSHPoller(cfg)

    if args.once:
        snap = poller.poll_cycle()
        if args.json:
            print(json.dumps(snap.to_dict(), indent=2))
        else:
            print(f"airOS Snapshot [{snap.host}] - State: {snap.connection_state.value} ({snap.poll_duration_s*1000:.1f}ms)")
            if snap.error_message:
                print(f"  Error: {snap.error_message}")
            if snap.summary:
                print(f"  Stations: {snap.summary.station_count} | Avg SNR: {snap.summary.avg_snr_db} dB | Airtime: {snap.summary.total_airtime_pct}%")
                for mac, st in snap.stations.items():
                    print(f"  -> {mac} ({st.device_name}): Signal={st.signal_dbm} dBm, Imbalance={st.chain_imbalance_db} dB, MCS={st.mcs}")
    else:
        def on_snap(s: AirOSTelemetrySnapshot):
            now = dt.datetime.fromtimestamp(s.timestamp).strftime("%H:%M:%S")
            print(f"[{now}] {s.host} | State={s.connection_state.value} | Stations={len(s.stations)} | Poll={s.poll_duration_s*1000:.1f}ms")

        poller.run_loop(callback=on_snap)


if __name__ == "__main__":
    main()
