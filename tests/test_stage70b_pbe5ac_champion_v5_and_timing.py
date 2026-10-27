"""Stage 70B tests for PowerBeam 5AC Gen2 Champion v5 Packager Merge and `ath_dev` / `uph_wifi0` Timing Sweep."""

from __future__ import annotations

import json
from pathlib import Path

from tools.deploy.guarida_stage29b_deploy_packager import (
    STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4,
    STAGE68A_AIROS8_PTP_CHAMPION_V5_COMMANDS,
    STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5,
    build_guarida_stage29b_and_stage48b_deploy_bundle,
    build_stage66a_curated_all_champions_deploy_package,
    render_stage68a_airos8_ptp_champion_v5_script,
    validate_stage66a_all_curated_champions_guard,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage70b_pbe5ac_ath_dev_and_timing_sweep_20261026.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE70B_PBE5AC_CHAMPION_V5_MERGE_AND_TIMING_SWEEP.md"


def test_stage70b_champion_v5_packager_merge_and_backward_compatibility() -> None:
    """Verify Stage 68A Champion v5 is merged into central deploy packager while preserving v4 compatibility."""
    assert STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5["champion_id"] == "STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5"
    assert STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5["profile_id"] == "S68A-R2-PTP-CHAMPION-V5"
    assert (
        STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5["supersedes_profile_id"]
        == "STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4"
    )
    assert STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4["champion_id"] == "STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4"

    dma_params = STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5["stage68a_r2_dma_napi_and_tsq_pacing_parameters"]
    assert dma_params["wifi0_set_CabqMaxdur"] == 20
    assert dma_params["uph_sync_flex"] == 0
    assert dma_params["dev_weight"] == 64
    assert dma_params["netdev_max_backlog"] == 2000
    assert dma_params["tcp_limit_output_bytes"] == 131072
    assert dma_params["tcp_pacing_ca_ratio"] == 120
    assert dma_params["tcp_pacing_ss_ratio"] == 200

    script_v5 = render_stage68a_airos8_ptp_champion_v5_script()
    assert "iwpriv wifi0 set_CabqMaxdur 20" in script_v5
    assert "net.core.netdev_max_backlog=2000" in script_v5
    assert "net.ipv4.tcp_limit_output_bytes=131072" in script_v5
    assert "net.ipv4.tcp_pacing_ca_ratio=120" in script_v5
    assert "net.ipv4.tcp_pacing_ss_ratio=200" in script_v5
    assert "cron.status=enabled" in script_v5
    assert len(STAGE68A_AIROS8_PTP_CHAMPION_V5_COMMANDS) >= 25

    guard = validate_stage66a_all_curated_champions_guard()
    assert guard["valid"] is True
    assert guard["stage68a_airos8_ptp_v5_verified"] is True

    pkg = build_stage66a_curated_all_champions_deploy_package()
    assert "stage68a_pbe5ac_lbe5ac_airos8_ptp_champion_v5" in pkg
    assert "stage68a_airos8_ptp_v5_script_sha256" in pkg["scripts"]

    bundle = build_guarida_stage29b_and_stage48b_deploy_bundle()
    assert "stage68a_pbe5ac_lbe5ac_airos8_ptp_champion_v5" in bundle
    assert bundle["safety_invariants_verified"]["all_safety_checks_passed"] is True


def test_stage70b_ath_dev_and_uph_wifi0_timing_sweep_artifact_and_doc() -> None:
    """Verify Stage 70B counterbalanced hardware benchmark artifact, ClosedLoopResearchReactor integration, and doc."""
    assert ARTIFACT_PATH.exists(), f"Missing Stage 70B artifact: {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 70B"
    assert data["ticket"] == "T-S70B-PBE5AC-CHAMPION-V5-PACKAGER-MERGE-AND-DEEP-ATH-DEV-SWEEP"

    hw = data["hardware_audit"]
    assert hw["discovered_procfs_path"] == "/proc/sys/dev/uph_wifi0/"
    assert hw["stock_ath0_protmode"] == 1
    assert hw["stock_ath_dev_minfree"]["ACBEMinfree"] == 32
    assert "===ATH_DEV_PARAMS===" in hw["ap_241_audit"]
    assert "===UPH_WIFI0===" in hw["ap_241_audit"]

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {"S70B-R1", "S70B-R2"}

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

    assert DOC_PATH.exists(), f"Missing Stage 70B doc: {DOC_PATH}"
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 250, f"Doc exceeds 250 lines ({len(doc_lines)})"
    assert doc_lines[0].startswith("<!-- doc-head:")
