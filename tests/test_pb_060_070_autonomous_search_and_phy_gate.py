#!/usr/bin/env python3
"""Unit tests for PB-060 Autonomous Search Pilot & PB-070 Custom-PHY Eligibility Gate."""

from __future__ import annotations

from controller.pb_060_070_autonomous_search_and_phy_gate import (
    SearchCandidateConfig,
    build_pb_060_070_pilot_report,
    deduplicate_candidates,
    evaluate_pb070_custom_phy_gate,
    validate_candidate_safety_envelope,
)


def test_pb_060_candidate_deduplication_and_safety_envelope() -> None:
    c1 = SearchCandidateConfig(
        candidate_id="C1",
        channel_width_mhz=10,
        tx_power_dbm=18,
        ldpc_enabled=True,
        stbc_enabled=True,
        sgi_enabled=False,
        rts_threshold_bytes=256,
        aql_be_limit_us=3000,
    )
    c2_dup = SearchCandidateConfig(
        candidate_id="C2_DUP",
        channel_width_mhz=10,
        tx_power_dbm=18,
        ldpc_enabled=True,
        stbc_enabled=True,
        sgi_enabled=False,
        rts_threshold_bytes=256,
        aql_be_limit_us=3000,
    )
    c3_illegal_eirp = SearchCandidateConfig(
        candidate_id="C3_ILLEGAL",
        channel_width_mhz=20,
        tx_power_dbm=31,
        ldpc_enabled=True,
        stbc_enabled=False,
        sgi_enabled=True,
        rts_threshold_bytes=256,
        aql_be_limit_us=3000,
    )

    unique, skipped = deduplicate_candidates([c1, c2_dup, c3_illegal_eirp])
    assert len(unique) == 2
    assert skipped == ["C2_DUP"]

    ok1, _ = validate_candidate_safety_envelope(c1)
    assert ok1 is True
    ok3, reason3 = validate_candidate_safety_envelope(c3_illegal_eirp)
    assert ok3 is False
    assert "tx_power_dbm=31" in reason3


def test_pb_060_pilot_holm_sidak_and_holdout_replication() -> None:
    report = build_pb_060_070_pilot_report()
    assert report["automatic_execution_allowed"] is False

    pilot = report["pb060_autonomous_search_pilot"]
    assert pilot["campaign_passed"] is False
    assert pilot['diagnostic_passed'] is True
    assert pilot['evidence_state'] == 'SYNTHETIC'
    assert pilot["negative_control_false_positives"] == 0
    assert pilot["skipped_duplicate_candidate_ids"] == ["CAND_02_DUPLICATE_OF_CAND_01"]
    assert len(pilot["rejected_safety_envelope_candidates"]) == 1
    assert pilot["rejected_safety_envelope_candidates"][0]["candidate_id"] == "CAND_04_ILLEGAL_TX_POWER_30DBM"
    assert pilot["promoted_candidate_ids"] == []
    assert pilot['synthetic_pass_candidate_ids'] == ["CAND_01_10MHZ_LDPC_STBC_AQL3000"]

    by_id = {c["candidate_id"]: c for c in pilot["candidate_evaluations"]}
    assert by_id["CAND_00_NEG_CTRL_AA"]["final_verdict"] == 'VALID_SYNTHETIC_NULL'
    assert by_id["CAND_01_10MHZ_LDPC_STBC_AQL3000"]["final_verdict"] == "SYNTHETIC_PASS"
    assert by_id["CAND_03_20MHZ_SGI_NO_HOLDOUT"]["final_verdict"] == "REJECT_FAILED_HOLDOUT_REPLICATION"


def test_pb_070_custom_phy_gate_locks_when_any_condition_unproven() -> None:
    saved = build_pb_060_070_pilot_report()
    pb070 = saved["pb070_custom_phy_eligibility_verdict"]
    assert pb070["verdict"] == "LOCKED_CONCENTRATE_ON_MAC_AND_POLICY"
    assert pb070["custom_phy_waveform_claims_allowed"] is False

    # Verify that even 2 of 3 conditions remains locked
    partial = evaluate_pb070_custom_phy_gate(
        condition_1_mapper_or_raw_iq_proven=False,
        condition_2_modified_target_execution_proven=True,
        condition_3_external_vsa_sdr_waveform_proven=True,
    )
    assert partial["verdict"] == "LOCKED_CONCENTRATE_ON_MAC_AND_POLICY"
    assert partial["custom_phy_waveform_claims_allowed"] is False

    # Verify that all 3 conditions proven unlocks custom-PHY eligibility
    unlocked = evaluate_pb070_custom_phy_gate(
        condition_1_mapper_or_raw_iq_proven=True,
        condition_2_modified_target_execution_proven=True,
        condition_3_external_vsa_sdr_waveform_proven=True,
    )
    assert unlocked["verdict"] == "ELIGIBLE_FOR_CUSTOM_PHY_EXPERIMENTS"
    assert unlocked["custom_phy_waveform_claims_allowed"] is True
