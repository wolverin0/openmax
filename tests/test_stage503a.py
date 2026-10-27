from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage503a_bmiss_csa_helper() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage503a_qca988x_bmiss_and_csa_resilience_helper.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "503A"
    assert data["status"] == "CONFIRMED"
    assert data["stage485a_re_linked"] is True
    assert all(data["checks"].values())
    assert not any(data["safety_audit"].values())
