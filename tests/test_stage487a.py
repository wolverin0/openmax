"""Tests for Stage 487A — Live PBE5AC STA VHT80 Capability Unlock & VHT40 Sweep."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "autoresearch" / "stage487a_live_pbe5ac_sta_vht80_cap_and_vht40_unlock.json"
DOC = ROOT / "docs" / "STAGE487A_LIVE_PBE5AC_STA_VHT80_CAP_AND_VHT40_UNLOCK.md"
SCRIPT = ROOT / "tools" / "benchmarks" / "run_stage487a_live_pbe5ac_sta_vht80_cap_and_vht40_unlock.py"


def test_stage487a_files_and_schema():
    assert SCRIPT.exists()
    assert ARTIFACT.exists()
    assert DOC.exists()

    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 487A"
    assert data["status"] == "CONFIRMED"
    assert data["sta_vht80_cap_unlock_verified"] is True
    assert len(data["profiles"]) >= 2
