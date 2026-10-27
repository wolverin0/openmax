from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage572a_ltu_tdma_framing_and_split_sfn_helper() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage572a_ltu_tdma_framing_and_split_sfn_helper.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "572A"
    assert data["status"] == "CONFIRMED"
    assert all(data["checks"].values())
    assert data["helper_script"]["zero_dev_ame_touches"] is True
    assert not any(data["safety_audit"].values())
