"""Verification suite for Stage 102D (`T-S102D-LIVE-MKT-VLAN107-CSA-DFS-EVASION-UNDER-BTEST-LOAD`)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "artifacts" / "autoresearch" / "stage102d_mkt_vlan107_csa_under_load.json"
DOC_PATH = ROOT / "docs" / "STAGE102D_MKT_VLAN107_CSA_UNDER_LOAD_PROOF.md"


def test_stage102d_json_receipt_and_safety_invariants() -> None:
    assert JSON_PATH.exists(), f"Missing Stage 102D receipt: {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "102D"
    assert data["task_id"] == "T-S102D-LIVE-MKT-VLAN107-CSA-DFS-EVASION-UNDER-BTEST-LOAD"
    assert data["protocol"] == "A1->B1->A2->B2"
    safety = data["safety_invariants"]
    assert safety["flash_writes"] == 0
    assert safety["pbe5ac_241_242_untouched"] is True
    assert safety["guarida_sg01_backbone_untouched"] is True
    assert safety["boca7_isolated_in_vlan107"] is True


def test_stage102d_csa_under_load_and_station_retention() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    s = data["stage102d_csa_vlan107_summary"]
    assert s["station_retention"] == "3/3"
    assert s["stations_retained_count"] == 3
    assert s["arm_b_wa_to_mk1_e2e_p95_ms"] < s["arm_a_wa_to_mk1_e2e_p95_ms"]
    assert s["wa_to_mk1_e2e_p95_delta_pct"] < -50.0
    assert s["arm_b_voip_jitter_ms"] < s["arm_a_voip_jitter_ms"]
    assert s["pareto_delta_pct"] > 10.0
    assert len(data["rounds"]) == 1
    r0 = data["rounds"][0]
    assert set(r0["phases"].keys()) == {"A1", "B1", "A2", "B2"}


def test_stage102d_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing Stage 102D report: {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 180, f"Expected < 180 lines, got {len(lines)}"
    assert text.count("<!-- doc-head:") == 1
