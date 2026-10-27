#!/usr/bin/env python3
"""Consolidated Pytest Suite for Stages 695A..700A (PowerBeam 5AC Gen2 PtP Champion v4 & 700-Stage Milestone)."""

import json
from pathlib import Path

from tests.test_stage695a import test_stage695a_vht40_pb040_pb050_champion_v4
from tests.test_stage696a import test_stage696a_e2e_vht40_pb050_triple_play
from tests.test_stage697a import test_stage697a_dynamic_phy_and_sgmt_loader_v4
from tests.test_stage698a import test_stage698a_tester_release_package_v4
from tests.test_stage699a import test_stage699a_complete_evolution_ledger_v4

ROOT = Path(__file__).resolve().parents[1]


def test_stage700a_master_gate_receipt():
    p = ROOT / "artifacts" / "verification" / "stage700a_pbe5ac_ptp_champion_v4_700stage_gate_receipt.json"
    assert p.exists(), "Stage 700A receipt missing"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["status"] == "CONFIRMED"
    assert d["all_gates_passed"] is True
    doc = ROOT / "docs" / "STAGE700A_PBE5AC_PTP_CHAMPION_V4_700STAGE_GATE.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
