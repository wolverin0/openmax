"""Unit tests for PtMP Conflict Graph Frequency Planner.

Covers:
1. Geodesic distance, bearing, and off-axis angle calculations.
2. 3-region antenna radiation pattern modeling (main lobe, side lobes, back lobe).
3. Spatial coupling under near-field (<30m) vs far-field (>5km) conditions.
4. Spectral conflict, co-channel overlap, adjacent channel leakage (ACLR), and wideband LNA desensitization.
5. Strict DFS weather radar avoidance and candidate channel filtering.
6. Graph coloring / greedy frequency optimization across collocated and adjacent sectors.
7. Channel width adaptation (40 MHz -> 20 MHz) under adjacent channel spill.
"""

from __future__ import annotations

import unittest

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


class TestConflictGraphGeometryAndRF(unittest.TestCase):
    """Test geometric calculations and RF propagation models."""

    def test_channel_to_freq_and_band_conversion(self):
        """Verify frequency and regulatory band mapping across 5 GHz spectrum."""
        self.assertEqual(channel_to_freq_mhz(36), 5180)
        self.assertEqual(channel_to_freq_mhz(100), 5500)
        self.assertEqual(channel_to_freq_mhz(149), 5745)
        self.assertEqual(channel_to_freq_mhz(165), 5825)

        self.assertEqual(freq_to_channel(5180), 36)
        self.assertEqual(freq_to_channel(5500), 100)
        self.assertEqual(freq_to_channel(5745), 149)

        self.assertEqual(get_band_for_channel(36), BandType.UNII_1)
        self.assertEqual(get_band_for_channel(56), BandType.UNII_2A_DFS)
        self.assertEqual(get_band_for_channel(120), BandType.UNII_2C_DFS)
        self.assertEqual(get_band_for_channel(157), BandType.UNII_3)

    def test_haversine_distance(self):
        """Verify distance between known geographic points."""
        # Same point -> 0 meters
        self.assertEqual(haversine_distance_m(-34.6037, -58.3816, -34.6037, -58.3816), 0.0)

        # Collocated rooftop APs: ~21 meters apart
        dist = haversine_distance_m(-34.6037, -58.3816, -34.6038, -58.3818)
        self.assertAlmostEqual(dist, 21.4, delta=2.0)

    def test_bearing_and_angle_difference(self):
        """Verify compass bearing and angular deviation calculations."""
        # Directly north: lat increases, lon constant -> 0 deg
        bearing_n = compute_bearing_deg(0.0, 0.0, 1.0, 0.0)
        self.assertAlmostEqual(bearing_n, 0.0, delta=0.5)

        # Directly east: lon increases, lat constant -> 90 deg
        bearing_e = compute_bearing_deg(0.0, 0.0, 0.0, 1.0)
        self.assertAlmostEqual(bearing_e, 90.0, delta=0.5)

        # Angle difference across 0/360 boundary
        self.assertAlmostEqual(angle_diff_deg(10.0, 350.0), 20.0, delta=0.1)
        self.assertAlmostEqual(angle_diff_deg(0.0, 180.0), 180.0, delta=0.1)
        self.assertAlmostEqual(angle_diff_deg(45.0, 90.0), 45.0, delta=0.1)

    def test_antenna_gain_pattern(self):
        """Verify 3-region antenna radiation model."""
        optimizer = ConflictGraphOptimizer()
        bw = 90.0  # half_bw = 45.0

        # Within main lobe: off-axis <= 45 deg -> factor 1.0 (0 dB)
        self.assertEqual(optimizer.compute_antenna_gain_factor(0.0, bw), 1.0)
        self.assertEqual(optimizer.compute_antenna_gain_factor(30.0, bw), 1.0)
        self.assertEqual(optimizer.compute_antenna_gain_factor(45.0, bw), 1.0)

        # Side lobe region: between 45 and 90 deg -> roll-off to 0.18 (-15 dB)
        gain_60 = optimizer.compute_antenna_gain_factor(67.5, bw)
        self.assertLess(gain_60, 1.0)
        self.assertGreater(gain_60, 0.18)

        # Back lobe region: > 90 deg -> 0.03 (-25 dB front-to-back ratio)
        self.assertEqual(optimizer.compute_antenna_gain_factor(120.0, bw), 0.03)
        self.assertEqual(optimizer.compute_antenna_gain_factor(180.0, bw), 0.03)

    def test_spatial_coupling_near_and_far(self):
        """Near-field collocated APs have high coupling; distant APs have negligible coupling."""
        optimizer = ConflictGraphOptimizer()

        # Collocated rooftop APs (21m apart)
        ap1 = SectorNode("AP1", -34.6037, -58.3816, azimuth_deg=0.0)
        ap2 = SectorNode("AP2", -34.6038, -58.3818, azimuth_deg=180.0)
        coupling_near = optimizer.compute_spatial_coupling(ap1, ap2)
        self.assertGreaterEqual(coupling_near, 0.85)

        # Distant APs (6 km apart)
        ap_far = SectorNode("AP_Far", -34.6500, -58.3816, azimuth_deg=180.0)
        coupling_far = optimizer.compute_spatial_coupling(ap1, ap_far)
        self.assertEqual(coupling_far, 0.0)


class TestSpectralConflictAndInterference(unittest.TestCase):
    """Test spectral overlap, adjacent channel spill, and wideband desensitization."""

    def setUp(self):
        self.optimizer = ConflictGraphOptimizer()

    def test_cochannel_overlap(self):
        """Identical frequencies and channel widths produce full spectral conflict (1.0)."""
        # Both on 5500 MHz @ 20 MHz
        conflict = self.optimizer.compute_spectral_conflict(5500, 20, 5500, 20)
        self.assertEqual(conflict, 1.0)

    def test_partial_channel_overlap(self):
        """Overlapping 40 MHz and 20 MHz channels produce proportional overlap factor."""
        # 40 MHz on 5510 (5490 - 5530) vs 20 MHz on 5500 (5490 - 5510) -> 20 MHz overlap / 20 MHz = 1.0
        conflict = self.optimizer.compute_spectral_conflict(5510, 40, 5500, 20)
        self.assertEqual(conflict, 1.0)

        # 40 MHz on 5510 (5490 - 5530) vs 20 MHz on 5520 (5510 - 5530) -> 20 MHz overlap = 1.0
        conflict2 = self.optimizer.compute_spectral_conflict(5510, 40, 5520, 20)
        self.assertEqual(conflict2, 1.0)

    def test_adjacent_channel_leakage_spill(self):
        """Non-overlapping but adjacent channels produce 0.35 ACLR spill penalty."""
        # 5180 (Ch 36, 20MHz) and 5200 (Ch 40, 20MHz)
        # Center diff = 20 MHz <= (20+20)/2 + 10 = 30 MHz threshold
        conflict = self.optimizer.compute_spectral_conflict(5180, 20, 5200, 20)
        self.assertEqual(conflict, 0.35)

    def test_wideband_desensitization_and_orthogonal_bands(self):
        """Separation < 100 MHz has non-zero LNA desensitization; > 100 MHz is orthogonal."""
        # 5180 vs 5240: diff = 60 MHz (adjacent threshold 30, < 100 MHz)
        conflict_60 = self.optimizer.compute_spectral_conflict(5180, 20, 5240, 20)
        self.assertGreater(conflict_60, 0.0)
        self.assertLess(conflict_60, 0.35)

        # UNII-1 (5180) vs UNII-3 (5745): diff = 565 MHz >> 100 MHz -> completely orthogonal
        conflict_ortho = self.optimizer.compute_spectral_conflict(5180, 20, 5745, 20)
        self.assertEqual(conflict_ortho, 0.0)


class TestFrequencyPlanningAndOptimization(unittest.TestCase):
    """Test global conflict graph frequency allocation algorithms."""

    def setUp(self):
        self.optimizer = ConflictGraphOptimizer()

    def test_collocated_orthogonal_band_allocation(self):
        """Collocated APs on same rooftop must be assigned orthogonal bands (> 80 MHz separation)."""
        ap1 = SectorNode(
            sector_id="AP-West",
            latitude=-34.6037,
            longitude=-58.3816,
            azimuth_deg=270.0,
            beamwidth_deg=120.0,
            current_channel=36,
            current_width_mhz=20,
        )
        ap2 = SectorNode(
            sector_id="AP-East",
            latitude=-34.6038,  # ~21m away
            longitude=-58.3818,
            azimuth_deg=90.0,
            beamwidth_deg=120.0,
            current_channel=36,
            current_width_mhz=20,
        )

        res = self.optimizer.optimize_frequency_plan([ap1, ap2])
        self.assertEqual(len(res.allocations), 2)

        f1 = res.allocations["AP-West"].frequency_mhz
        f2 = res.allocations["AP-East"].frequency_mhz
        freq_diff = abs(f1 - f2)

        self.assertGreater(freq_diff, 80, f"Expected >80 MHz band separation, got {freq_diff} MHz")
        self.assertGreater(res.improvement_pct, 50.0)

    def test_dfs_radar_avoidance(self):
        """Candidate channels must strictly bypass UNII-2 DFS bands when radar is detected."""
        ap_radar = SectorNode(
            sector_id="AP-Tower-Radar",
            latitude=-34.6000,
            longitude=-58.3800,
            azimuth_deg=0.0,
            current_channel=100,
            detected_interferences=["DFS_WEATHER_RADAR"],
        )

        candidates = self.optimizer.get_candidate_channels(ap_radar)
        # Verify no UNII-2A or UNII-2C channels in candidate pool
        for ch in candidates:
            band = get_band_for_channel(ch)
            self.assertNotIn(band, (BandType.UNII_2A_DFS, BandType.UNII_2C_DFS))

        plan = self.optimizer.optimize_channel_plan([ap_radar])
        assigned_band = plan["AP-Tower-Radar"]["band"]
        self.assertNotIn("UNII-2", assigned_band)

    def test_channel_width_adaptation_under_adjacent_spill(self):
        """Sector with ADJACENT_CHANNEL_SPILL adapts channel width from 40 MHz to 20 MHz."""
        ap_spill = SectorNode(
            sector_id="AP-Crowded",
            latitude=-34.6000,
            longitude=-58.3800,
            azimuth_deg=0.0,
            current_channel=40,
            current_width_mhz=40,
            detected_interferences=["ADJACENT_CHANNEL_SPILL"],
        )

        plan = self.optimizer.optimize_channel_plan([ap_spill], allow_width_adaptation=True)
        self.assertEqual(plan["AP-Crowded"]["width_mhz"], 20)

    def test_empty_and_single_sector_fleet(self):
        """Handles empty or single-node fleets cleanly without exceptions."""
        empty_res = self.optimizer.optimize_frequency_plan([])
        self.assertEqual(len(empty_res.allocations), 0)
        self.assertEqual(empty_res.total_conflict_score_before, 0.0)

        single_node = SectorNode("AP-Single", -34.6, -58.3, 0.0)
        single_res = self.optimizer.optimize_frequency_plan([single_node])
        self.assertEqual(len(single_res.allocations), 1)
        self.assertEqual(single_res.total_conflict_score_after, 0.0)


if __name__ == "__main__":
    unittest.main()
