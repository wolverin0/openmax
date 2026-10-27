#!/usr/bin/env python3
"""PB-060 & PB-070 Controller: Safe Autonomous MAC/PHY Holdout Search Pilot & Custom-PHY Gate Verifier.

Implements:
1. Gate PB-060: Closed-loop autonomous search pilot over allowlisted L1/L2 parameters with:
   - Canonical SHA-256 candidate fingerprinting and deduplication
   - Strict regulatory/envelope safety validation (no DFS/EIRP/ART violations)
   - Mandatory negative-control (A/A null) injection check
   - Canonical gatekeeper family-wise error control across M frozen candidates
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
import math
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
        """Canonical physical knobs; candidate ID and control role are separate metadata."""
        return {
            "channel_width_mhz": self.channel_width_mhz,
            "tx_power_dbm": self.tx_power_dbm,
            "ldpc_enabled": self.ldpc_enabled,
            "stbc_enabled": self.stbc_enabled,
            "sgi_enabled": self.sgi_enabled,
            "rts_threshold_bytes": self.rts_threshold_bytes,
            "aql_be_limit_us": self.aql_be_limit_us,
        }

    def fingerprint(self) -> str:
        raw = json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


def validate_candidate_safety_envelope(candidate: SearchCandidateConfig) -> Tuple[bool, str]:
    """Verifies that a candidate stays strictly within the allowlisted L1/L2 regulatory and hardware envelope."""
    if (any(type(getattr(candidate, key)) is not int for key in
            ("channel_width_mhz", "tx_power_dbm", "rts_threshold_bytes", "aql_be_limit_us"))
            or any(type(getattr(candidate, key)) is not bool for key in
                   ("ldpc_enabled", "stbc_enabled", "sgi_enabled", "is_negative_control"))):
        return False, "Invalid candidate field type"
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
    """Deduplicate identical knobs within a role; repeated IDs are invalid."""
    seen_fps: set[tuple[str, bool]] = set()
    seen_ids = set()
    unique: List[SearchCandidateConfig] = []
    skipped: List[str] = []
    for cand in candidates:
        if not isinstance(cand.candidate_id, str) or not cand.candidate_id or cand.candidate_id in seen_ids:
            raise ValueError("Duplicate or invalid candidate_id")
        seen_ids.add(cand.candidate_id)
        fp = (cand.fingerprint(), cand.is_negative_control)
        if fp in seen_fps:
            skipped.append(cand.candidate_id)
        else:
            seen_fps.add(fp)
            unique.append(cand)
    return unique, skipped


def _cohort_errors(runs: Sequence[RunMetrics], minimum_pairs: int = 4,
                   max_loss_pct: float = 10.0) -> List[str]:
    errors = []
    if not runs:
        return ['missing measured cohort']
    groups = {}
    ids = set()
    previous_end = None
    for position, run in enumerate(runs):
        try:
            run.__post_init__()
        except (ValueError, TypeError, AttributeError) as exc:
            errors.append('invalid normalized observation: ' + str(exc))
            continue
        if run.is_sentinel:
            errors.append('sentinel is not a complete paired observation')
        if not isinstance(run.run_id, str) or not run.run_id or run.run_id in ids:
            errors.append('duplicate/invalid run ID')
        ids.add(run.run_id)
        if type(run.block_index) is not int or run.block_index < 0 or run.arm not in ('A', 'B'):
            errors.append('invalid arm/block identity'); continue
        group = groups.setdefault(run.block_index, {})
        if run.arm in group:
            errors.append('duplicate arm in block')
        group[run.arm] = run
        if (position % 2 == 0 and run.arm != 'A') or (position % 2 == 1 and run.arm != 'B'):
            errors.append('reordered A/B events')
        values = (run.goodput_mbps, run.p95_lat_ms, run.p99_lat_ms, run.loss_pct, run.jain_fairness)
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
            errors.append('nonfinite or invalid metric')
            continue
        elif (min(run.goodput_mbps, run.p95_lat_ms, run.p99_lat_ms) < 0
              or run.p95_lat_ms > run.p99_lat_ms or not 0 <= run.loss_pct <= 100
              or not 0 <= run.jain_fairness <= 1):
            errors.append('metric range/percentile violation')
        if run.firmware_resets or run.loss_pct > max_loss_pct:
            errors.append('reset or excessive packet loss')
        begin, finish = getattr(run, 'window_start_s', None), getattr(run, 'window_end_s', None)
        if begin is not None or finish is not None:
            if (type(begin) not in (int, float) or type(finish) not in (int, float)
                    or not math.isfinite(begin) or not math.isfinite(finish) or begin >= finish):
                errors.append('invalid/nonfinite window bounds'); continue
            if previous_end is not None and begin < previous_end:
                errors.append('overlapping/reordered windows')
            previous_end = finish
    if len(groups) < minimum_pairs or any(set(group) != {'A', 'B'} for group in groups.values()):
        errors.append('insufficient complete A/B pairs')
    if any(set(group) == {'A', 'B'} and group['A'].channel_width_mhz != group['B'].channel_width_mhz
           for group in groups.values()):
        errors.append('paired channel-width contract mismatch')
    indices = [r.block_index for r in runs if type(r.block_index) is int]
    if indices != sorted(indices):
        errors.append('reordered block IDs')
    return errors


def _holdout_separation(discovery, holdout):
    errors = []
    for field in ('run_id', 'raw_sha256', 'session_id'):
        left = {getattr(r, field, None) for r in discovery} - {None, ''}
        right = {getattr(r, field, None) for r in holdout} - {None, ''}
        if left & right:
            errors.append('holdout overlaps discovery ' + field)
    if (discovery and holdout and all(getattr(r, 'window_end_s', None) is not None for r in discovery)
            and all(getattr(r, 'window_start_s', None) is not None for r in holdout)):
        if min(r.window_start_s for r in holdout) < max(r.window_end_s for r in discovery):
            errors.append('holdout overlaps discovery time window')
    return errors


def evaluate_pb060_search_campaign(
    candidates: Sequence[SearchCandidateConfig],
    discovery_runs_by_candidate: Dict[str, Sequence[RunMetrics]],
    holdout_runs_by_candidate: Dict[str, Sequence[RunMetrics]],
    *, evidence_root: Path | None = None,
    replication_receipts_by_candidate: Dict[str, str] | None = None,
    objective: str = 'LATENCY_WITH_CAPACITY_NONINFERIORITY',
) -> Dict[str, Any]:
    """Fail-closed campaign evaluation; typed synthetic diagnostics never promote."""
    from analysis.regression_gate import gatekeeper as canonical
    errors = []
    try:
        unique_candidates, skipped_duplicates = deduplicate_candidates(candidates)
    except ValueError as exc:
        unique_candidates, skipped_duplicates = [], []
        errors.append(str(exc))
    known_ids = {candidate.candidate_id for candidate in candidates}
    for datasets in (discovery_runs_by_candidate, holdout_runs_by_candidate):
        if set(datasets) - known_ids:
            errors.append('extraneous dataset candidate IDs')
        if any(datasets.get(label) for label in skipped_duplicates):
            errors.append('extraneous dataset for deduplicated candidate')
    valid_candidates, rejected_envelope = [], []
    for cand in unique_candidates:
        ok, reason = validate_candidate_safety_envelope(cand)
        if ok:
            valid_candidates.append(cand)
        else:
            rejected_envelope.append(dict(candidate_id=cand.candidate_id, fingerprint=cand.fingerprint(),
                status='REJECTED_OUTSIDE_SAFETY_ENVELOPE', reason=reason))
    controls = [cand for cand in valid_candidates if cand.is_negative_control]
    if not controls:
        errors.append('missing explicit measured negative control')
    all_runs = [run for cohort in (discovery_runs_by_candidate, holdout_runs_by_candidate)
                for runs in cohort.values() for run in runs]
    ids = [run.run_id for run in all_runs]
    if len(ids) != len(set(ids)):
        errors.append('duplicate run IDs across discovery/holdout/control cohorts')
    raw_hashes = [getattr(run, 'raw_sha256', None) for run in all_runs]
    raw_hashes = [digest for digest in raw_hashes if digest]
    if len(raw_hashes) != len(set(raw_hashes)):
        errors.append('duplicate raw evidence across cohorts')
    synthetic = bool(all_runs) and all(getattr(run, 'evidence_state', None) == 'SYNTHETIC' for run in all_runs)
    if not synthetic and any(getattr(run, 'evidence_state', None) == 'SYNTHETIC' for run in all_runs):
        errors.append('mixed synthetic and physical/unknown evidence')
    num_hypotheses = max(1, sum(not cand.is_negative_control for cand in valid_candidates))
    root = Path(evidence_root) if evidence_root is not None else REPO_ROOT
    gk = RegressionGatekeeper(min_blocks_for_keep=4, min_blocks_for_promote=6,
                              num_hypotheses_tested=num_hypotheses, evidence_root=root, objective=objective)
    family_fingerprints = sorted({cand.fingerprint() for cand in valid_candidates if not cand.is_negative_control})
    adjusted_alpha = canonical.compute_adjusted_alpha(gk.alpha, num_hypotheses)
    control_pairs_required = max(gk.min_blocks_for_keep, math.ceil(math.log2(2 / adjusted_alpha)))
    candidate_results, promoted, diagnostic_success = [], [], []
    false_positives = 0
    valid_controls = 0
    receipts = replication_receipts_by_candidate or {}
    if set(receipts) - known_ids:
        errors.append('extraneous replication receipt candidate ID')
    for cand in valid_candidates:
        disc = list(discovery_runs_by_candidate.get(cand.candidate_id, []))
        hold = list(holdout_runs_by_candidate.get(cand.candidate_id, []))
        local_errors = _cohort_errors(disc,
            minimum_pairs=control_pairs_required if cand.is_negative_control else gk.min_blocks_for_keep,
            max_loss_pct=gk.max_loss_pct)
        for run in disc + hold:
            if run.arm == 'B' or cand.is_negative_control:
                if getattr(run, 'applied_config_sha256', None) != cand.fingerprint():
                    local_errors.append('candidate config fingerprint differs from applied readback binding')
            elif not synthetic and getattr(run, 'applied_config_sha256', None) == cand.fingerprint():
                local_errors.append('non-control A/A readbacks are identical; no treatment contrast')
            if (run.arm == 'B' or cand.is_negative_control) and run.channel_width_mhz != cand.channel_width_mhz:
                local_errors.append('candidate channel width differs from observation')
        if not synthetic:
            local_errors.extend(canonical.validate_run_provenance(disc, evidence_root=root))
        if hold:
            local_errors.extend(_cohort_errors(hold, max_loss_pct=gk.max_loss_pct))
            local_errors.extend(_holdout_separation(disc, hold))
        disc_decision = hold_decision = None
        final = 'REJECT_INVALID_CAMPAIGN_EVIDENCE'
        if not local_errors:
            disc_decision = gk.evaluate_paired(disc, candidate_fingerprint=cand.fingerprint())
            successful = disc_decision.verdict in ('KEEP_FOR_REPLICATION', 'PROMOTE', 'SYNTHETIC_PASS')
            if cand.is_negative_control:
                if successful:
                    false_positives += 1
                    local_errors.append('negative control improved; campaign invalid')
                    final = 'REJECT_NEGATIVE_CONTROL_IMPROVEMENT'
                else:
                    valid_controls += 1
                    final = 'VALID_SYNTHETIC_NULL' if synthetic else 'VALID_MEASURED_NULL'
            elif successful:
                if hold:
                    if not synthetic:
                        local_errors.extend(canonical.validate_holdout_evidence(disc, hold,
                            candidate_fingerprint=cand.fingerprint(), evidence_root=root,
                            replication_receipt_path=receipts.get(cand.candidate_id)))
                        if not local_errors:
                            proof, _ = canonical._read_evidence(root, receipts[cand.candidate_id])
                            if sorted(proof.get('frozen_plan', {}).get('family_fingerprints', [])) != family_fingerprints:
                                local_errors.append('frozen candidate family differs from declared campaign')
                    if not local_errors:
                        hold_decision = gk.evaluate_paired(hold, discovery_runs=disc,
                            replication_receipt_path=receipts.get(cand.candidate_id),
                            candidate_fingerprint=cand.fingerprint(), holdout_replicated=not synthetic)
                        if synthetic and hold_decision.verdict == 'SYNTHETIC_PASS':
                            final = 'SYNTHETIC_PASS'; diagnostic_success.append(cand.candidate_id)
                        elif not synthetic and hold_decision.verdict == 'PROMOTE':
                            final = 'PROMOTE'; promoted.append(cand.candidate_id)
                        else:
                            final = 'REJECT_FAILED_HOLDOUT_REPLICATION'
                    else:
                        final = 'REJECT_FAILED_HOLDOUT_REPLICATION'
                else:
                    final = 'SYNTHETIC_DISCOVERY_ONLY' if synthetic else 'KEEP_FOR_REPLICATION'
            else:
                final = disc_decision.verdict
        if local_errors:
            errors.extend(cand.candidate_id + ': ' + error for error in local_errors)
        candidate_results.append(dict(candidate_id=cand.candidate_id, fingerprint=cand.fingerprint(),
            is_negative_control=cand.is_negative_control, config=cand.canonical_payload(),
            discovery_decision=asdict(disc_decision) if disc_decision else None,
            holdout_decision=asdict(hold_decision) if hold_decision else None,
            final_verdict=final, integrity_errors=local_errors))
    if valid_controls != len(controls):
        errors.append('missing valid measured negative-control cohort')
    passed = not errors and not synthetic and bool(promoted) and valid_controls > 0 and false_positives == 0
    diagnostic_passed = not errors and synthetic and bool(diagnostic_success) and valid_controls > 0
    if errors:
        for row in candidate_results:
            if row['final_verdict'] in ('PROMOTE', 'SYNTHETIC_PASS', 'KEEP_FOR_REPLICATION'):
                row['pre_campaign_verdict'] = row['final_verdict']
                row['final_verdict'] = 'REJECT_INVALID_CAMPAIGN'
    return dict(gate_id='PB-060', num_hypotheses_tested=num_hypotheses,
        objective=objective, frozen_contract=gk.frozen_contract, candidate_family_fingerprints=family_fingerprints,
        skipped_duplicate_candidate_ids=skipped_duplicates, rejected_safety_envelope_candidates=rejected_envelope,
        negative_control_false_positives=false_positives, valid_negative_controls=valid_controls,
        negative_control_minimum_pairs=control_pairs_required,
        negative_control_evidence='SYNTHETIC_ONLY' if synthetic else 'PHYSICAL_PROVENANCE_REQUIRED',
        promoted_candidate_ids=promoted if passed else [],
        synthetic_pass_candidate_ids=diagnostic_success if diagnostic_passed else [], campaign_passed=passed,
        diagnostic_passed=diagnostic_passed,
        evidence_state='SYNTHETIC' if synthetic else ('BENCH_REPLICATED' if passed else None),
        integrity_errors=list(dict.fromkeys(errors)), candidate_evaluations=candidate_results)


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
    candidate_fingerprint: str | None = None,
) -> List[RunMetrics]:
    lengths = {len(values) for values in (arm_a_gp, arm_b_gp, arm_a_p99, arm_b_p99)}
    if len(lengths) != 1:
        raise ValueError('Synthetic paired fixture lengths differ')
    runs: List[RunMetrics] = []
    for idx in range(len(arm_a_gp)):
        runs.append(
            RunMetrics(
                run_id=f"{prefix}_A_{idx}",
                evidence_state='SYNTHETIC',
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
                evidence_state='SYNTHETIC',
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
    for run in runs:
        if run.arm == 'B':
            run.applied_config_sha256 = candidate_fingerprint
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

    configs = {cand.candidate_id: cand for cand in candidates}
    for cohorts in (discovery_runs, holdout_runs):
        for candidate_id, runs in cohorts.items():
            config = configs[candidate_id]
            for run in runs:
                if run.arm == 'B' or config.is_negative_control:
                    run.applied_config_sha256 = config.fingerprint()
            if config.is_negative_control:
                for index in range(0, len(runs), 2):
                    runs[index + 1].loss_pct = runs[index].loss_pct
                    runs[index + 1].worst_peer_goodput_mbps = runs[index].worst_peer_goodput_mbps
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
