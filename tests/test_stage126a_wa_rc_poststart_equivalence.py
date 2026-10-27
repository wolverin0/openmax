#!/usr/bin/env python3
"""Pytest verification suite for Stage 126A
(`T-S126A-WA-RC-POSTSTART-13-BRIDGE-EQUIVALENCE-AND-DEEP-AUTORESEARCH-VERIFIER`).
"""

from __future__ import annotations

import pytest

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage126a_wa_rc_poststart_equivalence import (
    BRIDGE_IMPLEMENTATION_EVIDENCE_RULES,
    OUT_RECEIPT_JSON,
    STAGE119A_JSON,
    UNIVERSAL_CHAMPION_SH,
    verify_stage126a_wa_rc_poststart_equivalence,
)


@pytest.fixture(scope="module")
def stage126a_receipt() -> dict:
    return verify_stage126a_wa_rc_poststart_equivalence()


def test_stage126a_safety_and_files_exist(stage126a_receipt: dict) -> None:
    assert STAGE119A_JSON.exists()
    assert UNIVERSAL_CHAMPION_SH.exists()
    assert OUT_RECEIPT_JSON.exists()
    assert stage126a_receipt["live_devices_touched"] is False
    assert stage126a_receipt["pbe5ac_241_242_touched"] is False
    assert stage126a_receipt["flash_writes"] == 0
    assert stage126a_receipt["claim_status"] == "CONFIRMED"


def test_stage126a_powerbeam_and_litebeam_board_parity(stage126a_receipt: dict) -> None:
    parity = stage126a_receipt["board_parity_summary"]
    pbe = parity["powerbeam_5ac_gen2"]
    lbe = parity["litebeam_5ac_gen2"]

    assert pbe["model_code"] == "PBE-5AC-Gen2"
    assert pbe["board_sysid_hex"] == "0xe3d6"
    assert pbe["openwrt_board_name"] == "ubnt,powerbeam-5ac-gen2"
    assert pbe["shared_platform_dtsi"] == "ar9342_ubnt_wa.dtsi"
    assert pbe["universal_champion_supported"] is True
    assert pbe["all_13_bridges_implemented"] is True

    assert lbe["model_code"] == "LBE-5AC-Gen2"
    assert "0xe3d8" in lbe["board_sysid_hex"]
    assert "0xe7f9" in lbe["board_sysid_hex"]
    assert lbe["openwrt_board_name"] == "ubnt,litebeam-5ac-gen2"
    assert lbe["shared_platform_dtsi"] == "ar9342_ubnt_wa.dtsi"
    assert lbe["universal_champion_supported"] is True
    assert lbe["all_13_bridges_implemented"] is True


def test_stage126a_all_13_bridges_implemented_and_verified(
    stage126a_receipt: dict,
) -> None:
    assert stage126a_receipt["total_bridges_verified"] == 13
    assert stage126a_receipt["all_13_bridges_verified"] is True

    matrix = stage126a_receipt["bridge_01_to_13_verification_matrix"]
    assert len(matrix) == 13
    by_id = {b["knob_group_id"]: b for b in matrix}
    assert set(by_id.keys()) == set(BRIDGE_IMPLEMENTATION_EVIDENCE_RULES.keys())

    for gid, row in by_id.items():
        assert row["status"] == "CONFIRMED", f"{gid} not CONFIRMED"
        assert row["powerbeam_5ac_gen2_0xe3d6_implemented"] is True
        assert row["litebeam_5ac_gen2_0xe3d8_0xe7f9_implemented"] is True
        assert len(row["airos8_tokens_verified"]) >= 1
        assert len(row["openwrt_tokens_verified"]) >= 1
        assert len(row["source_files_verified"]) >= 1


def test_stage126a_deep_autoresearch_counterbalanced_champions(
    stage126a_receipt: dict,
) -> None:
    ar = stage126a_receipt["deep_autoresearch_summary"]
    assert ar["total_candidates_evaluated"] == 10
    assert ar["protocol"] == "A1->B1->A2->B2"
    assert ar["watchdog_seconds"] == 45

    hyb = ar["hybrid_vht20_champion"]
    assert hyb["candidate_id"] == "HYB-02-AQL1500-3000-THR3000-Q1514-BI30-RTS2346-VHT20"
    assert hyb["goodput_delta_pct"] > 20.0
    assert hyb["p95_rtt_delta_pct"] < -50.0

    owrt = ar["full_openwrt_vht20_champion"]
    assert (
        owrt["candidate_id"]
        == "OWRT-02-WA-UNIVERSAL-CHAMPION-AQL1500-3000-THR5000-Q1514-BI30-VHT20"
    )
    assert owrt["goodput_delta_pct"] > 10.0
    assert owrt["p95_rtt_delta_pct"] < -50.0


def test_stage126a_five_pillar_gate_compliance(stage126a_receipt: dict) -> None:
    audit = audit_stage_receipt_5pillars(stage126a_receipt)
    assert audit["compliant"] is True
    assert stage126a_receipt["five_pillar_gate_audit"]["compliant"] is True
