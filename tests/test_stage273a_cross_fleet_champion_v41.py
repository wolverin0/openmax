from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
S273A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage273a_cross_fleet_champion_v41_receipt.json"
S273A_DOC = REPO_ROOT / "docs" / "STAGE273A_CROSS_FLEET_CHAMPION_V41.md"


def test_stage273a_cross_fleet_champion_v41() -> None:
    assert S273A_JSON.exists(), "Missing stage273a_cross_fleet_champion_v41_receipt.json"
    assert S273A_DOC.exists(), "Missing STAGE273A_CROSS_FLEET_CHAMPION_V41.md"

    doc_text = S273A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S273A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-273A"
    assert data["master_version"] == "v41.0"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert set(data["cross_fleet_matrix_v41"].keys()) == {"WA", "XC", "2XC", "XW", "XM", "LTU"}
    assert "dualband_nlos_failover_policy_v41" in data["cross_fleet_matrix_v41"]["2XC"]
    assert data["five_pillar_compliant"] is True
