from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S345A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage345a_ltu_8round_champion_v6_receipt.json"
S345A_MD = REPO_ROOT / "docs" / "STAGE345A_LTU_8ROUND_CHAMPION_V6.md"


def test_stage345a_ltu_8round_champion_v6() -> None:
    assert S345A_JSON.exists()
    assert S345A_MD.exists()
    data = json.loads(S345A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "345A"
    assert data["champion_version"] == "v6"
    assert data["total_live_campaigns"] == 8
    assert data["total_live_ab_rounds"] == 24
    assert data["total_live_measurement_windows"] == 96
    assert all(data["checks"].values())
    lines = S345A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
