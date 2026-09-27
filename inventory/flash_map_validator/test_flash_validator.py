"""Unit tests for inventory.flash_map_validator.flash_validator (FlashMapValidator)."""

import unittest
from inventory.flash_map_validator.flash_validator import (
    FlashMapValidator,
    TOTAL_FLASH_SIZE_16MB,
    SAFE_UPGRADE_MAX_OFFSET,
    SAFE_UPGRADE_MIN_OFFSET,
)


VALID_AIROS_MTD = """
dev:    size   erasesize  name
mtd0: 00040000 00010000 "u-boot"
mtd1: 00010000 00010000 "u-boot-env"
mtd2: 00100000 00010000 "kernel"
mtd3: 00e00000 00010000 "rootfs"
mtd4: 00040000 00010000 "cfg"
mtd5: 00010000 00010000 "EEPROM"
"""

VALID_OPENWRT_MTD = """
dev:    size   erasesize  name
mtd0: 00040000 00010000 "u-boot"
mtd1: 00010000 00010000 "u-boot-env"
mtd2: 00f00000 00010000 "firmware"
mtd3: 00040000 00010000 "cfg"
mtd4: 00010000 00010000 "ART"
"""

CORRUPT_NO_ART_MTD = """
dev:    size   erasesize  name
mtd0: 00040000 00010000 "u-boot"
mtd1: 00010000 00010000 "u-boot-env"
mtd2: 00f00000 00010000 "firmware"
"""

CORRUPT_BAD_UBOOT_MTD = """
dev:    size   erasesize  name
mtd0: 00080000 00010000 "u-boot"
mtd1: 00010000 00010000 "EEPROM"
"""


class TestFlashMapValidator(unittest.TestCase):
    def test_validate_airos_layout(self):
        res = FlashMapValidator.validate_layout(VALID_AIROS_MTD, TOTAL_FLASH_SIZE_16MB)
        self.assertTrue(res.is_valid)
        self.assertEqual(len(res.violations), 0)
        self.assertIsNotNone(res.uboot_partition)
        self.assertEqual(res.uboot_partition.size, 0x40000)
        self.assertIsNotNone(res.art_partition)
        self.assertEqual(res.art_partition.offset, 0x00ff0000)
        self.assertEqual(res.art_partition.size, 0x10000)

    def test_validate_openwrt_layout(self):
        res = FlashMapValidator.validate_layout(VALID_OPENWRT_MTD, TOTAL_FLASH_SIZE_16MB)
        self.assertTrue(res.is_valid)
        self.assertEqual(len(res.violations), 0)
        self.assertIsNotNone(res.art_partition)
        self.assertEqual(res.art_partition.name, "ART")
        self.assertEqual(res.art_partition.offset, 0x00ff0000)

    def test_missing_art_fails_validation(self):
        res = FlashMapValidator.validate_layout(CORRUPT_NO_ART_MTD, TOTAL_FLASH_SIZE_16MB)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Missing 'EEPROM' or 'ART'" in v for v in res.violations))

    def test_bad_uboot_size_fails(self):
        res = FlashMapValidator.validate_layout(CORRUPT_BAD_UBOOT_MTD, TOTAL_FLASH_SIZE_16MB)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("u-boot partition has non-standard layout" in v for v in res.violations))

    def test_can_safely_flash_valid_image(self):
        res = FlashMapValidator.validate_layout(VALID_AIROS_MTD, TOTAL_FLASH_SIZE_16MB)
        safe_size = 8 * 1024 * 1024  # 8 MB
        can_flash, errors = res.can_safely_flash_image(safe_size, target_partition="firmware")
        self.assertTrue(can_flash)
        self.assertEqual(len(errors), 0)

    def test_reject_flash_to_protected_partition(self):
        res = FlashMapValidator.validate_layout(VALID_AIROS_MTD, TOTAL_FLASH_SIZE_16MB)
        for target in ("mtd0", "mtd1", "u-boot", "EEPROM", "ART", "cfg"):
            can_flash, errors = res.can_safely_flash_image(1024, target_partition=target)
            self.assertFalse(can_flash)
            self.assertTrue(any("CRITICAL SAFETY VIOLATION" in e for e in errors))

    def test_reject_oversized_firmware_image(self):
        res = FlashMapValidator.validate_layout(VALID_AIROS_MTD, TOTAL_FLASH_SIZE_16MB)
        oversized = (SAFE_UPGRADE_MAX_OFFSET - SAFE_UPGRADE_MIN_OFFSET) + 1024
        can_flash, errors = res.can_safely_flash_image(oversized, target_partition="firmware")
        self.assertFalse(can_flash)
        self.assertTrue(any("exceeds maximum safe firmware window" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
