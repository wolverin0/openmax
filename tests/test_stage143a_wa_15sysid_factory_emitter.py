#!/usr/bin/env python3
"""
Tests for Stage 143A — On-Demand WA-Family 15-Sysid (28 Single-PHY Board Records)
Factory Image Emitter & Checksum Manifest Builder (`retag_wa_factory_sysid.py`).
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from tools.firmware.retag_wa_factory_sysid import (
    DUAL_PHY_FORBIDDEN_SYSIDS,
    STAGE143A_RECEIPT_JSON,
    WA_15_SINGLE_PHY_SYSID_CATALOG,
    emit_wa_factory_for_sysid,
    generate_stage143a_manifest_and_receipt,
    verify_wa_factory_and_fwx0_image,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

EXPECTED_15_SINGLE_PHY_SYSIDS = {
    "0xe3d6",
    "0xe3d9",
    "0xe6f5",
    "0xe7f5",
    "0xe7f7",
    "0xe9f5",
    "0xe2c5",
    "0xe2c7",
    "0xe7f9",
    "0xe7fe",
    "0xe7ff",
    "0xe8f5",
    "0xe8e5",
    "0xe7fa",
    "0xe7fd",
}


def test_stage143a_receipt_passes_5pillars() -> None:
    receipt = generate_stage143a_manifest_and_receipt()
    assert STAGE143A_RECEIPT_JSON.exists(), f"Missing {STAGE143A_RECEIPT_JSON}"
    persisted = json.loads(STAGE143A_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert persisted["stage"] == "143A"
    assert persisted["status"] == "CONFIRMED"
    assert persisted["live_radios_241_242_touched"] is False

    audit = audit_stage_receipt_5pillars(persisted)
    assert audit["compliant"] is True, f"5-Pillar gate failed: {audit}"
    assert persisted["pillar_e_memory_master_claim_id"] == "mm-966e"
    assert receipt["summary"]["unique_single_phy_sysids"] == 15
    assert receipt["summary"]["single_phy_board_records"] == 28
    assert receipt["summary"]["total_emitted_variants_verified"] == 30


def test_stage143a_15_single_phy_sysids_and_28_records_mapping() -> None:
    assert set(WA_15_SINGLE_PHY_SYSID_CATALOG.keys()) == EXPECTED_15_SINGLE_PHY_SYSIDS
    all_records = []
    for sysid_hex, entry in WA_15_SINGLE_PHY_SYSID_CATALOG.items():
        assert entry["board_phycount"] == 1
        all_records.extend(entry["record_indices"])
        if sysid_hex in {
            "0xe3d6",
            "0xe3d9",
            "0xe6f5",
            "0xe7f5",
            "0xe7f7",
            "0xe9f5",
            "0xe2c5",
            "0xe2c7",
        }:
            assert entry["base_image_family"] == "powerbeam-5ac-gen2"
            assert entry["led_group"] == "74HC164_4LED_SSR"
        else:
            assert entry["base_image_family"] == "litebeam-5ac-gen2"
            assert entry["led_group"] == "DIRECT_SOC_GPIO_LEDS"

    assert len(all_records) == 28
    assert len(set(all_records)) == 28
    # Records 21 (0xe7fb NS-5AC), 23 & 24 (0xe7fc NBE-5AC-Gen2) are excluded dual-PHY
    assert set(all_records) == set(range(31)) - {21, 23, 24}


def test_stage143a_on_demand_emission_and_fwx0_open_crc_verification(tmp_path: Path) -> None:
    for sysid_hex in ("0xe3d6", "0xe3d9", "0xe7f9", "0xe8e5", "0xe7fa", "0xe7fd"):
        for role in ("ap", "sta"):
            out_bin = tmp_path / f"factory-{sysid_hex}-{role}.bin"
            img_bytes, meta = emit_wa_factory_for_sysid(
                sysid_hex, role=role, output_path=out_bin
            )
            assert out_bin.exists()
            assert len(img_bytes) == meta["emitted_size_bytes"]
            assert meta["all_crcs_valid"] is True

            ver = verify_wa_factory_and_fwx0_image(img_bytes)
            assert ver["open_magic_valid"] is True
            assert ver["ubnt_wa_ar934x_prefix_preserved"] is True
            assert ver["tagged_sysid_hex"] == sysid_hex
            assert ver["open_header_crc_valid"] is True
            assert ver["part_kernel_crc_valid"] is True
            assert ver["part_rootfs_crc_valid"] is True
            assert ver["ends_magic_valid"] is True
            assert ver["fwx0_metadata_crc_valid"] is True
            assert ver["fwx0_signature_crc_valid"] is True
            assert ver["fwx0_metadata"]["ubnt_sysid"] == sysid_hex


def test_stage143a_dual_phy_sysids_blocked() -> None:
    assert set(DUAL_PHY_FORBIDDEN_SYSIDS.keys()) == {"0xe7fb", "0xe7fc"}
    for dual_sysid in ("0xe7fb", "0xe7fc"):
        with pytest.raises(ValueError, match="dual-PHY"):
            emit_wa_factory_for_sysid(dual_sysid, role="ap")
