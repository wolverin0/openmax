"""Pytest verification suite for Stage 25 (`T-S25-SCHOLAR-MCP-HYPERRESEARCH-FUSION-AND-M3-M5-BENCH`)."""
from __future__ import annotations

import json
from pathlib import Path

from controller.multiradio_golden_profile_applicator import (
    GOLDEN_PROFILES,
    render_shell_script,
    validate_profile_safety,
)
from tools.bench.run_stage25_m3_txq_codel_and_m5_ack_pacing_bench import (
    LBM5_CHAMPION_APPLY,
    S25_R1_CONTROL_CMD,
    S25_R1_TREATMENT_CMD,
    S25_R2_CONTROL_CMD,
    S25_R2_TREATMENT_CMD,
    STAGE24E_CHAMPION_V5_EXTRAS,
    parse_ping_metrics,
    parse_station_dump,
    summarize_abab,
)
from tools.research.run_scholar_mcp_hyperresearch_fusion import (
    FUSION_RECEIPT_JSON,
    SCHOLAR_JEV_VERIFIED_PAPERS,
)

ROOT = Path(__file__).resolve().parents[1]
BENCH_RECEIPT_PATH = ROOT / "artifacts/autoresearch/stage25_scholar_fusion_and_m3_m5_bench_20261025.json"
REPORT_PATH = ROOT / "docs/STAGE25_SCHOLAR_HYPERRESEARCH_FUSION_AND_M3_M5_BENCHMARK.md"
LEDGER_PATH = ROOT / "artifacts/autoresearch/champion_state_ledger.json"


def test_stage25_scholar_hyperresearch_fusion_receipt():
    assert FUSION_RECEIPT_JSON.exists(), f"Missing fusion receipt: {FUSION_RECEIPT_JSON}"
    data = json.loads(FUSION_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert data["task_id"] == "T-S25-SCHOLAR-MCP-HYPERRESEARCH-FUSION-AND-M3-M5-BENCH"
    assert len(data["ingested_scholar_papers"]) == len(SCHOLAR_JEV_VERIFIED_PAPERS) == 2

    paper_ids = {p["paper_id"] for p in data["ingested_scholar_papers"]}
    assert paper_ids == {"1703.00064v2", "0806.1089v1"}
    for p in data["ingested_scholar_papers"]:
        assert p["verification_probability"] == 0.97
        assert p["model_version"] == "jev-1.14.0"
        assert p["exact_span"]["end_char"] > p["exact_span"]["start_char"]
        src_path = ROOT / p["source_file"]
        assert src_path.exists(), f"Missing ingested source file: {src_path}"

    claims_bundle = ROOT / data["claims_bundle_file"]
    assert claims_bundle.exists()
    assert data["vault_status_after_fusion"]["notes"]["total"] >= 22


def test_stage25_safety_and_champion_v6_profiles():
    for pid in ("openwrt_lap120_ptp_1cpe_champion", "openwrt_lap120_ptmp_multicpe_champion", "r5ac_prism_sta"):
        assert pid in GOLDEN_PROFILES
        assert validate_profile_safety(GOLDEN_PROFILES[pid]) is True
        s = render_shell_script(pid, mode="apply")
        assert "cfgmtd" not in s
        assert "uci commit" not in s

    ptp_apply = render_shell_script("openwrt_lap120_ptp_1cpe_champion", mode="apply")
    ptmp_apply = render_shell_script("openwrt_lap120_ptmp_multicpe_champion", mode="apply")
    assert "tcp_thin_linear_timeouts=1" in ptp_apply
    assert "tcp_autocorking=0" in ptp_apply
    assert "tcp_thin_linear_timeouts=1" in ptmp_apply
    assert "echo '0 600 1200'" in ptmp_apply

    for script in (
        LBM5_CHAMPION_APPLY,
        STAGE24E_CHAMPION_V5_EXTRAS,
        S25_R1_CONTROL_CMD,
        S25_R1_TREATMENT_CMD,
        S25_R2_CONTROL_CMD,
        S25_R2_TREATMENT_CMD,
    ):
        assert "cfgmtd" not in script
        assert "uci commit" not in script
        assert "mtd " not in script


def test_stage25_physical_bench_receipt_and_ram_state():
    assert BENCH_RECEIPT_PATH.exists(), f"Missing Stage 25 bench receipt: {BENCH_RECEIPT_PATH}"
    data = json.loads(BENCH_RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["status"] == "PASS_STAGE25_SCHOLAR_FUSION_AND_M3_M5_COMPLETE"
    assert data["rounds"]["S25-R1"]["decision"] == "RETAIN_CURRENT_CHAMPION"
    assert data["rounds"]["S25-R2"]["decision"] == "KEEP_NEW_CHAMPION"

    for r_id in ("S25-R1", "S25-R2"):
        for phase in ("A1", "B1", "A2", "B2"):
            assert phase in data["rounds"][r_id]["phases"]

    ram = data["final_ram_state"]
    assert ram["persistent_flash_writes"] is False
    assert ram["lap120_and_loco5ac_profile"] == "openwrt_lap120_ptp_1cpe_champion_v6"
    assert "tcp_thin_linear_timeouts = 1" in ram["lap120_verify"]
    assert "tcp_autocorking = 0" in ram["lap120_verify"]
    assert "tcp_thin_linear_timeouts = 1" in ram["loco5ac_verify"]
    assert "get_ani_enable:0" in ram["r5ac_prism_sta_verify"]
    assert "getAMPDUFrames:24" in ram["lbm5_xw_sta_verify"]
    assert LEDGER_PATH.exists()
    assert REPORT_PATH.exists()
