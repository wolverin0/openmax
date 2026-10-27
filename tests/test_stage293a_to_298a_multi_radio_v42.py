from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
S293A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage293a_live_xc198_round6_autoresearch.json"
S294A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage294a_live_2xc253_round6_autoresearch.json"
S295A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage295a_live_xm20_round6_autoresearch.json"
S296A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage296a_xc_2xc_xm_24window_scorecard.json"
S297A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage297a_cross_fleet_champion_v42_receipt.json"
S298A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage298a_multi_radio_v42_suite_gate_receipt.json"
S298A_DOC = REPO_ROOT / "docs" / "STAGE298A_MULTI_RADIO_V42_SUITE_GATE.md"


def test_stage293a_to_297a_all_receipts_and_safety() -> None:
    for p in (S293A_JSON, S294A_JSON, S295A_JSON, S296A_JSON, S297A_JSON):
        assert p.exists(), f"Missing {p}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["safety_boundaries"]["touched_241_or_242"] is False
        assert data["safety_boundaries"]["touched_20_or_250"] is False
        assert data["safety_boundaries"]["flash_writes"] == 0
        assert data["five_pillar_compliant"] is True


def test_stage298a_suite_gate_receipt_and_doc() -> None:
    assert S298A_JSON.exists(), "Missing stage298a_multi_radio_v42_suite_gate_receipt.json"
    assert S298A_DOC.exists(), "Missing STAGE298A_MULTI_RADIO_V42_SUITE_GATE.md"

    doc_text = S298A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S298A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-298A"
    assert data["status"] == "PASS"
    assert data["audited_stages_count"] == 5
    assert set(data["audited_stages"].keys()) == {
        "STAGE-293A",
        "STAGE-294A",
        "STAGE-295A",
        "STAGE-296A",
        "STAGE-297A",
    }
    assert data["five_pillar_compliant"] is True
