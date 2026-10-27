#!/usr/bin/env python3
"""
Unit & Schema Tests for Stage 42A (`T-S42A-M24-M25-PER-TID-QUANTUM-AND-AIROS6-MCAST-GUARD-BENCH`).
"""

from __future__ import annotations

import json
from pathlib import Path

from controller.multiradio_golden_profile_applicator import (
    STAGE42A_CHAMPION_V14_OVERLAY,
    export_champion_ledger,
    get_stage42a_champion_v14_profile,
)
from tools.bench.run_stage42a_m24_m25_airos6_mcast_and_txq_bench import (
    OUT_JSON,
    parse_lbm5_m24_readback,
    parse_netdev_txq_table,
)

ROOT = Path(__file__).resolve().parents[1]


def test_parse_netdev_txq_table() -> None:
    raw = """==> /sys/class/net/br-lan/tx_queue_len <==
256

==> /sys/class/net/phy0-ap0.sta1/tx_queue_len <==
256

==> /sys/class/net/phy0-ap0.sta2/tx_queue_len <==
256

==> /sys/class/net/phy0-ap0/tx_queue_len <==
256
"""
    parsed = parse_netdev_txq_table(raw)
    assert parsed == {
        "br-lan": 256,
        "phy0-ap0.sta1": 256,
        "phy0-ap0.sta2": 256,
        "phy0-ap0": 256,
    }


def test_parse_lbm5_m24_readback_handles_dict_and_str() -> None:
    raw_dict = {
        "stdout": (
            "br0_txqueuelen=256\n"
            "ath0_txqueuelen=256\n"
            "eth0_txqueuelen=256\n"
            "ewma_delegate=1\n"
            "txop_params=0 0\n"
            "no_ack_rate=0 -1\n"
            "no_auto_prio=0\n"
        )
    }
    parsed = parse_lbm5_m24_readback(raw_dict)
    assert parsed["br0_txqueuelen"] == 256
    assert parsed["ath0_txqueuelen"] == 256
    assert parsed["ewma_delegate"] == 1
    assert parsed["txop_params"] == "0 0"
    assert parsed["no_auto_prio"] == 0


def test_stage42a_artifact_and_champion_v14_promotion() -> None:
    assert OUT_JSON.exists(), f"Missing {OUT_JSON}"
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert payload["stage"] == "42A"
    assert payload["task_id"] == "T-S42A-M24-M25-PER-TID-QUANTUM-AND-AIROS6-MCAST-GUARD-BENCH"
    assert payload["safety_policy"]["ram_only"] is True
    assert payload["safety_policy"]["flash_writes"] == 0
    assert payload["safety_policy"]["production_radios_touched"] == 0

    rounds = {r["round_id"]: r for r in payload["rounds"]}
    assert "S42A-R1" in rounds
    assert "S42A-R2" in rounds
    assert "S42A-R3" in rounds
    assert "S42A-R4" in rounds
    assert "S42A-R5" in rounds

    # S42A-R1..R4 must be preserved as honest negative / diagnostic evidence
    for rid in ("S42A-R1", "S42A-R2", "S42A-R3", "S42A-R4"):
        assert rounds[rid]["promoted"] is False
        assert rounds[rid]["decision"] == "RETAIN_CURRENT_CHAMPION"

    # S42A-R5 must be promoted as Stage 42A Champion v14
    r5 = rounds["S42A-R5"]
    assert r5["promoted"] is True
    assert r5["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r5["claim_status"] == "CONFIRMED"
    assert r5["goodput_delta_pct"] > 0.0
    assert r5["p95_rtt_delta_pct"] < 0.0
    assert r5["iptv_arm_b_mean_loss_pct"] == 0.0
    assert r5["voip_arm_b_mean_loss_pct"] == 0.0

    # Verify direct sysfs tx_queue_len readback on B1 and B2 vs A1 and A2
    assert r5["phases"]["A1"]["getter_readback"]["ap_netdev_tx_queue_len"]["br-lan"] == 1000
    assert r5["phases"]["B1"]["getter_readback"]["ap_netdev_tx_queue_len"]["br-lan"] == 256
    assert r5["phases"]["B1"]["getter_readback"]["ap_netdev_tx_queue_len"]["phy0-ap0.sta1"] == 256
    assert r5["phases"]["B1"]["getter_readback"]["ap_netdev_tx_queue_len"]["phy0-ap0.sta2"] == 256
    assert r5["phases"]["B2"]["getter_readback"]["loco_netdev_tx_queue_len"]["phy0-sta0"] == 256


def test_stage42a_champion_v14_overlay_in_applicator_and_ledger(tmp_path: Path) -> None:
    prof = get_stage42a_champion_v14_profile()
    assert prof == STAGE42A_CHAMPION_V14_OVERLAY
    assert "S42A-R5" in prof["validated_rounds"]  # type: ignore[operator]
    ap_cmds = " ; ".join(prof["ap_extra_apply_commands"])  # type: ignore[arg-type]
    assert "/sys/class/net/phy0-ap0*/tx_queue_len" in ap_cmds
    assert "echo 256" in ap_cmds

    ledger_file = tmp_path / "ledger.json"
    ledger = export_champion_ledger(str(ledger_file))
    assert "stage42a_champion_v14" in ledger
    assert ledger["stage42a_champion_v14"]["champion_version"].startswith("Stage 42A Champion v14")
