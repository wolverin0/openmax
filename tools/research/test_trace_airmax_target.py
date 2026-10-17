import unittest
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.research.trace_airmax_target import l32r_addresses, trace


class LiteralModelTests(unittest.TestCase):
    def mocked_trace(self, disassembly, returncode=0):
        tool = {"probes": [{"family": family, "returncode": 0, "decode_returncode": 0,
                            "disassembly": f"  0: 006136 {family} a1,48\n"}
                           for family in ("entry", "callx8", "loopnez")],
                "windows": [{"address": 0x1000, "size": 6, "returncode": returncode,
                             "disassembly": disassembly}]}
        result = SimpleNamespace(returncode=0, stdout=json.dumps([tool]), stderr="")
        with patch("tools.research.trace_airmax_target.load_image", return_value=(
                {"container_sha256": "synthetic"}, [(0x1000, bytes.fromhex("210014210014"))])), \
                patch("tools.research.trace_airmax_target.subprocess.run", return_value=result):
            return trace(Path("synthetic"), "ptmp_ap", [0x1000], 6, "synthetic-", None)["tool"]["windows"][0]

    def test_duplicate_address_does_not_enrich_after_invalid_boundary(self):
        window = self.mocked_trace("  1000: 140021 l32r a2, 0\n  1000: 140021 l32r a2, 0\n")
        self.assertIn("literal_model", window["instructions"][0])
        self.assertNotIn("literal_model", window["instructions"][1])

    def test_failed_decode_never_enriches(self):
        window = self.mocked_trace("  1000: 140021 l32r a2, 0\n", returncode=1)
        self.assertEqual(window["syntax_stop_reason"], "decoder_failed")
        self.assertNotIn("literal_model", window["instructions"][0])

    def test_observed_entry_offset_model(self):
        result = l32r_addresses(bytes.fromhex("210014"), 0x983c03, 0x9bb001)
        self.assertEqual(result["signed_offset"], -0x3b000)
        self.assertEqual(result["pc_relative_address"], 0x948c04)
        self.assertEqual(result["hypothesis_literal_address"], 0x980000)
        self.assertEqual(result["status"], "CONDITIONAL_ON_UNVERIFIED_LITBASE")

    def test_no_hypothesis_does_not_invent_one(self):
        result = l32r_addresses(bytes.fromhex("210014"), 0x983c03, None)
        self.assertNotIn("hypothesis_literal_address", result)

    def test_operand_is_always_negative_before_base_addition(self):
        self.assertEqual(l32r_addresses(bytes.fromhex("21ffff"), 0x1000, None)["signed_offset"], -4)
        self.assertEqual(l32r_addresses(bytes.fromhex("210000"), 0x1000, None)["signed_offset"], -262144)

    def test_invalid_instruction_and_base(self):
        for encoded, pc, base in ((b"", 0, None), (b"\x20\0\0", 0, None),
                                  (b"\x21\0\0", True, None), (b"\x21\0\0", 0, 0x980000),
                                  (b"\x21\0\0", 0, 0x980003)):
            with self.subTest(encoded=encoded, base=base), self.assertRaises(ValueError):
                l32r_addresses(encoded, pc, base)


if __name__ == "__main__":
    unittest.main()
