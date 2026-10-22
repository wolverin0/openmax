"""Unit tests for Stage 1 Stock-airOS Intelligence modules:
1. controller/capacity_forecasting.py: Sector capacity, airtime saturation (>85% cliff),
   bottleneck CPE diagnosis, and counterfactual capacity gain projection.
2. controller/advisory_mode.py: Station link auditing (chain imbalance, poor SNR, receiver overload,
   retries), RF advisories (spectral channel selection, 20 vs 40 MHz width, TX power balancing),
   and CanaryManager with causal before/after evaluation and automatic rollback guard.
"""

from __future__ import annotations

import unittest
from typing import Any, Dict

from controller.advisory_mode import (
    AuditSeverity,
    CanaryManager,
    CanaryTrial,
    CPEAuditRecord,
    RFAdvisory,
    SectorAdvisor,
    calculate_jains_fairness,
)
from controller.capacity_forecasting import (
    DEFAULT_AIRTIME_CLIFF_PCT,
    DEFAULT_MAC_EFFICIENCY,
    DEFAULT_PLANS,
    BottleneckDiagnosis,
    CapacityForecastResult,
    PlanTier,
    SectorCapacityForecaster,
    SubscriberDemand,
)


class TestCapacityForecastingMath(unittest.TestCase):
    """Test fundamental 802.11ac physical bitrate and MAC goodput calculations."""

    def setUp(self):
        self.forecaster = SectorCapacityForecaster(default_bw_mhz=20)

    def test_vht_phy_rate_lookup_standard(self):
        """Verify standard 802.11ac PHY rates for 20, 40, and 80 MHz channels."""
        # 20 MHz, 1SS: MCS0=6.5, MCS7=65.0, MCS8=78.0
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(0, 20, 1), 6.5)
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(7, 20, 1), 65.0)
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(8, 20, 1), 78.0)

        # 20 MHz, 2SS: MCS7=130.0, MCS8=156.0
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(7, 20, 2), 130.0)
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(8, 20, 2), 156.0)

        # 40 MHz, 2SS: MCS7=270.0, MCS9=360.0
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(7, 40, 2), 270.0)
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(9, 40, 2), 360.0)

        # 80 MHz, 2SS: MCS7=585.0, MCS9=780.0
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(7, 80, 2), 585.0)
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(9, 80, 2), 780.0)

    def test_vht_phy_rate_short_gi(self):
        """Verify Short Guard Interval (400ns) increases symbol rate by 10/9 (~11.1%)."""
        lgi = SectorCapacityForecaster.calculate_phy_rate_mbps(7, 20, 1, short_gi=False)
        sgi = SectorCapacityForecaster.calculate_phy_rate_mbps(7, 20, 1, short_gi=True)
        self.assertEqual(lgi, 65.0)
        self.assertEqual(sgi, round(65.0 * 10.0 / 9.0, 1))
        self.assertGreater(sgi, lgi)

    def test_phy_rate_clamping(self):
        """Verify invalid or out-of-range inputs clamp gracefully."""
        # MCS < 0 clamps to 0; MCS > 9 clamps to 9
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(-5, 20, 1), 6.5)
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(15, 20, 1), 86.7)

        # Invalid BW defaults to 20 MHz
        self.assertEqual(SectorCapacityForecaster.calculate_phy_rate_mbps(7, 160, 1), 65.0)

    def test_effective_goodput_calculation(self):
        """Verify MAC efficiency (0.72) and PER degradation on delivered goodput."""
        # Clean link: 20MHz 2SS MCS7 (130 Mbps PHY), 0% retries
        clean_gp = self.forecaster.calculate_effective_goodput(mcs=7, bw_mhz=20, nss=2, retry_pct=0.0)
        self.assertEqual(clean_gp, round(130.0 * 0.72, 2))  # 93.6 Mbps

        # Degraded link: 10% retries -> throughput reduced by (1 - 0.10)
        degraded_gp = self.forecaster.calculate_effective_goodput(mcs=7, bw_mhz=20, nss=2, retry_pct=10.0)
        self.assertEqual(degraded_gp, round(130.0 * 0.72 * 0.90, 2))  # 84.24 Mbps
        self.assertLess(degraded_gp, clean_gp)

    def test_airtime_per_megabit(self):
        """Verify airtime calculation is the exact reciprocal of effective goodput."""
        effective_gp = self.forecaster.calculate_effective_goodput(mcs=7, bw_mhz=20, nss=2, retry_pct=0.0)
        at_per_mb = self.forecaster.calculate_airtime_per_megabit_s(mcs=7, bw_mhz=20, nss=2, retry_pct=0.0)
        self.assertAlmostEqual(at_per_mb * effective_gp, 1.0, places=5)

    def test_custom_plan_registration(self):
        """Verify custom plan tier can be registered and retrieved."""
        custom_plan = PlanTier("Gigabit_Trial", down_mbps=1000.0, up_mbps=200.0, concurrency_factor=0.10)
        self.forecaster.register_plan(custom_plan)
        self.assertIn("Gigabit_Trial", self.forecaster.plans)
        self.assertEqual(self.forecaster.plans["Gigabit_Trial"].down_mbps, 1000.0)


class TestSectorCapacityForecasting(unittest.TestCase):
    """Test sector capacity, airtime saturation forecasting, and bottleneck diagnosis."""

    def setUp(self):
        self.forecaster = SectorCapacityForecaster(default_bw_mhz=20, airtime_limit_pct=85.0)

    def test_forecast_empty_sector(self):
        """Empty sector should return 0 airtime, max headroom, and not be exhausted."""
        res = self.forecaster.forecast_sector_capacity([])
        self.assertEqual(res.subscriber_count, 0)
        self.assertEqual(res.active_subscribers, 0)
        self.assertEqual(res.aggregate_goodput_mbps, 0.0)
        self.assertEqual(res.total_airtime_demand_pct, 0.0)
        self.assertEqual(res.is_exhausted, False)
        self.assertEqual(res.remaining_airtime_headroom_pct, 85.0)
        self.assertEqual(len(res.bottlenecks), 0)

    def test_forecast_inactive_subscribers_filtered(self):
        """Subscribers marked active=False should not contribute to airtime demand."""
        subs = [
            SubscriberDemand("cpe-01", plan_name="Standard_25M", mcs=7, nss=2, active=True),
            SubscriberDemand("cpe-02", plan_name="Standard_25M", mcs=7, nss=2, active=False),
        ]
        res = self.forecaster.forecast_sector_capacity(subs)
        self.assertEqual(res.subscriber_count, 2)
        self.assertEqual(res.active_subscribers, 1)
        self.assertGreater(res.total_airtime_demand_pct, 0.0)
        self.assertFalse(res.is_exhausted)

    def test_forecast_uncongested_sector(self):
        """Sector with 4 healthy CPEs on Standard_25M (peak demand 6.25 Mbps each)."""
        subs = [
            SubscriberDemand(f"cpe-{i:02d}", plan_name="Standard_25M", mcs=7, nss=2, retry_pct=1.0)
            for i in range(1, 5)
        ]
        res = self.forecaster.forecast_sector_capacity(subs)
        self.assertEqual(res.active_subscribers, 4)
        # 4 * (25 * 0.25) = 25 Mbps aggregate demanded
        self.assertAlmostEqual(res.aggregate_goodput_mbps, 25.0, delta=0.5)
        # Total airtime should be ~ 27% (well under 85%)
        self.assertLess(res.total_airtime_demand_pct, 85.0)
        self.assertFalse(res.is_exhausted)
        self.assertGreater(res.remaining_airtime_headroom_pct, 50.0)
        self.assertGreater(res.max_admissible_additional_subscribers, 5)

    def test_forecast_airtime_exhaustion_cliff(self):
        """Sector with heavy subscriber load exceeding the 85% CSMA/CA airtime cliff."""
        # 16 subscribers on Pro_50M plan (50 Mbps * 0.30 = 15 Mbps each) at MCS5
        subs = [
            SubscriberDemand(f"cpe-{i:02d}", plan_name="Pro_50M", mcs=5, nss=2, retry_pct=5.0)
            for i in range(1, 17)
        ]
        res = self.forecaster.forecast_sector_capacity(subs)
        self.assertTrue(res.is_exhausted)
        self.assertGreaterEqual(res.total_airtime_demand_pct, 85.0)
        self.assertEqual(res.remaining_airtime_headroom_pct, 0.0)
        self.assertEqual(res.max_admissible_additional_subscribers, 0)

    def test_forecast_saturation_scaling(self):
        """When total airtime demand exceeds 100%, delivered goodput scales down proportionally."""
        # Force huge offered load
        subs = [
            SubscriberDemand("cpe-01", offered_load_mbps=100.0, mcs=1, nss=1, retry_pct=10.0),
            SubscriberDemand("cpe-02", offered_load_mbps=100.0, mcs=1, nss=1, retry_pct=10.0),
        ]
        res = self.forecaster.forecast_sector_capacity(subs)
        self.assertTrue(res.is_exhausted)
        # Airtime demand will exceed 100%
        self.assertGreater(res.total_airtime_demand_pct, 100.0)
        # Delivered goodput should be bounded and scaled down
        self.assertLess(res.aggregate_goodput_mbps, 200.0)

    def test_bottleneck_diagnosis_drag_factor(self):
        """Identify station consuming > 2x airtime relative to its delivered throughput."""
        healthy_subs = [
            SubscriberDemand(f"cpe-clean-{i}", plan_name="Standard_25M", mcs=8, nss=2, retry_pct=1.0)
            for i in range(4)
        ]
        # Drag station: MCS 1 (13 Mbps PHY) demanding 15 Mbps with 15% retries
        drag_sub = SubscriberDemand("cpe-drag-01", offered_load_mbps=15.0, mcs=1, nss=1, retry_pct=15.0)

        res = self.forecaster.forecast_sector_capacity(healthy_subs + [drag_sub])
        self.assertEqual(len(res.bottlenecks), 1)

        b = res.bottlenecks[0]
        self.assertEqual(b.cpe_id, "cpe-drag-01")
        self.assertTrue(b.is_bottleneck)
        self.assertGreater(b.inefficiency_ratio, 2.0)
        self.assertIn("drag factor", b.diagnosis_reason.lower())
        self.assertGreater(b.freed_airtime_pct_if_remediated, 0.0)

    def test_bottleneck_diagnosis_severe_mcs(self):
        """Station with MCS <= 3 is identified as a bottleneck."""
        subs = [
            SubscriberDemand("cpe-fast", plan_name="Standard_25M", mcs=8, nss=2),
            SubscriberDemand("cpe-slow", plan_name="Standard_25M", mcs=2, nss=1),
        ]
        bottlenecks = self.forecaster.identify_bottlenecks(subs)
        flagged_ids = [b.cpe_id for b in bottlenecks]
        self.assertIn("cpe-slow", flagged_ids)
        slow_b = next(b for b in bottlenecks if b.cpe_id == "cpe-slow")
        self.assertIn("severe mcs degradation", slow_b.diagnosis_reason.lower())

    def test_bottleneck_diagnosis_excessive_retries(self):
        """Station with retries >= 12% is identified as a bottleneck."""
        subs = [
            SubscriberDemand("cpe-01", plan_name="Standard_25M", mcs=7, nss=2, retry_pct=1.0),
            SubscriberDemand("cpe-retry", plan_name="Standard_25M", mcs=7, nss=2, retry_pct=18.0),
        ]
        bottlenecks = self.forecaster.identify_bottlenecks(subs)
        flagged_ids = [b.cpe_id for b in bottlenecks]
        self.assertIn("cpe-retry", flagged_ids)
        b = next(b for b in bottlenecks if b.cpe_id == "cpe-retry")
        self.assertIn("excessive retries", b.diagnosis_reason.lower())

    def test_bottleneck_freed_airtime_and_potential_gain(self):
        """Remediating bottlenecks computes quantitative freed airtime and sector capacity gain."""
        subs = [
            SubscriberDemand("cpe-clean-1", plan_name="Standard_25M", mcs=8, nss=2),
            SubscriberDemand("cpe-clean-2", plan_name="Standard_25M", mcs=8, nss=2),
            SubscriberDemand("cpe-degraded", offered_load_mbps=10.0, mcs=1, nss=1, retry_pct=10.0),
        ]
        res = self.forecaster.forecast_sector_capacity(subs)
        self.assertGreater(res.freed_airtime_if_bottlenecks_fixed_pct, 0.0)
        self.assertGreater(res.potential_goodput_gain_mbps, 0.0)


class TestStationAuditor(unittest.TestCase):
    """Test station link auditing for RF imbalances, poor SNR, retries, and receiver overload."""

    def setUp(self):
        self.advisor = SectorAdvisor()

    def test_clean_station_audit(self):
        """Healthy subscriber with balanced chains, high SNR, and low retries passes cleanly."""
        stations = [
            {
                "mac": "00:27:22:AA:BB:CC",
                "cpe_id": "cpe-clean-01",
                "chain0_signal_dbm": -62.0,
                "chain1_signal_dbm": -63.0,
                "signal_dbm": -62.5,
                "noise_floor_dbm": -95.0,
                "tx_retries": 5,
                "tx_packets": 1000,
                "mcs": 8,
            }
        ]
        records = self.advisor.audit_stations(stations)
        self.assertEqual(len(records), 1)
        r = records[0]
        self.assertEqual(r.severity, AuditSeverity.INFO)
        self.assertEqual(len(r.issues), 0)
        self.assertEqual(r.chain_imbalance_db, 1.0)
        self.assertAlmostEqual(r.snr_db, 32.5, delta=0.5)
        self.assertEqual(r.retry_pct, 0.5)

    def test_chain_imbalance_warning_and_critical(self):
        """Chain imbalance > 3.5 dB triggers WARNING; > 6.0 dB triggers CRITICAL."""
        stations = [
            # 4.0 dB delta -> WARNING
            {
                "mac": "00:27:22:11:11:11",
                "cpe_id": "cpe-warn-imbalance",
                "chain0_signal_dbm": -62.0,
                "chain1_signal_dbm": -66.0,
                "signal_dbm": -63.0,
                "noise_floor_dbm": -95.0,
                "tx_retries": 1,
                "tx_packets": 100,
            },
            # 7.5 dB delta -> CRITICAL
            {
                "mac": "00:27:22:22:22:22",
                "cpe_id": "cpe-crit-imbalance",
                "chain0_signal_dbm": -58.0,
                "chain1_signal_dbm": -65.5,
                "signal_dbm": -60.0,
                "noise_floor_dbm": -95.0,
                "tx_retries": 1,
                "tx_packets": 100,
            },
        ]
        records = self.advisor.audit_stations(stations)
        r_warn = records[0]
        r_crit = records[1]

        self.assertEqual(r_warn.severity, AuditSeverity.WARNING)
        self.assertIn("moderate chain imbalance", r_warn.issues[0].lower())

        self.assertEqual(r_crit.severity, AuditSeverity.CRITICAL)
        self.assertIn("severe chain imbalance", r_crit.issues[0].lower())
        self.assertTrue(any("re-alignment" in rec.lower() for rec in r_crit.recommendations))

    def test_receiver_overload_desensitization(self):
        """RSSI >= -45.0 dBm triggers CRITICAL receiver overload advisory."""
        stations = [
            {
                "mac": "00:27:22:33:33:33",
                "cpe_id": "cpe-too-hot",
                "chain0_signal_dbm": -42.0,
                "chain1_signal_dbm": -43.0,
                "signal_dbm": -42.0,
                "noise_floor_dbm": -95.0,
                "tx_retries": 0,
                "tx_packets": 100,
            }
        ]
        records = self.advisor.audit_stations(stations)
        r = records[0]
        self.assertEqual(r.severity, AuditSeverity.CRITICAL)
        self.assertTrue(any("receiver overloaded" in issue.lower() for issue in r.issues))
        self.assertTrue(any("reduce cpe transmit power" in rec.lower() for rec in r.recommendations))

    def test_poor_snr_warning_and_critical(self):
        """SNR <= 22 dB triggers WARNING; SNR <= 16 dB triggers CRITICAL."""
        stations = [
            {
                "mac": "00:27:22:44:44:44",
                "cpe_id": "cpe-subopt-snr",
                "signal_dbm": -75.0,
                "noise_floor_dbm": -95.0,  # SNR = 20 dB
                "chain0_signal_dbm": -75.0,
                "chain1_signal_dbm": -75.0,
                "tx_retries": 0,
                "tx_packets": 100,
            },
            {
                "mac": "00:27:22:55:55:55",
                "cpe_id": "cpe-crit-snr",
                "signal_dbm": -81.0,
                "noise_floor_dbm": -95.0,  # SNR = 14 dB
                "chain0_signal_dbm": -81.0,
                "chain1_signal_dbm": -81.0,
                "tx_retries": 0,
                "tx_packets": 100,
            },
        ]
        records = self.advisor.audit_stations(stations)
        self.assertEqual(records[0].severity, AuditSeverity.WARNING)
        self.assertTrue(any("suboptimal snr" in iss.lower() for iss in records[0].issues))

        self.assertEqual(records[1].severity, AuditSeverity.CRITICAL)
        self.assertTrue(any("critically low snr" in iss.lower() for iss in records[1].issues))

    def test_retry_rate_warning_and_critical(self):
        """Retries >= 15% triggers WARNING; >= 25% triggers CRITICAL."""
        stations = [
            {
                "mac": "00:27:22:66:66:66",
                "cpe_id": "cpe-warn-retries",
                "signal_dbm": -65.0,
                "noise_floor_dbm": -95.0,
                "tx_retries": 18,
                "tx_packets": 100,  # 18%
            },
            {
                "mac": "00:27:22:77:77:77",
                "cpe_id": "cpe-crit-retries",
                "signal_dbm": -65.0,
                "noise_floor_dbm": -95.0,
                "tx_retries": 30,
                "tx_packets": 100,  # 30%
            },
        ]
        records = self.advisor.audit_stations(stations)
        self.assertEqual(records[0].severity, AuditSeverity.WARNING)
        self.assertEqual(records[1].severity, AuditSeverity.CRITICAL)


class TestRFAdvisories(unittest.TestCase):
    """Test channel selection, width optimization, and TX power balancing advisories."""

    def setUp(self):
        self.advisor = SectorAdvisor()

    def test_recommend_channel_cleaner_frequency(self):
        """Recommends cleaner candidate channel if penalty is >20% lower than current."""
        spectral_data = {
            5500: {"noise_floor_dbm": -85.0, "peak_interference_dbm": -70.0, "channel_occupancy_pct": 65.0},
            5540: {"noise_floor_dbm": -94.0, "peak_interference_dbm": -90.0, "channel_occupancy_pct": 5.0},
        }
        adv = self.advisor.recommend_channel(current_freq_mhz=5500, spectral_data=spectral_data)
        self.assertEqual(adv.category, "CHANNEL")
        self.assertEqual(adv.recommended_value, 5540)
        self.assertIn(adv.priority, (AuditSeverity.WARNING, AuditSeverity.CRITICAL))
        self.assertIn("cleaner", adv.expected_benefit.lower())

    def test_recommend_channel_dfs_radar_avoidance(self):
        """Candidate channels with active DFS radar pulses must be bypassed."""
        spectral_data = {
            5500: {"noise_floor_dbm": -88.0, "peak_interference_dbm": -80.0, "channel_occupancy_pct": 40.0},
            5520: {
                "noise_floor_dbm": -96.0,
                "peak_interference_dbm": -95.0,
                "channel_occupancy_pct": 0.0,
                "dfs_radar_detected": True,  # Active radar!
            },
            5560: {"noise_floor_dbm": -94.0, "peak_interference_dbm": -92.0, "channel_occupancy_pct": 8.0},
        }
        adv = self.advisor.recommend_channel(current_freq_mhz=5500, spectral_data=spectral_data)
        # Must select 5560, NOT the radar-contaminated 5520
        self.assertEqual(adv.recommended_value, 5560)

    def test_recommend_channel_stay_on_optimal(self):
        """If current channel is already clean, recommend staying on current frequency."""
        spectral_data = {
            5500: {"noise_floor_dbm": -95.0, "peak_interference_dbm": -92.0, "channel_occupancy_pct": 5.0},
            5520: {"noise_floor_dbm": -93.0, "peak_interference_dbm": -90.0, "channel_occupancy_pct": 15.0},
        }
        adv = self.advisor.recommend_channel(current_freq_mhz=5500, spectral_data=spectral_data)
        self.assertEqual(adv.recommended_value, 5500)
        self.assertEqual(adv.priority, AuditSeverity.INFO)

    def test_recommend_channel_width_drop_under_interference(self):
        """40 MHz channel under high occupancy (>50%) recommends downscaling to 20 MHz."""
        adv = self.advisor.recommend_channel_width(
            current_width_mhz=40,
            spectral_occupancy_pct=60.0,
            avg_snr_db=24.0,
            noise_floor_dbm=-86.0,
        )
        self.assertEqual(adv.category, "CHANNEL_WIDTH")
        self.assertEqual(adv.recommended_value, 20)
        self.assertEqual(adv.priority, AuditSeverity.WARNING)
        self.assertIn("+3 db snr gain", adv.expected_benefit.lower())

    def test_recommend_channel_width_expand_in_clean_spectrum(self):
        """20 MHz channel in clean spectrum (<25% occupancy, SNR >= 28 dB) recommends expanding to 40 MHz."""
        adv = self.advisor.recommend_channel_width(
            current_width_mhz=20,
            spectral_occupancy_pct=10.0,
            avg_snr_db=32.0,
            noise_floor_dbm=-94.0,
        )
        self.assertEqual(adv.category, "CHANNEL_WIDTH")
        self.assertEqual(adv.recommended_value, 40)
        self.assertEqual(adv.priority, AuditSeverity.INFO)
        self.assertIn("doubles", adv.expected_benefit.lower())

    def test_recommend_tx_power_balancing(self):
        """Back off overpowered stations (> -48 dBm) and boost underpowered stations (< 25 dB SNR)."""
        stations = [
            # Overpowered: RSSI -42 dBm, TX power 20 dBm
            {
                "mac": "00:27:22:AA:01:01",
                "signal_dbm": -42.0,
                "noise_floor_dbm": -95.0,
                "tx_power_dbm": 20.0,
            },
            # Underpowered: SNR = 18 dB (-77 - (-95)), TX power 18 dBm
            {
                "mac": "00:27:22:BB:02:02",
                "signal_dbm": -77.0,
                "noise_floor_dbm": -95.0,
                "tx_power_dbm": 18.0,
            },
        ]
        advs = self.advisor.recommend_tx_power(stations)
        self.assertEqual(len(advs), 2)

        # Overpowered station should be backed off
        adv_hot = next(a for a in advs if a.target == "00:27:22:AA:01:01")
        self.assertLess(adv_hot.recommended_value, 20.0)
        self.assertIn("mitigate evm distortion", adv_hot.expected_benefit.lower())

        # Underpowered station should be boosted
        adv_weak = next(a for a in advs if a.target == "00:27:22:BB:02:02")
        self.assertGreater(adv_weak.recommended_value, 18.0)
        self.assertIn("gain", adv_weak.expected_benefit.lower())

    def test_full_advisory_report(self):
        """Verify full structured advisory report aggregates audits and advisories."""
        stations = [
            {
                "mac": "00:27:22:10:00:01",
                "cpe_id": "cpe-1",
                "chain0_signal_dbm": -60.0,
                "chain1_signal_dbm": -67.0,  # 7.0 dB imbalance -> CRITICAL
                "signal_dbm": -62.0,
                "noise_floor_dbm": -95.0,
                "tx_retries": 2,
                "tx_packets": 100,
            }
        ]
        spectral_data = {
            5500: {"noise_floor_dbm": -95.0, "peak_interference_dbm": -92.0, "channel_occupancy_pct": 5.0}
        }
        report = self.advisor.generate_full_advisory_report(
            stations=stations,
            current_freq_mhz=5500,
            current_width_mhz=20,
            spectral_data=spectral_data,
        )
        self.assertEqual(report["station_count"], 1)
        self.assertIn("00:27:22:10:00:01", report["critical_stations"])
        self.assertGreaterEqual(report["actionable_advisories_count"], 1)


class TestJainsFairness(unittest.TestCase):
    """Test Jain's Fairness Index computation."""

    def test_perfect_fairness(self):
        """Identical allocations yield exactly 1.0."""
        self.assertEqual(calculate_jains_fairness([10.0, 10.0, 10.0, 10.0]), 1.0)
        self.assertEqual(calculate_jains_fairness({"cpe1": 25.0, "cpe2": 25.0}), 1.0)

    def test_skewed_allocation(self):
        """Asymmetric allocations yield expected fairness value."""
        # 1 user gets 90, other user gets 10
        # (100)^2 / (2 * (90^2 + 10^2)) = 10000 / (2 * (8100 + 100)) = 10000 / 16400 = 0.6098
        fairness = calculate_jains_fairness([90.0, 10.0])
        self.assertEqual(fairness, 0.6098)

    def test_empty_or_zero(self):
        """Empty or all-zero allocations return 1.0 without dividing by zero."""
        self.assertEqual(calculate_jains_fairness([]), 1.0)
        self.assertEqual(calculate_jains_fairness([0.0, 0.0]), 1.0)


class TestCanaryManager(unittest.TestCase):
    """Test CanaryManager trial staging, causal impact evaluation, and rollback guard."""

    def setUp(self):
        self.manager = CanaryManager(
            max_acceptable_goodput_drop_pct=-10.0,
            max_acceptable_latency_increase_pct=20.0,
            max_acceptable_fairness_drop=0.15,
        )

    def test_stage_canary(self):
        """Staging initializes trial with active status and stores baseline metrics."""
        trial = self.manager.stage_canary(
            parameter_name="channel_width",
            old_value=20,
            new_value=40,
            before_metrics={"goodput_mbps": 45.0, "latency_p95_ms": 15.0, "resets": 0},
        )
        self.assertTrue(trial.trial_id.startswith("canary-"))
        self.assertEqual(trial.status, "TRIAL_ACTIVE")
        self.assertEqual(trial.before_metrics["goodput_mbps"], 45.0)

    def test_evaluate_successful_trial(self):
        """Trial with higher goodput and lower latency is ACCEPTED (KEEP)."""
        trial = self.manager.stage_canary(
            parameter_name="tx_power",
            old_value=18,
            new_value=21,
            before_metrics={
                "goodput_mbps": 50.0,
                "latency_p95_ms": 20.0,
                "per_station_goodputs": [25.0, 25.0],
                "resets": 0,
            },
        )
        after_metrics = {
            "goodput_mbps": 60.0,  # +20% gain
            "latency_p95_ms": 18.0,  # -10% latency
            "per_station_goodputs": [30.0, 30.0],
            "resets": 0,
        }
        res = self.manager.evaluate_canary(trial, after_metrics)
        self.assertEqual(res.decision, "KEEP")
        self.assertEqual(res.status, "ACCEPTED")
        self.assertAlmostEqual(res.goodput_delta_pct, 20.0, delta=0.1)
        self.assertAlmostEqual(res.latency_p95_delta_pct, -10.0, delta=0.1)

    def test_evaluate_revert_on_goodput_drop(self):
        """Trial resulting in > 10% goodput collapse triggers REVERT."""
        trial = self.manager.stage_canary(
            parameter_name="frequency",
            old_value=5500,
            new_value=5560,
            before_metrics={"goodput_mbps": 50.0, "latency_p95_ms": 15.0},
        )
        after_metrics = {
            "goodput_mbps": 40.0,  # -20% drop (< -10% threshold)
            "latency_p95_ms": 16.0,
        }
        res = self.manager.evaluate_canary(trial, after_metrics)
        self.assertEqual(res.decision, "REVERT")
        self.assertEqual(res.status, "REVERTED")
        self.assertTrue(any("goodput dropped" in reason.lower() for reason in res.decision_reason.split("|")))

    def test_evaluate_revert_on_latency_spike(self):
        """Trial resulting in > 20% loaded p95 latency degradation triggers REVERT."""
        trial = self.manager.stage_canary(
            parameter_name="aggregation_ampdu",
            old_value=32,
            new_value=64,
            before_metrics={"goodput_mbps": 50.0, "latency_p95_ms": 15.0},
        )
        after_metrics = {
            "goodput_mbps": 52.0,
            "latency_p95_ms": 25.0,  # +66.7% latency spike (> 20% threshold)
        }
        res = self.manager.evaluate_canary(trial, after_metrics)
        self.assertEqual(res.decision, "REVERT")
        self.assertEqual(res.status, "REVERTED")
        self.assertIn("loaded p95 latency", res.decision_reason.lower())

    def test_evaluate_revert_on_fairness_drop(self):
        """Trial starving some stations and dropping Jain fairness by > 0.15 triggers REVERT."""
        trial = self.manager.stage_canary(
            parameter_name="rate_mask",
            old_value="auto",
            new_value="vht-fixed",
            before_metrics={
                "goodput_mbps": 50.0,
                "latency_p95_ms": 15.0,
                "per_station_goodputs": [25.0, 25.0],  # Fairness = 1.0
            },
        )
        after_metrics = {
            "goodput_mbps": 52.0,
            "latency_p95_ms": 15.0,
            "per_station_goodputs": [48.0, 4.0],  # Fairness ~ 0.58 (drop > 0.40)
        }
        res = self.manager.evaluate_canary(trial, after_metrics)
        self.assertEqual(res.decision, "REVERT")
        self.assertEqual(res.status, "REVERTED")
        self.assertIn("fairness degraded", res.decision_reason.lower())

    def test_evaluate_revert_on_firmware_resets(self):
        """Trial triggering radio firmware resets or link disconnections triggers REVERT."""
        trial = self.manager.stage_canary(
            parameter_name="channel_width",
            old_value=20,
            new_value=80,
            before_metrics={"goodput_mbps": 50.0, "latency_p95_ms": 15.0, "resets": 0},
        )
        after_metrics = {
            "goodput_mbps": 55.0,
            "latency_p95_ms": 16.0,
            "resets": 2,  # Resets occurred!
        }
        res = self.manager.evaluate_canary(trial, after_metrics)
        self.assertEqual(res.decision, "REVERT")
        self.assertEqual(res.status, "REVERTED")
        self.assertIn("resets or association loss", res.decision_reason.lower())


if __name__ == "__main__":
    unittest.main()
