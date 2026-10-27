#!/usr/bin/env python3
"""Tests for Stage 455A — ubnt_poll UL Slot Starvation, Requeue, and Excess-Retry Dissection."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage455a_ubnt_poll_UL_slot_starvation_and_requeue_re.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE455A_UBNT_POLL_UL_SLOT_STARVATION_AND_REQUEUE_RE.md"


def test_stage455a_json_receipt() -> None:
    assert JSON_PATH.exists(), f"Missing {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "455A"
    assert data["status"] == "COMPLETED"
    assert data["claim_status"] == "CONFIRMED"
    assert data["writes_performed"] == 0

    mechs = data["binary_re_provenance"]["dissected_mechanisms"]
    assert mechs["wal_dbg_stats_copy_path"]["text_offset_hex"] == "0x0b5dbc"
    assert mechs["target_tdma_slot_expiry_requeue"]["tx_bd_exchange_handler_va"] == "0x0099b8d4"
    assert "0x00b404" in mechs["csma_hybrid_excess_retry_drop"]["swr_limit_handler"]

    mat = data["panel2_vs_panel3_requeue_and_retry_matrix"]
    assert mat["panel2_82"]["mpdus_requed"] == 139751148
    assert mat["panel2_82"]["excess_retries"] == 23
    assert mat["panel3_83"]["excess_retries"] == 9522084


def test_stage455a_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"Doc has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1
