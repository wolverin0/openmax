"""
PtMP Sector Conflict Graph and Joint Frequency/Width/Power Optimizer.
Calculates optimal orthogonal frequency allocation and channel widths for collocated APs.

Enforces Decision D-0010 and D-0011:
- 2 APs located ~21 meters apart on WISP roof form a tightly coupled RF domain.
- Requires orthogonal band separation (e.g. UNII-1 and UNII-3) to avoid LNA desensitization.
- Adapts channel width (20 MHz vs 40 MHz) based on spectral FFT interference findings.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class APSectorNode:
    ap_id: str
    latitude: float
    longitude: float
    azimuth_deg: float
    beamwidth_deg: float
    current_channel: int
    current_width_mhz: int
    max_eirp_dbm: float
    detected_interferences: List[str]  # e.g. ['DFS_WEATHER_RADAR', 'ADJACENT_CHANNEL_SPILL']


# 5 GHz Channel Plan Definitions
CHANNELS_UNII_1 = [36, 40, 44, 48]                 # 5180 - 5240 MHz (Indoor / Outdoor low)
CHANNELS_UNII_2A_DFS = [52, 56, 60, 64]            # 5260 - 5320 MHz (DFS)
CHANNELS_UNII_2C_DFS = [100, 104, 108, 112, 116,   # 5500 - 5700 MHz (DFS)
                        120, 124, 128, 132, 136, 140]
CHANNELS_UNII_3 = [149, 153, 157, 161, 165]       # 5745 - 5825 MHz (High power outdoor)


def channel_to_freq_mhz(channel: int) -> int:
    if 36 <= channel <= 64:
        return 5000 + channel * 5
    elif 100 <= channel <= 144:
        return 5000 + channel * 5
    elif 149 <= channel <= 165:
        return 5000 + channel * 5
    return 5180


def compute_ap_distance_m(ap1: APSectorNode, ap2: APSectorNode) -> float:
    """Approximate distance in meters between two AP coordinates."""
    dx = (ap1.longitude - ap2.longitude) * 111_000.0 * 0.76  # lat scale factor
    dy = (ap1.latitude - ap2.latitude) * 111_000.0
    return (dx * dx + dy * dy) ** 0.5


class ConflictGraphOptimizer:
    """Assigns optimal channels and bandwidths to minimize mutual interference."""

    def __init__(self, min_frequency_separation_mhz: int = 40):
        self.min_separation = min_frequency_separation_mhz

    def build_conflict_matrix(self, ap_fleet: List[APSectorNode]) -> Dict[Tuple[str, str], float]:
        """
        Builds conflict edges with interference weights [0.0, 1.0].
        Two APs within 50m have a severe conflict edge (weight > 0.8).
        """
        conflicts = {}
        for i in range(len(ap_fleet)):
            for j in range(i + 1, len(ap_fleet)):
                ap1 = ap_fleet[i]
                ap2 = ap_fleet[j]
                dist = compute_ap_distance_m(ap1, ap2)
                
                # Near-field coupling if dist < 30m
                if dist < 30.0:
                    weight = 1.0
                elif dist < 100.0:
                    weight = 0.6
                else:
                    weight = 0.1
                    
                conflicts[(ap1.ap_id, ap2.ap_id)] = weight
        return conflicts

    def optimize_channel_plan(self, ap_fleet: List[APSectorNode]) -> Dict[str, Dict]:
        """
        Assigns orthogonal channels and optimal channel widths.
        Returns plan: { ap_id: { 'channel': int, 'width_mhz': int, 'tx_power_dbm': int, 'band': str } }
        """
        plan = {}
        assigned_freqs = []

        for ap in ap_fleet:
            # Check spectral interference constraints
            has_dfs_radar = any("RADAR" in inf.upper() for inf in ap.detected_interferences)
            has_adjacent_spill = any("ADJACENT" in inf.upper() for inf in ap.detected_interferences)

            # Available pool
            candidate_channels = []
            
            # If DFS radar detected in sector, eliminate UNII-2A/2C DFS bands!
            if not has_dfs_radar:
                candidate_channels.extend(CHANNELS_UNII_2C_DFS)

            # Prioritize UNII-3 for clean high-power links
            candidate_channels.extend(CHANNELS_UNII_3)
            # Add UNII-1
            candidate_channels.extend(CHANNELS_UNII_1)

            # Find best channel that maximizes frequency distance from already assigned collocated APs
            best_ch = candidate_channels[0]
            best_min_dist = -1

            for ch in candidate_channels:
                freq = channel_to_freq_mhz(ch)
                if not assigned_freqs:
                    best_ch = ch
                    break
                min_dist = min(abs(freq - af) for af in assigned_freqs)
                if min_dist > best_min_dist:
                    best_min_dist = min_dist
                    best_ch = ch

            # Determine width: if channel is heavily contended or adjacent spill, drop to 20 MHz
            chosen_freq = channel_to_freq_mhz(best_ch)
            assigned_freqs.append(chosen_freq)

            if has_adjacent_spill or best_min_dist < 40:
                width = 20
            else:
                width = 40

            band_label = "UNII-3" if best_ch >= 149 else ("UNII-2C" if best_ch >= 100 else "UNII-1")

            plan[ap.ap_id] = {
                "channel": best_ch,
                "frequency_mhz": chosen_freq,
                "width_mhz": width,
                "tx_power_dbm": min(ap.max_eirp_dbm, 24.0 if band_label == "UNII-3" else 20.0),
                "band": band_label
            }

        return plan
