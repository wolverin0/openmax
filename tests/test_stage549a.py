"""Tests for Stage 549A: PBE-5AC-Gen2 & LBE-5AC-Gen2 PtP/PtMP Unified Field Installer v3."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER_SH_PATH = REPO_ROOT / "firmware" / "openwrt" / "common" / "fmx_pbe5ac_lbe5ac_field_installer_v3.sh"
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage549a_pbe5ac_lbe5ac_ptp_ptmp_unified_field_installer_v3.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE549A_PBE5AC_LBE5AC_PTP_PTMP_UNIFIED_FIELD_INSTALLER_V3.md"


def test_stage549a_installer_lf_and_caldata_check():
    assert INSTALLER_SH_PATH.exists()
    raw = INSTALLER_SH_PATH.read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    for part in ("mtd0", "mtd1", "mtd5"):
        assert part in text
    assert "htt_max_amsdu_ampdu" in text
    assert "rollback" in text


def test_stage549a_receipt_boards_and_safety():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "549A"
    boards = {b["board_id"]: b for b in data["supported_boards"]}
    assert "0xe3e5" in boards and "0xe4e5" in boards
    assert boards["0xe3e5"]["verified_vht40_goodput_mbps"] == 24.83
    assert data["safety_boundaries"]["protected_partitions_never_modified"] == ["mtd0", "mtd1", "mtd5"]
    assert "five_pillar_compliance" in data


def test_stage549a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
