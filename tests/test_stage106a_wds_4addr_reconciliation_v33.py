from __future__ import annotations

import json
import pathlib

from tools.verify.verify_stage106a_wds_4addr_reconciliation_v33 import (
    RECEIPT_PATH,
    verify_stage106a,
)


def test_stage106a_wds_4addr_reconciliation_v33() -> None:
    receipt = verify_stage106a()
    assert RECEIPT_PATH.exists()
    saved = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert saved["stage_id"] == "Stage 106A"
    assert saved["curation_version"] == "v33.0"
    assert saved["live_hardware_contact_241_242"] is False
    assert saved["hardware_ips_touched"] == []
    assert saved["five_pillars_compliance"]["compliant"] is True

    d36 = receipt["discoveries_reconciled"]["FMX-DISC-36"]
    assert d36["module_layout_size_bytes"] == 352
    assert d36["skb_data_offset_hex"] == "0xa8"
    assert d36["changed_bytes_count"] == 71
    assert d36["deterministic_patch_reproduced"] is True

    d37 = receipt["discoveries_reconciled"]["FMX-DISC-37"]
    assert d37["beacon_int_tu"] == 30
    assert d37["ie_free_window_sec"] == 65
    assert d37["ie_free_window_sec"] > d37["stock_airos8_full_scan_pass_sec"]
    assert all(d37["checks"].values())

    d38 = receipt["discoveries_reconciled"]["FMX-DISC-38"]
    assert d38["frame_control_hex"] == "0x8803"
    assert d38["tx_delta_after_assoc_resp_ms"] == 1.05
    assert d38["callsite_words_hex"] == [
        "0x0c000000",
        "0x24a5076c",
        "0x1000f819",
        "0x3c140002",
    ]

    for doc_info in receipt["master_docs_verification"].values():
        assert doc_info["under_215_lines"] is True
        assert doc_info["doc_head_count"] == 1
        assert doc_info["starts_with_doc_head"] is True
        assert doc_info["has_fmx_disc_36"] is True
        assert doc_info["has_fmx_disc_37"] is True
        assert doc_info["has_fmx_disc_38"] is True
