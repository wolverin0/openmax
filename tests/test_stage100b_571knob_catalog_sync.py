#!/usr/bin/env python3
"""
Tests for Stage 100B (`T-S100B-571KNOB-CATALOG-SYNC-STAGE93B-TO-99D`).
"""

from __future__ import annotations

import json

from tools.research.run_stage100b_571knob_catalog_sync import (
    DEFAULT_OUT_JSON,
    run_stage100b_571knob_catalog_sync,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


def test_stage100b_571knob_catalog_sync() -> None:
    receipt = run_stage100b_571knob_catalog_sync()
    assert DEFAULT_OUT_JSON.exists()
    assert receipt["stage"] == "100B"
    assert receipt["status"] == "CONFIRMED"

    integrity = receipt["catalog_integrity"]
    assert integrity["immutable_verified"] is True
    assert integrity["total_catalog_knobs"] == 571

    groups = {g["knob_key"]: g for g in receipt["stage_93b_to_99d_knob_evaluations"]}
    for expected_key in (
        "ath_pktlog_module_unload",
        "vow_extstats_vs_enable_ol_stats",
        "cwmenable_chwidth_vht_op_ie_autofollow",
        "doth_and_3int_doth_chanswitch",
        "2xc_ac_minfree_and_min_buf_resv",
        "ltu_rxgaintbl_board_ssid_0xae08",
        "ltu_eab_txcmd_dump_and_freq_analyzer_isr_giveup",
    ):
        assert expected_key in groups
        assert groups[expected_key]["epistemic_status"] == "CONFIRMED"


def test_stage100b_5pillar_gate_compliance() -> None:
    loaded = json.loads(DEFAULT_OUT_JSON.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True, f"5-pillar gate failed: {audit}"
