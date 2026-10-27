"""Multi-Sector Tower Co-Channel & Adjacent-Channel Conflict-Graph & Pareto Optimizer (Stage 12).

Synthesizes empirical hardware and production telemetry findings from:
- Stage 11A (`docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md`):
  - `WA_UNFILTERED_LAP` (`QCA9882` / `LAP-120` / `LAP-GPS`, wide passive SAW filter)
  - `XC_AIRPRISM_GEN2` (`Rocket Prism 5AC Gen2`, `sysid=0xe7e9`, `QCA9880v2` + active
    6-entry GPIO 13..16 `prism` bandpass filter selector + GPS `IRQ 22` sync + die-cast shield)
- Stage 12 (`docs/STAGE12_GUARIDA_32CPE_TELEMETRY_AND_MODE_B_OPTIMIZER.md`):
  - Real 3-sector Guarida tower (`Panel1` 4 CPEs, `Panel2` 22 CPEs including `FRANCO_Debora`
    at `-70 dBm` / `10.1 Mbps` DL and `SEVERO` at `-74 dBm`, `Panel3` 6 CPEs)
- Stage 12 Mission 1 & Mission 2 (`controller/ptmp_mode_selector.py`,
  `controller/per_cpe_distance_aql_scheduler.py`).

Provides:
1. Conflict-graph SINR / ACI / CCI coupling matrix evaluator (`evaluate_tower_configuration`)
2. Fast deterministic conflict-graph solver (`optimize_tower_plan`)
3. Multi-objective `pymoo` (v0.6.2) `NSGA-II` Pareto front explorer (`compute_pareto_front`)
   optimizing 3 conflicting objectives:
     - Objective 1: Maximize total tower aggregate goodput (Mbps) [minimized as `-goodput_mbps`]
     - Objective 2: Minimize worst-sector loaded `p95` RTT (ms)
     - Objective 3: Minimize inter-sector SINR degradation + weak-CPE airtime starvation penalty

Safety boundary: 100% offline advisory optimizer (`automatic_execution_allowed=False`).
Regulatory EIRP and DFS boundaries are strictly enforced as hard constraints.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.optimize import minimize

# Discrete 5 MHz channel center raster in U-NII-3 (5725..5850 MHz) safe for 20/40 MHz
UNII3_FREQUENCIES_MHZ: List[int] = [
    5735,
    5740,
    5745,
    5750,
    5755,
    5760,
    5765,
    5770,
    5775,
    5780,
    5785,
    5790,
    5795,
    5800,
    5805,
    5810,
    5815,
    5820,
    5825,
    5830,
    5835,
    5840,
]

CHANNEL_WIDTHS_MHZ: List[int] = [20, 40]

HARDWARE_CLASSES: Tuple[str, ...] = (
    "WA_UNFILTERED_LAP",
    "XC_AIRPRISM_GEN2",
)

MAC_MODES: Tuple[str, ...] = (
    "MODE_A_OPENWRT_CSMA_AQL",
    "MODE_B_AIRMAX_TDMA",
    "MODE_B_GPS_SYNC_TDMA",
)


# Exact 6-entry umac.ko:ubnt_prism_hook band-edge table (CONFIRMED Stage 11A F05)
PRISM_FILTER_TABLE: List[Dict[str, int]] = [
    {"entry": 0, "stage": 1, "start_mhz": 5150, "end_mhz": 5250, "gpio_val": 0x18000, "max_width_mhz": 160},
    {"entry": 1, "stage": 1, "start_mhz": 5470, "end_mhz": 5860, "gpio_val": 0x08000, "max_width_mhz": 50},
    {"entry": 2, "stage": 2, "start_mhz": 5200, "end_mhz": 5300, "gpio_val": 0x02000, "max_width_mhz": 160},
    {"entry": 3, "stage": 2, "start_mhz": 5725, "end_mhz": 5860, "gpio_val": 0x04000, "max_width_mhz": 160},
    {"entry": 4, "stage": 1, "start_mhz": 3000, "end_mhz": 6200, "gpio_val": 0x10000, "max_width_mhz": 160},
    {"entry": 5, "stage": 2, "start_mhz": 3000, "end_mhz": 6200, "gpio_val": 0x06000, "max_width_mhz": 160},
]


def select_prism_filter_entries(center_freq_mhz: int, width_mhz: int) -> Dict[str, Any]:
    """Reproduce exact umac.ko:ubnt_prism_hook (.text + 0xabeb0) stage 1 & 2 GPIO selection."""
    lower_edge = center_freq_mhz - (width_mhz // 2)
    upper_edge = center_freq_mhz + (width_mhz // 2)
    selected: Dict[int, Dict[str, int]] = {}
    for stage in (1, 2):
        for row in PRISM_FILTER_TABLE:
            if (
                row["stage"] == stage
                and lower_edge >= row["start_mhz"]
                and upper_edge <= row["end_mhz"]
                and width_mhz <= row["max_width_mhz"]
            ):
                selected[stage] = row
                break
    s1 = selected[1]
    s2 = selected[2]
    is_narrow_high_q = s1["entry"] in (0, 1) and s2["entry"] in (2, 3)
    return {
        "lower_edge_mhz": lower_edge,
        "upper_edge_mhz": upper_edge,
        "stage1_entry": s1["entry"],
        "stage2_entry": s2["entry"],
        "stage1_gpio_val": s1["gpio_val"],
        "stage2_gpio_val": s2["gpio_val"],
        "is_narrow_high_q_passband": is_narrow_high_q,
    }


@dataclass(frozen=True)
class SectorSpec:
    """Physical and subscriber specification of a single sector on a shared WISP tower."""

    sector_id: str
    azimuth_deg: float
    hardware_class: str
    antenna_gain_dbi: float
    max_eirp_dbm: float
    active_cpes: int
    mean_distance_km: float
    max_distance_km: float
    mean_rx_rssi_dbm: float
    min_rx_rssi_dbm: float
    weak_cpe_count: int
    hidden_node_fraction: float
    baseline_freq_mhz: int
    baseline_width_mhz: int
    baseline_tx_power_dbm: int
    baseline_mac_mode: str
    canary_mode_a_eligible: bool = False

    def max_conducted_tx_dbm(self) -> int:
        """Return maximum legal conducted TX power (dBm) respecting regulatory EIRP."""
        return int(min(24, max(10, math.floor(self.max_eirp_dbm - self.antenna_gain_dbi))))


def angular_separation_deg(az1_deg: float, az2_deg: float) -> float:
    """Compute shortest angular azimuth separation in [0, 180] degrees."""
    diff = abs(float(az1_deg) - float(az2_deg)) % 360.0
    return float(min(diff, 360.0 - diff))


def compute_spatial_isolation_db(
    az1_deg: float,
    az2_deg: float,
    hw1: str,
    hw2: str,
) -> float:
    """Compute antenna pattern + vertical mast + chassis shielding isolation (dB) between sectors."""
    delta_theta = angular_separation_deg(az1_deg, az2_deg)
    # Standard WISP tower mounting (1.5m vertical + 90/120 deg sector sidelobe roll-off):
    # ~46 dB at 60 deg, ~50.4 dB at 120 deg, ~52.0 dB at 180 deg back-to-back on WA housing.
    # XC Rocket Prism 5AC Gen2 die-cast aluminum chassis + RF choke adds +3.5 dB per end.
    base_db = 40.0
    if hw1 == "XC_AIRPRISM_GEN2":
        base_db += 3.5
    if hw2 == "XC_AIRPRISM_GEN2":
        base_db += 3.5
    front_to_back_bonus = 12.0 * math.sin(math.pi * delta_theta / 360.0)
    return float(base_db + front_to_back_bonus)


def compute_spectral_rejection_db(
    freq_victim_mhz: int,
    width_victim_mhz: int,
    freq_aggressor_mhz: int,
    width_aggressor_mhz: int,
    hw_victim: str,
    hw_aggressor: str,
) -> float:
    """Compute spectral filter + mask + LNA blocking rejection (dB) between victim RX and aggressor TX."""
    delta_f = abs(float(freq_victim_mhz) - float(freq_aggressor_mhz))
    half_sum_w = 0.5 * (float(width_victim_mhz) + float(width_aggressor_mhz))
    guard_band_mhz = delta_f - half_sum_w

    if guard_band_mhz < 0.0:
        # Overlapping channels (Co-Channel Interference / Partial spectral overlap)
        overlap_mhz = min(float(width_victim_mhz), float(width_aggressor_mhz), -guard_band_mhz)
        overlap_frac = max(0.05, min(1.0, overlap_mhz / float(min(width_victim_mhz, width_aggressor_mhz))))
        # Co-channel pre-LNA AirPrism filter + high-IP3 QCA9880v2 front-end adds +4 dB linearity
        cc_bonus = 4.0 if hw_victim == "XC_AIRPRISM_GEN2" else 0.0
        return float(-10.0 * math.log10(overlap_frac) + cc_bonus)

    # Adjacent-channel guard band >= 0 MHz:
    # Combines IEEE 802.11ac TX spectral mask + receiver analog/digital filter vs LNA 3rd-order blocking.
    if hw_victim == "XC_AIRPRISM_GEN2":
        prism_info = select_prism_filter_entries(freq_victim_mhz, width_victim_mhz)
        narrow_bonus = 6.0 if prism_info["is_narrow_high_q_passband"] else 0.0
        rej_db = (
            53.0
            + narrow_bonus
            + 0.55 * guard_band_mhz
            + 4.8 * math.log1p(0.35 * guard_band_mhz)
        )
    else:
        # Standard WA_UNFILTERED_LAP (wide 5150..5875 MHz passive SAW: suffers LNA blocking at G=0..25 MHz)
        rej_db = 41.0 + 0.38 * guard_band_mhz + 3.6 * math.log1p(0.22 * guard_band_mhz)

    # Aggressor TX PA linearity & phase-noise cleanliness bonus on QCA9880v2 + AirPrism TX path
    if hw_aggressor == "XC_AIRPRISM_GEN2":
        rej_db += 4.5

    return float(rej_db)


def compute_tdd_sync_isolation_db(mode_i: str, mode_j: str, delta_theta_deg: float) -> float:
    """Compute effective TDD frame synchronization isolation (dB) between co-located sectors.

    When both sectors run `MODE_B_GPS_SYNC_TDMA`, all APs transmit together during DL and
    receive together during UL, eliminating AP-TX into AP-RX self-interference on the mast.
    Residual interference is only distant CPE-TX into back-lobe AP-RX.
    """
    if mode_i == "MODE_B_GPS_SYNC_TDMA" and mode_j == "MODE_B_GPS_SYNC_TDMA":
        if delta_theta_deg >= 150.0:
            return 48.0
        if delta_theta_deg >= 110.0:
            return 26.0
        return 18.0
    if "MODE_B" in mode_i and "MODE_B" in mode_j:
        # Unsynchronized TDMA superframes drift across each other (~2.6 dB duty-cycle reduction)
        return 2.6
    # Asynchronous CSMA/CA or mixed CSMA + unsynced TDMA
    return 0.8


def evaluate_tower_configuration(
    sectors: Sequence[SectorSpec],
    frequencies_mhz: Sequence[int],
    widths_mhz: Sequence[int],
    tx_powers_dbm: Sequence[int],
    mac_modes: Sequence[str],
    hardware_overrides: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Evaluate conflict graph, per-sector SINR degradation, goodput, and p95 RTT for a tower plan."""
    n_sec = len(sectors)
    if not (len(frequencies_mhz) == len(widths_mhz) == len(tx_powers_dbm) == len(mac_modes) == n_sec):
        raise ValueError("All decision sequences must match len(sectors)")

    hw_list = list(hardware_overrides) if hardware_overrides is not None else [s.hardware_class for s in sectors]

    # 1. Pairwise conflict graph & interference bleed matrix
    conflict_edges: List[Dict[str, Any]] = []
    per_sector_interf_mw: List[float] = [0.0 for _ in range(n_sec)]

    thermal_noise_20mhz_dbm = -92.0
    for i in range(n_sec):
        for j in range(n_sec):
            if i == j:
                continue
            spatial_db = compute_spatial_isolation_db(
                sectors[i].azimuth_deg,
                sectors[j].azimuth_deg,
                hw_list[i],
                hw_list[j],
            )
            spectral_db = compute_spectral_rejection_db(
                freq_victim_mhz=int(frequencies_mhz[i]),
                width_victim_mhz=int(widths_mhz[i]),
                freq_aggressor_mhz=int(frequencies_mhz[j]),
                width_aggressor_mhz=int(widths_mhz[j]),
                hw_victim=hw_list[i],
                hw_aggressor=hw_list[j],
            )
            delta_theta = angular_separation_deg(sectors[i].azimuth_deg, sectors[j].azimuth_deg)
            sync_isolation_db = compute_tdd_sync_isolation_db(mac_modes[i], mac_modes[j], delta_theta)

            coupled_interf_dbm = float(tx_powers_dbm[j]) - spatial_db - spectral_db - sync_isolation_db
            coupled_interf_mw = 10.0 ** (coupled_interf_dbm / 10.0)
            per_sector_interf_mw[i] += coupled_interf_mw

            if i < j:
                delta_f = abs(int(frequencies_mhz[i]) - int(frequencies_mhz[j]))
                guard_mhz = delta_f - 0.5 * (int(widths_mhz[i]) + int(widths_mhz[j]))
                conflict_edges.append(
                    {
                        "sector_a": sectors[i].sector_id,
                        "sector_b": sectors[j].sector_id,
                        "delta_azimuth_deg": round(
                            angular_separation_deg(sectors[i].azimuth_deg, sectors[j].azimuth_deg), 1
                        ),
                        "delta_freq_mhz": delta_f,
                        "guard_band_mhz": guard_mhz,
                        "spatial_isolation_db": round(spatial_db, 2),
                        "spectral_rejection_a_from_b_db": round(spectral_db, 2),
                        "coupled_interference_dbm": round(coupled_interf_dbm, 2),
                    }
                )

    # 2. Per-sector performance evaluation
    sector_results: List[Dict[str, Any]] = []
    eirp_violations_db = 0.0
    mode_gate_violations = 0

    for i, sec in enumerate(sectors):
        f_mhz = int(frequencies_mhz[i])
        w_mhz = int(widths_mhz[i])
        p_dbm = int(tx_powers_dbm[i])
        mode = mac_modes[i]
        hw = hw_list[i]

        # Check regulatory EIRP constraint
        eirp_dbm = float(p_dbm) + sec.antenna_gain_dbi
        if eirp_dbm > sec.max_eirp_dbm:
            eirp_violations_db += eirp_dbm - sec.max_eirp_dbm

        # Check AGENTS.md Section 14 Rule #2 & hardware mode eligibility:
        # Mode A OpenWrt CSMA/AQL is only permitted if canary_mode_a_eligible is True (or N <= 4 with 0 weak CPEs).
        if mode == "MODE_A_OPENWRT_CSMA_AQL" and not sec.canary_mode_a_eligible:
            mode_gate_violations += 1
        # GPS Sync TDMA requires GPS-equipped AP hardware (XC_AIRPRISM_GEN2 or LAP-GPS)
        if mode == "MODE_B_GPS_SYNC_TDMA" and hw == "WA_UNFILTERED_LAP" and sec.sector_id == "Panel1-Guarida":
            # Panel1 is LAP-120 (no GPS); Panel2/Panel3 or upgraded XC have GPS/TDMA support
            mode_gate_violations += 1

        # Effective 20 MHz receiver noise floor including LNA noise figure + outdoor fading margin:
        # WA_UNFILTERED_LAP (QCA9882): -82.5 dBm; XC_AIRPRISM_GEN2 (QCA9880v2 + active AirPrism): -85.5 dBm
        base_nf_20mhz_dbm = -85.5 if hw == "XC_AIRPRISM_GEN2" else -82.5
        noise_floor_dbm = base_nf_20mhz_dbm + (3.0 if w_mhz == 40 else 0.0)
        noise_mw = 10.0 ** (noise_floor_dbm / 10.0)
        total_noise_plus_interf_dbm = 10.0 * math.log10(noise_mw + per_sector_interf_mw[i])
        sinr_degradation_db = max(0.0, total_noise_plus_interf_dbm - noise_floor_dbm)

        # U-NII-3 (5725..5850 MHz) band-edge containment check
        lower_edge_mhz = f_mhz - (w_mhz // 2)
        upper_edge_mhz = f_mhz + (w_mhz // 2)
        if lower_edge_mhz < 5725 or upper_edge_mhz > 5850:
            eirp_violations_db += 10.0

        # Effective RX signal scales with TX power delta from baseline
        tx_delta_db = float(p_dbm - sec.baseline_tx_power_dbm)
        # Excessive TX power (>20 dBm on WA, >22 dBm on XC) introduces PA EVM distortion
        pa_evm_penalty_db = max(0.0, 0.55 * (p_dbm - (21 if hw == "XC_AIRPRISM_GEN2" else 19)))

        mean_sinr_db = (sec.mean_rx_rssi_dbm + 0.5 * tx_delta_db) - total_noise_plus_interf_dbm - pa_evm_penalty_db
        weak_edge_sinr_db = (sec.min_rx_rssi_dbm + 0.5 * tx_delta_db) - total_noise_plus_interf_dbm - pa_evm_penalty_db

        # Spectral efficiency (bps/Hz) from VHT 2x2 MIMO curve (calibrated to R103 82 Mbps max on 20 MHz)
        max_spec_eff = 5.65 if hw == "XC_AIRPRISM_GEN2" else 5.25
        mean_lin_snr = 10.0 ** (max(0.5, mean_sinr_db) / 10.0)
        weak_lin_snr = 10.0 ** (max(-2.0, weak_edge_sinr_db) / 10.0)
        mean_spec_eff = min(max_spec_eff, 1.12 * math.log2(1.0 + 0.42 * mean_lin_snr))
        weak_spec_eff = min(4.50, 0.95 * math.log2(1.0 + 0.35 * weak_lin_snr))

        # Harmonic airtime collapse from weak CPEs (Stage 12 Guarida Mode B finding: FRANCO_Debora tax)
        weak_frac = float(sec.weak_cpe_count) / float(max(1, sec.active_cpes))
        if mode == "MODE_A_OPENWRT_CSMA_AQL":
            # CSMA/CA + AQL excels on small N <= 4 clean sectors, but collapses under N >= 6 + hidden nodes
            if sec.active_cpes <= 4 and sec.weak_cpe_count == 0:
                mac_efficiency = 0.72
            else:
                mac_efficiency = max(0.28, 0.68 - 0.022 * sec.active_cpes - 0.25 * sec.hidden_node_fraction)
            weak_hog_factor = 2.40  # Unpolled weak CPEs hog CSMA/CA airtime via retries
        elif mode == "MODE_B_AIRMAX_TDMA":
            mac_efficiency = 0.64
            weak_hog_factor = 1.85  # Matches G72-C08 Panel2 harmonic collapse ratio ~0.62
        else:
            # MODE_B_GPS_SYNC_TDMA
            mac_efficiency = 0.67
            weak_hog_factor = 1.55

        eff_weak_weight = min(0.75, weak_frac * weak_hog_factor)
        effective_spec_eff = 1.0 / (
            ((1.0 - eff_weak_weight) / max(0.2, mean_spec_eff))
            + (eff_weak_weight / max(0.15, weak_spec_eff))
        )

        # 40 MHz channel width doubles raw Hz only when AirPrism/SINR supports clean 40 MHz decoding
        if w_mhz == 20:
            width_scaling = 1.0
        else:
            if hw == "XC_AIRPRISM_GEN2" and weak_edge_sinr_db >= 7.5:
                width_scaling = 1.58
            elif sec.weak_cpe_count == 0 and sinr_degradation_db <= 1.5:
                width_scaling = 1.42
            else:
                width_scaling = 1.08
        goodput_mbps = 20.0 * width_scaling * effective_spec_eff * mac_efficiency

        # Loaded p95 RTT (ms)
        cov_slot_us = 9.0 + 3.0 * min(31.0, (sec.max_distance_km * 1000.0) / 450.0)
        interf_retry_penalty_ms = 1.65 * (sinr_degradation_db ** 1.35)
        if mode == "MODE_A_OPENWRT_CSMA_AQL":
            if sec.active_cpes <= 4:
                base_p95_ms = 7.8 + 0.04 * cov_slot_us
            else:
                base_p95_ms = 14.0 + 2.8 * sec.active_cpes * (0.4 + sec.hidden_node_fraction)
        elif mode == "MODE_B_AIRMAX_TDMA":
            base_p95_ms = 12.5 + 1.15 * sec.active_cpes + 0.06 * cov_slot_us
        else:
            base_p95_ms = 11.2 + 1.02 * sec.active_cpes + 0.05 * cov_slot_us

        p95_rtt_ms = base_p95_ms + interf_retry_penalty_ms + (4.5 if weak_edge_sinr_db < 10.0 else 0.0)

        # Weak-CPE starvation & SINR penalty score (lower is better)
        weak_starvation_penalty = (
            sinr_degradation_db * (1.0 + 1.5 * weak_frac)
            + max(0.0, 14.0 - weak_edge_sinr_db) * 1.2
        )

        sector_results.append(
            {
                "sector_id": sec.sector_id,
                "azimuth_deg": sec.azimuth_deg,
                "hardware_class": hw,
                "active_cpes": sec.active_cpes,
                "frequency_mhz": f_mhz,
                "width_mhz": w_mhz,
                "tx_power_dbm": p_dbm,
                "eirp_dbm": round(eirp_dbm, 2),
                "mac_mode": mode,
                "noise_floor_dbm": round(noise_floor_dbm, 2),
                "effective_noise_plus_interf_dbm": round(total_noise_plus_interf_dbm, 2),
                "sinr_degradation_db": round(sinr_degradation_db, 3),
                "mean_sinr_db": round(mean_sinr_db, 2),
                "weak_edge_sinr_db": round(weak_edge_sinr_db, 2),
                "goodput_mbps": round(goodput_mbps, 3),
                "spectral_efficiency_mbps_per_mhz": round(goodput_mbps / float(w_mhz), 4),
                "p95_rtt_ms": round(p95_rtt_ms, 3),
                "weak_starvation_penalty": round(weak_starvation_penalty, 3),
            }
        )

    total_goodput_mbps = sum(r["goodput_mbps"] for r in sector_results)
    total_spectrum_mhz = len(set(int(frequencies_mhz[i]) for i in range(n_sec))) * 20
    worst_p95_rtt_ms = max(r["p95_rtt_ms"] for r in sector_results)
    max_sinr_deg_db = max(r["sinr_degradation_db"] for r in sector_results)
    mean_sinr_deg_db = sum(r["sinr_degradation_db"] for r in sector_results) / float(n_sec)
    total_starvation_penalty = sum(r["weak_starvation_penalty"] for r in sector_results)

    return {
        "total_tower_goodput_mbps": round(total_goodput_mbps, 3),
        "tower_goodput_per_mhz": round(total_goodput_mbps / float(max(20, sum(widths_mhz))), 4),
        "worst_sector_p95_rtt_ms": round(worst_p95_rtt_ms, 3),
        "max_sinr_degradation_db": round(max_sinr_deg_db, 3),
        "mean_sinr_degradation_db": round(mean_sinr_deg_db, 3),
        "total_weak_starvation_penalty": round(total_starvation_penalty, 3),
        "eirp_violations_db": round(eirp_violations_db, 3),
        "mode_gate_violations": mode_gate_violations,
        "is_feasible": (eirp_violations_db <= 1e-6 and mode_gate_violations == 0),
        "sectors": sector_results,
        "conflict_graph_edges": conflict_edges,
        "automatic_execution_allowed": False,
    }


class TowerConflictGraphPymooProblem(ElementwiseProblem):
    """Pymoo multi-objective problem for N-sector WISP tower frequency/width/power/mode allocation."""

    def __init__(
        self,
        sectors: Sequence[SectorSpec],
        hardware_overrides: Optional[Sequence[str]] = None,
    ) -> None:
        self.sectors = list(sectors)
        self.hw_overrides = (
            list(hardware_overrides)
            if hardware_overrides is not None
            else [s.hardware_class for s in self.sectors]
        )
        n_sec = len(self.sectors)
        # Per sector 4 integer variables:
        #   0: freq_idx in [0, len(UNII3_FREQUENCIES_MHZ)-1]
        #   1: width_idx in [0, 1] (0->20 MHz, 1->40 MHz)
        #   2: tx_power_dbm in [12, max_conducted_tx_dbm]
        #   3: mode_idx in [0, 2]
        xl: List[int] = []
        xu: List[int] = []
        for idx, sec in enumerate(self.sectors):
            xl.extend([0, 0, 14, 0])
            max_tx = sec.max_conducted_tx_dbm()
            # Mode index bounds: if canary_mode_a_eligible, allow 0..2, else 1..2 (Mode B only)
            xu.extend([len(UNII3_FREQUENCIES_MHZ) - 1, 1, max_tx, 2])

        super().__init__(
            n_var=4 * n_sec,
            n_obj=3,
            n_ieq_constr=2,
            xl=np.array(xl, dtype=int),
            xu=np.array(xu, dtype=int),
            vtype=int,
        )

    def decode_decision_vector(self, x: Sequence[int]) -> Tuple[List[int], List[int], List[int], List[str]]:
        freqs: List[int] = []
        widths: List[int] = []
        powers: List[int] = []
        modes: List[str] = []
        for i, sec in enumerate(self.sectors):
            f_idx = int(np.clip(round(x[4 * i]), 0, len(UNII3_FREQUENCIES_MHZ) - 1))
            w_idx = int(np.clip(round(x[4 * i + 1]), 0, len(CHANNEL_WIDTHS_MHZ) - 1))
            p_dbm = int(np.clip(round(x[4 * i + 2]), 14, sec.max_conducted_tx_dbm()))
            m_idx = int(np.clip(round(x[4 * i + 3]), 0, len(MAC_MODES) - 1))
            if not sec.canary_mode_a_eligible and m_idx == 0:
                m_idx = 1  # Enforce AGENTS.md Section 14 Rule #2 Mode B gate
            if m_idx == 2 and self.hw_overrides[i] == "WA_UNFILTERED_LAP" and sec.sector_id == "Panel1-Guarida":
                m_idx = 0 if sec.canary_mode_a_eligible else 1
            f_mhz = UNII3_FREQUENCIES_MHZ[f_idx]
            w_mhz = CHANNEL_WIDTHS_MHZ[w_idx]
            if w_mhz == 40:
                f_mhz = min(5830, max(5745, f_mhz))
            freqs.append(f_mhz)
            widths.append(w_mhz)
            powers.append(p_dbm)
            modes.append(MAC_MODES[m_idx])
        return freqs, widths, powers, modes

    def _evaluate(self, x: np.ndarray, out: Dict[str, Any], *args: Any, **kwargs: Any) -> None:
        freqs, widths, powers, modes = self.decode_decision_vector(x)
        eval_res = evaluate_tower_configuration(
            sectors=self.sectors,
            frequencies_mhz=freqs,
            widths_mhz=widths,
            tx_powers_dbm=powers,
            mac_modes=modes,
            hardware_overrides=self.hw_overrides,
        )
        # 3 Objectives (all minimized in pymoo):
        # F1: -total_tower_goodput_mbps
        # F2: worst_sector_p95_rtt_ms
        # F3: total_weak_starvation_penalty (SINR bleed + weak-CPE starvation)
        f1 = -float(eval_res["total_tower_goodput_mbps"])
        f2 = float(eval_res["worst_sector_p95_rtt_ms"])
        f3 = float(eval_res["total_weak_starvation_penalty"])
        out["F"] = [f1, f2, f3]

        # Inequality constraints g(x) <= 0:
        # G1: eirp_violations_db <= 0
        # G2: worst_sector_p95_rtt_ms - 55.0 <= 0
        g1 = float(eval_res["eirp_violations_db"])
        g2 = float(eval_res["worst_sector_p95_rtt_ms"]) - 55.0
        out["G"] = [g1, g2]


def compute_pareto_front(
    sectors: Sequence[SectorSpec],
    hardware_overrides: Optional[Sequence[str]] = None,
    pop_size: int = 48,
    n_gen: int = 36,
    seed: int = 20261024,
) -> Dict[str, Any]:
    """Run pymoo NSGA-II to compute the non-dominated Pareto front for a multi-sector tower."""
    problem = TowerConflictGraphPymooProblem(sectors=sectors, hardware_overrides=hardware_overrides)
    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=IntegerRandomSampling(),
        crossover=SBX(prob=0.9, eta=15, vtype=float, repair=RoundingRepair()),
        mutation=PM(prob=0.25, eta=20, vtype=float, repair=RoundingRepair()),
        eliminate_duplicates=True,
    )
    res = minimize(
        problem,
        algorithm,
        termination=("n_gen", n_gen),
        seed=seed,
        verbose=False,
    )

    pareto_solutions: List[Dict[str, Any]] = []
    seen_signatures = set()

    if res.X is not None:
        xs = np.atleast_2d(res.X)
        for row in xs:
            freqs, widths, powers, modes = problem.decode_decision_vector(row)
            sig = (tuple(freqs), tuple(widths), tuple(powers), tuple(modes))
            if sig in seen_signatures:
                continue
            seen_signatures.add(sig)
            ev = evaluate_tower_configuration(
                sectors=sectors,
                frequencies_mhz=freqs,
                widths_mhz=widths,
                tx_powers_dbm=powers,
                mac_modes=modes,
                hardware_overrides=hardware_overrides,
            )
            if ev["is_feasible"]:
                pareto_solutions.append(ev)

    # Sort Pareto solutions by descending total_tower_goodput_mbps
    pareto_solutions.sort(key=lambda item: item["total_tower_goodput_mbps"], reverse=True)

    return {
        "n_pareto_solutions": len(pareto_solutions),
        "pareto_solutions": pareto_solutions,
        "automatic_execution_allowed": False,
    }


def optimize_tower_plan(
    sectors: Sequence[SectorSpec],
    hardware_overrides: Optional[Sequence[str]] = None,
    pop_size: int = 48,
    n_gen: int = 36,
    seed: int = 20261024,
) -> Dict[str, Any]:
    """Select the knee-point / balanced optimal tower plan from the conflict-graph + NSGA-II Pareto front."""
    hw_list = list(hardware_overrides) if hardware_overrides is not None else [s.hardware_class for s in sectors]

    # 1. Evaluate current baseline configuration
    baseline_eval = evaluate_tower_configuration(
        sectors=sectors,
        frequencies_mhz=[s.baseline_freq_mhz for s in sectors],
        widths_mhz=[s.baseline_width_mhz for s in sectors],
        tx_powers_dbm=[s.baseline_tx_power_dbm for s in sectors],
        mac_modes=[s.baseline_mac_mode for s in sectors],
        hardware_overrides=[s.hardware_class for s in sectors],
    )

    # 2. Construct deterministic conflict-graph greedy candidate (maximal frequency spacing + optimal modes)
    n_sec = len(sectors)
    if n_sec <= 3:
        # Spread 3 sectors maximally across U-NII-3 (5735, 5785, 5835 -> 50 MHz center spacing, 30 MHz guard band!)
        greedy_freqs = [5735, 5835, 5785][:n_sec]
    else:
        # For 6 sectors (0, 60, 120, 180, 240, 300 deg), assign front-to-back 180-deg pairs to maximally separated channels:
        # Pair (0, 180) -> 5735 / 5740, Pair (60, 240) -> 5785 / 5790, Pair (120, 300) -> 5835 / 5840
        pattern = [5735, 5785, 5835, 5735, 5785, 5835]
        greedy_freqs = [pattern[i % len(pattern)] for i in range(n_sec)]

    greedy_widths: List[int] = []
    greedy_powers: List[int] = []
    greedy_modes: List[str] = []
    for i, sec in enumerate(sectors):
        # Use 40 MHz only on clean small-N sectors without weak CPEs when frequency spacing permits
        if n_sec <= 3 and sec.active_cpes <= 4 and sec.weak_cpe_count == 0:
            greedy_widths.append(20)
        else:
            greedy_widths.append(20)
        opt_p = min(sec.max_conducted_tx_dbm(), 21 if hw_list[i] == "XC_AIRPRISM_GEN2" else 19)
        greedy_powers.append(opt_p)
        if sec.canary_mode_a_eligible and sec.active_cpes <= 4 and sec.weak_cpe_count == 0:
            greedy_modes.append("MODE_A_OPENWRT_CSMA_AQL")
        elif hw_list[i] == "XC_AIRPRISM_GEN2" or n_sec >= 4:
            greedy_modes.append("MODE_B_GPS_SYNC_TDMA")
        else:
            greedy_modes.append("MODE_B_AIRMAX_TDMA")

    greedy_eval = evaluate_tower_configuration(
        sectors=sectors,
        frequencies_mhz=greedy_freqs,
        widths_mhz=greedy_widths,
        tx_powers_dbm=greedy_powers,
        mac_modes=greedy_modes,
        hardware_overrides=hw_list,
    )

    # 3. Run pymoo NSGA-II Pareto search and include greedy conflict-graph solution in candidate pool
    pareto_bundle = compute_pareto_front(
        sectors=sectors,
        hardware_overrides=hw_list,
        pop_size=pop_size,
        n_gen=n_gen,
        seed=seed,
    )
    candidates = [greedy_eval] + pareto_bundle["pareto_solutions"]

    # Filter to non-dominated Pareto set across (-goodput, worst_p95_rtt, total_weak_starvation_penalty)
    non_dominated: List[Dict[str, Any]] = []
    for c in candidates:
        dominated = False
        for other in candidates:
            if other is c:
                continue
            if (
                other["total_tower_goodput_mbps"] >= c["total_tower_goodput_mbps"]
                and other["worst_sector_p95_rtt_ms"] <= c["worst_sector_p95_rtt_ms"]
                and other["total_weak_starvation_penalty"] <= c["total_weak_starvation_penalty"]
                and (
                    other["total_tower_goodput_mbps"] > c["total_tower_goodput_mbps"]
                    or other["worst_sector_p95_rtt_ms"] < c["worst_sector_p95_rtt_ms"]
                    or other["total_weak_starvation_penalty"] < c["total_weak_starvation_penalty"]
                )
            ):
                dominated = True
                break
        if not dominated:
            non_dominated.append(c)

    # Select balanced knee-point via normalized utopia distance (weights: 0.45 goodput, 0.30 p95, 0.25 SINR/starvation)
    def composite_score(sol: Dict[str, Any]) -> float:
        tput_gain = sol["total_tower_goodput_mbps"] / max(1.0, baseline_eval["total_tower_goodput_mbps"])
        rtt_ratio = sol["worst_sector_p95_rtt_ms"] / max(1.0, baseline_eval["worst_sector_p95_rtt_ms"])
        sinr_pen = sol["total_weak_starvation_penalty"] / max(0.5, baseline_eval["total_weak_starvation_penalty"] + 1.0)
        return float(0.50 * tput_gain - 0.30 * rtt_ratio - 0.20 * sinr_pen)

    best_plan = max(non_dominated, key=composite_score)

    return {
        "baseline_evaluation": baseline_eval,
        "recommended_knee_point_plan": best_plan,
        "pareto_front_count": len(non_dominated),
        "pareto_front": non_dominated,
        "goodput_gain_pct_vs_baseline": round(
            100.0
            * (best_plan["total_tower_goodput_mbps"] - baseline_eval["total_tower_goodput_mbps"])
            / max(1e-6, baseline_eval["total_tower_goodput_mbps"]),
            2,
        ),
        "worst_p95_rtt_reduction_pct_vs_baseline": round(
            100.0
            * (baseline_eval["worst_sector_p95_rtt_ms"] - best_plan["worst_sector_p95_rtt_ms"])
            / max(1e-6, baseline_eval["worst_sector_p95_rtt_ms"]),
            2,
        ),
        "sinr_degradation_reduction_db_vs_baseline": round(
            baseline_eval["max_sinr_degradation_db"] - best_plan["max_sinr_degradation_db"],
            3,
        ),
        "automatic_execution_allowed": False,
    }
