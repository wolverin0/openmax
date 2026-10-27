"""Unit and integration verification tests for Stage 69A (T-S69A-M5-XW-AND-CROSS-GEN-INTEROP-571KNOB-SWEEP)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage69a_m5_xw_crossgen_571knob_sweep import (
    DEFAULT_RECEIPT_PATH,
    SCHOLAR_VAULT_PATH,
    STAGE69A_SCHOLAR_VERIFIED_PAPERS,
    audit_m5_xw_and_crossgen_571knob_catalog,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage69a_571knob_catalog_audit_and_boundary_discoveries() -> None:
    audit = audit_m5_xw_and_crossgen_571knob_catalog()
    assert audit["total_knobs_in_catalog"] == 571
    assert audit["m5_xw_crossgen_applicable_count"] >= 30
    assert audit["stage69a_knobs_audited_count"] == 18

    discoveries = {d["id"]: d for d in audit["kernel_boundary_discoveries"]}
    assert set(discoveries.keys()) == {
        "FMX-S69A-KB-01",
        "FMX-S69A-KB-02",
        "FMX-S69A-KB-03",
    }
    for disc in discoveries.values():
        assert disc["claim_label"] == "CONFIRMED"
        assert disc["attribution"]


def test_stage69a_scholar_verified_papers_exist() -> None:
    assert len(STAGE69A_SCHOLAR_VERIFIED_PAPERS) >= 2
    for paper in STAGE69A_SCHOLAR_VERIFIED_PAPERS:
        assert paper["status"] == "supported"
        assert paper["result_state"] == "verified"
        assert float(paper["verification_probability"]) >= 0.90


def test_stage69a_receipt_passes_5pillar_gate_and_counterbalanced_contract() -> None:
    assert DEFAULT_RECEIPT_PATH.exists(), f"Missing receipt {DEFAULT_RECEIPT_PATH}"
    assert SCHOLAR_VAULT_PATH.exists(), f"Missing scholar vault {SCHOLAR_VAULT_PATH}"

    gate = audit_stage_receipt_5pillars(DEFAULT_RECEIPT_PATH)
    assert gate["overall_pass"] is True, f"5-pillar gate failed: {gate}"
    assert all(p["pass"] for p in gate["pillars"].values())

    data = json.loads(DEFAULT_RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 69A"
    assert data["task_id"] == "T-S69A-M5-XW-AND-CROSS-GEN-INTEROP-571KNOB-SWEEP"
    assert int(data["watchdog_timeout_s"]) == 45
    assert data["final_3cpe_health"]["all_healthy"] is True

    rounds = data["counterbalanced_rounds"]
    assert len(rounds) == 3
    expected_round_ids = [
        "S69A-R1-M5-XW-WMM-AMPDU-ACK-TXQ-SWEEP",
        "S69A-R2-M5-XW-HTB-U32-TOS-QDISC-SHAPER",
        "S69A-R3-AP-CROSSGEN-AQL-1800-3600-FQ-3028",
    ]
    assert [r["round_id"] for r in rounds] == expected_round_ids

    for r in rounds:
        assert int(r["watchdog_timeout_s"]) == 45
        blocks = r["blocks"]
        assert [b["block"] for b in blocks] == ["A1", "B1", "A2", "B2"]
        for b in blocks:
            assert float(b["aggregate_goodput_mbps"]) > 5.0
            assert float(b["p50_rtt_ms"]) > 0.0
            assert float(b["p95_rtt_ms"]) >= float(b["p50_rtt_ms"])
        assert r["decision"] in ("KEEP", "PROMOTE_NEW_CHAMPION", "REJECT")
        assert r["claim_label"] in ("CONFIRMED", "REFUTED")
        assert r["subsystem_attribution"]


def test_stage69a_docs_and_line_limits() -> None:
    stage69a_doc = REPO_ROOT / "docs" / "STAGE69A_M5_XW_CROSSGEN_571KNOB_AUTORESEARCH_SWEEP.md"
    current_state_doc = REPO_ROOT / "docs" / "CURRENT_STATE.md"
    master_index_doc = REPO_ROOT / "docs" / "MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md"

    for doc_path in (stage69a_doc, current_state_doc, master_index_doc):
        assert doc_path.exists(), f"Missing {doc_path}"
        lines = doc_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) < 250, f"{doc_path.name} has {len(lines)} lines (must be < 250)"
        assert lines[0].startswith("<!-- doc-head:"), f"{doc_path.name} missing doc-head on line 1"
        doc_head_count = sum(1 for ln in lines if "<!-- doc-head:" in ln)
        assert doc_head_count == 1, f"{doc_path.name} has {doc_head_count} doc-head blocks (must be 1)"
