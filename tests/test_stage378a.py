from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage378a_ltu_subband_puncturing_pareto() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage378a_ltu_subband_puncturing_pareto.json"
    doc_path = ROOT / "docs/STAGE378A_LTU_SUBBAND_PUNCTURING_PARETO.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "378A"
    assert data["status"] == "CONFIRMED"

    champ = data["regimes_compared"]["LTU_8Subband_Adaptive_Puncturing_Champion"]
    unpunc = data["regimes_compared"]["LTU_8Subband_Unpunctured_LowSubband"]
    wide = data["regimes_compared"]["Wideband_FullChannel_StepDown_80211ac_Style"]

    assert champ["aggregate_goodput_mbps"] > wide["aggregate_goodput_mbps"] * 1.8
    assert champ["p99_latency_ms"] < unpunc["p99_latency_ms"]
    assert champ["p99_latency_ms"] < wide["p99_latency_ms"]
    assert champ["ldpc_block_error_pct"] < unpunc["ldpc_block_error_pct"]

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
