from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.research.run_stage72c_571knob_ledger_and_scholar_synthesis import (
    CATALOG_PATH,
    DEFAULT_OUTPUT_JSON,
    EXPECTED_CATALOG_SHA256,
    STAGE72C_VAULT_JSON,
    build_stage72c_ledger_and_scholar_synthesis,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE72C_DOC = REPO_ROOT / "docs" / "STAGE72C_571KNOB_LEDGER_UPDATE_AND_SCHOLAR_REACTOR_SYNTHESIS.md"


def test_stage72c_preserves_571_knob_catalog_immutability() -> None:
    actual_sha256 = hashlib.sha256(CATALOG_PATH.read_bytes()).hexdigest()
    assert actual_sha256 == EXPECTED_CATALOG_SHA256
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    assert len(catalog["knobs"]) == 571


def test_stage72c_receipt_and_5pillar_compliance() -> None:
    payload = build_stage72c_ledger_and_scholar_synthesis()
    assert DEFAULT_OUTPUT_JSON.exists()
    assert STAGE72C_VAULT_JSON.exists()

    gate = audit_stage_receipt_5pillars(payload)
    assert gate["compliant"] is True, f"Missing pillars: {gate['missing_pillars']}"

    assert payload["immutable_source_catalog"]["total_knobs"] == 571
    assert len(payload["companion_571knob_ledger"]) == 571

    reconciliation = payload["stage60a_to_71b_empirical_reconciliation"]
    assert reconciliation["curated_knob_groups_evaluated"] == 10
    assert reconciliation["catalog_ids_directly_exercised_in_s60_s71"] >= 35

    verdict_by_key = {g["knob_key"]: g for g in reconciliation["knob_group_verdicts"]}
    assert verdict_by_key["set_multiq"]["overall_verdict"] == "KEEP"
    assert verdict_by_key["enable_tx_tcp_cksum"]["overall_verdict"] == "KEEP"
    assert verdict_by_key["aggr_swretry_nonaggr_swretry_ampduframes"]["verdict_ptp"] == "KEEP"
    assert verdict_by_key["aggr_swretry_nonaggr_swretry_ampduframes"]["verdict_ptmp"] == "DISCARD"
    assert verdict_by_key["ac_minfree_and_protmode"]["overall_verdict"] == "DISCARD"
    assert verdict_by_key["uph_wifi0_timing_and_daprot"]["verdict_ptp"] == "DISCARD"
    assert verdict_by_key["ltu_bug_01_to_08_and_binary_patches"]["overall_verdict"] == "KEEP"
    assert verdict_by_key["airprism_gpio_hsr_and_gps_sync_colocation"]["overall_verdict"] == "KEEP"

    scholar = payload["closed_loop_hyperresearch_scholar_synthesis"]
    assert scholar["verifier_model"] == "jev-1.14.0"
    paper_ids = {p["paper_id"] for p in scholar["verified_papers"]}
    assert {"1503.04533v6", "0806.4695v1", "2211.03471v1", "2101.07562v1", "1803.10148v1"}.issubset(paper_ids)


def test_stage72c_doc_budget_and_header() -> None:
    assert STAGE72C_DOC.exists()
    lines = STAGE72C_DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220, f"Expected < 220 lines, got {len(lines)}"
    assert lines[0].startswith("<!-- doc-head:")
    doc_head_count = sum(1 for ln in lines if "<!-- doc-head:" in ln)
    assert doc_head_count == 1
