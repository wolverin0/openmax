"""Stage 361A pytest suite."""

from __future__ import annotations

from pathlib import Path

from tools.observability.build_stage361a_guarida_32cpe_cooperative_fault_matrix import (
    build_stage361a_fault_matrix,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage361a_guarida_32cpe_cooperative_fault_matrix() -> None:
    report = build_stage361a_fault_matrix(REPO_ROOT)
    assert report["stage"] == "361A"
    assert report["status"] == "COMPLETED"
    assert report["writes_performed"] == 0

    s = report["summary"]
    assert s["total_cpes_classified"] == 32
    assert s["panel1_cpes"] == 4
    assert s["panel2_cpes"] == 22
    assert s["panel3_cpes"] == 6
    assert sum(s["category_counts"].values()) == 32
    assert s["simo_tx_2x2_mrc_rx_candidates_count"] == 4
    assert s["deferred_or_low_snr_cpes_count"] >= 4

    gate = audit_stage_receipt_5pillars(report)
    assert gate["compliant"], f"Stage 361A 5-pillar gate failed: {gate}"

    doc = REPO_ROOT / "docs" / "STAGE361A_GUARIDA_32CPE_COOPERATIVE_FAULT_MATRIX.md"
    assert doc.exists()
    txt = doc.read_text(encoding="utf-8")
    assert len(txt.splitlines()) < 220
    assert txt.count("<!-- doc-head:") == 1
