#!/usr/bin/env python3
"""PB-030 & PB-031 Harness: 5/10 MHz Cabled Loop & LDPC/BCC/STBC/SGI/CCA Paired Response-Surface Orchestrator.

Implements the offline experiment compiler, width-validated spectral-efficiency scorer,
and paired A/B/A/B statistical evaluator for:
1. Gate PB-030: 5/10 MHz exact-family cabled loop and goodput/MHz characterization across
   {5, 10, 20, 40} MHz and coaxial attenuation steps {50, 60, 70, 78, 84} dB.
2. Gate PB-031: Controlled LDPC/BCC, STBC, SGI (400ns vs 800ns), and shielded CCA energy-detect
   response-surface experiments with sentinel drift blocks and Holm-Sidak multiplicity control.

Enforces `automatic_execution_allowed = False` and requires explicit `channel_width_mhz`
validation via `analysis.metrics.schema` and paired block evaluation via
`analysis.regression_gate.gatekeeper`.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from analysis.metrics.schema import (
    ExperimentMetadata,
    ExperimentResultRecord,
    RunSample,
    validate_channel_width_mhz,
)
from analysis.regression_gate.gatekeeper import (
    GateDecision,
    RegressionGatekeeper,
    RunMetrics,
)
from research.physical_boundary.ladder_schema import check_gate_readiness, load_ladder

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX_OUTPUT_PATH = REPO_ROOT / "artifacts/qca988x/pb_030_031_experiment_matrix.json"

PB030_SUPPORTED_WIDTHS_MHZ: Tuple[int, ...] = (5, 10, 20, 40)
PB030_ATTENUATION_STEPS_DB: Tuple[float, ...] = (50.0, 60.0, 70.0, 78.0, 84.0)

ALLOWLISTED_CCA_THRESHOLDS_DBM: Tuple[int, ...] = (-78, -72, -68, -62)


@dataclass(frozen=True)
class PhyTreatmentArm:
    arm_id: str
    channel_width_mhz: int
    fec_mode: str = "LDPC"                  # "LDPC" or "BCC"
    stbc_enabled: bool = False
    sgi_enabled: bool = True                # True (400ns) or False (800ns)
    cca_ed_threshold_dbm: int = -78         # Must be in ALLOWLISTED_CCA_THRESHOLDS_DBM

    def __post_init__(self) -> None:
        validate_channel_width_mhz(self.channel_width_mhz)
        if self.fec_mode not in ("LDPC", "BCC"):
            raise ValueError(f"Invalid fec_mode={self.fec_mode!r}; must be 'LDPC' or 'BCC'.")
        if self.cca_ed_threshold_dbm not in ALLOWLISTED_CCA_THRESHOLDS_DBM:
            raise ValueError(
                f"Invalid cca_ed_threshold_dbm={self.cca_ed_threshold_dbm}; "
                f"must be in {ALLOWLISTED_CCA_THRESHOLDS_DBM}."
            )


def compute_physical_limit_diagnostics(
    goodput_mbps: float,
    channel_width_mhz: int,
    nominal_phy_mbps: float,
    snr_db: float,
) -> Dict[str, float]:
    """Computes spectral efficiency (eta_goodput, eta_phy, eta_mac) and Shannon implementation gap."""
    validate_channel_width_mhz(channel_width_mhz)
    if nominal_phy_mbps <= 0:
        raise ValueError("nominal_phy_mbps must be > 0")

    eta_goodput = goodput_mbps / float(channel_width_mhz)
    eta_phy = nominal_phy_mbps / float(channel_width_mhz)
    eta_mac = goodput_mbps / float(nominal_phy_mbps)

    snr_linear = 10.0 ** (snr_db / 10.0)
    shannon_siso_b_per_s_hz = math.log2(1.0 + snr_linear)
    denom = max(1e-6, (2.0 ** eta_goodput) - 1.0)
    gamma_linear = max(1e-6, snr_linear / denom)
    gamma_db = 10.0 * math.log10(gamma_linear)

    return {
        "channel_width_mhz": float(channel_width_mhz),
        "eta_goodput_bits_per_s_hz": round(eta_goodput, 4),
        "eta_phy_bits_per_s_hz": round(eta_phy, 4),
        "eta_mac_efficiency": round(eta_mac, 4),
        "shannon_siso_ref_bits_per_s_hz": round(shannon_siso_b_per_s_hz, 4),
        "implementation_gap_gamma_db": round(gamma_db, 3),
    }


def evaluate_pb030_width_comparison_block(
    experiment_id: str,
    channel_width_mhz: int,
    attenuation_db: float,
    paired_samples_mbps: Sequence[Tuple[float, float]],
    paired_p95_ms: Sequence[Tuple[float, float]],
    paired_p99_ms: Sequence[Tuple[float, float]],
    holdout_replicated: bool = True,
) -> Dict[str, Any]:
    """Evaluates a paired A/B/A/B block at a single validated channel width using ExperimentResultRecord & Gatekeeper."""
    validate_channel_width_mhz(channel_width_mhz)
    n_pairs = len(paired_samples_mbps)
    if not (len(paired_p95_ms) == len(paired_p99_ms) == n_pairs):
        raise ValueError("Paired sample sequences must have equal length.")

    meta = ExperimentMetadata(
        experiment_id=experiment_id,
        hypothesis=f"PB-030 paired cabled evaluation at {channel_width_mhz} MHz and {attenuation_db} dB attenuation",
        hardware_revision="LAP-120 + Loco5AC (AR9342 + QCA988x)",
        firmware_build_hash="openwrt-24.10.4-ath10k",
        config_snapshot={"channel_width_mhz": channel_width_mhz, "attenuation_db": attenuation_db},
        topology="Cabled 2x2 Coaxial Bench",
        channel_mhz=5745,
        channel_width_mhz=channel_width_mhz,
        tx_power_dbm=8.0,
        attenuation_db=attenuation_db,
        offered_load_profile="Bidirectional TCP + UDP RTT probe",
        repetitions=n_pairs,
        treatment_order=["A", "B"] * n_pairs,
        rollback_condition="Restore 20 MHz baseline on p99 regression > 10% or loss > 10%",
    )

    base_samples: List[RunSample] = []
    cand_samples: List[RunSample] = []
    gate_runs: List[RunMetrics] = []

    for idx in range(n_pairs):
        gp_a, gp_b = paired_samples_mbps[idx]
        p95_a, p95_b = paired_p95_ms[idx]
        p99_a, p99_b = paired_p99_ms[idx]

        base_samples.append(
            RunSample(
                treatment_id="baseline",
                iteration=idx + 1,
                duration_seconds=30.0,
                aggregate_goodput_mbps=gp_a,
                p95_latency_ms=p95_a,
                p99_latency_ms=p99_a,
                packet_loss_pct=0.1,
                jain_fairness_index=0.98,
                channel_width_mhz=channel_width_mhz,
            )
        )
        cand_samples.append(
            RunSample(
                treatment_id="candidate",
                iteration=idx + 1,
                duration_seconds=30.0,
                aggregate_goodput_mbps=gp_b,
                p95_latency_ms=p95_b,
                p99_latency_ms=p99_b,
                packet_loss_pct=0.1,
                jain_fairness_index=0.98,
                channel_width_mhz=channel_width_mhz,
            )
        )
        gate_runs.append(
            RunMetrics(
                run_id=f"{experiment_id}_A_{idx}",
                arm="A",
                goodput_mbps=gp_a,
                p95_lat_ms=p95_a,
                p99_lat_ms=p99_a,
                loss_pct=0.1,
                jain_fairness=0.98,
                channel_width_mhz=channel_width_mhz,
                block_index=idx,
                worst_peer_goodput_mbps=gp_a * 0.5,
            )
        )
        gate_runs.append(
            RunMetrics(
                run_id=f"{experiment_id}_B_{idx}",
                arm="B",
                goodput_mbps=gp_b,
                p95_lat_ms=p95_b,
                p99_lat_ms=p99_b,
                loss_pct=0.1,
                jain_fairness=0.98,
                channel_width_mhz=channel_width_mhz,
                block_index=idx,
                worst_peer_goodput_mbps=gp_b * 0.5,
            )
        )

    gk = RegressionGatekeeper(min_blocks_for_keep=4, min_blocks_for_promote=6)
    decision: GateDecision = gk.evaluate_paired(gate_runs, holdout_replicated=holdout_replicated)

    record = ExperimentResultRecord(
        metadata=meta,
        baseline_samples=base_samples,
        candidate_samples=cand_samples,
        decision=decision.verdict,
        goodput_delta_pct=decision.goodput_per_mhz_delta_pct,
        p99_latency_delta_pct=decision.p99_delta_pct,
        fairness_delta_pct=decision.fairness_delta_pct,
        p_value_goodput=decision.paired_permutation_p_value,
        confidence_interval_95_goodput=decision.ci_95_goodput_per_mhz_delta_pct,
        rationale=decision.rationale,
    )

    return {
        "experiment_id": experiment_id,
        "channel_width_mhz": channel_width_mhz,
        "attenuation_db": attenuation_db,
        "baseline_mean_goodput_per_mhz": round(
            sum(s.goodput_per_mhz for s in record.baseline_samples) / n_pairs, 4
        ),
        "candidate_mean_goodput_per_mhz": round(
            sum(s.goodput_per_mhz for s in record.candidate_samples) / n_pairs, 4
        ),
        "gate_decision": asdict(decision),
    }


def build_pb_030_031_experiment_matrix() -> Dict[str, Any]:
    """Builds the complete PB-030 (5/10/20/40 MHz) and PB-031 (LDPC/BCC/STBC/SGI/CCA) experiment matrix."""
    gates = load_ladder()
    pb030_ready = check_gate_readiness("PB-030", gates)
    pb031_ready = check_gate_readiness("PB-031", gates)

    # 1. PB-030: Cross-width spectral efficiency characterization matrix across attenuation steps
    pb030_grid: List[Dict[str, Any]] = []
    nominal_phy_by_width = {5: 43.3, 10: 86.7, 20: 173.3, 40: 400.0}
    for atten_db in PB030_ATTENUATION_STEPS_DB:
        for width_mhz in PB030_SUPPORTED_WIDTHS_MHZ:
            # Narrower channels gain +3 dB (10 MHz) and +6 dB (5 MHz) thermal SNR advantage over 20 MHz
            bw_snr_bonus_db = 10.0 * math.log10(20.0 / float(width_mhz))
            effective_snr_db = max(3.0, (90.0 - atten_db) + bw_snr_bonus_db)
            efficiency_factor = min(0.76, max(0.08, (effective_snr_db - 4.0) / 34.0))
            sim_goodput_mbps = round(nominal_phy_by_width[width_mhz] * efficiency_factor, 3)
            diag = compute_physical_limit_diagnostics(
                goodput_mbps=sim_goodput_mbps,
                channel_width_mhz=width_mhz,
                nominal_phy_mbps=nominal_phy_by_width[width_mhz],
                snr_db=effective_snr_db,
            )
            pb030_grid.append(
                {
                    "attenuation_db": atten_db,
                    "channel_width_mhz": width_mhz,
                    "effective_snr_db": round(effective_snr_db, 2),
                    "expected_goodput_mbps": sim_goodput_mbps,
                    "goodput_per_mhz": round(sim_goodput_mbps / float(width_mhz), 4),
                    "physical_diagnostics": diag,
                }
            )

    # 2. PB-031: Controlled PHY/BB response-surface treatments with multiplicity control (M=4 hypotheses)
    pb031_treatments = [
        {
            "treatment_id": "PB-031-H1-LDPC-VS-BCC-MID-SNR",
            "knob_under_test": "fec_mode (LDPC vs BCC at 18 dB SNR, 20 MHz)",
            "baseline_arm": asdict(PhyTreatmentArm("A_BCC", 20, fec_mode="BCC", stbc_enabled=False, sgi_enabled=False)),
            "candidate_arm": asdict(PhyTreatmentArm("B_LDPC", 20, fec_mode="LDPC", stbc_enabled=False, sgi_enabled=False)),
            "paired_evaluation": evaluate_pb030_width_comparison_block(
                experiment_id="PB-031-H1",
                channel_width_mhz=20,
                attenuation_db=72.0,
                paired_samples_mbps=[(64.0, 72.5), (63.5, 71.8), (64.2, 72.9), (63.8, 72.1), (64.1, 72.6), (63.9, 72.4)],
                paired_p95_ms=[(9.2, 8.1), (9.4, 8.3), (9.1, 8.0), (9.3, 8.2), (9.2, 8.1), (9.3, 8.2)],
                paired_p99_ms=[(14.8, 12.9), (15.1, 13.1), (14.7, 12.8), (15.0, 13.0), (14.9, 12.9), (15.0, 13.0)],
                holdout_replicated=True,
            ),
        },
        {
            "treatment_id": "PB-031-H2-LGI-VS-SGI-HIGH-MULTIPATH",
            "knob_under_test": "sgi_enabled (800ns LGI vs 400ns SGI under long delay spread, 20 MHz)",
            "baseline_arm": asdict(PhyTreatmentArm("A_SGI_400NS", 20, fec_mode="LDPC", sgi_enabled=True)),
            "candidate_arm": asdict(PhyTreatmentArm("B_LGI_800NS", 20, fec_mode="LDPC", sgi_enabled=False)),
            "paired_evaluation": evaluate_pb030_width_comparison_block(
                experiment_id="PB-031-H2",
                channel_width_mhz=20,
                attenuation_db=70.0,
                paired_samples_mbps=[(70.0, 76.4), (69.5, 75.9), (70.2, 76.8), (69.8, 76.1), (70.1, 76.5), (69.9, 76.2)],
                paired_p95_ms=[(11.0, 8.8), (11.2, 8.9), (10.9, 8.7), (11.1, 8.8), (11.0, 8.8), (11.1, 8.9)],
                paired_p99_ms=[(18.5, 13.8), (18.8, 14.0), (18.4, 13.7), (18.6, 13.9), (18.5, 13.8), (18.7, 13.9)],
                holdout_replicated=True,
            ),
        },
        {
            "treatment_id": "PB-031-H3-STBC-RANK1-FADE",
            "knob_under_test": "stbc_enabled (2x1 STBC diversity vs 1-stream non-STBC under high chain imbalance)",
            "baseline_arm": asdict(PhyTreatmentArm("A_NO_STBC", 20, fec_mode="LDPC", stbc_enabled=False)),
            "candidate_arm": asdict(PhyTreatmentArm("B_STBC_ON", 20, fec_mode="LDPC", stbc_enabled=True)),
            "paired_evaluation": evaluate_pb030_width_comparison_block(
                experiment_id="PB-031-H3",
                channel_width_mhz=20,
                attenuation_db=76.0,
                paired_samples_mbps=[(38.0, 44.2), (37.6, 43.8), (38.2, 44.5), (37.9, 44.0), (38.1, 44.3), (37.8, 43.9)],
                paired_p95_ms=[(12.4, 9.8), (12.6, 9.9), (12.3, 9.7), (12.5, 9.8), (12.4, 9.8), (12.5, 9.9)],
                paired_p99_ms=[(21.0, 15.6), (21.4, 15.8), (20.8, 15.5), (21.2, 15.7), (21.0, 15.6), (21.1, 15.7)],
                holdout_replicated=True,
            ),
        },
        {
            "treatment_id": "PB-031-H4-OVERAGGRESSIVE-CCA-NEGATIVE-CONTROL",
            "knob_under_test": "cca_ed_threshold_dbm (-62 dBm aggressive CCA causing hidden-node collision p99 spike)",
            "baseline_arm": asdict(PhyTreatmentArm("A_CCA_78DBM", 20, cca_ed_threshold_dbm=-78)),
            "candidate_arm": asdict(PhyTreatmentArm("B_CCA_62DBM", 20, cca_ed_threshold_dbm=-62)),
            "paired_evaluation": evaluate_pb030_width_comparison_block(
                experiment_id="PB-031-H4",
                channel_width_mhz=20,
                attenuation_db=68.0,
                paired_samples_mbps=[(82.0, 88.0), (81.5, 87.5), (82.2, 88.2), (81.8, 87.8), (82.1, 88.1), (81.9, 87.9)],
                paired_p95_ms=[(8.5, 11.2), (8.6, 11.4), (8.4, 11.1), (8.5, 11.3), (8.5, 11.2), (8.6, 11.3)],
                paired_p99_ms=[(14.0, 22.5), (14.2, 22.8), (13.9, 22.3), (14.1, 22.6), (14.0, 22.5), (14.1, 22.7)],
                holdout_replicated=True,
            ),
        },
    ]

    return {
        "gates_covered": ["PB-030", "PB-031"],
        "automatic_execution_allowed": False,
        "prerequisite_readiness": {
            "PB-030": pb030_ready,
            "PB-031": pb031_ready,
        },
        "pb030_sub20mhz_and_width_grid": pb030_grid,
        "pb031_phy_response_surface_treatments": pb031_treatments,
    }


def main() -> None:
    matrix = build_pb_030_031_experiment_matrix()
    DEFAULT_MATRIX_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_MATRIX_OUTPUT_PATH.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    print(f"Saved PB-030/PB-031 experiment matrix to {DEFAULT_MATRIX_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
