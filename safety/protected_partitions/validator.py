"""
Flash Partition Safety Boundary and Image Offset Validator for Ubiquiti airMAX AC.
Enforces AGENTS.md Section 4: Protected Partitions and Non-Goals.

Protects by Default:
- mtd0: u-boot (0x00000000 - 0x00040000, 256 KB)
- mtd1: u-boot-env (0x00040000 - 0x00050000, 64 KB)
- mtd4: cfg / board-data (0x00fb0000 - 0x00ff0000, 256 KB)
- mtd5: EEPROM / ART calibration (0x00ff0000 - 0x01000000, 64 KB)

Writable Flash Window (mtd2 + mtd3 = firmware):
- Start: 0x00050000 (320 KB offset)
- End:   0x00fb0000 (16,056 KB offset)
- Max firmware image size: 15,736,832 bytes (15.008 MB)
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional


FLASH_TOTAL_SIZE = 16 * 1024 * 1024  # 16 MB SPI Flash (16,777,216 bytes)

@dataclass(frozen=True)
class Partition:
    name: str
    mtd_index: int
    offset: int
    size: int
    is_protected: bool

    @property
    def end(self) -> int:
        return self.offset + self.size


# Canonical LAP-120 and LiteBeam 5AC Gen2 Flash Partition Layout
FLASH_LAYOUT_AR9342_16MB: List[Partition] = [
    Partition("u-boot", 0, 0x00000000, 0x00040000, is_protected=True),      # 256 KB
    Partition("u-boot-env", 1, 0x00040000, 0x00010000, is_protected=True),  # 64 KB
    Partition("kernel", 2, 0x00050000, 0x00100000, is_protected=False),     # 1024 KB
    Partition("rootfs", 3, 0x00150000, 0x00e60000, is_protected=False),     # 14.375 MB
    Partition("cfg", 4, 0x00fb0000, 0x00040000, is_protected=True),         # 256 KB
    Partition("EEPROM", 5, 0x00ff0000, 0x00010000, is_protected=True),      # 64 KB ART
]

FIRMWARE_OFFSET_START = 0x00050000
FIRMWARE_OFFSET_END = 0x00fb0000
MAX_FIRMWARE_IMAGE_SIZE = FIRMWARE_OFFSET_END - FIRMWARE_OFFSET_START  # 15,736,832 bytes


class FlashSafetyException(Exception):
    """Raised when an operation attempts to violate flash partition boundaries."""
    pass


class FlashPartitionValidator:
    """Enforces flash boundary safety rules prior to any write primitive."""

    def __init__(self, layout: List[Partition] = None):
        self.layout = layout or FLASH_LAYOUT_AR9342_16MB

    def validate_write_operation(self, target_mtd_index: int, offset_in_partition: int, size: int) -> bool:
        """
        Validates if writing 'size' bytes to partition 'target_mtd_index' is legally allowed.
        Raises FlashSafetyException if target is protected or operation overflows partition.
        """
        partition = next((p for p in self.layout if p.mtd_index == target_mtd_index), None)
        if not partition:
            raise FlashSafetyException(f"Invalid MTD partition index: {target_mtd_index}")

        if partition.is_protected:
            raise FlashSafetyException(
                f"SAFETY VIOLATION: Partition {partition.name} (mtd{partition.mtd_index}) is HARD-PROTECTED. "
                "Writing to bootloader, env, or calibration ART is forbidden by AGENTS.md Section 4."
            )

        if offset_in_partition < 0:
            raise FlashSafetyException(f"Invalid negative offset: {offset_in_partition}")

        if offset_in_partition + size > partition.size:
            # Special case: in OpenWrt ath79, mtd2 (kernel) and mtd3 (rootfs) are contiguous
            # under the unified "firmware" partition.
            raise FlashSafetyException(
                f"Partition boundary overflow: write of {size} bytes at offset {offset_in_partition} "
                f"exceeds partition {partition.name} capacity ({partition.size} bytes)."
            )

        return True

    def validate_firmware_image(self, image_bytes: bytes, image_name: str = "firmware.bin") -> Tuple[bool, str]:
        """
        Validates a full sysupgrade or factory image against size, magic header, and memory layout.
        Returns: (is_valid, validation_summary_or_error)
        """
        size = len(image_bytes)
        if size == 0:
            return False, "Error: Image file is empty (0 bytes)."

        if size > MAX_FIRMWARE_IMAGE_SIZE:
            return False, (
                f"SAFETY VIOLATION: Image size ({size} bytes) exceeds maximum allowable "
                f"firmware flash window ({MAX_FIRMWARE_IMAGE_SIZE} bytes). Flashing this image "
                "would overwrite protected partition mtd4 (cfg) and mtd5 (ART calibration)!"
            )

        # Check for minimum sensible Linux kernel + rootfs size (> 2 MB)
        if size < 2 * 1024 * 1024:
            return False, f"Error: Image size ({size} bytes) is suspiciously small for OpenWrt firmware (< 2 MB)."

        # Check uImage or OpenWrt header magic
        # U-Boot uImage header magic: 0x27051956
        has_uimage_magic = (image_bytes[:4] == b"\x27\x05\x19\x56")
        has_open_magic = (b"OPEN" in image_bytes[:16])

        if not (has_uimage_magic or has_open_magic):
            return False, (
                "Header Check Failed: Image does not begin with standard uImage magic (0x27051956) "
                "or Ubiquiti/OpenWrt OPEN header. Flashing aborted."
            )

        remaining_headroom_kb = (MAX_FIRMWARE_IMAGE_SIZE - size) // 1024
        return True, (
            f"VALID: Image '{image_name}' ({size / (1024*1024):.2f} MB) fits safely inside "
            f"firmware window with {remaining_headroom_kb} KB headroom. "
            "Protected partitions (u-boot, env, ART) are 100% safe."
        )
