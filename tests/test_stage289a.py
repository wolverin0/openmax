from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S289A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage289a_ltu_mimo_xpic_txbf_re.json"
S289A_MD = REPO_ROOT / "docs" / "STAGE289A_LTU_MIMO_XPIC_TXBF_RE.md"


def test_stage289a_ltu_mimo_xpic_txbf_re() -> None:
    assert S289A_JSON.exists()
    assert S289A_MD.exists()
    data = json.loads(S289A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "289A"
    assert data["safety_envelope"]["touched_dev_ame_nodes"] is False
    mimo = data["mimo_matrix_and_xpic_architecture"]
    assert len(mimo["siso_to_mimo_hysteresis_thresholds"]["autoMcsMimoTP_u16"]) == 5
    assert mimo["extracted_mimo_bbp_symbols_count"] > 20
    lines = S289A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
