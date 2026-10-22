"""Unit tests for controller.cooperative_sensor."""

from __future__ import annotations

import math
import pytest

from controller.cooperative_sensor import (
    ANGULAR_RF_INTERFERENCE_CLUSTER,
    CPE_CHAIN_IMBALANCE_OR_MISALIGNMENT,
    CPE_ETHERNET_POE_CABLE_FAULT,
    HEALTHY,
    SECTOR_WIDE_OR_BACKHAUL_FAULT,
    CpeTelemetrySample,
    compute_airtime_tax,
    evaluate_relay_feasibility,
    localize_sector_faults,
)


def test_compute_airtime_tax_flags_obstructed_airtime_hog():
    """Verify that a low-MCS high-airtime station is flagged as an airtime hog."""
    samples = [
        CpeTelemetrySample(
            cpe_id="CPE_FAST_1",
            mac="78:8a:20:71:99:7b",
            useful_bytes=50_000_000,
            measured_airtime_us=250_000,
            last_tx_bitrate_mbps=144.4,
        ),
        CpeTelemetrySample(
            cpe_id="CPE_FAST_2",
            mac="78:8a:20:71:99:7c",
            useful_bytes=45_000_000,
            measured_airtime_us=250_000,
            last_tx_bitrate_mbps=130.0,
        ),
        CpeTelemetrySample(
            cpe_id="CPE_HOG_WALL",
            mac="64:d1:54:1b:96:97",
            useful_bytes=5_000_000,  # Only 5% of sector bytes
            measured_airtime_us=500_000,  # Consumes 50% of sector airtime!
            last_tx_bitrate_mbps=6.5,
            be_deficit_us=-67099,
        ),
    ]

    results = compute_airtime_tax(samples)
    by_id = {r.cpe_id: r for r in results}

    assert not by_id["CPE_FAST_1"].is_airtime_hog
    assert not by_id["CPE_FAST_2"].is_airtime_hog
    assert by_id["CPE_FAST_1"].airtime_tax_ratio == pytest.approx(0.50, rel=1e-3)

    hog = by_id["CPE_HOG_WALL"]
    assert hog.is_airtime_hog is True
    assert hog.airtime_share == pytest.approx(0.50, rel=1e-3)
    assert hog.useful_byte_share == pytest.approx(0.05, rel=1e-3)
    assert hog.airtime_tax_ratio == pytest.approx(10.0, rel=1e-3)
    assert "deep_negative_be_deficit=-67099us" in hog.reason


def test_compute_airtime_tax_qca988x_6mbps_fallback_warning():
    """Verify QCA988x Wave-1 6 Mbps estimation fallback warning when peer stats are off."""
    samples = [
        CpeTelemetrySample(
            cpe_id="CPE_NO_PEER_STATS",
            mac="aa:bb:cc:dd:ee:01",
            useful_bytes=6_000_000,
            measured_airtime_us=None,
            last_tx_bitrate_mbps=0.0,  # Triggers 6 Mbps fallback per QCA988X_CONTROL_BOUNDARY.md
        ),
        CpeTelemetrySample(
            cpe_id="CPE_WITH_PEER_STATS",
            mac="aa:bb:cc:dd:ee:02",
            useful_bytes=6_000_000,
            measured_airtime_us=None,
            last_tx_bitrate_mbps=120.0,
        ),
    ]

    results = compute_airtime_tax(samples)
    by_id = {r.cpe_id: r for r in results}

    assert by_id["CPE_NO_PEER_STATS"].used_6mbps_fallback_warning is True
    assert by_id["CPE_WITH_PEER_STATS"].used_6mbps_fallback_warning is False
    # 6 MB at 6 Mbps fallback = 8,000,000 us vs 400,000 us at 120 Mbps (20x inflation)
    assert by_id["CPE_NO_PEER_STATS"].airtime_us == pytest.approx(8_000_000.0)
    assert by_id["CPE_WITH_PEER_STATS"].airtime_us == pytest.approx(400_000.0)
    assert "warning:last_tx_bitrate=0_6mbps_fallback" in by_id["CPE_NO_PEER_STATS"].reason


def test_evaluate_relay_feasibility_approves_severe_nlos_with_good_neighbor():
    """Case 1 from COOPERATIVE_CPE_FEASIBILITY.md Section 2.A.4:
    B->AP is 4.5 Mbps (222.2 ms/Mbit), B->A is 65 Mbps (-61 dBm), A->AP is 80 Mbps.
    With overhead_factor=1.25, relay costs 34.9 ms/Mbit (28.7 Mbps effective), saving 84.3% airtime.
    """
    res = evaluate_relay_feasibility(
        r_b_ap_mbps=4.5,
        r_b_a_mbps=65.0,
        r_a_ap_mbps=80.0,
        rssi_b_a_dbm=-61.0,
        overhead_factor=1.25,
    )
    assert res.approved is True
    assert res.direct_airtime_ms_per_mbit == pytest.approx(222.222, rel=1e-3)
    assert res.relay_airtime_ms_per_mbit == pytest.approx(34.855, rel=1e-3)
    assert res.effective_relay_rate_mbps == pytest.approx(28.69, rel=1e-2)
    assert res.airtime_savings_pct == pytest.approx(84.31, rel=1e-2)
    assert res.speedup_ratio == pytest.approx(6.375, rel=1e-2)


def test_evaluate_relay_feasibility_rejects_when_direct_link_is_already_good():
    """Case 3 from COOPERATIVE_CPE_FEASIBILITY.md:
    B->AP is 38 Mbps (26.3 ms/Mbit), B->A is 60 Mbps, A->AP is 75 Mbps.
    Two-hop relay costs 37.5 ms/Mbit (+42.5% more airtime than direct) -> REJECT.
    """
    res = evaluate_relay_feasibility(
        r_b_ap_mbps=38.0,
        r_b_a_mbps=60.0,
        r_a_ap_mbps=75.0,
        rssi_b_a_dbm=-63.0,
        overhead_factor=1.25,
    )
    assert res.approved is False
    assert res.airtime_savings_pct < 0.0
    assert "REJECT: relay costs" in res.reason


def test_evaluate_relay_feasibility_rejects_weak_sidelobe_rssi():
    """Case 4: LiteBeam 23 dBi dish off-axis sidelobe (-76 dBm < -68 dBm gate) -> REJECT."""
    res = evaluate_relay_feasibility(
        r_b_ap_mbps=6.0,
        r_b_a_mbps=40.0,
        r_a_ap_mbps=80.0,
        rssi_b_a_dbm=-76.0,
        overhead_factor=1.25,
    )
    assert res.approved is False
    assert "sidelobe RSSI" in res.reason


def test_localize_sector_faults_sector_wide_or_backhaul():
    """Verify detection of POP backhaul / AP-wide fault across wide azimuth spread."""
    samples = [
        CpeTelemetrySample(
            cpe_id="CPE_NORTH",
            mac="00:11:22:33:44:01",
            azimuth_deg=15.0,
            cinr_db=26.0,
            rtt_p95_ms=95.0,
            packet_loss_pct=6.5,
        ),
        CpeTelemetrySample(
            cpe_id="CPE_EAST",
            mac="00:11:22:33:44:02",
            azimuth_deg=85.0,
            cinr_db=24.0,
            rtt_p95_ms=110.0,
            packet_loss_pct=7.0,
        ),
        CpeTelemetrySample(
            cpe_id="CPE_SOUTH",
            mac="00:11:22:33:44:03",
            azimuth_deg=130.0,
            cinr_db=25.0,
            rtt_p95_ms=88.0,
            packet_loss_pct=5.2,
        ),
    ]

    report = localize_sector_faults(samples)
    assert report.sector_classification == SECTOR_WIDE_OR_BACKHAUL_FAULT
    assert set(report.affected_cpe_ids) == {"CPE_NORTH", "CPE_EAST", "CPE_SOUTH"}


def test_localize_sector_faults_angular_rf_interference_cluster():
    """Verify detection of localized directional RF interference along a narrow azimuth wedge."""
    samples = [
        CpeTelemetrySample(
            cpe_id="CPE_WEDGE_1",
            mac="00:11:22:33:44:11",
            azimuth_deg=42.0,
            cinr_db=12.0,
            baseline_cinr_db=24.0,
        ),
        CpeTelemetrySample(
            cpe_id="CPE_WEDGE_2",
            mac="00:11:22:33:44:12",
            azimuth_deg=54.0,
            cinr_db=13.5,
            baseline_cinr_db=25.0,
        ),
        CpeTelemetrySample(
            cpe_id="CPE_CLEAR_WEST",
            mac="00:11:22:33:44:13",
            azimuth_deg=115.0,
            cinr_db=27.0,
            baseline_cinr_db=27.0,
        ),
        CpeTelemetrySample(
            cpe_id="CPE_CLEAR_SOUTH",
            mac="00:11:22:33:44:14",
            azimuth_deg=150.0,
            cinr_db=26.0,
            baseline_cinr_db=26.0,
        ),
    ]

    report = localize_sector_faults(samples)
    assert report.sector_classification == ANGULAR_RF_INTERFERENCE_CLUSTER
    assert report.affected_cpe_ids == ["CPE_WEDGE_1", "CPE_WEDGE_2"]
    assert report.angular_cluster_center_deg == pytest.approx(48.0, rel=1e-2)
    assert report.per_cpe_classifications["CPE_CLEAR_WEST"] == HEALTHY


def test_localize_sector_faults_panel3_guarida_chain_imbalance():
    """Verify exact production telemetry from Panel3-Guarida (Stage 10 Section 5):
    GALEANO_Rocio_Del_Lujan has 10 dB chain imbalance (-36 vs -46 dBm), while
    TABORDA and SOSA are healthy.
    """
    samples = [
        CpeTelemetrySample(
            cpe_id="TABORDA_Ada_Cristina_Ayelen",
            mac="00:11:22:33:55:01",
            azimuth_deg=20.0,
            distance_m=2700.0,
            rssi_dbm=-62.0,
            cinr_db=24.0,
            chain0_dbm=-64.0,
            chain1_dbm=-65.0,
        ),
        CpeTelemetrySample(
            cpe_id="GALEANO_Rocio_Del_Lujan",
            mac="00:11:22:33:55:02",
            azimuth_deg=65.0,
            distance_m=1050.0,
            rssi_dbm=-60.0,
            cinr_db=29.0,
            chain0_dbm=-36.0,
            chain1_dbm=-46.0,  # 10 dB chain delta!
        ),
        CpeTelemetrySample(
            cpe_id="SOSA_Joaquin_Alejandro",
            mac="00:11:22:33:55:03",
            azimuth_deg=110.0,
            distance_m=450.0,
            rssi_dbm=-56.0,
            cinr_db=23.0,
            chain0_dbm=-58.0,
            chain1_dbm=-59.0,
        ),
    ]

    report = localize_sector_faults(samples)
    assert report.sector_classification == CPE_CHAIN_IMBALANCE_OR_MISALIGNMENT
    assert report.affected_cpe_ids == ["GALEANO_Rocio_Del_Lujan"]
    assert (
        report.per_cpe_classifications["GALEANO_Rocio_Del_Lujan"]
        == CPE_CHAIN_IMBALANCE_OR_MISALIGNMENT
    )
    assert report.per_cpe_classifications["TABORDA_Ada_Cristina_Ayelen"] == HEALTHY
    assert report.per_cpe_classifications["SOSA_Joaquin_Alejandro"] == HEALTHY


def test_localize_sector_faults_cpe_ethernet_poe_cable_fault():
    """Verify detection of customer RJ45 / PoE cable fault (10Mbps half-duplex / flaps)
    when the 5 GHz RF link is healthy.
    """
    samples = [
        CpeTelemetrySample(
            cpe_id="CPE_HEALTHY_1",
            mac="00:11:22:33:66:01",
            azimuth_deg=30.0,
            rssi_dbm=-53.0,
            cinr_db=25.0,
            eth_speed_mbps=100,
            eth_duplex="full",
        ),
        CpeTelemetrySample(
            cpe_id="CPE_BAD_POE_CABLE",
            mac="00:11:22:33:66:02",
            azimuth_deg=85.0,
            rssi_dbm=-54.0,
            cinr_db=26.0,
            eth_speed_mbps=10,
            eth_duplex="half",
            eth_carrier_flaps=7,
            eth_crc_errors=42,
        ),
    ]

    report = localize_sector_faults(samples)
    assert report.sector_classification == CPE_ETHERNET_POE_CABLE_FAULT
    assert report.affected_cpe_ids == ["CPE_BAD_POE_CABLE"]
    assert (
        report.per_cpe_classifications["CPE_BAD_POE_CABLE"]
        == CPE_ETHERNET_POE_CABLE_FAULT
    )
    assert report.per_cpe_classifications["CPE_HEALTHY_1"] == HEALTHY


def test_localize_sector_faults_healthy_sector():
    """Verify healthy classification when all CPEs are within normal RF and LAN bounds."""
    samples = [
        CpeTelemetrySample(
            cpe_id="CPE_1",
            mac="00:11:22:33:77:01",
            azimuth_deg=10.0,
            rssi_dbm=-53.0,
            cinr_db=25.0,
            chain0_dbm=-55.0,
            chain1_dbm=-56.0,
        ),
        CpeTelemetrySample(
            cpe_id="CPE_2",
            mac="00:11:22:33:77:02",
            azimuth_deg=90.0,
            rssi_dbm=-58.0,
            cinr_db=23.0,
            chain0_dbm=-60.0,
            chain1_dbm=-61.0,
        ),
    ]

    report = localize_sector_faults(samples)
    assert report.sector_classification == HEALTHY
    assert report.affected_cpe_ids == []
