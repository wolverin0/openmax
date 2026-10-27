from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S288A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage288a_ltu_auto_duty_cycle_scheduler_re.json"
S288A_MD = REPO_ROOT / "docs" / "STAGE288A_LTU_AUTO_DUTY_CYCLE_SCHEDULER_RE.md"


def test_stage288a_ltu_auto_duty_cycle_scheduler_re() -> None:
    assert S288A_JSON.exists()
    assert S288A_MD.exists()
    data = json.loads(S288A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "288A"
    assert data["safety_envelope"]["touched_dev_ame_nodes"] is False
    assert data["dynamic_split_duty_scheduler"]["supported_states_permille"] == [500, 670, 750]
    assert data["dynamic_split_duty_scheduler"]["extracted_scheduler_symbols_count"] > 20
    lines = S288A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
