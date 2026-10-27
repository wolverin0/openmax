"""
Unit and physical receipt verification tests for Stage 36A
(`T-S36A-LIVE-IPTV-AC-VI-DMS-AND-HLS-PACING-PTMP-BENCH`).
"""

from __future__ import annotations

import json
from pathlib import Path

from controller.multiradio_golden_profile_applicator import (
    STAGE36A_CHAMPION_V10_OVERLAY,
    export_champion_ledger,
    get_stage36a_champion_v10_profile,
)
from controller.openwisp_controller_api_bridge import (
    APPROVED_PROFILE_SET_SHA256,
    build_template_pack,
)
from tools.bench.run_stage36a_live_iptv_ac_vi_ptmp_bench import (
    parse_iptv_udp_output,
    parse_station_aqm_table,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_JSON = ROOT / "artifacts" / "autoresearch" / "stage36a_live_iptv_ac_vi_ptmp_bench_20261025.json"
REPORT_MD = ROOT / "docs" / "STAGE36A_LIVE_IPTV_AC_VI_AND_DMS_PTMP_BENCHMARK.md"


def test_stage36a_receipt_s36a_r1_and_s36a_r2_promotion() -> None:
    assert RECEIPT_JSON.exists(), f"Missing Stage 36A receipt: {RECEIPT_JSON}"
    data = json.loads(RECEIPT_JSON.read_text(encoding="utf-8"))
    assert data["task_id"] == "T-S36A-LIVE-IPTV-AC-VI-DMS-AND-HLS-PACING-PTMP-BENCH"
    assert data["flash_writes"] == 0

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert "S36A-R1" in rounds
    assert "S36A-R2" in rounds

    # S36A-R1 preserved failed/refuted attempt (squeezing AC_BE to 1000/2000 cut p95 -13.35% but lost -6.225% goodput)
    r1 = rounds["S36A-R1"]
    assert r1["mechanism_id"] == "M16_IPTV_AC_VI"
    assert r1["decision"] == "RETAIN_CURRENT_CHAMPION"
    assert r1["p95_rtt_delta_pct"] < -10.0
    assert r1["iptv_arm_b_mean_loss_pct"] == 0.0
    assert set(r1["phases"].keys()) == {"A1", "B1", "A2", "B2"}

    # S36A-R2 promoted Stage 36A Champion v10 (keeping AC_BE=1500/3000 + WMM AC_VI + direct mac80211 aqm fq_quantum=3028/1514)
    r2 = rounds["S36A-R2"]
    assert r2["mechanism_id"] == "M16b_IPTV_AC_VI_MAC80211_AQM"
    assert r2["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r2["promoted"] is True
    assert r2["claim_status"] == "CONFIRMED"
    assert r2["goodput_delta_pct"] > 2.0
    assert r2["p95_rtt_delta_pct"] < -3.0
    assert r2["iptv_arm_b_mean_loss_pct"] == 0.0
    assert r2["iptv_arm_b_mean_bitrate_mbps"] >= 3.45

    # Verify per-TID mac80211 TXQ isolation in B1 and B2 (TID 4 AC 1 carries ~1,990 IPTV packets with 0 drops)
    for b_phase in ("B1", "B2"):
        aqm_d = r2["phases"][b_phase]["mac80211_txq_aqm_delta"]
        assert aqm_d["tid4_ac1"]["tx_packets_delta"] >= 1980
        assert aqm_d["tid4_ac1"]["drops_delta"] == 0
        assert "RW fq_quantum 3028" in r2["phases"][b_phase]["getter_readback"]["ap_aqm_and_aql"]
        assert "RW fq_quantum 1514" in r2["phases"][b_phase]["getter_readback"]["loco_aqm"]


def test_stage36a_champion_v10_overlay_and_openwisp_pack_compatibility() -> None:
    v10 = get_stage36a_champion_v10_profile()
    assert v10 == STAGE36A_CHAMPION_V10_OVERLAY
    assert "Stage 36A Champion v10" in str(v10["champion_version"])
    assert "S36A-R2" in v10["validated_rounds"]

    ledger = export_champion_ledger()
    assert "stage36a_champion_v10" in ledger
    pack = build_template_pack()
    assert pack["manifest"]["profile_set_sha256"] == APPROVED_PROFILE_SET_SHA256


def test_stage36a_parsers_and_markdown_report() -> None:
    sample_iperf = "[  5]   0.00-6.02   sec  2.50 MBytes  3.48 Mbits/sec  1.814 ms  0/1993 (0%)  receiver\n"
    parsed = parse_iptv_udp_output(sample_iperf)
    assert parsed["delivered_bitrate_mbps"] == 3.48
    assert parsed["jitter_ms"] == 1.814
    assert parsed["lost_datagrams"] == 0
    assert parsed["total_datagrams"] == 1993
    assert parsed["packet_loss_pct"] == 0.0

    sample_aqm = (
        "tid ac backlog-bytes backlog-packets new-flows drops marks overlimit collisions tx-bytes tx-packets flags\n"
        "0 2 0 0 23944 0 0 0 0 34608992 23944 0x0(RUN)\n"
        "4 1 0 0 1993 0 0 0 0 2757000 1993 0x0(RUN)\n"
    )
    aqm = parse_station_aqm_table(sample_aqm)
    assert aqm["tid4_ac1"]["tx_packets"] == 1993
    assert aqm["tid0_ac2"]["tx_packets"] == 23944

    assert REPORT_MD.exists(), f"Missing Stage 36A report: {REPORT_MD}"
    text = REPORT_MD.read_text(encoding="utf-8")
    for token in (
        "S36A-R1",
        "S36A-R2",
        "M16b_IPTV_AC_VI_MAC80211_AQM",
        "Stage 36A Champion v10",
        "fq_quantum 3028",
        "tid4_ac1",
    ):
        assert token in text, f"Missing token {token} in Stage 36A report"
