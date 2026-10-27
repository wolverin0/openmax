"""Stage 37A verification tests for 3-CPE 5 GHz Triple-Play (VoIP AC_VO + Dual IPTV AC_VI + Bulk TCP AC_BE) & mac80211 fq_limit benchmark."""

from __future__ import annotations

import json
from pathlib import Path

from controller.multiradio_golden_profile_applicator import (
    STAGE37A_CHAMPION_V11_OVERLAY,
    get_stage37a_champion_v11_profile,
)
from tools.bench.run_stage37a_triple_play_aqm_fq_limit_bench import (
    parse_station_aqm_3tier_table,
    parse_udp_stream_output,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage37a_triple_play_aqm_fq_limit_bench_20261025.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE37A_TRIPLE_PLAY_IPTV_VOIP_AND_MAC80211_FQ_LIMIT_BENCHMARK.md"
LEDGER_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "champion_state_ledger.json"


def test_parse_udp_stream_output_dual_iptv_and_voip() -> None:
    dual_iptv_sample = (
        "[SUM]   0.00-6.05   sec  3.56 MBytes  4.94 Mbits/sec  1.679 ms  0/2839 (0%)  receiver\n"
    )
    parsed_iptv = parse_udp_stream_output(dual_iptv_sample)
    assert parsed_iptv["delivered_bitrate_mbps"] == 4.94
    assert parsed_iptv["jitter_ms"] == 1.679
    assert parsed_iptv["lost_datagrams"] == 0
    assert parsed_iptv["total_datagrams"] == 2839
    assert parsed_iptv["packet_loss_pct"] == 0.0

    voip_sample = (
        "[  5]   0.00-6.04   sec  93.8 KBytes   127 Kbits/sec  1.579 ms  0/600 (0%)  receiver\n"
    )
    parsed_voip = parse_udp_stream_output(voip_sample)
    assert parsed_voip["delivered_bitrate_mbps"] == 0.127
    assert parsed_voip["jitter_ms"] == 1.579
    assert parsed_voip["lost_datagrams"] == 0
    assert parsed_voip["total_datagrams"] == 600
    assert parsed_voip["packet_loss_pct"] == 0.0


def test_parse_station_aqm_3tier_table_extracts_tid0_tid4_tid6() -> None:
    sample_aqm = (
        "target 19999us interval 99999us ecn yes\n"
        "tid ac backlog-bytes backlog-packets new-flows drops marks overlimit collisions tx-bytes tx-packets flags\n"
        "0 2 0 0 120 0 0 0 2 28064051 19804 0x7\n"
        "4 1 0 0 8 0 0 0 0 3937624 2847 0x3\n"
        "6 0 0 0 4 0 0 0 0 136416 599 0x3\n"
        "7 0 0 0 1 0 0 0 0 120 2 0x3\n"
    )
    table = parse_station_aqm_3tier_table(sample_aqm)
    assert table["tid0_ac2"]["tx_packets"] == 19804
    assert table["tid4_ac1"]["tx_packets"] == 2847
    assert table["tid6_ac0"]["tx_packets"] == 599
    assert table["tid7_ac0"]["tx_packets"] == 2


def test_stage37a_receipt_and_3tier_txq_verification() -> None:
    assert RECEIPT_PATH.exists(), f"Missing Stage 37A receipt: {RECEIPT_PATH}"
    assert DOC_PATH.exists(), f"Missing Stage 37A markdown report: {DOC_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["task_id"] == "T-S37A-MULTI-STREAM-IPTV-PLUS-VOIP-AC-VO-AND-MAC80211-FQ-LIMIT-BENCH"
    assert data["flash_writes"] == 0
    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert "S37A-R1" in rounds
    assert "S37A-R2" in rounds

    # S37A-R1 preserved evidence: VoIP jitter -49.865%, IPTV jitter -41.78%, p95 -3.028%, GP -3.628% -> RETAIN
    r1 = rounds["S37A-R1"]
    assert r1["mechanism_id"] == "M17_MAC80211_FQ_LIMIT_TRIPLE_PLAY"
    assert r1["voip_jitter_delta_pct"] < -40.0
    assert r1["iptv_jitter_delta_pct"] < -35.0
    assert r1["p95_rtt_delta_pct"] < 0.0
    assert r1["decision"] == "RETAIN_CURRENT_CHAMPION"

    # S37A-R2 promoted evidence: Stage 37A Champion v11 (+2.648% GP, -3.778% p95 RTT, -22.45% p50 RTT, 0.0% IPTV/VoIP loss)
    r2 = rounds["S37A-R2"]
    assert r2["mechanism_id"] == "M17b_MAC80211_FQ_LIMIT_TRIPLE_PLAY_QUANTUM_VO_AQL"
    assert r2["promoted"] is True
    assert r2["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r2["goodput_delta_pct"] > 0.0
    assert r2["p95_rtt_delta_pct"] < 0.0
    assert r2["arm_b_mean_p50_rtt_ms"] < r2["arm_a_mean_p50_rtt_ms"]
    assert r2["iptv_arm_b_mean_loss_pct"] == 0.0
    assert r2["voip_arm_b_mean_loss_pct"] == 0.0

    for phase_key in ("B1", "B2"):
        ph = r2["phases"][phase_key]
        assert "RW fq_limit 2048" in ph["getter_readback"]["ap_aqm_and_aql"]
        assert "RW fq_quantum 4542" in ph["getter_readback"]["ap_aqm_and_aql"]
        assert "VO\t300\t\t600" in ph["getter_readback"]["ap_aqm_and_aql"]
        assert "RW fq_limit 1024" in ph["getter_readback"]["loco_aqm"]
        assert ph["mac80211_txq_aqm_delta"]["tid0_ac2"]["tx_packets_delta"] > 15000
        assert ph["mac80211_txq_aqm_delta"]["tid4_ac1"]["tx_packets_delta"] > 2500
        assert ph["mac80211_txq_aqm_delta"]["tid6_ac0"]["tx_packets_delta"] > 500


def test_stage37a_champion_v11_overlay_registered_in_ledger() -> None:
    prof = get_stage37a_champion_v11_profile()
    assert prof == STAGE37A_CHAMPION_V11_OVERLAY
    assert "S37A-R2" in prof["validated_rounds"]
    ap_cmds = "\n".join(prof["ap_extra_apply_commands"])
    cpe_cmds = "\n".join(prof["cpe_extra_apply_commands"])
    assert "fq_limit 2048" in ap_cmds
    assert "fq_quantum 4542" in ap_cmds
    assert "0 300 600" in ap_cmds
    assert "udp dport 5203 ip dscp set ef" in ap_cmds
    assert "fq_limit 1024" in cpe_cmds

    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    assert "stage37a_champion_v11" in ledger
    assert ledger["stage37a_champion_v11"]["champion_version"].startswith("Stage 37A Champion v11")
