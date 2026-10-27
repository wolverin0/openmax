"""Verification suite for Stage 101A (`T-S101A-CHAMPION-V23-WDS-CHURN-HEALER-DAEMON-AND-SOAK`)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "artifacts" / "autoresearch" / "stage101a_champion_v23_wds_churn_healer_benchmark.json"
DOC_PATH = ROOT / "docs" / "STAGE101A_CHAMPION_V23_WDS_CHURN_HEALER_PROOF.md"
PANEL1_ADMITTER = ROOT / "tools" / "panel1" / "panel1_admitter.sh"


def test_stage101a_panel1_admitter_has_wds_healer() -> None:
    text = PANEL1_ADMITTER.read_text(encoding="utf-8")
    assert "heal_stale_wds_and_reapply_qos" in text
    assert "FMX_S101A_STALE_WDS_FLUSH" in text


def test_stage101a_json_receipt_and_safety_invariants() -> None:
    assert JSON_PATH.exists(), f"Missing Stage 101A receipt: {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "101A"
    assert data["task_id"] == "T-S101A-CHAMPION-V23-WDS-CHURN-HEALER-DAEMON-AND-SOAK"
    assert data["protocol"] == "A1->B1->A2->B2"
    safety = data["safety_invariants"]
    assert safety["flash_writes"] == 0
    assert safety["pbe5ac_241_242_untouched"] is True
    assert safety["guarida_sg01_backbone_untouched"] is True
    assert safety["boca7_isolated_in_vlan107"] is True


def test_stage101a_autonomous_healer_and_survivor_qoe() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    s = data["stage101a_wds_healer_summary"]
    assert s["daemon_path_on_ap"] == "/usr/sbin/fmx_wds_churn_healer.sh"
    assert s["arm_b_survivor_wa_to_mk1_p95_ms"] < 8.0
    assert s["arm_b_survivor_wa_to_mk1_p95_ms"] < s["arm_a_survivor_wa_to_mk1_p95_ms"]
    assert s["arm_b_survivor_loss_pct"] == 0.0
    assert s["arm_b_auto_heal_recovery_ms"] < s["arm_a_auto_heal_recovery_ms"]
    assert len(data["rounds"]) == 1
    r0 = data["rounds"][0]
    assert set(r0["phases"].keys()) == {"A1", "B1", "A2", "B2"}


def test_stage101a_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing Stage 101A report: {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 180, f"Expected < 180 lines, got {len(lines)}"
    assert text.count("<!-- doc-head:") == 1
