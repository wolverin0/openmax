from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage502a_ltu_dcxo_monitor() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage502a_ltu_dcxo_gps_tcxo_drift_monitor.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "502A"
    assert data["status"] == "CONFIRMED"
    assert all(data["checks"].values())
    assert data["monitor_script"]["zero_dev_ame_touches"] is True
    assert not any(data["safety_audit"].values())
