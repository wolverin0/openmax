"""Stage 72B tests for PowerBeam 5AC Gen2 isolated `/proc/sys/dev/uph_wifi0/{daprot,ff_mcast_airtime_limit,ptp_xmit}` sweep."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage72b_pbe5ac_uph_ptp_xmit_and_daprot2_20261026.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE72B_PBE5AC_UPH_PTP_XMIT_AND_DAPROT2_BENCHMARK.md"


def test_stage72b_uph_ptp_xmit_and_daprot2_isolated_benchmark_artifact_and_doc() -> None:
    """Verify Stage 72B counterbalanced hardware benchmark artifact, readback audit, ClosedLoopResearchReactor, and doc."""
    assert ARTIFACT_PATH.exists(), f"Missing Stage 72B artifact: {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 72B"
    assert data["ticket"] == "T-S72B-PBE5AC-UPH-PTP-XMIT-AND-DAPROT2-ISOLATED-BENCH"

    rb = data["readback_audit"]
    assert "===PRE===" in rb["ap_241_readback"]
    assert "===POST_WRITE===" in rb["ap_241_readback"]
    assert isinstance(rb["daprot_2_accepted"], bool)
    assert isinstance(rb["ptp_xmit_1_accepted"], bool)
    assert isinstance(rb["ff_mcast_airtime_5_accepted"], bool)

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {"S72B-R1", "S72B-R2"}

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

    assert DOC_PATH.exists(), f"Missing Stage 72B doc: {DOC_PATH}"
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 250, f"Doc exceeds 250 lines ({len(doc_lines)})"
    assert doc_lines[0].startswith("<!-- doc-head:")
