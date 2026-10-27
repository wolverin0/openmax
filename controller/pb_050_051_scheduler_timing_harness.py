#!/usr/bin/env python3
"""PB-050 & PB-051 Harness: Host Queue-Gating vs Target TSF Timer Jitter Analyzer & Slot Gate Verifier.

Implements the offline timing analyzer, guard-interval floor calculator, out-of-slot CSMA
leakage verifier, and paired A/B/A/B evaluator for:
1. Gate PB-050: Host queue-gating (Linux hrtimer + mac80211 TXQ/AQL/WMI) vs QCA988x target
   TSF/PCU timer-resolution benchmark measured by external SDR burst-edge timestamps.
2. Gate PB-051: Target-resident sub-ms / 2ms slot scheduler feasibility gate under 2-CPE
   hidden-node contention, enforcing:
   - out_of_slot_tx_violation_rate_pct < 0.5%
   - slot_boundary_jitter_p99_us < 250.0 us
   - paired A/B/A/B hidden-node goodput_per_mhz and p99 latency promotion via RegressionGatekeeper.

Array-based timing/feasibility reports are diagnostics only. Fresh QoE campaigns
must use the source-bound Stage959A A/A, discovery and disjoint holdout runner.
Enforces `automatic_execution_allowed = False` during Phase 0.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from analysis.metrics.schema import validate_channel_width_mhz
from analysis.regression_gate.gatekeeper import RegressionGatekeeper, RunMetrics
from research.physical_boundary.ladder_schema import check_gate_readiness, load_ladder

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_OUTPUT_PATH = REPO_ROOT / "artifacts/qca988x/pb_050_051_timing_jitter_fixture.json"
PHYSICAL_EXPERIMENT_ROLE = 'PB050_051_SCHEDULER_TIMING'


def freeze_physical_retest_plan(**kwargs) -> Dict[str, Any]:
    """Freeze the explicit acquisition/configuration contract for this controller."""
    if 'experiment_role' in kwargs:
        raise ValueError('controller experiment role is fixed')
    from tools.autoresearch import run_stage959a_unified_physical_retest_runner as unified
    return unified.freeze_plan(experiment_role=PHYSICAL_EXPERIMENT_ROLE, **kwargs)


def run_physical_retest(plan, *, acquire_window, evidence_root, execute=False) -> Dict[str, Any]:
    """Run source-bound QoE retesting; external SDR timing acceptance is separate."""
    if not isinstance(plan, dict) or plan.get('experiment_role') != PHYSICAL_EXPERIMENT_ROLE:
        raise ValueError('wrong controller experiment role')
    from tools.autoresearch import run_stage959a_unified_physical_retest_runner as unified
    return unified.run_campaign(plan, acquire_window=acquire_window,
                                evidence_root=evidence_root, execute=execute)

SPEED_OF_LIGHT_US_PER_KM_ROUNDTRIP = 6.67128  # 2 * 1000m / (2.99792458e8 m/s) in microseconds
SIFS_PLUS_RXTX_TURNAROUND_US = 32.0           # 16us SIFS + 16us BB/RF switch margin


@dataclass(frozen=True)
class SdrBurstObservation:
    burst_id: int
    peer_id: str
    scheduled_slot_start_us: float
    scheduled_slot_duration_us: float
    assigned_guard_us: float
    observed_rf_start_us: float
    observed_rf_end_us: float


def _percentile(sorted_vals: Sequence[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    pos = (len(sorted_vals) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(sorted_vals[lo])
    frac = pos - lo
    return float(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac)


def compute_burst_edge_jitter_cdf(
    observations: Sequence[SdrBurstObservation],
    distance_km: float = 6.0,
) -> Dict[str, Any]:
    """Computes TX start-edge jitter CDF (p50/p95/p99), safe guard floor, and out-of-slot CSMA leakage."""
    if not observations:
        raise ValueError("observations must be non-empty.")
    if type(distance_km) not in (int, float) or not math.isfinite(distance_km) or distance_km < 0.0:
        raise ValueError("distance_km must be >= 0.0")

    jitters_us: List[float] = []
    out_of_slot_count = 0

    seen_bursts = set()
    for obs in observations:
        if obs.burst_id in seen_bursts:
            raise ValueError('duplicate SDR burst identity')
        seen_bursts.add(obs.burst_id)
        for field in ('scheduled_slot_start_us', 'scheduled_slot_duration_us', 'assigned_guard_us',
                      'observed_rf_start_us', 'observed_rf_end_us'):
            value = getattr(obs, field)
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError('finite SDR timing observations required')
        if (obs.scheduled_slot_duration_us <= 0 or obs.assigned_guard_us < 0
                or obs.assigned_guard_us > obs.scheduled_slot_duration_us
                or obs.observed_rf_end_us < obs.observed_rf_start_us):
            raise ValueError('invalid SDR interval or guard')
        jitter = abs(obs.observed_rf_start_us - obs.scheduled_slot_start_us)
        jitters_us.append(jitter)
        usable_end = obs.scheduled_slot_start_us + obs.scheduled_slot_duration_us - obs.assigned_guard_us
        # Violation if burst starts before scheduled start - 10us or extends past usable slot end + assigned_guard_us
        hard_slot_end = obs.scheduled_slot_start_us + obs.scheduled_slot_duration_us
        if obs.observed_rf_start_us < (obs.scheduled_slot_start_us - 10.0) or obs.observed_rf_end_us > hard_slot_end:
            out_of_slot_count += 1
        elif obs.observed_rf_end_us > usable_end:
            out_of_slot_count += 1

    sorted_j = sorted(jitters_us)
    p50 = _percentile(sorted_j, 0.50)
    p95 = _percentile(sorted_j, 0.95)
    p99 = _percentile(sorted_j, 0.99)
    max_j = sorted_j[-1]

    prop_rt_us = distance_km * SPEED_OF_LIGHT_US_PER_KM_ROUNDTRIP
    guard_floor_us = 2.0 * p99 + prop_rt_us + SIFS_PLUS_RXTX_TURNAROUND_US
    mean_slot_us = sum(o.scheduled_slot_duration_us for o in observations) / float(len(observations))
    guard_overhead_pct = (guard_floor_us / max(mean_slot_us, 1.0)) * 100.0
    leakage_pct = (out_of_slot_count / float(len(observations))) * 100.0

    return {
        "burst_count": len(observations),
        "distance_km": distance_km,
        "propagation_roundtrip_us": round(prop_rt_us, 2),
        "jitter_p50_us": round(p50, 2),
        "jitter_p95_us": round(p95, 2),
        "jitter_p99_us": round(p99, 2),
        "jitter_max_us": round(max_j, 2),
        "minimum_safe_guard_interval_us": round(guard_floor_us, 2),
        "mean_slot_duration_us": round(mean_slot_us, 2),
        "guard_overhead_pct": round(guard_overhead_pct, 2),
        "out_of_slot_violations": out_of_slot_count,
        "out_of_slot_violation_rate_pct": round(leakage_pct, 4),
        "sub_ms_slots_physically_credible": guard_floor_us < 350.0,
    }


def evaluate_pb051_target_slot_feasibility(
    sdr_observations: Sequence[SdrBurstObservation],
    paired_csma_vs_target_runs: Sequence[RunMetrics],
    distance_km: float = 6.0,
    holdout_replicated: bool = True,
    max_allowed_p99_jitter_us: float = 250.0,
    max_allowed_leakage_pct: float = 0.5,
) -> Dict[str, Any]:
    """Legacy array diagnostics only; a holdout boolean never grants promotion."""
    timing = compute_burst_edge_jitter_cdf(sdr_observations, distance_km=distance_km)
    if any(run.evidence_state != 'SYNTHETIC' for run in paired_csma_vs_target_runs):
        return {
            'gate_id': 'PB-051', 'overall_feasibility_verdict': 'RETEST_REQUIRED',
            'diagnostic_passed': False, 'physical_promotion_accepted': False,
            'evidence_state': 'IMPORTED_UNCLASSIFIED', 'timing_metrics': timing,
            'requires_unified_physical_retest': True,
            'reason': 'Array summaries and holdout_replicated do not prove a fresh physical campaign',
        }
    gk = RegressionGatekeeper(min_blocks_for_keep=4, min_blocks_for_promote=6)
    gate_decision = gk.evaluate_paired(list(paired_csma_vs_target_runs))

    passes_jitter = timing["jitter_p99_us"] <= max_allowed_p99_jitter_us
    passes_leakage = timing["out_of_slot_violation_rate_pct"] < max_allowed_leakage_pct
    passes_qoe = False  # This legacy array API is never a physical promotion route.
    diagnostic_pass = passes_jitter and passes_leakage and gate_decision.verdict == 'SYNTHETIC_PASS'

    overall_verdict = "PASSED_FEASIBILITY_GATE" if (passes_jitter and passes_leakage and passes_qoe) else "FAILED_FEASIBILITY_GATE"

    return {
        "gate_id": "PB-051",
        "overall_feasibility_verdict": 'SYNTHETIC_PASS' if diagnostic_pass else overall_verdict,
        "diagnostic_passed": diagnostic_pass,
        "physical_promotion_accepted": passes_jitter and passes_leakage and passes_qoe,
        "requires_unified_physical_retest": True,
        "evidence_state": gate_decision.evidence_state,
        "criteria_checks": {
            "p99_jitter_le_250us": passes_jitter,
            "out_of_slot_leakage_lt_0_5pct": passes_leakage,
            "paired_hidden_node_qoe_promoted": passes_qoe,
        },
        "timing_metrics": timing,
        "paired_qoe_decision": asdict(gate_decision),
    }


def _generate_synthetic_sdr_bursts(
    mode: str,
    count: int = 250,
) -> List[SdrBurstObservation]:
    """Generates deterministic SDR burst-edge fixtures matching host queue-gating vs target TSF timer."""
    obs: List[SdrBurstObservation] = []
    for i in range(count):
        peer = "cpe_near" if (i % 2 == 0) else "cpe_far"
        if mode == "HOST_QUEUE_GATING_15MS":
            slot_dur = 15000.0
            guard = 3800.0
            sched_start = i * slot_dur
            # Host hrtimer + WMI/TXQ wakeup jitter: p50 ~ 410 us, p95 ~ 1220 us, p99 ~ 1790 us
            bucket = i % 100
            if bucket == 99:
                jitter = 1820.0
            elif bucket >= 95:
                jitter = 1260.0 + (bucket - 95) * 80.0
            else:
                jitter = 180.0 + (bucket * 4.8)
            obs_start = sched_start + jitter
            obs_end = obs_start + 9200.0
        elif mode == "TARGET_TSF_TIMER_2MS":
            slot_dur = 2000.0
            guard = 260.0  # Matches airOS HT20 up_dur_gap / down_dur_gap scale
            sched_start = i * slot_dur
            # Target Xtensa TSF compare timer + PCU gate jitter: p50 ~ 18 us, p95 ~ 52 us, p99 ~ 84 us
            bucket = i % 100
            if bucket == 99:
                jitter = 86.0
            elif bucket >= 95:
                jitter = 54.0 + (bucket - 95) * 6.0
            else:
                jitter = 6.0 + (bucket * 0.26)
            obs_start = sched_start + jitter
            obs_end = obs_start + 1580.0
        else:
            raise ValueError(f"Unknown mode={mode!r}")

        obs.append(
            SdrBurstObservation(
                burst_id=i,
                peer_id=peer,
                scheduled_slot_start_us=sched_start,
                scheduled_slot_duration_us=slot_dur,
                assigned_guard_us=guard,
                observed_rf_start_us=obs_start,
                observed_rf_end_us=obs_end,
            )
        )
    return obs


def build_pb_050_051_fixture_report() -> Dict[str, Any]:
    """Builds the deterministic PB-050 and PB-051 benchmark fixture and feasibility verdict."""
    gates = load_ladder()
    pb050_ready = check_gate_readiness("PB-050", gates)
    pb051_ready = check_gate_readiness("PB-051", gates)

    host_obs = _generate_synthetic_sdr_bursts("HOST_QUEUE_GATING_15MS", count=250)
    target_obs = _generate_synthetic_sdr_bursts("TARGET_TSF_TIMER_2MS", count=250)

    host_timing = compute_burst_edge_jitter_cdf(host_obs, distance_km=6.0)
    target_timing = compute_burst_edge_jitter_cdf(target_obs, distance_km=6.0)

    # Paired 6-block A/B/A/B runs: Pure CSMA (Arm A) vs Target 2ms Slot Scheduler (Arm B) on 20 MHz hidden-node bench
    paired_runs: List[RunMetrics] = []
    csma_gp = [42.0, 41.2, 42.5, 41.8, 42.1, 41.6]
    target_gp = [68.4, 67.9, 68.8, 68.2, 68.5, 68.1]
    csma_p95 = [28.0, 29.2, 27.5, 28.6, 28.1, 28.8]
    target_p95 = [7.4, 7.6, 7.3, 7.5, 7.4, 7.5]
    csma_p99 = [64.0, 66.5, 62.8, 65.1, 64.4, 65.8]
    target_p99 = [11.8, 12.1, 11.6, 11.9, 11.8, 12.0]

    for idx in range(6):
        paired_runs.append(
            RunMetrics(
                evidence_state="SYNTHETIC",
                run_id=f"PB051_CSMA_A_{idx}",
                arm="A",
                goodput_mbps=csma_gp[idx],
                p95_lat_ms=csma_p95[idx],
                p99_lat_ms=csma_p99[idx],
                loss_pct=2.8,
                jain_fairness=0.72,
                channel_width_mhz=20,
                block_index=idx,
                worst_peer_goodput_mbps=12.5,
            )
        )
        paired_runs.append(
            RunMetrics(
                evidence_state="SYNTHETIC",
                run_id=f"PB051_TARGET_B_{idx}",
                arm="B",
                goodput_mbps=target_gp[idx],
                p95_lat_ms=target_p95[idx],
                p99_lat_ms=target_p99[idx],
                loss_pct=0.2,
                jain_fairness=0.97,
                channel_width_mhz=20,
                block_index=idx,
                worst_peer_goodput_mbps=33.2,
            )
        )

    pb051_eval = evaluate_pb051_target_slot_feasibility(
        sdr_observations=target_obs,
        paired_csma_vs_target_runs=paired_runs,
        distance_km=6.0,
        holdout_replicated=True,
    )

    return {
        "gates_covered": ["PB-050", "PB-051"],
        "automatic_execution_allowed": False,
        "evidence_state": "SYNTHETIC",
        "physical_acceptance": "UNKNOWN",
        "physical_retest_entrypoint": "run_physical_retest",
        "prerequisite_readiness": {
            "PB-050": pb050_ready,
            "PB-051": pb051_ready,
        },
        "pb050_host_vs_target_timing_comparison": {
            "host_queue_gating_15ms": host_timing,
            "target_tsf_timer_2ms": target_timing,
            "p99_jitter_reduction_factor": round(
                host_timing["jitter_p99_us"] / max(target_timing["jitter_p99_us"], 1e-6), 2
            ),
            "guard_floor_reduction_us": round(
                host_timing["minimum_safe_guard_interval_us"] - target_timing["minimum_safe_guard_interval_us"], 2
            ),
        },
        "pb051_target_scheduler_feasibility": pb051_eval,
    }


def main() -> None:
    report = build_pb_050_051_fixture_report()
    DEFAULT_FIXTURE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_FIXTURE_OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Saved PB-050/PB-051 timing fixture report to {DEFAULT_FIXTURE_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
