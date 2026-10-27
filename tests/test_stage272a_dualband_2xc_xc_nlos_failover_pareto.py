from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
S272A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage272a_dualband_2xc_xc_nlos_failover_pareto.json"
S272A_DOC = REPO_ROOT / "docs" / "STAGE272A_DUALBAND_2XC_XC_NLOS_FAILOVER_PARETO.md"


def test_stage272a_dualband_2xc_xc_nlos_failover_pareto() -> None:
    assert S272A_JSON.exists(), "Missing stage272a_dualband_2xc_xc_nlos_failover_pareto.json"
    assert S272A_DOC.exists(), "Missing STAGE272A_DUALBAND_2XC_XC_NLOS_FAILOVER_PARETO.md"

    doc_text = S272A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S272A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-272A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    summary = data["simulation_and_pareto_summary"]
    assert summary["pareto_front_count"] >= 5
    assert summary["goodput_gain_mbps"] > 20.0
    assert summary["nlos_p99_rtt_reduction_ms"] > 5.0
    assert data["five_pillar_compliant"] is True
