from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH_JSON = ROOT / "artifacts" / "autoresearch" / "stage30a_closed_loop_m8_bench_20261025.json"
QUEUE_JSON = ROOT / "artifacts" / "autoresearch" / "discovery_to_research_queue.json"
DOC_MD = ROOT / "docs" / "STAGE30A_CLOSED_LOOP_M8_MULTI_CPE_BENCHMARK.md"


def test_stage30a_closed_loop_m8_bench_receipt_and_reactor_queue() -> None:
    assert BENCH_JSON.exists()
    assert QUEUE_JSON.exists()
    assert DOC_MD.exists()

    bench = json.loads(BENCH_JSON.read_text(encoding="utf-8"))
    assert bench["stage"] == "STAGE30A"
    assert bench["status"] == "COMPLETED_ON_PHYSICAL_BENCH"
    assert bench["final_ram_state"]["persistent_flash_writes"] is False

    rounds = bench["rounds"]
    for rid in ("S30A-R1", "S30A-R2", "S30A-R3", "S30A-R4"):
        assert rid in rounds
        r = rounds[rid]
        assert r["research_reactor_triggered"] is True
        assert r["decision"] == "RETAIN_CURRENT_CHAMPION"
        assert r["promoted"] is False
        assert set(r["phases"].keys()) == {"A1", "B1", "A2", "B2"}

    # S30A-R1: removing netdev_budget=600 cut p95 RTT by -9.442%
    assert rounds["S30A-R1"]["p95_rtt_delta_pct"] < -8.0
    # S30A-R2: AC_BE=1100/2000 cut 3-CPE sector p95 RTT by -5.793%
    assert rounds["S30A-R2"]["p95_rtt_delta_pct"] < -5.0
    # S30A-R3: restoring br0 txqueuelen=1000 kept goodput within 0.5%
    assert abs(rounds["S30A-R3"]["goodput_delta_pct"]) < 1.0
    # S30A-R4: Stage 28 Champion v7 achieved 53.319 ms sector p95 RTT with 0.0% loss across all 3 CPEs
    assert rounds["S30A-R4"]["arm_a_mean_p95_rtt_ms"] < 55.0

    queue = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
    round_ids = {e["round_id"] for e in queue["events"]}
    assert {"S30A-R1", "S30A-R2", "S30A-R3", "S30A-R4"}.issubset(round_ids)
