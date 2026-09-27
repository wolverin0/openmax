"""Unit tests for telemetry.ath10k.debugfs_collector (Ath10kDebugfsCollector)."""

import unittest
from telemetry.ath10k.debugfs_collector import Ath10kDebugfsCollector


SAMPLE_HTT_TX_STATS = """
HTT TX Stats Snapshot:
  tx pkts: 45210
  tx bytes: 58921000
  tx completions: 45190
  tx retries: 2310
  msdu discards: 45
  queue depth: 12
"""

SAMPLE_AQL_QUEUES = """
mac80211 AQL status for phy0:
  AC_VO: pending: 150 us, limit: 2000 us
  AC_VI: pending: 800 us, limit: 4000 us
  AC_BE: pending: 6200 us, limit: 6000 us
  AC_BK: pending: 50 us, limit: 8000 us
"""

SAMPLE_STATION_DUMP = """
Station 24:a4:3c:aa:bb:cc (on wlan0)
	inactive time:	120 ms
	rx bytes:	12400500
	rx packets:	18200
	tx bytes:	45900200
	tx packets:	34100
	tx retries:	1200
	tx failed:	8
	signal:  	-64 dBm
	signal avg:	[-62, -67] dBm
	tx bitrate:	86.7 MBit/s 40MHz MCS 8 VHT-NSS 1 short GI
	rx bitrate:	72.2 MBit/s 40MHz MCS 7 VHT-NSS 1
	expected throughput:	65.4Mbps

Station f0:9f:c2:11:22:33 (on wlan0)
	inactive time:	40 ms
	rx bytes:	3100200
	rx packets:	4500
	tx bytes:	8900100
	tx packets:	7100
	tx retries:	320
	tx failed:	1
	signal:  	-58 dBm
	signal avg:	[-58, -59] dBm
	tx bitrate:	135.0 MBit/s 40MHz MCS 9 VHT-NSS 1 short GI
	rx bitrate:	120.0 MBit/s 40MHz MCS 8 VHT-NSS 1
	expected throughput:	98.1Mbps
"""


class TestAth10kDebugfsCollector(unittest.TestCase):
    def test_parse_htt_tx_stats(self):
        htt = Ath10kDebugfsCollector.parse_htt_tx_stats(SAMPLE_HTT_TX_STATS)
        self.assertEqual(htt.tx_packets, 45210)
        self.assertEqual(htt.tx_bytes, 58921000)
        self.assertEqual(htt.tx_completions, 45190)
        self.assertEqual(htt.tx_retries, 2310)
        self.assertEqual(htt.msdu_discards, 45)
        self.assertEqual(htt.queue_depth, 12)
        self.assertAlmostEqual(htt.retry_rate, 2310 / (45210 + 2310), places=4)
        self.assertAlmostEqual(htt.discard_rate, 45 / (45210 + 45), places=4)

    def test_parse_aql_queues(self):
        aql = Ath10kDebugfsCollector.parse_aql_queues(SAMPLE_AQL_QUEUES)
        self.assertIn("VO", aql)
        self.assertIn("BE", aql)
        self.assertEqual(aql["VO"].pending_airtime_us, 150)
        self.assertEqual(aql["VO"].limit_airtime_us, 2000)
        self.assertFalse(aql["VO"].is_throttled)
        
        # BE pending (6200) > limit (6000), should be throttled
        self.assertEqual(aql["BE"].pending_airtime_us, 6200)
        self.assertEqual(aql["BE"].limit_airtime_us, 6000)
        self.assertTrue(aql["BE"].is_throttled)

    def test_parse_station_dump(self):
        stations = Ath10kDebugfsCollector.parse_station_dump(SAMPLE_STATION_DUMP)
        self.assertEqual(len(stations), 2)
        sta1 = stations["24:a4:3c:aa:bb:cc"]
        self.assertEqual(sta1.signal_dbm, -64)
        self.assertEqual(sta1.chain0_signal_dbm, -62)
        self.assertEqual(sta1.chain1_signal_dbm, -67)
        self.assertEqual(sta1.chain_imbalance_db, 5.0)
        self.assertEqual(sta1.tx_mcs, 8)
        self.assertEqual(sta1.tx_bandwidth_mhz, 40)
        self.assertTrue(sta1.tx_short_gi)
        self.assertEqual(sta1.tx_rate_mbps, 86.7)
        self.assertEqual(sta1.expected_throughput_kbps, 65400)

        sta2 = stations["f0:9f:c2:11:22:33"]
        self.assertEqual(sta2.chain_imbalance_db, 1.0)
        self.assertEqual(sta2.tx_mcs, 9)

    def test_build_telemetry_report(self):
        report = Ath10kDebugfsCollector.build_telemetry_report(
            timestamp=1700000000.0,
            htt_stats_raw=SAMPLE_HTT_TX_STATS,
            aql_raw=SAMPLE_AQL_QUEUES,
            station_dump_raw=SAMPLE_STATION_DUMP,
        )
        self.assertEqual(report.total_active_stations, 2)
        self.assertAlmostEqual(report.aggregate_tx_rate_mbps, 86.7 + 135.0, places=2)
        self.assertEqual(report.highest_chain_imbalance_db, 5.0)
        self.assertTrue(report.is_any_queue_throttled)


if __name__ == "__main__":
    unittest.main()
