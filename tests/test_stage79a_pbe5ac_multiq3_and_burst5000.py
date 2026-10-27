"""Stage 79A tests for PowerBeam 5AC Gen2 `set_multiq=3` (`UMAC-BUG-01` Deep VLAN/PPPoE DSCP + 75% Per-AC XOFF) & `Burst:5000` (`200 200 5000`)."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage79a_pbe5ac_multiq3_and_burst5000_20261026.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE79A_PBE5AC_SET_MULTIQ3_AND_BURST5000_BENCHMARK.md"


def test_stage79a_silicon_audit_and_counterbalanced_benchmark() -> None:
    """Verify Stage 79A live silicon audit (get_multiq:3 and Down:200, Up:200, Burst:5000) and 8-window benchmark."""
    assert ARTIFACT_PATH.exists(), f"Missing Stage 79A artifact: {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 79A"
    assert data["ticket"] == "T-S79A-PBE5AC-SET-MULTIQ-3-DEEP-DSCP-XOFF-AND-BURST5000-BENCH"

    audit = data["silicon_audit"]
    assert "get_multiq:3" in audit["ap_241_audit"]
    assert "get_multiq:3" in audit["sta_242_audit"]
    assert "Down:200, Up:200, Burst:5000" in audit["ap_241_audit"]
    assert audit["set_multiq_3_verified"] is True
    assert audit["burst_5000_dmesg_verified"] is True
    assert audit["default_burst_6000_restored"] is True

    rounds = {r["round_id"]: r for r in data["rounds"]}
    assert set(rounds.keys()) == {"S79A-R1", "S79A-R2"}

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

    assert DOC_PATH.exists(), f"Missing Stage 79A doc: {DOC_PATH}"
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220, f"Doc exceeds 220 lines ({len(doc_lines)})"
    assert doc_lines[0].startswith("<!-- doc-head:")
