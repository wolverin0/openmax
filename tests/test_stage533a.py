from __future__ import annotations

import json
from pathlib import Path

from tools.re.dissect_stage533a_ubnt_poll_swr_limit_and_slot_guard_re import (
    build_stage533a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage533a_ubnt_poll_swr_limit_and_slot_guard_re.json"
)
DOC_PATH = REPO_ROOT / "docs" / "STAGE533A_UBNT_POLL_SWR_LIMIT_AND_SLOT_GUARD_RE.md"


def test_stage533a_swr_limit_and_slot_guard_re() -> None:
    assert ARTIFACT_PATH.exists()
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    live = build_stage533a_report()
    assert data["stage"] == "533A"
    assert data["writes_performed"] == 0
    assert data["binary_re_dissection"] == live["binary_re_dissection"]
    rtt_re = data["binary_re_dissection"]["ubnt_poll_host_set_node_rtt"]
    assert rtt_re["distance_formula_m"] == "distance_m = 150 * rtt_us"
    assert rtt_re["slot_guard_formula_us"] == "slot_guard_us = rtt_us + 21 (0x15)"
    assert data["guarida_sector_timing_comparison"]["panel2_82_fixed_10ms_67_33"]["guard_share_of_ul_slice_pct"] == 26.0


def test_stage533a_5pillar_and_doc_budget() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True, audit
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
