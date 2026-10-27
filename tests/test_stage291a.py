from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S291A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage291a_ltu_5round_champion_v3_receipt.json"
S291A_MD = REPO_ROOT / "docs" / "STAGE291A_LTU_5ROUND_CHAMPION_V3.md"


def test_stage291a_ltu_5round_champion_v3() -> None:
    assert S291A_JSON.exists()
    assert S291A_MD.exists()
    data = json.loads(S291A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "291A"
    assert data["total_live_ab_rounds"] == 15
    assert data["total_live_measurement_windows"] == 60
    assert all(data["checks"].values())
    lines = S291A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
