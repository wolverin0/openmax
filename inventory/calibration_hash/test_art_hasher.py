"""
Unit tests for ART calibration partition hasher and integrity verifier.
"""

import unittest
from inventory.calibration_hash.art_hasher import ARTHasher, ART_PARTITION_SIZE


class TestARTHasher(unittest.TestCase):

    def build_synthetic_art(self, mac: bytes = b"\x00\x27\x22\x1a\x2b\x3c", version: int = 0x0202) -> bytes:
        """Create a valid synthetic 64 KB ART blob."""
        buf = bytearray(b"\x00" * ART_PARTITION_SIZE)
        buf[0:2] = version.to_bytes(2, "big")
        buf[2:8] = mac
        # Fill some pseudo RF calibration tables
        for i in range(0x1000, 0x2000):
            buf[i] = (i * 7) % 256
        return bytes(buf)

    def test_valid_art_parsing(self):
        art_bytes = self.build_synthetic_art()
        profile = ARTHasher.parse_and_hash(art_bytes, board_model="LAP-120")
        self.assertTrue(profile.is_valid)
        self.assertEqual(profile.mac_address, "00:27:22:1a:2b:3c")
        self.assertEqual(len(profile.sha256), 64)
        self.assertEqual(profile.calibration_version, 0x0202)

    def test_invalid_size_rejection(self):
        short_art = b"\x00" * 1024
        profile = ARTHasher.parse_and_hash(short_art)
        self.assertFalse(profile.is_valid)
        self.assertIn("Invalid size", profile.summary)

    def test_erased_flash_detection(self):
        erased_art = b"\xff" * ART_PARTITION_SIZE
        profile = ARTHasher.parse_and_hash(erased_art)
        self.assertFalse(profile.is_valid)
        self.assertIn("CORRUPTED/ERASED", profile.summary)

    def test_golden_hash_verification(self):
        art_bytes = self.build_synthetic_art()
        profile = ARTHasher.parse_and_hash(art_bytes)
        
        # Test match
        matched, msg = ARTHasher.verify_golden_match(art_bytes, profile.sha256)
        self.assertTrue(matched)
        self.assertIn("100% bit-exact", msg)

        # Test tamper
        tampered_hash = "0" * 64
        matched_tamper, msg_tamper = ARTHasher.verify_golden_match(art_bytes, tampered_hash)
        self.assertFalse(matched_tamper)
        self.assertIn("DRIFT DETECTED", msg_tamper)


if __name__ == "__main__":
    unittest.main()
