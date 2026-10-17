"""Sector Capacity, Airtime Exhaustion, and Bottleneck Forecasting Engine.

Stage 1 Stock-airOS Intelligence module for PtMP fixed wireless sectors.
Implements:
1. 802.11ac theoretical PHY rate and MAC goodput modeling (20/40/80 MHz, 1SS/2SS, MCS 0..9).
2. Sector saturation forecasting under varying subscriber counts, oversubscription ratios, and plan tiers.
3. Airtime exhaustion detection (identifying when airtime demand exceeds the 85% CSMA/CA cliff).
4. Bottleneck CPE diagnosis: detects stations dragging down sector capacity due to low MCS, high retries,
   or disproportionate airtime share.
5. Quantitative counterfactual capacity gain projection (calculating throughput freed by throttling
   or realigning degraded stations).
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

# Standard 802.11ac PHY bitrates (Mbps) for 800ns Long Guard Interval (LGI)
# Format: (bw_mhz, nss): [MCS0..MCS9]
VHT_PHY_RATES_LGI: Dict[Tuple[int, int], List[float]] = {
    (20, 1): [6.5, 13.0, 19.5, 26.0, 39.0, 52.0, 58.5, 65.0, 78.0, 86.7],
    (20, 2): [13.0, 26.0, 39.0, 52.0, 78.0, 104.0, 117.0, 130.0, 156.0, 173.3],
    (40, 1): [13.5, 27.0, 40.5, 54.0, 81.0, 108.0, 121.5, 135.0, 162.0, 180.0],
    (40, 2): [27.0, 54.0, 81.0, 108.0, 162.0, 216.0, 243.0, 270.0, 324.0, 360.0],
    (80, 1): [29.3, 58.5, 87.8, 117.0, 175.5, 234.0, 263.3, 292.5, 351.0, 390.0],
    (80, 2): [58.5, 117.0, 175.5, 234.0, 351.0, 468.0, 526.5, 585.0, 702.0, 780.0],
}

DEFAULT_AIRTIME_CLIFF_PCT = 85.0
DEFAULT_MAC_EFFICIENCY = 0.72  # Typical A-MPDU aggregation efficiency on clean PtMP link


@dataclass(frozen=True)
class PlanTier:
    """Service plan tier definition."""

    name: str
    down_mbps: float
    up_mbps: float
    concurrency_factor: float = 0.25  # Peak busy hour concurrency probability

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


DEFAULT_PLANS: Dict[str, PlanTier] = {
    "Basic_10M": PlanTier("Basic_10M", down_mbps=10.0, up_mbps=2.0, concurrency_factor=0.20),
    "Standard_25M": PlanTier("Standard_25M", down_mbps=25.0, up_mbps=5.0, concurrency_factor=0.25),
    "Pro_50M": PlanTier("Pro_50M", down_mbps=50.0, up_mbps=10.0, concurrency_factor=0.30),
    "Ultra_100M": PlanTier("Ultra_100M", down_mbps=100.0, up_mbps=20.0, concurrency_factor=0.35),
}


@dataclass
class SubscriberDemand:
    """Subscriber profile and active wireless demand."""

    cpe_id: str
    plan_name: str = "Standard_25M"
    mcs: int = 7
    nss: int = 2
    bandwidth_mhz: int = 20
    short_gi: bool = False
    retry_pct: float = 2.0
    offered_load_mbps: Optional[float] = None
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BottleneckDiagnosis:
    """Detailed diagnosis of a bottleneck subscriber."""

    cpe_id: str
    is_bottleneck: bool
    inefficiency_ratio: float  # airtime_share / goodput_share
    airtime_consumed_pct: float
    goodput_delivered_mbps: float
    mcs: int
    retry_pct: float
    diagnosis_reason: str
    freed_airtime_pct_if_remediated: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CapacityForecastResult:
    """Sector capacity and airtime forecast result."""

    subscriber_count: int
    active_subscribers: int
    aggregate_goodput_mbps: float
    total_airtime_demand_pct: float
    airtime_limit_pct: float
    is_exhausted: bool
    remaining_airtime_headroom_pct: float
    max_admissible_additional_subscribers: int
    bottlenecks: List[BottleneckDiagnosis]
    freed_airtime_if_bottlenecks_fixed_pct: float
    potential_goodput_gain_mbps: float

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["bottlenecks"] = [b.to_dict() for b in self.bottlenecks]
        return d


class SectorCapacityForecaster:
    """Analytical forecasting engine for airMAX AC / 802.11ac PtMP sectors."""

    def __init__(
        self,
        default_bw_mhz: int = 20,
        airtime_limit_pct: float = DEFAULT_AIRTIME_CLIFF_PCT,
        mac_efficiency: float = DEFAULT_MAC_EFFICIENCY,
    ):
        self.default_bw_mhz = default_bw_mhz
        self.airtime_limit_pct = airtime_limit_pct
        self.mac_efficiency = mac_efficiency
        self.plans = dict(DEFAULT_PLANS)

    def register_plan(self, plan: PlanTier):
        """Register custom plan tier."""
        self.plans[plan.name] = plan

    @staticmethod
    def calculate_phy_rate_mbps(
        mcs: int,
        bw_mhz: int = 20,
        nss: int = 1,
        short_gi: bool = False,
    ) -> float:
        """Calculate standard 802.11ac physical bitrate in Mbps."""
        mcs_clamped = max(0, min(9, int(mcs)))
        bw_clamped = bw_mhz if bw_mhz in (20, 40, 80) else 20
        nss_clamped = max(1, min(2, int(nss)))

        table = VHT_PHY_RATES_LGI.get((bw_clamped, nss_clamped))
        if not table:
            table = VHT_PHY_RATES_LGI[(20, 1)]

        base_rate = table[mcs_clamped]
        # Short Guard Interval (400ns) increases symbol rate by 10/9 (~11.1%)
        if short_gi:
            base_rate = round(base_rate * (10.0 / 9.0), 1)

        return base_rate

    def calculate_effective_goodput(
        self,
        mcs: int,
        bw_mhz: int = 20,
        nss: int = 1,
        retry_pct: float = 0.0,
        short_gi: bool = False,
    ) -> float:
        """Calculate net payload goodput accounting for MAC headers, aggregation, and retries."""
        phy_rate = self.calculate_phy_rate_mbps(mcs, bw_mhz, nss, short_gi)
        per = max(0.0, min(0.95, float(retry_pct) / 100.0))

        # Effective throughput: phy * efficiency * (1 - PER)
        # Note: retransmissions consume airtime proportionally: 1 / (1 - PER)
        effective = phy_rate * self.mac_efficiency * (1.0 - per)
        return max(0.5, round(effective, 2))

    def calculate_airtime_per_megabit_s(
        self,
        mcs: int,
        bw_mhz: int = 20,
        nss: int = 1,
        retry_pct: float = 0.0,
        short_gi: bool = False,
    ) -> float:
        """Calculate airtime duration in seconds required to deliver 1 Megabit of payload."""
        effective_mbps = self.calculate_effective_goodput(mcs, bw_mhz, nss, retry_pct, short_gi)
        return 1.0 / effective_mbps

    def forecast_sector_capacity(
        self,
        subscribers: List[Union[SubscriberDemand, Dict[str, Any]]],
        custom_plans: Optional[Dict[str, PlanTier]] = None,
    ) -> CapacityForecastResult:
        """Forecast total sector capacity, airtime demand, and saturation status."""
        active_plans = custom_plans or self.plans
        norm_subs: List[SubscriberDemand] = []

        for s in subscribers:
            if isinstance(s, SubscriberDemand):
                norm_subs.append(s)
            else:
                norm_subs.append(
                    SubscriberDemand(
                        cpe_id=s.get("cpe_id", s.get("mac", "unknown")),
                        plan_name=s.get("plan_name", s.get("plan", "Standard_25M")),
                        mcs=int(s.get("mcs", 7)),
                        nss=int(s.get("nss", 2)),
                        bandwidth_mhz=int(s.get("bandwidth_mhz", self.default_bw_mhz)),
                        short_gi=bool(s.get("short_gi", False)),
                        retry_pct=float(s.get("retry_pct", s.get("tx_retries", 2.0))),
                        offered_load_mbps=s.get("offered_load_mbps"),
                        active=s.get("active", True),
                    )
                )

        active_subs = [s for s in norm_subs if s.active]
        total_sub_count = len(norm_subs)
        active_sub_count = len(active_subs)

        if active_sub_count == 0:
            return CapacityForecastResult(
                subscriber_count=total_sub_count,
                active_subscribers=0,
                aggregate_goodput_mbps=0.0,
                total_airtime_demand_pct=0.0,
                airtime_limit_pct=self.airtime_limit_pct,
                is_exhausted=False,
                remaining_airtime_headroom_pct=self.airtime_limit_pct,
                max_admissible_additional_subscribers=100,
                bottlenecks=[],
                freed_airtime_if_bottlenecks_fixed_pct=0.0,
                potential_goodput_gain_mbps=0.0,
            )

        # 1. Compute per-subscriber traffic demand and airtime consumption
        sub_airtimes: List[float] = []
        sub_goodputs: List[float] = []

        for sub in active_subs:
            plan = active_plans.get(sub.plan_name, active_plans.get("Standard_25M", DEFAULT_PLANS["Standard_25M"]))
            if sub.offered_load_mbps is not None:
                demanded_mbps = float(sub.offered_load_mbps)
            else:
                demanded_mbps = plan.down_mbps * plan.concurrency_factor

            # Airtime per Megabit
            at_per_mb = self.calculate_airtime_per_megabit_s(
                sub.mcs, sub.bandwidth_mhz, sub.nss, sub.retry_pct, sub.short_gi
            )
            # Total airtime fraction for this subscriber
            airtime_fraction = demanded_mbps * at_per_mb
            sub_airtimes.append(airtime_fraction)
            sub_goodputs.append(demanded_mbps)

        total_airtime_fraction = sum(sub_airtimes)
        total_airtime_pct = round(total_airtime_fraction * 100.0, 2)
        is_exhausted = total_airtime_pct >= self.airtime_limit_pct
        headroom_airtime_pct = max(0.0, round(self.airtime_limit_pct - total_airtime_pct, 2))

        # 2. Compute aggregate deliverable goodput
        # If airtime is saturated (> 1.0), delivered goodput scales down by total airtime demand
        scaling = 1.0 if total_airtime_fraction <= 1.0 else (1.0 / total_airtime_fraction)
        aggregate_goodput = round(sum(sub_goodputs) * scaling, 2)

        # 3. Compute bottleneck diagnoses
        bottlenecks = self.identify_bottlenecks(active_subs, sub_airtimes, sub_goodputs)

        # 4. Admissible subscriber projection
        avg_airtime_per_sub = (total_airtime_fraction / active_sub_count) if active_sub_count > 0 else 0.05
        if avg_airtime_per_sub > 0 and headroom_airtime_pct > 0:
            max_admissible = int((headroom_airtime_pct / 100.0) / avg_airtime_per_sub)
        else:
            max_admissible = 0

        # 5. Potential gain from fixing bottlenecks
        freed_airtime_pct = round(sum(b.freed_airtime_pct_if_remediated for b in bottlenecks), 2)
        # Freed airtime re-invested into sector at median sector efficiency
        median_rate = sorted([self.calculate_effective_goodput(s.mcs, s.bandwidth_mhz, s.nss) for s in active_subs])[
            active_sub_count // 2
        ]
        potential_gain = round((freed_airtime_pct / 100.0) * median_rate, 2)

        return CapacityForecastResult(
            subscriber_count=total_sub_count,
            active_subscribers=active_sub_count,
            aggregate_goodput_mbps=aggregate_goodput,
            total_airtime_demand_pct=total_airtime_pct,
            airtime_limit_pct=self.airtime_limit_pct,
            is_exhausted=is_exhausted,
            remaining_airtime_headroom_pct=headroom_airtime_pct,
            max_admissible_additional_subscribers=max_admissible,
            bottlenecks=bottlenecks,
            freed_airtime_if_bottlenecks_fixed_pct=freed_airtime_pct,
            potential_goodput_gain_mbps=potential_gain,
        )

    def identify_bottlenecks(
        self,
        subscribers: List[SubscriberDemand],
        airtimes: Optional[List[float]] = None,
        goodputs: Optional[List[float]] = None,
    ) -> List[BottleneckDiagnosis]:
        """Detect stations that disproportionately drag down sector goodput."""
        n = len(subscribers)
        if n == 0:
            return []

        if airtimes is None or goodputs is None:
            airtimes = []
            goodputs = []
            for sub in subscribers:
                plan = self.plans.get(sub.plan_name, DEFAULT_PLANS["Standard_25M"])
                demand = sub.offered_load_mbps if sub.offered_load_mbps is not None else (plan.down_mbps * plan.concurrency_factor)
                at_per_mb = self.calculate_airtime_per_megabit_s(sub.mcs, sub.bandwidth_mhz, sub.nss, sub.retry_pct, sub.short_gi)
                airtimes.append(demand * at_per_mb)
                goodputs.append(demand)

        total_at = sum(airtimes) or 1.0
        total_gp = sum(goodputs) or 1.0

        bottlenecks: List[BottleneckDiagnosis] = []

        for i, sub in enumerate(subscribers):
            at_pct = (airtimes[i] / total_at) * 100.0
            gp_pct = (goodputs[i] / total_gp) * 100.0
            inefficiency = round(at_pct / max(0.5, gp_pct), 2)

            reasons: List[str] = []
            is_bottleneck = False

            # Condition 1: Drag factor > 2.0 (consumes > 2x airtime relative to payload)
            if inefficiency > 2.0:
                reasons.append(f"High airtime drag factor ({inefficiency}x airtime relative to throughput)")
                is_bottleneck = True

            # Condition 2: Low MCS (< 4) on standard/high plan tier
            if sub.mcs <= 3:
                reasons.append(f"Severe MCS degradation (MCS {sub.mcs} @ {sub.bandwidth_mhz}MHz)")
                is_bottleneck = True

            # Condition 3: Excessive retries (> 12%)
            if sub.retry_pct >= 12.0:
                reasons.append(f"Excessive retries ({sub.retry_pct:.1f}% PER)")
                is_bottleneck = True

            # Condition 4: Consumes more than 25% of all sector airtime alone (in sectors with >= 4 stations)
            if n >= 4 and at_pct >= 25.0:
                reasons.append(f"Monopolizing sector airtime ({at_pct:.1f}% of sector)")
                is_bottleneck = True

            # Compute freed airtime if remediated (e.g. upgraded to healthy MCS7 @ 2% retry)
            current_at = airtimes[i]
            healthy_at = goodputs[i] * self.calculate_airtime_per_megabit_s(7, sub.bandwidth_mhz, sub.nss, 2.0)
            freed_pct = max(0.0, round((current_at - healthy_at) * 100.0, 2))

            if is_bottleneck:
                bottlenecks.append(
                    BottleneckDiagnosis(
                        cpe_id=sub.cpe_id,
                        is_bottleneck=True,
                        inefficiency_ratio=inefficiency,
                        airtime_consumed_pct=round(at_pct, 2),
                        goodput_delivered_mbps=round(goodputs[i], 2),
                        mcs=sub.mcs,
                        retry_pct=sub.retry_pct,
                        diagnosis_reason=" | ".join(reasons),
                        freed_airtime_pct_if_remediated=freed_pct,
                    )
                )

        return bottlenecks
