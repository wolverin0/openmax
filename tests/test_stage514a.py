"""Tests for Stage 514A: Real-Time Telemetry Exporter for PBE-5AC-Gen2 / LBE-5AC-Gen2 PtP Links (VHT40 Unlock, Fraunhofer Regime & WMM Queue Drops)."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage514a_pbe5ac_triple_play_and_vht40_telemetry_exporter.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE514A_PBE5AC_TRIPLE_PLAY_AND_VHT40_TELEMETRY_EXPORTER.md"


def test_stage514a_vht40_unlock_and_triple_play_telemetry():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "514A"
    vht40 = data["vht40_unlock_breakthrough"]
    assert vht40["sta_vht80_cap_unlock_verified"] is True
    assert vht40["vht40_40mhz_associated"] is True
    assert vht40["vht40_aggregate_mbps"] == 24.83
    assert vht40["voip_64b_loss_reduction_pct_points"] == 13.0
    assert len(data["exported_telemetry_frames"]) == 2
    assert "five_pillar_compliance" in data


def test_stage514a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
