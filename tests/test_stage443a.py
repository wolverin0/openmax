from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage443a_ltu_v9_champion() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage443a_ltu_11round_132window_champion_v9_receipt.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "443A"
    assert data["champion_version"] == "v9"
    assert data["total_live_campaigns"] == 11
    assert data["total_live_ab_rounds"] == 33
    assert data["total_live_measurement_windows"] == 132
    assert all(data["checks"].values())
    assert not any(data["safety_audit"].values())
