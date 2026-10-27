#!/usr/bin/env python3
"""Tests for Stage 417A — ubnt_poll_host.ko cbp_dur & AssocReq Vendor IE Hash Dissection."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage417a_ubnt_poll_cbp_dur_and_probereq_hash_re.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE417A_UBNT_POLL_CBP_DUR_AND_PROBEREQ_HASH_RE.md"


def test_stage417a_json_receipt() -> None:
    assert JSON_PATH.exists(), f"Missing {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "417A"
    assert data["status"] == "COMPLETED"
    assert data["claim_status"] == "CONFIRMED"
    assert data["writes_performed"] == 0

    funcs = data["binary_re_provenance"]["dissected_functions"]
    assert funcs["ubnt_poll_host_on_probe_req_rx"]["text_offset_hex"] == "0x00910c"
    assert funcs["ubnt_poll_host_on_assoc_req_rx"]["text_offset_hex"] == "0x009594"
    assert "0x009c8c" in funcs["ubnt_poll_host_on_assoc_req_rx"]["sta_hash_table_populate_call"]
    assert funcs["ubnt_poll_ht_comm_parse"]["text_offset_hex"] == "0x014894"
    assert "0x0220($s0)" in funcs["ubnt_poll_ht_comm_parse"]["defer_timeout_ms_write"]

    comp = data["cbp_dur_panel2_vs_panel3_comparison"]
    assert comp["panel2_82"]["cbp_dur_us"] == 180
    assert comp["panel3_83"]["cbp_dur_us"] == 900
    assert comp["panel2_82"]["flags_hex"] == "0x3a10"


def test_stage417a_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"Doc has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1
