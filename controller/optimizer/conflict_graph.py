"""PtMP Sector Conflict Graph and Frequency Planner.

Optimizes frequency allocation and channel widths across collocated and adjacent
fixed-wireless PtMP sectors using graph coloring heuristics and RF propagation models.

Features:
1. SectorNode: Geographic position, azimuth, 3dB beamwidth, channel width, and EIRP.
2. Spatial Interference Weighting: Distance-based near-field coupling (<30m) and
   angular beam overlap based on antenna radiation patterns (main, side, and back lobes).
3. Spectral Overlap & Adjacent Channel Leakage: Frequency overlap calculation and
   ACLR spill penalties.
4. Constraint Satisfaction: Strict DFS weather radar avoidance and bandwidth limits.
5. Optimal Allocation Heuristic: DSATUR / greedy graph coloring to minimize total
   network interference cost.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class BandType(str, Enum):
    UNII_1 = "UNII-1"
    UNII_2A_DFS = "UNII-2A"
    UNII_2C_DFS = "UNII-2C"
    UNII_3 = "UNII-3"


# Standard 5 GHz channel plans
CHANNELS_UNII_1 = [36, 40, 44, 48]                 # 5180 - 5240 MHz
CHANNELS_UNII_2A_DFS = [52, 56, 60, 64]            # 5260 - 5320 MHz (DFS)
CHANNELS_UNII_2C_DFS = [                           # 5500 - 5720 MHz (DFS)
    100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144
]
CHANNELS_UNII_3 = [149, 153, 157, 161, 165]       # 5745 - 5825 MHz

ALL_5GHZ_CHANNELS = CHANNELS_UNII_1 + CHANNELS_UNII_2A_DFS + CHANNELS_UNII_2C_DFS + CHANNELS_UNII_3


def channel_to_freq_mhz(channel: int) -> int:
    """Convert 802.11 5 GHz channel number to center frequency in MHz."""
    if 36 <= channel <= 165:
        return 5000 + channel * 5
    return 5180


def freq_to_channel(freq_mhz: int) -> int:
    """Convert 5 GHz center frequency in MHz to 802.11 channel number."""
    if 5180 <= freq_mhz <= 5825:
        return (freq_mhz - 5000) // 5
    return 36


def get_band_for_channel(channel: int) -> BandType:
    """Classify 5 GHz channel into regulatory band."""
    if 36 <= channel <= 48:
        return BandType.UNII_1
    elif 52 <= channel <= 64:
        return BandType.UNII_2A_DFS
    elif 100 <= channel <= 144:
        return BandType.UNII_2C_DFS
    elif 149 <= channel <= 165:
        return BandType.UNII_3
    return BandType.UNII_1


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate geodesic distance between two coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def compute_bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate initial compass bearing from (lat1, lon1) to (lat2, lon2) in degrees [0, 360)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0


def angle_diff_deg(a: float, b: float) -> float:
    """Smallest difference between two angles in degrees [0, 180]."""
    diff = abs((a - b + 180.0) % 360.0 - 180.0)
    return diff


@dataclass
class SectorNode:
    """Graph node representing a wireless PtMP sector."""

    sector_id: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    azimuth_deg: float = 0.0
    beamwidth_deg: float = 90.0
    current_channel: int = 36
    current_width_mhz: int = 20
    max_eirp_dbm: float = 27.0
    detected_interferences: List[str] = field(default_factory=list)
    tilt_deg: float = 0.0
    ap_id: Optional[str] = None

    def __post_init__(self):
        if not self.sector_id and self.ap_id:
            self.sector_id = self.ap_id
        elif not self.ap_id and self.sector_id:
            self.ap_id = self.sector_id

    @property
    def current_freq_mhz(self) -> int:
        return channel_to_freq_mhz(self.current_channel)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Backwards compatibility alias for existing code
APSectorNode = SectorNode


@dataclass
class SectorAllocation:
    """Optimized frequency and width assignment for a sector."""

    sector_id: str
    channel: int
    frequency_mhz: int
    width_mhz: int
    tx_power_dbm: float
    band: str
    interference_score: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FrequencyPlanResult:
    """Result of global sector frequency optimization."""

    allocations: Dict[str, SectorAllocation]
    total_conflict_score_before: float
    total_conflict_score_after: float
    improvement_pct: float
    conflict_edges_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allocations": {k: v.to_dict() for k, v in self.allocations.items()},
            "total_conflict_score_before": round(self.total_conflict_score_before, 3),
            "total_conflict_score_after": round(self.total_conflict_score_after, 3),
            "improvement_pct": round(self.improvement_pct, 1),
            "conflict_edges_count": self.conflict_edges_count,
        }


class ConflictGraphOptimizer:
    """PtMP Sector Conflict Graph and Joint Frequency/Width Optimizer."""

    def __init__(
        self,
        min_frequency_separation_mhz: int = 40,
        near_field_distance_m: float = 30.0,
        far_field_distance_m: float = 5000.0,
    ):
        self.min_separation = min_frequency_separation_mhz
        self.near_field_distance = near_field_distance_m
        self.far_field_distance = far_field_distance_m

    def compute_antenna_gain_factor(self, off_axis_angle_deg: float, beamwidth_deg: float) -> float:
        """Calculate relative antenna power fraction based on off-axis angle.

        Models a 3-region antenna pattern:
        1. Main lobe (<= beamwidth/2): gain factor 1.0 (0 dB attenuation).
        2. Side lobe (beamwidth/2 to 90 deg): roll-off to -15 dB (factor ~0.18).
        3. Back lobe (> 90 deg): front-to-back ratio -25 dB (factor ~0.03).
        """
        half_bw = beamwidth_deg / 2.0
        if off_axis_angle_deg <= half_bw:
            return 1.0
        elif off_axis_angle_deg <= 90.0:
            # Linear decay from 1.0 to 0.18 (-15 dB)
            span = 90.0 - half_bw
            if span <= 0:
                return 0.18
            ratio = (off_axis_angle_deg - half_bw) / span
            return 1.0 - ratio * 0.82
        else:
            # Back lobe isolation factor (-25 dB)
            return 0.03

    def compute_spatial_coupling(self, s1: SectorNode, s2: SectorNode) -> float:
        """Compute spatial coupling factor between two sectors in [0.0, 1.0]."""
        dist = haversine_distance_m(s1.latitude, s1.longitude, s2.latitude, s2.longitude)

        # 1. Collocated / Near-field (< 30m, e.g. same tower or rooftop)
        if dist < self.near_field_distance:
            # Strong near-field coupling regardless of azimuth
            # Slight mitigation if back-to-back (> 120 deg azimuth difference)
            az_diff = angle_diff_deg(s1.azimuth_deg, s2.azimuth_deg)
            if az_diff >= 120.0:
                return 0.85
            return 1.0

        # 2. Distant sectors (> far field distance -> minimal interaction)
        if dist >= self.far_field_distance:
            return 0.0

        # 3. Intermediate distance: directional path loss
        # Distance decay factor: 1.0 at 30m down to 0.05 at 5km
        dist_factor = max(0.05, 1.0 - (dist / self.far_field_distance) ** 0.5)

        # Bearing between sectors
        bearing_12 = compute_bearing_deg(s1.latitude, s1.longitude, s2.latitude, s2.longitude)
        bearing_21 = (bearing_12 + 180.0) % 360.0

        off_axis_1 = angle_diff_deg(s1.azimuth_deg, bearing_12)
        off_axis_2 = angle_diff_deg(s2.azimuth_deg, bearing_21)

        gain1 = self.compute_antenna_gain_factor(off_axis_1, s1.beamwidth_deg)
        gain2 = self.compute_antenna_gain_factor(off_axis_2, s2.beamwidth_deg)

        directional_factor = gain1 * gain2
        return round(min(1.0, dist_factor * directional_factor), 4)

    def compute_spectral_conflict(
        self,
        freq1_mhz: int,
        width1_mhz: int,
        freq2_mhz: int,
        width2_mhz: int,
    ) -> float:
        """Compute spectral conflict factor between two channels in [0.0, 1.0]."""
        f1_low = freq1_mhz - width1_mhz / 2.0
        f1_high = freq1_mhz + width1_mhz / 2.0
        f2_low = freq2_mhz - width2_mhz / 2.0
        f2_high = freq2_mhz + width2_mhz / 2.0

        # Calculate overlap in MHz
        overlap = max(0.0, min(f1_high, f2_high) - max(f1_low, f2_low))
        min_width = min(width1_mhz, width2_mhz)

        if overlap > 0.0:
            # Direct co-channel or partial overlapping channel
            return round(overlap / min_width, 3)

        # Non-overlapping: check adjacent channel leakage (ACLR)
        center_diff = abs(freq1_mhz - freq2_mhz)
        adjacent_threshold = (width1_mhz + width2_mhz) / 2.0 + 10.0

        if center_diff <= adjacent_threshold:
            # Adjacent channel spill: sideband emissions cause desensitization
            return 0.35

        # Wideband LNA desensitization on 5 GHz radio frontends (< 100 MHz separation)
        if center_diff < 100.0:
            decay = (center_diff - adjacent_threshold) / max(1.0, 100.0 - adjacent_threshold)
            return round(0.35 * max(0.0, 1.0 - decay), 3)

        return 0.0

    def compute_sector_interference(
        self,
        s1: SectorNode,
        s2: SectorNode,
        freq1: Optional[int] = None,
        width1: Optional[int] = None,
        freq2: Optional[int] = None,
        width2: Optional[int] = None,
    ) -> float:
        """Compute total weighted interference between two sectors."""
        f1 = freq1 if freq1 is not None else s1.current_freq_mhz
        w1 = width1 if width1 is not None else s1.current_width_mhz
        f2 = freq2 if freq2 is not None else s2.current_freq_mhz
        w2 = width2 if width2 is not None else s2.current_width_mhz

        spatial = self.compute_spatial_coupling(s1, s2)
        if spatial <= 0.0:
            return 0.0

        spectral = self.compute_spectral_conflict(f1, w1, f2, w2)
        return round(spatial * spectral, 4)

    def build_conflict_matrix(self, fleet: List[SectorNode]) -> Dict[Tuple[str, str], float]:
        """Build conflict edges between all sector pairs."""
        conflicts: Dict[Tuple[str, str], float] = {}
        n = len(fleet)
        for i in range(n):
            for j in range(i + 1, n):
                s1 = fleet[i]
                s2 = fleet[j]
                weight = self.compute_sector_interference(s1, s2)
                conflicts[(s1.sector_id, s2.sector_id)] = weight
        return conflicts

    def get_candidate_channels(self, sector: SectorNode) -> List[int]:
        """Determine candidate 5 GHz channels respecting DFS radar detections."""
        has_dfs_radar = any("RADAR" in inf.upper() for inf in sector.detected_interferences)

        candidates: List[int] = []
        # UNII-3 is top priority for outdoor PtMP
        candidates.extend(CHANNELS_UNII_3)

        # UNII-1
        candidates.extend(CHANNELS_UNII_1)

        # Only include DFS channels if no active radar detected
        if not has_dfs_radar:
            candidates.extend(CHANNELS_UNII_2C_DFS)
            candidates.extend(CHANNELS_UNII_2A_DFS)

        return candidates

    def optimize_channel_plan(
        self,
        fleet: List[SectorNode],
        allow_width_adaptation: bool = True,
    ) -> Dict[str, Dict[str, Any]]:
        """Backwards compatible channel plan optimizer."""
        res = self.optimize_frequency_plan(fleet, allow_width_adaptation)
        plan: Dict[str, Dict[str, Any]] = {}
        for s_id, alloc in res.allocations.items():
            plan[s_id] = {
                "channel": alloc.channel,
                "frequency_mhz": alloc.frequency_mhz,
                "width_mhz": alloc.width_mhz,
                "tx_power_dbm": alloc.tx_power_dbm,
                "band": alloc.band,
                "interference_score": alloc.interference_score,
            }
        return plan

    def optimize_frequency_plan(
        self,
        fleet: List[SectorNode],
        allow_width_adaptation: bool = True,
    ) -> FrequencyPlanResult:
        """Assign optimal orthogonal channels and widths to minimize mutual interference.

        Uses DSATUR-inspired greedy graph coloring ordering sectors by total
        potential spatial interference.
        """
        if not fleet:
            return FrequencyPlanResult(
                allocations={},
                total_conflict_score_before=0.0,
                total_conflict_score_after=0.0,
                improvement_pct=0.0,
                conflict_edges_count=0,
            )

        # 1. Compute baseline conflict score before optimization
        score_before = 0.0
        n = len(fleet)
        for i in range(n):
            for j in range(i + 1, n):
                score_before += self.compute_sector_interference(fleet[i], fleet[j])

        # 2. Sort sectors by total potential spatial coupling (highest conflict first)
        spatial_potentials: List[Tuple[float, SectorNode]] = []
        for s in fleet:
            pot = sum(self.compute_spatial_coupling(s, other) for other in fleet if other != s)
            spatial_potentials.append((pot, s))

        # Sort descending by potential
        spatial_potentials.sort(key=lambda x: x[0], reverse=True)
        sorted_sectors = [s for _, s in spatial_potentials]

        # 3. Greedy Frequency & Width Allocation
        allocations: Dict[str, SectorAllocation] = {}

        for sector in sorted_sectors:
            candidates = self.get_candidate_channels(sector)
            has_spill = any("ADJACENT" in inf.upper() for inf in sector.detected_interferences)

            best_ch = candidates[0]
            best_width = 20 if (has_spill and allow_width_adaptation) else sector.current_width_mhz
            best_cost = float("inf")
            best_min_collocated_fdist = -1.0

            if has_spill and allow_width_adaptation:
                widths_to_try = [20]
            else:
                widths_to_try = [sector.current_width_mhz]
                if allow_width_adaptation and sector.current_width_mhz > 20:
                    widths_to_try.append(20)

            for w in widths_to_try:
                for ch in candidates:
                    freq = channel_to_freq_mhz(ch)
                    # Evaluate cost against already-allocated sectors
                    cost = 0.0
                    min_collocated_fdist = float("inf")
                    for prev_id, prev_alloc in allocations.items():
                        prev_sec = next(s for s in fleet if s.sector_id == prev_id)
                        cost += self.compute_sector_interference(
                            sector, prev_sec, freq, w, prev_alloc.frequency_mhz, prev_alloc.width_mhz
                        )
                        d = haversine_distance_m(sector.latitude, sector.longitude, prev_sec.latitude, prev_sec.longitude)
                        if d < 50.0:
                            f_dist = abs(freq - prev_alloc.frequency_mhz)
                            if f_dist < min_collocated_fdist:
                                min_collocated_fdist = f_dist

                    # Prefer 40 MHz if cost is equal or negligible
                    width_bonus = -0.05 if w == 40 else 0.0
                    evaluated_score = cost + width_bonus

                    is_better = False
                    if evaluated_score < best_cost - 1e-4:
                        is_better = True
                    elif abs(evaluated_score - best_cost) <= 1e-4:
                        if min_collocated_fdist > best_min_collocated_fdist:
                            is_better = True

                    if is_better:
                        best_cost = evaluated_score
                        best_ch = ch
                        best_width = w
                        best_min_collocated_fdist = min_collocated_fdist

            chosen_freq = channel_to_freq_mhz(best_ch)
            band = get_band_for_channel(best_ch).value
            max_power = 24.0 if band == "UNII-3" else 20.0
            tx_power = min(sector.max_eirp_dbm, max_power)

            allocations[sector.sector_id] = SectorAllocation(
                sector_id=sector.sector_id,
                channel=best_ch,
                frequency_mhz=chosen_freq,
                width_mhz=best_width,
                tx_power_dbm=tx_power,
                band=band,
                interference_score=round(max(0.0, best_cost), 4),
            )

        # 4. Compute conflict score after optimization
        score_after = 0.0
        edge_count = 0
        for i in range(n):
            for j in range(i + 1, n):
                s1 = fleet[i]
                s2 = fleet[j]
                a1 = allocations[s1.sector_id]
                a2 = allocations[s2.sector_id]
                edge_cost = self.compute_sector_interference(
                    s1, s2, a1.frequency_mhz, a1.width_mhz, a2.frequency_mhz, a2.width_mhz
                )
                if edge_cost > 0.0:
                    edge_count += 1
                score_after += edge_cost

        improvement = 0.0
        if score_before > 0:
            improvement = max(0.0, round(((score_before - score_after) / score_before) * 100.0, 1))

        return FrequencyPlanResult(
            allocations=allocations,
            total_conflict_score_before=round(score_before, 4),
            total_conflict_score_after=round(score_after, 4),
            improvement_pct=improvement,
            conflict_edges_count=edge_count,
        )
