from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage603a_ltu110_round17_204window_receipt() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage603a_live_ltu110_round17_204window_autoresearch.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "603A"
    assert data["status"] == "CONFIRMED"
    assert data["summary_metrics"]["total_rounds"] == 3
    assert data["summary_metrics"]["total_windows"] == 12
    assert data["summary_metrics"]["cumulative_ltu110_live_campaigns"] == 17
    assert data["summary_metrics"]["cumulative_ltu110_live_windows"] == 204
    assert data["safety_audit"]["zero_dev_ame_touches"] is True
    assert data["safety_audit"]["touched_dev_ame_nodes"] is False
