"""Stage 758A pytest verification (Panel1-Guarida .84 v13 20.2h+ Audit)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage758a_receipt_valid() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage758a_live_panel1_guarida_84_v13_audit.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 758A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["zero_rf_disconnect_verified"] is True
    assert data["safety_boundaries"]["active_cpes_count"] == 3
