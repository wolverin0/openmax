"""Tests for Stage 449A: airFiber AF-4X / AF-5X Invictus 2 TDD & Cyclic Prefix (CP) Safe Optimization Kit."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
KIT_PATH = REPO_ROOT / "firmware" / "openwrt" / "common" / "fmx_af4x_af5x_invictus2_tdd_cp_kit.sh"
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage449a_af4x_af5x_invictus2_tdd_tuning_kit.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE449A_AF4X_AF5X_INVICTUS2_TDD_TUNING_KIT.md"


def test_stage449a_kit_script_lf_and_af_commands():
    assert KIT_PATH.exists()
    raw = KIT_PATH.read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "af set framelength 2.5ms" in text
    assert "af set cp 8" in text
    assert "af set stricttiming on" in text
    assert "rollback" in text


def test_stage449a_receipt_integrates_stage388a_and_wave2():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "449A"
    attrs = data["architectural_reconciliation"]["af5xhd_ltu_beetle_family"]["kernel_module_params_verified_in_stage388a"]["tdd_and_cp_attributes"]
    assert "cpsample" in attrs
    assert "duty_cycle" in attrs
    assert data["live_bench_verified_gains_af4x_244"]["cumulative_p95_rtt_reduction_pct"] == 22.8
    assert "five_pillar_compliance" in data


def test_stage449a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
