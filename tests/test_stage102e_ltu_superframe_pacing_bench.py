"""Verification tests for Stage 102E LTU-Lite #1 500 Hz Superframe Tail Guard & Burst Pacing benchmark."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "artifacts" / "autoresearch" / "stage102e_ltu_superframe_pacing_bench.json"
DOC_PATH = ROOT / "docs" / "STAGE102E_LTU_SUPERFRAME_PACING_BENCH.md"
SCRIPT_PATH = ROOT / "tools" / "benchmarks" / "run_stage102e_ltu_superframe_pacing_bench.py"


def test_stage102e_files_exist_and_doc_budget() -> None:
    assert SCRIPT_PATH.exists(), f"Missing script {SCRIPT_PATH}"
    assert ARTIFACT_PATH.exists(), f"Missing artifact {ARTIFACT_PATH}"
    assert DOC_PATH.exists(), f"Missing doc {DOC_PATH}"

    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 180, f"Doc exceeds 180 lines ({len(lines)})"
    assert lines[0].startswith("<!-- doc-head:"), "Doc must start with <!-- doc-head: -->"


def test_stage102e_counterbalanced_trials_and_zero_giveups() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "102E"
    assert data["status"] == "CONFIRMED"
    assert str(data.get("pillar_e_memory_master_claim_id", "")).startswith("mm-")

    trials = data["counterbalanced_trials"]
    assert len(trials) == 4
    expected = [
        "S102E-ARM-A-UNPACED-SUPERFRAME-BASELINE",
        "S102E-ARM-B-500HZ-SUPERFRAME-TAIL-GUARD-AND-BURST-PACING",
        "S102E-ARM-A-UNPACED-SUPERFRAME-BASELINE",
        "S102E-ARM-B-500HZ-SUPERFRAME-TAIL-GUARD-AND-BURST-PACING",
    ]
    assert [t["arm_id"] for t in trials] == expected

    arm_a = data["arm_summaries"]["S102E-ARM-A-UNPACED-SUPERFRAME-BASELINE"]
    arm_b = data["arm_summaries"]["S102E-ARM-B-500HZ-SUPERFRAME-TAIL-GUARD-AND-BURST-PACING"]

    assert arm_b["scheduler_giveup_max"] == 0
    assert arm_b["symbol_giveup_max"] == 0
    assert arm_b["soc_bulk_tcp_median_mbps"] >= arm_a["soc_bulk_tcp_median_mbps"]
    assert arm_b["irq52_mrx_cpu0_total"] > 4000
    assert arm_b["irq53_mtx_cpu0_total"] > 4000
    assert arm_b["irq63_gmac0_cpu1_total"] > 500
