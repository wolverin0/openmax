from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
S215A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage215a_live_xc_2xc_round4_stability.json"
S215A_DOC = REPO_ROOT / "docs" / "STAGE215A_LIVE_XC_2XC_ROUND4_STABILITY.md"
S216A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage216a_live_xm_nsm5_round4_oom_immunity.json"
S216A_DOC = REPO_ROOT / "docs" / "STAGE216A_LIVE_XM_NSM5_ROUND4_OOM_IMMUNITY.md"
S217A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage217a_cross_fleet_champion_v40_receipt.json"
S217A_DOC = REPO_ROOT / "docs" / "STAGE217A_CROSS_FLEET_CHAMPION_V40.md"


def test_stage215a_live_xc_2xc_round4_stability_receipt_and_doc() -> None:
    assert S215A_JSON.exists(), "Missing stage215a_live_xc_2xc_round4_stability.json"
    assert S215A_DOC.exists(), "Missing STAGE215A_LIVE_XC_2XC_ROUND4_STABILITY.md"

    doc_text = S215A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S215A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-215A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert data["safety_boundaries"]["flash_writes"] == 0
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert [w["window"] for w in r["windows"]] == ["A1", "B1", "A2", "B2"]
        for w in r["windows"]:
            assert w["under_load_rtt"]["samples"] >= 1
            assert w["mem_and_softirqs_198"]["mem_free_kb"] > 10000
    assert data["five_pillar_compliant"] is True


def test_stage216a_live_xm_nsm5_round4_oom_immunity_receipt_and_doc() -> None:
    assert S216A_JSON.exists(), "Missing stage216a_live_xm_nsm5_round4_oom_immunity.json"
    assert S216A_DOC.exists(), "Missing STAGE216A_LIVE_XM_NSM5_ROUND4_OOM_IMMUNITY.md"

    doc_text = S216A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S216A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-216A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert data["safety_boundaries"]["flash_writes"] == 0
    assert data["oom_immunity_verdict"]["oom_events_total"] == 0
    assert data["oom_immunity_verdict"]["kswapd_stalls_total"] == 0
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert [w["window"] for w in r["windows"]] == ["A1", "B1", "A2", "B2"]
        assert "arm_b_mean_p50_rtt_ms" in r
        assert "arm_b_mean_p95_rtt_ms" in r
        assert "arm_b_mean_p99_rtt_ms" in r
    assert data["five_pillar_compliant"] is True


def test_stage217a_cross_fleet_champion_v40_receipt_and_doc() -> None:
    assert S217A_JSON.exists(), "Missing stage217a_cross_fleet_champion_v40_receipt.json"
    assert S217A_DOC.exists(), "Missing STAGE217A_CROSS_FLEET_CHAMPION_V40.md"

    doc_text = S217A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S217A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-217A"
    assert data["master_version"] == "v40.0"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert set(data["cross_fleet_matrix_v40"].keys()) == {"WA", "XC", "2XC", "XW", "XM", "LTU"}
    assert "mode_a_openwrt_champion" in data["cross_fleet_matrix_v40"]["WA"]
    assert "mode_b_airos_champion" in data["cross_fleet_matrix_v40"]["WA"]
    assert data["five_pillar_compliant"] is True
