#!/usr/bin/env python3
"""
Tests for Stage 157A — OpenWrt-to-Stock airOS 8 1-Command MTD `firmware` Image Builder
(`stock_airos8_wa_8711_for_mtd_firmware.bin`) & Direct OpenWrt `.241` -> `.242` L2 Verification.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct

from tools.firmware.build_stage157a_stock_airos8_mtd_firmware import (
    EXPECTED_MAC80211_V3_SHA256,
    EXPECTED_MTD2_SHA256,
    KERNEL_SLOT_SIZE,
    OPENWRT_FIRMWARE_PART_MAX,
    OUT_MTD_FIRMWARE_BIN,
    STAGE157A_RECEIPT_JSON,
    build_and_verify_stock_airos8_mtd_firmware,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_stage157a_receipt_passes_5pillars_and_safety() -> None:
    receipt = build_and_verify_stock_airos8_mtd_firmware(write_output=True)
    assert STAGE157A_RECEIPT_JSON.exists(), f"Missing {STAGE157A_RECEIPT_JSON}"
    persisted = json.loads(STAGE157A_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert persisted["stage"] == "157A"
    assert persisted["status"] == "CONFIRMED"
    assert persisted["live_radios_241_242_touched"] is False

    audit = audit_stage_receipt_5pillars(persisted)
    assert audit["compliant"] is True, f"5-Pillar gate failed: {audit}"
    assert persisted["pillar_e_memory_master_claim_id"] == "mm-8fae"
    assert receipt["output_image"]["fits_openwrt_mtd_firmware"] is True


def test_stage157a_stock_mtd_firmware_binary_structure_and_parity() -> None:
    assert OUT_MTD_FIRMWARE_BIN.exists(), f"Missing {OUT_MTD_FIRMWARE_BIN}"
    raw = OUT_MTD_FIRMWARE_BIN.read_bytes()
    receipt = json.loads(STAGE157A_RECEIPT_JSON.read_text(encoding="utf-8"))
    img_meta = receipt["output_image"]

    assert len(raw) == img_meta["size_bytes"]
    assert len(raw) == 10092544  # 0x100000 (1,048,576 B kernel) + 0x8a0000 (9,043,968 B rootfs)
    assert len(raw) <= OPENWRT_FIRMWARE_PART_MAX
    assert (len(raw) % 0x10000) == 0
    assert _sha256(raw) == img_meta["sha256"]

    # 1. Verify 0x000000..0x100000 is the exact stock mtd2 kernel partition
    kernel_slot = raw[:KERNEL_SLOT_SIZE]
    assert kernel_slot[:4] == b"\x27\x05\x19\x56"  # uImage magic
    assert _sha256(kernel_slot) == EXPECTED_MTD2_SHA256
    assert img_meta["matches_backup_mtd2_byte_for_byte"] is True

    # 2. Verify 0x100000..end is the exact stock mtd3 SquashFS rootfs + 0xdeadc0de marker
    rootfs_slot = raw[KERNEL_SLOT_SIZE:]
    assert rootfs_slot[:4] == b"hsqs"
    bytes_used = struct.unpack_from("<Q", rootfs_slot, 40)[0]
    assert bytes_used == 8803133
    assert rootfs_slot[0x866000:0x866004] == b"\xde\xad\xc0\xde"
    assert img_meta["matches_backup_mtd3_squashfs_byte_for_byte"] is True


def test_stage157a_direct_openwrt_241_to_242_l2_verification_documented() -> None:
    receipt = json.loads(STAGE157A_RECEIPT_JSON.read_text(encoding="utf-8"))
    l2 = receipt["direct_openwrt_241_to_242_l2_verification"]
    assert l2["mac80211_v3_ko_sha256"] == EXPECTED_MAC80211_V3_SHA256
    assert len(l2["why_openwrt_241_passes_l2_directly_to_242"]) == 3
