from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage400a_ltu_gps_reuse1_tdd_pareto() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage400a_ltu_gps_reuse1_tdd_pareto.json"
    doc_path = ROOT / "docs/STAGE400A_LTU_GPS_REUSE1_TDD_PARETO.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "400A"
    assert data["status"] == "CONFIRMED"

    champ = data["regimes_compared"]["LTU_GPS_Locked_2ms_SQ_Reuse1_Champion"]
    std64 = data["regimes_compared"]["LTU_GPS_Locked_Std64_Reuse1"]
    unsync = data["regimes_compared"]["LTU_Unsynchronized_FreeRunning_Reuse1"]

    assert champ["dual_sector_reuse1_goodput_mbps"] > std64["dual_sector_reuse1_goodput_mbps"]
    assert champ["dual_sector_reuse1_goodput_mbps"] > unsync["dual_sector_reuse1_goodput_mbps"] * 2.5
    assert champ["p99_latency_ms"] < unsync["p99_latency_ms"]
    assert champ["tdd_cross_slot_retx_pct"] < unsync["tdd_cross_slot_retx_pct"]

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
