"""Stage 74A tests for PowerBeam 5AC Gen2 `UPH-BUG-05` (`atpc` `vec[2]/vec[3]` Inversion), `Champion v6` Packager Merge & Symmetric TDMA Timing Sweep."""

from __future__ import annotations

import json
from pathlib import Path

from tools.deploy.guarida_stage29b_deploy_packager import (
    STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4,
    STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5,
    STAGE73A_AIROS8_PTP_CHAMPION_V6_COMMANDS,
    STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6,
    build_guarida_stage29b_and_stage48b_deploy_bundle,
    build_stage66a_curated_all_champions_deploy_package,
    render_stage73a_airos8_ptp_champion_v6_script,
    validate_stage66a_all_curated_champions_guard,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage74a_pbe5ac_uph_bug05_atpc_and_timing_20261026.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE74A_PBE5AC_UPH_BUG05_ATPC_AND_CHAMPION_V6_MERGE.md"


def test_stage74a_champion_v6_packager_merge_and_v4_v5_compatibility() -> None:
    """Verify Stage 73A Champion v6 is merged into central deploy packager while preserving v4 and v5 aliases."""
    assert STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6["champion_id"] == "STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6"
    assert STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6["profile_id"] == "S73A-R1-PTP-CHAMPION-V6"
    assert (
        STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6["supersedes_profile_id"]
        == "STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5"
    )
    assert STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5["champion_id"] == "STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5"
    assert STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4["champion_id"] == "STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4"

    uph_params = STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6[
        "stage73a_r1_uph_wifi0_ptp_xmit_daprot_and_mcast_parameters"
    ]
    assert uph_params["uph_wifi0_ptp_xmit"] == 1
    assert uph_params["uph_wifi0_daprot"] == 2
    assert uph_params["uph_wifi0_ff_mcast_airtime_limit"] == 5
    assert uph_params["ff_mcast_written_last_fmx_disc_11"] is True

    script_v6 = render_stage73a_airos8_ptp_champion_v6_script()
    assert "echo 1 > /proc/sys/dev/uph_wifi0/ptp_xmit" in script_v6
    assert "echo 2 > /proc/sys/dev/uph_wifi0/daprot" in script_v6
    assert "echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit" in script_v6
    assert "cron.status=enabled" in script_v6
    assert len(STAGE73A_AIROS8_PTP_CHAMPION_V6_COMMANDS) >= 30

    guard = validate_stage66a_all_curated_champions_guard()
    assert guard["valid"] is True
    assert guard["stage73a_airos8_ptp_v6_verified"] is True

    pkg = build_stage66a_curated_all_champions_deploy_package()
    assert "stage73a_pbe5ac_lbe5ac_airos8_ptp_champion_v6" in pkg
    assert "stage73a_airos8_ptp_v6_script_sha256" in pkg["scripts"]

    bundle = build_guarida_stage29b_and_stage48b_deploy_bundle()
    assert "stage73a_pbe5ac_lbe5ac_airos8_ptp_champion_v6" in bundle
    assert bundle["safety_invariants_verified"]["all_safety_checks_passed"] is True


def test_stage74a_uph_bug05_atpc_and_timing_benchmark_artifact_and_doc() -> None:
    """Verify Stage 74A counterbalanced hardware benchmark artifact, UPH-BUG-05 silicon audit, and doc."""
    assert ARTIFACT_PATH.exists(), f"Missing Stage 74A artifact: {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 74A"
    assert data["ticket"] == "T-S74A-PBE5AC-UPH-BUG05-ATPC-INVERSION-AND-CHAMPION-V6-PACKAGER-MERGE"

    audit = data["uph_bug05_and_timing_silicon_audit"]
    assert "ATPC enabled (-62/10/24/24)" in audit["ap_241_dmesg_audit"]
    assert "ATPC enabled (-62/24/24/24)" in audit["ap_241_dmesg_audit"]
    assert "Timing params set to Down:2000, Up:2000, Burst:1000" in audit["ap_241_dmesg_audit"]
    assert "ATPC disabled (0/0/0/24)" in audit["ap_241_dmesg_audit"]
    assert audit["uph_bug05_asymmetric_10_24_observed"] is True
    assert audit["symmetric_24_24_lock_verified"] is True
    assert audit["default_24dbm_restored"] is True

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {"S74A-R1", "S74A-R2"}

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

    assert DOC_PATH.exists(), f"Missing Stage 74A doc: {DOC_PATH}"
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 250, f"Doc exceeds 250 lines ({len(doc_lines)})"
    assert doc_lines[0].startswith("<!-- doc-head:")
