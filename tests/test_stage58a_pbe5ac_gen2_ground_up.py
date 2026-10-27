from __future__ import annotations

import hashlib
import json
from pathlib import Path

from firmware.openwrt.futuramax_openwrt_imagebuilder_packager import TARGET_DEVICE_SPECS
from inventory.calibration_hash.art_hasher import ARTHasher
from inventory.flash_map_validator.flash_validator import FlashMapValidator
from tools.inventory.probe_and_backup_pbe5ac_gen2_ground_up import (
    dissect_eeprom_art_bytes,
    parse_ubnt_factory_fw_header,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage58a_receipt_and_protected_partition_backups_exist() -> None:
    receipt_path = (
        REPO_ROOT
        / "artifacts"
        / "autoresearch"
        / "stage58a_pbe5ac_gen2_ground_up_and_caldata_backup_20261026.json"
    )
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "58A"
    assert data["safety_policy"]["flash_writes_performed"] == 0

    for unit_key, expected_mac, expected_mtd5_sha in [
        ("pbe5ac_241", "AC8BA9C28A01", "d780aed0db673b3b72f71325b52c6c777aed9a607a9c9db89348ea0d2108846d"),
        ("pbe5ac_242", "AC8BA9C28773", "f88bc3d756e078c4f04b3ee7e1700ea091a7288e8edcc217b4cd7dbda9de3754"),
    ]:
        u = data["units"][unit_key]
        assert u["board_info"]["board.sysid"] == "0xe3d6"
        assert u["board_info"]["board.model"] == "PBE-5AC-Gen2"
        assert u["board_info"]["board.hwaddr"] == expected_mac
        assert u["flash_map_validation"]["is_valid"] is True

        for mtd_name, expected_size in [("mtd0", 262144), ("mtd1", 65536), ("mtd4", 262144), ("mtd5", 65536)]:
            binfo = u["protected_partition_backups"][mtd_name]
            bpath = REPO_ROOT / binfo["backup_file"]
            assert bpath.exists(), f"Missing backup file {bpath}"
            raw = bpath.read_bytes()
            assert len(raw) == expected_size
            assert hashlib.sha256(raw).hexdigest() == binfo["sha256"]

        mtd5_bytes = (REPO_ROOT / u["protected_partition_backups"]["mtd5"]["backup_file"]).read_bytes()
        ok, msg = ARTHasher.verify_golden_match(mtd5_bytes, expected_mtd5_sha)
        assert ok, msg
        dissected = dissect_eeprom_art_bytes(mtd5_bytes)
        assert dissected["ar9342_2g_wmac_caldata_0x1000"]["valid"] is True
        assert dissected["qca9882_5g_pcie_caldata_0x5000"]["valid"] is True
        assert "0x000c (e3d6)" in dissected["sysid_0xe3d6_occurrences"]

    # Verify .251 is confirmed as Rocket 2AC Prism (0xe2f2)
    r2ac = data["units"]["r2ac_prism_251"]
    assert r2ac["board_info"]["board.sysid"] == "0xe2f2"
    assert r2ac["board_info"]["board.model"] == "R2AC-PRISM"
    assert r2ac["firmware_version"] == "2XC.v8.7.11"


def test_stage58a_openwrt_24_10_4_images_and_packager_spec() -> None:
    assert "ubnt_powerbeam-5ac-gen2" in TARGET_DEVICE_SPECS
    spec = TARGET_DEVICE_SPECS["ubnt_powerbeam-5ac-gen2"]
    assert spec.ubnt_sysid == "0xe3d6"
    assert spec.pci_subsystem_id == "0777:e3d6"

    factory_bin = (
        REPO_ROOT / "firmware" / "openwrt" / "openwrt-24.10.4-ath79-generic-ubnt_powerbeam-5ac-gen2-squashfs-factory.bin"
    )
    sysupgrade_bin = (
        REPO_ROOT
        / "firmware"
        / "openwrt"
        / "openwrt-24.10.4-ath79-generic-ubnt_powerbeam-5ac-gen2-squashfs-sysupgrade.bin"
    )
    initramfs_bin = (
        REPO_ROOT
        / "firmware"
        / "openwrt"
        / "openwrt-24.10.4-ath79-generic-ubnt_powerbeam-5ac-gen2-initramfs-kernel.bin"
    )
    assert factory_bin.exists()
    assert sysupgrade_bin.exists()
    assert initramfs_bin.exists()

    hdr = parse_ubnt_factory_fw_header(factory_bin.read_bytes())
    assert hdr["header_magic"] == "OPEN"
    assert hdr["contains_sysid_0xe3d6"] is True
    assert [p["name"] for p in hdr["parts_detected"]] == ["kernel", "rootfs"]

    val = FlashMapValidator.validate_layout(
        'dev:    size   erasesize  name\n'
        'mtd0: 00040000 00010000 "u-boot"\n'
        'mtd1: 00010000 00010000 "u-boot-env"\n'
        'mtd2: 00100000 00010000 "kernel"\n'
        'mtd3: 00e60000 00010000 "rootfs"\n'
        'mtd4: 00040000 00010000 "cfg"\n'
        'mtd5: 00010000 00010000 "EEPROM"\n'
    )
    safe, errs = val.can_safely_flash_image(factory_bin.stat().st_size, target_partition="firmware")
    assert safe is True
    assert errs == []
