from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage539a_dfs_cac_and_chirp_immunity() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage539a_qca988x_dfs_cac_and_chirp_immunity_kit.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "539A"
    assert data["status"] == "CONFIRMED"
    assert data["stage499a_re_linked"] is True
    assert all(data["checks"].values())
    assert not any(data["safety_audit"].values())
