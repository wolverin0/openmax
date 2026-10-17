"""Disposable byte-check fixtures; never execute firmware or mutate real inputs."""
import unittest
import tempfile
from pathlib import Path
from re1_pilot import validate_window_bytes, compare_xtensa


class ByteQualificationTests(unittest.TestCase):
    def test_identical_bytes(self):
        self.assertEqual(validate_window_bytes(bytes.fromhex("12345678"), {0: {"hex": "12345678"}}, 0, 4, {}), [])

    def test_undeclared_mismatch_fails(self):
        with self.assertRaisesRegex(ValueError, "Undeclared"):
            validate_window_bytes(bytes.fromhex("12345678"), {0: {"hex": "12345679"}}, 0, 4, {})

    def test_declared_relocation_preserves_original_and_limit(self):
        changed = validate_window_bytes(bytes.fromhex("12345678"), {0: {"hex": "12345679"}},
                                        0, 4, {0: {"symbol": ".text", "elf_relocation_type": 4}})
        self.assertEqual(changed[0]["original_hex"], "12345678")
        self.assertIn("not runtime", changed[0]["status"])

    def test_missing_ghidra_row_fails(self):
        with self.assertRaises(KeyError):
            validate_window_bytes(bytes.fromhex("12345678"), {}, 0, 4, {})

    def test_declared_relocation_cannot_change_opcode(self):
        with self.assertRaisesRegex(ValueError, "opcode/register"):
            validate_window_bytes(bytes.fromhex("12345678"), {0: {"hex": "22345678"}},
                                  0, 4, {0: {"symbol": ".text", "elf_relocation_type": 4}})

    def test_prior_oracle_tampering_fails(self):
        with tempfile.TemporaryDirectory(prefix="re1-fixture-") as fixture:
            root = Path(fixture)
            (root / "research/raw").mkdir(parents=True)
            (root / "research/raw/xtensa-qualification-20261006-elf.json").write_text('{}')
            with self.assertRaisesRegex(ValueError, "receipt changed"):
                compare_xtensa(root, root, [])


if __name__ == "__main__":
    unittest.main()
