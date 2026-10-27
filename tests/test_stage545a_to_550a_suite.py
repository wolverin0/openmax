"""Consolidated test suite for Stages 545A to 550A."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage550a_consolidated_receipt_and_docs():
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage550a_550stage_milestone_gate_receipt.json"
    doc_path = REPO_ROOT / "docs" / "STAGE550A_550STAGE_MILESTONE_GATE.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "550A"
    assert len(data["verified_stages"]) == 5
    assert data["repo_5pillar_gate_result"]["compliant"] is True
    assert data["safety_boundaries"]["touched_protected_ips"] is False

    for sh_rel in data["shell_kits_verified_lf"]:
        sh_path = REPO_ROOT / sh_rel
        assert sh_path.exists()
        assert b"\r\n" not in sh_path.read_bytes()

    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1


def test_5pillar_repo_gate_remains_compliant_after_550a():
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "verify" / "enforce_5pillar_research_gate.py"), "--check-repo"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    gate = json.loads(proc.stdout)
    assert gate["compliant"] is True
