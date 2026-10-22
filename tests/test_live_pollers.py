"""Unit tests for telemetry/airos/live_ssh_poller.py and telemetry/openwrt/live_ssh_poller.py.

Tests:
- Successful polling cycles with mock SSH command responses
- Object conversion into StationTelemetry, SectorSummary, InterfaceStats, and Ath10kTelemetryReport
- Transient error handling, degradation states, and consecutive error escalation
- Reconnection logic and backoff reset upon recovery
- Loop termination via max_iterations and callback invocation
"""

import json
import struct
import unittest
from typing import Tuple

from telemetry.airos.live_ssh_poller import (
    AirOSLiveSSHPoller,
    AirOSPollerConfig,
    AirOSTelemetrySnapshot,
    ConnectionState,
    WirelessInterfaceStats,
)
from telemetry.openwrt.live_ssh_poller import (
    OpenWrtLiveSSHPoller,
    OpenWrtPollerConfig,
    OpenWrtTelemetrySnapshot,
)
from telemetry.spectral_fft.parser import (
    ATH_FFT_SAMPLE_ATH10K,
    HEADER_FORMAT,
    HEADER_SIZE,
)


# Mock data payloads
MOCK_WSTALIST = json.dumps([
    {
        "mac": "00:27:22:11:22:33",
        "name": "CPE-North",
        "signal": -62,
        "noisefloor": -95,
        "rssi": [-63, -65],
        "tx_rate": 144.4,
        "rx_rate": 130.0,
        "tx_mcs": 6,
        "tx_nss": 2,
        "tx_retries": 12,
        "tx_failed": 1,
        "distance": 500,
        "airmax": {
            "priority": 2,
            "quality": 92,
            "capacity": 85,
            "airtime": {
                "tx": 15.0,
                "rx": 8.0,
            }
        }
    }
])

MOCK_PROC_NET_WIRELESS = """
Inter-| sta-|   Quality        |   Discarded packets               | Missed | WE
 face | tus | link level noise |  nwid  crypt   frag  retry   misc | beacon | 22
  ath0: 0000   65.  -62.  -95.       0      0      0     12      0        0
"""

MOCK_PROC_NET_DEV = """
Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
  ath0: 1048576    1024    0    0    0     0          0         0  5242880    4096    1    0    0     0       0          0
"""

MOCK_AIROS_SPECTRAL_JSON = json.dumps({
    "samples": [
        {
            "center_freq": 5200,
            "chan_width": 20,
            "noise_floor": -95,
            "bins": [-95.0, -94.0, -50.0, -95.0]
        }
    ]
})

MOCK_IW_STATION_DUMP = """
Station 00:27:22:aa:bb:cc (on phy0-ap0)
\tinactive time:\t80 ms
\trx bytes:\t2097152
\trx packets:\t2048
\ttx bytes:\t8388608
\ttx packets:\t6144
\ttx retries:\t25
\ttx failed:\t3
\tsignal:\t-65 dBm
\tsignal avg:\t[-66, -68] dBm
\ttx bitrate:\t86.7 MBit/s, 40MHz, MCS 4, VHT-NSS 2, short GI
\trx bitrate:\t86.7 MBit/s, 40MHz, MCS 4, VHT-NSS 2
\tairtime:\t45000 us
"""

MOCK_HTT_TX_STATS = """
htt_tx_stats:
  tx pkts: 6144
  tx bytes: 8388608
  tx completions: 6100
  tx retries: 25
  msdu discards: 3
  queue depth: 4
"""

MOCK_TXQ_AQL = """
AC_BE pending: 1200 limit: 6000
AC_VI pending: 0 limit: 6000
"""


def build_mock_spectral_sample_bytes() -> bytes:
    """Build a valid binary ath10k Type 2 sample."""
    bin_count = 56
    tlv_type = ATH_FFT_SAMPLE_ATH10K
    payload_len = (HEADER_SIZE - 3) + bin_count
    header = struct.pack(
        HEADER_FORMAT,
        tlv_type, payload_len, 20, 10, 20,
        150, 0, -65, 40, 15,
        5200, 0, 1, -95, 123456789
    )
    bins = bytes([35 for _ in range(bin_count)])
    return header + bins


class TestAirOSLiveSSHPoller(unittest.TestCase):
    """Test suite for airOS live SSH poller."""

    def test_parse_proc_net_wireless_and_dev(self):
        stats = AirOSLiveSSHPoller.parse_proc_net_wireless(MOCK_PROC_NET_WIRELESS)
        self.assertIn("ath0", stats)
        ath0 = stats["ath0"]
        self.assertEqual(ath0.link_quality, 65)
        self.assertEqual(ath0.signal_level_dbm, -62)
        self.assertEqual(ath0.noise_level_dbm, -95)

        # Enrich with dev stats
        AirOSLiveSSHPoller.parse_proc_net_dev(MOCK_PROC_NET_DEV, stats)
        self.assertEqual(ath0.rx_bytes, 1048576)
        self.assertEqual(ath0.tx_bytes, 5242880)
        self.assertEqual(ath0.tx_errors, 1)

    def test_poll_cycle_success(self):
        delimiter = "---FMX_DELIM---"
        compound_output = f"{MOCK_WSTALIST}\n{delimiter}\n{MOCK_PROC_NET_WIRELESS}\n{delimiter}\n{MOCK_PROC_NET_DEV}\n{delimiter}\n{MOCK_AIROS_SPECTRAL_JSON}"

        def mock_executor(cmd: str, timeout: float) -> Tuple[str, str, int]:
            return compound_output, "", 0

        cfg = AirOSPollerConfig(host="192.168.1.2")
        poller = AirOSLiveSSHPoller(config=cfg, ssh_executor=mock_executor)

        snapshot = poller.poll_cycle()

        self.assertEqual(snapshot.connection_state, ConnectionState.CONNECTED)
        self.assertEqual(snapshot.consecutive_errors, 0)
        self.assertEqual(len(snapshot.stations), 1)

        # Verify parsed station metrics
        st = snapshot.stations["00:27:22:11:22:33"]
        self.assertEqual(st.device_name, "CPE-North")
        self.assertEqual(st.signal_dbm, -62)
        self.assertEqual(st.snr_db, 33.0)
        self.assertEqual(st.chain_imbalance_db, 2.0)
        self.assertEqual(st.mcs, 6)
        self.assertEqual(st.nss, 2)
        self.assertEqual(st.airtime_dl_pct, 15.0)
        self.assertEqual(st.airtime_ul_pct, 8.0)

        # Sector summary
        self.assertIsNotNone(snapshot.summary)
        self.assertEqual(snapshot.summary.station_count, 1)
        self.assertEqual(snapshot.summary.total_tx_retries, 12)

        # Spectral report
        self.assertIsNotNone(snapshot.spectral_report)
        self.assertEqual(snapshot.spectral_report.center_freq_mhz, 5200.0)

    def test_error_handling_and_recovery(self):
        fail_count = 0

        def flaky_executor(cmd: str, timeout: float) -> Tuple[str, str, int]:
            nonlocal fail_count
            if fail_count < 3:
                fail_count += 1
                return "", "Connection refused", 255
            else:
                delimiter = "---FMX_DELIM---"
                return f"{MOCK_WSTALIST}\n{delimiter}\n{MOCK_PROC_NET_WIRELESS}\n{delimiter}\n{MOCK_PROC_NET_DEV}", "", 0

        cfg = AirOSPollerConfig(host="192.168.1.2", max_consecutive_errors=2)
        poller = AirOSLiveSSHPoller(config=cfg, ssh_executor=flaky_executor)

        # Poll 1: First failure -> DEGRADED
        s1 = poller.poll_cycle()
        self.assertEqual(s1.connection_state, ConnectionState.DEGRADED)
        self.assertEqual(s1.consecutive_errors, 1)
        self.assertGreater(poller.current_backoff, cfg.initial_backoff_s)

        # Poll 2: Second failure -> reached max_consecutive_errors -> ERROR
        s2 = poller.poll_cycle()
        self.assertEqual(s2.connection_state, ConnectionState.ERROR)
        self.assertEqual(s2.consecutive_errors, 2)

        # Poll 3: Third failure -> ERROR
        s3 = poller.poll_cycle()
        self.assertEqual(s3.connection_state, ConnectionState.ERROR)
        self.assertEqual(s3.consecutive_errors, 3)

        # Poll 4: Success -> Recover to CONNECTED, reset counters
        s4 = poller.poll_cycle()
        self.assertEqual(s4.connection_state, ConnectionState.CONNECTED)
        self.assertEqual(s4.consecutive_errors, 0)
        self.assertEqual(poller.current_backoff, cfg.initial_backoff_s)
        self.assertEqual(len(s4.stations), 1)

    def test_run_loop_with_callback(self):
        snapshots = []
        delimiter = "---FMX_DELIM---"
        mock_out = f"{MOCK_WSTALIST}\n{delimiter}\n{MOCK_PROC_NET_WIRELESS}\n{delimiter}\n{MOCK_PROC_NET_DEV}"

        poller = AirOSLiveSSHPoller(
            config=AirOSPollerConfig(poll_interval_s=0.01),
            ssh_executor=lambda cmd, t: (mock_out, "", 0),
        )

        poller.run_loop(callback=lambda s: snapshots.append(s), max_iterations=2)
        self.assertEqual(len(snapshots), 2)
        self.assertEqual(poller.total_polls, 2)
        self.assertEqual(poller.successful_polls, 2)


class TestOpenWrtLiveSSHPoller(unittest.TestCase):
    """Test suite for OpenWrt ath10k live SSH poller."""

    def test_poll_cycle_success(self):
        delimiter = "---FMX_DELIM---"
        raw_spec_str = build_mock_spectral_sample_bytes().decode("latin-1")
        compound_output = f"{MOCK_IW_STATION_DUMP}\n{delimiter}\n{MOCK_HTT_TX_STATS}\n{delimiter}\n{MOCK_TXQ_AQL}\n{delimiter}\n{raw_spec_str}"

        def mock_executor(cmd: str, timeout: float) -> Tuple[str, str, int]:
            return compound_output, "", 0

        cfg = OpenWrtPollerConfig(host="10.99.0.1", iface="phy0-ap0")
        poller = OpenWrtLiveSSHPoller(config=cfg, ssh_executor=mock_executor)

        snapshot = poller.poll_cycle()

        self.assertEqual(snapshot.connection_state, ConnectionState.CONNECTED)
        self.assertEqual(snapshot.consecutive_errors, 0)
        self.assertEqual(len(snapshot.stations), 1)

        # Station checks
        st = snapshot.stations["00:27:22:aa:bb:cc"]
        self.assertEqual(st.signal_dbm, -65)
        self.assertEqual(st.chain_imbalance_db, 2.0)
        self.assertEqual(st.tx_rate_mbps, 86.7)
        self.assertEqual(st.mcs, 4)
        self.assertEqual(st.nss, 2)
        self.assertEqual(st.bandwidth_mhz, 40)
        self.assertTrue(st.short_gi)
        self.assertEqual(st.tx_retries, 25)
        self.assertEqual(st.tx_failed, 3)

        # Ath10k HTT & AQL report checks
        self.assertIsNotNone(snapshot.ath10k_report)
        htt = snapshot.ath10k_report.htt_stats
        self.assertEqual(htt.tx_packets, 6144)
        self.assertEqual(htt.tx_retries, 25)
        self.assertEqual(htt.queue_depth, 4)
        self.assertIn("BE", snapshot.ath10k_report.aql_queues)

        # Spectral check
        self.assertIsNotNone(snapshot.spectral_report)
        self.assertEqual(snapshot.spectral_report.center_freq_mhz, 5200.0)

        # Serialization to dict
        d = snapshot.to_dict()
        self.assertEqual(d["connection_state"], "CONNECTED")
        self.assertEqual(d["host"], "10.99.0.1")
        self.assertEqual(d["iface"], "phy0-ap0")

    def test_error_and_recovery(self):
        calls = 0

        def flaky_openwrt_executor(cmd: str, timeout: float) -> Tuple[str, str, int]:
            nonlocal calls
            calls += 1
            if calls == 1:
                return "", "Host unreachable", 1
            delimiter = "---FMX_DELIM---"
            return f"{MOCK_IW_STATION_DUMP}\n{delimiter}\n{MOCK_HTT_TX_STATS}\n{delimiter}\n{MOCK_TXQ_AQL}", "", 0

        cfg = OpenWrtPollerConfig(host="10.99.0.1")
        poller = OpenWrtLiveSSHPoller(config=cfg, ssh_executor=flaky_openwrt_executor)

        # 1st call fails
        s1 = poller.poll_cycle()
        self.assertEqual(s1.connection_state, ConnectionState.DEGRADED)
        self.assertEqual(s1.consecutive_errors, 1)

        # 2nd call succeeds
        s2 = poller.poll_cycle()
        self.assertEqual(s2.connection_state, ConnectionState.CONNECTED)
        self.assertEqual(s2.consecutive_errors, 0)
        self.assertEqual(len(s2.stations), 1)


if __name__ == "__main__":
    unittest.main()
