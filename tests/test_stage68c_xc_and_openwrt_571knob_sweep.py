from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage68c_xc_and_openwrt_571knob_sweep import (
    OUT_JSON,
    audit_571knob_catalog_for_stage68c,
)

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "STAGE68C_XC_AND_OPENWRT_UNEXPLORED_571KNOB_AUTORESEARCH_SWEEP.md"


def test_stage68c_571knob_catalog_audit() -> None:
    audit = audit_571knob_catalog_for_stage68c()
    assert audit["total_catalog_entries"] >= 248
    assert audit["previously_tested_entries"] == 245
    assert audit["untested_pool_entries"] == 326
    assert audit["auto_rollback_watchdog_timeout_s"] == 45
    assert len(audit["selected_xc_knobs"]) >= 5
    assert len(audit["selected_openwrt_knobs"]) >= 5


def test_stage68c_live_counterbalanced_sweep_receipt_and_safety_guards() -> None:
    assert OUT_JSON.exists(), f"Missing Stage 68C artifact: {OUT_JSON}"
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "68C"
    assert data["task_id"] == "T-S68C-XC-AND-OPENWRT-UNEXPLORED-571KNOB-AUTORESEARCH-SWEEP"
    assert data["status"] == "CONFIRMED"

    safety = data["safety_invariants"]
    assert safety["flash_writes"] == 0
    assert safety["auto_rollback_watchdog_timeout_s"] == 45
    assert safety["ar9342_64mb_oom_score_adj"] == -900
    assert safety["ar9342_64mb_fq_memory_limit_bytes"] == 4194304
    assert safety["direct_sysfs_tx_queue_len_only"] is True
    assert safety["uph_16int_vector_ff_mcast_written_last"] is True

    rounds = data["rounds"]
    assert [r["round_id"] for r in rounds] == ["S68C-XC-R1", "S68C-XC-R2", "S68C-OWRT-R1"]
    for r in rounds:
        assert set(r["phases"].keys()) == {"A1", "B1", "A2", "B2"}
        assert r["arm_a_mean_goodput_mbps"] > 0
        assert r["arm_b_mean_goodput_mbps"] > 0
        assert r["arm_a_mean_p95_rtt_ms"] > 0
        assert r["arm_b_mean_p95_rtt_ms"] > 0
        for phase_key in ("A1", "B1", "A2", "B2"):
            rb = r["phases"][phase_key]["getter_readback"]
            assert rb["ap_eth0_bql"]["hold_time"] == 800
            assert rb["ap_eth0_bql"]["limit_min"] == 4542
            assert rb["ap_eth0_bql"]["limit_max"] == 42392
            assert rb["ap_aqm"]["fq_memory_limit"] == 4194304
            assert "xc_extended_readback" in rb


def test_stage68c_doc_exists_and_under_250_lines() -> None:
    assert DOC_PATH.exists(), f"Missing Stage 68C doc: {DOC_PATH}"
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 250, f"Stage 68C doc has {len(lines)} lines (must be < 250)"
    assert lines[0].startswith("<!-- doc-head:")
