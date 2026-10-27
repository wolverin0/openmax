"""Stage 73A tests for PowerBeam 5AC Gen2 combined `ptp_xmit=1` + `daprot=2` + `ff_mcast_airtime_limit=5` (`Champion v6`) & `noack_mode=0` sweep."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage73a_pbe5ac_champion_v6_ptp_xmit_daprot2_20261026.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE73A_PBE5AC_COMBINED_PTP_XMIT1_DAPROT2_CHAMPION_V6.md"


def test_stage73a_combined_ptp_xmit1_daprot2_champion_v6_artifact_and_doc() -> None:
    """Verify Stage 73A counterbalanced hardware benchmark artifact, write-order audit, ClosedLoopResearchReactor, and doc."""
    assert ARTIFACT_PATH.exists(), f"Missing Stage 73A artifact: {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 73A"
    assert data["ticket"] == "T-S73A-PBE5AC-COMBINED-PTP-XMIT1-AND-DAPROT2-CHAMPION-V6-BENCH"

    wo = data["write_order_audit"]
    assert "===BEFORE_FF_MCAST===" in wo["ap_241_write_order_audit"]
    assert "===AFTER_FF_MCAST_LAST===" in wo["ap_241_write_order_audit"]
    assert "===AFTER_SCALARS_REAPPLIED===" in wo["ap_241_write_order_audit"]
    assert wo["ptp_xmit_1_verified"] is True
    assert isinstance(wo["daprot_2_verified"], bool)
    assert isinstance(wo["noack_mode_0_verified"], bool)
    assert wo["ff_mcast_5_verified"] is True

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {"S73A-R1", "S73A-R2"}

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

    assert DOC_PATH.exists(), f"Missing Stage 73A doc: {DOC_PATH}"
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 250, f"Doc exceeds 250 lines ({len(doc_lines)})"
    assert doc_lines[0].startswith("<!-- doc-head:")
