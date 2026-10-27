"""Tests for Stage 448A: XW (M5 AR9344) Maximum Ratio Combining (MRC) & Adaptive Noise Immunity (ANI) Champion Kit."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
KIT_PATH = REPO_ROOT / "firmware" / "openwrt" / "common" / "fmx_xw_ar9344_mrc_ani_champion.sh"
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage448a_xw_ar9344_mrc_and_ani_champion_kit.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE448A_XW_AR9344_MRC_AND_ANI_CHAMPION_KIT.md"


def test_stage448a_kit_script_lf_and_symbols():
    assert KIT_PATH.exists()
    raw = KIT_PATH.read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "rxchainmask 3" in text
    assert "ewma_delegate_on" in text
    assert "ath9k/ani" in text


def test_stage448a_receipt_integrates_stage396a():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "448A"
    assert data["re_symbol_integration"]["modules_verified"] == 8
    assert "ar9300_is_ani_noise_spur" in data["re_symbol_integration"]["ath_hal_ani_symbols"]
    assert "ath_set_rx_chainmask" in data["re_symbol_integration"]["ath_dev_chainmask_symbols"]
    assert data["bench_proven_anchors"]["p95_rtt_reduction_pct"] == 68.0
    assert "five_pillar_compliance" in data


def test_stage448a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
