"""Tests for Stage 429A — Live PBE5AC Counterbalanced PtP Champion v2 vs Stock airOS 8."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "autoresearch" / "stage429a_live_pbe5ac_counterbalanced_v2_vs_airos8.json"
DOC = ROOT / "docs" / "STAGE429A_LIVE_PBE5AC_COUNTERBALANCED_V2_VS_AIROS8.md"
SCRIPT = ROOT / "tools" / "benchmarks" / "run_stage429a_live_pbe5ac_counterbalanced_v2_vs_airos8.py"


def test_stage429a_files_and_schema():
    assert SCRIPT.exists()
    assert ARTIFACT.exists()
    assert DOC.exists()

    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 429A"
    assert data["status"] == "CONFIRMED"
    assert [w["window"] for w in data["windows"]] == ["A1", "B1", "A2", "B2"]
    assert data["summary"]["arm_b_mean_ul_mbps"] > data["summary"]["arm_a_mean_ul_mbps"]
    assert data["summary"]["arm_b_mean_1472b_loss_pct"] <= data["summary"]["arm_a_mean_1472b_loss_pct"]
