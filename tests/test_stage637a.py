from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage637a_qca_txbf_stbc_and_ldpc_guard() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage637a_qca_txbf_stbc_and_ldpc_guard.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "637A"
    assert data["status"] == "CONFIRMED"
    assert all(data["checks"].values())
    assert data["stage615a_re_foundation"]["bf_means_buffer_in_ath_dev"] is True
    assert not any(data["safety_audit"].values())
