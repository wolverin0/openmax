from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage638a_ltu_v16_champion() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage638a_ltu_18round_216window_champion_v16_receipt.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "638A"
    assert data["champion_version"] == "v16"
    assert data["total_live_campaigns"] == 18
    assert data["total_live_ab_rounds"] == 54
    assert data["total_live_measurement_windows"] == 216
    assert all(data["checks"].values())
    assert not any(data["safety_audit"].values())
