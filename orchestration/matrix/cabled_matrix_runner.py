"""Cabled RF Attenuation Matrix test runner for Tier 1 lab testbed (Decision D-0010).

Summary: Orchestrates deterministic benchtop coaxial experiments using stepped or
programmable SMA attenuators and Wilkinson power splitters. Maps target outdoor distances
to equivalent RF attenuation via Free Space Path Loss (FSPL), executes traffic sweeps,
and records comprehensive multi-station performance curves.
Keywords: cabled matrix, benchtop lab, FSPL, attenuation sweep, D-0010, Tier 1, rate curves.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


SPEED_OF_LIGHT = 299792458.0  # m/s


@dataclass
class ChannelAttenuationStep:
    step_id: int
    equivalent_distance_meters: float
    total_attenuation_db: float
    expected_rssi_dbm: float
    measured_rssi_dbm: float = 0.0
    aggregate_goodput_mbps: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    packet_loss_pct: float = 0.0
    retry_rate: float = 0.0
    mcs_distribution: Dict[int, int] = field(default_factory=dict)
    is_link_established: bool = False


@dataclass
class MatrixExperimentConfig:
    experiment_id: str
    frequency_mhz: int = 5180
    ap_tx_power_dbm: float = 20.0
    ap_antenna_gain_dbi: float = 16.0  # LAP-120 / LAP-GPS sector gain
    cpe_antenna_gain_dbi: float = 23.0  # LiteBeam 5AC Gen2 dish gain
    cable_splitter_loss_db: float = 8.0  # Fixed loss from coax, adapters, and splitters
    target_distances_meters: List[float] = field(
        default_factory=lambda: [100.0, 500.0, 1000.0, 2500.0, 5000.0, 10000.0]
    )
    workload_duration_seconds: float = 10.0


@dataclass
class MatrixExperimentReport:
    config: MatrixExperimentConfig
    steps: List[ChannelAttenuationStep] = field(default_factory=list)
    max_clean_distance_meters: float = 0.0
    throughput_half_life_meters: float = 0.0
    is_fully_executed: bool = False


class CabledMatrixRunner:
    """Manages coaxial RF matrix attenuation configuration and multi-distance testing."""

    @classmethod
    def calculate_fspl_db(cls, distance_meters: float, frequency_mhz: float) -> float:
        """Calculates Free Space Path Loss in dB."""
        if distance_meters <= 0:
            return 0.0
        # FSPL(dB) = 20*log10(d) + 20*log10(f_Hz) - 147.55
        freq_hz = frequency_mhz * 1e6
        fspl = 20.0 * math.log10(distance_meters) + 20.0 * math.log10(freq_hz) - 147.55
        return round(max(0.0, fspl), 2)

    @classmethod
    def calculate_required_matrix_attenuation(
        cls,
        distance_meters: float,
        frequency_mhz: float,
        fixed_bench_loss_db: float = 8.0,
    ) -> float:
        """Determines the programmable attenuator setting (dB) required to simulate a distance."""
        fspl = cls.calculate_fspl_db(distance_meters, frequency_mhz)
        # Attenuator setting = Path Loss - Fixed bench hardware losses
        attenuator_db = max(0.0, fspl - fixed_bench_loss_db)
        return round(attenuator_db, 1)

    @classmethod
    def calculate_expected_rssi(
        cls,
        tx_power_dbm: float,
        tx_gain_dbi: float,
        rx_gain_dbi: float,
        total_attenuation_db: float,
    ) -> float:
        """Computes expected receiver RSSI in dBm."""
        # RSSI = TX_power + TX_gain + RX_gain - total_loss
        rssi = tx_power_dbm + tx_gain_dbi + rx_gain_dbi - total_attenuation_db
        return round(rssi, 1)

    def __init__(self, config: MatrixExperimentConfig):
        self.config = config

    def plan_attenuation_steps(self) -> List[ChannelAttenuationStep]:
        """Prepares the planned sweep steps from target distances."""
        steps: List[ChannelAttenuationStep] = []
        for idx, dist in enumerate(self.config.target_distances_meters):
            fspl = self.calculate_fspl_db(dist, self.config.frequency_mhz)
            matrix_att = self.calculate_required_matrix_attenuation(
                dist, self.config.frequency_mhz, self.config.cable_splitter_loss_db
            )
            total_loss = matrix_att + self.config.cable_splitter_loss_db
            expected_rssi = self.calculate_expected_rssi(
                self.config.ap_tx_power_dbm,
                self.config.ap_antenna_gain_dbi,
                self.config.cpe_antenna_gain_dbi,
                total_loss,
            )
            step = ChannelAttenuationStep(
                step_id=idx + 1,
                equivalent_distance_meters=dist,
                total_attenuation_db=total_loss,
                expected_rssi_dbm=expected_rssi,
            )
            steps.append(step)
        return steps

    def run_sweep(
        self,
        set_hardware_attenuation_fn: Optional[Callable[[float], bool]] = None,
        traffic_benchmark_fn: Optional[Callable[[ChannelAttenuationStep], Dict[str, float]]] = None,
    ) -> MatrixExperimentReport:
        """Executes the stepped attenuation experiment loop."""
        steps = self.plan_attenuation_steps()
        max_clean_dist = 0.0

        for step in steps:
            # 1. Apply hardware attenuation
            if set_hardware_attenuation_fn:
                ok = set_hardware_attenuation_fn(step.total_attenuation_db)
                if not ok:
                    step.is_link_established = False
                    continue

            # 2. Run benchmark workload
            if traffic_benchmark_fn:
                results = traffic_benchmark_fn(step)
                step.measured_rssi_dbm = results.get("measured_rssi", step.expected_rssi_dbm)
                step.aggregate_goodput_mbps = results.get("goodput_mbps", 0.0)
                step.p50_latency_ms = results.get("p50_ms", 0.0)
                step.p95_latency_ms = results.get("p95_ms", 0.0)
                step.p99_latency_ms = results.get("p99_ms", 0.0)
                step.packet_loss_pct = results.get("loss_pct", 0.0)
                step.retry_rate = results.get("retry_rate", 0.0)
                step.is_link_established = results.get("is_up", True)
            else:
                # Default synthetic physics calculation if no hardware callback provided
                step.measured_rssi_dbm = step.expected_rssi_dbm
                step.is_link_established = step.expected_rssi_dbm > -88.0
                if step.is_link_established:
                    # Model realistic 802.11ac goodput dropoff with distance
                    if step.expected_rssi_dbm >= -62.0:
                        step.aggregate_goodput_mbps = 95.0
                    elif step.expected_rssi_dbm >= -72.0:
                        step.aggregate_goodput_mbps = 75.0
                    elif step.expected_rssi_dbm >= -80.0:
                        step.aggregate_goodput_mbps = 45.0
                    else:
                        step.aggregate_goodput_mbps = 15.0
                    step.p99_latency_ms = 15.0 if step.expected_rssi_dbm >= -70.0 else 45.0
                else:
                    step.aggregate_goodput_mbps = 0.0
                    step.packet_loss_pct = 100.0

            if step.is_link_established and step.aggregate_goodput_mbps > 50.0:
                max_clean_dist = max(max_clean_dist, step.equivalent_distance_meters)

        return MatrixExperimentReport(
            config=self.config,
            steps=steps,
            max_clean_distance_meters=max_clean_dist,
            is_fully_executed=True,
        )
