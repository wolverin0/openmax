#!/usr/bin/env python3
"""Tests for Stage 418A — Panel3 (.83) 674.5M local_enqued MCS 2 Storm Dissection."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage418a_panel3_local_enqued_mcs2_storm_re.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE418A_PANEL3_LOCAL_ENQUED_MCS2_STORM_RE.md"


def test_stage418a_json_receipt() -> None:
    assert JSON_PATH.exists(), f"Missing {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "418A"
    assert data["status"] == "COMPLETED"
    assert data["claim_status"] == "CONFIRMED"
    assert data["writes_performed"] == 0

    funcs = data["binary_re_provenance"]["dissected_functions"]
    assert funcs["ol_get_radio_stats"]["text_offset_hex"] == "0x000bcd40"
    assert funcs["athbox_ol_stats_printer"]["vaddr_hex"] == "0x00401930"

    comp = data["guarida_4radio_local_enqued_comparison"]
    assert comp["panel3_83"]["local_enqued"] == 674501176
    assert comp["panel3_83"]["ast_tx_mgmt"] == 674501176
    assert comp["panel3_83"]["tx_mcs2_frames"] == 669086302
    assert comp["panel3_83"]["local_enqued_share_pct"] == 78.44


def test_stage418a_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"Doc has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1
