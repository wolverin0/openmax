from __future__ import annotations

import json
from pathlib import Path

from tools.re.dissect_stage476a_xtensa_ht_comm_opcodes_full_table_re import (
    OUT_JSON,
    build_stage476a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/STAGE476A_XTENSA_HT_COMM_OPCODES_FULL_TABLE_RE.md"


def test_stage476a_ht_comm_opcodes_full_table_re() -> None:
    rep = build_stage476a_report()
    assert OUT_JSON.exists()
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "476A"
    assert loaded["status"] == "CONFIRMED"
    assert loaded["live_devices_touched"] is False
    assert loaded["wa_xc_opcode_parity"] is True
    assert loaded["xc_va_shift_bytes"] == 4

    table = loaded["ht_comm_opcode_table"]
    assert len(table) == 51
    assert loaded["functions_dissected"]["ht_comm_rx_dispatch"]["active_opcode_count"] == 21
    assert loaded["functions_dissected"]["ht_comm_unpack_msg"]["active_opcode_count"] == 24
    assert loaded["functions_dissected"]["ht_comm_tx_send"]["wmi_event_id"] == "0x901f"

    assert table[14]["name"] == "HT_COMM_OP_SET_SW_RETRY_AND_MODE"
    assert table[14]["is_rx_active"] is True
    assert table[12]["name"] == "HT_COMM_OP_STA_QUOTA_WEIGHTS"
    assert table[50]["is_rx_active"] is True

    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True

    assert DOC_PATH.exists()
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert doc_lines[0].startswith("<!-- doc-head:")
