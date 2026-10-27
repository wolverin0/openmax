#!/usr/bin/env python3
"""
Tests for Stage 100A (`T-S100A-GIT-PUBLIC-REPO-SAFETY-AND-REDDIT-HTML-SYNC`).
"""

from __future__ import annotations

import json

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage100a_git_public_repo_safety import (
    DEFAULT_OUT_JSON,
    REDDIT_HTML_PATH,
    REDDIT_MD_PATH,
    build_stage100a_receipt,
)


def test_stage100a_reddit_sync_and_gitignore_safety() -> None:
    receipt = build_stage100a_receipt()
    assert DEFAULT_OUT_JSON.exists()
    assert receipt["stage"] == "100A"
    assert receipt["status"] == "CONFIRMED"

    reddit = receipt["reddit_sync_verification"]
    assert reddit["all_tokens_synced"] is True
    assert REDDIT_MD_PATH.exists()
    assert REDDIT_HTML_PATH.exists()

    gitignore = receipt["gitignore_safety_verification"]
    assert gitignore["all_mandatory_paths_ignored"] is True, (
        f"Unignored paths: {[k for k, v in gitignore['ignored_status_by_path'].items() if not v]}"
    )
    assert gitignore["git_commit_or_push_executed"] is False


def test_stage100a_5pillar_gate_compliance() -> None:
    loaded = json.loads(DEFAULT_OUT_JSON.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True, f"5-pillar gate failed: {audit}"
