"""Tests for Stage 513A: QCA988x DFS False-Radar Pulse Discriminator & 120s CAC Watchdog Helper (FMX-DISC-24)."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER_SH_PATH = REPO_ROOT / "firmware" / "openwrt" / "common" / "fmx_qca988x_dfs_immunity_helper.sh"
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage513a_qca988x_dfs_false_radar_immunity_helper.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE513A_QCA988X_DFS_FALSE_RADAR_IMMUNITY_HELPER.md"


def test_stage513a_helper_script_lf_and_disc24():
    assert HELPER_SH_PATH.exists()
    raw = HELPER_SH_PATH.read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "5250" in text and "5720" in text
    assert "echo 120" in text and "echo 45" in text
    assert "nf_cal_period" in text


def test_stage513a_receipt_integrates_stage485a():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "513A"
    assert data["fmx_disc_24_watchdog_sec" if "fmx_disc_24_watchdog_sec" in data else "fmx_disc_24_watchdog_contract"]["dfs_unii2_watchdog_sec"] == 120
    assert data["fmx_disc_24_watchdog_contract"]["non_dfs_watchdog_sec"] == 45
    assert "ieee80211_add_ubnt_csa" in data["stage485a_csa_and_bmiss_re_integration"]["csa_symbols_verified"]
    assert data["safety_boundaries"]["regulatory_dfs_bypass_attempted"] is False
    assert "five_pillar_compliance" in data


def test_stage513a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
