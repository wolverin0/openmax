import unittest

from tools.research.trace_target_consumers import branch_table, call8_target, scan_call8_candidates, validated_block


class ConsumerTraceTests(unittest.TestCase):
    def test_actual_positive_call(self):
        self.assertEqual(call8_target(bytes.fromhex("654603"), 0x9B2005), 0x9B546C)

    def test_actual_negative_call(self):
        self.assertEqual(call8_target(bytes.fromhex("e5e0ff"), 0x9B05EE), 0x9B03FC)

    def test_alignment_and_wrap(self):
        self.assertEqual(call8_target(bytes.fromhex("250000"), 0xFFFFFFFF), 0)

    def test_reject_other_calls_and_bad_pc(self):
        for instruction, pc in [(b"\x05\0\0", 0), (b"\x25\0", 0), (b"\x25\0\0", True), (b"\x25\0\0", -1)]:
            with self.assertRaises(ValueError):
                call8_target(instruction, pc)

    def test_scan_is_explicit_candidate(self):
        rows = scan_call8_candidates(bytes.fromhex("0065460300"), 0x9B2004, {0x9B546C})
        self.assertEqual(rows[0]["address"], 0x9B2005)
        self.assertEqual(rows[0]["status"], "BYTE_PATTERN_CANDIDATE_NOT_BOUNDARY_PROOF")

    def test_scan_limits(self):
        for data, base, targets in [(b"", 0, {1}), (b"x" * (1024 * 1024 + 1), 0, {1}), (b"abc", 0, set()), (b"abc", 0xFFFFFFFF, {1})]:
            with self.assertRaises(ValueError):
                scan_call8_candidates(data, base, targets)

    def test_contiguous_branch_rows(self):
        rows = [{"address": 10, "mnemonic": "j", "byte_length": 3, "operands": "9b2578"}]
        self.assertEqual(branch_table(rows, 10, 1)[0]["target"], 0x9B2578)

    def test_branch_reject_unknown_missing_and_duplicate(self):
        row = {"address": 10, "mnemonic": "j", "byte_length": 3, "operands": "9b2578"}
        for rows in [[], [dict(row, mnemonic=".byte")], [dict(row, byte_length=2)], [dict(row, operands="a8")], [row, row]]:
            with self.assertRaises(ValueError):
                branch_table(rows, 10, 1)

    def test_validated_block_discards_suffix(self):
        rows = [{"address": 10, "mnemonic": "retw.n", "byte_length": 2},
                {"address": 12, "mnemonic": ".byte", "byte_length": 1}]
        window = {"address": 10, "returncode": 0, "unparsed_instruction_line_count": 0,
                  "instructions": rows, "syntax_prefix_addresses": [10]}
        self.assertEqual(validated_block(window, 10), rows[:1])
        with self.assertRaises(ValueError):
            validated_block(window, 12)

    def test_validated_block_rejects_failed_decoder(self):
        with self.assertRaises(ValueError):
            validated_block({"returncode": 1}, 10)

    def test_validated_block_rejects_nonpositional_prefix(self):
        window = {"address": 10, "returncode": 0, "unparsed_instruction_line_count": 0,
                  "instructions": [{"address": 10, "mnemonic": ".byte", "byte_length": 1},
                                   {"address": 11, "mnemonic": "retw.n", "byte_length": 2}],
                  "syntax_prefix_addresses": [11]}
        with self.assertRaises(ValueError):
            validated_block(window, 11)


if __name__ == "__main__":
    unittest.main()
