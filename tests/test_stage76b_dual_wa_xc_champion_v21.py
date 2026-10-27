"""Stage 76B Tests: Dual WA + XC S70C Offload, NAPI CPU-Class Scaling & BusyBox seq Warmup (`tests/test_stage76b_dual_wa_xc_champion_v21.py`)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage76b_dual_wa_xc_offload_champion_v21 import (
    OUT_JSON,
    STAGE70C_XC_COMMANDS,
    STAGE76B_WA_CANDIDATE_COMMANDS_R1,
    STAGE76B_WA_CANDIDATE_COMMANDS_R5,
    STAGE76B_WA_CANDIDATE_COMMANDS_R6,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT_DIR / "docs" / "STAGE76B_DUAL_WA_AND_XC_OFFLOAD_CHAMPION_V21_BENCHMARK.md"


def test_stage76b_artifact_and_6_counterbalanced_rounds() -> None:
    """Verify Stage 76B receipt exists and contains all 6 counterbalanced A1->B1->A2->B2 rounds (24 windows)."""
    assert OUT_JSON.exists()
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "76B"
    assert data["task_id"] == "T-S76B-DUAL-WA-AND-XC-S70C-OFFLOAD-CHAMPION-V21-BENCH"
    assert data["status"] == "CONFIRMED"

    inv = data["safety_invariants"]
    assert inv["flash_writes"] == 0
    assert inv["auto_rollback_watchdog_timeout_s"] == 45
    assert inv["ar9342_64mb_oom_score_adj"] == -900
    assert inv["ar9342_64mb_fq_memory_limit_bytes"] == 4194304
    assert inv["direct_sysfs_tx_queue_len_only"] is True
    assert inv["uph_16int_vector_ff_mcast_written_last"] is True

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert len(rounds) == 6
    for rid, r in rounds.items():
        for phase in ("A1", "B1", "A2", "B2"):
            assert phase in r["phases"], f"{rid} missing phase {phase}"

    # S76B-R1: WA budget=800 cuts p50 RTT -11.88%, p95 RTT -4.575% (<80 ms), p99 RTT -13.75%, IPTV jitter -15.47%, Pareto +1.06%
    r1 = rounds["S76B-R1-DUAL-WA-XC-OFFLOAD-BUDGET800-TSQ98304"]
    assert r1["p95_rtt_delta_pct"] == -4.575
    assert r1["iptv_jitter_delta_pct"] == -15.47
    assert r1["pareto_score_delta_pct"] > 1.0

    # S76B-R5 & S76B-R6: Restoring WA budget=600 on 535 MHz AR9342 turns goodput positive (+1.292% and +1.498%)
    r5 = rounds["S76B-R5-WARMED-WA-BUDGET600-TSQ65536-LOWAT6144-XC-S70C-CHAMPION-V21"]
    assert r5["goodput_delta_pct"] == 1.292
    assert r5["iptv_jitter_delta_pct"] == -25.348

    r6 = rounds["S76B-R6-WARMED-WA-ACBE-750-1350-THR3500-BUDGET600-XC-S70C-CHAMPION-V21"]
    assert r6["goodput_delta_pct"] == 1.498
    assert r6["voip_jitter_delta_pct"] == -14.08


def test_stage76b_commands_and_doc_invariants() -> None:
    """Verify Stage 76B command lists and markdown report invariants (< 220 lines, 1 doc-head)."""
    for cmd_list in (
        STAGE70C_XC_COMMANDS,
        STAGE76B_WA_CANDIDATE_COMMANDS_R1,
        STAGE76B_WA_CANDIDATE_COMMANDS_R5,
        STAGE76B_WA_CANDIDATE_COMMANDS_R6,
    ):
        joined = "\n".join(cmd_list)
        assert "ip link set" not in joined
        assert "ff_mcast_airtime_limit" in cmd_list[-1]

    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"Doc has {len(lines)} lines (must be < 220)"
    assert text.count("<!-- doc-head:") == 1
    for token in ("FMX-DISC-21", "FMX-DISC-22", "S76B-R1", "S76B-R5", "S76B-R6", "STAGE72A_CHAMPION_V20"):
        assert token in text
