from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
S297A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage297a_cross_fleet_champion_v42_receipt.json"
S297A_DOC = REPO_ROOT / "docs" / "STAGE297A_CROSS_FLEET_CHAMPION_V42.md"


def test_stage297a_cross_fleet_champion_v42() -> None:
    assert S297A_JSON.exists(), "Missing stage297a_cross_fleet_champion_v42_receipt.json"
    assert S297A_DOC.exists(), "Missing STAGE297A_CROSS_FLEET_CHAMPION_V42.md"

    doc_text = S297A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S297A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-297A"
    assert data["master_version"] == "v42.0"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert set(data["cross_fleet_matrix_v42"].keys()) == {"WA", "XC", "2XC", "XW", "XM", "LTU"}
    assert data["cross_fleet_matrix_v42"]["XC"]["mode_b_airos_champion_v42"]["bridge_nf_call_iptables"] == 0
    assert data["cross_fleet_matrix_v42"]["2XC"]["mode_b_airos_champion_v42"]["rmem_max"] == 262144
    assert data["cross_fleet_matrix_v42"]["XM"]["mode_b_airos_champion_v42"]["tcp_tso_win_divisor"] == 8
    assert data["five_pillar_compliant"] is True
