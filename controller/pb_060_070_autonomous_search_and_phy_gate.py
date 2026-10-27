#!/usr/bin/env python3
"""PB-060 & PB-070 Controller: Safe Autonomous MAC/PHY Holdout Search Pilot & Custom-PHY Gate Verifier.

Implements:
1. Gate PB-060: Closed-loop autonomous search pilot over allowlisted L1/L2 parameters with:
   - Canonical SHA-256 candidate fingerprinting and deduplication
   - Strict regulatory/envelope safety validation (no DFS/EIRP/ART violations)
   - Mandatory negative-control (A/A null) injection check
   - Holm-Sidak family-wise error rate control across M tested candidates
   - Mandatory two-stage promotion: Discovery Paired A/B/A/B -> Unseen Holdout Time-Block Replication
2. Gate PB-070: Formal 3-condition custom constellation / learned-PHY eligibility gate evaluator:
   - Condition 1: Writable constellation mapper/pilot/FEC table OR continuous raw TX/RX IQ injection (PB-023)
   - Condition 2: Verified modified QCA988x target execution (PB-040)
   - Condition 3: External calibrated VSA/SDR waveform & EVM verification
   - Emits `LOCKED_CONCENTRATE_ON_MAC_AND_POLICY` when any condition is unproven/negative.

Enforces `automatic_execution_allowed = False` during Phase 0.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from analysis.metrics.schema import validate_channel_width_mhz
from analysis.regression_gate.gatekeeper import GateDecision, RegressionGatekeeper, RunMetrics
from research.physical_boundary.ladder_schema import check_gate_readiness, load_ladder

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PILOT_OUTPUT_PATH = REPO_ROOT / "artifacts/qca988x/pb_060_070_pilot_and_verdict.json"

ALLOWED_CHANNEL_WIDTHS = (5, 10, 20, 40)
MIN_TX_POWER_DBM = 3
MAX_TX_POWER_DBM = 23
ALLOWED_RTS_THRESHOLDS = (256, 512, 2347)
MIN_AQL_BE_LIMIT_US = 2000
MAX_AQL_BE_LIMIT_US = 8000


@dataclass(frozen=True)
class SearchCandidateConfig:
    candidate_id: str
    channel_width_mhz: int
    tx_power_dbm: int
    ldpc_enabled: bool
    stbc_enabled: bool
    sgi_enabled: bool
    rts_threshold_bytes: int
    aql_be_limit_us: int
    is_negative_control: bool = False

    def canonical_payload(self) -> Dict[str, Any]:
        """Returns the canonical configuration dictionary excluding candidate_id for deduplication."""
        return {
            "channel_width_mhz": self.channel_width_mhz,
            "tx_power_dbm": self.tx_power_dbm,
            "ldpc_enabled": self.ldpc_enabled,
            "stbc_enabled": self.stbc_enabled,
            "sgi_enabled": self.sgi_enabled,
            "rts_threshold_bytes": self.rts_threshold_bytes,
            "aql_be_limit_us": self.aql_be_limit_us,
            "is_negative_control": self.is_negative_control,
        }

    def fingerprint(self) -> str:
        raw = json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:16]


def validate_candidate_safety_envelope(candidate: SearchCandidateConfig) -> Tuple[bool, str]:
    """Verifies that a candidate stays strictly within the allowlisted L1/L2 regulatory and hardware envelope."""
    try:
        validate_channel_width_mhz(candidate.channel_width_mhz)
    except ValueError as exc:
        return False, str(exc)

    if candidate.channel_width_mhz not in ALLOWED_CHANNEL_WIDTHS:
        return False, f"channel_width_mhz={candidate.channel_width_mhz} outside allowlist {ALLOWED_CHANNEL_WIDTHS}"
    if not (MIN_TX_POWER_DBM <= candidate.tx_power_dbm <= MAX_TX_POWER_DBM):
        return False, f"tx_power_dbm={candidate.tx_power_dbm} outside regulatory envelope [{MIN_TX_POWER_DBM}, {MAX_TX_POWER_DBM}]"
    if candidate.rts_threshold_bytes not in ALLOWED_RTS_THRESHOLDS:
        return False, f"rts_threshold_bytes={candidate.rts_threshold_bytes} outside allowlist {ALLOWED_RTS_THRESHOLDS}"
    if not (MIN_AQL_BE_LIMIT_US <= candidate.aql_be_limit_us <= MAX_AQL_BE_LIMIT_US):
        return False, f"aql_be_limit_us={candidate.aql_be_limit_us} outside allowlist [{MIN_AQL_BE_LIMIT_US}, {MAX_AQL_BE_LIMIT_US}]"
    return True, "SAFE_ALLOWLISTED_L1_L2_CANDIDATE"


def deduplicate_candidates(
    candidates: Sequence[SearchCandidateConfig],
) -> Tuple[List[SearchCandidateConfig], List[str]]:
    """Deduplicates candidates by canonical SHA-256 fingerprint, returning (unique_candidates, skipped_ids)."""
    seen_fps: set[str] = set()
    unique: List[SearchCandidateConfig] = []
    skipped: List[str] = []
    for cand in candidates:
        fp = cand.fingerprint()
        if fp in seen_fps:
            skipped.append(cand.candidate_id)
        else:
            seen_fps.add(fp)
            unique.append(cand)
    return unique, skipped


def evaluate_pb060_search_campaign(
    candidates: Sequence[SearchCandidateConfig],
    discovery_runs_by_candidate: Dict[str, Sequence[RunMetrics]],
    holdout_runs_by_candidate: Dict[str, Sequence[RunMetrics]],
) -> Dict[str, Any]:
    """Executes the two-stage PB-060 autonomous search evaluation with Holm-Sidak and holdout replication."""
    unique_candidates, skipped_duplicates = deduplicate_candidates(candidates)

    valid_candidates: List[SearchCandidateConfig] = []
    rejected_envelope: List[Dict[str, Any]] = []
    for cand in unique_candidates:
        ok, reason = validate_candidate_safety_envelope(cand)
        if not ok:
            rejected_envelope.append(
                {
                    "candidate_id": cand.candidate_id,
                    "fingerprint": cand.fingerprint(),
                    "status": "REJECTED_OUTSIDE_SAFETY_ENVELOPE",
                    "reason": reason,
                }
            )
        else:
            valid_candidates.append(cand)

    num_hypotheses = max(1, sum(1 for c in valid_candidates if not c.is_negative_control))
    gk = RegressionGatekeeper(
        min_blocks_for_keep=4,
        min_blocks_for_promote=6,
        num_hypotheses_tested=num_hypotheses,
    )

    candidate_results: List[Dict[str, Any]] = []
    negative_control_false_positives = 0
    promoted_candidates: List[str] = []

    for cand in valid_candidates:
        disc_runs = list(discovery_runs_by_candidate.get(cand.candidate_id, []))
        disc_decision: GateDecision = gk.evaluate_paired(
            disc_runs,
            holdout_replicated=False,
        )

        holdout_decision_dict: Optional[Dict[str, Any]] = None
        final_verdict = disc_decision.verdict

        if cand.is_negative_control and disc_decision.verdict in ("KEEP_FOR_REPLICATION", "PROMOTE"):
            negative_control_false_positives += 1

        # If discovery passes (`KEEP_FOR_REPLICATION`), evaluate on unseen holdout time-block
        if disc_decision.verdict in ("KEEP_FOR_REPLICATION", "PROMOTE"):
            hold_runs = list(holdout_runs_by_candidate.get(cand.candidate_id, []))
            if hold_runs:
                hold_decision = gk.evaluate_paired(
                    hold_runs,
                    holdout_replicated=True,
                )
                holdout_decision_dict = asdict(hold_decision)
                if hold_decision.verdict == "PROMOTE":
                    final_verdict = "PROMOTE"
                    if not cand.is_negative_control:
                        promoted_candidates.append(cand.candidate_id)
                else:
                    final_verdict = "REJECT_FAILED_HOLDOUT_REPLICATION"
            else:
                final_verdict = "KEEP_FOR_REPLICATION"

        candidate_results.append(
            {
                "candidate_id": cand.candidate_id,
                "fingerprint": cand.fingerprint(),
                "is_negative_control": cand.is_negative_control,
                "config": cand.canonical_payload(),
                "discovery_decision": asdict(disc_decision),
                "holdout_decision": holdout_decision_dict,
                "final_verdict": final_verdict,
            }
        )

    campaign_passed = (
        negative_control_false_positives == 0
        and len(promoted_candidates) >= 1
    )

    return {
        "gate_id": "PB-060",
        "num_hypotheses_tested": num_hypotheses,
        "skipped_duplicate_candidate_ids": skipped_duplicates,
        "rejected_safety_envelope_candidates": rejected_envelope,
        "negative_control_false_positives": negative_control_false_positives,
        "promoted_candidate_ids": promoted_candidates,
        "campaign_passed": campaign_passed,
        "candidate_evaluations": candidate_results,
    }


def evaluate_pb070_custom_phy_gate(
    condition_1_mapper_or_raw_iq_proven: bool,
    condition_2_modified_target_execution_proven: bool,
    condition_3_external_vsa_sdr_waveform_proven: bool,
    evidence_notes: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Evaluates Gate PB-070 3-condition eligibility for custom constellation / learned-PHY claims."""
    notes = evidence_notes or {}
    all_three_proven = (
        bool(condition_1_mapper_or_raw_iq_proven)
        and bool(condition_2_modified_target_execution_proven)
        and bool(condition_3_external_vsa_sdr_waveform_proven)
    )

    if all_three_proven:
        verdict = "ELIGIBLE_FOR_CUSTOM_PHY_EXPERIMENTS"
        policy_directive = (
            "All 3 physical prerequisites proven; bounded lab custom-PHY experiments may be scheduled."
        )
    else:
        verdict = "LOCKED_CONCENTRATE_ON_MAC_AND_POLICY"
        policy_directive = (
            "QCA988x constellation mapper and BCC/LDPC datapath remain hardware-locked unless all 3 "
            "prerequisites are physically proven. Concentrate 100% of engineering effort on MAC scheduling, "
            "sub-20 MHz width adaptation, LDPC/STBC/CCA response surfaces, and closed-loop QoE policy."
        )

    return {
        "gate_id": "PB-070",
        "verdict": verdict,
        "custom_phy_waveform_claims_allowed": all_three_proven,
        "conditions": {
            "condition_1_mapper_or_raw_iq_proven": bool(condition_1_mapper_or_raw_iq_proven),
            "condition_2_modified_target_execution_proven": bool(condition_2_modified_target_execution_proven),
            "condition_3_external_vsa_sdr_waveform_proven": bool(condition_3_external_vsa_sdr_waveform_proven),
        },
        "evidence_notes": {
            "condition_1": notes.get(
                "condition_1",
                "UNPROVEN: QCA988x 802.11ac constellation mapper/demapper and FEC are fixed in baseband silicon; "
                "BB capture mode (0x9070 / spectral ADC) is diagnostic snapshot only.",
            ),
            "condition_2": notes.get(
                "condition_2",
                "OFFLINE_PREP_ONLY: PB-011/PB-040 proved unsigned SGMT BCL-LZ77 container re-packing offline, "
                "but live target execution awaits physical bench gate PB-040.",
            ),
            "condition_3": notes.get(
                "condition_3",
                "UNPROVEN: External VSA/SDR custom constellation EVM verification has not been executed.",
            ),
        },
        "policy_directive": policy_directive,
    }


def _make_paired_runs(
    prefix: str,
    width_mhz: int,
    arm_a_gp: Sequence[float],
    arm_b_gp: Sequence[float],
    arm_a_p99: Sequence[float],
    arm_b_p99: Sequence[float],
    arm_a_fair: float = 0.88,
    arm_b_fair: float = 0.94,
) -> List[RunMetrics]:
    runs: List[RunMetrics] = []
    for idx in range(len(arm_a_gp)):
        runs.append(
            RunMetrics(
                run_id=f"{prefix}_A_{idx}",
                arm="A",
                goodput_mbps=arm_a_gp[idx],
                p95_lat_ms=arm_a_p99[idx] * 0.65,
                p99_lat_ms=arm_a_p99[idx],
                loss_pct=0.5,
                jain_fairness=arm_a_fair,
                channel_width_mhz=width_mhz,
                block_index=idx,
                worst_peer_goodput_mbps=arm_a_gp[idx] * 0.35,
            )
        )
        runs.append(
            RunMetrics(
                run_id=f"{prefix}_B_{idx}",
                arm="B",
                goodput_mbps=arm_b_gp[idx],
                p95_lat_ms=arm_b_p99[idx] * 0.65,
                p99_lat_ms=arm_b_p99[idx],
                loss_pct=0.2,
                jain_fairness=arm_b_fair,
                channel_width_mhz=width_mhz,
                block_index=idx,
                worst_peer_goodput_mbps=arm_b_gp[idx] * 0.42,
            )
        )
    return runs


def build_pb_060_070_pilot_report() -> Dict[str, Any]:
    """Builds the deterministic PB-060 autonomous search pilot and PB-070 custom-PHY verdict artifact."""
    gates = load_ladder()
    pb060_ready = check_gate_readiness("PB-060", gates)
    pb070_ready = check_gate_readiness("PB-070", gates)

    candidates = [
        # 1. Mandatory Negative Control (A/A null)
        SearchCandidateConfig(
            candidate_id="CAND_00_NEG_CTRL_AA",
            channel_width_mhz=20,
            tx_power_dbm=18,
            ldpc_enabled=True,
            stbc_enabled=False,
            sgi_enabled=True,
            rts_threshold_bytes=2347,
            aql_be_limit_us=4000,
            is_negative_control=True,
        ),
        # 2. Candidate 1: 10 MHz + LDPC + STBC + 3000us AQL + RTS=256 (Strong winner in discovery & holdout)
        SearchCandidateConfig(
            candidate_id="CAND_01_10MHZ_LDPC_STBC_AQL3000",
            channel_width_mhz=10,
            tx_power_dbm=18,
            ldpc_enabled=True,
            stbc_enabled=True,
            sgi_enabled=False,
            rts_threshold_bytes=256,
            aql_be_limit_us=3000,
        ),
        # 3. Duplicate of Candidate 1 with different ID (tests fingerprint deduplication)
        SearchCandidateConfig(
            candidate_id="CAND_02_DUPLICATE_OF_CAND_01",
            channel_width_mhz=10,
            tx_power_dbm=18,
            ldpc_enabled=True,
            stbc_enabled=True,
            sgi_enabled=False,
            rts_threshold_bytes=256,
            aql_be_limit_us=3000,
        ),
        # 4. Candidate 3: Overfitted discovery candidate that fails unseen holdout replication
        SearchCandidateConfig(
            candidate_id="CAND_03_20MHZ_SGI_NO_HOLDOUT",
            channel_width_mhz=20,
            tx_power_dbm=20,
            ldpc_enabled=True,
            stbc_enabled=False,
            sgi_enabled=True,
            rts_threshold_bytes=512,
            aql_be_limit_us=2500,
        ),
        # 5. Candidate 4: Out-of-envelope candidate (illegal 30 dBm EIRP)
        SearchCandidateConfig(
            candidate_id="CAND_04_ILLEGAL_TX_POWER_30DBM",
            channel_width_mhz=20,
            tx_power_dbm=30,
            ldpc_enabled=True,
            stbc_enabled=False,
            sgi_enabled=True,
            rts_threshold_bytes=256,
            aql_be_limit_us=3000,
        ),
    ]

    base_gp = [24.0, 23.8, 24.2, 23.9, 24.1, 23.7, 24.0, 23.9]
    base_p99 = [22.0, 22.5, 21.8, 22.2, 22.1, 22.4, 22.0, 22.3]

    discovery_runs = {
        "CAND_00_NEG_CTRL_AA": _make_paired_runs(
            "DISC_C00", 20, base_gp, base_gp, base_p99, base_p99, 0.90, 0.90
        ),
        "CAND_01_10MHZ_LDPC_STBC_AQL3000": _make_paired_runs(
            "DISC_C01",
            10,
            [12.0, 11.9, 12.1, 12.0, 12.1, 11.8, 12.0, 11.9],
            [17.4, 17.2, 17.5, 17.3, 17.6, 17.1, 17.4, 17.3],
            [24.0, 24.5, 23.8, 24.2, 24.1, 24.4, 24.0, 24.3],
            [13.2, 13.5, 13.0, 13.4, 13.1, 13.3, 13.2, 13.4],
        ),
        "CAND_03_20MHZ_SGI_NO_HOLDOUT": _make_paired_runs(
            "DISC_C03",
            20,
            base_gp,
            [27.8, 27.5, 28.0, 27.6, 27.9, 27.4, 27.8, 27.7],
            base_p99,
            [18.5, 18.8, 18.2, 18.6, 18.4, 18.7, 18.5, 18.6],
        ),
    }

    holdout_runs = {
        "CAND_01_10MHZ_LDPC_STBC_AQL3000": _make_paired_runs(
            "HOLD_C01",
            10,
            [11.8, 12.0, 11.9, 12.1, 12.0, 11.9, 11.8, 12.0],
            [17.1, 17.3, 17.2, 17.5, 17.4, 17.2, 17.1, 17.3],
            [24.2, 24.0, 24.4, 23.9, 24.1, 24.3, 24.2, 24.0],
            [13.4, 13.2, 13.5, 13.1, 13.3, 13.2, 13.4, 13.1],
        ),
        # CAND_03 regresses p99 latency on unseen holdout block -> rejected!
        "CAND_03_20MHZ_SGI_NO_HOLDOUT": _make_paired_runs(
            "HOLD_C03",
            20,
            base_gp,
            [24.2, 24.0, 24.3, 24.1, 24.2, 23.9, 24.1, 24.0],
            base_p99,
            [31.0, 32.5, 30.8, 31.9, 31.4, 32.1, 31.5, 32.0],
        ),
    }

    pb060_pilot = evaluate_pb060_search_campaign(
        candidates=candidates,
        discovery_runs_by_candidate=discovery_runs,
        holdout_runs_by_candidate=holdout_runs,
    )

    pb070_verdict = evaluate_pb070_custom_phy_gate(
        condition_1_mapper_or_raw_iq_proven=False,
        condition_2_modified_target_execution_proven=False,
        condition_3_external_vsa_sdr_waveform_proven=False,
    )

    return {
        "gates_covered": ["PB-060", "PB-070"],
        "automatic_execution_allowed": False,
        "prerequisite_readiness": {
            "PB-060": pb060_ready,
            "PB-070": pb070_ready,
        },
        "pb060_autonomous_search_pilot": pb060_pilot,
        "pb070_custom_phy_eligibility_verdict": pb070_verdict,
    }


def main() -> None:
    report = build_pb_060_070_pilot_report()
    DEFAULT_PILOT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_PILOT_OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Saved PB-060/PB-070 pilot & verdict report to {DEFAULT_PILOT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
