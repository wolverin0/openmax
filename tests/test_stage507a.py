"""Stage 507A verification suite (R50..R52 = 212 cumulative live windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage507a_receipt_and_pb050_live_fw_checksums() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage507a_live_wa_pb050_rc_probe_dampen_and_slot_r50_52.json"
    assert p.exists(), "Missing stage507a receipt"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 507A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["cumulative_wa_total_windows_including_e2e"] == 212
    assert data["pb050_live_ram_seg2_verification"]["pb050_fw_checksums"]["firmware-N.bin"] == "92363606"
    assert data["pb050_live_ram_seg2_verification"]["pb050_fw_checksums"]["athwlan"] == "12b29d01"
    assert len(data["rounds"]) == 3
    res = audit_stage_receipt_5pillars(data)
    assert res["compliant"] is True, f"5-pillar failure: {res['failures']}"
