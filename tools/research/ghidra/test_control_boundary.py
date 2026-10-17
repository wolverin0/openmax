"""Disposable static-memory fixtures for RE1.6; no device/service access."""
import tempfile
import unittest
from pathlib import Path

from control_boundary import checked_bytes, survey_regions


class ControlBoundaryTests(unittest.TestCase):
    def test_absent_slot_is_unknown_not_zero(self):
        row = survey_regions([(0x980000, b"\x00" * 8)])["0x406414"]
        self.assertFalse(row["four_byte_slot_covered"])
        self.assertIsNone(row["slot_word_le"])

    def test_register_hypothesis_is_not_dereferenced(self):
        self.assertNotIn("0x9bb001", survey_regions([(0x9BB001, bytes(4))]))

    def test_partial_slot_not_covered(self):
        self.assertFalse(survey_regions([(0x406414, b"\x00" * 3)])["0x406414"]["four_byte_slot_covered"])

    def test_zero_slot_is_distinct_from_absence(self):
        row = survey_regions([(0x406414, bytes(4))])["0x406414"]
        self.assertTrue(row["four_byte_slot_covered"])
        self.assertEqual(row["slot_word_le"], "0x0")

    def test_alignment_uses_mapped_address_not_buffer(self):
        literal = (0x4062DC).to_bytes(4, "little")
        result = survey_regions([(0x980001, b"\x00" * 3 + literal + b"\x00")])
        self.assertEqual(result["0x4062dc"]["aligned_literal_addresses"], ["0x980004"])
        self.assertEqual(survey_regions([(0x980001, literal)])["0x4062dc"]["aligned_literal_count"], 0)

    def test_candidate_cap_retains_total(self):
        row = survey_regions([(0x980000, (0x4062DC).to_bytes(4, "little") * 40)])["0x4062dc"]
        self.assertEqual(row["aligned_literal_count"], 40)
        self.assertEqual(len(row["aligned_literal_addresses"]), 32)
        self.assertTrue(row["matches_truncated"])

    def test_tampered_input_rejected(self):
        with tempfile.TemporaryDirectory(prefix="re16-fixture-") as temp:
            path = Path(temp) / "input.bin"
            path.write_bytes(b"fixture")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                checked_bytes(path, "0" * 64)


if __name__ == "__main__":
    unittest.main()
