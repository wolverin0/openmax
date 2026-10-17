"""Manufactured format vectors, not device captures or acceptance evidence."""
import hashlib
import struct
import unittest
from unittest.mock import patch

from tools.research.sgmt import MAGIC, MAX_OUTPUT, parse_sgmt


def record(address, length):
    return struct.pack("<II", address, length)


def fixture(payload=b"\xffabc", size=3, flags=1):
    return record(MAGIC, flags) + record(0x1000, size) + payload + record(0, 0xFFFFFFFF)


class SGMTTests(unittest.TestCase):
    def test_literals_hash_and_consumption(self):
        data = fixture()
        result = parse_sgmt(data)
        self.assertEqual(result["consumed_bytes"], len(data))
        self.assertEqual(result["decoded_total"], 3)
        self.assertEqual(result["records"][0]["decoded_sha256"], hashlib.sha256(b"abc").hexdigest())
        self.assertEqual(result["records"][0]["compressed_bytes"], 4)
        self.assertNotIn("payload", result["records"][0])

    def test_marker_escape(self):
        self.assertEqual(parse_sgmt(fixture(b"\xff\xff\0", 1))["decoded_total"], 1)

    def test_overlapping_backreference(self):
        result = parse_sgmt(fixture(b"\xffa\xff\x05\x01", 6))
        self.assertEqual(result["records"][0]["decoded_sha256"], hashlib.sha256(b"aaaaaa").hexdigest())

    def test_multibyte_varint(self):
        result = parse_sgmt(fixture(b"\xffa\xff\x81\0\x01", 129))
        self.assertEqual(result["decoded_total"], 129)

    def test_invalid_backreference(self):
        for payload in (b"\xff\xff\x03\x01", b"\xffa\xff\x03\0"):
            with self.subTest(payload=payload), self.assertRaisesRegex(ValueError, "back-reference"):
                parse_sgmt(fixture(payload, 4))

    def test_decoded_overrun(self):
        with self.assertRaisesRegex(ValueError, "overrun"):
            parse_sgmt(fixture(b"\xffa\xff\x05\x01", 2))

    def test_truncation(self):
        for data in (b"", record(MAGIC, 1), record(MAGIC, 1) + record(0, 3),
                     record(MAGIC, 1) + record(0, 3) + b"\xff\xff",
                     record(MAGIC, 1) + record(0, 3) + b"\xffa\xff\x81"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse_sgmt(data)

    def test_varint_overflow_and_too_long(self):
        for token in (b"\x90\x80\x80\x80\0", b"\x80" * 5):
            with self.subTest(token=token), self.assertRaisesRegex(ValueError, "varint"):
                parse_sgmt(fixture(b"\xffa\xff" + token, 3))

    def test_output_limit(self):
        with self.assertRaisesRegex(ValueError, "output limit"):
            parse_sgmt(fixture(b"", MAX_OUTPUT + 1))

    def test_aggregate_output_limit(self):
        data = fixture()[:-8] + record(0x2000, 3) + b"\xffabc" + record(0, 0xFFFFFFFF)
        with patch("tools.research.sgmt.MAX_OUTPUT", 5), self.assertRaisesRegex(ValueError, "output limit"):
            parse_sgmt(data)

    def test_sequential_overlapping_destinations_allowed(self):
        data = fixture()[:-8] + record(0x1001, 3) + b"\xffdef" + record(0, 0xFFFFFFFF)
        result = parse_sgmt(data)
        self.assertEqual(result["decoded_total"], 6)
        self.assertEqual(result["records"][1]["destination"], 0x1001)

    def test_input_limit(self):
        with self.assertRaisesRegex(ValueError, "input limit"):
            parse_sgmt(b"\0" * (16 * 1024 * 1024 + 1))

    def test_address_overflow(self):
        with self.assertRaisesRegex(ValueError, "range overflow"):
            parse_sgmt(record(MAGIC, 1) + record(0xFFFFFFFF, 2))

    def test_trailing_and_missing_done(self):
        for data in (fixture() + b"\0", fixture()[:-8]):
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse_sgmt(data)

    def test_unknown_flags_magic_and_zero_length(self):
        for data in (fixture(flags=2), record(0, 1), fixture(b"", 0)):
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse_sgmt(data)

    def test_special_records(self):
        data = record(MAGIC, 1) + record(0x1234, 0xFFFFFFFD) + record(0x5678, 0xFFFFFFFC) + record(0, 0xFFFFFFFF)
        self.assertEqual([r["kind"] for r in parse_sgmt(data)["records"]], ["BEGINADDR", "EXEC", "DONE"])
        for length in (0xFFFFFFFE, 0xFFFFFFFB):
            with self.subTest(length=length), self.assertRaisesRegex(ValueError, "special"):
                parse_sgmt(record(MAGIC, 1) + record(0, length))

    def test_record_limit(self):
        with self.assertRaisesRegex(ValueError, "record count"):
            parse_sgmt(record(MAGIC, 1) + record(0, 0xFFFFFFFD) * 128 + record(0, 0xFFFFFFFF))

    def test_uncompressed(self):
        result = parse_sgmt(fixture(b"abc", flags=0))
        self.assertEqual(result["records"][0]["compressed_bytes"], 0)
        self.assertEqual(result["records"][0]["stored_bytes"], 3)
        with self.assertRaisesRegex(ValueError, "uncompressed"):
            parse_sgmt(record(MAGIC, 0) + record(0, 3) + b"a")

    def test_type(self):
        with self.assertRaises(TypeError):
            parse_sgmt(bytearray(fixture()))


if __name__ == "__main__":
    unittest.main()
