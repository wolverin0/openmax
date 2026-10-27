from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage470a_ltu_v10_champion() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage470a_ltu_12round_144window_champion_v10_receipt.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "470A"
    assert data["champion_version"] == "v10"
    assert data["total_live_campaigns"] == 12
    assert data["total_live_ab_rounds"] == 36
    assert data["total_live_measurement_windows"] == 144
    assert all(data["checks"].values())
    assert not any(data["safety_audit"].values())
