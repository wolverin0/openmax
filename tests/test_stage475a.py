from __future__ import annotations

import json
from pathlib import Path

from tools.re.dissect_stage475a_xtensa_wal_peer_32params_and_retry_sched_re import (
    OUT_JSON,
    build_stage475a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/STAGE475A_XTENSA_WAL_PEER_32PARAMS_AND_RETRY_SCHED_RE.md"


def test_stage475a_wal_peer_32params_and_retry_sched_re() -> None:
    rep = build_stage475a_report()
    assert OUT_JSON.exists()
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "475A"
    assert loaded["status"] == "CONFIRMED"
    assert loaded["live_devices_touched"] is False
    assert loaded["wa_xc_byte_identical"] is True

    table = loaded["wal_peer_param_table"]
    assert len(table) == 33
    assert loaded["functions_dissected"]["wal_peer_set_param"]["active_slot_count"] == 22
    assert loaded["functions_dissected"]["wal_peer_get_param"]["active_slot_count"] == 21

    # Verify RC context pointer slots 15, 16, 17 map to 0x44, 0x48, 0x40
    assert table[15]["peer_struct_offset"] == "0x44 (68)"
    assert table[16]["peer_struct_offset"] == "0x48 (72)"
    assert table[17]["peer_struct_offset"] == "0x40 (64)"
    assert table[28]["name"] == "WAL_PEER_PARAM_NON_AGG_RTS_ENABLE"

    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True

    assert DOC_PATH.exists()
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert doc_lines[0].startswith("<!-- doc-head:")
