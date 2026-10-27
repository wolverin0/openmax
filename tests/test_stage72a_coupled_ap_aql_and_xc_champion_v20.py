from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage72a_coupled_ap_aql_and_xc_champion_v20 import (
    OUT_JSON,
    STAGE72A_AP_CANDIDATE_COMMANDS,
    STAGE72A_R3_XC_CANDIDATE_COMMANDS,
    STAGE72A_XC_CANDIDATE_COMMANDS,
)


def test_stage72a_coupled_ap_aql_and_xc_commands_preserve_safety_and_disc11() -> None:
    """
    Verify Stage 72A commands preserve 64MB AR9342 guards, PtMP AMPDUFrames=24 & swretry=4/4,
    and FMX-DISC-11 16-int vector rule (ff_mcast_airtime_limit=5 written last).
    """
    ap_cmds = "\n".join(STAGE72A_AP_CANDIDATE_COMMANDS)
    assert "echo '2 1350 2700' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit" in ap_cmds
    assert "echo 2000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold" in ap_cmds
    assert "oom_score_adj" in ap_cmds
    assert "fq_memory_limit 4194304" in ap_cmds
    assert "tx_queue_len" in ap_cmds
    assert "hold_time" in ap_cmds

    for xc_list in (STAGE72A_XC_CANDIDATE_COMMANDS, STAGE72A_R3_XC_CANDIDATE_COMMANDS):
        xc_cmds = "\n".join(xc_list)
        assert "iwpriv ath0 set_multiq 1" in xc_cmds
        assert "iwpriv wifi0 AMPDUFrames 24" in xc_cmds
        assert "iwpriv wifi0 aggr_swretry 4" in xc_cmds
        assert "iwpriv wifi0 nonaggr_swretry 4" in xc_cmds
        assert "enable_tx_tcp_cksum" in xc_cmds
        assert "net.core.netdev_budget=800" in xc_cmds
        assert "echo 2 > /proc/sys/dev/uph_wifi0/daprot" in xc_cmds
        assert "echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit" in xc_cmds
        assert xc_cmds.index("daprot") < xc_cmds.index("ff_mcast_airtime_limit")


def test_stage72a_four_counterbalanced_rounds_and_promoted_champion_v20() -> None:
    assert OUT_JSON.exists(), f"Missing Stage 72A receipt: {OUT_JSON}"
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "72A"
    assert data["task_id"] == "T-S72A-COUPLED-AP-ACBE-AQL-WITH-S70C-STRICT-CHAMPION-V20-BENCH"
    assert data["safety_invariants"]["flash_writes"] == 0
    assert data["safety_invariants"]["auto_rollback_watchdog_timeout_s"] == 45
    assert data["safety_invariants"]["xc_ampdu_frames_fixed"] == 24

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {
        "S72A-COUPLED-AP-AQL-XC-V20",
        "S72A-R2-AP-AQL-1500-3000-THR-4500-XC-V20",
        "S72A-R3-WARMED-PACED-AP-V19-XC-MULTIQ-CKSUM-BUDGET800-TSQ98304",
        "S72A-R4-WARMED-AP-V19-XC-S70C-CHAMPION-V20",
    }

    for rid, r in rounds.items():
        assert list(r["phases"].keys()) == ["A1", "B1", "A2", "B2"], f"{rid} missing windows"

    # Verify R1 getter readback (AP AC_BE=1350/2700 thr=2000)
    rb_r1_b1 = rounds["S72A-COUPLED-AP-AQL-XC-V20"]["phases"]["B1"]["getter_readback"]
    assert rb_r1_b1["ap_aql_txq_limit"]["BE"] == {"low_us": 1350, "high_us": 2700}
    assert rb_r1_b1["ap_aql_threshold"] == 2000

    # Verify R4 promoted Champion v20
    r4 = rounds["S72A-R4-WARMED-AP-V19-XC-S70C-CHAMPION-V20"]
    assert r4["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r4["promoted"] is True
    assert r4["goodput_delta_pct"] > 0.0
    assert r4["p95_rtt_delta_pct"] < 0.0
    assert r4["pareto_score_delta_pct"] > 8.0

    rb_r4_b1 = r4["phases"]["B1"]["getter_readback"]
    assert rb_r4_b1["ap_aql_txq_limit"]["BE"] == {"low_us": 1500, "high_us": 3000}
    assert rb_r4_b1["ap_aql_threshold"] == 5000
    assert rb_r4_b1["xc_extended_readback"]["tx_tcp_cksum"] == 1
    assert rb_r4_b1["xc_extended_readback"]["netdev_budget"] == 800
    assert rb_r4_b1["xc_extended_readback"]["daprot"] == 2
    assert rb_r4_b1["xc_extended_readback"]["ff_mcast_airtime_limit"] == 5

    mids = [m["mechanism_id"] for m in data["closed_loop_reactor_event"]["synthesized_next_mechanisms"]]
    assert "M41" in mids

    doc_path = Path(__file__).resolve().parents[1] / "docs" / "STAGE72A_COUPLED_AP_AQL_AND_XC_CHAMPION_V20_BENCHMARK.md"
    assert doc_path.exists()
    lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("<!-- doc-head:")
    assert len(lines) < 250
