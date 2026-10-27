"""Stage 77B tests for PowerBeam 5AC Gen2 Fast Turnaround TDMA Timing (`200 200 4000`) & Pure Symmetric `ATPC` (`1 -62 24 24 24` without `swr_limit`)."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage77b_pbe5ac_fast_turnaround_and_pure_atpc_20261026.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE77B_PBE5AC_FAST_TURNAROUND_200_200_4000_AND_PURE_ATPC.md"


def test_stage77b_silicon_audit_and_counterbalanced_benchmark() -> None:
    """Verify Stage 77B live silicon dmesg audit (Down:200, Up:200, Burst:4000 and pure ATPC) and 8-window benchmark."""
    assert ARTIFACT_PATH.exists(), f"Missing Stage 77B artifact: {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 77B"
    assert data["ticket"] == "T-S77B-PBE5AC-FAST-TURNAROUND-200-200-4000-AND-PURE-ATPC-BENCH"

    audit = data["silicon_audit"]
    assert "Down:200, Up:200, Burst:4000" in audit["ap_241_dmesg_audit"]
    assert "ATPC enabled (-62/24/24/24)" in audit["ap_241_dmesg_audit"]
    assert audit["fast_turnaround_200_200_4000_verified"] is True
    assert audit["pure_symmetric_atpc_24_verified"] is True
    assert audit["default_200_200_6000_restored"] is True

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {"S77B-R1", "S77B-R2"}

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

    assert DOC_PATH.exists(), f"Missing Stage 77B doc: {DOC_PATH}"
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220, f"Doc exceeds 220 lines ({len(doc_lines)})"
    assert doc_lines[0].startswith("<!-- doc-head:")
