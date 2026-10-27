"""Tests for Stage 425A — Live PBE5AC DL High-MCS Asymmetric Sweep."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "autoresearch" / "stage425a_live_pbe5ac_dl_high_mcs_asymmetric_sweep.json"
DOC = ROOT / "docs" / "STAGE425A_LIVE_PBE5AC_DL_HIGH_MCS_ASYMMETRIC_SWEEP.md"
SCRIPT = ROOT / "tools" / "benchmarks" / "run_stage425a_live_pbe5ac_dl_high_mcs_asymmetric_sweep.py"


def test_stage425a_files_and_schema():
    assert SCRIPT.exists(), "Stage 425A benchmark script must exist"
    assert ARTIFACT.exists(), "Stage 425A JSON artifact must exist"
    assert DOC.exists(), "Stage 425A documentation must exist"

    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220, f"Doc must be < 220 lines, got {len(lines)}"
    assert lines[0].startswith("<!-- doc-head:"), "Doc must start with <!-- doc-head: ... -->"

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 425A"
    assert data["status"] == "CONFIRMED"
    assert len(data["candidates"]) >= 6
    champ = data["champion"]
    assert champ["aggregate_mbps"] > 10.0
    assert champ["ping_1472b"]["loss_pct"] <= 10.0
