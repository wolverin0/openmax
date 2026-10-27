from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S379A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage379a_ltu_9round_champion_v7_receipt.json"
S379A_MD = REPO_ROOT / "docs" / "STAGE379A_LTU_9ROUND_CHAMPION_V7.md"


def test_stage379a_ltu_9round_champion_v7() -> None:
    assert S379A_JSON.exists()
    assert S379A_MD.exists()
    data = json.loads(S379A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "379A"
    assert data["champion_version"] == "v7"
    assert data["total_live_campaigns"] == 9
    assert data["total_live_ab_rounds"] == 27
    assert data["total_live_measurement_windows"] == 108
    assert all(data["checks"].values())
    lines = S379A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
