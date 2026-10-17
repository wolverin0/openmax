"""PtMP Sector Conflict Graph and Frequency Optimizer (controller.spectrum proxy).

Re-exports from controller.optimizer.conflict_graph for full backwards compatibility.
"""

from controller.optimizer.conflict_graph import (
    ALL_5GHZ_CHANNELS,
    APSectorNode,
    BandType,
    CHANNELS_UNII_1,
    CHANNELS_UNII_2A_DFS,
    CHANNELS_UNII_2C_DFS,
    CHANNELS_UNII_3,
    ConflictGraphOptimizer,
    FrequencyPlanResult,
    SectorAllocation,
    SectorNode,
    angle_diff_deg,
    channel_to_freq_mhz,
    compute_bearing_deg,
    freq_to_channel,
    get_band_for_channel,
    haversine_distance_m,
)

__all__ = [
    "ALL_5GHZ_CHANNELS",
    "APSectorNode",
    "BandType",
    "CHANNELS_UNII_1",
    "CHANNELS_UNII_2A_DFS",
    "CHANNELS_UNII_2C_DFS",
    "CHANNELS_UNII_3",
    "ConflictGraphOptimizer",
    "FrequencyPlanResult",
    "SectorAllocation",
    "SectorNode",
    "angle_diff_deg",
    "channel_to_freq_mhz",
    "compute_bearing_deg",
    "freq_to_channel",
    "get_band_for_channel",
    "haversine_distance_m",
]
