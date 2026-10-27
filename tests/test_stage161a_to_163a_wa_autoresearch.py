"""Pytest verification suite for Stage 161A, Stage 162A, and Stage 163A Continuous WA Autoresearch Megamission."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
ART_161A = ROOT / "artifacts" / "autoresearch" / "stage161a_live_wa_round16_18_autoresearch.json"
ART_162A = ROOT / "artifacts" / "autoresearch" / "stage162a_live_wa_e2e_forwarding_offload_benchmark.json"
ART_163A = ROOT / "artifacts" / "autoresearch" / "stage163a_cumulative_18round_wa_champion_v2.json"
DOC_161A = ROOT / "docs" / "STAGE161A_LIVE_WA_ROUND16_18_AUTORESEARCH.md"
DOC_162A = ROOT / "docs" / "STAGE162A_LIVE_WA_E2E_FORWARDING_OFFLOAD_BENCHMARK.md"
DOC_163A = ROOT / "docs" / "STAGE163A_CUMULATIVE_18ROUND_WA_CHAMPION_V2.md"
CHAMPION_SH = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion"


def test_stage161a_round16_to_18_and_5pillar() -> None:
    assert ART_161A.exists()
    d = json.loads(ART_161A.read_text(encoding="utf-8"))
    assert d["stage"] == "Stage 161A"
    assert d["status"] == "CONFIRMED"
    assert d["cumulative_wa_live_windows_r1_to_r18"] == 72
    assert d["safety_boundaries"]["touched_241_or_242"] is False
    assert d["safety_boundaries"]["flash_writes"] == 0
    assert [r["round_id"] for r in d["rounds"]] == ["S161A-R16", "S161A-R17", "S161A-R18"]
    for r in d["rounds"]:
        assert [w["window"] for w in r["windows"]] == ["A1", "B1", "A2", "B2"]
        for w in r["windows"]:
            assert w["goodput_mbps"] > 0.0
            assert 0.0 < w["under_load_rtt"]["p50_ms"] < 250.0
            assert w["ap_mem_available_mb"] > 8.0
            assert w["cpe_mem_available_mb"] > 5.0
    assert audit_stage_receipt_5pillars(d)["compliant"] is True


def test_stage162a_e2e_forwarding_and_5pillar() -> None:
    assert ART_162A.exists()
    d = json.loads(ART_162A.read_text(encoding="utf-8"))
    assert d["stage"] == "Stage 162A"
    assert d["status"] == "CONFIRMED"
    assert d["safety_boundaries"]["touched_241_or_242"] is False
    assert len(d["rounds"]) == 1
    r = d["rounds"][0]
    assert r["round_id"] == "S162A-E2E-R1"
    assert [w["window"] for w in r["windows"]] == ["A1", "B1", "A2", "B2"]
    for w in r["windows"]:
        assert w["goodput_mbps"] > 0.0
        assert "boca7_e2e_rtt" in w
        assert w["boca7_e2e_rtt"]["p50_ms"] > 0.0
    assert audit_stage_receipt_5pillars(d)["compliant"] is True


def test_stage163a_cumulative_18round_champion_and_docs() -> None:
    assert ART_163A.exists()
    d = json.loads(ART_163A.read_text(encoding="utf-8"))
    assert d["stage"] == "Stage 163A"
    assert d["status"] == "CONFIRMED"
    assert d["total_counterbalanced_rounds"] == 18
    assert d["total_live_wa_triple_play_windows"] == 72
    assert d["total_live_windows_including_stage162a_e2e"] == 76
    assert len(d["rounds_r1_to_r18_ledger"]) == 18
    assert audit_stage_receipt_5pillars(d)["compliant"] is True

    for doc in (DOC_161A, DOC_162A, DOC_163A):
        assert doc.exists(), f"Missing doc: {doc}"
        txt = doc.read_text(encoding="utf-8")
        assert len(txt.splitlines()) < 220
        assert txt.count("<!-- doc-head:") == 1

    sh_txt = CHAMPION_SH.read_text(encoding="utf-8")
    assert "FMX_MIN_FREE_KBYTES" in sh_txt
    assert "FMX_AQL_THRESHOLD" in sh_txt
    assert "FMX_DISTANCE_M" in sh_txt
    assert "FMX_TCP_PACING_CA_RATIO" in sh_txt
