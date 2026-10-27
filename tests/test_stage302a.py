from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S302A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage302a_ltu_thermal_rainfade_hysteresis_pareto.json"
S302A_MD = REPO_ROOT / "docs" / "STAGE302A_LTU_THERMAL_RAINFADE_HYSTERESIS_PARETO.md"


def test_stage302a_ltu_thermal_rainfade_hysteresis_pareto() -> None:
    assert S302A_JSON.exists()
    assert S302A_MD.exists()
    data = json.loads(S302A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "302A"
    assert data["safety_envelope"]["simulation_only"] is True
    b = data["benchmarks"]
    assert b["goodput_gain_mbps"] > 10.0
    assert b["p99_latency_reduction_ms"] > 1.0
    assert data["nsga2_pareto_front"]["solutions_count"] >= 1
    lines = S302A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
