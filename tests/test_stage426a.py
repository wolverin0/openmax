"""Tests for Stage 426A — Live PBE5AC Near-Field TX Power & A-MSDU/A-MPDU Sweep."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "autoresearch" / "stage426a_live_pbe5ac_txpower_and_ani_nearfield_sweep.json"
DOC = ROOT / "docs" / "STAGE426A_LIVE_PBE5AC_TXPOWER_AND_ANI_NEARFIELD_SWEEP.md"
SCRIPT = ROOT / "tools" / "benchmarks" / "run_stage426a_live_pbe5ac_txpower_and_ani_nearfield_sweep.py"


def test_stage426a_files_and_schema():
    assert SCRIPT.exists()
    assert ARTIFACT.exists()
    assert DOC.exists()

    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 426A"
    assert data["status"] == "CONFIRMED"
    assert len(data["configs"]) == 5
    assert data["champion"]["aggregate_mbps"] > 10.0
