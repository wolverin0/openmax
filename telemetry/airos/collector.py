"""Telemetry collector and parser for Ubiquiti airOS 8.x airMAX AC sectors.

Summary: Ingests airOS /status.cgi and wstalist JSON payloads, parsing proprietary
airMAX TDMA polling metrics (quality, capacity, airtime allocation, station priority,
remote RSSI, CINR, and per-chain balance).
Keywords: airOS, telemetry, wstalist, airMAX TDMA, airtime, quality, capacity, CINR.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AirOSStationTelemetry:
    mac: str
    device_name: str
    signal_dbm: int
    chain0_signal_dbm: Optional[int] = None
    chain1_signal_dbm: Optional[int] = None
    chain_imbalance_db: float = 0.0
    remote_signal_dbm: Optional[int] = None
    remote_chain_imbalance_db: float = 0.0
    distance_meters: int = 0
    noise_floor_dbm: int = -95
    snr_db: float = 0.0
    tx_rate_mbps: float = 0.0
    rx_rate_mbps: float = 0.0
    tx_bytes: int = 0
    rx_bytes: int = 0
    airmax_priority: int = 2  # 0=Low, 1=Medium, 2=High, 3=None
    airmax_quality_pct: int = 0
    airmax_capacity_pct: int = 0
    airtime_dl_pct: float = 0.0
    airtime_ul_pct: float = 0.0


@dataclass
class AirOSSectorTelemetry:
    timestamp: float
    hostname: str
    frequency_mhz: int
    channel_width_mhz: int
    noise_floor_dbm: int
    airmax_overall_quality: int
    airmax_overall_capacity: int
    stations: Dict[str, AirOSStationTelemetry] = field(default_factory=dict)
    total_active_stations: int = 0
    total_airtime_dl_pct: float = 0.0
    total_airtime_ul_pct: float = 0.0
    severe_imbalance_stations: List[str] = field(default_factory=list)


class AirOSTelemetryCollector:
    """Parses and standardizes airOS telemetry feeds."""

    @classmethod
    def parse_wstalist(cls, raw_json: str) -> Dict[str, AirOSStationTelemetry]:
        """Parses output from 'wstalist' or '/api/v1/stations' JSON."""
        data = json.loads(raw_json)
        stations: Dict[str, AirOSStationTelemetry] = {}

        if not isinstance(data, list):
            data = data.get("stations", [])

        for item in data:
            mac = item.get("mac", "").lower()
            if not mac:
                continue

            name = item.get("name", item.get("hostname", "Unnamed-CPE"))
            sig = item.get("signal", -95)
            noise = item.get("noisefloor", -95)
            snr = round(float(sig - noise), 1)

            # Local RSSI chains
            rssi = item.get("rssi", [])
            c0, c1 = None, None
            imbalance = 0.0
            if isinstance(rssi, list) and len(rssi) >= 2:
                c0, c1 = int(rssi[0]), int(rssi[1])
                imbalance = round(abs(c0 - c1), 1)

            # Remote station RSSI
            remote = item.get("remote", {})
            rem_sig = remote.get("signal")
            rem_rssi = remote.get("rssi", [])
            rem_imbalance = 0.0
            if isinstance(rem_rssi, list) and len(rem_rssi) >= 2:
                rem_imbalance = round(abs(int(rem_rssi[0]) - int(rem_rssi[1])), 1)

            # AirMAX TDMA specific metrics
            airmax_data = item.get("airmax", {})
            priority = airmax_data.get("priority", 2)
            quality = airmax_data.get("quality", 0)
            capacity = airmax_data.get("capacity", 0)
            airtime = airmax_data.get("airtime", {})
            at_rx = float(airtime.get("rx", 0.0))
            at_tx = float(airtime.get("tx", 0.0))

            telemetry = AirOSStationTelemetry(
                mac=mac,
                device_name=name,
                signal_dbm=sig,
                chain0_signal_dbm=c0,
                chain1_signal_dbm=c1,
                chain_imbalance_db=imbalance,
                remote_signal_dbm=rem_sig,
                remote_chain_imbalance_db=rem_imbalance,
                distance_meters=item.get("distance", 0),
                noise_floor_dbm=noise,
                snr_db=snr,
                tx_rate_mbps=float(item.get("tx_rate", 0.0)),
                rx_rate_mbps=float(item.get("rx_rate", 0.0)),
                tx_bytes=int(item.get("tx_bytes", 0)),
                rx_bytes=int(item.get("rx_bytes", 0)),
                airmax_priority=priority,
                airmax_quality_pct=quality,
                airmax_capacity_pct=capacity,
                airtime_dl_pct=at_tx,
                airtime_ul_pct=at_rx,
            )
            stations[mac] = telemetry

        return stations

    @classmethod
    def parse_status_cgi(cls, raw_json: str) -> Dict[str, Any]:
        """Parses /status.cgi JSON dictionary."""
        return json.loads(raw_json)

    @classmethod
    def build_sector_telemetry(
        cls,
        timestamp: float,
        status_cgi_raw: str,
        wstalist_raw: str,
    ) -> AirOSSectorTelemetry:
        """Assembles unified sector telemetry from status.cgi and wstalist."""
        status = cls.parse_status_cgi(status_cgi_raw)
        stations = cls.parse_wstalist(wstalist_raw)

        host_info = status.get("host", {})
        wireless_info = status.get("wireless", {})
        airmax_info = status.get("airmax", {})

        hostname = host_info.get("hostname", "airMAX-AC")
        freq = int(wireless_info.get("frequency", 5180))
        chanbw = int(wireless_info.get("chanbw", 40))
        noise = int(wireless_info.get("noisef", -95))

        overall_qual = int(airmax_info.get("quality", 0))
        overall_cap = int(airmax_info.get("capacity", 0))

        total_dl = round(sum(s.airtime_dl_pct for s in stations.values()), 1)
        total_ul = round(sum(s.airtime_ul_pct for s in stations.values()), 1)

        # Flag stations with severe RF imbalance (> 3.5 dB)
        severe = [s.mac for s in stations.values() if s.chain_imbalance_db > 3.5 or s.remote_chain_imbalance_db > 3.5]

        return AirOSSectorTelemetry(
            timestamp=timestamp,
            hostname=hostname,
            frequency_mhz=freq,
            channel_width_mhz=chanbw,
            noise_floor_dbm=noise,
            airmax_overall_quality=overall_qual,
            airmax_overall_capacity=overall_cap,
            stations=stations,
            total_active_stations=len(stations),
            total_airtime_dl_pct=total_dl,
            total_airtime_ul_pct=total_ul,
            severe_imbalance_stations=severe,
        )
