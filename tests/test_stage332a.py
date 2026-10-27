from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage332a_ltu_64cpe_ofdma_airtime_pareto() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage332a_ltu_64cpe_ofdma_airtime_pareto.json"
    doc_path = ROOT / "docs/STAGE332A_LTU_64CPE_OFDMA_AIRTIME_PARETO.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "332A"
    assert data["status"] == "CONFIRMED"
    assert data["sector_topology"]["total_cpes"] == 64

    champ = data["regimes_compared"]["LTU_64CPE_OFDMA_ATF_Champion"]
    fifo = data["regimes_compared"]["LTU_64CPE_Unweighted_Packet_FIFO"]
    openmax = data["regimes_compared"]["OpenMAX_WA_AC_64CPE_AQL_Reference"]

    assert champ["aggregate_goodput_mbps"] > fifo["aggregate_goodput_mbps"]
    assert champ["aggregate_goodput_mbps"] > openmax["aggregate_goodput_mbps"]
    assert champ["p99_latency_ms"] < fifo["p99_latency_ms"]
    assert champ["jain_airtime_fairness"] > 0.90

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
