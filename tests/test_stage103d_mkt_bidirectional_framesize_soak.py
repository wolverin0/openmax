"""Verification suite for Stage 103D (`T-S103D-LIVE-MKT-BOCA7-BIDIRECTIONAL-RFC2544-AND-CAKE-DSCP-SOAK`)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "artifacts" / "autoresearch" / "stage103d_mkt_bidirectional_framesize_soak.json"
DOC_PATH = ROOT / "docs" / "STAGE103D_MKT_BIDIRECTIONAL_FRAMESIZE_SOAK.md"


def test_stage103d_json_receipt_and_safety_invariants() -> None:
    assert JSON_PATH.exists(), f"Missing Stage 103D receipt: {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "103D"
    assert data["task_id"] == "T-S103D-LIVE-MKT-BOCA7-BIDIRECTIONAL-RFC2544-AND-CAKE-DSCP-SOAK"
    assert data["protocol"] == "A1->B1->A2->B2"
    safety = data["safety_invariants"]
    assert safety["flash_writes"] == 0
    assert safety["pbe5ac_241_242_untouched"] is True
    assert safety["guarida_sg01_backbone_untouched"] is True
    assert safety["boca7_isolated_in_vlan107"] is True


def test_stage103d_rfc2544_framesizes_and_diffserv4_isolation() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    s = data["stage103d_rfc2544_diffserv4_summary"]
    assert s["frame_sizes_bytes"] == [64, 512, 1400]
    assert s["arm_b_64b_voice_p50_ms"] < s["arm_a_64b_voice_p50_ms"]
    assert s["arm_b_64b_voice_p99_ms"] < s["arm_a_64b_voice_p99_ms"]
    assert s["arm_b_1400b_be_p95_ms"] < s["arm_a_1400b_be_p95_ms"]
    assert s["arm_b_composite_e2e_p95_ms"] < s["arm_a_composite_e2e_p95_ms"]
    assert s["arm_b_sector_p95_rtt_ms"] < s["arm_a_sector_p95_rtt_ms"]
    assert s["pareto_delta_pct"] > 5.0
    assert len(data["rounds"]) == 1
    r0 = data["rounds"][0]
    assert set(r0["phases"].keys()) == {"A1", "B1", "A2", "B2"}


def test_stage103d_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing Stage 103D report: {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 180, f"Expected < 180 lines, got {len(lines)}"
    assert text.count("<!-- doc-head:") == 1
