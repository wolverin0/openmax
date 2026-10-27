"""Tests for Stage 480A: Guarida Backbone (.60 <-> .61) Subcarrier-51 Multipath Notch & 230.7M ast_rxorn Mitigation Kit."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
KIT_PATH = REPO_ROOT / "firmware" / "guarida_safe_kits" / "rc.poststart_backbone_60_61_notch_rescue.sh"
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage480a_guarida_backbone_60_61_subcarrier51_notch_rescue.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE480A_GUARIDA_BACKBONE_60_61_SUBCARRIER51_NOTCH_RESCUE.md"


def test_stage480a_kit_script_lf_and_knobs():
    assert KIT_PATH.exists()
    raw = KIT_PATH.read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "netdev_budget=600" in text
    assert "shortgi 0" in text
    assert "rollback" in text


def test_stage480a_receipt_integrates_stage419a():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "480A"
    b60 = data["stage419a_backbone_radiography"]["almafuerte_60"]
    assert b60["chain0_min_subcarrier_idx"] == 51
    assert b60["chain0_multipath_notch_depth_db"] == 6.45
    assert data["stage419a_backbone_radiography"]["guarida_bh_61"]["cumulative_ast_rxorn_overruns"] == 230_700_000
    assert data["safety_boundaries"]["sg01_guarida_backbone_respected"] is True
    assert "five_pillar_compliance" in data


def test_stage480a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
