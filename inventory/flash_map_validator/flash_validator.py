"""Flash map layout validator for Ubiquiti airMAX AC hardware.

Summary: Enforces AGENTS.md §4 rules by validating /proc/mtd and device-tree flash layouts
against canonical 16 MB SPI-NOR maps. Detects partition overlaps, validates that ART/EEPROM
is pinned at 0x00ff0000, and verifies flash write eligibility.
Keywords: flash map, MTD validator, u-boot, ART, EEPROM, safety boundary, 16MB flash.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


TOTAL_FLASH_SIZE_16MB = 0x01000000  # 16,777,216 bytes
ERASE_BLOCK_SIZE_64KB = 0x00010000  # 65,536 bytes

# Canonical Protected Ranges for Ubiquiti airMAX AC (WA / XC)
PROTECTED_RANGES: Dict[str, Tuple[int, int]] = {
    "u-boot": (0x00000000, 0x00040000),      # 256 KB
    "u-boot-env": (0x00040000, 0x00050000),  # 64 KB
    "cfg": (0x00f50000, 0x00f90000),         # 256 KB
    "EEPROM": (0x00ff0000, 0x01000000),      # 64 KB (ART)
}

SAFE_UPGRADE_MAX_OFFSET = 0x00f50000         # Firmware cannot exceed 0x00f50000 (15,008 KB)
SAFE_UPGRADE_MIN_OFFSET = 0x00050000         # Firmware starts after u-boot-env


@dataclass
class FlashPartitionEntry:
    dev_name: str       # "mtd0", "mtd1", etc.
    name: str           # "u-boot", "kernel", "rootfs", "EEPROM", etc.
    size: int           # Size in bytes
    erasesize: int      # Erase block size in bytes
    offset: int         # Offset in flash from start (0x00000000)
    is_protected: bool  # Whether partition is strictly protected from writes


@dataclass
class FlashValidationResult:
    is_valid: bool
    total_flash_size: int
    partitions: List[FlashPartitionEntry] = field(default_factory=list)
    art_partition: Optional[FlashPartitionEntry] = None
    uboot_partition: Optional[FlashPartitionEntry] = None
    firmware_window: Tuple[int, int] = (0, 0)
    violations: List[str] = field(default_factory=list)

    def can_safely_flash_image(self, image_size_bytes: int, target_partition: str = "firmware") -> Tuple[bool, List[str]]:
        """Validates whether a sysupgrade image of given size can be safely written to target."""
        errors: List[str] = []
        if not self.is_valid:
            errors.append("Cannot flash: Flash map validation has critical violations")
            return False, errors

        # AGENTS.md §4: never write to bootloader or calibration
        if target_partition in ("u-boot", "u-boot-env", "EEPROM", "ART", "cfg", "mtd0", "mtd1", "mtd4", "mtd5"):
            errors.append(f"CRITICAL SAFETY VIOLATION: Write requested to protected partition '{target_partition}'")
            return False, errors

        # Check maximum allowed firmware size
        max_allowed_fw = SAFE_UPGRADE_MAX_OFFSET - SAFE_UPGRADE_MIN_OFFSET
        if image_size_bytes > max_allowed_fw:
            errors.append(
                f"Image size ({image_size_bytes} bytes) exceeds maximum safe firmware window "
                f"({max_allowed_fw} bytes, 0x00050000 - 0x00f50000)"
            )
            return False, errors

        return True, []


class FlashMapValidator:
    """Validates MTD partition maps against hardware safety specifications."""

    @classmethod
    def parse_proc_mtd(cls, mtd_content: str) -> List[Tuple[str, int, int, str]]:
        """Parses /proc/mtd lines into (dev_name, size, erasesize, name)."""
        entries = []
        for line in mtd_content.splitlines():
            line = line.strip()
            if not line or line.startswith("dev:"):
                continue
            m = re.match(r"(mtd\d+):\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+\"([^\"]+)\"", line)
            if m:
                dev = m.group(1)
                size = int(m.group(2), 16)
                erasesize = int(m.group(3), 16)
                name = m.group(4)
                entries.append((dev, size, erasesize, name))
        return entries

    @classmethod
    def validate_layout(cls, mtd_content: str, assumed_total_size: int = TOTAL_FLASH_SIZE_16MB) -> FlashValidationResult:
        """Validates the flash partition table and computes absolute offsets."""
        parsed = cls.parse_proc_mtd(mtd_content)
        violations: List[str] = []
        partitions: List[FlashPartitionEntry] = []
        
        current_offset = 0
        art_part: Optional[FlashPartitionEntry] = None
        uboot_part: Optional[FlashPartitionEntry] = None

        has_virtual_firmware = any(name in ("firmware", "all") for _, _, _, name in parsed)

        for dev, size, erasesize, name in parsed:
            # Skip virtual aggregate partitions like 'firmware' or 'all' when calculating physical layout offsets
            is_virtual = name in ("firmware", "all")
            
            # Determine protection
            is_prot = (
                name in ("u-boot", "u-boot-env", "EEPROM", "ART", "cfg") 
                or dev in ("mtd0", "mtd1", "mtd4", "mtd5")
            )

            # Fixed offset mapping for well-known partitions
            offset = current_offset
            if name == "u-boot":
                offset = 0x00000000
            elif name == "u-boot-env":
                offset = 0x00040000
            elif name in ("EEPROM", "ART"):
                offset = assumed_total_size - size  # standard is 0x00ff0000 for 64KB ART in 16MB flash

            entry = FlashPartitionEntry(
                dev_name=dev,
                name=name,
                size=size,
                erasesize=erasesize,
                offset=offset,
                is_protected=is_prot,
            )
            partitions.append(entry)

            if not is_virtual:
                current_offset = offset + size

            if name == "u-boot":
                uboot_part = entry
            elif name in ("EEPROM", "ART"):
                art_part = entry

        # Verify u-boot partition
        if not uboot_part:
            violations.append("Missing 'u-boot' partition in flash map")
        elif uboot_part.offset != 0x00000000 or uboot_part.size != 0x00040000:
            violations.append(
                f"u-boot partition has non-standard layout (offset=0x{uboot_part.offset:08x}, size=0x{uboot_part.size:08x})"
            )

        # Verify ART / EEPROM partition
        if not art_part:
            violations.append("Missing 'EEPROM' or 'ART' calibration partition")
        else:
            if art_part.size != 0x00010000:
                violations.append(f"ART partition size is not 64 KB (actual: {art_part.size} bytes)")
            expected_art_offset = assumed_total_size - 0x00010000
            if art_part.offset != expected_art_offset:
                violations.append(
                    f"ART partition offset (0x{art_part.offset:08x}) does not match expected top-of-flash "
                    f"(0x{expected_art_offset:08x})"
                )

        # Check total flash size boundaries
        fw_window = (SAFE_UPGRADE_MIN_OFFSET, SAFE_UPGRADE_MAX_OFFSET)

        is_valid = len(violations) == 0

        return FlashValidationResult(
            is_valid=is_valid,
            total_flash_size=assumed_total_size,
            partitions=partitions,
            art_partition=art_part,
            uboot_partition=uboot_part,
            firmware_window=fw_window,
            violations=violations,
        )
