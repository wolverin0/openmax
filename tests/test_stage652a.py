#!/usr/bin/env python3
"""Tests for Stage 652A: XW M5 ath_dev.ko + ubnt_poll.ko vs WA/XC Mixed-Mode TDMA Translator RE."""
from __future__ import annotations

from tools.re.dissect_stage652a_xw_ath_dev_mixed_mode_tdma_translator_re import (
    OUT_JSON,
    ROOT,
    build_stage652a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


def test_stage652a_xw_ath_dev_mixed_mode_tdma_translator_re() -> None:
    rep = build_stage652a_report()
    assert OUT_JSON.exists()
    assert rep["stage"] == "652A"
    assert rep["status"] == "PASS"
    assert rep["claim_label"] == "CONFIRMED"
    assert rep["live_devices_touched"] is False
    assert audit_stage_receipt_5pillars(rep)["compliant"] is True

    xw_builds = rep["xw_builds_dissected"]
    assert len(xw_builds) == 2
    for b in xw_builds:
        assert b["ubnt_poll_ko"]["ht40_aggr_len_table"]["values_u32"] == [
            12,
            60156,
            22,
            120240,
        ]
        assert b["ubnt_poll_ko"]["ht20_aggr_len_table"]["values_u32"] == [
            12,
            19304,
            20,
            38600,
        ]
        assert b["ubnt_poll_ko"]["mixed_mode_11ac_and_hybrid_symbol_count"] >= 50
        assert b["ath_dev_ko"]["ath_pkt_duration"]["size_bytes"] in (240, 284)
        assert b["ath_dev_ko"]["ath_pkt_duration_to_len"]["size_bytes"] in (196, 220)

    ac_builds = rep["ac_host_builds_dissected"]
    assert len(ac_builds) == 2
    for ac in ac_builds:
        assert ac["total_symbols"] == 358

    doc_path = (
        ROOT / "docs" / "STAGE652A_XW_ATH_DEV_MIXED_MODE_TDMA_TRANSLATOR_RE.md"
    )
    assert doc_path.exists()
    lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
