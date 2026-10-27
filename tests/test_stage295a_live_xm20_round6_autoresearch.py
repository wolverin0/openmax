from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
S295A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage295a_live_xm20_round6_autoresearch.json"
S295A_DOC = REPO_ROOT / "docs" / "STAGE295A_LIVE_XM20_ROUND6_AUTORESEARCH.md"


def test_stage295a_live_xm20_round6_autoresearch() -> None:
    assert S295A_JSON.exists(), "Missing stage295a_live_xm20_round6_autoresearch.json"
    assert S295A_DOC.exists(), "Missing STAGE295A_LIVE_XM20_ROUND6_AUTORESEARCH.md"

    doc_text = S295A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S295A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-295A"
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
