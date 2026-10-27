from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
S182A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage182a_live_xc_2xc_round2_autoresearch.json"
S182A_DOC = REPO_ROOT / "docs" / "STAGE182A_LIVE_XC_2XC_ROUND2_AUTORESEARCH.md"
S183A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage183a_live_xm_nsm5_round2_autoresearch.json"
S183A_DOC = REPO_ROOT / "docs" / "STAGE183A_LIVE_XM_NSM5_ROUND2_AUTORESEARCH.md"
S184A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage184a_cross_fleet_champion_v38_receipt.json"


def test_stage182a_live_xc_2xc_round2_receipt_and_doc() -> None:
    assert S182A_JSON.exists(), "Missing stage182a_live_xc_2xc_round2_autoresearch.json"
    assert S182A_DOC.exists(), "Missing STAGE182A_LIVE_XC_2XC_ROUND2_AUTORESEARCH.md"

    doc_text = S182A_DOC.read_text(encoding="utf-8")
    doc_lines = doc_text.splitlines()
    assert len(doc_lines) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S182A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-182A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert data["safety_boundaries"]["flash_writes"] == 0
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert [w["window"] for w in r["windows"]] == ["A1", "B1", "A2", "B2"]
        for w in r["windows"]:
            assert w["under_load_rtt"]["samples"] >= 1
    assert data["five_pillar_compliant"] is True


def test_stage183a_live_xm_nsm5_round2_receipt_and_doc() -> None:
    assert S183A_JSON.exists(), "Missing stage183a_live_xm_nsm5_round2_autoresearch.json"
    assert S183A_DOC.exists(), "Missing STAGE183A_LIVE_XM_NSM5_ROUND2_AUTORESEARCH.md"

    doc_text = S183A_DOC.read_text(encoding="utf-8")
    doc_lines = doc_text.splitlines()
    assert len(doc_lines) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S183A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-183A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert data["safety_boundaries"]["flash_writes"] == 0
    assert data["bench_xm_topology"]["boca2_nanostation_xm"]["lan_ip"] == "192.168.1.20"
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert [w["window"] for w in r["windows"]] == ["A1", "B1", "A2", "B2"]
        for w in r["windows"]:
            assert w["boca2_xm_1_20_rtt"]["samples"] >= 1
    assert data["five_pillar_compliant"] is True


def test_stage184a_cross_fleet_champion_v38_receipt() -> None:
    assert S184A_JSON.exists(), "Missing stage184a_cross_fleet_champion_v38_receipt.json"
    data = json.loads(S184A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-184A"
    assert data["status"] == "PASS"
    assert data["master_version"] == "v38.0"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert set(data["families"].keys()) == {"WA", "XC", "2XC", "XW", "XM", "LTU"}
    assert data["five_pillar_compliant"] is True
