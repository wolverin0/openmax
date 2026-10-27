#!/usr/bin/env python3
"""
FuturaMAX Stage 12 — Mode A vs. Mode B Hidden-Node & Distance Crossover Audit
=============================================================================

Audits the exact physical, MAC-timing, and queueing crossover boundary between:
  - Mode A (OpenWrt Tuned CSMA/CA):
      mac80211 + ath10k-ct with RTS/CTS = 256B, Asymmetric Per-AC AQL
      (AP BE = 1500/3000 us, CPE BE = 2100/4200 us, VO/VI = 600/1200 us),
      ATF (airtime_flags=3), fq_codel (quantum=256B, target=10ms/50ms),
      TCP TSQ (128KB), and WMM AC_VO DiffServ Deficit Bypass (DSCP EF).
  - Mode B (Stock airOS 8 TDMA Polling):
      ubnt_poll_host.ko + umac.ko + athwlan_AR9888v2_ptmp_ap_bin / ptmp_sta_bin
      centralized AP polling (POLL-ENABLE, INFOTXQ, NO-TX-DETECT, addradio mode 1).

Evaluated across N = 2..32 CPEs and d = 1..14 km (including Stage 12 1.5 km steps).

Epistemic Classification (per AGENTS.md Section 2 & 6):
  - CONFIRMED ON BENCH: Stage 7.1-7.4 (N=3 multivendor PtMP, RTS/CTS=256B +18.5% UL
    goodput, WMM AC_VO Deficit Bypass 21.0x RTT reduction) and Stage 12 R60-R80
    (11-point declared distance / coverage-class grid 100 m .. 15,000 m).
  - CONFIRMED BY STATIC RE: Stage 10-12 ubnt_poll_host.ko + ptmp_ap_bin polling
    state machine, 30s missing-poll timer (.text+0x7c08), and INFOTXQ mechanics.
  - INFERRED / MODELED: Coupled Bianchi + hidden-node RTS vulnerability window +
    coverage-class slot inflation vs. TDMA polling turnaround overhead across
    N = 4..32 CPEs and outdoor propagation d = 1..14 km.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Speed of light in tropospheric air (m / us)
C_AIR_M_PER_US: float = 299.702547

# Standard IEEE 802.11ac (VHT20, 5 GHz) timing constants (us)
SIFS_US: float = 16.0
BaseSlot_US: float = 9.0
BaseACKTimeout_US: float = 18.0
RTS_DURATION_US: float = 20.0
CTS_DURATION_US: float = 20.0
BA_DURATION_US: float = 28.0
PHY_PREAMBLE_US: float = 20.0

# Stage 12 empirical distance anchors on 20 MHz VHT20 2x2 MIMO (6-flow bidir)
STAGE12_EMPIRICAL_ANCHORS: Dict[float, Dict[str, float]] = {
    0.1: {"run": 60, "class": 0, "slot_us": 9.0, "ack_us": 18.0, "stock_gp_mbps": 105.36, "mode_a_gp_mbps": 105.29, "mode_a_p50_ms": 5.95, "mode_a_p95_ms": 15.10, "mode_a_p99_ms": 22.40, "stock_p95_ms": 45.40},
    1.5: {"run": 76, "class": 3, "slot_us": 18.0, "ack_us": 36.0, "stock_gp_mbps": 108.92, "mode_a_gp_mbps": 107.41, "mode_a_p50_ms": 6.84, "mode_a_p95_ms": 21.73, "mode_a_p99_ms": 31.52, "stock_p95_ms": 46.08},
    3.0: {"run": 61, "class": 6, "slot_us": 27.0, "ack_us": 54.0, "stock_gp_mbps": 104.20, "mode_a_gp_mbps": 102.89, "mode_a_p50_ms": 6.60, "mode_a_p95_ms": 20.10, "mode_a_p99_ms": 29.80, "stock_p95_ms": 44.50},
    4.5: {"run": 70, "class": 10, "slot_us": 39.0, "ack_us": 78.0, "stock_gp_mbps": 98.80, "mode_a_gp_mbps": 97.32, "mode_a_p50_ms": 6.42, "mode_a_p95_ms": 19.40, "mode_a_p99_ms": 28.90, "stock_p95_ms": 43.20},
    6.0: {"run": 62, "class": 13, "slot_us": 48.0, "ack_us": 96.0, "stock_gp_mbps": 94.50, "mode_a_gp_mbps": 93.72, "mode_a_p50_ms": 6.30, "mode_a_p95_ms": 18.90, "mode_a_p99_ms": 28.10, "stock_p95_ms": 42.10},
    7.5: {"run": 77, "class": 16, "slot_us": 57.0, "ack_us": 114.0, "stock_gp_mbps": 91.78, "mode_a_gp_mbps": 89.92, "mode_a_p50_ms": 6.18, "mode_a_p95_ms": 18.37, "mode_a_p99_ms": 33.38, "stock_p95_ms": 41.60},
    9.0: {"run": 69, "class": 20, "slot_us": 69.0, "ack_us": 138.0, "stock_gp_mbps": 88.10, "mode_a_gp_mbps": 87.54, "mode_a_p50_ms": 5.95, "mode_a_p95_ms": 17.10, "mode_a_p99_ms": 25.80, "stock_p95_ms": 40.20},
    10.5: {"run": 78, "class": 23, "slot_us": 78.0, "ack_us": 156.0, "stock_gp_mbps": 85.14, "mode_a_gp_mbps": 84.43, "mode_a_p50_ms": 5.77, "mode_a_p95_ms": 15.78, "mode_a_p99_ms": 23.73, "stock_p95_ms": 39.50},
    12.0: {"run": 73, "class": 27, "slot_us": 90.0, "ack_us": 180.0, "stock_gp_mbps": 79.80, "mode_a_gp_mbps": 78.46, "mode_a_p50_ms": 5.45, "mode_a_p95_ms": 15.02, "mode_a_p99_ms": 21.30, "stock_p95_ms": 38.40},
    13.5: {"run": 79, "class": 30, "slot_us": 99.0, "ack_us": 198.0, "stock_gp_mbps": 74.36, "mode_a_gp_mbps": 74.94, "mode_a_p50_ms": 5.16, "mode_a_p95_ms": 14.25, "mode_a_p99_ms": 18.98, "stock_p95_ms": 37.80},
    15.0: {"run": 75, "class": 33, "slot_us": 108.0, "ack_us": 216.0, "stock_gp_mbps": 71.20, "mode_a_gp_mbps": 70.15, "mode_a_p50_ms": 5.05, "mode_a_p95_ms": 14.10, "mode_a_p99_ms": 18.70, "stock_p95_ms": 37.10},
}


@dataclass(frozen=True)
class RegimeSpec:
    """Defines a hidden-node and uplink traffic concurrency regime."""
    regime_id: str
    title: str
    alpha_hn: float        # Fraction of CPE pairs that are mutually hidden [0..1]
    rho_ul: float          # Active UL traffic concurrency factor under AQL/TSQ pacing [0..1]
    poll_active_ratio: float  # Fraction of N stations polled at high rate per TDMA cycle
    description: str


REGIMES: Dict[str, RegimeSpec] = {
    "regime_3_saturated_full_hn": RegimeSpec(
        regime_id="regime_3_saturated_full_hn",
        title="Regime 3: Worst-Case Saturated Full Hidden-Node Uplink (alpha_HN=1.0, rho_UL=1.0)",
        alpha_hn=1.0,
        rho_ul=1.0,
        poll_active_ratio=1.0,
        description=(
            "All N CPEs are simultaneously backlogged with continuous uplink traffic "
            "and 100% of CPE pairs are mutually hidden (cannot hear peer RTS frames, "
            "only the AP's broadcast CTS)."
        ),
    ),
    "regime_2_typical_wisp_sector": RegimeSpec(
        regime_id="regime_2_typical_wisp_sector",
        title="Regime 2: Typical 90-120 deg WISP Sector with Partial Clutter + AQL/TSQ Pacing (alpha_HN=0.50, rho_UL=0.35)",
        alpha_hn=0.50,
        rho_ul=0.35,
        poll_active_ratio=0.55,
        description=(
            "Representative outdoor 90-120 deg PtMP sector where 50% of CPE pairs are "
            "mutually hidden by terrain/foliage/azimuth and Cooperative CPE Asymmetric AQL "
            "(2100/4200 us) + TCP TSQ (128 KB) pace uplink bursts to 35% simultaneous contention."
        ),
    ),
    "regime_1_low_hn_narrow_sector": RegimeSpec(
        regime_id="regime_1_low_hn_narrow_sector",
        title="Regime 1: Narrow/LOS Sector or Light Uplink Contention (alpha_HN=0.15, rho_UL=0.25)",
        alpha_hn=0.15,
        rho_ul=0.25,
        poll_active_ratio=0.40,
        description=(
            "Narrow-beamwidth (30-60 deg horn/sector) or co-visible LOS cluster where 85% "
            "of CPE pairs hear each other's RTS preamble and AQL/TSQ keeps simultaneous "
            "uplink burst concurrency at 25%."
        ),
    ),
}


@dataclass
class DistanceTiming:
    """Physical and mac80211 coverage-class timing at distance d_km."""
    d_km: float
    one_way_prop_us: float
    rtt_prop_us: float
    coverage_class: int
    slot_time_us: float
    ack_cts_timeout_us: float
    aifs_be_us: float
    aifs_vo_us: float
    rts_vuln_window_us: float
    vuln_slots: float


@dataclass
class PointEvaluation:
    """Complete Mode A vs. Mode B evaluation at a single (N, d_km, regime) coordinate."""
    regime_id: str
    n_cpes: int
    d_km: float
    coverage_class: int
    slot_time_us: float
    ack_cts_timeout_us: float
    rtt_prop_us: float
    rts_vuln_window_us: float
    n_eff_contenders: float
    # Mode A metrics (OpenWrt CSMA/CA + RTS/CTS 256B + Asymmetric AQL + WMM AC_VO Bypass)
    mode_a_rts_collision_prob: float
    mode_a_ul_goodput_mbps: float
    mode_a_dl_goodput_mbps: float
    mode_a_total_goodput_mbps: float
    mode_a_ac_vo_p50_rtt_ms: float
    mode_a_ac_vo_p95_rtt_ms: float
    mode_a_ac_vo_p99_rtt_ms: float
    mode_a_ac_be_p95_rtt_ms: float
    mode_a_jain_fairness: float
    mode_a_fmx_score: float
    # Mode B metrics (Stock airOS 8 ubnt_poll_host.ko TDMA Polling)
    mode_b_poll_overhead_pct: float
    mode_b_poll_cycle_ms: float
    mode_b_ul_goodput_mbps: float
    mode_b_dl_goodput_mbps: float
    mode_b_total_goodput_mbps: float
    mode_b_p50_rtt_ms: float
    mode_b_p95_rtt_ms: float
    mode_b_p99_rtt_ms: float
    mode_b_jain_fairness: float
    mode_b_fmx_score: float
    # Winner & deltas
    winner_ul_goodput: str
    winner_total_goodput: str
    winner_interactive_p95_rtt: str
    winner_fmx_composite: str
    delta_total_goodput_mbps: float     # Mode A - Mode B
    delta_ul_goodput_mbps: float        # Mode A - Mode B
    delta_interactive_p95_ms: float     # Mode B p95 - Mode A AC_VO p95 (positive = Mode A lower latency)
    delta_fmx_score: float              # Mode A - Mode B


def compute_distance_timing(d_km: float) -> DistanceTiming:
    """
    Compute exact air propagation delay, mac80211 coverage class, slot time,
    ACK/CTS timeout, and hidden-node RTS vulnerability window at distance d_km.
    """
    d_m = max(0.0, d_km * 1000.0)
    one_way_us = d_m / C_AIR_M_PER_US
    rtt_us = 2.0 * one_way_us
    # Preserve exact Stage 12 declared coverage class on anchor points (e.g. 12.0 km -> class 27)
    anchor_key = round(d_km, 1)
    if anchor_key in STAGE12_EMPIRICAL_ANCHORS:
        cov_class = int(STAGE12_EMPIRICAL_ANCHORS[anchor_key]["class"])
    else:
        cov_class = min(33, int(math.floor(d_m / 450.0 + 1e-9)))
    slot_us = BaseSlot_US + 3.0 * cov_class
    ack_to_us = BaseACKTimeout_US + 6.0 * cov_class
    # WMM AIFS: AIFSN(BE)=3, AIFSN(VO)=2
    aifs_be_us = SIFS_US + 3.0 * slot_us
    aifs_vo_us = SIFS_US + 2.0 * slot_us
    # Hidden-node RTS vulnerability window: T_RTS (20 us) + SIFS (16 us) + 2*tau(d)
    rts_vuln_us = RTS_DURATION_US + SIFS_US + rtt_us
    vuln_slots = rts_vuln_us / slot_us
    return DistanceTiming(
        d_km=round(d_km, 3),
        one_way_prop_us=round(one_way_us, 3),
        rtt_prop_us=round(rtt_us, 3),
        coverage_class=cov_class,
        slot_time_us=round(slot_us, 3),
        ack_cts_timeout_us=round(ack_to_us, 3),
        aifs_be_us=round(aifs_be_us, 3),
        aifs_vo_us=round(aifs_vo_us, 3),
        rts_vuln_window_us=round(rts_vuln_us, 3),
        vuln_slots=round(vuln_slots, 4),
    )


def solve_mode_a_bianchi_hidden_node(
    n_eff: float,
    timing: DistanceTiming,
    alpha_hn: float,
    cw_min: int = 15,
    m_stages: int = 6,
) -> Tuple[float, float, float]:
    """
    Solve the coupled Bianchi + Hidden-Node RTS/CTS fixed-point equations for:
      - tau_slot: per-slot transmission attempt probability of an active contender
      - p_coll: conditional collision probability per RTS transmission attempt
      - mean_backoff_slots: expected backoff slots per successful TXOP

    Returns (tau_slot, p_coll, mean_backoff_slots).
    """
    if n_eff <= 1.0001:
        return (2.0 / (cw_min + 2.0), 0.0, cw_min / 2.0)

    # Hidden stations are blind across T_vuln(d), which spans vuln_slots = T_vuln / sigma(d).
    # In addition, async slot boundaries across hidden nodes add a 0.5-slot overlap factor.
    effective_hn_slots = timing.vuln_slots + 0.5
    n_others = max(0.0, n_eff - 1.0)
    exp_covis = (1.0 - alpha_hn) * n_others
    exp_hidden = alpha_hn * n_others * effective_hn_slots

    # Fixed-point iteration on p_coll in [0, 0.96]
    p = 0.12
    for _ in range(80):
        # Bianchi Attempt Probability given p
        if abs(1.0 - 2.0 * p) < 1e-6:
            tau = 2.0 / (cw_min + 1.0 + cw_min * m_stages / 2.0)
        else:
            num = 2.0 * (1.0 - 2.0 * p)
            den = (1.0 - 2.0 * p) * (cw_min + 1.0) + p * cw_min * (1.0 - math.pow(2.0 * p, m_stages))
            tau = max(1e-5, min(0.5, num / den))

        # Survival probability: no co-visible station transmits in the same slot AND
        # no hidden station starts an RTS within the vulnerability window.
        p_survive = math.pow(1.0 - tau, exp_covis + exp_hidden)
        p_new = min(0.95, max(0.0, 1.0 - p_survive))
        if abs(p_new - p) < 1e-7:
            p = p_new
            break
        p = 0.5 * p + 0.5 * p_new

    # Expected backoff slots across geometric retry stages
    mean_slots = 0.0
    prob_weight = 1.0 - p
    total_weight = 0.0
    for stage in range(m_stages + 1):
        cw_stage = (cw_min + 1) * (2 ** min(stage, m_stages)) - 1
        w_bar = cw_stage / 2.0
        w = prob_weight * (p ** stage) if stage < m_stages else (p ** m_stages)
        mean_slots += w * ((stage + 1) * w_bar)
        total_weight += w
    if total_weight > 0:
        mean_slots /= total_weight

    return (tau, p, mean_slots)


def interpolate_stage12_baseline_goodput(d_km: float) -> Tuple[float, float, float]:
    """
    Interpolate the single-link / baseline 20 MHz VHT20 total sector goodput (Mbps),
    Mode A UL share, and Stock UL share from the physical QCA988x Stage 12 R60-R80
    distance grid (0.1 km .. 15.0 km).
    """
    anchors = sorted(STAGE12_EMPIRICAL_ANCHORS.keys())
    if d_km <= anchors[0]:
        gp = STAGE12_EMPIRICAL_ANCHORS[anchors[0]]["mode_a_gp_mbps"]
    elif d_km >= anchors[-1]:
        gp = STAGE12_EMPIRICAL_ANCHORS[anchors[-1]]["mode_a_gp_mbps"]
    else:
        gp = 85.0
        for i in range(len(anchors) - 1):
            d0, d1 = anchors[i], anchors[i + 1]
            if d0 <= d_km <= d1:
                g0 = STAGE12_EMPIRICAL_ANCHORS[d0]["mode_a_gp_mbps"]
                g1 = STAGE12_EMPIRICAL_ANCHORS[d1]["mode_a_gp_mbps"]
                frac = (d_km - d0) / (d1 - d0)
                gp = g0 + frac * (g1 - g0)
                break
    # In Stage 12 R76-R79 (CONFIRMED ON BENCH), Mode A Asymmetric AQL (AP=1500us, CPE=2100us)
    # boosts bidirectional UL share to ~23.8% (e.g., R76: 24.41/107.41 = 22.7%, R78: 21.21/84.43 = 25.1%),
    # whereas Stock airOS / unpaced TDMA achieves ~18.5% UL share under bidirectional load.
    return (gp, 0.238, 0.185)


def evaluate_point(n_cpes: int, d_km: float, regime: RegimeSpec) -> PointEvaluation:
    """
    Evaluate both Mode A and Mode B at (n_cpes, d_km) under the specified RegimeSpec.
    """
    timing = compute_distance_timing(d_km)
    base_phy_goodput_mbps, mode_a_ul_share_base, mode_b_ul_share_base = (
        interpolate_stage12_baseline_goodput(d_km)
    )

    # Effective simultaneously contending uplink stations in Mode A
    n_eff = 1.0 + (n_cpes - 1.0) * regime.rho_ul
    _, p_coll, mean_backoff_slots = solve_mode_a_bianchi_hidden_node(
        n_eff=n_eff,
        timing=timing,
        alpha_hn=regime.alpha_hn,
    )

    # --- MODE A: OpenWrt CSMA/CA + RTS/CTS 256B + Asymmetric AQL + WMM AC_VO Bypass ---
    # Typical A-MPDU payload airtime under Asymmetric AQL (CPE BE=2100/4200 us, AP BE=1500/3000 us)
    t_payload_us = 1550.0
    # RTS/CTS 4-way handshake overhead per successful TXOP:
    t_rts_cts_oh_us = (
        RTS_DURATION_US
        + SIFS_US
        + CTS_DURATION_US
        + SIFS_US
        + SIFS_US
        + BA_DURATION_US
        + 2.0 * timing.rtt_prop_us
        + timing.aifs_be_us
    )
    # Single-link baseline TXOP duration (already absorbed into Stage 12 base_phy_goodput_mbps):
    w0_bar = 7.5
    t_base_single_us = t_payload_us + t_rts_cts_oh_us + w0_bar * timing.slot_time_us

    # Excess multi-station collision waste per successful TXOP:
    expected_collisions = p_coll / max(0.05, 1.0 - p_coll)
    t_single_collision_us = RTS_DURATION_US + timing.ack_cts_timeout_us + timing.aifs_be_us
    t_collision_waste_us = expected_collisions * t_single_collision_us

    # Excess backoff inflation from binary exponential backoff above single-station W0_bar:
    # Plus multi-station hidden-node slot desynchronization across coverage-class slots sigma(d)
    delta_backoff_slots = max(0.0, mean_backoff_slots - w0_bar) + 0.85 * max(0.0, n_eff - 1.0) * (1.0 + 0.6 * regime.alpha_hn)
    t_excess_backoff_us = delta_backoff_slots * timing.slot_time_us

    # Total Mode A TXOP duration including multi-station hidden-node RTS collisions and BEB inflation
    t_mode_a_txop_us = t_base_single_us + t_excess_backoff_us + t_collision_waste_us

    # Contention efficiency relative to single-link Stage 12 anchor at distance d
    contention_efficiency_a = t_base_single_us / max(t_base_single_us, t_mode_a_txop_us)

    # Uplink suffers direct multi-station hidden-node RTS collision & BEB slot inflation;
    # Downlink from the single AP is protected by AP CTS and Asymmetric AQL, suffering only
    # medium airtime sharing with UL collisions and TCP ACK pacing.
    mode_a_ul_gp = base_phy_goodput_mbps * mode_a_ul_share_base * contention_efficiency_a
    dl_efficiency_a = 1.0 - 0.52 * (1.0 - contention_efficiency_a)
    mode_a_dl_gp = base_phy_goodput_mbps * (1.0 - mode_a_ul_share_base) * dl_efficiency_a
    mode_a_total_gp = mode_a_ul_gp + mode_a_dl_gp

    # Mode A Interactive Latency (WMM AC_VO Deficit Bypass + Asymmetric AQL)
    # Anchored to Stage 7.4 (p50 = 6.80 ms, p95 = 8.15..18.37 ms at N=2..3)
    # AC_VO uses CWmin=3, CWmax=7, AIFSN=2 and bypasses negative AC_BE deficit (-67,099 us),
    # so its latency remains low until RF medium collision + CTS_Timeout waste saturates airtime.
    rf_congestion_delay_ms = (
        (t_collision_waste_us + 0.75 * t_excess_backoff_us) * max(0.0, n_eff - 1.0) / 1000.0
    )
    base_vo_p50_ms = 5.4 + 0.08 * d_km
    mode_a_vo_p50_ms = base_vo_p50_ms + 0.55 * rf_congestion_delay_ms
    mode_a_vo_p95_ms = (13.8 + 0.12 * d_km) + 1.85 * rf_congestion_delay_ms
    mode_a_vo_p99_ms = (20.5 + 0.18 * d_km) + 2.85 * rf_congestion_delay_ms
    # Bulk AC_BE p95 RTT (bounded by AQL 1500/2100 us + fq_codel 10ms/50ms + N sharing)
    mode_a_be_p95_ms = (16.5 + 0.15 * d_km) + 1.35 * max(0.0, n_eff - 1.0) + 2.35 * rf_congestion_delay_ms

    # Mode A Jain's Fairness Index (ATF airtime_flags=3 + RTS=256B holds >0.92 at low N,
    # degrades when hidden-node RTS collisions cause binary exponential backoff capture)
    mode_a_jain = max(0.52, min(0.99, 0.985 - 0.42 * (p_coll ** 1.5) - 0.0025 * max(0, n_cpes - 2)))

    # --- MODE B: Stock airOS 8 ubnt_poll_host.ko + athwlan_AR9888v2_ptmp_ap_bin TDMA ---
    # Zero hidden-node RTS collisions (addradio mode 1 halts autonomous CPE TX).
    # However, AP must poll stations across distance d_km:
    #   - Active polled stations: N_active_poll = max(1, n_cpes * poll_active_ratio)
    #   - Idle/background polled stations per superframe: N_idle_poll = (N - N_active_poll) * 0.40
    n_active_poll = max(1.0, n_cpes * regime.poll_active_ratio)
    n_idle_poll = max(0.0, n_cpes - n_active_poll) * 0.40

    # Per-active-poll overhead: Poll frame (36 us) + SIFS (16 us) + slot guard (24 us) + 2*tau(d) = 76 us + rtt_prop_us
    t_poll_active_oh_us = 76.0 + timing.rtt_prop_us
    # Per-idle-poll overhead (NO-TX-DETECT slot timeout in ptmp_ap_bin): 36 us + 32 us + 2*tau(d)
    t_poll_idle_oh_us = 68.0 + timing.rtt_prop_us

    # Mean UL slot payload duration per active polled CPE (us)
    t_ul_slot_payload_us = 1200.0
    # Downlink subframe burst duration per TDMA cycle (us)
    t_dl_subframe_us = 2600.0 + 340.0 * min(8.0, n_active_poll)

    # Fixed TDMA superframe DL/UL turnaround guard (180 us) + CBP ranging slots (220 us) = 400 us
    total_poll_oh_us = (
        n_active_poll * t_poll_active_oh_us
        + n_idle_poll * t_poll_idle_oh_us
        + 400.0
    )
    total_useful_tx_us = t_dl_subframe_us + n_active_poll * t_ul_slot_payload_us
    t_poll_cycle_us = total_useful_tx_us + total_poll_oh_us
    mode_b_poll_cycle_ms = t_poll_cycle_us / 1000.0
    mode_b_poll_oh_pct = 100.0 * total_poll_oh_us / t_poll_cycle_us

    # Fundamental physical distinction between CSMA/CA (Mode A) and TDMA Polling (Mode B):
    # In CSMA/CA, round-trip propagation 2*tau(d) is paid ON EVERY BACKOFF SLOT (sigma(d) = 9 + 3*c(d)),
    # costing (AIFSN + W0_bar) * 3*c(d) = 10.5 * 3*c(d) us per TXOP even at N=1.
    # In TDMA (ubnt_poll_host.ko), there are NO random backoff slots; 2*tau(d) is paid ONLY ONCE
    # per poll turnaround! Thus as distance d grows, TDMA recovers the single-link CSMA slot-tax:
    single_link_csma_slot_tax_us = 8.5 * (timing.slot_time_us - BaseSlot_US)
    csma_single_link_slot_recovery = 1.0 + 0.42 * (single_link_csma_slot_tax_us / t_base_single_us)
    tdma_efficiency = (total_useful_tx_us / t_poll_cycle_us) * csma_single_link_slot_recovery
    mode_b_total_gp = base_phy_goodput_mbps * tdma_efficiency
    # Under multi-station load, TDMA polling guarantees deterministic UL slot allocation
    mode_b_ul_gp = mode_b_total_gp * mode_b_ul_share_base
    mode_b_dl_gp = mode_b_total_gp * (1.0 - mode_b_ul_share_base)

    # Mode B Latency: Stock airOS 8 lacks mac80211 AQL (1500/3000 us), fq_codel (256B), and
    # WMM AC_VO Deficit Bypass. Loaded latency is governed by:
    #   1. Unmanaged INFOTXQ / driver queue soak (~18 ms p50, ~36 ms p95 at N=1..2 per Stage 12 baseline)
    #   2. TDMA token rotation wait across N stations: +0.55 * mode_b_poll_cycle_ms (p50)
    #      and +1.25 * mode_b_poll_cycle_ms (p95)
    mode_b_p50_ms = 16.5 + 0.12 * d_km + 0.65 * mode_b_poll_cycle_ms
    mode_b_p95_ms = 34.0 + 0.25 * d_km + 1.30 * mode_b_poll_cycle_ms
    mode_b_p99_ms = 48.0 + 0.35 * d_km + 1.85 * mode_b_poll_cycle_ms

    # Mode B Jain's Fairness Index: deterministic round-robin TDMA polling keeps fairness >= 0.94
    mode_b_jain = max(0.93, 0.985 - 0.0012 * n_cpes)

    # --- Composite FuturaMAX Operational Score (0..100 scale, higher is better) ---
    # Weights:
    #   - 45%: Total Sector Goodput (normalized to base_phy_goodput_mbps)
    #   - 25%: Uplink Goodput under Hidden-Node load (normalized to base UL capacity)
    #   - 20%: Interactive p95 Latency penalty (20 ms target reference)
    #   - 10%: Jain's Fairness Index
    base_ul_ref = max(1.0, base_phy_goodput_mbps * mode_a_ul_share_base)
    mode_a_fmx_score = (
        45.0 * (mode_a_total_gp / base_phy_goodput_mbps)
        + 25.0 * (mode_a_ul_gp / base_ul_ref)
        + 20.0 * max(0.0, 1.0 - (mode_a_vo_p95_ms - 12.0) / 45.0)
        + 10.0 * mode_a_jain
    )
    mode_b_fmx_score = (
        45.0 * (mode_b_total_gp / base_phy_goodput_mbps)
        + 25.0 * (mode_b_ul_gp / base_ul_ref)
        + 20.0 * max(0.0, 1.0 - (mode_b_p95_ms - 12.0) / 45.0)
        + 10.0 * mode_b_jain
    )

    winner_ul = "Mode A" if mode_a_ul_gp >= mode_b_ul_gp else "Mode B"
    winner_tot = "Mode A" if mode_a_total_gp >= mode_b_total_gp else "Mode B"
    winner_lat = "Mode A" if mode_a_vo_p95_ms <= mode_b_p95_ms else "Mode B"
    winner_fmx = "Mode A" if mode_a_fmx_score >= mode_b_fmx_score else "Mode B"

    return PointEvaluation(
        regime_id=regime.regime_id,
        n_cpes=n_cpes,
        d_km=round(d_km, 2),
        coverage_class=timing.coverage_class,
        slot_time_us=timing.slot_time_us,
        ack_cts_timeout_us=timing.ack_cts_timeout_us,
        rtt_prop_us=timing.rtt_prop_us,
        rts_vuln_window_us=timing.rts_vuln_window_us,
        n_eff_contenders=round(n_eff, 2),
        mode_a_rts_collision_prob=round(p_coll, 4),
        mode_a_ul_goodput_mbps=round(mode_a_ul_gp, 2),
        mode_a_dl_goodput_mbps=round(mode_a_dl_gp, 2),
        mode_a_total_goodput_mbps=round(mode_a_total_gp, 2),
        mode_a_ac_vo_p50_rtt_ms=round(mode_a_vo_p50_ms, 2),
        mode_a_ac_vo_p95_rtt_ms=round(mode_a_vo_p95_ms, 2),
        mode_a_ac_vo_p99_rtt_ms=round(mode_a_vo_p99_ms, 2),
        mode_a_ac_be_p95_rtt_ms=round(mode_a_be_p95_ms, 2),
        mode_a_jain_fairness=round(mode_a_jain, 4),
        mode_a_fmx_score=round(mode_a_fmx_score, 2),
        mode_b_poll_overhead_pct=round(mode_b_poll_oh_pct, 2),
        mode_b_poll_cycle_ms=round(mode_b_poll_cycle_ms, 2),
        mode_b_ul_goodput_mbps=round(mode_b_ul_gp, 2),
        mode_b_dl_goodput_mbps=round(mode_b_dl_gp, 2),
        mode_b_total_goodput_mbps=round(mode_b_total_gp, 2),
        mode_b_p50_rtt_ms=round(mode_b_p50_ms, 2),
        mode_b_p95_rtt_ms=round(mode_b_p95_ms, 2),
        mode_b_p99_rtt_ms=round(mode_b_p99_ms, 2),
        mode_b_jain_fairness=round(mode_b_jain, 4),
        mode_b_fmx_score=round(mode_b_fmx_score, 2),
        winner_ul_goodput=winner_ul,
        winner_total_goodput=winner_tot,
        winner_interactive_p95_rtt=winner_lat,
        winner_fmx_composite=winner_fmx,
        delta_total_goodput_mbps=round(mode_a_total_gp - mode_b_total_gp, 2),
        delta_ul_goodput_mbps=round(mode_a_ul_gp - mode_b_ul_gp, 2),
        delta_interactive_p95_ms=round(mode_b_p95_ms - mode_a_vo_p95_ms, 2),
        delta_fmx_score=round(mode_a_fmx_score - mode_b_fmx_score, 2),
    )


def find_crossover_n_for_distance(
    d_km: float,
    regime: RegimeSpec,
    n_values: List[int],
) -> Dict[str, Optional[int]]:
    """
    Find the minimum N in n_values at distance d_km where Mode B overtakes Mode A
    for each primary metric:
      - n_star_fmx_composite: Mode B FMX composite score > Mode A FMX composite score
      - n_star_total_goodput: Mode B total goodput > Mode A total goodput
      - n_star_ul_goodput: Mode B UL goodput > Mode A UL goodput
      - n_star_interactive_p95: Mode B p95 RTT < Mode A AC_VO p95 RTT
    """
    n_star_fmx: Optional[int] = None
    n_star_tot: Optional[int] = None
    n_star_ul: Optional[int] = None
    n_star_lat: Optional[int] = None

    for n in n_values:
        pt = evaluate_point(n, d_km, regime)
        if n_star_fmx is None and pt.winner_fmx_composite == "Mode B":
            n_star_fmx = n
        if n_star_tot is None and pt.winner_total_goodput == "Mode B":
            n_star_tot = n
        if n_star_ul is None and pt.winner_ul_goodput == "Mode B":
            n_star_ul = n
        if n_star_lat is None and pt.winner_interactive_p95_rtt == "Mode B":
            n_star_lat = n

    return {
        "n_star_fmx_composite": n_star_fmx,
        "n_star_total_goodput": n_star_tot,
        "n_star_ul_goodput": n_star_ul,
        "n_star_interactive_p95": n_star_lat,
    }


def run_full_audit() -> Dict[str, object]:
    """
    Execute the complete N = 2..32 x d = 1..14 km crossover audit across all 3 regimes.
    """
    # Include all integer km 1..14 plus the exact Stage 12 half-km bench points
    distances_km: List[float] = sorted(
        list({float(d) for d in range(1, 15)} | {1.5, 4.5, 7.5, 10.5, 13.5})
    )
    n_values: List[int] = list(range(2, 33))

    timing_table = [asdict(compute_distance_timing(d)) for d in distances_km]

    regime_results: Dict[str, Dict[str, object]] = {}
    for regime_id, regime in REGIMES.items():
        grid_points: List[Dict[str, object]] = []
        crossover_by_distance: List[Dict[str, object]] = []

        for d_km in distances_km:
            timing = compute_distance_timing(d_km)
            xover = find_crossover_n_for_distance(d_km, regime, n_values)
            crossover_by_distance.append(
                {
                    "d_km": d_km,
                    "coverage_class": timing.coverage_class,
                    "slot_time_us": timing.slot_time_us,
                    "ack_cts_timeout_us": timing.ack_cts_timeout_us,
                    "rts_vuln_window_us": timing.rts_vuln_window_us,
                    **xover,
                }
            )
            for n in n_values:
                pt = evaluate_point(n, d_km, regime)
                grid_points.append(asdict(pt))

        regime_results[regime_id] = {
            "spec": asdict(regime),
            "crossover_by_distance": crossover_by_distance,
            "grid": grid_points,
        }

    return {
        "audit_id": "FMX-STAGE12-MODE-A-VS-MODE-B-CROSSOVER-20261024",
        "scope": {
            "n_cpes_min": 2,
            "n_cpes_max": 32,
            "d_km_min": 1.0,
            "d_km_max": 14.0,
            "distances_evaluated_km": distances_km,
            "channel_width_mhz": 20,
            "phy_mode": "VHT20 2x2 MIMO (MCS 7/8 LOS + mixed edge SNR)",
        },
        "epistemic_classification": {
            "CONFIRMED_ON_BENCH": [
                "Stage 7.2: ATF (airtime_flags=3) + AQL (1500/3000 us) cuts loaded p50 RTT by 4.06x (51.35 -> 12.65 ms) and TCP retransmits by 10x (158 -> 16).",
                "Stage 7.3: RTS/CTS = 256B under 3-station hidden-node UL contention boosts total sector UL goodput by +18.5% (150.40 -> 178.17 Mbps) and weak NLOS CPE goodput by 3.07x (1.97 -> 6.03 Mbps).",
                "Stage 7.4: WMM AC_VO DiffServ Deficit Bypass (DSCP EF -> Deficit: VO +256 us) bypasses negative Deficit: BE (-67,099 us), cutting weak-station p50 RTT by 21.0x (143.00 -> 6.80 ms).",
                "Stage 12 R60-R80: 11-point declared distance / coverage-class grid (100 m .. 15,000 m, class 0..33) verified on physical QCA988x bench with <2% goodput loss and 2.1x-3.0x p95 RTT reduction vs stock.",
            ],
            "CONFIRMED_BY_STATIC_RE": [
                "Stage 10-12: Stock airOS 8 TDMA uses ubnt_poll_host.ko + umac.ko + athwlan_AR9888v2_ptmp_ap_bin / ptmp_sta_bin with addradio mode 1 autonomous TX suppression, 30s missing-poll timer (.text+0x7c08), INFOTXQ, and NO-TX-DETECT.",
            ],
            "INFERRED_MODELED": [
                "Coupled Bianchi + hidden-node RTS vulnerability window T_vuln(d) = 36 + 6.671*d_km us and coverage-class slot inflation sigma(d) = 9 + 3*c(d) us vs. TDMA polling turnaround overhead across N = 4..32 CPEs and d = 1..14 km.",
            ],
        },
        "distance_timing_table": timing_table,
        "stage12_empirical_anchors": STAGE12_EMPIRICAL_ANCHORS,
        "regimes": regime_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit the exact Mode A vs Mode B hidden-node crossover boundary across N=2..32 and d=1..14 km."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/autoresearch/mode_a_vs_mode_b_crossover_20261024.json"),
        help="Output JSON artifact path.",
    )
    args = parser.parse_args()

    result = run_full_audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"[OK] Wrote {args.output} ({args.output.stat().st_size:,} bytes)")
    print("\n=== SUMMARY OF CRITICAL CROSSOVER N*(d): [UL_GP / TOT_GP / FMX_QOE / VO_P95] ===")
    header = (
        f"{'d (km)':>6} | {'Class':>5} | {'Slot':>6} | {'T_vuln':>8} | "
        f"{'R3 Sat HN (UL/Tot/FMX/p95)':>26} | "
        f"{'R2 WISP (UL/Tot/FMX/p95)':>24} | "
        f"{'R1 Low HN (UL/Tot/FMX/p95)':>26}"
    )
    print(header)
    print("-" * len(header))

    r3_map = {row["d_km"]: row for row in result["regimes"]["regime_3_saturated_full_hn"]["crossover_by_distance"]}
    r2_map = {row["d_km"]: row for row in result["regimes"]["regime_2_typical_wisp_sector"]["crossover_by_distance"]}
    r1_map = {row["d_km"]: row for row in result["regimes"]["regime_1_low_hn_narrow_sector"]["crossover_by_distance"]}

    def _fmt(row: Dict[str, object]) -> str:
        u = row["n_star_ul_goodput"] or ">32"
        t = row["n_star_total_goodput"] or ">32"
        f = row["n_star_fmx_composite"] or ">32"
        l = row["n_star_interactive_p95"] or ">32"
        return f"{u:>3}/{t:>3}/{f:>3}/{l:>3}"

    for t in result["distance_timing_table"]:
        d = t["d_km"]
        r3_s = _fmt(r3_map[d])
        r2_s = _fmt(r2_map[d])
        r1_s = _fmt(r1_map[d])
        print(
            f"{d:6.1f} | {t['coverage_class']:5d} | {t['slot_time_us']:4.0f}us | {t['rts_vuln_window_us']:6.1f}us | "
            f"{r3_s:>26} | {r2_s:>24} | {r1_s:>26}"
        )


if __name__ == "__main__":
    main()
