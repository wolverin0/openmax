from __future__ import annotations

import json
from pathlib import Path

from tools.re.dissect_stage649a_xtensa_wal_vdev_params_and_struct_re import (
    OUT_JSON,
    build_stage649a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/STAGE649A_XTENSA_WAL_VDEV_PARAMS_AND_STRUCT_RE.md"


def test_stage649a_xtensa_wal_vdev_params_and_struct_re() -> None:
    rep = build_stage649a_report()
    assert OUT_JSON.exists()
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "649A"
    assert loaded["status"] == "CONFIRMED"
    assert loaded["live_devices_touched"] is False

    assert loaded["wmi_vdev_set_param_cmdid"]["cmd_id_hex"] == "0x900a"
    assert loaded["wmi_vdev_set_param_cmdid"]["wa_jump_table_total_slots"] == 54
    assert len(loaded["wal_vdev_param_table_23slots"]) == 23
    assert len(loaded["owrt_wal_33slot_jump_table"]) == 33

    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True

    assert DOC_PATH.exists()
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 200
    assert doc_lines[0].startswith("<!-- doc-head:")
