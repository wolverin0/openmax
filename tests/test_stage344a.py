from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage344a_ltu_sq_micro_ap_split_freq_pareto() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage344a_ltu_sq_micro_ap_split_freq_pareto.json"
    doc_path = ROOT / "docs/STAGE344A_LTU_SQ_MICRO_AP_SPLIT_FREQ_PARETO.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "344A"
    assert data["status"] == "CONFIRMED"

    champ = data["regimes_compared"]["LTU_SQ8_SplitFreq_AD9361_Champion"]
    sq_single = data["regimes_compared"]["LTU_SQ8_CoChannel_SingleFreq"]
    std64 = data["regimes_compared"]["LTU_Std64_CoChannel_Default"]

    assert champ["aggregate_goodput_mbps"] > sq_single["aggregate_goodput_mbps"]
    assert champ["aggregate_goodput_mbps"] > std64["aggregate_goodput_mbps"]
    assert champ["p99_latency_ms"] < std64["p99_latency_ms"]
    assert champ["ul_harq_retx_pct"] < std64["ul_harq_retx_pct"]

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
