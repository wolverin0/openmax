from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage70c_xc_pure_multiq_cksum_champion_v20 import (
    OUT_JSON,
    STAGE70C_XC_CANDIDATE_COMMANDS,
)


def test_stage70c_xc_pure_multiq_cksum_commands_preserve_ptmp_airtime_and_disc11() -> None:
    """
    Verify Stage 70C Champion v20 Candidate preserves PtMP AMPDUFrames=24 & swretry=4/4
    while enabling set_multiq=1, enable_tx_tcp_cksum=1, netdev_budget=800,
    tcp_limit_output_bytes=98304, and FMX-DISC-11 16-int vector-safe uph_wifi0 (written last).
    """
    xc_cmds = "\n".join(STAGE70C_XC_CANDIDATE_COMMANDS)
    assert "iwpriv ath0 set_multiq 1" in xc_cmds
    assert "iwpriv wifi0 AMPDUFrames 24" in xc_cmds
    assert "iwpriv wifi0 aggr_swretry 4" in xc_cmds
    assert "iwpriv wifi0 nonaggr_swretry 4" in xc_cmds
    assert "enable_tx_tcp_cksum" in xc_cmds
    assert "net.core.netdev_budget=800" in xc_cmds
    assert "net.ipv4.tcp_limit_output_bytes=98304" in xc_cmds
    assert "echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit" in xc_cmds
    # Verify ff_mcast_airtime_limit=5 is written after voip_bias=6 per FMX-DISC-11
    assert xc_cmds.index("voip_bias") < xc_cmds.index("ff_mcast_airtime_limit")


def test_stage70c_openwrt_64mb_ar9342_guards_present_in_readback() -> None:
    """Verify 64MB AR9342 stability guards are present on both Arm A and Arm B in live readback."""
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    invariants = data["safety_invariants"]
    assert invariants["ar9342_64mb_oom_score_adj"] == -900
    assert invariants["ar9342_64mb_fq_memory_limit_bytes"] == 4194304
    assert invariants["direct_sysfs_tx_queue_len_only"] is True
    assert invariants["uph_16int_vector_ff_mcast_written_last"] is True

    phases = data["rounds"][0]["phases"]
    for win_key in ("A1", "B1", "A2", "B2"):
        rb = phases[win_key]["getter_readback"]
        assert rb["ap_eth0_bql"]["hold_time"] == 800
        assert rb["ap_eth0_bql"]["limit_min"] == 4542
        assert rb["ap_aqm"]["fq_memory_limit"] == 4194304
        assert rb["ap_netdev_tx_queue_len"]["br-lan"] == 256


def test_stage70c_receipt_and_doc_budget() -> None:
    assert OUT_JSON.exists(), f"Missing Stage 70C receipt: {OUT_JSON}"
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "70C"
    assert data["task_id"] == "T-S70C-ISOLATED-XC-MULTIQ-CKSUM-NETDEV800-CHAMPION-V20-BENCH"
    assert data["safety_invariants"]["flash_writes"] == 0
    assert data["safety_invariants"]["auto_rollback_watchdog_timeout_s"] == 45
    assert data["safety_invariants"]["xc_ampdu_frames_fixed"] == 24

    r = data["rounds"][0]
    assert r["round_id"] == "S70C-XC-PURE-MULTIQ-CKSUM-NETDEV800"
    assert list(r["phases"].keys()) == ["A1", "B1", "A2", "B2"]
    for win_key, w in r["phases"].items():
        assert w["aggregate_goodput_mbps"] > 20.0, f"{win_key} goodput too low"
        assert w["voip_stream_ac_vo"]["packet_loss_pct"] == 0.0
        assert w["iptv_dual_stream_ac_vi"]["packet_loss_pct"] == 0.0

    # Verify FMX-DISC-11 hardware readback in B1/B2
    assert r["phases"]["B1"]["getter_readback"]["xc_extended_readback"]["tx_tcp_cksum"] == 1
    assert r["phases"]["B1"]["getter_readback"]["xc_extended_readback"]["netdev_budget"] == 800
    assert r["phases"]["B1"]["getter_readback"]["xc_extended_readback"]["daprot"] == 2
    assert r["phases"]["B1"]["getter_readback"]["xc_extended_readback"]["ff_mcast_airtime_limit"] == 5

    mids = [m["mechanism_id"] for m in data["closed_loop_reactor_event"]["synthesized_next_mechanisms"]]
    assert "M40" in mids

    doc_path = Path(__file__).resolve().parents[1] / "docs" / "STAGE70C_XC_PURE_MULTIQ_CKSUM_NETDEV800_CHAMPION_V20_BENCHMARK.md"
    assert doc_path.exists()
    lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("<!-- doc-head:")
    assert len(lines) < 250
