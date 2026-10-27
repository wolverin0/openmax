#!/usr/bin/env python3
"""Pytest suite for Stage 133A: Unified Test & 5-Pillar Verification Sweep for WA-Family Universal Kit (Stages 116A..141A)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars  # noqa: E402
from tools.verify.verify_stage133a_wa_kit_suite_gate import (  # noqa: E402
    RECEIPT_PATH,
    STAGE_MATRIX,
    verify_stage133a_wa_kit_suite_gate,
)


def test_stage133a_receipt_generated_and_5pillar_compliant() -> None:
    verify_stage133a_wa_kit_suite_gate(run_pytest_subprocess=False)
    assert RECEIPT_PATH.is_file()
    persisted = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert persisted["stage"] == "STAGE-133A"
    assert persisted["stage_range"] == "116A..141A"
    assert persisted["claim_status"] == "CONFIRMED"
    assert persisted["five_pillar_compliant"] is True
    audit = audit_stage_receipt_5pillars(persisted)
    assert audit["compliant"] is True
    assert audit["missing_pillars"] == []


def test_stage133a_all_stages_116a_to_141a_receipts_and_5pillars() -> None:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert len(STAGE_MATRIX) >= 24
    assert receipt["summary"]["stages_swept_count"] == len(STAGE_MATRIX)
    assert receipt["summary"]["all_receipts_exist"] is True
    assert receipt["summary"]["all_receipts_5pillar_compliant"] is True
    stage_ids = {entry["stage"] for entry in receipt["stage_audits"]}
    assert "STAGE-116A" in stage_ids
    assert "STAGE-130A" in stage_ids
    assert "STAGE-140A" in stage_ids
    assert "STAGE-141A" in stage_ids
    for entry in receipt["stage_audits"]:
        assert entry["receipt_exists"] is True, f"Missing receipt for {entry['stage']}"
        assert entry["five_pillar_audit"]["compliant"] is True, (
            f"5-Pillar non-compliant for {entry['stage']}: {entry['five_pillar_audit']}"
        )


def test_stage133a_all_pytest_suites_exist_and_have_tests() -> None:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert receipt["summary"]["all_test_suites_exist"] is True
    assert receipt["summary"]["total_ast_test_functions"] >= 130
    for entry in receipt["stage_audits"]:
        assert entry["test_suite_exists"] is True, f"Missing test suite for {entry['stage']}"
        assert entry["ast_test_function_count"] >= 1, (
            f"Too few tests in {entry['test_suite_path']}"
        )


def test_stage133a_repo_5pillar_gate_and_safety_boundaries() -> None:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert receipt["repo_5pillar_gate"]["compliant"] is True
    assert receipt["summary"]["overall_sweep_pass"] is True
    safety = receipt["safety_boundaries"]
    assert safety["live_devices_touched"] is False
    assert safety["flash_writes"] == 0
    assert safety["guarida_backbone_untouched"] is True
    assert safety["radios_241_242_untouched"] is True
