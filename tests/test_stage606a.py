from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage606a_ltu_v15_champion() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage606a_ltu_17round_204window_champion_v15_receipt.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "606A"
    assert data["champion_version"] == "v15"
    assert data["total_live_campaigns"] == 17
    assert data["total_live_ab_rounds"] == 51
    assert data["total_live_measurement_windows"] == 204
    assert all(data["checks"].values())
    assert not any(data["safety_audit"].values())
