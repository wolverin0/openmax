#!/usr/bin/env python3
"""Tests for Stage 651A: LTU 4096-QAM (12X) LDPC & Phase-Noise Tracker Dissection."""
from __future__ import annotations

from pathlib import Path

from tools.re.dissect_stage651a_ltu_4096qam_ldpc_and_phase_noise_tracker_re import (
    OUT_JSON,
    ROOT,
    build_stage651a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


def test_stage651a_ltu_4096qam_ldpc_and_phase_noise_tracker_re() -> None:
    rep = build_stage651a_report()
    assert OUT_JSON.exists()
    assert rep["stage"] == "651A"
    assert rep["status"] == "PASS"
    assert rep["claim_label"] == "CONFIRMED"
    assert rep["live_devices_touched"] is False
    assert audit_stage_receipt_5pillars(rep)["compliant"] is True

    builds = rep["builds_dissected"]
    assert len(builds) == 2
    for b in builds:
        assert b["rodata_mcs_thresholds"]["startThrd_4096"] == 97
        assert b["rodata_mcs_thresholds"]["stayThrd_4096"] == 90
        assert b["rodata_mcs_thresholds"]["mcsUpThrd_1024"] == 93
        assert b["rodata_mcs_thresholds"]["mcsUpThrd_256"] == 96
        assert b["data_mcs_and_cfo_thresholds"]["cont1024Threshold"] == 1
        assert b["data_mcs_and_cfo_thresholds"]["pb_cfo_apply"] == 1
        assert b["data_mcs_and_cfo_thresholds"]["cfo_pass_threshold"] == 400
        assert (
            b["rate_tables_rodata"]["autoMcsOthersTbl"]["includes_4096qam_12x_0x011f"]
            is True
        )
        assert (
            b["super4096_rfic_linearity"]["bbp_rf_get_super4096"]["rfic_chain0_reg"]
            == "0x0351"
        )
        assert (
            b["super4096_rfic_linearity"]["bbp_rf_get_super4096"]["rfic_chain1_reg"]
            == "0x03d1"
        )
        assert (
            "0x00048000"
            in b["ldpc_iteration_control"]["bbp_mrx_util_set_rxTopB_ldpcIteration"][
                "mmio_base_offset"
            ]
        )

    doc_path = (
        ROOT / "docs" / "STAGE651A_LTU_4096QAM_LDPC_AND_PHASE_NOISE_TRACKER_RE.md"
    )
    assert doc_path.exists()
    lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
