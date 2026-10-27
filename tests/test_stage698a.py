#!/usr/bin/env python3
"""Pytest verification for Stage 698A — PowerBeam 5AC Gen2 & LiteBeam 5AC Gen2 Tester Release Package v4."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage698a_tester_release_package_v4():
    p = ROOT / "artifacts" / "autoresearch" / "stage698a_pbe5ac_lbe5ac_tester_release_package_v4.json"
    assert p.exists(), "Stage 698A artifact missing"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["status"] == "CONFIRMED"
    assert len(d["binaries"]) >= 2
    assert len(d["wa_board_compatibility_matrix"]) >= 4
    assert len(d["operator_3step_guide"]) == 3
    doc = ROOT / "docs" / "STAGE698A_PBE5AC_LBE5AC_TESTER_RELEASE_PACKAGE_V4.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
