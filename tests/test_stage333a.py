from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S333A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage333a_ltu_7round_champion_v5_receipt.json"
S333A_MD = REPO_ROOT / "docs" / "STAGE333A_LTU_7ROUND_CHAMPION_V5.md"


def test_stage333a_ltu_7round_champion_v5() -> None:
    assert S333A_JSON.exists()
    assert S333A_MD.exists()
    data = json.loads(S333A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "333A"
    assert data["champion_version"] == "v5"
    assert data["total_live_campaigns"] == 7
    assert data["total_live_ab_rounds"] == 21
    assert data["total_live_measurement_windows"] == 84
    assert all(data["checks"].values())
    lines = S333A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
