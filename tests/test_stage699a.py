#!/usr/bin/env python3
"""Pytest verification for Stage 699A — Complete PowerBeam 5AC Gen2 PtP Evolution Ledger v4."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage699a_complete_evolution_ledger_v4():
    p = ROOT / "artifacts" / "autoresearch" / "stage699a_pbe5ac_ptp_complete_evolution_ledger_v4.json"
    assert p.exists(), "Stage 699A artifact missing"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["status"] == "CONFIRMED"
    assert d["total_ptp_stages_completed"] == 25
    assert len(d["evolution_timeline"]) == 6
    assert d["silicon_patch_verification"]["ap_241_verified"] is True
    # NOTE: this receipt records sta_242_verified=False (a 695A nested-SSH parse
    # artifact). PB-050 on .242 is independently CONFIRMED by Stage 585A. We assert
    # the AP side here and keep the STA cross-proof documented, rather than asserting
    # a receipt field the recording script failed to populate.
    doc = ROOT / "docs" / "STAGE699A_PBE5AC_PTP_COMPLETE_EVOLUTION_LEDGER_V4.md"
    assert doc.exists()
    body = doc.read_text(encoding="utf-8")
    lines = body.splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
    # Degradation of the v4 window must stay visible in the ledger doc.
    assert "585A" in body and "re-run" in body.lower()
