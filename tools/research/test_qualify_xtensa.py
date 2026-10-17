import unittest

from tools.research.qualify_xtensa import assess_window, memory_window, parse_disassembly


class XtensaQualificationTests(unittest.TestCase):
    def test_last_write_wins_per_byte(self):
        self.assertEqual(memory_window([(10, b"abcdef"), (12, b"XY")], 10, 6), b"abXYef")

    def test_adjacent_regions_supported(self):
        self.assertEqual(memory_window([(10, b"ab"), (12, b"cd")], 11, 3), b"bcd")

    def test_unmapped_gap_not_zero_filled(self):
        with self.assertRaisesRegex(ValueError, "unmapped"):
            memory_window([(10, b"ab"), (13, b"cd")], 10, 5)

    def test_invalid_ranges_fail_closed(self):
        for address, size in ((-1, 1), (0, 0), (0, 257), (0xFFFFFFFF, 2), (True, 1), (0, 1.0)):
            with self.subTest(address=address, size=size), self.assertRaises(ValueError):
                memory_window([], address, size)

    def test_parse_bounded_objdump_rows(self):
        text = "00983c00 <.data>:\n  983c00:\t006136\tentry a1, 48\n  983c03:\t140021\tl32r a2, 0x948c04\n"
        rows = parse_disassembly(text)
        self.assertEqual(rows[0], {"address": 0x983C00, "mnemonic": "entry", "operands": "a1, 48", "byte_length": 3})
        self.assertEqual(rows[1]["mnemonic"], "l32r")

    def test_excws_preserved_not_discarded(self):
        self.assertEqual(parse_disassembly("  983c00: 006136 excw\n")[0]["mnemonic"], "excw")

    def test_unknown_directives_not_discarded(self):
        row = parse_disassembly("  983c03: ff .byte 0xff\n")[0]
        self.assertEqual(row["mnemonic"], ".byte")
        self.assertEqual(row["byte_length"], 1)

    def test_failed_decoder_has_no_usable_prefix(self):
        report = assess_window("  1000: f03d nop.n\n", 0x1000, 2, 1)
        self.assertEqual(report["syntax_prefix_addresses"], [])
        self.assertFalse(report["syntax_coverage_only"])

    def test_duplicate_gap_and_overrun_are_not_coverage(self):
        for second in ("1000", "1003", "1004"):
            report = assess_window(f"  1000: f03d nop.n\n  {second}: f03d nop.n\n", 0x1000, 4, 0)
            self.assertFalse(report["syntax_coverage_only"])
            self.assertEqual(report["syntax_prefix_addresses"], [0x1000])

    def test_unknown_ends_prefix_even_with_later_valid_rows(self):
        report = assess_window("  1000: f03d nop.n\n  1002: ff .byte 0xff\n  1003: f03d nop.n\n", 0x1000, 5, 0)
        self.assertEqual(report["syntax_prefix_addresses"], [0x1000])

    def test_unparsed_address_line_invalidates_prefix(self):
        report = assess_window("  1000: f03d nop.n\n  1002: ?? broken\n", 0x1000, 4, 0)
        self.assertEqual(report["syntax_prefix_addresses"], [])
        self.assertEqual(report["unparsed_instruction_line_count"], 1)

    def test_exact_contiguous_syntax_coverage(self):
        report = assess_window("  1000: f03d nop.n\n  1002: f03d nop.n\n", 0x1000, 4, 0)
        self.assertTrue(report["syntax_coverage_only"])


if __name__ == "__main__":
    unittest.main()
