"""Unified Station Telemetry Poller & Parser for Linux (iw) and Ubiquiti airOS.

Extracts and standardizes per-station link state across OpenWrt/Linux and airOS:
- MCS (Modulation and Coding Scheme)
- NSS (Number of Spatial Streams)
- TX/RX bitrate (Mbps)
- TX retries and failures
- Signal (dBm), noise floor (dBm), and SNR (dB)
- Per-chain imbalance (dB)
- DL/UL airtime utilization (%)
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class StationTelemetry:
    """Standardized telemetry record for an associated wireless station (CPE)."""
    mac: str
    device_name: str = "Unnamed-Station"
    source: str = "unknown"  # "iw" or "airos"
    signal_dbm: int = -95
    noise_floor_dbm: int = -95
    snr_db: float = 0.0
    chain0_signal_dbm: Optional[int] = None
    chain1_signal_dbm: Optional[int] = None
    chain_imbalance_db: float = 0.0
    tx_rate_mbps: float = 0.0
    rx_rate_mbps: float = 0.0
    mcs: Optional[int] = None
    nss: Optional[int] = None
    bandwidth_mhz: Optional[int] = None
    short_gi: bool = False
    tx_retries: int = 0
    tx_failed: int = 0
    rx_bytes: int = 0
    tx_bytes: int = 0
    rx_packets: int = 0
    tx_packets: int = 0
    airtime_dl_pct: float = 0.0
    airtime_ul_pct: float = 0.0
    airtime_total_pct: float = 0.0
    expected_throughput_kbps: Optional[int] = None
    distance_meters: Optional[int] = None
    airmax_priority: Optional[int] = None
    airmax_quality_pct: Optional[int] = None
    airmax_capacity_pct: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StationSectorSummary:
    """Summary of all stations connected to an AP sector."""
    timestamp: float
    source: str
    station_count: int
    stations: Dict[str, StationTelemetry] = field(default_factory=dict)
    avg_snr_db: float = 0.0
    avg_tx_rate_mbps: float = 0.0
    total_tx_retries: int = 0
    total_airtime_dl_pct: float = 0.0
    total_airtime_ul_pct: float = 0.0
    total_airtime_pct: float = 0.0
    degraded_stations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "source": self.source,
            "station_count": self.station_count,
            "avg_snr_db": self.avg_snr_db,
            "avg_tx_rate_mbps": self.avg_tx_rate_mbps,
            "total_tx_retries": self.total_tx_retries,
            "total_airtime_dl_pct": self.total_airtime_dl_pct,
            "total_airtime_ul_pct": self.total_airtime_ul_pct,
            "total_airtime_pct": self.total_airtime_pct,
            "degraded_stations": self.degraded_stations,
            "stations": {k: v.to_dict() for k, v in self.stations.items()},
        }


class StationMonitor:
    """Parses and polls station metrics from Linux `iw` and Ubiquiti airOS."""

    @classmethod
    def parse_iw_station_dump(
        cls,
        raw_text: str,
        noise_floor_dbm: int = -95,
        total_airtime_window_us: Optional[int] = None,
    ) -> Dict[str, StationTelemetry]:
        """Parses Linux `iw dev <iface> station dump` into StationTelemetry objects."""
        stations: Dict[str, StationTelemetry] = {}
        station_blocks = re.split(r"^Station\s+([0-9a-fA-F:]{17})", raw_text, flags=re.MULTILINE)

        if len(station_blocks) > 1:
            for i in range(1, len(station_blocks), 2):
                mac = station_blocks[i].lower()
                body = station_blocks[i + 1]

                st = StationTelemetry(
                    mac=mac,
                    source="iw",
                    noise_floor_dbm=noise_floor_dbm,
                )

                # Signal
                m_sig = re.search(r"signal:\s+(-?\d+)\s+dBm", body)
                if m_sig:
                    st.signal_dbm = int(m_sig.group(1))

                # Per-chain signal
                m_chains = re.search(r"signal (?:avg)?:\s+\[(-?\d+),\s*(-?\d+)\]\s+dBm", body)
                if m_chains:
                    c0, c1 = int(m_chains.group(1)), int(m_chains.group(2))
                    st.chain0_signal_dbm = c0
                    st.chain1_signal_dbm = c1
                    st.chain_imbalance_db = round(abs(c0 - c1), 1)

                st.snr_db = round(float(st.signal_dbm - noise_floor_dbm), 1)

                # Bytes and packets
                m_rx_b = re.search(r"rx bytes:\s+(\d+)", body)
                if m_rx_b:
                    st.rx_bytes = int(m_rx_b.group(1))

                m_tx_b = re.search(r"tx bytes:\s+(\d+)", body)
                if m_tx_b:
                    st.tx_bytes = int(m_tx_b.group(1))

                m_rx_p = re.search(r"rx packets:\s+(\d+)", body)
                if m_rx_p:
                    st.rx_packets = int(m_rx_p.group(1))

                m_tx_p = re.search(r"tx packets:\s+(\d+)", body)
                if m_tx_p:
                    st.tx_packets = int(m_tx_p.group(1))

                m_ret = re.search(r"tx retries:\s+(\d+)", body)
                if m_ret:
                    st.tx_retries = int(m_ret.group(1))

                m_fail = re.search(r"tx failed:\s+(\d+)", body)
                if m_fail:
                    st.tx_failed = int(m_fail.group(1))

                # TX bitrate line
                m_tx_rate = re.search(r"tx bitrate:\s+([0-9\.]+)\s+MBit/s(.*)", body)
                if m_tx_rate:
                    st.tx_rate_mbps = float(m_tx_rate.group(1))
                    tx_extra = m_tx_rate.group(2)

                    m_mcs = re.search(r"(?:VHT-MCS|MCS)\s+(\d+)", tx_extra)
                    if m_mcs:
                        st.mcs = int(m_mcs.group(1))

                    m_nss = re.search(r"VHT-NSS\s+(\d+)", tx_extra)
                    if m_nss:
                        st.nss = int(m_nss.group(1))
                    elif st.mcs is not None and st.mcs >= 8 and "VHT" not in tx_extra:
                        # 802.11n HT MCS 8-15 uses 2 spatial streams
                        st.nss = 2 if st.mcs >= 8 else 1

                    m_bw = re.search(r"(\d+)MHz", tx_extra)
                    if m_bw:
                        st.bandwidth_mhz = int(m_bw.group(1))

                    if "short GI" in tx_extra:
                        st.short_gi = True

                # RX bitrate line
                m_rx_rate = re.search(r"rx bitrate:\s+([0-9\.]+)\s+MBit/s", body)
                if m_rx_rate:
                    st.rx_rate_mbps = float(m_rx_rate.group(1))

                # Expected throughput
                m_exp = re.search(r"expected throughput:\s+([0-9\.]+)\s*([kKmMgG])bps", body)
                if m_exp:
                    val = float(m_exp.group(1))
                    unit = m_exp.group(2).lower()
                    if unit == "m":
                        val *= 1000.0
                    st.expected_throughput_kbps = int(val)

                # Airtime us (if available in mac80211 driver)
                m_air = re.search(r"airtime:\s+(\d+)\s*us", body)
                if m_air:
                    air_us = int(m_air.group(1))
                    if total_airtime_window_us and total_airtime_window_us > 0:
                        st.airtime_total_pct = round((air_us / total_airtime_window_us) * 100.0, 2)
                        st.airtime_dl_pct = st.airtime_total_pct

                stations[mac] = st

        return stations

    @classmethod
    def parse_airos_telemetry(
        cls,
        raw_data: Union[str, dict, list],
    ) -> Dict[str, StationTelemetry]:
        """Parses airOS wstalist JSON or status.cgi into StationTelemetry objects."""
        if isinstance(raw_data, str):
            data = json.loads(raw_data)
        else:
            data = raw_data

        if isinstance(data, dict):
            station_list = data.get("stations", [])
            # Also handle single station object
            if not station_list and "mac" in data:
                station_list = [data]
        elif isinstance(data, list):
            station_list = data
        else:
            station_list = []

        stations: Dict[str, StationTelemetry] = {}
        for item in station_list:
            if not isinstance(item, dict):
                continue

            mac = item.get("mac", "").lower()
            if not mac:
                continue

            name = item.get("name", item.get("hostname", "Unnamed-CPE"))
            sig = int(item.get("signal", -95))
            noise = int(item.get("noisefloor", -95))
            snr = round(float(sig - noise), 1)

            # Local chains
            rssi = item.get("rssi", [])
            c0, c1 = None, None
            imbalance = 0.0
            if isinstance(rssi, list) and len(rssi) >= 2:
                c0, c1 = int(rssi[0]), int(rssi[1])
                imbalance = round(abs(c0 - c1), 1)

            # AirMAX metrics
            airmax = item.get("airmax", {})
            priority = airmax.get("priority", 2)
            quality = airmax.get("quality", 0)
            capacity = airmax.get("capacity", 0)
            airtime = airmax.get("airtime", {})
            at_rx = float(airtime.get("rx", 0.0))
            at_tx = float(airtime.get("tx", 0.0))
            at_total = round(at_rx + at_tx, 1)

            tx_rate = float(item.get("tx_rate", 0.0))
            rx_rate = float(item.get("rx_rate", 0.0))

            # Infer MCS/NSS if provided in airOS format
            # airOS often reports tx_mcs or last_tx_rate
            mcs = item.get("tx_mcs")
            nss = item.get("tx_nss")
            if mcs is None and "tx_rate_desc" in item:
                m_desc = re.search(r"MCS\s*(\d+)", item["tx_rate_desc"])
                if m_desc:
                    mcs = int(m_desc.group(1))

            st = StationTelemetry(
                mac=mac,
                device_name=name,
                source="airos",
                signal_dbm=sig,
                noise_floor_dbm=noise,
                snr_db=snr,
                chain0_signal_dbm=c0,
                chain1_signal_dbm=c1,
                chain_imbalance_db=imbalance,
                tx_rate_mbps=tx_rate,
                rx_rate_mbps=rx_rate,
                mcs=mcs,
                nss=nss,
                tx_retries=int(item.get("tx_retries", item.get("retries", 0))),
                tx_failed=int(item.get("tx_failed", 0)),
                rx_bytes=int(item.get("rx_bytes", 0)),
                tx_bytes=int(item.get("tx_bytes", 0)),
                rx_packets=int(item.get("rx_packets", item.get("rx_pkts", 0))),
                tx_packets=int(item.get("tx_packets", item.get("tx_pkts", 0))),
                airtime_dl_pct=at_tx,
                airtime_ul_pct=at_rx,
                airtime_total_pct=at_total,
                distance_meters=int(item.get("distance", 0)),
                airmax_priority=priority,
                airmax_quality_pct=quality,
                airmax_capacity_pct=capacity,
            )
            stations[mac] = st

        return stations

    @classmethod
    def summarize(
        cls,
        stations: Dict[str, StationTelemetry],
        source: str = "unknown",
    ) -> StationSectorSummary:
        """Assembles sector summary with average SNR, rates, retries, and degraded stations."""
        count = len(stations)
        if count == 0:
            return StationSectorSummary(
                timestamp=time.time(),
                source=source,
                station_count=0,
            )

        snr_vals = [s.snr_db for s in stations.values()]
        tx_rates = [s.tx_rate_mbps for s in stations.values()]
        retries = sum(s.tx_retries for s in stations.values())
        total_dl = round(sum(s.airtime_dl_pct for s in stations.values()), 2)
        total_ul = round(sum(s.airtime_ul_pct for s in stations.values()), 2)
        total_at = round(sum(s.airtime_total_pct for s in stations.values()), 2)

        # Degraded station criteria:
        # 1. Chain imbalance > 3.5 dB
        # 2. SNR < 15 dB
        # 3. MCS <= 2 (if MCS is known)
        # 4. Failed transmissions > 20
        degraded: List[str] = []
        for s in stations.values():
            is_degraded = (
                s.chain_imbalance_db > 3.5
                or s.snr_db < 15.0
                or (s.mcs is not None and s.mcs <= 2)
                or s.tx_failed > 20
            )
            if is_degraded:
                degraded.append(s.mac)

        return StationSectorSummary(
            timestamp=time.time(),
            source=source,
            station_count=count,
            stations=stations,
            avg_snr_db=round(sum(snr_vals) / count, 1),
            avg_tx_rate_mbps=round(sum(tx_rates) / count, 1),
            total_tx_retries=retries,
            total_airtime_dl_pct=total_dl,
            total_airtime_ul_pct=total_ul,
            total_airtime_pct=total_at,
            degraded_stations=degraded,
        )

    @classmethod
    def poll_iw_ssh(
        cls,
        host: str,
        iface: str = "wlan0",
        ssh_user: str = "root",
        timeout: int = 10,
    ) -> Dict[str, StationTelemetry]:
        """Polls `iw dev <iface> station dump` over SSH."""
        cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "BatchMode=yes",
            "-o", f"ConnectTimeout={timeout}",
            f"{ssh_user}@{host}",
            f"iw dev {iface} station dump",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if res.returncode != 0:
            return {}
        return cls.parse_iw_station_dump(res.stdout)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="FuturaMAX Station Telemetry Poller")
    parser.add_argument("--host", help="AP/CPE Host IP address")
    parser.add_argument("--iface", default="phy0-ap0", help="Wireless interface (default: phy0-ap0)")
    parser.add_argument("--source", choices=["iw", "airos"], default="iw", help="Source type")
    parser.add_argument("--file", help="Parse from input text/JSON file instead of live SSH")
    parser.add_argument("--json", action="store_true", help="Print output in JSON format")

    args = parser.parse_args()

    if args.file:
        content = open(args.file, "r", encoding="utf-8").read()
        if args.source == "iw":
            stations = StationMonitor.parse_iw_station_dump(content)
        else:
            stations = StationMonitor.parse_airos_telemetry(content)
    elif args.host:
        stations = StationMonitor.poll_iw_ssh(args.host, iface=args.iface)
    else:
        print("[!] Specify either --host or --file")
        return

    summary = StationMonitor.summarize(stations, source=args.source)

    if args.json:
        print(json.dumps(summary.to_dict(), indent=2))
    else:
        print(f"Station Telemetry Summary ({summary.station_count} stations, source={summary.source}):")
        print(f"  Avg SNR: {summary.avg_snr_db} dB | Avg TX Rate: {summary.avg_tx_rate_mbps} Mbps | Total Retries: {summary.total_tx_retries}")
        print(f"  Total Airtime: DL {summary.total_airtime_dl_pct}% | UL {summary.total_airtime_ul_pct}%")
        print(f"  Degraded Stations: {summary.degraded_stations or 'None'}")
        for mac, s in summary.stations.items():
            print(f"  -> Station {mac} ({s.device_name}): Signal={s.signal_dbm} dBm, SNR={s.snr_db} dB, MCS={s.mcs}, NSS={s.nss}, TX={s.tx_rate_mbps} Mbps, Imbalance={s.chain_imbalance_db} dB")


if __name__ == "__main__":
    main()
