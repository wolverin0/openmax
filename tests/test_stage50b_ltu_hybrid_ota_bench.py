#!/usr/bin/env python3
"""
Unit tests for Stage 50B — LTU Hybrid SWQ/FPGA Register Suite + Adaptive MCS Ceiling
+ Bottleneck-Matched 2-Tier HTB Over-The-Air Benchmark.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage50b_ltu_hybrid_swq_and_mcs_ceiling_ota_bench import (
    OUT_JSON_PATH,
    PROFILES,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "STAGE50B_LTU_HYBRID_SWQ_AND_MCS_CEILING_OTA_BENCHMARK.md"


def test_stage50b_flash_persistence_and_profiles() -> None:
    """Verify Stage 50B artifact includes dual-partition flash persistence on both LTU1 and remote LTU2."""
    assert OUT_JSON_PATH.exists(), f"Missing Stage 50B artifact: {OUT_JSON_PATH}"
    data = json.loads(OUT_JSON_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 50B"
    assert (
        data["task_id"]
        == "T-S50B-LTU-HYBRID-S49B-R1-R2-ADAPTIVE-MCS-CEILING-AND-DUTY-CYCLE-OTA-BENCH"
    )
    assert data["winning_profile"] in (
        "S50B-R1-HYBRID-AUTOMCS-19-256QAM-8X",
        "S50B-R2-HYBRID-AUTOMCS-15-64QAM-6X-SWQ2",
    )

    fp = data["flash_persistence_receipt"]
    assert fp["ltu1_boca5_cfgmtd_rc"] == 0
    assert "[%100]" in fp["ltu1_boca5_cfgmtd_out"]
    assert fp["ltu2_ota_cfgmtd_rc"] == 0
    assert "[%100]" in fp["ltu2_ota_cfgmtd_out"]


def test_stage50b_counterbalanced_trials_and_doc() -> None:
    """Verify Stage 50B 9 counterbalanced trials, OTA health checks, and documentation completeness."""
    assert OUT_JSON_PATH.exists(), f"Missing Stage 50B artifact: {OUT_JSON_PATH}"
    data = json.loads(OUT_JSON_PATH.read_text(encoding="utf-8"))

    assert len(data["trials"]) == 9
    for trial in data["trials"]:
        assert trial["apply_meta"]["ota_verified"] is True
        assert trial["apply_meta"]["cpe_watchdog_disarmed_after_verify"] is True

    for prof in PROFILES:
        s = data["summary_by_profile"][prof]
        assert s["n_trials"] == 3
        assert s["mean_aggregate_dl_mbps"] > 18.0
        assert s["mean_loaded_ping_p50_ms"] < 15.0

    post = data["ota_link_verification_post_bench"]
    assert "AP-PTMP(Run)" in post["ltu1_common_info"]
    assert "Stations count: 1" in post["ltu1_common_info"]

    assert DOC_PATH.exists(), f"Missing Stage 50B report: {DOC_PATH}"
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    assert "S50B-R0-STAGE49B-BASELINE" in doc_text
    assert "S50B-R1-HYBRID-AUTOMCS-19-256QAM-8X" in doc_text
    assert "S50B-R2-HYBRID-AUTOMCS-15-64QAM-6X-SWQ2" in doc_text
