"""Tests for Stage 546A: LTU TX Power LUT, PA DPD & Super4096 Safe Telemetry Monitor Helper."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MONITOR_SH_PATH = REPO_ROOT / "firmware" / "ltu_safe_kit" / "fmx_ltu_dpd_super4096_monitor.sh"
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage546a_ltu_tx_power_lut_dpd_and_super4096_helper.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE546A_LTU_TX_POWER_LUT_DPD_AND_SUPER4096_HELPER.md"


def test_stage546a_monitor_script_lf_and_symbols():
    assert MONITOR_SH_PATH.exists()
    raw = MONITOR_SH_PATH.read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    for sym in ("bbp_rf_set_super4096", "ame_bbp_set_dpd", "ame_bbp_set_pa", "ptmp_ap_autopwr_tx_power_adjust_routine"):
        assert sym in text


def test_stage546a_receipt_integrates_stage544a():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "546A"
    assert data["monitor_artifact"]["zero_dev_ame_touches"] is True
    s544 = data["stage544a_re_integration"]
    assert "bbp_rf_set_super4096" in s544["super4096_symbols"]
    assert "ame_bbp_set_dpd" in s544["dpd_symbols"]
    assert "five_pillar_compliance" in data


def test_stage546a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
