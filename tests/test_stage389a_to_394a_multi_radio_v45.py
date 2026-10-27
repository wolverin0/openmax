#!/usr/bin/env python3
"""Consolidated verification suite for Stage 389A through Stage 394A Multi-Radio Round 9 Campaign (Champion v45.0)."""
from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage389a_to_394a_multi_radio_v45_suite() -> None:
    expected_artifacts = [
        (
            "STAGE-389A",
            "tools/benchmarks/run_stage389a_live_xc198_round9_autoresearch.py",
            "artifacts/autoresearch/stage389a_live_xc198_round9_autoresearch.json",
            "docs/STAGE389A_LIVE_XC198_ROUND9_AUTORESEARCH.md",
            "tests/test_stage389a.py",
        ),
        (
            "STAGE-390A",
            "tools/benchmarks/run_stage390a_live_2xc253_round9_autoresearch.py",
            "artifacts/autoresearch/stage390a_live_2xc253_round9_autoresearch.json",
            "docs/STAGE390A_LIVE_2XC253_ROUND9_AUTORESEARCH.md",
            "tests/test_stage390a.py",
        ),
        (
            "STAGE-391A",
            "tools/benchmarks/run_stage391a_live_xm20_round9_autoresearch.py",
            "artifacts/autoresearch/stage391a_live_xm20_round9_autoresearch.json",
            "docs/STAGE391A_LIVE_XM20_ROUND9_AUTORESEARCH.md",
            "tests/test_stage391a.py",
        ),
        (
            "STAGE-392A",
            "tools/benchmarks/build_stage392a_multi_radio_9round_scorecard.py",
            "artifacts/autoresearch/stage392a_multi_radio_9round_scorecard.json",
            "docs/STAGE392A_MULTI_RADIO_9ROUND_SCORECARD.md",
            "tests/test_stage392a.py",
        ),
        (
            "STAGE-393A",
            "tools/firmware/build_stage393a_cross_fleet_champion_v45.py",
            "artifacts/autoresearch/stage393a_cross_fleet_champion_v45.json",
            "docs/STAGE393A_CROSS_FLEET_CHAMPION_V45.md",
            "tests/test_stage393a.py",
        ),
        (
            "STAGE-394A",
            "tools/verify/verify_stage394a_multi_radio_v45_suite_gate.py",
            "artifacts/autoresearch/stage394a_multi_radio_v45_suite_gate_receipt.json",
            "docs/STAGE394A_MULTI_RADIO_V45_SUITE_GATE.md",
            "tests/test_stage389a_to_394a_multi_radio_v45.py",
        ),
    ]

    for stage_id, script_rel, receipt_rel, doc_rel, test_rel in expected_artifacts:
        s_path = ROOT / script_rel
        r_path = ROOT / receipt_rel
        d_path = ROOT / doc_rel
        t_path = ROOT / test_rel

        assert s_path.exists(), f"Missing script for {stage_id}: {s_path}"
        assert r_path.exists(), f"Missing receipt for {stage_id}: {r_path}"
        assert d_path.exists(), f"Missing doc for {stage_id}: {d_path}"
        assert t_path.exists(), f"Missing test for {stage_id}: {t_path}"

        doc_text = d_path.read_text(encoding="utf-8")
        doc_lines = doc_text.splitlines()
        assert len(doc_lines) < 220, f"Doc {doc_rel} exceeds 220 lines ({len(doc_lines)})"
        assert doc_text.count("<!-- doc-head:") == 1, f"Doc {doc_rel} must have 1 doc-head"

        data = json.loads(r_path.read_text(encoding="utf-8"))
        assert data["stage"] == stage_id
        audit = audit_stage_receipt_5pillars(data)
        assert audit["compliant"] is True, f"5-pillar audit failed for {stage_id}: {audit}"
