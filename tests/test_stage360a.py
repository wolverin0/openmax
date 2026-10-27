"""Stage 360A pytest suite."""

from __future__ import annotations

from pathlib import Path

from tools.re.dissect_stage360a_ubnt_poll_deferred_sta_state_machine import (
    build_stage360a_report,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage360a_ubnt_poll_deferred_sta_state_machine() -> None:
    report = build_stage360a_report()
    assert report["stage"] == "360A"
    assert report["status"] == "COMPLETED"
    assert report["writes_performed"] == 0

    re_prov = report["binary_re_provenance"]
    assert re_prov["rodata_strings"]["$LC11_added_to_deferred_list"]["offset_hex"] == "0x14e4"
    assert re_prov["rodata_strings"]["$LC12_not_added_to_deferred_list"]["offset_hex"] == "0x1534"
    assert re_prov["dissected_functions"]["ubnt_poll_host_on_sta_connect"]["text_offset_hex"] == "0x008134"
    assert re_prov["dissected_functions"]["ubnt_poll_host_create_sta_def"]["text_offset_hex"] == "0x00cc7c"
    assert re_prov["dissected_functions"]["ubnt_poll_host_create_sta_def"]["struct_size_bytes"] == 24
    assert re_prov["dissected_functions"]["ubnt_poll_host_deferred_timer_cb"]["text_offset_hex"] == "0x0062fc"

    p82 = report["panel2_82_tdma_and_wal_requeue_interaction"]
    assert p82["ff_frame_dur_us"] == 10000
    assert p82["cbp_dur_us"] == 180
    assert len(p82["deferred_cpes_on_panel2"]) == 4

    gate = audit_stage_receipt_5pillars(report)
    assert gate["compliant"], f"Stage 360A 5-pillar gate failed: {gate}"

    doc = REPO_ROOT / "docs" / "STAGE360A_UBNT_POLL_DEFERRED_STA_STATE_MACHINE.md"
    assert doc.exists()
    txt = doc.read_text(encoding="utf-8")
    assert len(txt.splitlines()) < 220
    assert txt.count("<!-- doc-head:") == 1
