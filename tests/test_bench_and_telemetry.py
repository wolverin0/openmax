"""Comprehensive Unit Tests for FuturaMAX Physical Bench and Telemetry Suite.

Covers:
1. tools/bench/bufferbloat_suite.py (percentile math, latency distribution, ping parsing, iperf3 JSON parsing, receipt generation)
2. tools/bench/tc_cake_tune.py (command generation for CAKE/FQ, qdisc output parsing for drops, backlogs, memory, delays)
3. telemetry/spectral_fft/parser.py (ath10k type 2 & 3 parsing, airOS JSON parsing, per-bin power, peak interference frequency, channel occupancy)
4. telemetry/station_monitor.py (Linux iw station dump parsing, airOS wstalist JSON parsing, sector summary, degraded station detection)
"""

import json
import struct
import pytest
from pathlib import Path

# Module imports
from tools.bench.bufferbloat_suite import (
    calculate_percentile,
    calculate_latency_stats,
    parse_ping_output,
    parse_iperf3_json,
    BufferbloatSuite,
    LatencyStats,
    BenchReceipt,
)
from tools.bench.tc_cake_tune import (
    build_cake_cmd,
    build_fq_cmd,
    build_fq_codel_cmd,
    build_del_cmd,
    build_show_cmd,
    parse_tc_qdisc_output,
    _parse_time_unit_to_ms,
    _parse_size_to_bytes,
    _parse_bandwidth_to_bps,
)
from telemetry.spectral_fft.parser import (
    SpectralParser,
    AirOSSpectralParser,
    LightweightInterferenceClassifier,
    InterferenceClass,
    calculate_peak_interference_frequency,
    calculate_channel_occupancy,
    analyze_spectral_sample,
    ATH_FFT_SAMPLE_ATH10K,
    ATH_FFT_SAMPLE_ATH10K_TYPE3,
    HEADER_FORMAT,
    HEADER_SIZE,
    HEADER_TYPE3_PAYLOAD_FORMAT,
    HEADER_TYPE3_PAYLOAD_SIZE,
)
from telemetry.station_monitor import (
    StationMonitor,
    StationTelemetry,
    StationSectorSummary,
)


# ============================================================================
# 1. BUFFERBLOAT SUITE TESTS
# ============================================================================

class TestBufferbloatSuite:

    def test_calculate_percentile_empty_and_single(self):
        assert calculate_percentile([], 50.0) == 0.0
        assert calculate_percentile([42.5], 90.0) == 42.5
        assert calculate_percentile([42.5], 50.0) == 42.5

    def test_calculate_percentile_interpolation(self):
        data = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        # p50 on 10 elements: index = 4.5 -> 55.0
        assert calculate_percentile(data, 50.0) == 55.0
        assert calculate_percentile(data, 0.0) == 10.0
        assert calculate_percentile(data, 100.0) == 100.0
        assert calculate_percentile(data, 90.0) == 91.0
        assert calculate_percentile(data, 95.0) == 95.5
        assert calculate_percentile(data, 99.0) == 99.1

    def test_calculate_latency_stats_known_distribution(self):
        rtts = [10.0, 12.0, 15.0, 11.0, 14.0, 20.0, 100.0]
        stats = calculate_latency_stats(rtts, packets_sent=10, packets_recv=7)

        assert stats.sample_count == 7
        assert stats.packets_sent == 10
        assert stats.packets_recv == 7
        assert stats.packet_loss_pct == 30.0
        assert stats.min_ms == 10.0
        assert stats.max_ms == 100.0
        assert stats.avg_ms == round(sum(rtts) / 7.0, 3)
        assert stats.p50_ms == 14.0
        assert stats.p95_ms > 20.0
        assert stats.max_jitter_ms == 80.0  # |100.0 - 20.0|
        assert stats.rfc3550_jitter_ms > 0.0
        assert stats.stddev_ms > 0.0

    def test_calculate_latency_stats_zero_samples(self):
        stats = calculate_latency_stats([], packets_sent=50, packets_recv=0)
        assert stats.sample_count == 0
        assert stats.packet_loss_pct == 100.0
        assert stats.min_ms == 0.0
        assert stats.p50_ms == 0.0

    def test_parse_ping_output(self):
        raw_ping = """
PING 10.99.0.1 (10.99.0.1) 56(84) bytes of data.
64 bytes from 10.99.0.1: icmp_seq=1 ttl=64 time=1.23 ms
64 bytes from 10.99.0.1: icmp_seq=2 ttl=64 time=2.45 ms
64 bytes from 10.99.0.1: icmp_seq=3 ttl=64 time=1.89 ms
64 bytes from 10.99.0.1: icmp_seq=4 ttl=64 time=3.10 ms

--- 10.99.0.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 1.230/2.167/3.100/0.678 ms
"""
        rtts, sent, recv = parse_ping_output(raw_ping)
        assert len(rtts) == 4
        assert rtts == [1.23, 2.45, 1.89, 3.10]
        assert sent == 4
        assert recv == 4

    def test_parse_ping_output_with_packet_loss(self):
        raw_ping = """
PING 10.99.0.1 (10.99.0.1) 56(84) bytes of data.
64 bytes from 10.99.0.1: icmp_seq=1 ttl=64 time=5.12 ms
64 bytes from 10.99.0.1: icmp_seq=3 ttl=64 time=4.88 ms

--- 10.99.0.1 ping statistics ---
5 packets transmitted, 2 received, 60% packet loss, time 4010ms
"""
        rtts, sent, recv = parse_ping_output(raw_ping)
        assert len(rtts) == 2
        assert sent == 5
        assert recv == 2

    def test_parse_iperf3_json_tcp(self):
        sample_json = json.dumps({
            "end": {
                "sum_sent": {
                    "bits_per_second": 94500000.0,
                    "retransmits": 3
                },
                "sum_received": {
                    "bits_per_second": 93200000.0
                }
            }
        })
        res = parse_iperf3_json(sample_json)
        assert res["throughput_mbps"] == 93.20
        assert res["retransmits"] == 3
        assert res["udp_loss_pct"] is None

    def test_parse_iperf3_json_udp(self):
        sample_json = json.dumps({
            "end": {
                "sum": {
                    "bits_per_second": 49800000.0,
                    "lost_percent": 0.45,
                    "jitter_ms": 1.254
                }
            }
        })
        res = parse_iperf3_json(sample_json)
        assert res["throughput_mbps"] == 49.80
        assert res["udp_loss_pct"] == 0.45
        assert res["udp_jitter_ms"] == 1.254
        assert res["retransmits"] is None

    def test_parse_iperf3_json_error(self):
        res = parse_iperf3_json('{"error": "unable to connect to server"}')
        assert "unable to connect" in res["error"]

    def test_bufferbloat_suite_dry_run_and_receipt(self, tmp_path):
        suite = BufferbloatSuite(
            target_ip="10.99.0.1",
            ping_interval=0.02,
            duration=2,
            out_dir=tmp_path,
            dry_run=True,
        )
        receipt = suite.run_suite(profiles=["tcp_dl", "udp_50m"])
        assert len(receipt.results) == 2
        assert "tcp_dl" in receipt.results
        assert "udp_50m" in receipt.results
        assert receipt.summary["total_profiles_tested"] == 2
        assert receipt.summary["bufferbloat_grade"] in ["A+", "A", "B"]

        saved_path = suite.save_receipt(receipt)
        assert saved_path.exists()
        loaded = json.loads(saved_path.read_text(encoding="utf-8"))
        assert loaded["run_id"] == receipt.run_id


# ============================================================================
# 2. TC CAKE / FQ TUNING TESTS
# ============================================================================

class TestTcCakeTune:

    def test_build_cake_cmd(self):
        cmd = build_cake_cmd("eth0", "50Mbit")
        assert cmd == ["tc", "qdisc", "replace", "dev", "eth0", "root", "cake", "bandwidth", "50Mbit", "diffserv4", "ack-filter"]

        cmd2 = build_cake_cmd("enp3s0", "100Mbit", diffserv="besteffort", ack_filter=False, rtt="20ms", memlimit="8Mb")
        assert cmd2 == ["tc", "qdisc", "replace", "dev", "enp3s0", "root", "cake", "bandwidth", "100Mbit", "besteffort", "rtt", "20ms", "memlimit", "8Mb"]

    def test_build_fq_cmd(self):
        cmd = build_fq_cmd("eth0", pacing=True, limit=10000, flow_limit=100)
        assert cmd == ["tc", "qdisc", "replace", "dev", "eth0", "root", "fq", "pacing", "limit", "10000", "flow_limit", "100"]

        cmd2 = build_fq_cmd("eth0", pacing=False)
        assert cmd2 == ["tc", "qdisc", "replace", "dev", "eth0", "root", "fq"]

    def test_build_fq_codel_cmd(self):
        cmd = build_fq_codel_cmd("eth0", limit=1024, target="5ms", interval="100ms", ecn=False)
        assert cmd == ["tc", "qdisc", "replace", "dev", "eth0", "root", "fq_codel", "limit", "1024", "target", "5ms", "interval", "100ms", "noecn"]

    def test_build_del_and_show_cmd(self):
        assert build_del_cmd("eth0") == ["tc", "qdisc", "del", "dev", "eth0", "root"]
        assert build_show_cmd("eth0") == ["tc", "-s", "qdisc", "show", "dev", "eth0"]

    def test_unit_conversion_helpers(self):
        assert _parse_time_unit_to_ms("1.2ms") == 1.2
        assert _parse_time_unit_to_ms("450us") == 0.45
        assert _parse_time_unit_to_ms("0us") == 0.0
        assert _parse_time_unit_to_ms("2s") == 2000.0

        assert _parse_size_to_bytes("1514b") == 1514
        assert _parse_size_to_bytes("4Mb") == 4 * 1024 * 1024
        assert _parse_size_to_bytes("64Kb") == 64 * 1024

        assert _parse_bandwidth_to_bps("50Mbit") == 50_000_000
        assert _parse_bandwidth_to_bps("3125Kbit") == 3_125_000
        assert _parse_bandwidth_to_bps("1Gbit") == 1_000_000_000

    def test_parse_tc_qdisc_output_cake(self):
        raw_output = """
qdisc cake 8001: dev eth0 root refcnt 2 bandwidth 50Mbit diffserv4 ack-filter
 Sent 12345678 bytes 9876 pkt (dropped 14, overlimits 34 requeues 0)
 backlog 1514b 1p requeues 0
 memory used: 1514b of 4Mb
 capacity estimate: 50Mbit
 min net len: 64b, max net len: 1514b
   Tin 0: Bulk
     thresh 3125Kbit
     target 5.0ms interval 100.0ms
     pk_delay 1.2ms av_delay 450us
     sp_delay 120us
     backlog 0b 0p
     pkts 100 bytes 150000
     drops 2 marks 0
     ack_drop 0
   Tin 1: Best Effort
     thresh 50Mbit
     target 5.0ms interval 100.0ms
     pk_delay 2.8ms av_delay 850us
     sp_delay 200us
     backlog 1514b 1p
     pkts 9776 bytes 12195678
     drops 12 marks 5
     ack_drop 2
"""
        stats_list = parse_tc_qdisc_output(raw_output)
        assert len(stats_list) == 1
        s = stats_list[0]
        assert s.qdisc_type == "cake"
        assert s.handle == "8001:"
        assert s.iface == "eth0"
        assert s.params.get("bandwidth") == "50Mbit"
        assert s.params.get("diffserv") == "diffserv4"
        assert s.params.get("ack_filter") is True
        assert s.bytes_sent == 12345678
        assert s.packets_sent == 9876
        assert s.dropped == 14
        assert s.overlimits == 34
        assert s.backlog_bytes == 1514
        assert s.backlog_packets == 1
        assert s.memory_used_bytes == 1514
        assert s.memory_limit_bytes == 4 * 1024 * 1024
        assert s.capacity_estimate_bps == 50_000_000
        assert len(s.tin_stats) == 2

        tin0 = s.tin_stats[0]
        assert tin0.tin_id == 0
        assert tin0.name == "Bulk"
        assert tin0.pk_delay_ms == 1.2
        assert tin0.av_delay_ms == 0.45
        assert tin0.drops == 2

        tin1 = s.tin_stats[1]
        assert tin1.tin_id == 1
        assert tin1.name == "Best Effort"
        assert tin1.drops == 12
        assert tin1.ack_drops == 2
        assert s.peak_delay_ms == 2.8

    def test_parse_tc_qdisc_output_fq(self):
        raw_output = """
qdisc fq 8002: dev eth1 root refcnt 2 limit 10000p flow_limit 100p pacing
 Sent 54321 bytes 123 pkt (dropped 5, overlimits 10 requeues 0)
 backlog 0b 0p requeues 0
  flows 2 (inactive 1 throttled 0)
"""
        stats_list = parse_tc_qdisc_output(raw_output)
        assert len(stats_list) == 1
        s = stats_list[0]
        assert s.qdisc_type == "fq"
        assert s.iface == "eth1"
        assert s.bytes_sent == 54321
        assert s.packets_sent == 123
        assert s.dropped == 5
        assert s.overlimits == 10
        assert s.params.get("pacing") is True


# ============================================================================
# 3. SPECTRAL FFT PARSER & RF METRICS TESTS
# ============================================================================

class TestSpectralFFTParser:

    def test_calculate_peak_interference_frequency(self):
        # 56 bins, 20 MHz wide, center freq 5200 MHz
        # Bins: 0 to 55. If bin 28 is maximum, frequency should be close to center (5200.179 MHz)
        bin_dbm = [-95.0] * 56
        bin_dbm[28] = -50.0  # Strong peak at center bin
        freq = calculate_peak_interference_frequency(bin_dbm, center_freq_mhz=5200.0, chan_width_mhz=20.0)
        assert 5199.5 <= freq <= 5200.5

        # If bin 0 is maximum (lowest edge)
        bin_dbm_low = [-95.0] * 56
        bin_dbm_low[0] = -40.0
        freq_low = calculate_peak_interference_frequency(bin_dbm_low, center_freq_mhz=5200.0, chan_width_mhz=20.0)
        assert 5189.5 <= freq_low <= 5190.5

    def test_calculate_channel_occupancy(self):
        # 50 bins, noise floor -95 dBm
        # 10 bins at -80 dBm (which is >= -95 + 10 = -85 dBm)
        bin_dbm = [-95.0] * 40 + [-80.0] * 10
        occupancy = calculate_channel_occupancy(bin_dbm, noise_floor_dbm=-95.0, threshold_delta_db=10.0)
        assert occupancy == 20.0  # 10 / 50 = 20%

        # Absolute threshold test
        occupancy_abs = calculate_channel_occupancy(bin_dbm, noise_floor_dbm=-95.0, absolute_threshold_dbm=-85.0)
        assert occupancy_abs == 20.0

        # All clean
        clean_bins = [-95.0] * 50
        assert calculate_channel_occupancy(clean_bins, -95.0) == 0.0

    def test_ath10k_type3_relay_dump_parsing(self):
        # Synthetic ath10k Type 3 sample matching openwrt/ath10k-ct debugfs relayfs layout
        tlv_type = ATH_FFT_SAMPLE_ATH10K_TYPE3
        payload_len = HEADER_TYPE3_PAYLOAD_SIZE + 64  # 24 byte header + 64 bins

        width = 20
        f1 = 5180
        f2 = 0
        noise = -94
        maxmag = 150
        gain = 35
        basepwr = 10
        tsf = 987654321
        maxidx = 32
        rssi = 25
        relpwr = 12
        avgpwr = 20
        maxexp = 1

        body_hdr = struct.pack(
            HEADER_TYPE3_PAYLOAD_FORMAT,
            width, f1, f2, noise, maxmag, gain, basepwr, tsf, maxidx, rssi, relpwr, avgpwr, maxexp
        )
        bins = bytes([30 + (i % 4) for i in range(64)])

        packet = struct.pack(">BH", tlv_type, payload_len) + body_hdr + bins

        parser = SpectralParser()
        samples = list(parser.feed(packet))
        assert len(samples) == 1
        s = samples[0]
        assert s.tlv_type == ATH_FFT_SAMPLE_ATH10K_TYPE3
        assert s.chan_width_mhz == 20
        assert s.freq1_mhz == 5180
        assert s.noise_dbm == -94
        assert len(s.bin_dbm) == 64

    def test_airos_spectral_json_parsing(self):
        airos_json = {
            "samples": [
                {
                    "center_freq": 5200,
                    "chan_width": 20,
                    "noise_floor": -96,
                    "rssi": -65,
                    "timestamp": 1728000000,
                    "bins": [-96.0, -95.5, -55.0, -96.0, -95.0, -96.0]
                }
            ]
        }
        samples = AirOSSpectralParser.parse_json(airos_json)
        assert len(samples) == 1
        s = samples[0]
        assert s.freq1_mhz == 5200
        assert s.chan_width_mhz == 20
        assert s.noise_dbm == -96
        assert len(s.bin_dbm) == 6
        assert s.bin_dbm[2] == -55.0

    def test_analyze_spectral_sample(self):
        airos_json = {
            "center_freq": 5240,
            "chan_width": 20,
            "noise_floor": -95,
            "bins": [-95.0] * 30 + [-50.0] + [-95.0] * 25  # 56 bins, peak at bin 30
        }
        sample = AirOSSpectralParser.parse_json(airos_json)[0]
        report = analyze_spectral_sample(sample, threshold_delta_db=10.0)

        assert report.center_freq_mhz == 5240.0
        assert report.chan_width_mhz == 20.0
        assert report.noise_floor_dbm == -95.0
        assert report.peak_power_dbm == -50.0
        assert 5239.0 <= report.peak_interference_freq_mhz <= 5242.0
        assert report.channel_occupancy_pct > 0.0
        assert report.interference_class in [InterferenceClass.RADAR_DFS, InterferenceClass.NARROWBAND_CW]
        assert "papr_db" in report.metrics


# ============================================================================
# 4. STATION MONITOR TESTS
# ============================================================================

class TestStationMonitor:

    def test_parse_iw_station_dump(self):
        raw_iw = """
Station 00:27:22:11:22:33 (on phy0-ap0)
\tinactive time:\t120 ms
\trx bytes:\t1048576
\trx packets:\t1024
\ttx bytes:\t5242880
\ttx packets:\t4096
\ttx retries:\t15
\ttx failed:\t2
\tsignal:\t-62 dBm
\tsignal avg:\t[-64, -66] dBm
\ttx bitrate:\t144.4 MBit/s, 40MHz, MCS 6, VHT-NSS 2, short GI
\trx bitrate:\t130.0 MBit/s, 40MHz, MCS 5, VHT-NSS 2
\texpected throughput:\t95.2Mbps
\tairtime:\t12500 us
Station 00:27:22:44:55:66 (on phy0-ap0)
\tinactive time:\t50 ms
\trx bytes:\t2000
\trx packets:\t20
\ttx bytes:\t3000
\ttx packets:\t30
\ttx retries:\t120
\ttx failed:\t35
\tsignal:\t-85 dBm
\tsignal avg:\t[-82, -91] dBm
\ttx bitrate:\t13.5 MBit/s, 20MHz, MCS 1, VHT-NSS 1
\trx bitrate:\t13.5 MBit/s, 20MHz, MCS 1, VHT-NSS 1
"""
        stations = StationMonitor.parse_iw_station_dump(raw_iw, noise_floor_dbm=-95)
        assert len(stations) == 2

        # Station 1
        s1 = stations["00:27:22:11:22:33"]
        assert s1.signal_dbm == -62
        assert s1.chain0_signal_dbm == -64
        assert s1.chain1_signal_dbm == -66
        assert s1.chain_imbalance_db == 2.0
        assert s1.snr_db == 33.0  # -62 - (-95)
        assert s1.tx_rate_mbps == 144.4
        assert s1.mcs == 6
        assert s1.nss == 2
        assert s1.bandwidth_mhz == 40
        assert s1.short_gi is True
        assert s1.tx_retries == 15
        assert s1.tx_failed == 2

        # Station 2
        s2 = stations["00:27:22:44:55:66"]
        assert s2.signal_dbm == -85
        assert s2.chain_imbalance_db == 9.0  # |-82 - (-91)|
        assert s2.mcs == 1
        assert s2.nss == 1
        assert s2.tx_retries == 120
        assert s2.tx_failed == 35

    def test_parse_airos_telemetry(self):
        raw_airos = [
            {
                "mac": "00:27:22:AA:BB:CC",
                "name": "CPE-Tower-North",
                "signal": -58,
                "noisefloor": -94,
                "rssi": [-59, -60],
                "tx_rate": 86.7,
                "rx_rate": 86.7,
                "tx_mcs": 8,
                "tx_nss": 1,
                "tx_retries": 10,
                "distance": 450,
                "airmax": {
                    "priority": 2,
                    "quality": 95,
                    "capacity": 88,
                    "airtime": {
                        "tx": 12.5,
                        "rx": 6.8
                    }
                }
            }
        ]
        stations = StationMonitor.parse_airos_telemetry(raw_airos)
        assert len(stations) == 1
        s = stations["00:27:22:aa:bb:cc"]
        assert s.device_name == "CPE-Tower-North"
        assert s.signal_dbm == -58
        assert s.noise_floor_dbm == -94
        assert s.snr_db == 36.0
        assert s.chain_imbalance_db == 1.0
        assert s.mcs == 8
        assert s.nss == 1
        assert s.airtime_dl_pct == 12.5
        assert s.airtime_ul_pct == 6.8
        assert s.airtime_total_pct == 19.3
        assert s.distance_meters == 450
        assert s.airmax_quality_pct == 95

    def test_station_monitor_summarize_and_degraded_detection(self):
        raw_iw = """
Station 00:27:22:11:22:33 (on phy0-ap0)
\tsignal:\t-60 dBm
\tsignal avg:\t[-60, -60] dBm
\ttx bitrate:\t100.0 MBit/s, 40MHz, MCS 7, VHT-NSS 2
\ttx retries:\t5
\ttx failed:\t0
Station 00:27:22:44:55:66 (on phy0-ap0)
\tsignal:\t-86 dBm
\tsignal avg:\t[-82, -90] dBm
\ttx bitrate:\t13.5 MBit/s, 20MHz, MCS 1, VHT-NSS 1
\ttx retries:\t200
\ttx failed:\t40
"""
        stations = StationMonitor.parse_iw_station_dump(raw_iw, noise_floor_dbm=-95)
        summary = StationMonitor.summarize(stations, source="iw")

        assert summary.station_count == 2
        assert summary.total_tx_retries == 205
        assert summary.avg_tx_rate_mbps == 56.8  # (100 + 13.5) / 2
        # Station 2 must be flagged as degraded (imbalance 8.0 > 3.5, MCS 1 <= 2, failed 40 > 20)
        assert "00:27:22:44:55:66" in summary.degraded_stations
        assert "00:27:22:11:22:33" not in summary.degraded_stations
