from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage504a_ltu_v11_champion() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage504a_ltu_13round_156window_champion_v11_receipt.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "504A"
    assert data["champion_version"] == "v11"
    assert data["total_live_campaigns"] == 13
    assert data["total_live_ab_rounds"] == 39
    assert data["total_live_measurement_windows"] == 156
    assert all(data["checks"].values())
    assert not any(data["safety_audit"].values())
