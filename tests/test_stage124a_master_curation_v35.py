from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage124a_master_curation_v35 import (
    MASTER_DOCS,
    RECEIPT_OUT,
    STAGE_109_TO_121_RECEIPTS,
    verify_abi_divergence_fmx_disc_39,
    verify_stage124a,
)


def test_stage124a_abi_divergence_fmx_disc_39() -> None:
    abi = verify_abi_divergence_fmx_disc_39()
    assert abi["claim_status"] == "CONFIRMED"
    assert abi["prior_6_6_73_hypothesis"] == "REFUTED"
    assert abi["panel1_lap120_snapshot_6_6_110"]["size_bytes"] == 829464
    assert abi["panel1_lap120_snapshot_6_6_110"]["module_layout_size_bytes"] == 384
    assert abi["panel1_lap120_snapshot_6_6_110"]["skb_data_offset_hex"] == "0xa4"
    assert abi["openwrt_24_10_4_release_6_6_110"]["size_bytes"] == 815640
    assert abi["openwrt_24_10_4_release_6_6_110"]["module_layout_size_bytes"] == 352
    assert abi["openwrt_24_10_4_release_6_6_110"]["skb_data_offset_hex"] == "0xa8"
    assert abi["file_size_delta_bytes"] == 13824


def test_stage124a_master_curation_v35_and_5pillar_gate() -> None:
    receipt = verify_stage124a()
    assert RECEIPT_OUT.exists()
    saved = json.loads(RECEIPT_OUT.read_text(encoding="utf-8"))

    gate = audit_stage_receipt_5pillars(saved)
    assert gate["compliant"] is True
    assert gate["missing_pillars"] == []

    assert saved["curation_version"] == "v35.0"
    assert saved["hardware_safety"]["touched_241"] is False
    assert saved["hardware_safety"]["touched_242"] is False
    assert saved["hardware_safety"]["flash_writes"] == 0

    disc40 = saved["discoveries_reconciled"]["FMX-DISC-40"]
    assert disc40["wa_boards_built_count"] == 4
    assert disc40["total_images_verified_count"] == 16
    assert set(disc40["boards_summary"].keys()) == {
        "powerbeam-5ac-gen2",
        "litebeam-5ac-gen2",
        "lap-120",
        "nanostation-ac-loco",
    }

    assert set(saved["stages_synchronized"].keys()) == set(STAGE_109_TO_121_RECEIPTS.keys())

    for key, doc_info in saved["master_curation_v35_docs"].items():
        assert doc_info["under_215_lines"] is True, f"{key} line count >= 215"
        assert doc_info["doc_head_count"] == 1
        assert doc_info["starts_with_doc_head"] is True
        assert doc_info["has_fmx_disc_39"] is True
        assert doc_info["has_fmx_disc_40"] is True
        assert doc_info["has_abi_829464_0xa4"] is True
        assert doc_info["has_abi_815640_0xa8"] is True
        assert doc_info["has_wa_16_images"] is True

    for key, path in MASTER_DOCS.items():
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) < 215
