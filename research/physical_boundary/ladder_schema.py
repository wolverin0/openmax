"""Schema validator and DAG readiness checker for the QCA988x Physical-Boundary Experimental Ladder (PB-000..PB-070)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
import yaml

CANONICAL_LADDER_IDS: Tuple[str, ...] = (
    "PB-000",
    "PB-001",
    "PB-010",
    "PB-011",
    "PB-020",
    "PB-021",
    "PB-022",
    "PB-023",
    "PB-024",
    "PB-030",
    "PB-031",
    "PB-040",
    "PB-050",
    "PB-051",
    "PB-060",
    "PB-070",
)

VALID_SAFETY_LEVELS: Set[str] = {"L0", "L1", "L2", "L3", "L4"}
VALID_BRICK_RISKS: Set[str] = {"None", "Low", "Low-Medium", "Medium", "High"}
VALID_EXECUTION_MODES: Set[str] = {
    "offline",
    "cabled_bench",
    "shielded_ota",
    "sacrificial_pair",
    "production_canary",
}
VALID_GATE_STATUSES: Set[str] = {
    "NOT_STARTED",
    "READY_FOR_BENCH",
    "BLOCKED",
    "PASSED",
    "FAILED",
    "INCONCLUSIVE",
}

REQUIRED_GATE_FIELDS: Tuple[str, ...] = (
    "id",
    "title",
    "hypothesis",
    "branch_unlocked",
    "branch_killed",
    "prerequisites",
    "required_hardware",
    "required_software",
    "safety_level",
    "brick_risk",
    "regulatory_risk",
    "execution_mode",
    "primary_metrics",
    "secondary_metrics",
    "acceptance_criteria",
    "falsification_criteria",
    "rollback_condition",
    "artifacts_expected",
    "status",
    "automatic_execution_allowed",
)

DEFAULT_LADDER_PATH = Path(__file__).resolve().parent / "ladder.yaml"


@dataclass(frozen=True)
class LadderGate:
    id: str
    title: str
    hypothesis: str
    branch_unlocked: str
    branch_killed: str
    prerequisites: Tuple[str, ...]
    required_hardware: Tuple[str, ...]
    required_software: Tuple[str, ...]
    safety_level: str
    brick_risk: str
    regulatory_risk: str
    execution_mode: str
    primary_metrics: Tuple[str, ...]
    secondary_metrics: Tuple[str, ...]
    acceptance_criteria: str
    falsification_criteria: str
    rollback_condition: str
    artifacts_expected: Tuple[str, ...]
    status: str
    automatic_execution_allowed: bool

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> LadderGate:
        for field_name in REQUIRED_GATE_FIELDS:
            if field_name not in raw:
                raise ValueError(f"Gate {raw.get('id', '<unknown>')} missing required field '{field_name}'.")

        gate_id = str(raw["id"]).strip()
        for text_field in (
            "title",
            "hypothesis",
            "branch_unlocked",
            "branch_killed",
            "regulatory_risk",
            "acceptance_criteria",
            "falsification_criteria",
            "rollback_condition",
        ):
            val = str(raw[text_field]).strip()
            if not val:
                raise ValueError(f"Gate {gate_id} has empty required text field '{text_field}'.")

        safety_level = str(raw["safety_level"]).strip()
        if safety_level not in VALID_SAFETY_LEVELS:
            raise ValueError(f"Gate {gate_id} invalid safety_level={safety_level!r}; must be in {VALID_SAFETY_LEVELS}.")

        brick_risk = str(raw["brick_risk"]).strip()
        if brick_risk not in VALID_BRICK_RISKS:
            raise ValueError(f"Gate {gate_id} invalid brick_risk={brick_risk!r}; must be in {VALID_BRICK_RISKS}.")

        execution_mode = str(raw["execution_mode"]).strip()
        if execution_mode not in VALID_EXECUTION_MODES:
            raise ValueError(
                f"Gate {gate_id} invalid execution_mode={execution_mode!r}; must be in {VALID_EXECUTION_MODES}."
            )

        status = str(raw["status"]).strip()
        if status not in VALID_GATE_STATUSES:
            raise ValueError(f"Gate {gate_id} invalid status={status!r}; must be in {VALID_GATE_STATUSES}.")

        auto_allowed = raw["automatic_execution_allowed"]
        if not isinstance(auto_allowed, bool):
            raise ValueError(f"Gate {gate_id} automatic_execution_allowed must be boolean.")

        # Phase 0 safety invariant: no hardware-touching experiment may allow automatic execution
        if execution_mode != "offline" and auto_allowed:
            raise ValueError(
                f"Gate {gate_id} touches hardware (execution_mode={execution_mode!r}) "
                f"and MUST set automatic_execution_allowed=False during Phase 0."
            )

        for list_field in ("required_hardware", "required_software", "primary_metrics", "artifacts_expected"):
            seq = raw[list_field]
            if not isinstance(seq, list) or len(seq) == 0:
                raise ValueError(f"Gate {gate_id} field '{list_field}' must be a non-empty list.")

        prereqs = raw["prerequisites"]
        if not isinstance(prereqs, list):
            raise ValueError(f"Gate {gate_id} field 'prerequisites' must be a list.")

        return cls(
            id=gate_id,
            title=str(raw["title"]).strip(),
            hypothesis=str(raw["hypothesis"]).strip(),
            branch_unlocked=str(raw["branch_unlocked"]).strip(),
            branch_killed=str(raw["branch_killed"]).strip(),
            prerequisites=tuple(str(p).strip() for p in prereqs),
            required_hardware=tuple(str(x).strip() for x in raw["required_hardware"]),
            required_software=tuple(str(x).strip() for x in raw["required_software"]),
            safety_level=safety_level,
            brick_risk=brick_risk,
            regulatory_risk=str(raw["regulatory_risk"]).strip(),
            execution_mode=execution_mode,
            primary_metrics=tuple(str(x).strip() for x in raw["primary_metrics"]),
            secondary_metrics=tuple(str(x).strip() for x in raw["secondary_metrics"]),
            acceptance_criteria=str(raw["acceptance_criteria"]).strip(),
            falsification_criteria=str(raw["falsification_criteria"]).strip(),
            rollback_condition=str(raw["rollback_condition"]).strip(),
            artifacts_expected=tuple(str(x).strip() for x in raw["artifacts_expected"]),
            status=status,
            automatic_execution_allowed=auto_allowed,
        )


def load_ladder(path: Optional[Path] = None) -> List[LadderGate]:
    """Loads and validates the physical-boundary ladder YAML file."""
    target = path or DEFAULT_LADDER_PATH
    data = yaml.safe_load(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "gates" not in data:
        raise ValueError(f"Ladder file {target} must contain top-level 'gates' list.")
    gates = [LadderGate.from_dict(item) for item in data["gates"]]
    validate_ladder_dag(gates)
    return gates


def validate_ladder_dag(
    gates: Sequence[LadderGate],
    require_canonical_ids: bool = True,
) -> Tuple[str, ...]:
    """Validates unique IDs, canonical PB-000..PB-070 coverage, prerequisite references, and DAG acyclicity."""
    by_id: Dict[str, LadderGate] = {}
    for g in gates:
        if g.id in by_id:
            raise ValueError(f"Duplicate gate id '{g.id}' in experimental ladder.")
        by_id[g.id] = g

    if require_canonical_ids:
        missing = [cid for cid in CANONICAL_LADDER_IDS if cid not in by_id]
        if missing:
            raise ValueError(f"Ladder is missing canonical gate IDs: {missing}")

    # Verify prerequisite references exist
    for g in gates:
        for prereq in g.prerequisites:
            if prereq not in by_id:
                raise ValueError(f"Gate {g.id} references unknown prerequisite '{prereq}'.")
            if prereq == g.id:
                raise ValueError(f"Gate {g.id} cannot depend on itself.")

    # Verify PB-070 custom-PHY gate enforces strict prerequisites
    if "PB-070" in by_id:
        pb070 = by_id["PB-070"]
        for required_prereq in ("PB-023", "PB-040"):
            if required_prereq not in pb070.prerequisites:
                raise ValueError(
                    f"PB-070 (Custom PHY eligibility gate) must require '{required_prereq}' as a prerequisite."
                )

    # Topological sort (Kahn's algorithm) to detect cycles
    in_degree: Dict[str, int] = {g.id: len(g.prerequisites) for g in gates}
    dependents: Dict[str, List[str]] = {g.id: [] for g in gates}
    for g in gates:
        for prereq in g.prerequisites:
            dependents[prereq].append(g.id)

    ready = sorted([gid for gid, deg in in_degree.items() if deg == 0])
    topo_order: List[str] = []

    while ready:
        curr = ready.pop(0)
        topo_order.append(curr)
        for dep in sorted(dependents[curr]):
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                ready.append(dep)
                ready.sort()

    if len(topo_order) != len(gates):
        cyclic = sorted(set(by_id.keys()) - set(topo_order))
        raise ValueError(f"Cycle detected in experimental ladder prerequisites involving: {cyclic}")

    return tuple(topo_order)


def check_gate_readiness(
    gate_id: str,
    gates: Sequence[LadderGate],
    passed_overrides: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Checks whether all prerequisites for a given gate have status PASSED (or are in passed_overrides)."""
    by_id = {g.id: g for g in gates}
    if gate_id not in by_id:
        raise KeyError(f"Unknown gate_id '{gate_id}'.")

    gate = by_id[gate_id]
    if passed_overrides is not None:
        passed_set = set(passed_overrides)
    else:
        passed_set = {g.id for g in gates if g.status == "PASSED"}

    unmet = [p for p in gate.prerequisites if p not in passed_set]
    return {
        "gate_id": gate.id,
        "title": gate.title,
        "ready_to_execute": len(unmet) == 0,
        "unmet_prerequisites": unmet,
        "safety_level": gate.safety_level,
        "execution_mode": gate.execution_mode,
        "automatic_execution_allowed": gate.automatic_execution_allowed,
    }
