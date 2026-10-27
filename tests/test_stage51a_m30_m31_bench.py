from __future__ import annotations

import json
from pathlib import Path

from controller.multiradio_golden_profile_applicator import (
    STAGE51A_CHAMPION_V17_OVERLAY,
    get_stage51a_champion_v17_profile,
)
from tools.bench.run_stage51a_m30_m31_bql_sweetspot_and_aql_bench import OUT_JSON

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_JSON = ROOT / "artifacts" / "autoresearch" / "stage51a_m30_m31_bql_limit_max_and_aql_bench_20261025.json"


def test_stage51a_artifact_schema_and_6_rounds() -> None:
    assert OUT_JSON.exists(), f"Missing Stage 51A artifact: {OUT_JSON}"
    assert CANONICAL_JSON.exists(), f"Missing canonical Stage 51A artifact: {CANONICAL_JSON}"
    data = json.loads(CANONICAL_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "51A"
    assert data["task_id"] == "T-S51A-M30-M31-BQL-LIMIT-MAX-36288-AND-PER-AC-AQL-TX-BIAS-BENCH"
    assert data["safety_policy"]["ram_only"] is True
    assert data["safety_policy"]["flash_writes"] == 0
    assert data["safety_policy"]["production_radios_touched"] == 0
    assert data["safety_policy"]["counterbalanced_order"] == ["A1", "B1", "A2", "B2"]

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {"S51A-R1", "S51A-R2", "S51A-R3", "S51A-R4", "S51A-R5", "S51A-R6"}

    for rid in ("S51A-R1", "S51A-R2", "S51A-R3", "S51A-R4", "S51A-R5"):
        r = rounds[rid]
        assert r["promoted"] is False
        assert r["decision"] == "RETAIN_CURRENT_CHAMPION"
        assert r["claim_status"] == "REFUTED"
        assert set(r["phases"].keys()) == {"A1", "B1", "A2", "B2"}

    # Verify S51A-R1 getter readback shows eth0 BQL limit_max=36336, limit_min=3028, hold_time=750 in Arm B
    r1_b1_bql = rounds["S51A-R1"]["phases"]["B1"]["getter_readback"]["ap_eth0_bql"]
    assert r1_b1_bql["limit_max"] == 36336
    assert r1_b1_bql["limit_min"] == 3028
    assert r1_b1_bql["hold_time"] == 750

    # Verify S51A-R5 getter readback shows AC_VI aql_txq_limit 2000/3500 us in Arm B vs 1200/2400 us in Arm A
    r5_a1_aql = rounds["S51A-R5"]["phases"]["A1"]["getter_readback"]["ap_aql_txq_limit"]
    r5_b1_aql = rounds["S51A-R5"]["phases"]["B1"]["getter_readback"]["ap_aql_txq_limit"]
    assert r5_a1_aql["VI"] == {"low_us": 1200, "high_us": 2400}
    assert r5_b1_aql["VI"] == {"low_us": 2000, "high_us": 3500}


def test_stage51a_r6_strict_pareto_promotion() -> None:
    data = json.loads(CANONICAL_JSON.read_text(encoding="utf-8"))
    r6 = next(r for r in data["rounds"] if r["round_id"] == "S51A-R6")
    assert r6["mechanism_id"] == "M30c_PURE_BQL_LIMIT_MAX_42392_HOLD_1000_3CPE_VERIFIED"
    assert r6["promoted"] is True
    assert r6["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r6["claim_status"] == "CONFIRMED"
    assert r6["goodput_delta_pct"] > 6.0
    assert r6["p95_rtt_delta_pct"] < -6.0
    assert r6["iptv_jitter_delta_pct"] < -20.0
    assert r6["voip_jitter_delta_pct"] < -30.0
    assert r6["pareto_score_delta_pct"] > 8.5
    assert data["summary"]["promoted_count"] == 1
    assert "Stage 51A Champion v17" in data["summary"]["active_champion_after_stage51a"]

    # Verify all 3 CPEs have 0.0% loss across all 4 windows in S51A-R6 and eth0 BQL limit_max=42392 in B1/B2
    for phase_key in ("A1", "B1", "A2", "B2"):
        phase = r6["phases"][phase_key]
        assert phase["mean_loss_pct"] == 0.0
        for cpe_key in ("Loco5AC_WA", "Rocket5AC_XC", "LiteBeamM5_XW"):
            assert phase["per_cpe"][cpe_key]["latency"]["loss_pct"] == 0.0

    assert r6["phases"]["A1"]["getter_readback"]["ap_eth0_bql"]["limit_max"] == 1879048192
    assert r6["phases"]["B1"]["getter_readback"]["ap_eth0_bql"]["limit_max"] == 42392
    assert r6["phases"]["B1"]["getter_readback"]["ap_eth0_bql"]["limit_min"] == 3028
    assert r6["phases"]["B1"]["getter_readback"]["ap_eth0_bql"]["hold_time"] == 1000
    assert r6["phases"]["B1"]["getter_readback"]["cpe_eth0_bql"]["limit_max"] == 42392
    assert r6["phases"]["B1"]["getter_readback"]["ap_sysctl"]["dev_weight_tx_bias"] == 2


def test_stage51a_champion_v17_overlay() -> None:
    prof = get_stage51a_champion_v17_profile()
    assert "Stage 51A Champion v17" in str(prof["champion_version"])
    assert "S51A-R6" in prof["validated_rounds"]
    ap_cmds = " ".join(str(x) for x in STAGE51A_CHAMPION_V17_OVERLAY["ap_extra_apply_commands"])
    cpe_cmds = " ".join(str(x) for x in STAGE51A_CHAMPION_V17_OVERLAY["cpe_extra_apply_commands"])
    assert "echo 42392 > /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max" in ap_cmds
    assert "echo 3028 > /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_min" in ap_cmds
    assert "net.core.dev_weight_tx_bias=2" in ap_cmds
    assert "echo 42392 > /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max" in cpe_cmds
