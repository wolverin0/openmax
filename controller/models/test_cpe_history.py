"""
Unit tests for stationary CPE historical profiler and link diagnostics.
"""

import unittest
from controller.models.cpe_history import CPEHistoryModel, CPEStationProfile


class TestCPEHistoryModel(unittest.TestCase):

    def setUp(self):
        self.model = CPEHistoryModel()

    def test_fspl_and_expected_rssi(self):
        """Test theoretical Line-of-Sight receive power calculation for a 1.5 km link."""
        profile = CPEStationProfile(
            cpe_id="CPE-01-Test",
            hardware_model="LiteBeam 5AC Gen2",
            distance_m=1500.0,
            azimuth_deg=270.0,
            service_plan_mbps=50.0,
            tx_power_dbm=20.0,
            antenna_gain_dbi=23.0,
            ap_antenna_gain_dbi=16.0,
            frequency_mhz=5500.0
        )
        self.model.register_station(profile)

        # FSPL for 1500m at 5.5 GHz is ~ 110.7 dB
        fspl = self.model.calculate_theoretical_fspl_db(1500.0, 5500.0)
        self.assertAlmostEqual(fspl, 110.7, delta=1.5)

        # Expected RSSI: 20 dBm + 23 dBi + 16 dBi - 110.7 dB = -51.7 dBm
        expected = self.model.get_expected_rssi_dbm("CPE-01-Test")
        self.assertAlmostEqual(expected, -51.7, delta=2.0)

    def test_misalignment_and_rate_ceiling_diagnosis(self):
        """If measured RSSI is 15 dB worse than expected, flag severe attenuation and cap rate at MCS0-5."""
        profile = CPEStationProfile(
            cpe_id="CPE-02-Degraded",
            hardware_model="NanoStation 5AC Loco",
            distance_m=1000.0,
            azimuth_deg=180.0,
            service_plan_mbps=25.0,
            rssi_ewma=-75.0,      # Expected is around -55 dBm
            noise_floor_dbm=-95.0 # SNR = 20 dB
        )
        self.model.register_station(profile)

        diag = self.model.diagnose_link_health("CPE-02-Degraded")
        self.assertEqual(diag["link_status"], "SEVERE_ATTENUATION_FOLIAGE_OR_MISALIGNMENT")
        # With 20 dB SNR, recommended rate is capped at MCS0-5 (cannot sustain 64/256 QAM)
        self.assertEqual(diag["recommended_rate_ceiling"], "MCS0-5")

    def test_telemetry_ewma_update(self):
        """Updating telemetry updates EWMA smoothly."""
        profile = CPEStationProfile(
            cpe_id="CPE-03-Live",
            hardware_model="LiteBeam 5AC Gen2",
            distance_m=800.0,
            azimuth_deg=90.0,
            service_plan_mbps=100.0,
            rssi_ewma=-60.0
        )
        self.model.register_station(profile)

        # Simulate 10 packet reports
        for _ in range(10):
            self.model.update_telemetry("CPE-03-Live", rssi=-62.0, noise_dbm=-96.0, per=0.01, retries=1, mcs_used=7)

        sta = self.model.stations["CPE-03-Live"]
        self.assertLess(sta.rssi_ewma, -60.0)
        self.assertEqual(sta.mcs_counts[7], 10)


if __name__ == "__main__":
    unittest.main()
