"""Stage 755A pytest verification (R78..R80 = 328 Cumulative Windows)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage755a_receipt_valid() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage755a_live_wa_spectral_phyerr_and_vdev_guard_r78_80.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 755A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["cumulative_wa_total_windows_including_e2e"] == 328
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert len(r["windows"]) == 4
