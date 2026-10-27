"""Stage 675A pytest verification (R71..R73 = 296 Cumulative Windows)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage675a_receipt_valid() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage675a_live_wa_pb060_and_htt_tx_compl_r71_73.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 675A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["cumulative_wa_total_windows_including_e2e"] == 296
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert len(r["windows"]) == 4
