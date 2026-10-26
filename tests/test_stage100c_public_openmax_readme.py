"""Unit tests for Stage 100C public openMAX README.md & docs/DOCS-MAP.md polish."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.verify_stage100c_public_openmax_readme import (
    DOCS_MAP_PATH,
    FORBIDDEN_PUBLIC_TOKENS,
    OUTPUT_JSON_PATH,
    README_PATH,
    REQUIRED_HIGHLIGHT_TOKENS,
    run_stage100c_verification,
)


def test_stage100c_verification_runs_and_passes() -> None:
    payload = run_stage100c_verification()
    assert payload["status"] == "CONFIRMED"
    assert payload["all_checks_passed"] is True
    assert OUTPUT_JSON_PATH.exists()


def test_stage100c_readme_and_docs_map_line_budgets() -> None:
    readme_lines = README_PATH.read_text(encoding="utf-8").splitlines()
    docs_map_lines = DOCS_MAP_PATH.read_text(encoding="utf-8").splitlines()
    assert len(readme_lines) < 215, f"README.md has {len(readme_lines)} lines (>= 215)"
    assert len(docs_map_lines) < 215, f"DOCS-MAP.md has {len(docs_map_lines)} lines (>= 215)"

    doc_head_open = sum(1 for ln in docs_map_lines if ln.strip().startswith("<!-- doc-head"))
    doc_head_close = sum(1 for ln in docs_map_lines if ln.strip() == "<!-- /doc-head -->")
    assert doc_head_open == 1
    assert doc_head_close == 1


def test_stage100c_zero_forbidden_public_tokens() -> None:
    for path in (README_PATH, DOCS_MAP_PATH):
        lower = path.read_text(encoding="utf-8").lower()
        for tok in FORBIDDEN_PUBLIC_TOKENS:
            assert tok not in lower, f"Forbidden token {tok!r} found in {path.name}"


def test_stage100c_required_engineering_highlights_present() -> None:
    for path in (README_PATH, DOCS_MAP_PATH):
        text = path.read_text(encoding="utf-8")
        for tok in REQUIRED_HIGHLIGHT_TOKENS:
            assert tok in text, f"Missing required highlight {tok!r} in {path.name}"


def test_stage100c_five_pillar_compliance_receipt() -> None:
    data = json.loads(OUTPUT_JSON_PATH.read_text(encoding="utf-8"))
    pillars = data["five_pillar_compliance"]
    assert pillars["compliant"] is True
    for key in (
        "pillar_a_ground_up_re_and_knob_catalog",
        "pillar_b_hyperresearch_and_scholar_reactor",
        "pillar_c_karpathy_autoresearch_and_watchdog",
        "pillar_d_scientific_pareto_validation",
        "pillar_e_memory_master_claim_id",
    ):
        assert pillars["pillar_status"][key] is True
