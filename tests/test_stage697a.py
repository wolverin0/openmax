#!/usr/bin/env python3
"""Pytest verification for Stage 697A — Dynamic phy* Wiphy Index & RAM SGMT Bind-Mount Loader v4."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage697a_dynamic_phy_and_sgmt_loader_v4():
    p = ROOT / "artifacts" / "autoresearch" / "stage697a_pbe5ac_dynamic_phy_and_sgmt_loader_v4.json"
    assert p.exists(), "Stage 697A artifact missing"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["status"] == "CONFIRMED"
    assert d["deployed_on_241_and_242"] is True
    assert d["watchdog_non_dfs_s"] == 45
    assert d["watchdog_dfs_s"] == 120
    assert (ROOT / d["loader_path"]).exists()
    assert (ROOT / d["champion_v4_path"]).exists()
    doc = ROOT / "docs" / "STAGE697A_PBE5AC_DYNAMIC_PHY_AND_SGMT_LOADER_V4.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
