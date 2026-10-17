"""Synthetic RAM-only fixtures; no device or proprietary-code acceptance."""
import hashlib
import json
import struct
import unittest

from tools.research.sgmt import decode_sgmt_memory, parse_sgmt
from tools.research.test_sgmt import fixture, record, MAGIC
from tools.research.target_firmware_map import loaded_regions, map_container, map_target, preceding_address_runs


class TargetMapTests(unittest.TestCase):
    def test_memory_decoder_matches_metadata(self):
        metadata, payloads = decode_sgmt_memory(fixture())
        self.assertEqual(metadata, parse_sgmt(fixture()))
        self.assertEqual(payloads, [(0x1000, b"abc")])
        json.dumps(metadata)

    def test_memory_decoder_rejects_bad_tail(self):
        with self.assertRaises(ValueError):
            decode_sgmt_memory(fixture() + b"bad")

    def test_memory_decoder_keeps_load_order(self):
        data = record(MAGIC, 0) + record(0x1000, 3) + b"abc" + record(0x1001, 3) + b"DEF" + record(0, 0xffffffff)
        _, payloads = decode_sgmt_memory(data)
        self.assertEqual(loaded_regions(payloads), [(0x1000, b"aDEF")])

    def test_overlay_splits_and_merges(self):
        self.assertEqual(loaded_regions([(10, b"abcdef"), (12, b"XY")]), [(10, b"abXYef")])

    def test_overlay_covers_multiple_regions(self):
        self.assertEqual(loaded_regions([(0, b"ab"), (4, b"ef"), (1, b"1234")]), [(0, b"a1234f")])

    def test_region_bounds(self):
        for value in ([(-1, b"a")], [(0xffffffff, b"ab")], [(True, b"a")], [(0, b"")]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                loaded_regions(value)

    def test_little_and_big_endian_word_candidates(self):
        payload = struct.pack("<I", 0x1008) + struct.pack(">I", 0x1008) + b"ubnt-poll\0"
        result = map_target([(0x1000, payload)])
        refs = result["string_anchors"][0]["aligned_word_matches"]
        self.assertEqual(refs["little"], [0x1000])
        self.assertEqual(refs["big"], [0x1004])
        self.assertEqual(result["loaded_regions"][0]["sha256"], hashlib.sha256(payload).hexdigest())
        json.dumps(result)

    def test_absolute_alignment_and_unaligned_exclusion(self):
        result = map_target([(0x1001, b"abc" + struct.pack("<I", 0x9064) + b"x" + struct.pack("<I", 0x9064))])
        self.assertEqual(result["command_literal_candidate"]["little"], [0x1004])

    def test_overwritten_pointer_is_not_reported(self):
        result = map_target([(0x1000, struct.pack("<I", 0x1004) + b"ubnt\0"), (0x1000, b"xxxx")])
        self.assertEqual(result["string_anchors"][0]["aligned_word_matches"]["little"], [])

    def test_adjacent_segment_string(self):
        result = map_target([(100, b"ub"), (102, b"nt\0")])
        self.assertEqual(result["string_anchors"][0]["text"], "ubnt")

    def test_only_terminated_interesting_strings(self):
        self.assertEqual(map_target([(0, b"normal\0ubnt")])["string_anchor_count"], 0)

    def test_long_unterminated_printable_run(self):
        self.assertEqual(map_target([(0, b"ubnt" + b"x" * (1024 * 1024))])["string_anchor_count"], 0)

    def test_exec_is_not_silently_flattened(self):
        data = fixture()[:-8] + record(0x1000, 0xfffffffc) + record(0, 0xffffffff)
        with self.assertRaisesRegex(ValueError, "EXEC"):
            map_container(data)

    def test_candidate_run_is_bounded_by_non_address(self):
        data = struct.pack("<IIII", 7, 0x2000, 0x2004, 0x9064)
        regions = [(0x1000, data), (0x2000, b"notcode!")]
        runs = preceding_address_runs(regions, [0x100c], [0x2000])
        self.assertEqual(runs[0]["start"], 0x1004)
        self.assertEqual(runs[0]["word_count"], 2)
        self.assertFalse(runs[0]["left_boundary_unproven"])
        self.assertEqual(runs[0]["entries"][1]["value"], 0x2004)

    def test_no_entrypoint_means_no_run(self):
        self.assertEqual(preceding_address_runs([(0, struct.pack("<II", 0, 0x9064))], [4], []), [])

    def test_run_bound_is_explicit(self):
        regions = [(0, struct.pack("<I", 0x2000) * 129 + struct.pack("<I", 0x9064)), (0x2000, b"code")]
        run = preceding_address_runs(regions, [129 * 4], [0x2000])[0]
        self.assertEqual(run["word_count"], 128)
        self.assertTrue(run["left_boundary_unproven"])


if __name__ == "__main__":
    unittest.main()
