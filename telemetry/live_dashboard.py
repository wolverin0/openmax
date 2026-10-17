#!/usr/bin/env python3
"""FuturaMAX Live Terminal Telemetry Dashboard.

Combines station_monitor.py and spectral_fft/parser.py into a unified,
real-time terminal view of PtMP wireless sector health:
- Real-time station metrics (MAC, MCS, NSS, RSSI, SNR, Chain Imbalance, Retries, Airtime)
- RF baseband spectral analysis (Peak interference frequency, channel occupancy %, classifier status)
- Sector-wide airtime and health summaries with degraded station alerting.

Supports:
- Interactive live refresh mode (--interval 1.0)
- Single snapshot execution (--once)
- Offline mock mode (--mock) for hermetic testing and verification
- Structured JSON output (--json)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from telemetry.spectral_fft.parser import (
    AirOSSpectralParser,
    InterferenceClass,
    SpectralAnalysisReport,
    SpectralParser,
    SpectralSample,
    analyze_spectral_sample,
)
from telemetry.station_monitor import (
    StationMonitor,
    StationSectorSummary,
    StationTelemetry,
)


def _render_bar(percentage: float, width: int = 24) -> str:
    """Renders a simple ASCII percentage progress/occupancy bar."""
    clamped = max(0.0, min(100.0, percentage))
    filled_len = int(round((clamped / 100.0) * width))
    bar = "=" * filled_len + "-" * (width - filled_len)
    return f"[{bar}] {clamped:5.1f}%"


def generate_mock_dashboard_data() -> Tuple[Dict[str, StationTelemetry], SpectralAnalysisReport]:
    """Generates synthetic station and spectral telemetry for dry-run and test mode."""
    # Stations
    s1 = StationTelemetry(
        mac="00:27:22:a1:b2:c3",
        device_name="CPE-North-Silo",
        source="iw",
        signal_dbm=-62,
        noise_floor_dbm=-95,
        snr_db=33.0,
        chain0_signal_dbm=-63,
        chain1_signal_dbm=-64,
        chain_imbalance_db=1.0,
        tx_rate_mbps=144.4,
        rx_rate_mbps=130.0,
        mcs=6,
        nss=2,
        bandwidth_mhz=40,
        short_gi=True,
        tx_retries=18,
        tx_failed=0,
        airtime_dl_pct=14.5,
        airtime_ul_pct=6.2,
        airtime_total_pct=20.7,
        distance_meters=420,
    )

    s2 = StationTelemetry(
        mac="00:27:22:d4:e5:f6",
        device_name="CPE-South-Farm",
        source="iw",
        signal_dbm=-71,
        noise_floor_dbm=-95,
        snr_db=24.0,
        chain0_signal_dbm=-70,
        chain1_signal_dbm=-73,
        chain_imbalance_db=3.0,
        tx_rate_mbps=86.7,
        rx_rate_mbps=78.0,
        mcs=4,
        nss=2,
        bandwidth_mhz=40,
        short_gi=True,
        tx_retries=45,
        tx_failed=2,
        airtime_dl_pct=22.0,
        airtime_ul_pct=8.5,
        airtime_total_pct=30.5,
        distance_meters=1150,
    )

    s3 = StationTelemetry(
        mac="00:27:22:77:88:99",
        device_name="CPE-West-Ridge",
        source="iw",
        signal_dbm=-86,
        noise_floor_dbm=-95,
        snr_db=9.0,
        chain0_signal_dbm=-83,
        chain1_signal_dbm=-91,
        chain_imbalance_db=8.0,  # Severe imbalance
        tx_rate_mbps=13.5,
        rx_rate_mbps=13.5,
        mcs=1,
        nss=1,
        bandwidth_mhz=20,
        short_gi=False,
        tx_retries=240,
        tx_failed=38,
        airtime_dl_pct=32.0,
        airtime_ul_pct=11.0,
        airtime_total_pct=43.0,  # Airtime hog due to low MCS
        distance_meters=3200,
    )

    stations = {s1.mac: s1, s2.mac: s2, s3.mac: s3}

    # Spectral sample with radar spike around 5240 MHz
    bin_dbm = [-95.0] * 56
    bin_dbm[34] = -48.0  # Narrowband interference spike
    bin_dbm[35] = -52.0
    for i in range(12, 24):
        bin_dbm[i] = -82.0

    sample = SpectralSample(
        tlv_type=2,
        length=56 + 26,
        chan_width_mhz=20,
        relpwr_db=15,
        avgpwr_db=25,
        max_magnitude=210,
        max_index=6,
        rssi=-65,
        total_gain_db=40,
        base_pwr_db=15,
        freq1_mhz=5240,
        freq2_mhz=0,
        max_exp=1,
        noise_dbm=-95,
        tsf_us=int(time.time() * 1e6),
        bins=[int(abs(p)) for p in bin_dbm],
        bin_dbm=bin_dbm,
    )
    spectral_report = analyze_spectral_sample(sample)

    return stations, spectral_report


def render_dashboard(
    stations: Dict[str, StationTelemetry],
    spectral_report: Optional[SpectralAnalysisReport],
    header_info: Optional[Dict[str, str]] = None,
) -> str:
    """Renders the unified terminal dashboard into an ASCII formatted string."""
    now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hdr = header_info or {}
    target_ap = hdr.get("target_ap", "10.99.0.1 (fmx-ap1)")
    iface = hdr.get("iface", "phy0-ap0")

    summary: StationSectorSummary = StationMonitor.summarize(stations, source="unified")

    lines = []
    lines.append("=" * 86)
    lines.append(f"  FUTURAMAX TELEMETRY DASHBOARD  |  AP: {target_ap} [{iface}]  |  {now_str}")
    lines.append("=" * 86)

    # 1. Baseband Spectrum & Interference Section
    lines.append(" [RF SPECTRUM OCCUPANCY & INTERFERENCE CLASSIFIER]")
    if spectral_report:
        cf = spectral_report.center_freq_mhz
        bw = spectral_report.chan_width_mhz
        nf = spectral_report.noise_floor_dbm
        pk_f = spectral_report.peak_interference_freq_mhz
        pk_p = spectral_report.peak_power_dbm
        occ = spectral_report.channel_occupancy_pct
        cls_name = spectral_report.interference_class
        conf = spectral_report.confidence * 100.0

        bar = _render_bar(occ, width=28)
        lines.append(f"  Channel: {cf:.0f} MHz (BW {bw:.0f} MHz)  |  Noise Floor: {nf:.0f} dBm  |  Occupancy: {bar}")
        lines.append(f"  Peak Interference: {pk_f:.1f} MHz ({pk_p:.1f} dBm)  |  Status: {cls_name} ({conf:.0f}% conf)")
    else:
        lines.append("  Spectral scanner: Offline or waiting for sample feed...")

    lines.append("-" * 86)

    # 2. Associated Stations Table
    lines.append(" [ASSOCIATED CPE STATIONS]")
    lines.append(
        "  {:<17} {:<15} {:<7} {:<7} {:<6} {:<5} {:<5} {:<8} {:<7} {:<8}".format(
            "MAC", "Device Name", "Signal", "SNR", "Imbal", "MCS", "NSS", "Bitrate", "Retries", "Airtime"
        )
    )
    lines.append(
        "  {:<17} {:<15} {:<7} {:<7} {:<6} {:<5} {:<5} {:<8} {:<7} {:<8}".format(
            "-" * 17, "-" * 15, "-" * 7, "-" * 7, "-" * 6, "-" * 5, "-" * 5, "-" * 8, "-" * 7, "-" * 8
        )
    )

    if not stations:
        lines.append("  (No associated stations detected)")
    else:
        for mac, s in sorted(stations.items()):
            is_degraded = mac in summary.degraded_stations
            deg_marker = " !" if is_degraded else "  "

            sig_str = f"{s.signal_dbm} dBm"
            snr_str = f"{s.snr_db:.1f} dB"
            imb_str = f"{s.chain_imbalance_db:.1f} dB"
            mcs_str = str(s.mcs) if s.mcs is not None else "-"
            nss_str = str(s.nss) if s.nss is not None else "-"
            rate_str = f"{s.tx_rate_mbps:.1f}M"
            ret_str = str(s.tx_retries)
            at_str = f"{s.airtime_total_pct:.1f}%"

            name_cut = s.device_name[:15]
            lines.append(
                f"{deg_marker}{mac:<17} {name_cut:<15} {sig_str:<7} {snr_str:<7} {imb_str:<6} {mcs_str:<5} {nss_str:<5} {rate_str:<8} {ret_str:<7} {at_str:<8}"
            )

    lines.append("-" * 86)

    # 3. Sector Health Summary Section
    deg_count = len(summary.degraded_stations)
    status_tag = f"CRITICAL ({deg_count} degraded)" if deg_count > 0 else "HEALTHY"
    lines.append(" [SECTOR SUMMARY & AIRTIME DEMAND]")
    lines.append(
        f"  Active Stations: {summary.station_count}  |  Avg SNR: {summary.avg_snr_db:.1f} dB  |  Avg TX Rate: {summary.avg_tx_rate_mbps:.1f} Mbps"
    )
    lines.append(
        f"  Total Airtime: DL {summary.total_airtime_dl_pct:.1f}% / UL {summary.total_airtime_ul_pct:.1f}% (Sum: {summary.total_airtime_pct:.1f}%)  |  Total Retries: {summary.total_tx_retries}"
    )
    lines.append(f"  Sector Health: {status_tag}")
    if summary.degraded_stations:
        lines.append(f"  Degraded Stations: {', '.join(summary.degraded_stations)}")
    lines.append("=" * 86)

    return "\n".join(lines)


class LiveDashboard:
    """Dashboard runner polling live telemetry or rendering offline snapshots."""

    def __init__(
        self,
        target_ap: str = "10.99.0.1",
        iface: str = "phy0-ap0",
        source: str = "iw",
        interval: float = 1.0,
        mock: bool = False,
    ):
        self.target_ap = target_ap
        self.iface = iface
        self.source = source
        self.interval = interval
        self.mock = mock

    def poll_once(self) -> Tuple[Dict[str, StationTelemetry], Optional[SpectralAnalysisReport]]:
        """Collects one instant of station and spectral telemetry."""
        if self.mock:
            return generate_mock_dashboard_data()

        # Live poll
        stations: Dict[str, StationTelemetry] = {}
        try:
            stations = StationMonitor.poll_iw_ssh(self.target_ap, iface=self.iface)
        except Exception:
            pass

        # Try spectral sample if accessible
        spectral_report: Optional[SpectralAnalysisReport] = None
        # On physical hardware, could read /sys/kernel/debug/...
        return stations, spectral_report

    def render(self) -> str:
        """Collects telemetry and returns formatted dashboard string."""
        stations, spectral_report = self.poll_once()
        header = {"target_ap": self.target_ap, "iface": self.iface}
        return render_dashboard(stations, spectral_report, header)

    def run_loop(self) -> None:
        """Runs continuous interactive terminal dashboard loop."""
        try:
            while True:
                # Clear terminal screen
                print("\033[2J\033[H", end="")
                print(self.render())
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n[*] Live Dashboard terminated.")


def main():
    parser = argparse.ArgumentParser(description="FuturaMAX Live Terminal Telemetry Dashboard")
    parser.add_argument("--host", default="10.99.0.1", help="AP host IP (default: 10.99.0.1)")
    parser.add_argument("--iface", default="phy0-ap0", help="Wireless interface (default: phy0-ap0)")
    parser.add_argument("--interval", type=float, default=1.0, help="Refresh interval in seconds (default: 1.0)")
    parser.add_argument("--once", action="store_true", help="Print single snapshot and exit")
    parser.add_argument("--mock", action="store_true", help="Use synthetic mock telemetry")
    parser.add_argument("--json", action="store_true", help="Output JSON structured metrics")

    args = parser.parse_args()

    dashboard = LiveDashboard(
        target_ap=args.host,
        iface=args.iface,
        interval=args.interval,
        mock=args.mock,
    )

    if args.json:
        stations, spectral = dashboard.poll_once()
        summary = StationMonitor.summarize(stations, source="dashboard")
        out = {
            "timestamp": time.time(),
            "target": args.host,
            "iface": args.iface,
            "summary": summary.to_dict(),
            "spectral": spectral.to_dict() if spectral else None,
        }
        print(json.dumps(out, indent=2))
    elif args.once:
        print(dashboard.render())
    else:
        dashboard.run_loop()


if __name__ == "__main__":
    main()
