#!/usr/bin/env python3
"""Stage 536A — Consolidated Verification Suite for Stages 531A..536A
(`SOSA_Joaquin` `16.26 dB` EVM Gap at `0 dB` RSSI Diff, `athbox` vs `umac.ko` 25-Field
`scn_stats` Aliasing Map, `ubnt_poll_host_set_node_rtt` `150*rtt_us` & `rtt_us+21` Slot Guard,
`Panel1 .84` `OpenWrt 24.10.4` `1.227%` Retry / `19.31h` Hybrid Uptime, Guarida `34`-Endpoint
Maintenance Dossier `v3`, and `FMX-DISC-49/50` Curation).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage536a_guarida_scn_stats_and_64evm_gate import build_stage536a_report

REPO_ROOT = Path(__file__).resolve().parents[1]

STAGE_JSONS = [
    ("531A", REPO_ROOT / "artifacts" / "autoresearch" / "stage531a_guarida_panel2_panel3_per_cpe_64evm_forensics.json"),
    ("532A", REPO_ROOT / "artifacts" / "autoresearch" / "stage532a_athbox_vs_umac_scn_stats_aliasing_map.json"),
    ("533A", REPO_ROOT / "artifacts" / "autoresearch" / "stage533a_ubnt_poll_swr_limit_and_slot_guard_re.json"),
    ("534A", REPO_ROOT / "artifacts" / "autoresearch" / "stage534a_panel1_guarida_84_openwrt_per_sta_airtime_and_rc.json"),
    ("535A", REPO_ROOT / "artifacts" / "autoresearch" / "stage535a_guarida_34endpoint_zero_fp_maintenance_dossier_v3.json"),
    ("536A", REPO_ROOT / "artifacts" / "verification" / "stage536a_guarida_scn_stats_and_64evm_gate_receipt.json"),
]

STAGE_DOCS = [
    REPO_ROOT / "docs" / "STAGE531A_GUARIDA_PANEL2_PANEL3_PER_CPE_64EVM_FORENSICS.md",
    REPO_ROOT / "docs" / "STAGE532A_ATHBOX_VS_UMAC_SCN_STATS_ALIASING_MAP.md",
    REPO_ROOT / "docs" / "STAGE533A_UBNT_POLL_SWR_LIMIT_AND_SLOT_GUARD_RE.md",
    REPO_ROOT / "docs" / "STAGE534A_PANEL1_GUARIDA_84_OPENWRT_PER_STA_AIRTIME_AND_RC.md",
    REPO_ROOT / "docs" / "STAGE535A_GUARIDA_34ENDPOINT_ZERO_FP_MAINTENANCE_DOSSIER_V3.md",
    REPO_ROOT / "docs" / "STAGE536A_GUARIDA_SCN_STATS_AND_64EVM_GATE.md",
    REPO_ROOT / "docs" / "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md",
]


@pytest.mark.parametrize(("expected_stage", "json_path"), STAGE_JSONS)
def test_stage531a_to_536a_receipts_and_5pillars(expected_stage: str, json_path: Path) -> None:
    assert json_path.exists(), f"Missing receipt: {json_path}"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["stage"] == expected_stage
    assert data["status"] == "COMPLETED"
    assert data["claim_status"] == "CONFIRMED"
    assert data["writes_performed"] == 0
    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, gate


@pytest.mark.parametrize("doc_path", STAGE_DOCS)
def test_stage531a_to_536a_markdown_line_budget_and_doc_head(doc_path: Path) -> None:
    assert doc_path.exists(), f"Missing doc: {doc_path}"
    text = doc_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"{doc_path.name} has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1, f"{doc_path.name} must have exactly 1 doc-head comment"


def test_stage536a_consolidated_suite_and_curated_discoveries() -> None:
    report = build_stage536a_report()
    assert report["all_checks_passed"] is True
    assert report["curated_discoveries_verified"]["FMX-DISC-49"] is True
    assert report["curated_discoveries_verified"]["FMX-DISC-50"] is True
