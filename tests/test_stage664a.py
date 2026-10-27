"""Pytest suite for Stage 664A Zero-FP Observability Engine v6 (Slot-Guard >20% Auditor)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage664a_auditor_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage664a_zero_fp_observability_engine_v6_slot_guard_auditor.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "664A"
    assert data["status"] == "CONFIRMED"
    assert data["starvation_threshold_pct"] == 20.0
    audits = data["sector_audits"]
    assert audits[0]["guard_ratio_pct"] == 26.0
    assert audits[0]["exceeds_20pct_threshold"] is True
    assert audits[1]["guard_ratio_pct"] == 4.33
    assert audits[1]["exceeds_20pct_threshold"] is False


def test_stage664a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE664A_ZERO_FP_OBSERVABILITY_ENGINE_V6_SLOT_GUARD_AUDITOR.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
