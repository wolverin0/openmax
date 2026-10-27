from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S299A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage299a_live_ltu110_round6_voip_jitter.json"
S299A_MD = REPO_ROOT / "docs" / "STAGE299A_LIVE_LTU110_ROUND6_VOIP_JITTER.md"


def test_stage299a_live_ltu110_round6_voip_jitter() -> None:
    assert S299A_JSON.exists()
    assert S299A_MD.exists()
    data = json.loads(S299A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "299A"
    assert data["protocol"] == "A1 -> B1 -> A2 -> B2"
    assert data["watchdog_seconds"] == 45
    assert data["safety_envelope"]["touched_dev_ame_nodes"] is False
    assert data["safety_envelope"]["touched_forbidden_hosts_241_242_20_250"] is False
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert set(r["phases"].keys()) == {"A1", "B1", "A2", "B2"}
        assert r["summary"]["winner"] == "B_CHAMPION"
    lines = S299A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
