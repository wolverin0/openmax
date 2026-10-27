#!/usr/bin/env python3
"""Consolidated verification suite for Stage 365A through Stage 370A Multi-Radio Round 8 Campaign (Champion v44.0)."""
from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage365a_to_370a_multi_radio_v44_suite() -> None:
    expected_artifacts = [
        (
            "STAGE-365A",
            "tools/benchmarks/run_stage365a_live_xc198_round8_autoresearch.py",
            "artifacts/autoresearch/stage365a_live_xc198_round8_autoresearch.json",
            "docs/STAGE365A_LIVE_XC198_ROUND8_AUTORESEARCH.md",
            "tests/test_stage365a.py",
        ),
        (
            "STAGE-366A",
            "tools/benchmarks/run_stage366a_live_2xc253_round8_autoresearch.py",
            "artifacts/autoresearch/stage366a_live_2xc253_round8_autoresearch.json",
            "docs/STAGE366A_LIVE_2XC253_ROUND8_AUTORESEARCH.md",
            "tests/test_stage366a.py",
        ),
        (
            "STAGE-367A",
            "tools/benchmarks/run_stage367a_live_xm20_round8_autoresearch.py",
            "artifacts/autoresearch/stage367a_live_xm20_round8_autoresearch.json",
            "docs/STAGE367A_LIVE_XM20_ROUND8_AUTORESEARCH.md",
            "tests/test_stage367a.py",
        ),
        (
            "STAGE-368A",
            "tools/benchmarks/build_stage368a_multi_radio_8round_scorecard.py",
            "artifacts/autoresearch/stage368a_multi_radio_8round_scorecard.json",
            "docs/STAGE368A_MULTI_RADIO_8ROUND_SCORECARD.md",
            "tests/test_stage368a.py",
        ),
        (
            "STAGE-369A",
            "tools/firmware/build_stage369a_cross_fleet_champion_v44.py",
            "artifacts/autoresearch/stage369a_cross_fleet_champion_v44.json",
            "docs/STAGE369A_CROSS_FLEET_CHAMPION_V44.md",
            "tests/test_stage369a.py",
        ),
        (
            "STAGE-370A",
            "tools/verify/verify_stage370a_multi_radio_v44_suite_gate.py",
            "artifacts/autoresearch/stage370a_multi_radio_v44_suite_gate_receipt.json",
            "docs/STAGE370A_MULTI_RADIO_V44_SUITE_GATE.md",
            "tests/test_stage365a_to_370a_multi_radio_v44.py",
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
