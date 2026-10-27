from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
S296A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage296a_xc_2xc_xm_24window_scorecard.json"
S296A_DOC = REPO_ROOT / "docs" / "STAGE296A_XC_2XC_XM_24WINDOW_SCORECARD.md"


def test_stage296a_xc_2xc_xm_24window_scorecard() -> None:
    assert S296A_JSON.exists(), "Missing stage296a_xc_2xc_xm_24window_scorecard.json"
    assert S296A_DOC.exists(), "Missing STAGE296A_XC_2XC_XM_24WINDOW_SCORECARD.md"

    doc_text = S296A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S296A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-296A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    for fam in ("XC_198", "2XC_253", "XM_1_20"):
        card = data["scorecards"][fam]
        assert card["selected_champion_rounds_count"] == 6
        assert card["selected_champion_windows_count"] == 24
        assert card["cumulative_subrounds_count"] == 18
        assert card["cumulative_physical_windows_count"] == 72
    assert data["five_pillar_compliant"] is True
