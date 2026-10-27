"""Tests for Stage 447A: SimPy + pymoo NSGA-II Evaluation of Pillar 3 50-us Xtensa Hardware Try #2 Fallback (WMI 0x9044)."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage447a_wmi_0x9044_50us_hardware_retry_pareto.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE447A_WMI_0X9044_50US_HARDWARE_RETRY_PARETO.md"


def test_stage447a_pareto_gain_over_host_8ms():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "447A"
    assert data["wmi_command_spec"]["cmd_id"] == "0x9044"
    assert data["wmi_command_spec"]["hardware_turnaround_us"] == 50.0
    assert data["comparative_deltas"]["goodput_gain_pct"] > 50.0
    assert data["comparative_deltas"]["p99_latency_reduction_pct"] > 50.0
    assert len(data["pareto_front"]) >= 1
    assert "five_pillar_compliance" in data


def test_stage447a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
