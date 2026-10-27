#!/usr/bin/env python3
"""
Tests for Stage 120A — PowerBeam 5AC Gen2 (0xe3d6) & LiteBeam 5AC Gen2 (0xe3d8/0xe7f9)
Exhaustive Autoresearch Harness & Universal WA Champion (99-fmx-wa-universal-champion).
"""

from __future__ import annotations

import json
from pathlib import Path

from orchestration.autoresearch.fmx_pbe5ac_deep_autoresearch_runner import (
    build_exhaustive_sweep_grid,
    run_stage120a_deep_sweep,
    verify_universal_wa_script,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_JSON = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage120a_pbe5ac_deep_autoresearch_harness_receipt.json"
)
UNIVERSAL_SCRIPT = (
    REPO_ROOT
    / "firmware"
    / "openwrt"
    / "pbe5ac_gen2_ptp_kit"
    / "99-fmx-wa-universal-champion"
)


def test_stage120a_receipt_passes_5pillars() -> None:
    assert RECEIPT_JSON.exists(), f"Missing {RECEIPT_JSON}"
    receipt = json.loads(RECEIPT_JSON.read_text(encoding="utf-8"))
    assert receipt["stage"] == "120A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["live_radios_241_242_touched"] is False

    audit = audit_stage_receipt_5pillars(receipt)
    assert audit["compliant"], f"5-Pillar gate failed: {audit}"
    assert str(receipt["pillar_e_memory_master_claim_id"]).startswith("mm-")


def test_stage120a_universal_wa_champion_script() -> None:
    assert UNIVERSAL_SCRIPT.exists(), f"Missing {UNIVERSAL_SCRIPT}"
    audit = verify_universal_wa_script()
    assert audit["all_checks_passed"] is True
    for k, v in audit["checks"].items():
        assert v is True, f"Check failed: {k}"


def test_stage120a_exhaustive_grid_and_counterbalanced_sweep() -> None:
    grid = build_exhaustive_sweep_grid()
    assert len(grid) == 10
    modes = {c.mode for c in grid}
    assert modes == {
        "HYBRID_OPENWRT_AP_AIROS8_STA",
        "FULL_OPENWRT_AP_OPENWRT_STA",
    }

    # Verify OpenWrt and airOS 8 parameter coverage
    aql_limits = {c.aql_txq_limit_be for c in grid}
    assert (1500, 3000) in aql_limits
    assert (2000, 4000) in aql_limits
    assert (3000, 6000) in aql_limits

    htmodes = {c.htmode for c in grid}
    assert htmodes == {"VHT20", "VHT40", "VHT80"}

    beacons = {c.beacon_int for c in grid}
    assert beacons == {30, 100}

    rts_vals = {c.rts for c in grid}
    assert rts_vals == {"off", "2346"}

    receipt = run_stage120a_deep_sweep()
    champions = receipt["selected_champions"]
    assert champions["hybrid_vht20_champion"]["goodput_delta_pct"] > 20.0
    assert champions["hybrid_vht20_champion"]["p95_rtt_delta_pct"] < -50.0
    assert champions["full_openwrt_vht20_champion"]["goodput_delta_pct"] > 10.0
    assert champions["full_openwrt_vht20_champion"]["p95_rtt_delta_pct"] < -50.0
