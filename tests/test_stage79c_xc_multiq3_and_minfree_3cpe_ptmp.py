#!/usr/bin/env python3
"""
Tests for Stage 79C — `XC` (`Rocket 5AC Prism Gen2`) `set_multiq=3` (`0x3`) + WMM `Minfree` Hierarchy
& `XW` `txqueuelen=64/128` 3-CPE Heterogeneous PtMP Benchmark (`FMX-DISC-23`).
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage79c_xc_multiq3_and_minfree_3cpe_ptmp import (
    OUT_JSON,
    STAGE72A_XC_V20_BASELINE_COMMANDS,
    STAGE79C_R1_XC_MULTIQ3_MINFREE_COMMANDS,
    STAGE79C_R2_XW_CANDIDATE_COMMANDS,
    STAGE79C_R3_XW_CANDIDATE_COMMANDS,
    STAGE79C_XW_BASELINE_COMMANDS,
)

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "STAGE79C_XC_SET_MULTIQ3_AND_MINFREE_3CPE_PTMP_BENCHMARK.md"


def test_stage79c_command_profiles() -> None:
    assert "iwpriv ath0 set_multiq 1" in STAGE72A_XC_V20_BASELINE_COMMANDS
    assert "iwpriv ath0 set_multiq 3" in STAGE79C_R1_XC_MULTIQ3_MINFREE_COMMANDS
    assert "echo 0 > /sys/module/ath_dev/parameters/ACVOMinfree 2>/dev/null || true" in STAGE79C_R1_XC_MULTIQ3_MINFREE_COMMANDS
    assert "echo 16 > /sys/module/ath_dev/parameters/ACVIMinfree 2>/dev/null || true" in STAGE79C_R1_XC_MULTIQ3_MINFREE_COMMANDS
    assert "echo 32 > /sys/module/ath_dev/parameters/ACBEMinfree 2>/dev/null || true" in STAGE79C_R1_XC_MULTIQ3_MINFREE_COMMANDS
    assert "echo 48 > /sys/module/ath_dev/parameters/ACBKMinfree 2>/dev/null || true" in STAGE79C_R1_XC_MULTIQ3_MINFREE_COMMANDS
    assert any("txqueuelen 64" in c for c in STAGE79C_R2_XW_CANDIDATE_COMMANDS)
    assert any("txqueuelen 128" in c for c in STAGE79C_R3_XW_CANDIDATE_COMMANDS)
    assert any("txqueuelen 256" in c for c in STAGE79C_XW_BASELINE_COMMANDS)


def test_stage79c_json_receipt_exists_and_invariants() -> None:
    assert OUT_JSON.exists(), f"Missing Stage 79C artifact: {OUT_JSON}"
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert payload["stage"] == "79C"
    assert payload["task_id"] == "T-S79C-XC-SET-MULTIQ-3-AND-WMM-MINFREE-HIERARCHY-3CPE-PTMP-BENCH"
    assert payload["status"] == "CONFIRMED"

    inv = payload["safety_invariants"]
    assert inv["flash_writes"] == 0
    assert inv["auto_rollback_watchdog_timeout_s"] == 45
    assert inv["xc_set_multiq_candidate"] == 3
    assert inv["xc_wmm_minfree_hierarchy"] == {"ACVO": 0, "ACVI": 16, "ACBE": 32, "ACBK": 48}
    assert inv["per_window_busybox_seq_warmup"] is True


def test_stage79c_r1_xc_multiq3_and_minfree_telemetry() -> None:
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    rounds = {r["round_id"]: r for r in payload["rounds"]}
    r1 = rounds["S79C-R1-XC-SET-MULTIQ-3-AND-MINFREE-HIERARCHY-ON-V20"]
    assert r1["arm_a_mean_goodput_mbps"] == 39.196
    assert r1["arm_b_mean_goodput_mbps"] == 40.734
    assert r1["goodput_delta_pct"] > 3.9
    assert r1["iptv_jitter_delta_pct"] < -28.0
    assert r1["voip_jitter_delta_pct"] < -7.5
    assert r1["pareto_score_delta_pct"] > 1.5
    assert r1["phases"]["B1"]["getter_readback"]["xc_extended_readback"]["multiq"] == 3
    assert r1["phases"]["B1"]["getter_readback"]["xc_extended_readback"]["ACVIMinfree"] == 16
    assert r1["phases"]["B1"]["getter_readback"]["xc_extended_readback"]["ACBEMinfree"] == 32
    assert r1["phases"]["B1"]["getter_readback"]["xc_extended_readback"]["ACBKMinfree"] == 48
    assert r1["phases"]["A1"]["getter_readback"]["xc_extended_readback"]["multiq"] == 1


def test_stage79c_r2_and_r3_xw_txqueuelen_telemetry() -> None:
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    rounds = {r["round_id"]: r for r in payload["rounds"]}

    r2 = rounds["S79C-R2-XC-SET-MULTIQ-3-PLUS-XW-TXQUEUELEN-64"]
    assert r2["p95_rtt_delta_pct"] < -19.0
    assert r2["arm_b_mean_p95_rtt_ms"] < r2["arm_a_mean_p95_rtt_ms"]
    assert r2["arm_b_mean_p99_rtt_ms"] < r2["arm_a_mean_p99_rtt_ms"]
    assert r2["pareto_score_delta_pct"] > 3.7

    r3 = rounds["S79C-R3-XC-SET-MULTIQ-3-PLUS-XW-TXQUEUELEN-128"]
    assert r3["iptv_jitter_delta_pct"] < -2.0
    assert r3["voip_jitter_delta_pct"] < -9.0
    assert set(r3["phases"].keys()) == {"A1", "B1", "A2", "B2"}


def test_stage79c_markdown_doc_exists_and_meets_budget() -> None:
    assert DOC_PATH.exists(), f"Missing Stage 79C report: {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0].startswith("<!-- doc-head:")
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
    assert len(lines) < 220
    assert "FMX-DISC-23" in text
    assert "S79C-R1" in text
    assert "S79C-R2" in text
    assert "S79C-R3" in text
