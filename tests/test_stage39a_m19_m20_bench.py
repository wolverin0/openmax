"""Stage 39A verification tests for M19 + M20 (WDS Port Multicast Fast-Leave + airOS 8 Shared uph_wifi0 Buffer Discipline -> Champion v12)."""

from __future__ import annotations

import json
from pathlib import Path

from controller.multiradio_golden_profile_applicator import (
    STAGE39A_CHAMPION_V12_OVERLAY,
    export_champion_ledger,
    get_stage39a_champion_v12_profile,
)
from tools.bench.run_stage39a_m19_m20_igmp_fast_leave_bench import parse_bridge_mcast_readback

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage39a_m19_m20_igmp_fast_leave_bench_20261025.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE39A_M19_M20_IGMP_FAST_LEAVE_AND_MCAST_STALL_BENCHMARK.md"
LEDGER_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "champion_state_ledger.json"


def test_parse_bridge_mcast_readback_extracts_bridge_brif_and_uph() -> None:
    raw = (
        "==> /sys/devices/virtual/net/br-lan/bridge/multicast_igmp_version <==\n"
        "2\n\n"
        "==> /sys/devices/virtual/net/br-lan/brif/phy0-ap0.sta1/multicast_fast_leave <==\n"
        "1\n\n"
        "==> /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit <==\n"
        "5\t0\t0\t0\n"
    )
    parsed = parse_bridge_mcast_readback(raw)
    assert parsed["bridge/multicast_igmp_version"] == 2
    assert parsed["brif/phy0-ap0.sta1/multicast_fast_leave"] == 1
    assert parsed["uph_wifi0/ff_mcast_airtime_limit"] == 5


def test_stage39a_receipt_and_champion_v12_promotion() -> None:
    assert RECEIPT_PATH.exists(), f"Missing Stage 39A receipt: {RECEIPT_PATH}"
    assert DOC_PATH.exists(), f"Missing Stage 39A report: {DOC_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["task_id"] == "T-S39A-M19-M20-AIROS8-MCAST-STALL-AND-IGMP-FAST-LEAVE-BENCH"
    assert data["flash_writes"] == 0
    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert "S39A-R1" in rounds
    assert "S39A-R2" in rounds
    assert "S39A-R3" in rounds

    # S39A-R1 preserved evidence: IGMPv3 tid7_ac0 preemption + voip_bias shared-buffer clobber -> RETAIN
    r1 = rounds["S39A-R1"]
    assert r1["decision"] == "RETAIN_CURRENT_CHAMPION"
    assert r1["phases"]["B1"]["mac80211_txq_aqm_delta"]["tid7_ac0"]["tx_packets_delta"] > 0
    assert r1["phases"]["B1"]["getter_readback"]["r198_m19_readback"]["uph_wifi0/ff_mcast_airtime_limit"] == 1

    # S39A-R2 preserved evidence: IGMPv2 eliminates tid7_ac0 preemption and cuts VoIP jitter -28.254%
    r2 = rounds["S39A-R2"]
    assert r2["decision"] == "RETAIN_CURRENT_CHAMPION"
    assert r2["voip_jitter_delta_pct"] < -20.0
    assert r2["phases"]["B1"]["mac80211_txq_aqm_delta"]["tid7_ac0"]["tx_packets_delta"] == 0

    # S39A-R3 promoted evidence: Stage 39A Champion v12 (+5.863% GP, -5.361% p95 RTT, 0.0% IPTV/VoIP loss, 0 drops)
    r3 = rounds["S39A-R3"]
    assert r3["mechanism_id"] == "M19c_M20c_CLEAN_WDS_FAST_LEAVE_AND_UPH_MCAST_LIMIT"
    assert r3["promoted"] is True
    assert r3["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r3["goodput_delta_pct"] > 5.0
    assert r3["p95_rtt_delta_pct"] < -5.0
    assert r3["iptv_arm_b_mean_loss_pct"] == 0.0
    assert r3["voip_arm_b_mean_loss_pct"] == 0.0

    for phase_key in ("B1", "B2"):
        ph = r3["phases"][phase_key]
        ap_rb = ph["getter_readback"]["ap_m20_readback"]
        r198_rb = ph["getter_readback"]["r198_m19_readback"]
        assert ap_rb["brif/phy0-ap0/multicast_fast_leave"] == 1
        assert ap_rb["brif/phy0-ap0.sta1/multicast_fast_leave"] == 1
        assert ap_rb["brif/phy0-ap0.sta2/multicast_fast_leave"] == 1
        assert ap_rb["brif/phy0-ap0.sta1/multicast_to_unicast"] == 1
        assert ap_rb["brif/phy0-ap0.sta2/multicast_to_unicast"] == 1
        assert r198_rb["uph_wifi0/ff_mcast_airtime_limit"] == 5
        assert r198_rb["brif/ath0/multicast_fast_leave"] == 1
        assert ph["mac80211_txq_aqm_delta"]["tid0_ac2"]["drops_delta"] == 0
        assert ph["mac80211_txq_aqm_delta"]["tid7_ac0"]["tx_packets_delta"] == 0


def test_stage39a_champion_v12_overlay_registered_in_ledger() -> None:
    export_champion_ledger()
    prof = get_stage39a_champion_v12_profile()
    assert prof == STAGE39A_CHAMPION_V12_OVERLAY
    assert "S39A-R3" in prof["validated_rounds"]
    ap_cmds = "\n".join(prof["ap_extra_apply_commands"])
    r5ac_cmds = "\n".join(prof["r5ac_xc_extra_apply_commands"])
    assert "multicast_fast_leave" in ap_cmds
    assert "multicast_to_unicast" in ap_cmds
    assert "fq_quantum 4542" in ap_cmds
    assert "fq_limit 2048" in ap_cmds
    assert "ff_mcast_airtime_limit" in r5ac_cmds

    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    assert "stage39a_champion_v12" in ledger
    assert ledger["stage39a_champion_v12"]["champion_version"].startswith("Stage 39A Champion v12")
