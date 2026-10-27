"""Tests for Stages 203A, 204A, and 205A (Guarida 4-Radio Spectral Audit, Pymoo Frequency Optimizer & Zero-False-Positive RF Scorecard)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage203a_guarida_4radio_spectral_coexistence_audit() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage203a_guarida_4radio_spectral_coexistence_audit.json"
    assert p.exists(), "Missing Stage 203A JSON artifact"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "203A"
    assert data["production_safety_audit"]["almafuerte_60_writes"] == 0
    assert data["production_safety_audit"]["guarida_61_writes"] == 0
    assert data["production_safety_audit"]["panel2_82_writes"] == 0
    assert data["production_safety_audit"]["panel3_83_writes"] == 0
    assert data["production_safety_audit"]["panel1_84_writes"] == 0

    radios = {r["radio_id"]: r for r in data["tower_radios"]}
    assert len(radios) == 4
    assert radios["GUARIDA_BACKHAUL_STA_61"]["center_freq_mhz"] == 5355
    assert radios["PANEL1_GUARIDA_84"]["center_freq_mhz"] == 5240
    assert radios["PANEL3_GUARIDA_83"]["center_freq_mhz"] == 5755
    assert radios["PANEL2_GUARIDA_82"]["center_freq_mhz"] == 5805

    assert len(data["pairwise_guard_band_matrix"]) == 6
    assert data["key_spectral_findings"]["panel2_panel3_center_separation_mhz"] == 50
    assert data["key_spectral_findings"]["panel2_panel3_narrow_guard_band_mhz"] == 30

    doc = REPO_ROOT / "docs" / "STAGE203A_GUARIDA_4RADIO_SPECTRAL_COEXISTENCE_AUDIT.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1

    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"], f"Stage 203A failed 5-pillar gate: {audit}"


def test_stage204a_guarida_tower_frequency_pareto_plan() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage204a_guarida_tower_frequency_pareto_plan.json"
    assert p.exists(), "Missing Stage 204A JSON artifact"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "204A"
    assert data["production_safety_audit"]["writes_performed"] == 0
    assert data["optimizer_metadata"]["engine"] == "pymoo NSGA-II"
    assert data["optimizer_metadata"]["pareto_solutions_count"] >= 5

    plan = data["recommended_frequency_and_power_plan"]
    assert plan["panel1_84"]["recommended_freq_mhz"] == 5180
    assert plan["backhaul_60_61"]["recommended_freq_mhz"] == 5500
    assert plan["panel3_83"]["recommended_freq_mhz"] == 5745
    assert plan["panel2_82"]["recommended_freq_mhz"] == 5825
    assert plan["expected_improvements"]["panel3_panel2_edge_guard_mhz_after"] == 60

    doc = REPO_ROOT / "docs" / "STAGE204A_GUARIDA_TOWER_FREQUENCY_PARETO_PLAN.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1

    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"], f"Stage 204A failed 5-pillar gate: {audit}"


def test_stage205a_guarida_zero_false_positive_rf_scorecard() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage205a_guarida_zero_false_positive_rf_scorecard.json"
    assert p.exists(), "Missing Stage 205A JSON artifact"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "205A"
    assert data["production_safety_audit"]["writes_performed"] == 0

    summary = data["summary"]
    assert summary["total_scored_entities"] == 33
    assert summary["backhaul_links_scored"] == 1
    assert summary["total_guarida_cpes_scored"] == 32
    assert summary["single_poll_false_down_prob_dual_round_5ping"] < 1e-12

    doc = REPO_ROOT / "docs" / "STAGE205A_GUARIDA_ZERO_FALSE_POSITIVE_RF_SCORECARD.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1

    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"], f"Stage 205A failed 5-pillar gate: {audit}"
