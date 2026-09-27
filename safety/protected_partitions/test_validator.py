"""
Unit tests for Flash Partition Validator.
Verifies rejection of protected partitions, size overflows, and invalid headers.
"""

import unittest
from safety.protected_partitions.validator import (
    FlashPartitionValidator, FlashSafetyException, MAX_FIRMWARE_IMAGE_SIZE
)


class TestFlashPartitionValidator(unittest.TestCase):

    def setUp(self):
        self.validator = FlashPartitionValidator()

    def test_reject_writing_to_uboot(self):
        """Writing to mtd0 (u-boot) must immediately raise FlashSafetyException."""
        with self.assertRaises(FlashSafetyException) as ctx:
            self.validator.validate_write_operation(target_mtd_index=0, offset_in_partition=0, size=1024)
        self.assertIn("HARD-PROTECTED", str(ctx.exception))

    def test_reject_writing_to_uboot_env(self):
        """Writing to mtd1 (u-boot-env) must immediately raise FlashSafetyException."""
        with self.assertRaises(FlashSafetyException) as ctx:
            self.validator.validate_write_operation(target_mtd_index=1, offset_in_partition=0, size=512)
        self.assertIn("HARD-PROTECTED", str(ctx.exception))

    def test_reject_writing_to_eeprom_art(self):
        """Writing to mtd5 (EEPROM/ART) must immediately raise FlashSafetyException."""
        with self.assertRaises(FlashSafetyException) as ctx:
            self.validator.validate_write_operation(target_mtd_index=5, offset_in_partition=0, size=1024)
        self.assertIn("HARD-PROTECTED", str(ctx.exception))

    def test_allow_valid_write_to_kernel(self):
        """Writing 512 KB to mtd2 (kernel, 1024 KB) must pass."""
        valid = self.validator.validate_write_operation(target_mtd_index=2, offset_in_partition=0, size=512 * 1024)
        self.assertTrue(valid)

    def test_reject_overflow_write_to_kernel(self):
        """Writing 2 MB to mtd2 (kernel, 1024 KB capacity) must raise overflow exception."""
        with self.assertRaises(FlashSafetyException) as ctx:
            self.validator.validate_write_operation(target_mtd_index=2, offset_in_partition=0, size=2 * 1024 * 1024)
        self.assertIn("overflow", str(ctx.exception).lower())

    def test_reject_oversized_firmware_image(self):
        """An image larger than 15.008 MB must be rejected to prevent ART corruption."""
        dummy_oversized = b"\x27\x05\x19\x56" + b"\x00" * (MAX_FIRMWARE_IMAGE_SIZE + 1024)
        valid, msg = self.validator.validate_firmware_image(dummy_oversized, "bad_large.bin")
        self.assertFalse(valid)
        self.assertIn("SAFETY VIOLATION", msg)

    def test_reject_invalid_magic_header(self):
        """An image with invalid magic header must be rejected."""
        dummy_corrupt = b"\xde\xad\xbe\xef" + b"\x00" * (5 * 1024 * 1024)
        valid, msg = self.validator.validate_firmware_image(dummy_corrupt, "corrupt.bin")
        self.assertFalse(valid)
        self.assertIn("Header Check Failed", msg)

    def test_accept_valid_openwrt_image(self):
        """A valid 7 MB OpenWrt image with uImage magic must pass with reported headroom."""
        valid_bytes = b"\x27\x05\x19\x56" + b"\x00" * (7 * 1024 * 1024)
        valid, msg = self.validator.validate_firmware_image(valid_bytes, "openwrt-sysupgrade.bin")
        self.assertTrue(valid)
        self.assertIn("VALID", msg)
        self.assertIn("headroom", msg)


if __name__ == "__main__":
    unittest.main()
