from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage672a_ltu_v17_champion() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage672a_ltu_19round_228window_champion_v17_receipt.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "672A"
    assert data["champion_version"] == "v17"
    assert data["total_live_campaigns"] == 19
    assert data["total_live_ab_rounds"] == 57
    assert data["total_live_measurement_windows"] == 228
    assert all(data["checks"].values())
    assert not any(data["safety_audit"].values())
