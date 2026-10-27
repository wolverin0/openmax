"""Tests for Stage 430A — Universal WA PtP Champion v2 Kit & Full 425A..430A Suite."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "autoresearch" / "stage430a_pbe5ac_lbe5ac_wa_ptp_champion_v2_kit.json"
DOC = ROOT / "docs" / "STAGE430A_PBE5AC_LBE5AC_WA_PTP_CHAMPION_V2_KIT.md"
SCRIPT = ROOT / "tools" / "firmware" / "build_stage430a_pbe5ac_lbe5ac_wa_ptp_champion_v2_kit.py"


def test_stage430a_files_and_schema():
    assert SCRIPT.exists()
    assert ARTIFACT.exists()
    assert DOC.exists()

    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 430A"
    assert data["status"] == "CONFIRMED"
    assert len(data["supported_wa_boards"]) == 4
    assert data["live_sync_verified_on_241_and_242"] is True
