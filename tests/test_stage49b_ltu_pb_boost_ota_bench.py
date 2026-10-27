#!/usr/bin/env python3
"""
Unit tests for Stage 49B — LTU Over-The-Air pb_boost, 2.0ms Superframe / frame_len Bug Discovery,
and Fail-Safe EVM-Matched Auto-Rate Ceiling Benchmark.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage49b_ltu_pb_boost_and_frame_len_ota_bench import (
    OUT_JSON_PATH,
    PROFILES,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "STAGE49B_LTU_PB_BOOST_AND_FRAME_LEN_OTA_BENCHMARK.md"


def test_stage49b_hardware_discoveries_and_profiles() -> None:
    """Verify Stage 49B artifact documents the ame_core.ko sysfs frame_len bug and autoMcsCeiling map."""
    assert OUT_JSON_PATH.exists(), f"Missing Stage 49B artifact: {OUT_JSON_PATH}"
    data = json.loads(OUT_JSON_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 49B"
    assert data["task_id"] == "T-S49B-LTU-40MHZ-AND-PB-BOOST-OTA-DISTANCE-BENCH"

    hw = data["hardware_and_driver_discoveries"]
    assert hw["ame_core_sysfs_frame_len_bug_confirmed"] is True
    assert "duty_cycle:5000" in hw["bandwidthConfig_after_echo_5000_frame_len"]
    assert "duty_cycle:750" in hw["bandwidthConfig_after_restore_duty_cycle_750"]
    assert hw["verified_autoMcsCeiling_map"]["15"] == "64qam (6x)"
    assert hw["verified_autoMcsCeiling_map"]["23"] == "1024qam (10x)"


def test_stage49b_counterbalanced_trials_and_doc() -> None:
    """Verify Stage 49B 9 counterbalanced trials, OTA health checks, and documentation completeness."""
    assert OUT_JSON_PATH.exists(), f"Missing Stage 49B artifact: {OUT_JSON_PATH}"
    data = json.loads(OUT_JSON_PATH.read_text(encoding="utf-8"))

    assert len(data["trials"]) == 9
    for trial in data["trials"]:
        assert trial["apply_meta"]["ota_verified"] is True

    for prof in PROFILES:
        s = data["summary_by_profile"][prof]
        assert s["n_trials"] == 3
        assert s["mean_aggregate_dl_mbps"] > 20.0
        assert s["mean_loaded_ping_p50_ms"] < 15.0

    post = data["ota_link_verification_post_bench"]
    assert "AP-PTMP(Run)" in post["ltu1_common_info"]
    assert "Stations count: 1" in post["ltu1_common_info"]

    assert DOC_PATH.exists(), f"Missing Stage 49B report: {DOC_PATH}"
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    assert "S49B-R0-STAGE48B-BASELINE" in doc_text
    assert "S49B-R1-PB-BOOST-ON-2MS" in doc_text
    assert "S49B-R2-PB-BOOST-AND-EVM-MCS-CEILING" in doc_text
    assert "duty_cycle:5000" in doc_text or "duty_cycle" in doc_text
