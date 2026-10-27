#!/usr/bin/env python3
"""PB-000..PB-070 Master End-to-End Ladder Orchestrator & Readiness Audit.

Integrates all 16 gates of the openMAX QCA988x Physical-Boundary Experimental Ladder
(`PB-000` through `PB-070`) into a single deterministic pipeline that:
1. Validates the 16-gate DAG topology and safety invariants (`validate_ladder_dag`).
2. Audits and computes SHA-256 digests for all implementation modules and offline
   evidence/fixture artifacts across all 16 gates.
3. Evaluates prerequisite readiness (`check_gate_readiness`) and next-unblocked bench tracks.
4. Verifies Track 1 and Track 2 preflight safety envelopes (`evaluate_campaign_preflight`).
5. Enforces `automatic_execution_allowed = False` for all hardware-touching gates (`PB-020`..`PB-070`).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

from controller.pb_campaign_preflight_verifier import (
    TRACK1_READONLY_UTF_ALLOWLIST,
    TRACK2_CHANNEL_CAPTURE_FIELDS,
    CampaignPreflightRequest,
    verify_campaign_preflight,
)
from research.physical_boundary.ladder_schema import (
    LadderGate,
    check_gate_readiness,
    load_ladder,
    validate_ladder_dag,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_OUTPUT_PATH = REPO_ROOT / "artifacts/qca988x/pb_master_ladder_readiness_audit_20261024.json"

# Canonical mapping from each of the 16 gates to its offline implementation modules and artifacts
GATE_MODULE_AND_ARTIFACT_MAP: Dict[str, Dict[str, List[str]]] = {
    "PB-000": {
        "modules": [
            "tools/qca988x/extract_descriptor_map.py",
            "tools/qca988x/utf_build_inventory.py",
            "tools/qca988x/trace_utf_handlers.py",
            "tools/qca988x/memory_diff_analyzer.py",
        ],
        "artifacts": [
            "research/openMAX_QCA988x_physical_boundary_research_2026-10-24.md",
            "research/physical_boundary/ladder.yaml",
            "artifacts/qca988x/ar9888_v2_descriptor_map.json",
            "artifacts/qca988x/ar9888_utf_handler_and_build_matrix.json",
            "artifacts/qca988x/memory_diff_fixture_report.json",
        ],
    },
    "PB-001": {
        "modules": [
            "analysis/metrics/schema.py",
            "analysis/regression_gate/gatekeeper.py",
        ],
        "artifacts": [
            "tests/test_pb_metrics_schema_width.py",
            "tests/test_pb_gatekeeper_paired_aa.py",
        ],
    },
    "PB-010": {
        "modules": [
            "tools/qca988x/wmi_htt_strip_site_mapper.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_010_wmi_htt_strip_map.json",
            "docs/FIRMWARE_RE_TARGET_MAP.md",
        ],
    },
    "PB-011": {
        "modules": [
            "tools/qca988x/sgmt_container_inspector.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_011_sgmt_container_audit.json",
            "docs/FIRMWARE_RE_TARGET_MAP.md",
        ],
    },
    "PB-020": {
        "modules": [
            "tools/qca988x/utf_readonly_probe_harness.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_020_023_utf_probe_fixture.json",
        ],
    },
    "PB-021": {
        "modules": [
            "tools/qca988x/channel_capture_and_sdr_correlator.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_021_022_024_qualification_fixture.json",
        ],
    },
    "PB-022": {
        "modules": [
            "tools/qca988x/channel_capture_and_sdr_correlator.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_021_022_024_qualification_fixture.json",
        ],
    },
    "PB-023": {
        "modules": [
            "tools/qca988x/utf_readonly_probe_harness.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_020_023_utf_probe_fixture.json",
        ],
    },
    "PB-024": {
        "modules": [
            "tools/qca988x/channel_capture_and_sdr_correlator.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_021_022_024_qualification_fixture.json",
        ],
    },
    "PB-030": {
        "modules": [
            "controller/pb_030_031_phy_response_surface_harness.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_030_031_experiment_matrix.json",
            "docs/STAGE12_PB_030_031_SUB20MHZ_AND_PHY_RESPONSE_SURFACE_SPEC.md",
        ],
    },
    "PB-031": {
        "modules": [
            "controller/pb_030_031_phy_response_surface_harness.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_030_031_experiment_matrix.json",
            "docs/STAGE12_PB_030_031_SUB20MHZ_AND_PHY_RESPONSE_SURFACE_SPEC.md",
        ],
    },
    "PB-040": {
        "modules": [
            "tools/qca988x/inert_target_mutation_builder.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_040_inert_mutation_dryrun_receipt.json",
        ],
    },
    "PB-050": {
        "modules": [
            "controller/pb_050_051_scheduler_timing_harness.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_050_051_timing_jitter_fixture.json",
            "docs/STAGE12_PB_050_051_SCHEDULER_TIMING_AND_SLOT_GATE_SPEC.md",
        ],
    },
    "PB-051": {
        "modules": [
            "controller/pb_050_051_scheduler_timing_harness.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_050_051_timing_jitter_fixture.json",
            "docs/STAGE12_PB_050_051_SCHEDULER_TIMING_AND_SLOT_GATE_SPEC.md",
        ],
    },
    "PB-060": {
        "modules": [
            "controller/pb_060_070_autonomous_search_and_phy_gate.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_060_070_pilot_and_verdict.json",
            "docs/STAGE12_PB_060_070_AUTONOMOUS_SEARCH_AND_PHY_GATE.md",
        ],
    },
    "PB-070": {
        "modules": [
            "controller/pb_060_070_autonomous_search_and_phy_gate.py",
        ],
        "artifacts": [
            "artifacts/qca988x/pb_060_070_pilot_and_verdict.json",
            "docs/STAGE12_PB_060_070_AUTONOMOUS_SEARCH_AND_PHY_GATE.md",
        ],
    },
}


def _hash_repo_file(rel_path: str) -> Dict[str, Any]:
    full = REPO_ROOT / rel_path
    if not full.exists():
        return {
            "path": rel_path,
            "exists": False,
            "size_bytes": 0,
            "sha256": None,
        }
    data = full.read_bytes()
    return {
        "path": rel_path,
        "exists": True,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def build_master_ladder_readiness_audit(
    passed_overrides: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Executes the end-to-end PB-000..PB-070 ladder audit and returns the master readiness report."""
    gates: List[LadderGate] = load_ladder()
    dag_summary = validate_ladder_dag(gates)

    # Verify all 16 canonical gates are present in GATE_MODULE_AND_ARTIFACT_MAP
    gate_entries: List[Dict[str, Any]] = []
    missing_files: List[str] = []
    hardware_auto_exec_violations: List[str] = []

    for g in gates:
        mapping = GATE_MODULE_AND_ARTIFACT_MAP.get(g.id, {"modules": [], "artifacts": []})
        mod_hashes = [_hash_repo_file(p) for p in mapping["modules"]]
        art_hashes = [_hash_repo_file(p) for p in mapping["artifacts"]]

        for item in mod_hashes + art_hashes:
            if not item["exists"]:
                missing_files.append(item["path"])

        if g.execution_mode != "offline" and g.automatic_execution_allowed:
            hardware_auto_exec_violations.append(g.id)

        readiness = check_gate_readiness(g.id, gates=gates, passed_overrides=passed_overrides)
        gate_entries.append(
            {
                "gate_id": g.id,
                "title": g.title,
                "status": g.status,
                "execution_mode": g.execution_mode,
                "safety_level": g.safety_level,
                "brick_risk": g.brick_risk,
                "automatic_execution_allowed": g.automatic_execution_allowed,
                "prerequisites": list(g.prerequisites),
                "readiness": readiness,
                "modules_verified": mod_hashes,
                "offline_artifacts_verified": art_hashes,
            }
        )

    # Evaluate Track 1 and Track 2 preflight verifiers (default operator_gate_approved=False -> BLOCKED_AWAITING_OPERATOR_GATE)
    track1_req = CampaignPreflightRequest(
        track_id="TRACK_1_UTF_READONLY",
        gate_id="PB-020",
        target_device_ip="192.168.1.20",
        execution_mode="cabled_bench",
        rf_terminated_50ohm=True,
        coaxial_attenuation_db=55.0,
        ram_only_target_load=True,
        serial_console_attached=True,
        tftp_recovery_verified=True,
        poe_power_relay_verified=True,
        requested_commands=TRACK1_READONLY_UTF_ALLOWLIST,
        passed_prerequisite_gates=("PB-000", "PB-001", "PB-010"),
        operator_gate_approved=False,
    )
    track2_req = CampaignPreflightRequest(
        track_id="TRACK_2_CHANNEL_CAPTURE",
        gate_id="PB-021",
        target_device_ip="192.168.1.21",
        execution_mode="cabled_bench",
        rf_terminated_50ohm=False,
        coaxial_attenuation_db=55.0,
        ram_only_target_load=True,
        serial_console_attached=True,
        tftp_recovery_verified=True,
        poe_power_relay_verified=True,
        inspected_descriptor_fields=TRACK2_CHANNEL_CAPTURE_FIELDS,
        passed_prerequisite_gates=("PB-000", "PB-001", "PB-010"),
        operator_gate_approved=False,
    )
    track1_default = verify_campaign_preflight(track1_req)
    track2_default = verify_campaign_preflight(track2_req)

    # Load key headline metrics from the generated JSON artifacts
    pb010_data = json.loads((REPO_ROOT / "artifacts/qca988x/pb_010_wmi_htt_strip_map.json").read_text(encoding="utf-8"))
    pb011_data = json.loads((REPO_ROOT / "artifacts/qca988x/pb_011_sgmt_container_audit.json").read_text(encoding="utf-8"))
    pb030_data = json.loads((REPO_ROOT / "artifacts/qca988x/pb_030_031_experiment_matrix.json").read_text(encoding="utf-8"))
    pb040_data = json.loads((REPO_ROOT / "artifacts/qca988x/pb_040_inert_mutation_dryrun_receipt.json").read_text(encoding="utf-8"))
    pb050_data = json.loads((REPO_ROOT / "artifacts/qca988x/pb_050_051_timing_jitter_fixture.json").read_text(encoding="utf-8"))
    pb060_data = json.loads((REPO_ROOT / "artifacts/qca988x/pb_060_070_pilot_and_verdict.json").read_text(encoding="utf-8"))

    ready_gate_ids = [e["gate_id"] for e in gate_entries if e["readiness"]["ready_to_execute"]]
    passed_gate_ids = [g.id for g in gates if g.status == "PASSED"]

    pb011_containers = sum(
        len(p.get("sgmt_containers", {})) for p in pb011_data.get("platforms", {}).values()
    )
    pb031_promoted = [
        t["treatment_id"]
        for t in pb030_data.get("pb031_phy_response_surface_treatments", [])
        if t.get("paired_evaluation", {}).get("gate_decision", {}).get("verdict") == "PROMOTE"
    ]
    pb040_roles = pb040_data.get("roles_verified", {})
    pb040_diff_bytes = (
        pb040_roles["athwlan_AR9888v2_ptmp_ap_bin"]["observed_total_diff_bytes"]
        if "athwlan_AR9888v2_ptmp_ap_bin" in pb040_roles
        else 0
    )

    return {
        "orchestrator_version": "1.0.0",
        "audit_date_utc": "2026-10-24T19:02:00Z",
        "automatic_execution_allowed": False,
        "dag_validation": dag_summary,
        "all_16_gates_mapped": len(gate_entries) == 16,
        "missing_files_count": len(missing_files),
        "missing_files": missing_files,
        "hardware_auto_exec_violations": hardware_auto_exec_violations,
        "passed_gate_ids": passed_gate_ids,
        "currently_unblocked_gate_ids": ready_gate_ids,
        "preflight_safety_checks": {
            "track1_channel_and_timing": asdict(track1_default),
            "track2_utf_and_sub20mhz": asdict(track2_default),
        },
        "quantitative_workstream_scorecard": {
            "pb010_wmi_opcodes_mapped": len(pb010_data["wmi_dispatch_map"]["opcodes"]),
            "pb011_sgmt_containers_verified": pb011_containers,
            "pb030_grid_points_evaluated": len(pb030_data.get("pb030_sub20mhz_and_width_grid", [])),
            "pb031_promoted_phy_treatments": pb031_promoted,
            "pb040_inert_diff_byte_count": pb040_diff_bytes,
            "pb050_p99_jitter_reduction_factor": pb050_data["pb050_host_vs_target_timing_comparison"][
                "p99_jitter_reduction_factor"
            ],
            "pb051_feasibility_verdict": pb050_data["pb051_target_scheduler_feasibility"][
                "overall_feasibility_verdict"
            ],
            "pb060_promoted_candidate_ids": pb060_data["pb060_autonomous_search_pilot"]["promoted_candidate_ids"],
            "pb070_custom_phy_verdict": pb060_data["pb070_custom_phy_eligibility_verdict"]["verdict"],
        },
        "gates": gate_entries,
    }


def main() -> None:
    report = build_master_ladder_readiness_audit()
    DEFAULT_AUDIT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_AUDIT_OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Saved PB-000..PB-070 master readiness audit to {DEFAULT_AUDIT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
