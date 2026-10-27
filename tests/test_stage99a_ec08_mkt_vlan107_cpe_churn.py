"""Verification suite for Stage 99A (`T-S99A-EC08-MKT-VLAN107-AND-3CPE-CHURN-RESILIENCE-PROOF`)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "artifacts" / "autoresearch" / "stage99a_ec08_mkt_vlan107_cpe_churn_benchmark.json"
DOC_PATH = ROOT / "docs" / "STAGE99A_EC08_MKT_VLAN107_CPE_CHURN_PROOF.md"


def test_stage99a_ec08_json_receipt_and_safety_invariants() -> None:
    assert JSON_PATH.exists(), f"Missing Stage 99A receipt: {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "99A"
    assert data["task_id"] == "T-S99A-EC08-MKT-VLAN107-AND-3CPE-CHURN-RESILIENCE-PROOF"
    assert data["protocol"] == "A1->B1->A2->B2"
    safety = data["safety_invariants"]
    assert safety["flash_writes"] == 0
    assert safety["pbe5ac_241_242_untouched"] is True
    assert safety["guarida_sg01_backbone_untouched"] is True
    assert safety["boca7_isolated_in_vlan107"] is True


def test_stage99a_ec08_churn_resilience_and_survivor_qoe() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    s = data["stage99a_ec08_churn_summary"]
    assert s["arm_b_survivor_wa_to_mk1_p95_ms"] < s["arm_a_survivor_wa_to_mk1_p95_ms"]
    assert s["survivor_wa_to_mk1_p95_delta_pct"] < 0.0
    assert s["arm_b_sector_p95_rtt_ms"] <= s["arm_a_sector_p95_rtt_ms"]
    assert s["arm_b_voip_loss_pct"] <= 1.0
    assert len(data["rounds"]) == 1
    r0 = data["rounds"][0]
    assert set(r0["phases"].keys()) == {"A1", "B1", "A2", "B2"}


def test_stage99a_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing Stage 99A report: {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 180, f"Expected < 180 lines, got {len(lines)}"
    assert text.count("<!-- doc-head:") == 1
