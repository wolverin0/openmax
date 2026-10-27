"""Tests for Stage 490A — Live PBE5AC Xtensa SGMT RAM Bind-Mount Canary Proof."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "autoresearch" / "stage490a_live_pbe5ac_xtensa_sgmt_ram_canary_proof.json"
DOC = ROOT / "docs" / "STAGE490A_LIVE_PBE5AC_XTENSA_SGMT_RAM_CANARY_PROOF.md"
SCRIPT = ROOT / "tools" / "benchmarks" / "run_stage490a_live_pbe5ac_xtensa_sgmt_ram_canary_proof.py"


def test_stage490a_files_and_schema():
    assert SCRIPT.exists()
    assert ARTIFACT.exists()
    assert DOC.exists()

    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 490A"
    assert data["status"] == "CONFIRMED"
    assert data["ram_bind_mount_active"] is True
    assert data["zero_flash_bytes_modified"] is True
    assert len(data["firmware_files_sha256"]) >= 1
