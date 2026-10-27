"""Tests for Stage 445A: Closed-Loop Pillar 1/3 Xtensa CCA/AGC Dynamic Threshold Stepping Daemon."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAEMON_PATH = REPO_ROOT / "firmware" / "openwrt" / "common" / "fmx_xtensa_cca_agc_daemon.sh"
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage445a_xtensa_cca_agc_dynamic_stepping_daemon.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE445A_XTENSA_CCA_AGC_DYNAMIC_STEPPING_DAEMON.md"


def test_stage445a_daemon_script_exists_and_lf():
    assert DAEMON_PATH.exists()
    raw = DAEMON_PATH.read_bytes()
    assert b"\r\n" not in raw, "Shell script must use strict LF line endings"
    text = raw.decode("utf-8")
    for thresh in ("-82", "-78", "-74", "-70"):
        assert f"={thresh}" in text
    assert "fw_stats" in text
    assert "fmx_pb021_ppdu_evm.json" in text


def test_stage445a_receipt_and_five_pillars():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "445A"
    assert data["daemon_artifact"]["stepping_ladder_dbm"] == [-82, -78, -74, -70]
    assert len(data["closed_loop_verification_traces"]) == 5
    abort_trace = data["closed_loop_verification_traces"][-1]
    assert abort_trace["selected_cca_thresh62_dbm"] == -82
    assert "safety_rollback" in abort_trace["transition_reason"]
    assert "five_pillar_compliance" in data


def test_stage445a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220
    assert text.count("<!-- doc-head:") == 1
