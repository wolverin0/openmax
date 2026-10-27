from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S303A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage303a_ltu_6round_champion_v4_receipt.json"
S303A_MD = REPO_ROOT / "docs" / "STAGE303A_LTU_6ROUND_CHAMPION_V4.md"


def test_stage303a_ltu_6round_champion_v4() -> None:
    assert S303A_JSON.exists()
    assert S303A_MD.exists()
    data = json.loads(S303A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "303A"
    assert data["total_live_ab_rounds"] == 18
    assert data["total_live_measurement_windows"] == 72
    assert all(data["checks"].values())
    lines = S303A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
