from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
S335A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage335a_live_xc198_round7_autoresearch.json"
S335A_DOC = REPO_ROOT / "docs" / "STAGE335A_LIVE_XC198_ROUND7_AUTORESEARCH.md"


def test_stage335a_live_xc198_round7_autoresearch() -> None:
    assert S335A_JSON.exists(), "Missing stage335a_live_xc198_round7_autoresearch.json"
    assert S335A_DOC.exists(), "Missing STAGE335A_LIVE_XC198_ROUND7_AUTORESEARCH.md"

    doc_text = S335A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S335A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-335A"
    assert data["status"] == "CONFIRMED"
    assert data["watchdog_seconds"] == 45
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_250"] is False
    assert data["safety_boundaries"]["flash_writes"] == 0
    assert [w["window"] for w in data["windows"]] == ["A1", "B1", "A2", "B2"]
    assert data["xc198_round7_champion_profile"]["dev_weight"] == 96
    assert data["xc198_round7_champion_profile"]["netdev_budget"] == 600
    assert data["xc198_round7_champion_profile"]["tcp_thin_linear_timeouts"] == 1
    assert data["five_pillar_compliant"] is True
