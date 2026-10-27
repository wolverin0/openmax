"""Pytest for Stage 688A (4-Objective NSGA-III Pareto Fixed 10ms 67/33 + Slot Guard 39us + A-MSDU 7935B)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage688a_receipt_and_doc() -> None:
    p_json = ROOT / "artifacts/autoresearch/stage688a_nsga3_pareto_slot_guard_and_dl_ul_67_33.json"
    p_doc = ROOT / "docs/STAGE688A_NSGA3_PARETO_SLOT_GUARD_AND_DL_UL_67_33.md"
    assert p_json.exists()
    assert p_doc.exists()
    data = json.loads(p_json.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-688A"
    assert data["status"] == "CONFIRMED"
    assert data["panel2_82_dl_airtime_gain_pct"] == 34.84
    assert len(data["pareto_front_ids"]) >= 2
    assert data["five_pillar_compliant"] is True
    doc_text = p_doc.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 200
    assert doc_text.count("<!-- doc-head:") == 1
