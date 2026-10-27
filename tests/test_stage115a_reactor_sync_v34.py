from __future__ import annotations

import json

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage115a_reactor_sync_v34 import (
    RECEIPT_PATH,
    collect_stage100_to_114_receipts,
    verify_stage115a,
)


def test_stage115a_reactor_sync_v34_all_receipts_compliant() -> None:
    receipt = verify_stage115a()
    assert RECEIPT_PATH.exists()
    saved = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))

    assert saved["stage_id"] == "Stage 115A"
    assert saved["curation_version"] == "v34.0"
    assert saved["live_hardware_contact_241_242"] is False
    assert saved["hardware_ips_touched"] == []
    assert saved["audited_receipt_count"] >= 22
    assert saved["all_receipts_5pillar_compliant"] is True
    assert saved["enqueued_stage100_to_114_count"] == saved["audited_receipt_count"]
    assert saved["repo_deterministic_gate"]["compliant"] is True

    self_audit = audit_stage_receipt_5pillars(saved)
    assert self_audit["compliant"] is True
    assert self_audit["missing_pillars"] == []

    for p in collect_stage100_to_114_receipts():
        data = json.loads(p.read_text(encoding="utf-8"))
        gate = audit_stage_receipt_5pillars(data)
        assert gate["compliant"] is True, f"{p.name} failed 5-pillar gate: {gate}"
