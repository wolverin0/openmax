"""Stage 403A verification tests — PB040 RAM Canary, nf_cal_period, and pktlog_filter R43..R45."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage403a_receipt_and_5pillar() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage403a_live_wa_pb040_ram_canary_and_nfcal_r43_45.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 403A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_wa_total_windows_including_e2e"] == 184
    assert len(data["rounds"]) == 3
    assert [r["round_id"] for r in data["rounds"]] == ["S403A-R43", "S403A-R44", "S403A-R45"]
    pb = data["pb040_live_ram_canary_verification"]
    assert pb["patched_fw_checksums"]["firmware-N.bin"] == "912bcb63"
    assert pb["patched_fw_checksums"]["athwlan"] == "278d2d76"
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
