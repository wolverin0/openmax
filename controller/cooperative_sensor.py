"""Cooperative CPE Sensor, Airtime Tax Detector, Relay Break-Even Gate & Spatial Fault Localizer.

Implements the deterministic control-plane models specified in:
- docs/COOPERATIVE_CPE_FEASIBILITY.md (Section 2.A.4 Two-Hop Relay Break-Even Equation)
- docs/WISP_EDGE_SCRIPTS_AND_INTELLIGENCE.md (Sections 2.1 and 2.2)

All algorithms are pure, deterministic, and side-effect-free for offline sector analysis
and closed-loop controller gating.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence


# Fault localization classification labels
SECTOR_WIDE_OR_BACKHAUL_FAULT = "SECTOR_WIDE_OR_BACKHAUL_FAULT"
ANGULAR_RF_INTERFERENCE_CLUSTER = "ANGULAR_RF_INTERFERENCE_CLUSTER"
CPE_CHAIN_IMBALANCE_OR_MISALIGNMENT = "CPE_CHAIN_IMBALANCE_OR_MISALIGNMENT"
CPE_ETHERNET_POE_CABLE_FAULT = "CPE_ETHERNET_POE_CABLE_FAULT"
HEALTHY = "HEALTHY"


@dataclass(frozen=True)
class CpeTelemetrySample:
    """Per-CPE telemetry snapshot collected from Sector AP + optional CPE heartbeat."""

    cpe_id: str
    mac: str
    azimuth_deg: float = 0.0
    distance_m: float = 500.0
    # Useful payload bytes transferred during the measurement window
    useful_bytes: int = 0
    # Measured airtime in microseconds (if reported by airOS wstalist or ath10k-ct)
    measured_airtime_us: Optional[int] = None
    # Fallback estimation inputs when WMI_SERVICE_REPORT_AIRTIME is absent (QCA988x Wave-1)
    last_tx_bitrate_mbps: float = 0.0
    tx_retry_ratio: float = 0.0
    be_deficit_us: int = 0
    # RF signal metrics
    rssi_dbm: float = -55.0
    baseline_rssi_dbm: Optional[float] = None
    cinr_db: float = 25.0
    baseline_cinr_db: Optional[float] = None
    chain0_dbm: Optional[float] = None
    chain1_dbm: Optional[float] = None
    # Network / QoE metrics
    rtt_p95_ms: float = 5.0
    packet_loss_pct: float = 0.0
    # Customer LAN / PoE interface telemetry (eth0)
    eth_speed_mbps: int = 100
    eth_duplex: str = "full"
    eth_carrier_flaps: int = 0
    eth_crc_errors: int = 0

    def effective_airtime_us(self) -> float:
        """Return measured airtime (us) or retry-inflated QCA988x Wave-1 estimate.

        Per knowledge/QCA988X_CONTROL_BOUNDARY.md, when last_tx_bitrate is 0 on
        QCA988x (peer stats disabled), mainline ath10k falls back to 6 Mbps.
        Here we also inflate estimated airtime by (1 + tx_retry_ratio) and account
        for deep negative mac80211 BE deficit from Stage 7.4.
        """
        if self.measured_airtime_us is not None and self.measured_airtime_us > 0:
            return float(self.measured_airtime_us)

        rate_mbps = self.last_tx_bitrate_mbps if self.last_tx_bitrate_mbps > 0.0 else 6.0
        retry_multiplier = 1.0 + max(0.0, self.tx_retry_ratio)
        base_us = (float(max(0, self.useful_bytes)) * 8.0 / rate_mbps) * retry_multiplier
        if self.be_deficit_us < 0:
            base_us += float(abs(self.be_deficit_us))
        return base_us


@dataclass(frozen=True)
class AirtimeTaxResult:
    """Computed Airtime Tax metrics and hog classification for a single CPE."""

    cpe_id: str
    mac: str
    airtime_us: float
    useful_bytes: int
    airtime_share: float
    useful_byte_share: float
    airtime_tax_ratio: float
    is_airtime_hog: bool
    used_6mbps_fallback_warning: bool
    reason: str


@dataclass(frozen=True)
class RelayFeasibilityResult:
    """Evaluation of the 5 GHz same-channel two-hop relay break-even equation."""

    approved: bool
    direct_airtime_ms_per_mbit: float
    relay_airtime_ms_per_mbit: float
    effective_relay_rate_mbps: float
    airtime_savings_pct: float
    speedup_ratio: float
    reason: str


@dataclass(frozen=True)
class FaultLocalizationReport:
    """Result of spatial differential fault localization across a sector."""

    sector_classification: str
    affected_cpe_ids: List[str]
    per_cpe_classifications: Dict[str, str]
    angular_cluster_center_deg: Optional[float] = None
    recommended_action: str = ""
    evidence: Dict[str, object] = field(default_factory=dict)


def compute_airtime_tax(
    samples: Sequence[CpeTelemetrySample],
    tax_ratio_threshold: float = 2.5,
    min_airtime_share: float = 0.15,
    be_deficit_hog_threshold_us: int = -15000,
) -> List[AirtimeTaxResult]:
    """Compute per-CPE Airtime Tax Ratio (airtime_share / useful_byte_share).

    Flags a station as an airtime hog when its airtime_tax_ratio >= tax_ratio_threshold
    and its airtime_share >= min_airtime_share (or when its mac80211 Deficit: BE
    is deeper than be_deficit_hog_threshold_us while consuming >= min_airtime_share).
    """
    if not samples:
        return []

    airtimes = [max(0.0, s.effective_airtime_us()) for s in samples]
    total_airtime = sum(airtimes)
    total_bytes = sum(max(0, s.useful_bytes) for s in samples)

    results: List[AirtimeTaxResult] = []
    for sample, air_us in zip(samples, airtimes):
        air_share = (air_us / total_airtime) if total_airtime > 0.0 else 0.0
        byte_share = (
            (max(0, sample.useful_bytes) / float(total_bytes))
            if total_bytes > 0
            else 0.0
        )

        if byte_share > 0.0:
            tax_ratio = air_share / byte_share
        elif air_share > 0.0:
            tax_ratio = float("inf")
        else:
            tax_ratio = 1.0

        used_fallback = (
            sample.measured_airtime_us is None
            and sample.last_tx_bitrate_mbps <= 0.0
            and sample.useful_bytes > 0
        )

        is_hog_by_ratio = (
            tax_ratio >= tax_ratio_threshold and air_share >= min_airtime_share
        )
        is_hog_by_deficit = (
            sample.be_deficit_us <= be_deficit_hog_threshold_us
            and air_share >= min_airtime_share
        )
        is_hog = bool(is_hog_by_ratio or is_hog_by_deficit)

        reasons: List[str] = []
        if is_hog_by_ratio:
            reasons.append(
                f"airtime_tax_ratio={tax_ratio:.2f}>={tax_ratio_threshold:.2f} "
                f"(airtime_share={air_share:.2%}, byte_share={byte_share:.2%})"
            )
        if is_hog_by_deficit:
            reasons.append(
                f"deep_negative_be_deficit={sample.be_deficit_us}us<={be_deficit_hog_threshold_us}us"
            )
        if used_fallback:
            reasons.append("warning:last_tx_bitrate=0_6mbps_fallback")
        if not reasons:
            reasons.append("normal_airtime_efficiency")

        results.append(
            AirtimeTaxResult(
                cpe_id=sample.cpe_id,
                mac=sample.mac,
                airtime_us=air_us,
                useful_bytes=sample.useful_bytes,
                airtime_share=air_share,
                useful_byte_share=byte_share,
                airtime_tax_ratio=tax_ratio,
                is_airtime_hog=is_hog,
                used_6mbps_fallback_warning=used_fallback,
                reason="; ".join(reasons),
            )
        )

    return results


def evaluate_relay_feasibility(
    r_b_ap_mbps: float,
    r_b_a_mbps: float,
    r_a_ap_mbps: float,
    rssi_b_a_dbm: float,
    overhead_factor: float = 1.25,
    min_rssi_b_a_dbm: float = -68.0,
    min_airtime_savings_pct: float = 15.0,
) -> RelayFeasibilityResult:
    """Evaluate the 5 GHz same-channel two-hop relay break-even condition.

    Equation (docs/COOPERATIVE_CPE_FEASIBILITY.md Section 2.A.4):
        T_direct = 1 / R_direct(B->AP)
        T_relay  = overhead_factor * (1 / R(B->A) + 1 / R(A->AP))

    Relaying B -> A -> AP is approved if and only if:
      1) All link rates are strictly positive and overhead_factor >= 1.0,
      2) Local sidelobe/inter-CPE link RSSI >= min_rssi_b_a_dbm (-68 dBm default),
      3) T_relay < T_direct with at least min_airtime_savings_pct net sector airtime saved.
    """
    if r_b_ap_mbps <= 0.0 or r_b_a_mbps <= 0.0 or r_a_ap_mbps <= 0.0:
        return RelayFeasibilityResult(
            approved=False,
            direct_airtime_ms_per_mbit=float("inf"),
            relay_airtime_ms_per_mbit=float("inf"),
            effective_relay_rate_mbps=0.0,
            airtime_savings_pct=0.0,
            speedup_ratio=0.0,
            reason="REJECT: non-positive link rate input",
        )

    gamma = max(1.0, float(overhead_factor))
    direct_ms_per_mbit = 1000.0 / r_b_ap_mbps
    relay_ms_per_mbit = gamma * (1000.0 / r_b_a_mbps + 1000.0 / r_a_ap_mbps)
    eff_relay_mbps = 1000.0 / relay_ms_per_mbit
    airtime_savings_pct = (
        (direct_ms_per_mbit - relay_ms_per_mbit) / direct_ms_per_mbit
    ) * 100.0
    speedup_ratio = eff_relay_mbps / r_b_ap_mbps

    if rssi_b_a_dbm < min_rssi_b_a_dbm:
        return RelayFeasibilityResult(
            approved=False,
            direct_airtime_ms_per_mbit=direct_ms_per_mbit,
            relay_airtime_ms_per_mbit=relay_ms_per_mbit,
            effective_relay_rate_mbps=eff_relay_mbps,
            airtime_savings_pct=airtime_savings_pct,
            speedup_ratio=speedup_ratio,
            reason=(
                f"REJECT: inter-CPE sidelobe RSSI {rssi_b_a_dbm:.1f} dBm < "
                f"minimum gate {min_rssi_b_a_dbm:.1f} dBm"
            ),
        )

    if airtime_savings_pct < min_airtime_savings_pct:
        return RelayFeasibilityResult(
            approved=False,
            direct_airtime_ms_per_mbit=direct_ms_per_mbit,
            relay_airtime_ms_per_mbit=relay_ms_per_mbit,
            effective_relay_rate_mbps=eff_relay_mbps,
            airtime_savings_pct=airtime_savings_pct,
            speedup_ratio=speedup_ratio,
            reason=(
                f"REJECT: relay costs {relay_ms_per_mbit:.1f} ms/Mbit vs direct "
                f"{direct_ms_per_mbit:.1f} ms/Mbit (savings {airtime_savings_pct:.1f}% < "
                f"{min_airtime_savings_pct:.1f}% gate)"
            ),
        )

    return RelayFeasibilityResult(
        approved=True,
        direct_airtime_ms_per_mbit=direct_ms_per_mbit,
        relay_airtime_ms_per_mbit=relay_ms_per_mbit,
        effective_relay_rate_mbps=eff_relay_mbps,
        airtime_savings_pct=airtime_savings_pct,
        speedup_ratio=speedup_ratio,
        reason=(
            f"APPROVE: relay cuts airtime by {airtime_savings_pct:.1f}% "
            f"({direct_ms_per_mbit:.1f} -> {relay_ms_per_mbit:.1f} ms/Mbit, "
            f"{speedup_ratio:.2f}x effective rate gain)"
        ),
    )


def _angular_distance_deg(a_deg: float, b_deg: float) -> float:
    """Return shortest angular distance in degrees on [0, 180]."""
    diff = abs((a_deg % 360.0) - (b_deg % 360.0)) % 360.0
    return 360.0 - diff if diff > 180.0 else diff


def _angular_span_deg(angles_deg: Sequence[float]) -> float:
    """Return minimum circular arc in degrees covering all angles."""
    if len(angles_deg) <= 1:
        return 0.0
    norm = sorted((a % 360.0) for a in angles_deg)
    max_gap = 0.0
    for idx in range(len(norm)):
        nxt = norm[(idx + 1) % len(norm)]
        gap = (nxt - norm[idx]) % 360.0
        if len(norm) == 2 and idx == 1:
            gap = (norm[0] + 360.0 - norm[1]) % 360.0
        if gap > max_gap:
            max_gap = gap
    return max(0.0, 360.0 - max_gap)


def localize_sector_faults(
    samples: Sequence[CpeTelemetrySample],
    chain_imbalance_threshold_db: float = 6.0,
    cinr_drop_threshold_db: float = 6.0,
    low_cinr_threshold_db: float = 16.0,
    high_rtt_threshold_ms: float = 35.0,
    packet_loss_threshold_pct: float = 3.0,
    max_interference_wedge_deg: float = 35.0,
) -> FaultLocalizationReport:
    """Perform spatial differential fault localization across a sector's CPEs.

    Classifies the sector and individual CPEs into one of five states:
      1. SECTOR_WIDE_OR_BACKHAUL_FAULT
      2. ANGULAR_RF_INTERFERENCE_CLUSTER
      3. CPE_ETHERNET_POE_CABLE_FAULT
      4. CPE_CHAIN_IMBALANCE_OR_MISALIGNMENT
      5. HEALTHY
    """
    if not samples:
        return FaultLocalizationReport(
            sector_classification=HEALTHY,
            affected_cpe_ids=[],
            per_cpe_classifications={},
            recommended_action="No CPE samples provided.",
        )

    n_total = len(samples)
    per_cpe: Dict[str, str] = {s.cpe_id: HEALTHY for s in samples}

    # 1. Check for sector-wide / backhaul degradation:
    # >= 70% of CPEs (and at least 2 CPEs when n >= 2) experience high RTT or packet loss
    qoe_degraded = [
        s
        for s in samples
        if s.rtt_p95_ms >= high_rtt_threshold_ms
        or s.packet_loss_pct >= packet_loss_threshold_pct
    ]
    rf_degraded = []
    for s in samples:
        cinr_drop = (
            (s.baseline_cinr_db - s.cinr_db)
            if s.baseline_cinr_db is not None
            else 0.0
        )
        if s.cinr_db <= low_cinr_threshold_db or cinr_drop >= cinr_drop_threshold_db:
            rf_degraded.append(s)

    if n_total >= 2 and len(qoe_degraded) >= max(2, int(0.7 * n_total)):
        qoe_span = _angular_span_deg([s.azimuth_deg for s in qoe_degraded])
        # If QoE degradation spans a wide sector arc (> max_interference_wedge_deg)
        # or RF RSSI/CINR is intact across most degraded nodes -> backhaul/AP fault
        if qoe_span > max_interference_wedge_deg or len(rf_degraded) < len(qoe_degraded):
            affected = [s.cpe_id for s in qoe_degraded]
            for cid in affected:
                per_cpe[cid] = SECTOR_WIDE_OR_BACKHAUL_FAULT
            return FaultLocalizationReport(
                sector_classification=SECTOR_WIDE_OR_BACKHAUL_FAULT,
                affected_cpe_ids=affected,
                per_cpe_classifications=per_cpe,
                recommended_action=(
                    "Inspect POP backhaul link, switch port errors, or Sector AP CPU/queue saturation; "
                    "do not dispatch subscriber truck rolls."
                ),
                evidence={
                    "qoe_degraded_count": len(qoe_degraded),
                    "total_cpes": n_total,
                    "azimuth_span_deg": round(qoe_span, 2),
                },
            )

    # 2. Check for localized angular RF interference cluster:
    # >= 2 CPEs suffer simultaneous RF CINR drop / low CINR within a narrow angular wedge (<= 35 deg)
    # while at least 1 CPE outside the wedge on the same sector remains healthy.
    if len(rf_degraded) >= 2 and len(rf_degraded) < n_total:
        rf_angles = [s.azimuth_deg for s in rf_degraded]
        wedge_span = _angular_span_deg(rf_angles)
        if wedge_span <= max_interference_wedge_deg:
            affected = [s.cpe_id for s in rf_degraded]
            for cid in affected:
                per_cpe[cid] = ANGULAR_RF_INTERFERENCE_CLUSTER
            center_deg = sum(s.azimuth_deg for s in rf_degraded) / float(len(rf_degraded))
            return FaultLocalizationReport(
                sector_classification=ANGULAR_RF_INTERFERENCE_CLUSTER,
                affected_cpe_ids=affected,
                per_cpe_classifications=per_cpe,
                angular_cluster_center_deg=round(center_deg, 2),
                recommended_action=(
                    f"Directional RF interferer detected along bearing ~{center_deg:.1f} deg "
                    f"(wedge {wedge_span:.1f} deg). Run AirView/spectral scan or shift channel/subband."
                ),
                evidence={
                    "rf_degraded_cpes": affected,
                    "wedge_span_deg": round(wedge_span, 2),
                    "cluster_center_deg": round(center_deg, 2),
                },
            )

    # 3. Evaluate individual CPE faults (Ethernet/PoE fault vs Chain-Imbalance/Misalignment)
    eth_fault_ids: List[str] = []
    chain_fault_ids: List[str] = []

    for s in samples:
        has_eth_fault = (
            (0 < s.eth_speed_mbps < 100)
            or (s.eth_duplex.lower() != "full")
            or (s.eth_carrier_flaps >= 3)
            or (s.eth_crc_errors >= 10)
        )
        chain_delta = (
            abs(s.chain0_dbm - s.chain1_dbm)
            if (s.chain0_dbm is not None and s.chain1_dbm is not None)
            else 0.0
        )
        rssi_drop = (
            (s.baseline_rssi_dbm - s.rssi_dbm)
            if s.baseline_rssi_dbm is not None
            else 0.0
        )
        cinr_drop = (
            (s.baseline_cinr_db - s.cinr_db)
            if s.baseline_cinr_db is not None
            else 0.0
        )
        has_rf_alignment_fault = (
            chain_delta >= chain_imbalance_threshold_db
            or rssi_drop >= cinr_drop_threshold_db
            or cinr_drop >= cinr_drop_threshold_db
            or s.cinr_db <= low_cinr_threshold_db
        )

        # Priority: if RF is healthy (or even if both occur, Ethernet physical layer fault is local to eth0)
        if has_eth_fault and not has_rf_alignment_fault:
            per_cpe[s.cpe_id] = CPE_ETHERNET_POE_CABLE_FAULT
            eth_fault_ids.append(s.cpe_id)
        elif has_rf_alignment_fault:
            per_cpe[s.cpe_id] = CPE_CHAIN_IMBALANCE_OR_MISALIGNMENT
            chain_fault_ids.append(s.cpe_id)
        elif has_eth_fault:
            per_cpe[s.cpe_id] = CPE_ETHERNET_POE_CABLE_FAULT
            eth_fault_ids.append(s.cpe_id)

    if eth_fault_ids and not chain_fault_ids:
        return FaultLocalizationReport(
            sector_classification=CPE_ETHERNET_POE_CABLE_FAULT,
            affected_cpe_ids=eth_fault_ids,
            per_cpe_classifications=per_cpe,
            recommended_action=(
                f"Inspect RJ45 crimp, water ingress, or PoE injector/cable on CPE(s): {', '.join(eth_fault_ids)}. "
                "Wireless link is healthy."
            ),
            evidence={"eth_fault_cpes": eth_fault_ids},
        )

    if chain_fault_ids:
        return FaultLocalizationReport(
            sector_classification=CPE_CHAIN_IMBALANCE_OR_MISALIGNMENT,
            affected_cpe_ids=chain_fault_ids + eth_fault_ids,
            per_cpe_classifications=per_cpe,
            recommended_action=(
                f"Single-CPE antenna misalignment, chain imbalance (>= {chain_imbalance_threshold_db:.1f} dB), "
                f"or Fresnel obstruction on: {', '.join(chain_fault_ids)}."
            ),
            evidence={
                "chain_or_alignment_fault_cpes": chain_fault_ids,
                "eth_fault_cpes": eth_fault_ids,
            },
        )

    return FaultLocalizationReport(
        sector_classification=HEALTHY,
        affected_cpe_ids=[],
        per_cpe_classifications=per_cpe,
        recommended_action="Sector and all associated CPEs operating within nominal RF and LAN parameters.",
    )
