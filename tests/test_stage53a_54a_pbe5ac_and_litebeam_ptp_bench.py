#!/usr/bin/env python3
"""
Unit tests for Stage 53A (PowerBeam 5AC Gen2 PtP OTA Autoresearch Benchmark)
and Stage 54A (Cross-Node .251 -> .241 -> .242 PtP Autoresearch Benchmark).
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage53a_pbe5ac_ptp_ota_autoresearch_bench import (
    OUT_JSON_PATH as OUT_S53A_JSON,
    ROUND_TREATMENTS as ROUNDS_S53A,
)
from tools.bench.run_stage54a_litebeam_and_pbe5ac_ptp_autoresearch import (
    OUT_JSON_PATH as OUT_S54A_JSON,
    ROUND_TREATMENTS_S54A as ROUNDS_S54A,
)
from tools.bench.run_stage56a_ptp_pbe5ac_and_litebeam_golden_stack_bench import (
    OUT_JSON_PATH as OUT_S56A_JSON,
    ROUND_TREATMENTS_S56A as ROUNDS_S56A,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_S53A = REPO_ROOT / "docs" / "STAGE53A_PBE5AC_PTP_OTA_AUTORESEARCH_BENCHMARK.md"
DOC_S54A = REPO_ROOT / "docs" / "STAGE54A_LITEBEAM_AND_PBE5AC_PTP_AUTORESEARCH_BENCHMARK.md"
DOC_S56A = REPO_ROOT / "docs" / "STAGE56A_PTP_PBE5AC_AND_LITEBEAM_GOLDEN_STACK_BENCHMARK.md"
OPENWISP_SEED = REPO_ROOT / "tools" / "nms" / "seed_real_openwisp_db.py"


def test_stage53a_pbe5ac_ptp_artifact_and_persistence() -> None:
    """Verify Stage 53A 16-window counterbalanced PtP artifact, flash persistence, and documentation."""
    assert OUT_S53A_JSON.exists(), f"Missing Stage 53A artifact: {OUT_S53A_JSON}"
    data = json.loads(OUT_S53A_JSON.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 53A"
    assert data["task_id"] == "T-S53A-PBE5AC-PTP-OTA-AUTORESEARCH-BENCH"
    assert len(data["windows"]) == 16

    for w in data["windows"]:
        assert w["apply_meta"]["ota_verified"] is True
        assert w["apply_meta"]["sta_watchdog_disarmed"] is True

    for r_id in ROUNDS_S53A:
        assert r_id in data["rounds_summary"]
        r = data["rounds_summary"][r_id]
        assert r["treatment_B"]["mean_aggregate_dl_mbps"] > 10.0

    fp = data["flash_persistence_receipt"]
    assert fp["ap_241_cfgmtd_rc"] == 0
    assert fp["sta_242_cfgmtd_rc"] == 0

    assert DOC_S53A.exists(), f"Missing Stage 53A report: {DOC_S53A}"
    doc_text = DOC_S53A.read_text(encoding="utf-8")
    for r_id in ROUNDS_S53A:
        assert r_id in doc_text


def test_stage54a_cross_node_ptp_artifact_and_persistence() -> None:
    """Verify Stage 54A 12-window cross-node (.251 -> .241 -> .242) PtP artifact and documentation."""
    assert OUT_S54A_JSON.exists(), f"Missing Stage 54A artifact: {OUT_S54A_JSON}"
    data = json.loads(OUT_S54A_JSON.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 54A"
    assert data["task_id"] == "T-S54A-LITEBEAM-TO-REMOTE-PBE5AC-CROSS-PTP-AUTORESEARCH-BENCH"
    assert len(data["windows"]) == 12

    for w in data["windows"]:
        assert w["apply_meta"]["e2e_ota_verified"] is True
        assert w["apply_meta"]["sta_watchdog_disarmed"] is True

    for r_id in ROUNDS_S54A:
        assert r_id in data["rounds_summary"]
        r = data["rounds_summary"][r_id]
        assert r["treatment_B"]["mean_aggregate_dl_mbps"] > 10.0

    fp = data["flash_persistence_receipt"]
    assert fp["lbe_251_cfgmtd_rc"] == 0
    assert fp["ap_241_cfgmtd_rc"] == 0
    assert fp["sta_242_cfgmtd_rc"] == 0

    assert DOC_S54A.exists(), f"Missing Stage 54A report: {DOC_S54A}"
    doc_text = DOC_S54A.read_text(encoding="utf-8")
    for r_id in ROUNDS_S54A:
        assert r_id in doc_text


def test_stage56a_ptp_golden_stack_v2_and_openwisp_template() -> None:
    """Verify Stage 56A 12-window Golden Stack v2 artifact, flash persistence, report, and OpenWISP seed."""
    assert OUT_S56A_JSON.exists(), f"Missing Stage 56A artifact: {OUT_S56A_JSON}"
    data = json.loads(OUT_S56A_JSON.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 56A"
    assert data["task_id"] == "T-S56A-PTP-PBE5AC-AND-LITEBEAM-SIFS-BURST-AND-TCP-LOW-LATENCY-OTA-BENCH"
    assert len(data["windows"]) == 12

    for w in data["windows"]:
        assert w["apply_meta"]["e2e_ota_verified"] is True
        assert w["apply_meta"]["sta_watchdog_disarmed"] is True

    for r_id in ROUNDS_S56A:
        assert r_id in data["rounds_summary"]
        r = data["rounds_summary"][r_id]
        assert r["treatment_B"]["mean_aggregate_dl_mbps"] > 10.0

    fp = data["flash_persistence_receipt"]
    assert fp["lbe_251_cfgmtd_rc"] == 0
    assert fp["ap_241_cfgmtd_rc"] == 0
    assert fp["sta_242_cfgmtd_rc"] == 0

    assert DOC_S56A.exists(), f"Missing Stage 56A report: {DOC_S56A}"
    doc_text = DOC_S56A.read_text(encoding="utf-8")
    for r_id in ROUNDS_S56A:
        assert r_id in doc_text

    seed_text = OPENWISP_SEED.read_text(encoding="utf-8")
    assert "FuturaMAX-PtP-PowerBeam-LiteBeam-Golden-v2" in seed_text
    assert "FMX-R2AC-PRISM-BENCH-ETH8" in seed_text

