from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage377a_ltu_subband_cinr_puncturing_re() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage377a_ltu_subband_cinr_puncturing_re.json"
    doc_path = ROOT / "docs/STAGE377A_LTU_SUBBAND_CINR_PUNCTURING_RE.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "377A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_audit"]["touched_dev_ame_nodes"] is False
    arch = data["subband_cinr_and_puncturing_architecture"]
    assert arch["subbands_per_channel"] == 8
    assert arch["modulation_cinr_thresholds_db"]["12x_4096QAM_9_10"] == 38.0
    assert data["cinr_subband_symbol_count"] > 20

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
