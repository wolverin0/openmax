from __future__ import annotations

import json
from pathlib import Path

from controller.multiradio_golden_profile_applicator import (
    GOLDEN_PROFILES,
    export_champion_ledger,
    validate_profile_safety,
)
from controller.stage20_closed_loop_champion_switcher import IncrementalChampionPromoter

ROOT = Path(__file__).resolve().parents[1]
REACTOR_RECEIPT = ROOT / "artifacts" / "autoresearch" / "stage28_closed_loop_reactor_receipt_20261025.json"
QUEUE_JSON = ROOT / "artifacts" / "autoresearch" / "discovery_to_research_queue.json"
BENCH_JSON = ROOT / "artifacts" / "autoresearch" / "stage28_closed_loop_reactor_m6_m7_bench_20261025.json"
CLAIMS_JSON = ROOT / "artifacts" / "hyperresearch_vault" / "claims" / "scholar_jev_verified_claims_stage28.json"


def test_stage28_closed_loop_reactor_and_jev_claims_verified() -> None:
    assert REACTOR_RECEIPT.exists()
    assert QUEUE_JSON.exists()
    assert CLAIMS_JSON.exists()

    reactor = json.loads(REACTOR_RECEIPT.read_text(encoding="utf-8"))
    assert reactor["stage"] == "STAGE28"
    papers = reactor["scholar_and_hyperresearch_ingestion"]["ingested_followup_papers"]
    assert len(papers) == 2
    paper_ids = {p["paper_id"]: p for p in papers}
    assert "2211.03471v1" in paper_ids
    assert paper_ids["2211.03471v1"]["verification_probability"] == 0.97
    assert "0806.4695v1" in paper_ids
    assert paper_ids["0806.4695v1"]["verification_probability"] == 0.77

    queue = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
    assert queue["events_count"] >= 7
    round_ids = {e["round_id"] for e in queue["events"]}
    assert {"S24F-R1", "S25-R1", "S25-R2", "S27-R2AC-R1", "S27-R2AC-R2", "S28-R1", "S28-R2"}.issubset(round_ids)


def test_stage28_bench_and_champion_v7_promotion() -> None:
    assert BENCH_JSON.exists()
    bench = json.loads(BENCH_JSON.read_text(encoding="utf-8"))
    assert bench["status"] == "COMPLETED_ON_PHYSICAL_BENCH"
    assert bench["final_ram_state"]["persistent_flash_writes"] is False

    r1 = bench["rounds"]["S28-R1"]
    assert r1["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r1["promoted"] is True
    assert r1["research_reactor_triggered"] is True
    assert r1["p95_rtt_delta_pct"] < -8.0
    assert r1["goodput_delta_pct"] > 0.0

    r2 = bench["rounds"]["S28-R2"]
    assert r2["decision"] == "RETAIN_CURRENT_CHAMPION"
    assert r2["promoted"] is False
    assert r2["research_reactor_triggered"] is True

    r3 = bench["rounds"]["S28-R3"]
    assert r3["goodput_delta_pct"] > 5.0
    assert r3["decision"] == "RETAIN_CURRENT_CHAMPION"
    assert r3["research_reactor_triggered"] is True

    # Verify Champion v7 promotion in Golden Profiles & Ledger
    for pid in ("openwrt_lap120_ptp_1cpe_champion", "openwrt_lap120_ptmp_multicpe_champion"):
        prof = GOLDEN_PROFILES[pid]
        validate_profile_safety(prof)
        assert "S28-R1" in prof.validated_rounds
        joined = " && ".join(prof.apply_commands)
        assert "quantum 3028" in joined
        assert "br-lan txqueuelen 256" in joined
        assert "tcp_dsack=1" in joined

    ledger = export_champion_ledger()
    assert "S28-R1" in ledger["profiles"]["openwrt_lap120_ptp_1cpe_champion"]["validated_rounds"]

    # Verify IncrementalChampionPromoter auto-triggers research reactor
    res = IncrementalChampionPromoter.evaluate_candidate(
        profile_id="openwrt_lap120_ptp_1cpe_champion",
        round_id="S28-UNIT-TEST",
        candidate_apply_commands=GOLDEN_PROFILES["openwrt_lap120_ptp_1cpe_champion"].apply_commands,
        gp_champion_mbps=39.20,
        p95_champion_ms=42.72,
        gp_candidate_mbps=39.44,
        p95_candidate_ms=38.96,
        auto_trigger_research=True,
    )
    assert res["decision"] == "PROMOTE_NEW_CHAMPION"
    assert res["research_reactor_triggered"] is True
    assert len(res["followup_scholar_queries"]) >= 1
