"""Regression tests for Stage 68A: PowerBeam 5AC Gen2 Hybrid OTA OpenWrt STA Readiness
Verification and Ground-Up v5 Autoresearch Benchmark.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE68A_JSON = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage68a_pbe5ac_hybrid_and_v5_autoresearch_20261026.json"
)


def test_stage68a_hybrid_ota_readiness_and_v5_autoresearch() -> None:
    assert STAGE68A_JSON.exists(), f"Missing {STAGE68A_JSON}"
    rep = json.loads(STAGE68A_JSON.read_text(encoding="utf-8"))
    assert rep["stage"] == "Stage 68A"
    assert rep["ticket"] == "T-S68A-PBE5AC-HYBRID-OTA-OPENWRT-STA-242-AND-AIROS8-V5-BENCH"

    # 1. Verify Hybrid OTA readiness & MTD flags audit on .241 and .242
    hyb = rep["hybrid_ota_and_mtd_readiness"]
    assert hyb["hybrid_link_stays_associated"] is True
    assert "mtd2" in hyb["sta_242_mtd_and_uboot_env_audit"]
    assert "mtd3" in hyb["sta_242_mtd_and_uboot_env_audit"]
    assert "mtd5" in hyb["sta_242_mtd_and_uboot_env_audit"]
    assert "flags=0xc00" in hyb["sta_242_mtd_and_uboot_env_audit"]

    # 2. Verify all 3 counterbalanced A1->B1->A2->B2 rounds (12 windows, >=28 RTT samples/arm)
    rounds = rep["rounds"]
    assert len(rounds) == 3
    for r in rounds:
        assert len(r["arm_a_windows"]) == 2
        assert len(r["arm_b_windows"]) == 2
        assert r["arm_a_summary"]["rtt_samples_total"] >= 28
        assert r["arm_b_summary"]["rtt_samples_total"] >= 28
        assert r["karpathy_autoresearch_eval"]["decision"] in ("keep", "discard")

    # Verify S68A-R1 and S68A-R2 achieved KEEP while S68A-R3 was DISCARD
    assert rounds[0]["round_id"] == "S68A-R1"
    assert rounds[0]["karpathy_autoresearch_eval"]["decision"] == "keep"
    assert rounds[0]["deltas"]["aggregate_goodput_delta_pct"] > 30.0
    assert rounds[0]["deltas"]["rtt_p95_delta_pct"] < -50.0

    assert rounds[1]["round_id"] == "S68A-R2"
    assert rounds[1]["karpathy_autoresearch_eval"]["decision"] == "keep"
    assert rounds[1]["deltas"]["aggregate_goodput_delta_pct"] > 10.0
    assert rounds[1]["deltas"]["rtt_p95_delta_pct"] < -10.0

    assert rounds[2]["round_id"] == "S68A-R3"
    assert rounds[2]["karpathy_autoresearch_eval"]["decision"] == "discard"
    assert rep["winning_round_id"] == "S68A-R2"

    # 3. Verify cfgmtd persistence succeeded on both AP (.241) and STA (.242)
    pers = rep["champion_persistence"]
    assert "CFGMTD_RC=0" in pers["ap_cfgmtd_receipt"]
    assert "CFGMTD_RC=0" in pers["sta_cfgmtd_receipt"]
