from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
S271A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage271a_live_xm20_round5_autoresearch.json"
S271A_DOC = REPO_ROOT / "docs" / "STAGE271A_LIVE_XM20_ROUND5_AUTORESEARCH.md"


def test_stage271a_live_xm20_round5_autoresearch() -> None:
    assert S271A_JSON.exists(), "Missing stage271a_live_xm20_round5_autoresearch.json"
    assert S271A_DOC.exists(), "Missing STAGE271A_LIVE_XM20_ROUND5_AUTORESEARCH.md"

    doc_text = S271A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S271A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-271A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert data["safety_boundaries"]["flash_writes"] == 0
    assert data["target_radio"]["lan_ip"] == "192.168.1.20"
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert [w["window"] for w in r["windows"]] == ["A1", "B1", "A2", "B2"]
        for w in r["windows"]:
            assert w["boca2_xm_1_20_rtt"]["samples"] >= 1
    assert data["five_pillar_compliant"] is True
