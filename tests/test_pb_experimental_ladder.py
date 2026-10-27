"""Tests for Phase 0 Workstream C: QCA988x Physical-Boundary Experimental Ladder (PB-000..PB-070)."""

from __future__ import annotations

import copy
import pytest

from research.physical_boundary.ladder_schema import (
    CANONICAL_LADDER_IDS,
    LadderGate,
    check_gate_readiness,
    load_ladder,
    validate_ladder_dag,
)


def test_ladder_loads_all_16_canonical_gates_and_is_acyclic() -> None:
    gates = load_ladder()
    ids = tuple(g.id for g in gates)
    assert ids == CANONICAL_LADDER_IDS
    topo = validate_ladder_dag(gates)
    assert len(topo) == 16
    assert topo[0] == "PB-000"
    assert "PB-070" in topo


def test_all_hardware_touching_gates_disallow_automatic_execution() -> None:
    gates = load_ladder()
    for gate in gates:
        if gate.execution_mode != "offline":
            assert gate.automatic_execution_allowed is False, (
                f"{gate.id} has execution_mode={gate.execution_mode} so automatic_execution_allowed must be False"
            )
        assert len(gate.acceptance_criteria) > 20
        assert len(gate.falsification_criteria) > 20
        assert len(gate.rollback_condition) > 5


def test_pb070_custom_phy_gate_requires_pb023_and_pb040_and_is_blocked() -> None:
    gates = load_ladder()
    by_id = {g.id: g for g in gates}
    pb070 = by_id["PB-070"]
    assert "PB-023" in pb070.prerequisites
    assert "PB-040" in pb070.prerequisites
    assert pb070.status == "BLOCKED"

    readiness = check_gate_readiness("PB-070", gates)
    assert readiness["ready_to_execute"] is False
    assert "PB-023" in readiness["unmet_prerequisites"]
    assert "PB-040" in readiness["unmet_prerequisites"]

    readiness_when_prereqs_pass = check_gate_readiness(
        "PB-070",
        gates,
        passed_overrides={"PB-023", "PB-031", "PB-040"},
    )
    assert readiness_when_prereqs_pass["ready_to_execute"] is True
    assert readiness_when_prereqs_pass["unmet_prerequisites"] == []


def test_validator_rejects_cycles_and_hardware_auto_execution() -> None:
    gates = load_ladder()
    raw_gate = {
        "id": "PB-999",
        "title": "Unsafe hardware auto-exec gate",
        "hypothesis": "Test hypothesis",
        "branch_unlocked": "None",
        "branch_killed": "None",
        "prerequisites": ["PB-000"],
        "required_hardware": ["Sacrificial radio"],
        "required_software": ["Runner"],
        "safety_level": "L2",
        "brick_risk": "Medium",
        "regulatory_risk": "Low",
        "execution_mode": "cabled_bench",
        "primary_metrics": ["metric1"],
        "secondary_metrics": ["metric2"],
        "acceptance_criteria": "Valid acceptance criteria",
        "falsification_criteria": "Valid falsification criteria",
        "rollback_condition": "Power cycle",
        "artifacts_expected": ["out.json"],
        "status": "NOT_STARTED",
        "automatic_execution_allowed": True,
    }
    with pytest.raises(ValueError, match="MUST set automatic_execution_allowed=False"):
        LadderGate.from_dict(raw_gate)

    # Create a 2-node cycle between PB-000 and PB-001
    g0 = copy.deepcopy(gates[0])
    g1 = copy.deepcopy(gates[1])
    cyclic_g0 = LadderGate(**{**g0.__dict__, "prerequisites": ("PB-001",)})
    cyclic_gates = [cyclic_g0, g1] + list(gates[2:])
    with pytest.raises(ValueError, match="Cycle detected"):
        validate_ladder_dag(cyclic_gates)
