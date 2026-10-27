from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S401A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage401a_ltu_10round_120window_champion_v8_receipt.json"
S401A_MD = REPO_ROOT / "docs" / "STAGE401A_LTU_10ROUND_120WINDOW_CHAMPION_V8.md"


def test_stage401a_ltu_10round_120window_champion_v8() -> None:
    assert S401A_JSON.exists()
    assert S401A_MD.exists()
    data = json.loads(S401A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "401A"
    assert data["champion_version"] == "v8"
    assert data["total_live_campaigns"] == 10
    assert data["total_live_ab_rounds"] == 30
    assert data["total_live_measurement_windows"] == 120
    assert all(data["checks"].values())
    lines = S401A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
