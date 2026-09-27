"""
Persistent Stationary CPE Historical Profiler and Airtime Deficit Tracker.
Implements the core premise of AGENTS.md Section 1 and Section 8:
Stationary outdoor PtMP links have known geometry, surveyed distances, and learnable historical envelopes.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CPEStationProfile:
    cpe_id: str
    hardware_model: str
    distance_m: float
    azimuth_deg: float
    service_plan_mbps: float
    tx_power_dbm: float = 20.0
    antenna_gain_dbi: float = 23.0  # LiteBeam 5AC Gen2 dish gain
    ap_antenna_gain_dbi: float = 16.0  # LAP-120 sector horn gain
    frequency_mhz: float = 5500.0

    # Historical moving averages
    rssi_ewma: float = -65.0
    noise_floor_dbm: float = -95.0
    per_ewma: float = 0.02
    retry_ratio_ewma: float = 0.05
    mcs_counts: Dict[int, int] = field(default_factory=lambda: {i: 0 for i in range(10)})
    airtime_consumed_us: int = 0
    alpha: float = 0.95  # EWMA smoothing factor


class CPEHistoryModel:
    """Manages persistent historical profiles for outdoor fixed-wireless subscribers."""

    def __init__(self):
        self.stations: Dict[str, CPEStationProfile] = {}

    def register_station(self, profile: CPEStationProfile):
        self.stations[profile.cpe_id] = profile

    @staticmethod
    def calculate_theoretical_fspl_db(distance_m: float, freq_mhz: float = 5500.0) -> float:
        """
        Free Space Path Loss (FSPL) in dB:
        FSPL = 20*log10(d) + 20*log10(f_Hz) - 147.55
        """
        if distance_m <= 1.0:
            return 47.0
        f_hz = freq_mhz * 1e6
        return (20.0 * math.log10(distance_m)) + (20.0 * math.log10(f_hz)) - 147.55

    def get_expected_rssi_dbm(self, cpe_id: str) -> float:
        """
        Calculates theoretical Line-of-Sight receive power (dBm):
        RSSI_expected = P_tx + G_tx + G_rx - FSPL
        """
        sta = self.stations.get(cpe_id)
        if not sta:
            return -70.0
        fspl = self.calculate_theoretical_fspl_db(sta.distance_m, sta.frequency_mhz)
        eirp = sta.tx_power_dbm + sta.antenna_gain_dbi
        expected_rssi = eirp + sta.ap_antenna_gain_dbi - fspl
        return round(expected_rssi, 1)

    def diagnose_link_health(self, cpe_id: str) -> Dict[str, any]:
        """
        Compares measured RSSI against theoretical LOS model.
        Detects misalignment, Fresnel zone obstruction, or water in feedhorn.
        """
        sta = self.stations.get(cpe_id)
        if not sta:
            return {"error": "Station not found"}

        expected_rssi = self.get_expected_rssi_dbm(cpe_id)
        delta_db = sta.rssi_ewma - expected_rssi
        snr_db = sta.rssi_ewma - sta.noise_floor_dbm

        # Diagnosis logic
        if delta_db < -12.0:
            status = "SEVERE_ATTENUATION_FOLIAGE_OR_MISALIGNMENT"
        elif delta_db < -6.0:
            status = "SUBOPTIMAL_ALIGNMENT_OR_FRESNEL_ENCROACHMENT"
        elif delta_db > 6.0:
            status = "NEAR_FIELD_OR_REFLECTIVE_MULTIPATH"
        else:
            status = "HEALTHY_LOS_LINK"

        # Recommend rate ceiling based on physical SNR
        # 802.11ac 256-QAM requires > 29 dB SNR
        # 64-QAM requires > 22 dB SNR
        # 16-QAM requires > 16 dB SNR
        if snr_db >= 32.0:
            rec_arm = "MCS0-9"
        elif snr_db >= 25.0:
            rec_arm = "MCS0-7"
        elif snr_db >= 18.0:
            rec_arm = "MCS0-5"
        else:
            rec_arm = "MCS0-3"

        return {
            "cpe_id": cpe_id,
            "measured_rssi": round(sta.rssi_ewma, 1),
            "expected_rssi": expected_rssi,
            "delta_db": round(delta_db, 1),
            "snr_db": round(snr_db, 1),
            "link_status": status,
            "recommended_rate_ceiling": rec_arm
        }

    def update_telemetry(self, cpe_id: str, rssi: float, noise_dbm: float, per: float, retries: int, mcs_used: int):
        sta = self.stations.get(cpe_id)
        if not sta:
            return

        sta.rssi_ewma = (sta.alpha * sta.rssi_ewma) + ((1.0 - sta.alpha) * rssi)
        sta.noise_floor_dbm = (sta.alpha * sta.noise_floor_dbm) + ((1.0 - sta.alpha) * noise_dbm)
        sta.per_ewma = (sta.alpha * sta.per_ewma) + ((1.0 - sta.alpha) * per)
        
        if 0 <= mcs_used <= 9:
            sta.mcs_counts[mcs_used] += 1
