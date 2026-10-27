from __future__ import annotations

import json
from pathlib import Path

from controller.multiradio_golden_profile_applicator import (
    STAGE52A_CHAMPION_V18_OVERLAY,
    get_stage52a_champion_v18_profile,
)
from tools.bench.run_stage52a_m32_m33_budget_usecs_and_bql_min_bench import OUT_JSON

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_JSON = ROOT / "artifacts" / "autoresearch" / "stage52a_m32_m33_budget_usecs_and_bql_min_bench_20261025.json"


def test_stage52a_artifact_schema_and_4_rounds() -> None:
    assert OUT_JSON.exists(), f"Missing Stage 52A artifact: {OUT_JSON}"
    assert CANONICAL_JSON.exists(), f"Missing canonical Stage 52A artifact: {CANONICAL_JSON}"
    data = json.loads(CANONICAL_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "52A"
    assert data["task_id"] == "T-S52A-M32-M33-NETDEV-BUDGET-USECS-AND-PER-TID-AQL-V17-BENCH"
    assert data["safety_policy"]["ram_only"] is True
    assert data["safety_policy"]["flash_writes"] == 0
    assert data["safety_policy"]["production_radios_touched"] == 0
    assert data["safety_policy"]["counterbalanced_order"] == ["A1", "B1", "A2", "B2"]

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {"S52A-R1", "S52A-R2", "S52A-R3", "S52A-R4"}

    for rid in ("S52A-R1", "S52A-R2", "S52A-R4"):
        r = rounds[rid]
        assert r["promoted"] is False
        assert r["decision"] == "RETAIN_CURRENT_CHAMPION"
        assert r["claim_status"] == "REFUTED"
        assert set(r["phases"].keys()) == {"A1", "B1", "A2", "B2"}

    # Verify CONFIG_HZ=100 min_netdev_budget_usecs=20000 control boundary in S52A-R1 getter readback
    r1_b1_sys = rounds["S52A-R1"]["phases"]["B1"]["getter_readback"]["ap_sysctl"]
    assert r1_b1_sys["netdev_budget_usecs"] == 20000
    assert r1_b1_sys["dev_weight_tx_bias"] == 2

    # Verify S52A-R2 getter readback shows eth0 BQL limit_min=4542 (3xMTU) and limit_max=42392 in Arm B vs 3028 in Arm A
    r2_a1_bql = rounds["S52A-R2"]["phases"]["A1"]["getter_readback"]["ap_eth0_bql"]
    r2_b1_bql = rounds["S52A-R2"]["phases"]["B1"]["getter_readback"]["ap_eth0_bql"]
    assert r2_a1_bql["limit_min"] == 3028
    assert r2_a1_bql["limit_max"] == 42392
    assert r2_b1_bql["limit_min"] == 4542
    assert r2_b1_bql["limit_max"] == 42392
    assert r2_b1_bql["hold_time"] == 1000


def test_stage52a_r3_strict_pareto_promotion() -> None:
    data = json.loads(CANONICAL_JSON.read_text(encoding="utf-8"))
    r3 = next(r for r in data["rounds"] if r["round_id"] == "S52A-R3")
    assert r3["mechanism_id"] == "M33a_COMBINED_BUDGET_USECS_6000_AND_BQL_MIN_4542"
    assert r3["promoted"] is True
    assert r3["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r3["claim_status"] == "CONFIRMED"
    assert r3["goodput_delta_pct"] > 7.0
    assert r3["p95_rtt_delta_pct"] < -1.5
    assert r3["arm_b_mean_p50_rtt_ms"] < r3["arm_a_mean_p50_rtt_ms"]
    assert r3["pareto_score_delta_pct"] > 7.5
    assert data["summary"]["promoted_count"] == 1
    assert "Stage 52A Champion v18" in data["summary"]["active_champion_after_stage52a"]

    # Verify all 3 CPEs have 0.0% loss across all 4 windows in S52A-R3 and eth0 BQL limit_min=4542 in B1/B2
    for phase_key in ("A1", "B1", "A2", "B2"):
        phase = r3["phases"][phase_key]
        assert phase["mean_loss_pct"] == 0.0
        for cpe_key in ("Loco5AC_WA", "Rocket5AC_XC", "LiteBeamM5_XW"):
            assert phase["per_cpe"][cpe_key]["latency"]["loss_pct"] == 0.0

    assert r3["phases"]["A1"]["getter_readback"]["ap_eth0_bql"]["limit_min"] == 3028
    assert r3["phases"]["B1"]["getter_readback"]["ap_eth0_bql"]["limit_min"] == 4542
    assert r3["phases"]["B1"]["getter_readback"]["ap_eth0_bql"]["limit_max"] == 42392
    assert r3["phases"]["B1"]["getter_readback"]["ap_eth0_bql"]["hold_time"] == 1000
    assert r3["phases"]["B1"]["getter_readback"]["cpe_eth0_bql"]["limit_min"] == 4542
    assert r3["phases"]["B1"]["getter_readback"]["cpe_eth0_bql"]["limit_max"] == 42392
    assert r3["phases"]["B1"]["getter_readback"]["ap_sysctl"]["dev_weight_tx_bias"] == 2


def test_stage52a_champion_v18_overlay() -> None:
    prof = get_stage52a_champion_v18_profile()
    assert "Stage 52A Champion v18" in str(prof["champion_version"])
    assert "S52A-R3" in prof["validated_rounds"]
    ap_cmds = " ".join(str(x) for x in STAGE52A_CHAMPION_V18_OVERLAY["ap_extra_apply_commands"])
    cpe_cmds = " ".join(str(x) for x in STAGE52A_CHAMPION_V18_OVERLAY["cpe_extra_apply_commands"])
    assert "echo 42392 > /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max" in ap_cmds
    assert "echo 4542 > /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_min" in ap_cmds
    assert "net.core.dev_weight_tx_bias=2" in ap_cmds
    assert "echo 4542 > /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_min" in cpe_cmds
