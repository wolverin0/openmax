#!/usr/bin/env python3
"""
Unit tests for Stage 41C — Closed-Loop Research Reactor Ingestion of
Stage 34A (M15), Stage 35A (M15_5GHz Champion v9), and Stage 36A (S36A-R1 vs S36A-R2 Champion v10)
and synthesis of next-wave mechanisms M18..M21.
Task ID: T-S41C-GEM2-CLOSED-LOOP-REACTOR-STAGE35A-36A-CHAMPION-V10-AND-IPTV-INGESTION
"""

from __future__ import annotations

import json
from pathlib import Path

from controller.multiradio_golden_profile_applicator import FORBIDDEN_TOKENS
from tools.research.closed_loop_research_reactor import (
    DISCOVERY_QUEUE_JSON,
    STAGE41C_REACTOR_V10_RECEIPT_JSON,
    VAULT_ROOT,
    ingest_stage34a_35a_36a_champion_v10_and_synthesize_m18_m21,
)


def test_stage41c_ingests_s34a_s35a_s36a_and_synthesizes_m18_to_m21(tmp_path: Path) -> None:
    out_file = tmp_path / "stage41c_test.json"
    receipt = ingest_stage34a_35a_36a_champion_v10_and_synthesize_m18_m21(out_file)
    assert out_file.exists()
    assert STAGE41C_REACTOR_V10_RECEIPT_JSON.exists()
    assert receipt["stage"] == "41C"

    events_by_round = {e["round_id"]: e for e in receipt["ingested_reactor_events"]}
    assert set(events_by_round.keys()) == {"S34A-R1", "S35A-R1", "S36A-R1", "S36A-R2"}

    # Verify S34A-R1 (M15 2.4 GHz) and S35A-R1 (M15_5GHz Champion v9)
    assert events_by_round["S34A-R1"]["empirical_status"] == "HW_CONFIRMED"
    assert events_by_round["S34A-R1"]["gp_delta_pct"] == 7.244
    assert events_by_round["S35A-R1"]["empirical_status"] == "HW_CONFIRMED"
    assert events_by_round["S35A-R1"]["p95_delta_pct"] == -15.121

    # Verify S36A-R1 (REFUTED AC_BE=1000/2000) vs S36A-R2 (CONFIRMED Champion v10 direct mac80211 aqm)
    assert events_by_round["S36A-R1"]["empirical_status"] == "HW_REFUTED_OR_BOUNDED"
    assert events_by_round["S36A-R1"]["gp_delta_pct"] == -6.225
    assert events_by_round["S36A-R2"]["empirical_status"] == "HW_CONFIRMED"
    assert events_by_round["S36A-R2"]["gp_delta_pct"] == 2.513
    assert events_by_round["S36A-R2"]["p95_delta_pct"] == -3.375

    # Verify M18..M21 next-wave candidate synthesis
    wave = receipt["next_wave_mechanisms_m18_to_m21"]
    mids = [m["mechanism_id"] for m in wave]
    assert mids == ["M18", "M19", "M20", "M21"]

    by_mid = {m["mechanism_id"]: m for m in wave}
    assert any("fq_limit 2048" in c for c in by_mid["M18"]["candidate_delta_commands"])
    assert any("ff_mcast_airtime_limit" in c for c in by_mid["M19"]["candidate_delta_commands"])
    assert any("multicast_fast_leave" in c for c in by_mid["M20"]["candidate_delta_commands"])
    assert any("maxrate 3500kbit" in c for c in by_mid["M21"]["candidate_delta_commands"])

    for m in wave:
        for cmd in m["candidate_delta_commands"]:
            for token in FORBIDDEN_TOKENS:
                assert token not in cmd


def test_discovery_queue_and_vault_feedback_notes_created() -> None:
    queue = json.loads(DISCOVERY_QUEUE_JSON.read_text(encoding="utf-8"))
    round_ids = {e["round_id"] for e in queue["events"]}
    assert {"S34A-R1", "S35A-R1", "S36A-R1", "S36A-R2"}.issubset(round_ids)

    feedback_dir = VAULT_ROOT / "notes" / "empirical_feedback"
    for rid in ("S34A-R1", "S35A-R1", "S36A-R1", "S36A-R2"):
        note_path = feedback_dir / f"empirical_feedback_{rid}.md"
        assert note_path.exists()
        content = note_path.read_text(encoding="utf-8")
        assert rid in content
