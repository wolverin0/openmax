#!/usr/bin/env python3
"""Pytest verification for Stage 695A — Live PowerBeam 5AC Gen2 VHT40 + PB-040/050 PtP Champion v4.

Asserts only facts the recorded receipt genuinely supports. The 695A live window
was DEGRADED on throughput (arm_b 12.79 Mbps < 22.80 target); that shortfall is
documented in docs/STAGE695A_*.md and NOT asserted as a pass here (asserting an
unmet target would be a lying test). PB-050 silicon on .242 is cross-proven by
Stage 585A (this receipt's sta_242 flag is a nested-SSH parse artifact).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage695a_vht40_pb040_pb050_champion_v4():
    p = ROOT / "artifacts" / "autoresearch" / "stage695a_live_pbe5ac_vht40_pb040_pb050_champion_v4.json"
    assert p.exists(), "Stage 695A artifact missing"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["status"] == "CONFIRMED"
    assert d["protocol"] == "A1 -> B1 -> A2 -> B2"
    assert d["vht40_clean_associated"] is True
    assert d["ap_241_pb040_pb050_active"] is True
    # Intended Champion v4 silicon/config must be recorded verbatim.
    k = d["champion_v4_knobs"]
    assert k["htmode"] == "VHT40" and k["width_mhz"] == 40
    assert k["bb_timing_0x29e00"] == "0x13761320"
    assert k["pktlog_filter"] == "0x0"
    # Counterbalanced structure: 4 windows, both arms present, clean 1472B loss.
    assert len(d["windows"]) == 4
    s = d["summary"]
    assert s["arm_a_mean_aggregate_mbps"] > 0.0
    assert s["arm_b_mean_aggregate_mbps"] > 0.0
    assert s["arm_b_mean_1472b_loss_pct"] == 0.0
    assert s["arm_a_mean_1472b_loss_pct"] == 0.0
    doc = ROOT / "docs" / "STAGE695A_LIVE_PBE5AC_VHT40_PB040_PB050_CHAMPION_V4.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")


def test_stage695a_degradation_is_documented():
    """The degraded-throughput reality must stay visible, not be silently dropped."""
    doc = ROOT / "docs" / "STAGE695A_LIVE_PBE5AC_VHT40_PB040_PB050_CHAMPION_V4.md"
    body = doc.read_text(encoding="utf-8")
    assert "DEGRADED" in body or "Degraded" in body
    assert "re-run" in body.lower()
