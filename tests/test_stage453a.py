#!/usr/bin/env python3
"""Tests for Stage 453A — Guarida-BH (.61) 230M ast_rxorn Binary & Telemetry Dissection."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage453a_guarida_bh_230m_ast_rxorn_and_pcie_ce_ring_re.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE453A_GUARIDA_BH_230M_AST_RXORN_AND_PCIE_CE_RING_RE.md"


def test_stage453a_json_receipt() -> None:
    assert JSON_PATH.exists(), f"Missing {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "453A"
    assert data["status"] == "COMPLETED"
    assert data["claim_status"] == "CONFIRMED"
    assert data["writes_performed"] == 0

    funcs = data["binary_re_provenance"]["dissected_functions"]
    assert funcs["process_rx_stats"]["text_offset_hex"] == "0x0b4d64"
    assert "-0x1de0($fp)" in funcs["process_rx_stats"]["counter_increment"]
    assert funcs["ol_get_radio_stats"]["text_offset_hex"] == "0x0b5e20"

    corr = data["guarida_4radio_ast_rxorn_vs_rx_ppdu_correlation"]
    assert corr["guarida_bh_61"]["ast_rxorn_stage359a"] == 230722380
    assert corr["guarida_bh_61"]["ast_rxorn_to_rx_ppdu_ratio_pct"] > 90.0
    assert corr["almafuerte_60"]["5snapshot_delta_ratio_pct"] > 90.0


def test_stage453a_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"Doc has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1
