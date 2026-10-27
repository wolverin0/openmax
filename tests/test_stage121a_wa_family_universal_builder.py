from __future__ import annotations

import json

from tools.firmware.build_wa_family_universal_kit import (
    RECEIPT_PATH,
    build_and_verify_wa_family_universal_kit,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


def test_stage121a_wa_family_universal_builder() -> None:
    receipt = build_and_verify_wa_family_universal_kit(write_images=False)
    assert RECEIPT_PATH.exists()
    saved = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))

    assert saved["stage_id"] == "Stage 121A"
    assert saved["live_hardware_contact_241_242"] is False
    assert saved["hardware_ips_touched"] == []
    assert saved["wa_boards_built_count"] == 4
    assert saved["total_images_verified_count"] == 16

    gate = audit_stage_receipt_5pillars(saved)
    assert gate["compliant"] is True
    assert gate["missing_pillars"] == []

    boards = receipt["boards"]
    for slug in (
        "powerbeam-5ac-gen2",
        "litebeam-5ac-gen2",
        "lap-120",
        "nanostation-ac-loco",
    ):
        assert slug in boards
        b = boards[slug]
        for role in ("factory_ap", "factory_sta"):
            assert b[role]["open_magic"] == "OPEN"
            assert b[role]["open_header_crc_valid"] is True
            assert b[role]["part_kernel_crc_valid"] is True
            assert b[role]["part_rootfs_crc_valid"] is True
        for role in ("sysupgrade_ap", "sysupgrade_sta"):
            assert b[role]["fwtool_metadata_crc_valid"] is True
            assert b[role]["fwtool_signature_crc_valid"] is True

    assert boards["powerbeam-5ac-gen2"]["ubnt_sysid_hex"] == "0xe3d6"
    assert boards["litebeam-5ac-gen2"]["ubnt_sysid_hex"] == "0xe7f9"
    assert (
        "ubnt,litebeam-5ac-gen2"
        in boards["litebeam-5ac-gen2"]["supported_devices_aliases"]
    )
    assert boards["lap-120"]["ubnt_sysid_hex"] == "0xe7f5"
    assert boards["nanostation-ac-loco"]["ubnt_sysid_hex"] == "0xe7f7"

    teb = receipt["kernel_and_admitter_verification"]["mac80211_teb_patch"]
    assert teb["matches_expected_teb_sha256"] is True
    assert teb["module_layout_size_bytes"] == 352
    assert teb["skb_data_offset_hex"] == "0xa8"
