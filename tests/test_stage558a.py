from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage558a_ltu_super4096_dpd_evm_guard() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage558a_ltu_super4096_dpd_evm_guard.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "558A"
    assert data["status"] == "CONFIRMED"
    assert all(data["checks"].values())
    assert data["guard_script"]["zero_dev_ame_touches"] is True
    assert not any(data["safety_audit"].values())
