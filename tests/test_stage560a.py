from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage560a_ltu_v13_champion() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage560a_ltu_15round_180window_champion_v13_receipt.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "560A"
    assert data["champion_version"] == "v13"
    assert data["total_live_campaigns"] == 15
    assert data["total_live_ab_rounds"] == 45
    assert data["total_live_measurement_windows"] == 180
    assert all(data["checks"].values())
    assert not any(data["safety_audit"].values())
