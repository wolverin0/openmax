"""Tests for Stage 489A — Live PBE5AC Bidirectional E2E WDS Bridge Verification."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "autoresearch" / "stage489a_live_pbe5ac_bidirectional_end_to_end_via_mk1_251.json"
DOC = ROOT / "docs" / "STAGE489A_LIVE_PBE5AC_BIDIRECTIONAL_E2E_VIA_MK1_251.md"
SCRIPT = ROOT / "tools" / "benchmarks" / "run_stage489a_live_pbe5ac_bidirectional_end_to_end_via_mk1_251.py"


def test_stage489a_files_and_schema():
    assert SCRIPT.exists()
    assert ARTIFACT.exists()
    assert DOC.exists()

    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 489A"
    assert data["status"] == "CONFIRMED"
    assert data["ap_wds_vlan_active"] is True
    assert data["sta_4addr_wds_active"] is True
    assert data["host_pc_to_242_e2e_bytes"] == 4194304
