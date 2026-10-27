#!/usr/bin/env python3
"""Stage 422A — Consolidated Verification Suite for Stages 417A..422A
(Guarida `ubnt_poll` Contention Window `cbp_dur`, `local_enqued` `MCS 2` Storm,
64-Subcarrier EVM Notch/Tilt Radiography, NSGA-II Joint Pareto, & `FMX-DISC-45/46`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

STAGE_JSONS = [
    ("417A", REPO_ROOT / "artifacts" / "autoresearch" / "stage417a_ubnt_poll_cbp_dur_and_probereq_hash_re.json"),
    ("418A", REPO_ROOT / "artifacts" / "autoresearch" / "stage418a_panel3_local_enqued_mcs2_storm_re.json"),
    ("419A", REPO_ROOT / "artifacts" / "autoresearch" / "stage419a_guarida_subcarrier_evm_notch_tilt.json"),
    ("420A", REPO_ROOT / "artifacts" / "autoresearch" / "stage420a_panel2_panel3_joint_tdma_pareto.json"),
    ("421A", REPO_ROOT / "artifacts" / "autoresearch" / "stage421a_fmx_disc_45_46_curation_receipt.json"),
]

STAGE_DOCS = [
    REPO_ROOT / "docs" / "STAGE417A_UBNT_POLL_CBP_DUR_AND_PROBEREQ_HASH_RE.md",
    REPO_ROOT / "docs" / "STAGE418A_PANEL3_LOCAL_ENQUED_MCS2_STORM_RE.md",
    REPO_ROOT / "docs" / "STAGE419A_GUARIDA_SUBCARRIER_EVM_NOTCH_TILT.md",
    REPO_ROOT / "docs" / "STAGE420A_PANEL2_PANEL3_JOINT_TDMA_PARETO.md",
    REPO_ROOT / "docs" / "STAGE421A_FMX_DISC_45_46_CURATION.md",
    REPO_ROOT / "docs" / "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md",
]


@pytest.mark.parametrize(("expected_stage", "json_path"), STAGE_JSONS)
def test_stage417a_to_421a_receipts_and_5pillars(expected_stage: str, json_path: Path) -> None:
    assert json_path.exists(), f"Missing receipt: {json_path}"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["stage"] == expected_stage
    assert data["status"] == "COMPLETED"
    assert data["claim_status"] == "CONFIRMED"
    assert data["writes_performed"] == 0

    pillars = data["five_pillar_compliance"]
    for key in [
        "pillar_a_ground_up_re_and_knob_catalog",
        "pillar_b_hyperresearch_and_scholar_reactor",
        "pillar_c_karpathy_autoresearch_and_watchdog",
        "pillar_d_scientific_pareto_validation",
        "pillar_e_memory_master_claim_id",
    ]:
        assert key in pillars and pillars[key], f"Missing {key} in {json_path.name}"


@pytest.mark.parametrize("doc_path", STAGE_DOCS)
def test_stage417a_to_421a_markdown_line_budget_and_doc_head(doc_path: Path) -> None:
    assert doc_path.exists(), f"Missing doc: {doc_path}"
    text = doc_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"{doc_path.name} has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1, f"{doc_path.name} must have exactly 1 doc-head comment"


def test_cross_stage_invariants_417a_to_421a() -> None:
    s417 = json.loads(STAGE_JSONS[0][1].read_text(encoding="utf-8"))
    s418 = json.loads(STAGE_JSONS[1][1].read_text(encoding="utf-8"))
    s419 = json.loads(STAGE_JSONS[2][1].read_text(encoding="utf-8"))
    s420 = json.loads(STAGE_JSONS[3][1].read_text(encoding="utf-8"))
    s421 = json.loads(STAGE_JSONS[4][1].read_text(encoding="utf-8"))

    assert s417["cbp_dur_panel2_vs_panel3_comparison"]["panel2_82"]["cbp_dur_us"] == 180
    assert s417["cbp_dur_panel2_vs_panel3_comparison"]["panel3_83"]["cbp_dur_us"] == 900
    assert s418["guarida_4radio_local_enqued_comparison"]["panel3_83"]["local_enqued"] == 674501176
    assert s419["summary_metrics"]["total_subcarrier_samples"] == 3072
    assert s420["deltas_vs_baseline"]["joint_goodput_gain_mbps"] > 40.0
    assert s421["curated_doc_verification"]["has_fmx_disc_45"] is True
    assert s421["curated_doc_verification"]["has_fmx_disc_46"] is True
