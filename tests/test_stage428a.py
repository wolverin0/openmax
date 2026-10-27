"""Tests for Stage 428A — Live PBE5AC Ground-Up RAM Canary & Rescue Daemon."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "autoresearch" / "stage428a_live_pbe5ac_ground_up_ram_canary_and_rescue_daemon.json"
DOC = ROOT / "docs" / "STAGE428A_LIVE_PBE5AC_GROUND_UP_RAM_CANARY_AND_RESCUE_DAEMON.md"
SCRIPT = ROOT / "tools" / "benchmarks" / "run_stage428a_live_pbe5ac_ground_up_ram_canary_and_rescue_daemon.py"


def test_stage428a_files_and_schema():
    assert SCRIPT.exists()
    assert ARTIFACT.exists()
    assert DOC.exists()

    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 428A"
    assert data["status"] == "CONFIRMED"
    assert data["sta_242_wmi_hook_active"] is True
    assert data["ap_241_wmi_hook_active"] is True
    assert data["post_rescue_1472b_loss_pct"] <= 10.0
