#!/usr/bin/env python3
"""Stage 352A — Consolidated Verification Suite for Stages 347A..352A (Ground-Up PHY & WA v8 SquashFS Bake)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.audit_all_docs_line_budget_and_dochead import inspect_markdown
from tools.verify.enforce_5pillar_research_gate import audit_repo_deterministic_gates

REPO_ROOT = Path(__file__).resolve().parents[1]

STAGE_DOCS = [
    REPO_ROOT / "docs" / "STAGE347A_XTENSA_SGMT_RAM_PATCH_PROFILES.md",
    REPO_ROOT / "docs" / "STAGE348A_PB021_PPDU_EVM_RANGING_EXTRACTOR.md",
    REPO_ROOT / "docs" / "STAGE349A_CHAIN_IMBALANCE_RESCUE_DAEMON.md",
    REPO_ROOT / "docs" / "STAGE350A_COOPERATIVE_CPE_DIFFERENTIAL_CLASSIFIER.md",
    REPO_ROOT / "docs" / "STAGE351A_WA_SQUASHFS_V8_BAKE.md",
    REPO_ROOT / "docs" / "STAGE352A_CONSOLIDATED_GROUND_UP_PHY_AND_V8_VERIFICATION.md",
]

STAGE_ARTIFACTS = [
    ("347A", "mm-61aa", REPO_ROOT / "artifacts" / "autoresearch" / "stage347a_xtensa_sgmt_ram_patch_profiles.json"),
    ("348A", "mm-22d6", REPO_ROOT / "artifacts" / "autoresearch" / "stage348a_pb021_ppdu_evm_ranging_extractor.json"),
    ("349A", "mm-9ce7", REPO_ROOT / "artifacts" / "autoresearch" / "stage349a_chain_imbalance_rescue_daemon.json"),
    ("350A", "mm-7295", REPO_ROOT / "artifacts" / "autoresearch" / "stage350a_cooperative_cpe_differential_classifier.json"),
    ("351A", "mm-91f1", REPO_ROOT / "artifacts" / "autoresearch" / "stage351a_wa_squashfs_v8_bake.json"),
    ("352A", "mm-62bf", REPO_ROOT / "artifacts" / "autoresearch" / "stage352a_consolidated_ground_up_phy_and_v8_verification.json"),
]


def test_stage347a_to_352a_docs_budget_and_dochead() -> None:
    for doc_path in STAGE_DOCS:
        assert doc_path.exists(), f"Missing {doc_path}"
        res = inspect_markdown(doc_path.read_bytes())
        assert res["compliant"] is True, f"Doc failed line-budget/doc-head gate: {res}"


def test_stage347a_to_352a_artifacts_and_memory_master_claims() -> None:
    for stage_id, expected_mm, art_path in STAGE_ARTIFACTS:
        assert art_path.exists(), f"Missing {art_path}"
        data = json.loads(art_path.read_text(encoding="utf-8"))
        assert data["stage"] == stage_id
        assert data["memory_master_claim_id"] == expected_mm
        assert data["claim_status"] == "CONFIRMED"
        assert "five_pillar_compliance" in data


def test_stage352a_five_pillar_repo_gate() -> None:
    gate = audit_repo_deterministic_gates()
    assert gate["compliant"] is True, f"5-pillar repo gate failed: {gate}"
