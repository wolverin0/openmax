"""Stage 80B tests for PowerBeam 5AC Gen2 `Stage 79A Champion v7` Packager Merge, `ATHDEV-BUG-02` `CABlevel=15` + `tcp_notsent_lowat=16384` & `Burst:4500` Fine-Grid Benchmark."""

from __future__ import annotations

import json
from pathlib import Path

from tools.deploy.guarida_stage29b_deploy_packager import (
    STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4,
    STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5,
    STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6,
    STAGE79A_AIROS8_PTP_CHAMPION_V7_COMMANDS,
    STAGE79A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V7,
    build_guarida_stage29b_and_stage48b_deploy_bundle,
    build_stage66a_curated_all_champions_deploy_package,
    render_stage79a_airos8_ptp_champion_v7_script,
    validate_stage66a_all_curated_champions_guard,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage80b_pbe5ac_champion_v7_merge_and_cablevel_20261026.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE80B_PBE5AC_CHAMPION_V7_MERGE_AND_CABLEVEL_BENCHMARK.md"


def test_stage80b_champion_v7_packager_merge_and_v4_v5_v6_compatibility() -> None:
    """Verify Stage 79A Champion v7 is merged into central deploy packager while preserving v4, v5, and v6 aliases."""
    assert STAGE79A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V7["champion_id"] == "STAGE79A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V7"
    assert STAGE79A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V7["profile_id"] == "S79A-R1-PTP-CHAMPION-V7"
    assert (
        STAGE79A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V7["supersedes_profile_id"]
        == "STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6"
    )
    assert STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6["champion_id"] == "STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6"
    assert STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5["champion_id"] == "STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5"
    assert STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4["champion_id"] == "STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4"

    v7_params = STAGE79A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V7["stage79a_r1_multiq3_and_burst5000_parameters"]
    assert v7_params["ath0_set_multiq"] == 3
    assert v7_params["umac_bug01_deep_vlan_pppoe_dscp_and_75pct_xoff"] is True
    assert v7_params["uph_wifi0_timing"] == "200 200 5000"
    assert v7_params["burst_dur_us"] == 5000

    script_v7 = render_stage79a_airos8_ptp_champion_v7_script()
    assert "iwpriv ath0 set_multiq 3" in script_v7
    assert "echo '200 200 5000' > /proc/sys/dev/uph_wifi0/timing" in script_v7
    assert "echo 1 > /proc/sys/dev/uph_wifi0/ptp_xmit" in script_v7
    assert "echo 2 > /proc/sys/dev/uph_wifi0/daprot" in script_v7
    assert "echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit" in script_v7
    assert "cron.status=enabled" in script_v7
    assert len(STAGE79A_AIROS8_PTP_CHAMPION_V7_COMMANDS) >= 32

    guard = validate_stage66a_all_curated_champions_guard()
    assert guard["valid"] is True
    assert guard["stage79a_airos8_ptp_v7_verified"] is True

    pkg = build_stage66a_curated_all_champions_deploy_package()
    assert "stage79a_pbe5ac_lbe5ac_airos8_ptp_champion_v7" in pkg
    assert "stage79a_airos8_ptp_v7_script_sha256" in pkg["scripts"]

    bundle = build_guarida_stage29b_and_stage48b_deploy_bundle()
    assert "stage79a_pbe5ac_lbe5ac_airos8_ptp_champion_v7" in bundle
    assert bundle["safety_invariants_verified"]["all_safety_checks_passed"] is True


def test_stage80b_cablevel_and_burst4500_benchmark_artifact_and_doc() -> None:
    """Verify Stage 80B counterbalanced hardware benchmark artifact, silicon audit, and doc."""
    assert ARTIFACT_PATH.exists(), f"Missing Stage 80B artifact: {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 80B"
    assert data["ticket"] == "T-S80B-PROMOTE-PBE5AC-CHAMPION-V7-AND-ATHDEV-CABLEVEL-BENCH"

    audit = data["silicon_audit"]
    assert "Down:200, Up:200, Burst:4500" in audit["ap_241_audit"]
    assert audit["cab_minfree_48_and_ol_ath_boundary_verified"] is True
    assert audit["burst_4500_dmesg_verified"] is True
    assert audit["champion_v7_burst_5000_restored"] is True

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {"S80B-R1", "S80B-R2"}

    for rid, r in rounds.items():
        assert len(r["arm_a_windows"]) == 2, f"{rid} must have 2 Arm A windows"
        assert len(r["arm_b_windows"]) == 2, f"{rid} must have 2 Arm B windows"
        assert r["arm_a_summary"]["aggregate_goodput_mbps"] > 5.0
        assert r["arm_b_summary"]["aggregate_goodput_mbps"] > 5.0
        assert r["verdict"] in ("KEEP", "DISCARD")
        assert "closed_loop_reactor_followup" in r
        assert "followup_scholar_queries" in r["closed_loop_reactor_followup"]

    assert "CFGMTD_OK" in data["persistence"]["ap_241_cfgmtd"]
    assert "CFGMTD_OK" in data["persistence"]["sta_242_cfgmtd"]

    assert DOC_PATH.exists(), f"Missing Stage 80B doc: {DOC_PATH}"
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220, f"Doc exceeds 220 lines ({len(doc_lines)})"
    assert doc_lines[0].startswith("<!-- doc-head:")
