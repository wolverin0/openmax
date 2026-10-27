"""Tests for Stage 545A: QCA988x ANI Firstep & Spur Immunity Helper."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER_SH_PATH = REPO_ROOT / "firmware" / "openwrt" / "common" / "fmx_qca988x_ani_spur_helper.sh"
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage545a_qca988x_ani_firstep_and_spur_immunity_helper.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE545A_QCA988X_ANI_FIRSTEP_AND_SPUR_IMMUNITY_HELPER.md"


def test_stage545a_helper_lf_and_wmi_params():
    assert HELPER_SH_PATH.exists()
    raw = HELPER_SH_PATH.read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    for hex_id in ("0x900d", "0x900e", "0x900f"):
        assert hex_id in text
    assert "ani_enable" in text
    assert "ani_ofdm_level" in text


def test_stage545a_receipt_integrates_stage543a():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "545A"
    assert data["wmi_pdev_ani_parameters"]["WMI_PDEV_PARAM_ANI_ENABLE"] == "0x900d"
    assert data["stage543a_re_integration"]["modules_analyzed"] == 7
    assert "ar9300_ani_control" in data["stage543a_re_integration"]["hal_ani_lifecycle_symbols"]
    assert "five_pillar_compliance" in data


def test_stage545a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
