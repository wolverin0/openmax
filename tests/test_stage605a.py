from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage605a_qca988x_wmi_peer_rate_sgi_guard() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage605a_qca988x_wmi_peer_rate_sgi_guard.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "605A"
    assert data["status"] == "CONFIRMED"
    assert all(data["checks"].values())
    assert data["stage589a_re_foundation"]["vocab_is_umac_only"] is True
    assert not any(data["safety_audit"].values())
