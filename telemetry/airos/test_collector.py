"""Unit tests for telemetry.airos.collector (AirOSTelemetryCollector)."""

import unittest
from telemetry.airos.collector import AirOSTelemetryCollector


SAMPLE_STATUS_CGI = """{
  "host": {
    "hostname": "LAP-GPS-Sector1",
    "uptime": 86400,
    "loadavg": [0.12, 0.05, 0.02]
  },
  "wireless": {
    "mode": "ap-ptmp-airmax-ac",
    "essid": "FuturaMAX-Production",
    "frequency": 5200,
    "chanbw": 40,
    "signal": -59,
    "noisef": -96,
    "txpower": 23,
    "count": 2
  },
  "airmax": {
    "enabled": 1,
    "quality": 94,
    "capacity": 89,
    "stations": 2
  }
}"""

SAMPLE_WSTALIST = """[
  {
    "mac": "24:a4:3c:10:20:30",
    "name": "CPE-Client-01",
    "signal": -58,
    "rssi": [-59, -57],
    "noisefloor": -96,
    "distance": 850,
    "tx_bytes": 120500100,
    "rx_bytes": 35002000,
    "tx_rate": 180.0,
    "rx_rate": 162.0,
    "remote": {
      "signal": -60,
      "rssi": [-60, -60],
      "noisefloor": -95,
      "tx_power": 19
    },
    "airmax": {
      "priority": 2,
      "quality": 96,
      "capacity": 91,
      "airtime": {
        "rx": 8.4,
        "tx": 31.6
      }
    }
  },
  {
    "mac": "f0:9f:c2:44:55:66",
    "name": "CPE-Client-02",
    "signal": -68,
    "rssi": [-65, -71],
    "noisefloor": -95,
    "distance": 2400,
    "tx_bytes": 45001000,
    "rx_bytes": 8200100,
    "tx_rate": 108.0,
    "rx_rate": 81.0,
    "remote": {
      "signal": -70,
      "rssi": [-67, -73],
      "noisefloor": -95,
      "tx_power": 22
    },
    "airmax": {
      "priority": 1,
      "quality": 82,
      "capacity": 71,
      "airtime": {
        "rx": 4.1,
        "tx": 15.2
      }
    }
  }
]"""


class TestAirOSTelemetryCollector(unittest.TestCase):
    def test_parse_wstalist(self):
        stations = AirOSTelemetryCollector.parse_wstalist(SAMPLE_WSTALIST)
        self.assertEqual(len(stations), 2)
        
        # Test station 1
        s1 = stations["24:a4:3c:10:20:30"]
        self.assertEqual(s1.device_name, "CPE-Client-01")
        self.assertEqual(s1.signal_dbm, -58)
        self.assertEqual(s1.snr_db, 38.0)
        self.assertEqual(s1.chain_imbalance_db, 2.0)
        self.assertEqual(s1.remote_chain_imbalance_db, 0.0)
        self.assertEqual(s1.distance_meters, 850)
        self.assertEqual(s1.airmax_quality_pct, 96)
        self.assertEqual(s1.airmax_capacity_pct, 91)
        self.assertEqual(s1.airtime_dl_pct, 31.6)
        self.assertEqual(s1.airtime_ul_pct, 8.4)

        # Test station 2 (severe chain imbalance: 6.0 dB)
        s2 = stations["f0:9f:c2:44:55:66"]
        self.assertEqual(s2.chain_imbalance_db, 6.0)
        self.assertEqual(s2.remote_chain_imbalance_db, 6.0)

    def test_build_sector_telemetry(self):
        sector = AirOSTelemetryCollector.build_sector_telemetry(
            timestamp=1700000000.0,
            status_cgi_raw=SAMPLE_STATUS_CGI,
            wstalist_raw=SAMPLE_WSTALIST,
        )
        self.assertEqual(sector.hostname, "LAP-GPS-Sector1")
        self.assertEqual(sector.frequency_mhz, 5200)
        self.assertEqual(sector.channel_width_mhz, 40)
        self.assertEqual(sector.airmax_overall_quality, 94)
        self.assertEqual(sector.airmax_overall_capacity, 89)
        self.assertEqual(sector.total_active_stations, 2)
        
        # Total airtimes
        self.assertAlmostEqual(sector.total_airtime_dl_pct, 31.6 + 15.2, places=1)
        self.assertAlmostEqual(sector.total_airtime_ul_pct, 8.4 + 4.1, places=1)

        # Severe imbalance station flagged
        self.assertIn("f0:9f:c2:44:55:66", sector.severe_imbalance_stations)
        self.assertNotIn("24:a4:3c:10:20:30", sector.severe_imbalance_stations)


if __name__ == "__main__":
    unittest.main()
