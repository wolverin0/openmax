from __future__ import annotations

import json
from pathlib import Path

from tools.firmware.build_stage650a_pb060_xtensa_txop_and_tid_sched_sgmt_patch import (
    OUT_JSON,
    build_stage650a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/STAGE650A_PB060_XTENSA_TXOP_AND_TID_SCHED_SGMT_PATCH.md"


def test_stage650a_pb060_xtensa_txop_and_tid_sched_sgmt_patch() -> None:
    rep = build_stage650a_report()
    assert OUT_JSON.exists()
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "650A"
    assert loaded["status"] == "CONFIRMED"
    assert loaded["live_devices_touched"] is False
    assert loaded["patched_images_count"] == 7

    for img in loaded["patched_images"]:
        assert img["composable_with_pb040_and_pb050"] is True
        assert img["orig_sha256"] != img["patched_sha256"]
        assert (ROOT / img["output_sgmt_path"]).exists()

    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True

    assert DOC_PATH.exists()
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 200
    assert doc_lines[0].startswith("<!-- doc-head:")
