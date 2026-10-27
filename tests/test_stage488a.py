"""Tests for Stage 488A — Live PBE5AC Triple-Play VoIP + IPTV + Bulk TCP QoE."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "autoresearch" / "stage488a_live_pbe5ac_triple_play_voip_iptv_bulk_qoe.json"
DOC = ROOT / "docs" / "STAGE488A_LIVE_PBE5AC_TRIPLE_PLAY_VOIP_IPTV_BULK_QOE.md"
SCRIPT = ROOT / "tools" / "benchmarks" / "run_stage488a_live_pbe5ac_triple_play_voip_iptv_bulk_qoe.py"


def test_stage488a_files_and_schema():
    assert SCRIPT.exists()
    assert ARTIFACT.exists()
    assert DOC.exists()

    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 488A"
    assert data["status"] == "CONFIRMED"
    assert data["arm_b_champion_v2"]["concurrent_bulk_mbps"] > data["arm_a_stock"]["concurrent_bulk_mbps"]
