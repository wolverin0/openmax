from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S287A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage287a_live_ltu110_round5_autoresearch.json"
S287A_MD = REPO_ROOT / "docs" / "STAGE287A_LIVE_LTU110_ROUND5_AUTORESEARCH.md"


def test_stage287a_live_ltu110_round5_autoresearch() -> None:
    assert S287A_JSON.exists(), f"Missing {S287A_JSON}"
    assert S287A_MD.exists(), f"Missing {S287A_MD}"
    data = json.loads(S287A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "287A"
    assert data["status"] == "CONFIRMED"
    assert data["protocol"] == "A1 -> B1 -> A2 -> B2"
    assert data["watchdog_seconds"] == 45
    assert data["safety_envelope"]["touched_dev_ame_nodes"] is False
    assert data["safety_envelope"]["touched_forbidden_hosts_241_242_20_250"] is False
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert set(r["phases"].keys()) == {"A1", "B1", "A2", "B2"}
        assert r["summary"]["winner"] == "B_CHAMPION"

    lines = S287A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
