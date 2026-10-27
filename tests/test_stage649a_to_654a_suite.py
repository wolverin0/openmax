#!/usr/bin/env python3
"""Consolidated pytest suite for Stages 649A..654A."""
from __future__ import annotations

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage654a_xtensa_vdev_pb060_and_ltu_12x_suite import (
    OUT_JSON,
    STAGE_DOCS,
    verify_stage654a_suite,
)


def test_stage649a_to_654a_consolidated_suite() -> None:
    rep = verify_stage654a_suite()
    assert OUT_JSON.exists()
    assert rep["stage"] == "654A"
    assert rep["status"] == "PASS"
    assert rep["live_devices_touched"] is False
    assert audit_stage_receipt_5pillars(rep)["compliant"] is True

    for st_id in ("649A", "650A", "651A", "652A", "653A"):
        assert rep["verified_stages"][st_id]["five_pillar_compliant"] is True
        assert rep["verified_stages"][st_id]["live_devices_touched"] is False

    assert len(rep["verified_docs"]) == len(STAGE_DOCS)
    inv = rep["cross_stage_invariants"]
    assert inv["stage650a_patched_firmware_images"] == 7
    assert inv["stage650a_triple_combo_verified"] is True
    assert inv["stage651a_ltu_builds_verified"] == 2
    assert inv["stage652a_xw_and_ac_modules_verified"] == 4
    assert inv["stage653a_triple_vs_stock_goodput_gain_mbps"] > 100.0
    assert inv["stage653a_triple_vs_stock_p99_reduction_pct"] > 40.0
