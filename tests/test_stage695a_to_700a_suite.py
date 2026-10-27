#!/usr/bin/env python3
"""Consolidated Pytest Suite for Stages 695A..700A (Live PtP Champion v4 & 700-Stage Gate)."""

import json
from pathlib import Path

from tests.test_stage695a import test_stage695a_vht40_pb040_pb050_champion_v4
from tests.test_stage696a import test_stage696a_e2e_vht40_pb050_triple_play
from tests.test_stage697a import test_stage697a_dynamic_phy_and_sgmt_loader_v4
from tests.test_stage698a import test_stage698a_tester_release_package_v4
from tests.test_stage699a import test_stage699a_complete_evolution_ledger_v4

ROOT = Path(__file__).resolve().parents[1]

__all__ = [
    "test_stage695a_vht40_pb040_pb050_champion_v4",
    "test_stage696a_e2e_vht40_pb050_triple_play",
    "test_stage697a_dynamic_phy_and_sgmt_loader_v4",
    "test_stage698a_tester_release_package_v4",
    "test_stage699a_complete_evolution_ledger_v4",
]


def test_stage700a_live_gate_receipt():
    p = ROOT / "artifacts" / "autoresearch" / "stage700a_live_pbe5ac_ptp_v4_gate_receipt.json"
    assert p.exists(), "Stage 700A live gate receipt missing"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["status"] == "CONFIRMED"
    assert d["all_gates_passed"] is True
    assert d["live_devices_touched"] is False
    assert d["receipt_audit"]["all_receipts_ok"] is True
    # Every required upstream receipt (695A..699A) must have passed its invariant checks.
    assert len(d["receipt_audit"]["receipts"]) == 5
    assert all(r["ok"] for r in d["receipt_audit"]["receipts"])


def test_stage700a_doc_head_and_budget():
    doc = ROOT / "docs" / "STAGE700A_LIVE_PBE5AC_PTP_V4_GATE.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 180
    assert lines[0].startswith("<!-- doc-head:")
