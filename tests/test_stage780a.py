"""Pytest verification for Stage 780A (NSGA-III Pareto of QCA988x ANI Immunity & AF-LTU IRQ 52 / NAPI)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "artifacts" / "autoresearch" / "stage780a_nsga3_pareto_ani_immunity_and_irq52_napi.json"
DOC = ROOT / "docs" / "STAGE780A_NSGA3_PARETO_ANI_IMMUNITY_AND_IRQ52_NAPI.md"


def test_stage780a_nsga3_ani_and_irq52_napi() -> None:
    assert RECEIPT.exists(), f"Missing {RECEIPT}"
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-780A"
    assert data["status"] == "CONFIRMED"
    assert data["nsga3_config"]["n_objectives"] == 4
    knee = data["selected_champion_knee"]
    base = data["baseline_unoptimized"]
    assert knee["ani_ofdm_level"] in (2, 3)
    assert knee["ltu_irq52_affinity_mode"] == "cpu1_dedicated_mask2"
    assert knee["netdev_budget"] == 480
    assert knee["dev_weight"] == 48
    assert knee["goodput_mbps"] > base["goodput_mbps"]
    assert knee["p95_rtt_ms"] < base["p95_rtt_ms"]
    assert knee["irq_cpu0_contention_pct"] < 3.0
    assert knee["weak_drop_or_false_cca_pct"] < 1.0

    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
