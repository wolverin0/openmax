"""Intelligent RF & Station Advisory Engine for airOS and OpenWrt PtMP Sectors.

Stage 1 Stock-airOS Intelligence module.
Implements:
1. Station link auditing:
   - Chain imbalance detection (> 3.5 dB delta indicates feedhorn tilt, cross-pol misalignment, or obstruction).
   - Poor SNR / CINR diagnosis (< 22 dB for 64-QAM / MCS7, < 18 dB for 16-QAM).
   - High retry rate detection (> 15% packet error rate).
   - Receiver overload / near-field desensitization detection (RSSI > -45 dBm).
2. Concrete RF optimization advisories:
   - Channel selection optimizer based on spectral FFT occupancy and peak interference power.
   - Channel width optimizer (20 MHz vs 40 MHz trade-off under interference).
   - Per-station and sector EIRP / TX-power adjustments targeting 25-32 dB SNR.
3. Canary change manager:
   - Safe trial change modeling with causal before/after impact evaluation.
   - Quantitative evaluation of aggregate goodput, p95 latency, and Jain fairness.
   - Automated rollback recommendations if performance degrades.
"""

from __future__ import annotations

import datetime as dt
import math
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# Regulatory and Hardware Constraints
CHAIN_IMBALANCE_WARNING_DB = 3.5
CHAIN_IMBALANCE_CRITICAL_DB = 6.0
RECEIVER_DESENSITIZED_RSSI_DBM = -45.0
LOW_SNR_WARNING_DB = 22.0
LOW_SNR_CRITICAL_DB = 16.0
HIGH_RETRY_WARNING_PCT = 15.0
HIGH_RETRY_CRITICAL_PCT = 25.0

TARGET_SNR_MIN_DB = 25.0
TARGET_SNR_MAX_DB = 32.0


class AuditSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class CPEAuditRecord:
    """Audit evaluation for an individual subscriber station."""

    mac: str
    cpe_id: str
    issues: List[str]
    chain_imbalance_db: float
    snr_db: float
    rssi_dbm: float
    retry_pct: float
    current_mcs: Optional[int]
    severity: AuditSeverity
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d


@dataclass
class RFAdvisory:
    """Actionable optimization advisory for sector RF configuration."""

    advisory_id: str
    category: str  # "CHANNEL", "CHANNEL_WIDTH", "TX_POWER", "ALIGNMENT"
    target: str    # "SECTOR" or station MAC
    current_value: Any
    recommended_value: Any
    expected_benefit: str
    priority: AuditSeverity
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["priority"] = self.priority.value
        return d


@dataclass
class CanaryTrial:
    """State and evaluation of a canary change experiment."""

    trial_id: str
    parameter_name: str
    old_value: Any
    new_value: Any
    timestamp: str
    before_metrics: Dict[str, Any]
    after_metrics: Optional[Dict[str, Any]] = None
    status: str = "TRIAL_STAGED"  # STAGED, ACTIVE, ACCEPTED, REVERTED
    decision: str = "INCONCLUSIVE"  # KEEP, REVERT, INCONCLUSIVE
    decision_reason: str = "Awaiting evaluation."
    goodput_delta_pct: Optional[float] = None
    latency_p95_delta_pct: Optional[float] = None
    fairness_before: Optional[float] = None
    fairness_after: Optional[float] = None
    fairness_delta: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def calculate_jains_fairness(values: Union[List[float], Dict[str, float]]) -> float:
    """Calculate Jain's Fairness Index over a set of station throughputs.

    Formula: J = (sum(x_i))^2 / (N * sum(x_i^2))
    Returns 1.0 if all values are equal. Minimum is 1/N.
    """
    if isinstance(values, dict):
        vals = [float(v) for v in values.values()]
    else:
        vals = [float(v) for v in values]

    if not vals:
        return 1.0

    n = len(vals)
    total = sum(vals)
    if total == 0.0:
        return 1.0

    sum_sq = sum(x * x for x in vals)
    if sum_sq == 0.0:
        return 1.0

    fairness = (total * total) / (n * sum_sq)
    return round(float(fairness), 4)


class CanaryManager:
    """Manages canary trials with causal before/after evaluation and automatic rollback guard."""

    def __init__(
        self,
        max_acceptable_goodput_drop_pct: float = -10.0,
        max_acceptable_latency_increase_pct: float = 20.0,
        max_acceptable_fairness_drop: float = 0.15,
    ):
        self.max_drop_pct = max_acceptable_goodput_drop_pct
        self.max_latency_inc = max_acceptable_latency_increase_pct
        self.max_fairness_drop = max_acceptable_fairness_drop
        self.trials: Dict[str, CanaryTrial] = {}

    def stage_canary(
        self,
        parameter_name: str,
        old_value: Any,
        new_value: Any,
        before_metrics: Dict[str, Any],
    ) -> CanaryTrial:
        """Stage a new canary trial with baseline metrics captured."""
        trial_id = f"canary-{uuid.uuid4().hex[:8]}"
        ts = dt.datetime.now(dt.timezone.utc).isoformat()

        trial = CanaryTrial(
            trial_id=trial_id,
            parameter_name=parameter_name,
            old_value=old_value,
            new_value=new_value,
            timestamp=ts,
            before_metrics=dict(before_metrics),
            status="TRIAL_ACTIVE",
        )
        self.trials[trial_id] = trial
        return trial

    def evaluate_canary(
        self,
        trial: CanaryTrial,
        after_metrics: Dict[str, Any],
    ) -> CanaryTrial:
        """Evaluate canary trial results against baseline and produce KEEP or REVERT decision."""
        trial.after_metrics = dict(after_metrics)
        bm = trial.before_metrics
        am = trial.after_metrics

        # 1. Goodput comparison
        bg = float(bm.get("goodput_mbps", 1.0) or 1.0)
        ag = float(am.get("goodput_mbps", 1.0) or 1.0)
        goodput_delta = round(((ag - bg) / bg) * 100.0, 2)
        trial.goodput_delta_pct = goodput_delta

        # 2. Latency p95 comparison
        bp95 = float(bm.get("latency_p95_ms", bm.get("p95_ms", 10.0)) or 10.0)
        ap95 = float(am.get("latency_p95_ms", am.get("p95_ms", 10.0)) or 10.0)
        latency_delta = round(((ap95 - bp95) / bp95) * 100.0, 2)
        trial.latency_p95_delta_pct = latency_delta

        # 3. Jain fairness comparison
        b_subs = bm.get("per_station_goodputs", [bg])
        a_subs = am.get("per_station_goodputs", [ag])
        fairness_b = calculate_jains_fairness(b_subs)
        fairness_a = calculate_jains_fairness(a_subs)
        fairness_delta = round(fairness_a - fairness_b, 4)

        trial.fairness_before = fairness_b
        trial.fairness_after = fairness_a
        trial.fairness_delta = fairness_delta

        # 4. Rollback / Keep Decision Evaluation
        reasons: List[str] = []
        should_revert = False

        if goodput_delta < self.max_drop_pct:
            should_revert = True
            reasons.append(f"Goodput dropped by {goodput_delta:.1f}% (< threshold {self.max_drop_pct}%)")

        if latency_delta > self.max_latency_inc:
            should_revert = True
            reasons.append(f"Loaded p95 latency degraded by +{latency_delta:.1f}% (> threshold +{self.max_latency_inc}%)")

        if fairness_delta < -self.max_fairness_drop:
            should_revert = True
            reasons.append(f"Jain fairness degraded by {fairness_delta:.3f} (< threshold -{self.max_fairness_drop})")

        # Check resets / disconnects
        b_resets = bm.get("resets", 0)
        a_resets = am.get("resets", 0)
        if a_resets > b_resets:
            should_revert = True
            reasons.append(f"Firmware resets or association loss detected: {a_resets} > {b_resets}")

        if should_revert:
            trial.decision = "REVERT"
            trial.status = "REVERTED"
            trial.decision_reason = "Rollback recommended: " + " | ".join(reasons)
        else:
            trial.decision = "KEEP"
            trial.status = "ACCEPTED"
            trial.decision_reason = (
                f"Canary trial successful. Goodput delta: {goodput_delta:+.1f}%, "
                f"Latency delta: {latency_delta:+.1f}%, Fairness: {fairness_a:.3f}"
            )

        return trial


class SectorAdvisor:
    """Intelligent RF & Station Advisor."""

    def __init__(self, target_snr_min: float = TARGET_SNR_MIN_DB, target_snr_max: float = TARGET_SNR_MAX_DB):
        self.target_snr_min = target_snr_min
        self.target_snr_max = target_snr_max

    def audit_stations(self, stations: Union[Dict[str, Any], List[Any]]) -> List[CPEAuditRecord]:
        """Audit all connected subscriber stations for RF and alignment issues."""
        records: List[CPEAuditRecord] = []

        if isinstance(stations, dict):
            sta_list = list(stations.values())
        else:
            sta_list = list(stations)

        for s in sta_list:
            d = s.to_dict() if hasattr(s, "to_dict") else dict(s)
            mac = d.get("mac", "unknown")
            cpe_id = d.get("cpe_id", d.get("device_name", mac))

            chain0 = d.get("chain0_signal_dbm")
            chain1 = d.get("chain1_signal_dbm")
            rssi = float(d.get("signal_dbm", d.get("rssi", -65.0)) or -65.0)
            noise = float(d.get("noise_floor_dbm", -95.0) or -95.0)
            snr = float(d.get("snr_db", rssi - noise) or (rssi - noise))

            retries = int(d.get("tx_retries", 0) or 0)
            tx_pkts = int(d.get("tx_packets", 0) or 0)
            retry_pct = (retries / tx_pkts * 100.0) if tx_pkts > 0 else float(retries)

            current_mcs = d.get("mcs")

            # 1. Chain Imbalance
            if chain0 is not None and chain1 is not None:
                imbalance = abs(float(chain0) - float(chain1))
            else:
                imbalance = float(d.get("chain_imbalance_db", 0.0) or 0.0)

            issues: List[str] = []
            recs: List[str] = []
            severity = AuditSeverity.INFO

            if imbalance >= CHAIN_IMBALANCE_CRITICAL_DB:
                issues.append(f"Severe chain imbalance ({imbalance:.1f} dB)")
                recs.append("Physical re-alignment or feedhorn inspection required (likely cross-polarization tilt or partial obstruction)")
                severity = AuditSeverity.CRITICAL
            elif imbalance >= CHAIN_IMBALANCE_WARNING_DB:
                issues.append(f"Moderate chain imbalance ({imbalance:.1f} dB)")
                recs.append("Check line-of-sight clearance and antenna elevation alignment")
                if severity != AuditSeverity.CRITICAL:
                    severity = AuditSeverity.WARNING

            # 2. Receiver Overload / Near-field Desensitization
            if rssi >= RECEIVER_DESENSITIZED_RSSI_DBM:
                issues.append(f"Receiver overloaded / near-field desensitization (RSSI {rssi:.1f} dBm)")
                recs.append("Reduce CPE transmit power immediately to prevent EVM distortion and intermodulation")
                severity = AuditSeverity.CRITICAL

            # 3. Poor SNR / CINR
            if snr <= LOW_SNR_CRITICAL_DB:
                issues.append(f"Critically low SNR ({snr:.1f} dB)")
                recs.append("Increase TX power or upgrade CPE antenna to maintain minimum link margin")
                severity = AuditSeverity.CRITICAL
            elif snr <= LOW_SNR_WARNING_DB:
                issues.append(f"Suboptimal SNR ({snr:.1f} dB for 802.11ac 64-QAM)")
                recs.append("Consider channel frequency change or CPE power increase to reach 25 dB SNR")
                if severity != AuditSeverity.CRITICAL:
                    severity = AuditSeverity.WARNING

            # 4. High Retries
            if retry_pct >= HIGH_RETRY_CRITICAL_PCT:
                issues.append(f"Critical retry rate ({retry_pct:.1f}%)")
                recs.append("Cap rate mask below failing MCS or lower channel width to 20MHz")
                severity = AuditSeverity.CRITICAL
            elif retry_pct >= HIGH_RETRY_WARNING_PCT:
                issues.append(f"Elevated retries ({retry_pct:.1f}%)")
                recs.append("Monitor channel interference and enable rate bandit bounding")
                if severity != AuditSeverity.CRITICAL:
                    severity = AuditSeverity.WARNING

            records.append(
                CPEAuditRecord(
                    mac=mac,
                    cpe_id=cpe_id,
                    issues=issues,
                    chain_imbalance_db=round(imbalance, 1),
                    snr_db=round(snr, 1),
                    rssi_dbm=round(rssi, 1),
                    retry_pct=round(retry_pct, 1),
                    current_mcs=current_mcs,
                    severity=severity,
                    recommendations=recs,
                )
            )

        return records

    def recommend_channel(
        self,
        current_freq_mhz: int,
        spectral_data: Dict[int, Dict[str, Any]],
    ) -> RFAdvisory:
        """Analyze spectral scan data and recommend the optimal low-noise frequency."""
        if not spectral_data:
            return RFAdvisory(
                advisory_id=f"adv-chan-{uuid.uuid4().hex[:6]}",
                category="CHANNEL",
                target="SECTOR",
                current_value=current_freq_mhz,
                recommended_value=current_freq_mhz,
                expected_benefit="No change: insufficient spectral FFT data",
                priority=AuditSeverity.INFO,
                rationale="Spectral data empty.",
            )

        # Score candidate frequencies
        best_freq = current_freq_mhz
        best_score = float("inf")
        curr_score = float("inf")

        for freq, metrics in spectral_data.items():
            if metrics.get("dfs_radar_detected", False):
                continue  # Skip channels with active DFS radar pulses

            noise = float(metrics.get("noise_floor_dbm", -95.0) or -95.0)
            peak_pwr = float(metrics.get("peak_interference_dbm", noise) or noise)
            occ_pct = float(metrics.get("channel_occupancy_pct", metrics.get("occupancy_pct", 0.0)) or 0.0)

            # Combined interference penalty: occupancy weight + interference power above -95
            penalty = occ_pct * 1.5 + max(0.0, peak_pwr - (-95.0)) * 2.0 + max(0.0, noise - (-95.0)) * 1.0

            if freq == current_freq_mhz:
                curr_score = penalty

            if penalty < best_score:
                best_score = penalty
                best_freq = freq

        # Only recommend channel jump if meaningful improvement (> 20% cleaner)
        if best_freq != current_freq_mhz and best_score < curr_score * 0.80:
            curr_metrics = spectral_data.get(current_freq_mhz, {})
            best_metrics = spectral_data.get(best_freq, {})

            prio = AuditSeverity.CRITICAL if curr_score > 60.0 else AuditSeverity.WARNING
            benefit = f"+{curr_score - best_score:.1f} penalty points cleaner; avoids {curr_metrics.get('channel_occupancy_pct', 0)}% occupancy on {current_freq_mhz}MHz"
            rationale = (
                f"Candidate channel {best_freq} MHz exhibits lower noise floor ({best_metrics.get('noise_floor_dbm', -95)} dBm vs {curr_metrics.get('noise_floor_dbm', -95)} dBm) "
                f"and {best_metrics.get('channel_occupancy_pct', 0)}% occupancy compared to {current_freq_mhz} MHz."
            )
            rec_val = best_freq
        else:
            rec_val = current_freq_mhz
            prio = AuditSeverity.INFO
            benefit = "Current channel is optimal or within acceptable interference envelope"
            rationale = f"Current channel {current_freq_mhz} MHz score ({curr_score:.1f}) is satisfactory."

        return RFAdvisory(
            advisory_id=f"adv-chan-{uuid.uuid4().hex[:6]}",
            category="CHANNEL",
            target="SECTOR",
            current_value=current_freq_mhz,
            recommended_value=rec_val,
            expected_benefit=benefit,
            priority=prio,
            rationale=rationale,
        )

    def recommend_channel_width(
        self,
        current_width_mhz: int,
        spectral_occupancy_pct: float,
        avg_snr_db: float,
        noise_floor_dbm: float = -90.0,
    ) -> RFAdvisory:
        """Recommend 20 MHz vs 40 MHz channel width based on interference and SNR."""
        adv_id = f"adv-width-{uuid.uuid4().hex[:6]}"

        # Rule 1: High noise / dense interference on 40 MHz -> drop to 20 MHz
        if current_width_mhz >= 40 and (spectral_occupancy_pct > 50.0 or noise_floor_dbm > -85.0):
            return RFAdvisory(
                advisory_id=adv_id,
                category="CHANNEL_WIDTH",
                target="SECTOR",
                current_value=current_width_mhz,
                recommended_value=20,
                expected_benefit="+3 dB SNR gain, eliminates collision risk on second 20MHz segment",
                priority=AuditSeverity.WARNING,
                rationale=(
                    f"40 MHz width in congested spectrum ({spectral_occupancy_pct:.1f}% occupancy, "
                    f"noise floor {noise_floor_dbm} dBm) creates frequent packet collisions. "
                    "Downscaling to 20 MHz concentrates RF power and improves MCS stability."
                ),
            )

        # Rule 2: Clean spectrum on 20 MHz with high SNR -> expand to 40 MHz
        if current_width_mhz == 20 and spectral_occupancy_pct < 25.0 and avg_snr_db >= 28.0 and noise_floor_dbm <= -92.0:
            return RFAdvisory(
                advisory_id=adv_id,
                category="CHANNEL_WIDTH",
                target="SECTOR",
                current_value=current_width_mhz,
                recommended_value=40,
                expected_benefit="Doubles channel symbol rate and peak sector throughput",
                priority=AuditSeverity.INFO,
                rationale=(
                    f"Spectrum is clean ({spectral_occupancy_pct:.1f}% occupancy) and average station SNR is high "
                    f"({avg_snr_db:.1f} dB). 40 MHz can double capacity safely."
                ),
            )

        # Default: maintain current width
        return RFAdvisory(
            advisory_id=adv_id,
            category="CHANNEL_WIDTH",
            target="SECTOR",
            current_value=current_width_mhz,
            recommended_value=current_width_mhz,
            expected_benefit="Current channel width matches RF environment",
            priority=AuditSeverity.INFO,
            rationale=f"Current {current_width_mhz} MHz width is well-suited to {spectral_occupancy_pct:.1f}% occupancy.",
        )

    def recommend_tx_power(
        self,
        stations: Union[Dict[str, Any], List[Any]],
        ap_tx_power_dbm: float = 20.0,
    ) -> List[RFAdvisory]:
        """Generate TX power adjustment advisories per CPE and for sector AP."""
        advisories: List[RFAdvisory] = []
        sta_list = list(stations.values()) if isinstance(stations, dict) else list(stations)

        for s in sta_list:
            d = s.to_dict() if hasattr(s, "to_dict") else dict(s)
            mac = d.get("mac", "unknown")
            rssi = float(d.get("signal_dbm", d.get("rssi", -65.0)) or -65.0)
            noise = float(d.get("noise_floor_dbm", -95.0) or -95.0)
            snr = float(d.get("snr_db", rssi - noise) or (rssi - noise))
            current_cpe_tx = float(d.get("tx_power_dbm", 20.0) or 20.0)

            # Case A: Overpowered CPE (RSSI > -48 dBm)
            if rssi > -48.0:
                delta = math.ceil(rssi - (-58.0))
                rec_tx = max(4.0, current_cpe_tx - delta)
                advisories.append(
                    RFAdvisory(
                        advisory_id=f"adv-pwr-{uuid.uuid4().hex[:6]}",
                        category="TX_POWER",
                        target=mac,
                        current_value=current_cpe_tx,
                        recommended_value=rec_tx,
                        expected_benefit=f"Mitigate EVM distortion and AP receiver desensitization (-{delta:.1f} dB)",
                        priority=AuditSeverity.WARNING,
                        rationale=f"Station RSSI is {rssi:.1f} dBm (too hot). Backing off TX power to reach ~ -58 dBm.",
                    )
                )

            # Case B: Underpowered CPE (SNR < 23 dB)
            elif snr < self.target_snr_min:
                delta = math.ceil(self.target_snr_min - snr)
                rec_tx = min(24.0, current_cpe_tx + delta)
                if rec_tx > current_cpe_tx:
                    advisories.append(
                        RFAdvisory(
                            advisory_id=f"adv-pwr-{uuid.uuid4().hex[:6]}",
                            category="TX_POWER",
                            target=mac,
                            current_value=current_cpe_tx,
                            recommended_value=rec_tx,
                            expected_benefit=f"Gain +{rec_tx - current_cpe_tx:.1f} dB SNR margin for higher MCS",
                            priority=AuditSeverity.WARNING,
                            rationale=f"Station SNR {snr:.1f} dB is below {self.target_snr_min} dB target. Increasing TX power.",
                        )
                    )

        return advisories

    def generate_full_advisory_report(
        self,
        stations: Union[Dict[str, Any], List[Any]],
        current_freq_mhz: int = 5500,
        current_width_mhz: int = 20,
        spectral_data: Optional[Dict[int, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate a complete structured advisory report for an entire PtMP sector."""
        audits = self.audit_stations(stations)

        # Compute average SNR and channel occupancy
        snrs = [a.snr_db for a in audits] if audits else [25.0]
        avg_snr = sum(snrs) / len(snrs)

        spec = spectral_data or {}
        curr_spec = spec.get(current_freq_mhz, {})
        occupancy = float(curr_spec.get("channel_occupancy_pct", curr_spec.get("occupancy_pct", 10.0)) or 10.0)
        noise = float(curr_spec.get("noise_floor_dbm", -95.0) or -95.0)

        # Generate advisories
        chan_adv = self.recommend_channel(current_freq_mhz, spec)
        width_adv = self.recommend_channel_width(current_width_mhz, occupancy, avg_snr, noise)
        pwr_advs = self.recommend_tx_power(stations)

        # Generate physical alignment advisories for stations with chain imbalance
        align_advs: List[RFAdvisory] = []
        for a in audits:
            if a.chain_imbalance_db >= CHAIN_IMBALANCE_WARNING_DB:
                align_advs.append(
                    RFAdvisory(
                        advisory_id=f"adv-align-{uuid.uuid4().hex[:6]}",
                        category="ALIGNMENT",
                        target=a.mac,
                        current_value=f"{a.chain_imbalance_db:.1f} dB delta",
                        recommended_value="< 2.0 dB delta",
                        expected_benefit="Restore dual-stream MIMO multiplexing and eliminate cross-pol loss",
                        priority=a.severity,
                        rationale=" | ".join(a.recommendations) or "Antenna re-alignment required.",
                    )
                )

        all_advisories = [chan_adv, width_adv] + pwr_advs + align_advs
        actionable_advisories = [a for a in all_advisories if a.priority in (AuditSeverity.WARNING, AuditSeverity.CRITICAL)]

        return {
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "station_count": len(audits),
            "audits": [a.to_dict() for a in audits],
            "advisories": [a.to_dict() for a in all_advisories],
            "actionable_advisories_count": len(actionable_advisories),
            "critical_stations": [a.mac for a in audits if a.severity == AuditSeverity.CRITICAL],
            "warning_stations": [a.mac for a in audits if a.severity == AuditSeverity.WARNING],
        }
