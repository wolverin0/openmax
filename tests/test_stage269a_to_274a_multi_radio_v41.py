from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
S269A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage269a_live_xc198_round5_autoresearch.json"
S270A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage270a_live_2xc253_round5_autoresearch.json"
S271A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage271a_live_xm20_round5_autoresearch.json"
S272A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage272a_dualband_2xc_xc_nlos_failover_pareto.json"
S273A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage273a_cross_fleet_champion_v41_receipt.json"
S274A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage274a_multi_radio_v41_suite_gate_receipt.json"
S274A_DOC = REPO_ROOT / "docs" / "STAGE274A_MULTI_RADIO_V41_SUITE_GATE.md"


def test_stage269a_to_273a_all_receipts_and_safety() -> None:
    for p in (S269A_JSON, S270A_JSON, S271A_JSON, S272A_JSON, S273A_JSON):
        assert p.exists(), f"Missing {p}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["safety_boundaries"]["touched_241_or_242"] is False
        assert data["safety_boundaries"]["touched_20_or_250"] is False
        assert data["safety_boundaries"]["flash_writes"] == 0
        assert data["five_pillar_compliant"] is True


def test_stage274a_suite_gate_receipt_and_doc() -> None:
    assert S274A_JSON.exists(), "Missing stage274a_multi_radio_v41_suite_gate_receipt.json"
    assert S274A_DOC.exists(), "Missing STAGE274A_MULTI_RADIO_V41_SUITE_GATE.md"

    doc_text = S274A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S274A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-274A"
    assert data["status"] == "PASS"
    assert data["audited_stages_count"] == 5
    assert set(data["audited_stages"].keys()) == {
        "STAGE-269A",
        "STAGE-270A",
        "STAGE-271A",
        "STAGE-272A",
        "STAGE-273A",
    }
    assert data["five_pillar_compliant"] is True
