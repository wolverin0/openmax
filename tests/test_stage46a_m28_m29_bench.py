from __future__ import annotations

import json

from controller.multiradio_golden_profile_applicator import (
    STAGE46A_CHAMPION_V16_OVERLAY,
    get_stage46a_champion_v16_profile,
)
from tools.bench.run_stage46a_m28_m29_bql_and_tx_bias_bench import (
    OUT_JSON,
    parse_bql_table,
)


def test_parse_bql_table() -> None:
    sample_bql = (
        "==> /sys/class/net/eth0/queues/tx-0/byte_queue_limits/hold_time <==\n500\n"
        "==> /sys/class/net/eth0/queues/tx-0/byte_queue_limits/inflight <==\n1514\n"
        "==> /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit <==\n24576\n"
        "==> /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max <==\n24576\n"
        "==> /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_min <==\n3028\n"
    )
    parsed = parse_bql_table(sample_bql)
    assert parsed == {
        "hold_time": 500,
        "inflight": 1514,
        "limit": 24576,
        "limit_max": 24576,
        "limit_min": 3028,
    }


def test_stage46a_artifact_schema_and_4_rounds() -> None:
    assert OUT_JSON.exists(), f"Missing Stage 46A artifact: {OUT_JSON}"
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "46A"
    assert data["task_id"] == "T-S46A-M28-M29-AG71XX-BQL-HOLD-TIME-AND-ATH10K-VI-AQL-IPTV-BENCH"
    assert data["safety_policy"]["ram_only"] is True
    assert data["safety_policy"]["flash_writes"] == 0
    assert data["safety_policy"]["production_radios_touched"] == 0
    assert data["safety_policy"]["counterbalanced_order"] == ["A1", "B1", "A2", "B2"]

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {"S46A-R1", "S46A-R2", "S46A-R3", "S46A-R4", "S46A-R5", "S46A-R6"}

    # S46A-R1, S46A-R2, S46A-R4, S46A-R5, S46A-R6 must be REFUTED
    for rid in ("S46A-R1", "S46A-R2", "S46A-R4", "S46A-R5", "S46A-R6"):
        r = rounds[rid]
        assert r["promoted"] is False
        assert r["decision"] == "RETAIN_CURRENT_CHAMPION"
        assert r["claim_status"] == "REFUTED"
        assert set(r["phases"].keys()) == {"A1", "B1", "A2", "B2"}

    # Verify S46A-R1 getter readback shows eth0 BQL limit_max=24576, limit_min=3028, hold_time=500 in Arm B
    r1_b1_bql = rounds["S46A-R1"]["phases"]["B1"]["getter_readback"]["ap_eth0_bql"]
    assert r1_b1_bql["limit_max"] == 24576
    assert r1_b1_bql["limit_min"] == 3028
    assert r1_b1_bql["hold_time"] == 500
    assert rounds["S46A-R1"]["iptv_jitter_delta_pct"] < -65.0


def test_stage46a_r3_strict_pareto_promotion() -> None:
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    r3 = next(r for r in data["rounds"] if r["round_id"] == "S46A-R3")
    assert r3["mechanism_id"] == "M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600"
    assert r3["promoted"] is True
    assert r3["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r3["claim_status"] == "CONFIRMED"
    assert r3["goodput_delta_pct"] > 3.0
    assert r3["p95_rtt_delta_pct"] < -6.0
    assert r3["iptv_jitter_delta_pct"] < -15.0
    assert r3["voip_jitter_delta_pct"] < -5.0
    assert data["summary"]["promoted_count"] == 1
    assert "Stage 46A Champion v16" in data["summary"]["active_champion_after_stage46a"]

    # Verify dev_weight_tx_bias=2 at full netdev_budget=600 in B1/B2 vs 1 in A1/A2
    assert r3["phases"]["A1"]["getter_readback"]["ap_sysctl"]["dev_weight_tx_bias"] == 1
    assert r3["phases"]["B1"]["getter_readback"]["ap_sysctl"]["dev_weight_tx_bias"] == 2
    assert r3["phases"]["B1"]["getter_readback"]["ap_sysctl"]["netdev_budget"] == 600
    assert r3["phases"]["B1"]["getter_readback"]["cpe_sysctl"]["dev_weight_tx_bias"] == 2


def test_stage46a_champion_v16_overlay() -> None:
    prof = get_stage46a_champion_v16_profile()
    assert "Stage 46A Champion v16" in str(prof["champion_version"])
    assert "S46A-R3" in prof["validated_rounds"]
    ap_cmds = " ".join(str(x) for x in STAGE46A_CHAMPION_V16_OVERLAY["ap_extra_apply_commands"])
    cpe_cmds = " ".join(str(x) for x in STAGE46A_CHAMPION_V16_OVERLAY["cpe_extra_apply_commands"])
    assert "net.core.dev_weight_tx_bias=2" in ap_cmds
    assert "net.core.netdev_budget=600" in ap_cmds
    assert "net.core.dev_weight_tx_bias=2" in cpe_cmds
