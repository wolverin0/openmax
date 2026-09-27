"""
Atheros Radio Test (ART / EEPROM) Partition Calibration Hash and Integrity Verifier.
Protects and verifies mtd5 (64 KB) across firmware upgrades and research runs.

Enforces AGENTS.md Section 4:
- Never modify calibration/ART/factory/MAC-address partitions.
- Every flash workflow must include checksum and health check.
"""

import hashlib
import struct
from dataclasses import dataclass
from typing import Tuple, Dict, Optional


ART_PARTITION_SIZE = 64 * 1024  # 65,536 bytes (64 KB)


@dataclass
class CalibrationProfile:
    sha256: str
    md5: str
    mac_address: str
    board_model: str
    calibration_version: int
    is_valid: bool
    summary: str


class ARTHasher:
    """Verifies cryptographic integrity and extracts key parameters from the 64 KB ART partition."""

    @staticmethod
    def parse_and_hash(art_bytes: bytes, board_model: str = "Unknown") -> CalibrationProfile:
        """
        Parses raw 64 KB ART partition bytes and generates cryptographic profile.
        """
        if len(art_bytes) != ART_PARTITION_SIZE:
            return CalibrationProfile(
                sha256="",
                md5="",
                mac_address="",
                board_model=board_model,
                calibration_version=0,
                is_valid=False,
                summary=f"Invalid size: expected exactly {ART_PARTITION_SIZE} bytes, got {len(art_bytes)} bytes."
            )

        sha256_hash = hashlib.sha256(art_bytes).hexdigest()
        md5_hash = hashlib.md5(art_bytes).hexdigest()

        # Atheros ART layout on AR934x:
        # Offset 0x0000: 2 bytes magic/version
        # Offset 0x0002: 6 bytes MAC address
        cal_version = struct.unpack(">H", art_bytes[:2])[0]
        mac_raw = art_bytes[2:8]
        mac_str = ":".join(f"{b:02x}" for b in mac_raw)

        # Basic validity check: MAC address should not be all 0x00 or all 0xFF
        is_valid_mac = (mac_raw != b"\x00" * 6) and (mac_raw != b"\xff" * 6)

        # Check for empty/erased flash (all 0xFF)
        is_erased = all(b == 0xFF for b in art_bytes)

        is_valid = is_valid_mac and not is_erased

        summary = (
            f"ART Profile for {board_model} | MAC: {mac_str} | "
            f"Version: 0x{cal_version:04x} | SHA-256: {sha256_hash[:16]}... | "
            f"Status: {'VALID' if is_valid else 'CORRUPTED/ERASED'}"
        )

        return CalibrationProfile(
            sha256=sha256_hash,
            md5=md5_hash,
            mac_address=mac_str,
            board_model=board_model,
            calibration_version=cal_version,
            is_valid=is_valid,
            summary=summary
        )

    @staticmethod
    def verify_golden_match(live_art_bytes: bytes, golden_sha256: str) -> Tuple[bool, str]:
        """
        Compares live ART bytes against golden backup hash.
        Guarantees zero RF calibration drift.
        """
        profile = ARTHasher.parse_and_hash(live_art_bytes)
        if not profile.is_valid:
            return False, f"Live ART data is corrupted or invalid: {profile.summary}"

        if profile.sha256.lower() != golden_sha256.lower():
            return False, (
                f"CALIBRATION DRIFT DETECTED! Live hash {profile.sha256} does NOT match "
                f"golden backup hash {golden_sha256}. Physical RF calibration was modified!"
            )

        return True, f"VERIFIED: 100% bit-exact calibration match with golden reference. MAC: {profile.mac_address}"
