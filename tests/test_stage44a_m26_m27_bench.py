from __future__ import annotations

import json
from pathlib import Path

from controller.multiradio_golden_profile_applicator import (
    GOLDEN_PROFILES,
    STAGE44A_CHAMPION_V15_OVERLAY,
    get_stage44a_champion_v15_profile,
)
from tools.bench.run_stage44a_m26_m27_napi_and_r5ac_txq_bench import (
    OUT_JSON,
    parse_netdev_int_table,
    parse_r5ac_m26_readback,
)


def test_parse_netdev_int_table_and_r5ac_m26_readback() -> None:
    sample_napi = """==> /sys/class/net/br-lan/napi_defer_hard_irqs <==
2

==> /sys/class/net/eth0/napi_defer_hard_irqs <==
2

==> /sys/class/net/phy0-ap0.sta1/napi_defer_hard_irqs <==
2
"""
    parsed_napi = parse_netdev_int_table(sample_napi, "napi_defer_hard_irqs")
    assert parsed_napi == {"br-lan": 2, "eth0": 2, "phy0-ap0.sta1": 2}

    sample_r5ac = (
        b"br0_txqueuelen=256\nath0_txqueuelen=256\neth0_txqueuelen=256\n"
        b"netdev_budget=600\ndev_weight=64\nff_mcast_airtime_limit=5\n",
        b"",
    )
    parsed_r5ac = parse_r5ac_m26_readback(sample_r5ac)
    assert parsed_r5ac["br0_txqueuelen"] == 256
    assert parsed_r5ac["ath0_txqueuelen"] == 256
    assert parsed_r5ac["eth0_txqueuelen"] == 256
    assert parsed_r5ac["netdev_budget"] == 600
    assert parsed_r5ac["dev_weight"] == 64
    assert parsed_r5ac["ff_mcast_airtime_limit"] == 5


def test_stage44a_artifact_schema_and_5_rounds() -> None:
    assert OUT_JSON.exists(), f"Missing Stage 44A artifact: {OUT_JSON}"
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "44A"
    assert data["task_id"] == "T-S44A-M26-M27-PER-STA-WDS-NAPI-WEIGHT-AND-UDP-GRO-IPTV-BENCH"
    assert data["safety_policy"]["ram_only"] is True
    assert data["safety_policy"]["flash_writes"] == 0
    assert data["safety_policy"]["production_radios_touched"] == 0
    assert data["safety_policy"]["counterbalanced_order"] == ["A1", "B1", "A2", "B2"]

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {"S44A-R1", "S44A-R2", "S44A-R3", "S44A-R4", "S44A-R5"}

    # S44A-R1..R4 must record honest REFUTED / RETAIN_CURRENT_CHAMPION results
    for rid in ("S44A-R1", "S44A-R2", "S44A-R3", "S44A-R4"):
        r = rounds[rid]
        assert r["promoted"] is False
        assert r["decision"] == "RETAIN_CURRENT_CHAMPION"
        assert r["claim_status"] == "REFUTED"
        assert set(r["phases"].keys()) == {"A1", "B1", "A2", "B2"}

    # Verify S44A-R2 getter readback shows napi_defer_hard_irqs=2 and gro_flush_timeout=100000 in Arm B
    r2_b1_rb = rounds["S44A-R2"]["phases"]["B1"]["getter_readback"]
    assert r2_b1_rb["ap_napi_defer_hard_irqs"]["br-lan"] == 2
    assert r2_b1_rb["ap_gro_flush_timeout_ns"]["br-lan"] == 100000


def test_stage44a_r5_promotion_and_zero_iptv_voip_loss() -> None:
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    r5 = next(r for r in data["rounds"] if r["round_id"] == "S44A-R5")
    assert r5["mechanism_id"] == "M26b_PURE_R5AC_BR0_TXQ_256_OPENWRT_ETH0_1000"
    assert r5["promoted"] is True
    assert r5["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r5["claim_status"] == "CONFIRMED"
    assert r5["goodput_delta_pct"] > 5.0
    assert r5["p95_rtt_delta_pct"] < -3.0
    assert r5["iptv_arm_b_mean_loss_pct"] == 0.0
    assert r5["voip_arm_b_mean_loss_pct"] == 0.0

    # Verify R5AC br0_txqueuelen=256 and netdev_budget=600 in B1/B2 vs 1000/300 in A1/A2
    assert r5["phases"]["A1"]["getter_readback"]["r5ac_m26_state"]["br0_txqueuelen"] == 1000
    assert r5["phases"]["A1"]["getter_readback"]["r5ac_m26_state"]["netdev_budget"] == 300
    assert r5["phases"]["B1"]["getter_readback"]["r5ac_m26_state"]["br0_txqueuelen"] == 256
    assert r5["phases"]["B1"]["getter_readback"]["r5ac_m26_state"]["netdev_budget"] == 600
    assert r5["phases"]["B1"]["getter_readback"]["ap_netdev_tx_queue_len"]["eth0"] == 1000
    assert r5["phases"]["B1"]["getter_readback"]["ap_netdev_tx_queue_len"]["br-lan"] == 256


def test_stage44a_champion_v15_overlay_and_r5ac_profile() -> None:
    prof = get_stage44a_champion_v15_profile()
    assert "Stage 44A Champion v15" in str(prof["champion_version"])
    assert "S44A-R5" in prof["validated_rounds"]
    r5ac_cmds = " ".join(str(x) for x in STAGE44A_CHAMPION_V15_OVERLAY["r5ac_xc_extra_apply_commands"])
    assert "ifconfig br0 txqueuelen 256" in r5ac_cmds
    assert "net.core.netdev_budget=600" in r5ac_cmds
