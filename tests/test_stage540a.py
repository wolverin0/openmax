from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage540a_ltu_v12_champion() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage540a_ltu_14round_168window_champion_v12_receipt.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "540A"
    assert data["champion_version"] == "v12"
    assert data["total_live_campaigns"] == 14
    assert data["total_live_ab_rounds"] == 42
    assert data["total_live_measurement_windows"] == 168
    assert all(data["checks"].values())
    assert not any(data["safety_audit"].values())
