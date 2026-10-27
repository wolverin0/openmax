"""Stage 362A pytest suite."""

from __future__ import annotations

from pathlib import Path

from tools.sim.run_stage362a_panel2_deferred_sta_rescue_pareto import (
    build_stage362a_pareto_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage362a_panel2_deferred_sta_rescue_pareto() -> None:
    report = build_stage362a_pareto_report()
    assert report["stage"] == "362A"
    assert report["status"] == "COMPLETED"
    assert report["writes_performed"] == 0

    delta = report["pareto_delta_summary"]
    assert delta["baseline_mpdus_requed_pct"] > 19.0
    assert delta["champion_mpdus_requed_pct"] < 3.0
    assert delta["target_mpdus_requed_under_3pct_met"] is True
    assert delta["p95_rtt_relative_delta_pct"] < -60.0

    gate = audit_stage_receipt_5pillars(report)
    assert gate["compliant"], f"Stage 362A 5-pillar gate failed: {gate}"

    doc = REPO_ROOT / "docs" / "STAGE362A_PANEL2_DEFERRED_STA_RESCUE_PARETO.md"
    assert doc.exists()
    txt = doc.read_text(encoding="utf-8")
    assert len(txt.splitlines()) < 220
    assert txt.count("<!-- doc-head:") == 1
