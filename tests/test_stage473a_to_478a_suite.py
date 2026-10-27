from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage478a_xtensa_pb050_and_wal_peer_suite import (
    OUT_JSON,
    STAGE_ARTIFACTS,
    STAGE_DOCS,
    build_stage478a_suite_receipt,
)


def test_stage473a_to_478a_consolidated_suite() -> None:
    rep = build_stage478a_suite_receipt()
    assert OUT_JSON.exists()
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "478A"
    assert loaded["status"] == "CONFIRMED"
    assert loaded["live_devices_touched"] is False

    for stage_id, art_path in STAGE_ARTIFACTS.items():
        assert art_path.exists(), f"Missing {stage_id} artifact"
        art_data = json.loads(art_path.read_text(encoding="utf-8"))
        assert art_data["live_devices_touched"] is False
        assert audit_stage_receipt_5pillars(art_data)["compliant"] is True

    for stage_id, doc_path in STAGE_DOCS.items():
        assert doc_path.exists(), f"Missing {stage_id} doc"
        lines = doc_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) < 220
        assert lines[0].startswith("<!-- doc-head:")

    highlights = loaded["consolidated_highlights"]
    assert highlights["stage473a_firmwares_mapped"] == 10
    assert highlights["stage474a_sgmt_images_patched"] == 7
    assert highlights["stage475a_wal_peer_slots_dissected"] == 33
    assert highlights["stage476a_ht_comm_slots_dissected"] == 51
    assert highlights["stage477a_pb050_goodput_gain_mbps"] > 100.0

    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True
