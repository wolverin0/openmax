"""Consolidated pytest suite for Stages 655A to 660A (650-Stage Audit, 216-Window Multi-Radio Milestone & Cross-Fleet Champion v54.0)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(rel_path: str) -> dict:
    p = ROOT / rel_path
    assert p.exists(), f"Missing artifact: {rel_path}"
    return json.loads(p.read_text(encoding="utf-8"))


def _check_doc(rel_path: str) -> None:
    p = ROOT / rel_path
    assert p.exists(), f"Missing doc: {rel_path}"
    text = p.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1


def test_stage655a_multi_radio_216w_and_650stage_audit() -> None:
    data = _load("artifacts/autoresearch/stage655a_multi_radio_216w_and_650stage_audit.json")
    assert data["stage"] == "STAGE-655A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_multi_radio_windows"] == 216
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE655A_MULTI_RADIO_216W_AND_650STAGE_AUDIT.md")


def test_stage656a_nsga3_pareto_pb060_txop_tid_sched_and_vht40() -> None:
    data = _load("artifacts/autoresearch/stage656a_nsga3_pareto_pb060_txop_tid_sched_and_vht40.json")
    assert data["stage"] == "STAGE-656A"
    assert data["status"] == "CONFIRMED"
    assert len(data["pareto_front_ids"]) >= 2
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE656A_NSGA3_PARETO_PB060_TXOP_TID_SCHED_AND_VHT40.md")


def test_stage657a_cross_fleet_champion_v54_bundle() -> None:
    data = _load("artifacts/autoresearch/stage657a_cross_fleet_champion_v54_bundle.json")
    assert data["stage"] == "STAGE-657A"
    assert data["status"] == "CONFIRMED"
    assert data["champion_version"] == "v54.0"
    assert data["window_totals"]["total_cross_lane_windows"] == 684
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE657A_CROSS_FLEET_CHAMPION_V54_BUNDLE.md")


def test_stage658a_guarida_32cpe_pb060_voip_iptv_bulk_sim() -> None:
    data = _load("artifacts/autoresearch/stage658a_guarida_32cpe_pb060_voip_iptv_bulk_sim.json")
    assert data["stage"] == "STAGE-658A"
    assert data["status"] == "CONFIRMED"
    assert data["guarida_topology"]["total_panels"] == 3
    assert data["guarida_topology"]["total_cpes"] == 32
    assert data["triple_stack_summary"]["max_iptv_loss_pct"] == 0.0
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE658A_GUARIDA_32CPE_PB060_VOIP_IPTV_BULK_SIM.md")


def test_stage659a_memorymaster_and_650stage_ledger() -> None:
    data = _load("artifacts/autoresearch/stage659a_memorymaster_and_650stage_ledger.json")
    assert data["stage"] == "STAGE-659A"
    assert data["status"] == "CONFIRMED"
    assert data["scope"] == "project:futuramax"
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE659A_MEMORYMASTER_AND_650STAGE_LEDGER.md")


def test_stage660a_multi_radio_216w_v54_gate() -> None:
    data = _load("artifacts/autoresearch/stage660a_multi_radio_216w_v54_gate_receipt.json")
    assert data["stage"] == "STAGE-660A"
    assert data["status"] == "CONFIRMED"
    assert data["all_stages_passed"] is True
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE660A_MULTI_RADIO_216W_V54_GATE.md")
