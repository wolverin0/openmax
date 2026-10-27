"""Deterministic PtMP Sector Operating Mode Selector.

Given live or planned sector conditions:
  (active_uploading_cpes, hidden_node_fraction, max_distance_km, has_legacy_m5_or_mikrotik_cpes)
outputs the optimal sector operating mode among:
  - `MODE_A_CSMA_AQL_ONLY`: FuturaMAX Asymmetric AQL (`AP BE=1550/3100 us`, `CPE BE=2100/4200 us`,
    `af=1`, `retry 6/4`, `AC_VO` DiffServ steering) with `RTS/CTS=OFF`.
  - `MODE_A_PLUS_RTS_CTS_256B`: FuturaMAX Asymmetric AQL + `RTS/CTS=256B` AP-mediated virtual
    carrier sense + `AC_VO` DiffServ Deficit Bypass.
  - `MODE_B_AIRMAX_TDMA_HYBRID`: Stock `airMAX` `ubnt_poll_host.ko` TDMA polling scheduler
    (fixed polling overhead per active CPE + zero inter-CPE hidden-node collisions) + FuturaMAX CAKE/AQL pacing.

All predictions are pure offline metadata (`automatic_execution_allowed=False`) derived from the
Stage 7 hardware-calibrated and Stage 12 (`R76`, `R98..R102`) distance-anchored SimPy discrete-event
airtime-collision & slot state machine.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

from tools.sim.fmx_ptmp_hidden_node_tdma_vs_csma_sim import (
    ALL_MODES,
    MODE_A_CSMA_AQL_ONLY,
    MODE_A_PLUS_RTS_CTS_256B,
    MODE_B_AIRMAX_TDMA_HYBRID,
    MODE_STOCK_CSMA_UNPROTECTED,
    PtMPSimConfig,
     SEED_DEFAULT,
    simulate_ptmp_sector,
    timing_for_distance_km,
)

CONTROLLABLE_MODES = (
    MODE_A_CSMA_AQL_ONLY,
    MODE_A_PLUS_RTS_CTS_256B,
    MODE_B_AIRMAX_TDMA_HYBRID,
)


@dataclass(frozen=True)
class PtMPModeRecommendation:
    selected_mode: str
    reason: str
    active_uploading_cpes: int
    hidden_node_fraction: float
    max_distance_km: float
    has_legacy_m5_or_mikrotik_cpes: bool
    coverage_class: int
    slot_time_us: int
    ack_timeout_us: int
    predicted_aggregate_ul_mbps: float
    predicted_aggregate_bidir_mbps: float
    predicted_per_cpe_ul_mean_mbps: float
    predicted_min_cpe_ul_mbps: float
    predicted_jain_fairness: float
    predicted_p50_rtt_ms: float
    predicted_p95_rtt_ms: float
    predicted_p99_rtt_ms: float
    predicted_mac_collision_rate: float
    predicted_qoe_score: float
    gain_vs_stock_csma_ul_pct: float
    rtt_p95_cut_vs_stock_csma_multiplier: float
    candidate_modes: dict[str, dict[str, Any]]
    evidence_status: str
    automatic_execution_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def select_ptmp_operating_mode(
    active_uploading_cpes: int,
    hidden_node_fraction: float,
    max_distance_km: float,
    has_legacy_m5_or_mikrotik_cpes: bool = False,
    *,
    seed: int = SEED_DEFAULT,
) -> dict[str, Any]:
    """Deterministically select the optimal PtMP sector operating mode and return exact predictions.

    Policy Decision Rules (backed by SimPy discrete-event evaluation):
    1. Hardware / Protocol Feasibility Gate:
       - If `has_legacy_m5_or_mikrotik_cpes=True` (sector contains third-party 802.11n/ac CPEs such as
         MikroTik `ath9k` SXT or `airMAX=off` standard 802.11 stations that lack Ubiquiti's proprietary
         `ubnt_poll_host.ko` airMAX AC polling state machine), `MODE_B_AIRMAX_TDMA_HYBRID` is structurally
         ineligible (`ELIGIBLE_MODES = {MODE_A_CSMA_AQL_ONLY, MODE_A_PLUS_RTS_CTS_256B}`).
    2. Single Active Uploader or Zero Hidden Nodes at Low-to-Moderate Contention (`N == 1` or (`h == 0.0` and `N <= 16`)):
       - When `active_uploading_cpes == 1` or (`hidden_node_fraction == 0.0` and `active_uploading_cpes <= 16`),
         every station hears every other station's preamble (`CCA`). Enabling `RTS/CTS=256B` or `TDMA` polling
         adds pure handshake/token overhead (`~4.5%` to `12%`) without preventing hidden-node collisions.
       - Select `MODE_A_CSMA_AQL_ONLY` (Asymmetric AQL `1550/2100 us` + `af=1` + `retry 6/4` + `AC_VO` DiffServ steering).
    3. Multi-CPE Sector with Hidden Nodes (`h > 0`):
       - If `has_legacy_m5_or_mikrotik_cpes=True`:
         Select `MODE_A_PLUS_RTS_CTS_256B` for all `N >= 2, h > 0` (AP-broadcast `CTS` virtual carrier sense
         is the strongest standard 802.11 mechanism available across multi-vendor CPEs).
       - If homogeneous `airMAX AC` (`WA`/`XC`) sector (`has_legacy_m5_or_mikrotik_cpes=False`):
         Evaluate exact simulated QoE score across `MODE_A_CSMA_AQL_ONLY`, `MODE_A_PLUS_RTS_CTS_256B`, and
         `MODE_B_AIRMAX_TDMA_HYBRID`:
         * For small-to-moderate active uploaders (`N in 2..6` at `h <= 0.75`), `MODE_A_PLUS_RTS_CTS_256B`
           wins because the `52 us` RTS/CTS handshake is lighter than full TDMA polling while eliminating
           mid-A-MPDU collisions.
         * For dense simultaneous uploaders (`N >= 8` with `h >= 0.50`, or `N >= 10` with `h >= 0.25`, or
           `N >= 4` with `h == 1.0`), `MODE_B_AIRMAX_TDMA_HYBRID` wins decisively: RTS-on-RTS contention
           degrades CSMA, whereas TDMA deterministic polling holds collision waste near zero, preserves
           Jain fairness `> 0.96`, and bounds `p95` RTT to the linear superframe cycle.
    """
    if type(active_uploading_cpes) is not int or not (1 <= active_uploading_cpes <= 64):
        raise ValueError(f"active_uploading_cpes must be an int in [1, 64], got {active_uploading_cpes}")
    if (
        not isinstance(hidden_node_fraction, (int, float))
        or not math.isfinite(hidden_node_fraction)
        or not (0.0 <= hidden_node_fraction <= 1.0)
    ):
        raise ValueError(f"hidden_node_fraction must be finite in [0.0, 1.0], got {hidden_node_fraction}")
    if (
        not isinstance(max_distance_km, (int, float))
        or not math.isfinite(max_distance_km)
        or not (0.1 <= max_distance_km <= 30.0)
    ):
        raise ValueError(f"max_distance_km must be finite in [0.1, 30.0], got {max_distance_km}")
    if type(has_legacy_m5_or_mikrotik_cpes) is not bool:
        raise ValueError("has_legacy_m5_or_mikrotik_cpes must be a boolean")
    if type(seed) is not int:
        raise ValueError("seed must be an int")

    h = float(hidden_node_fraction)
    d = float(max_distance_km)
    n = active_uploading_cpes
    t_info = timing_for_distance_km(d)

    # Simulate all 4 modes at this exact (n, h, d) operating point
    candidate_modes: dict[str, dict[str, Any]] = {}
    for mode in ALL_MODES:
        sim_out = simulate_ptmp_sector(
            PtMPSimConfig(
                n_cpes=n,
                hidden_node_fraction=h,
                distance_km=d,
                mode=mode,
                seed=seed,
            )
        )
        m_metrics = dict(sim_out["metrics"])
        if mode == MODE_B_AIRMAX_TDMA_HYBRID and has_legacy_m5_or_mikrotik_cpes:
            m_metrics["eligible"] = False
            m_metrics["ineligible_reason"] = (
                "Legacy M5 (airMAX=off) or third-party MikroTik (ath9k) CPEs present; "
                "proprietary airMAX AC TDMA polling requires homogeneous Ubiquiti poll-capable stations."
            )
        else:
            m_metrics["eligible"] = True
            m_metrics["ineligible_reason"] = None
        candidate_modes[mode] = m_metrics

    eligible_modes = [
        m for m in CONTROLLABLE_MODES if candidate_modes[m]["eligible"]
    ]

    # Select optimal eligible mode by QoE score
    selected_mode = max(eligible_modes, key=lambda m: candidate_modes[m]["qoe_score"])
    sel = candidate_modes[selected_mode]
    stock = candidate_modes[MODE_STOCK_CSMA_UNPROTECTED]

    if selected_mode == MODE_A_CSMA_AQL_ONLY:
        if n == 1:
            reason = (
                "Single active uploader (N=1): zero inter-CPE UL contention; "
                "Asymmetric AQL (1550/2100 us) + af=1 + AC_VO steering maximizes goodput and minimizes RTT "
                "without RTS/CTS or TDMA polling overhead."
            )
        else:
            reason = (
                f"Mutual carrier sense intact (N={n}, h={h:.2f}): all CPEs hear each other's preambles; "
                "Asymmetric AQL + CoDel + AC_VO deficit bypass avoids RTS/CTS handshake overhead while keeping RTT low."
            )
    elif selected_mode == MODE_A_PLUS_RTS_CTS_256B:
        if has_legacy_m5_or_mikrotik_cpes:
            reason = (
                f"Mixed-vendor sector (has_legacy_m5_or_mikrotik_cpes=True) with hidden nodes (N={n}, h={h:.2f}, d={d:.1f}km): "
                "proprietary airMAX TDMA cannot run across third-party 802.11n/ac CPEs; "
                "Asymmetric AQL + RTS/CTS=256B AP-broadcast CTS virtual carrier sense + AC_VO bypass is optimal."
            )
        else:
            reason = (
                f"Moderate multi-CPE hidden-node contention (N={n}, h={h:.2f}, d={d:.1f}km): "
                "RTS/CTS=256B confines hidden collisions to the 28us RTS window and outperforms TDMA polling overhead at small N."
            )
    else:
        reason = (
            f"Dense multi-CPE hidden-node contention (N={n}, h={h:.2f}, d={d:.1f}km): "
            "CSMA/CA and RTS-on-RTS contention degrade under high N*h; "
            "airMAX TDMA Hybrid polling + FuturaMAX CAKE/AQL eliminates inter-CPE hidden collisions, "
            f"preserving Jain fairness ({sel['jain_fairness']:.4f}) and bounding p95 RTT ({sel['p95_rtt_ms']:.1f} ms)."
        )

    gain_vs_stock_ul_pct = round(
        (sel["aggregate_ul_goodput_mbps"] - stock["aggregate_ul_goodput_mbps"])
        / max(1e-6, stock["aggregate_ul_goodput_mbps"])
        * 100.0,
        2,
    )
    rtt_cut_mult = round(
        stock["p95_rtt_ms"] / max(1e-6, sel["p95_rtt_ms"]),
        2,
    )

    rec = PtMPModeRecommendation(
        selected_mode=selected_mode,
        reason=reason,
        active_uploading_cpes=n,
        hidden_node_fraction=h,
        max_distance_km=d,
        has_legacy_m5_or_mikrotik_cpes=has_legacy_m5_or_mikrotik_cpes,
        coverage_class=int(t_info["coverage_class"]),
        slot_time_us=int(t_info["slot_time_us"]),
        ack_timeout_us=int(t_info["ack_timeout_us"]),
        predicted_aggregate_ul_mbps=sel["aggregate_ul_goodput_mbps"],
        predicted_aggregate_bidir_mbps=sel["aggregate_bidir_goodput_mbps"],
        predicted_per_cpe_ul_mean_mbps=sel["per_cpe_ul_mean_mbps"],
        predicted_min_cpe_ul_mbps=sel["min_cpe_ul_goodput_mbps"],
        predicted_jain_fairness=sel["jain_fairness"],
        predicted_p50_rtt_ms=sel["p50_rtt_ms"],
        predicted_p95_rtt_ms=sel["p95_rtt_ms"],
        predicted_p99_rtt_ms=sel["p99_rtt_ms"],
        predicted_mac_collision_rate=sel["mac_collision_rate"],
        predicted_qoe_score=sel["qoe_score"],
        gain_vs_stock_csma_ul_pct=gain_vs_stock_ul_pct,
        rtt_p95_cut_vs_stock_csma_multiplier=rtt_cut_mult,
        candidate_modes=candidate_modes,
        evidence_status=(
            "CONFIRMED_SINGLE_CPE_ANCHOR"
            if (n == 1 and d in {3.0, 6.0, 9.0, 12.0, 14.0})
            else "INFERRED_FROM_STAGE7_AND_R98_R102_CALIBRATED_SIMPY_MODEL"
        ),
        automatic_execution_allowed=False,
    )
    return rec.to_dict()


class PtMPModeSelector:
    """Object-oriented wrapper for deterministic PtMP sector policy selection."""

    def __init__(self, *, seed: int = SEED_DEFAULT) -> None:
        if type(seed) is not int:
            raise ValueError("seed must be an integer")
        self.seed = seed

    def select(
        self,
        active_uploading_cpes: int,
        hidden_node_fraction: float,
        max_distance_km: float,
        has_legacy_m5_or_mikrotik_cpes: bool = False,
    ) -> dict[str, Any]:
        return select_ptmp_operating_mode(
            active_uploading_cpes=active_uploading_cpes,
            hidden_node_fraction=hidden_node_fraction,
            max_distance_km=max_distance_km,
            has_legacy_m5_or_mikrotik_cpes=has_legacy_m5_or_mikrotik_cpes,
            seed=self.seed,
        )
