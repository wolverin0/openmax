"""Pytest suite for Stage 644A Zero-FP Observability Engine v5 (25-Field athstats + 64-EVM)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage644a_engine_v5_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage644a_zero_fp_observability_engine_v5_25field_athstats.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "644A"
    assert data["status"] == "CONFIRMED"
    a = data["stage532a_athstats_audit"]
    assert a["struct_size_bytes"] == 784
    assert a["total_audited_fields"] == 25
    assert a["genuine_rate_normalized_fields"] == 19
    assert a["always_zero_target_offload_fields"] == 3
    assert a["struct_aliased_bogus_fields"] == 3
    assert len(data["stage531a_64evm_detectors"]) == 2


def test_stage644a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE644A_ZERO_FP_OBSERVABILITY_ENGINE_V5_25FIELD_ATHSTATS.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
