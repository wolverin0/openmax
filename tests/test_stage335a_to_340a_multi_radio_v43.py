#!/usr/bin/env python3
"""Consolidated verification suite for Stage 335A through Stage 340A Multi-Radio Round 7 Campaign (Champion v43.0)."""
from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage335a_to_340a_multi_radio_v43_suite() -> None:
    expected_artifacts = [
        (
            "STAGE-335A",
            "tools/benchmarks/run_stage335a_live_xc198_round7_autoresearch.py",
            "artifacts/autoresearch/stage335a_live_xc198_round7_autoresearch.json",
            "docs/STAGE335A_LIVE_XC198_ROUND7_AUTORESEARCH.md",
            "tests/test_stage335a.py",
        ),
        (
            "STAGE-336A",
            "tools/benchmarks/run_stage336a_live_2xc253_round7_autoresearch.py",
            "artifacts/autoresearch/stage336a_live_2xc253_round7_autoresearch.json",
            "docs/STAGE336A_LIVE_2XC253_ROUND7_AUTORESEARCH.md",
            "tests/test_stage336a.py",
        ),
        (
            "STAGE-337A",
            "tools/benchmarks/run_stage337a_live_xm20_round7_autoresearch.py",
            "artifacts/autoresearch/stage337a_live_xm20_round7_autoresearch.json",
            "docs/STAGE337A_LIVE_XM20_ROUND7_AUTORESEARCH.md",
            "tests/test_stage337a.py",
        ),
        (
            "STAGE-338A",
            "tools/benchmarks/build_stage338a_multi_radio_7round_scorecard.py",
            "artifacts/autoresearch/stage338a_multi_radio_7round_scorecard.json",
            "docs/STAGE338A_MULTI_RADIO_7ROUND_SCORECARD.md",
            "tests/test_stage338a.py",
        ),
        (
            "STAGE-339A",
            "tools/firmware/build_stage339a_cross_fleet_champion_v43.py",
            "artifacts/autoresearch/stage339a_cross_fleet_champion_v43.json",
            "docs/STAGE339A_CROSS_FLEET_CHAMPION_V43.md",
            "tests/test_stage339a.py",
        ),
        (
            "STAGE-340A",
            "tools/verify/verify_stage340a_multi_radio_v43_suite_gate.py",
            "artifacts/autoresearch/stage340a_multi_radio_v43_suite_gate_receipt.json",
            "docs/STAGE340A_MULTI_RADIO_V43_SUITE_GATE.md",
            "tests/test_stage335a_to_340a_multi_radio_v43.py",
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
