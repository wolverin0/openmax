from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage538a_ad9361_fastlock_temp_helper() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage538a_ltu_ad9361_fastlock_and_temp_comp_helper.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "538A"
    assert data["status"] == "CONFIRMED"
    assert data["stage486a_re_linked"]["artifact_exists"] is True
    assert all(data["checks"].values())
    assert data["helper_script"]["zero_dev_ame_touches"] is True
    assert not any(data["safety_audit"].values())
