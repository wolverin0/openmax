"""
Unit tests for PtMP Conflict Graph Frequency Optimizer.
"""

import unittest
from controller.spectrum.conflict_graph import ConflictGraphOptimizer, APSectorNode


class TestConflictGraphOptimizer(unittest.TestCase):

    def setUp(self):
        self.optimizer = ConflictGraphOptimizer()

    def test_orthogonal_channel_assignment_for_collocated_aps(self):
        """2 APs located 21 meters apart must be assigned completely orthogonal frequency bands."""
        ap1 = APSectorNode(
            ap_id="AP-West-Sector",
            latitude=-34.6037,
            longitude=-58.3816,
            azimuth_deg=270.0,
            beamwidth_deg=120.0,
            current_channel=36,
            current_width_mhz=20,
            max_eirp_dbm=27.0,
            detected_interferences=[]
        )
        ap2 = APSectorNode(
            ap_id="AP-East-Sector",
            latitude=-34.6038,  # ~21 meters away
            longitude=-58.3818,
            azimuth_deg=90.0,
            beamwidth_deg=120.0,
            current_channel=36,
            current_width_mhz=20,
            max_eirp_dbm=27.0,
            detected_interferences=[]
        )

        plan = self.optimizer.optimize_channel_plan([ap1, ap2])
        self.assertEqual(len(plan), 2)
        
        freq1 = plan["AP-West-Sector"]["frequency_mhz"]
        freq2 = plan["AP-East-Sector"]["frequency_mhz"]
        freq_diff = abs(freq1 - freq2)
        
        # Must have at least 100 MHz separation (e.g. UNII-1 vs UNII-3)
        self.assertGreater(freq_diff, 80, f"Expected >80 MHz separation, got {freq_diff} MHz")

    def test_dfs_radar_evasion(self):
        """If DFS radar is detected, candidate channels in UNII-2 must be excluded."""
        ap_radar = APSectorNode(
            ap_id="AP-Radar-Zone",
            latitude=-34.6037,
            longitude=-58.3816,
            azimuth_deg=180.0,
            beamwidth_deg=120.0,
            current_channel=100,
            current_width_mhz=20,
            max_eirp_dbm=24.0,
            detected_interferences=["DFS_WEATHER_RADAR"]
        )

        plan = self.optimizer.optimize_channel_plan([ap_radar])
        assigned_band = plan["AP-Radar-Zone"]["band"]
        # Must NOT be in UNII-2C or UNII-2A
        self.assertNotIn("UNII-2", assigned_band)


if __name__ == "__main__":
    unittest.main()
