#!/usr/bin/env python3
"""Pytest verification for Stage 696A — Live PowerBeam 5AC Gen2 E2E via MK1-251 VHT40 + PB-050 Triple-Play."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage696a_e2e_vht40_pb050_triple_play():
    p = ROOT / "artifacts" / "autoresearch" / "stage696a_live_pbe5ac_mk1_251_e2e_vht40_pb050_triple_play.json"
    assert p.exists(), "Stage 696A artifact missing"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["status"] == "CONFIRMED"
    assert d["ap_wds_vlan_active"] is True
    assert d["sta_4addr_wds_active"] is True
    assert d["multicast_snooping_active"] is True
    assert d["host_pc_to_242_e2e_bytes"] == 4194304
    assert d["host_pc_to_242_e2e_single_tcp_mbps"] > 5.0
    assert d["arm_b_champion_v4_vht40"]["concurrent_bulk_mbps"] > 3.0
    assert d["post_restore_vht20_1472b_ping"]["loss_pct"] == 0.0
    doc = ROOT / "docs" / "STAGE696A_LIVE_PBE5AC_MK1_251_E2E_VHT40_PB050_TRIPLE_PLAY.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
