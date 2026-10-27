"""Pytest suite for Stage 661A WA Champion v11 (284-Window) Field Rollout Kit."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage661a_kit_and_receipt():
    helper = ROOT / "firmware" / "openwrt" / "common" / "fmx_wa_v11_284window_field_kit.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage661a_wa_champion_v11_284window_field_rollout_kit.json"
    assert helper.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "661A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_wa_windows"] == 284
    p = data["parameters"]
    assert p["bql_limit_max_bytes"] == 15140
    assert p["aql_txq_limit_low_us"] == 2000
    assert p["aql_txq_limit_high_us"] == 4000
    assert p["fq_codel_quantum_bytes"] == 3028
    assert p["fq_codel_initial_quantum_bytes"] == 15140


def test_stage661a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE661A_WA_CHAMPION_V11_284WINDOW_FIELD_ROLLOUT_KIT.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
