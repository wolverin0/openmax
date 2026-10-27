from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S290A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage290a_ltu_dynamic_duty_cycle_pareto.json"
S290A_MD = REPO_ROOT / "docs" / "STAGE290A_LTU_DYNAMIC_DUTY_CYCLE_PARETO.md"


def test_stage290a_ltu_dynamic_duty_cycle_pareto() -> None:
    assert S290A_JSON.exists()
    assert S290A_MD.exists()
    data = json.loads(S290A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "290A"
    assert data["safety_envelope"]["simulation_only"] is True
    b = data["benchmarks_32cpe"]
    assert b["auto_vs_fixed_ul_p99_reduction_ms"] > 0.5
    assert data["nsga2_pareto_front"]["solutions_count"] >= 1
    lines = S290A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
