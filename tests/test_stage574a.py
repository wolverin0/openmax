from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage574a_ltu_v14_champion() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage574a_ltu_16round_192window_champion_v14_receipt.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "574A"
    assert data["champion_version"] == "v14"
    assert data["total_live_campaigns"] == 16
    assert data["total_live_ab_rounds"] == 48
    assert data["total_live_measurement_windows"] == 192
    assert all(data["checks"].values())
    assert not any(data["safety_audit"].values())
