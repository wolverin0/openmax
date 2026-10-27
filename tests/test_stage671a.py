from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage671a_qca_htt_tx_compl_and_aql_guard() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage671a_qca_htt_tx_compl_and_aql_guard.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "671A"
    assert data["status"] == "CONFIRMED"
    assert all(data["checks"].values())
    assert data["htt_tx_backpressure_profile"]["completion_message"] == "HTT_T2H_MSG_TYPE_TX_COMPL_IND"
    assert not any(data["safety_audit"].values())
