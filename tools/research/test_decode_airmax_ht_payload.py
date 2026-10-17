import struct
import unittest

from tools.research.decode_airmax_ht_payload import COMMAND_ID, decode


class AirmaxLayoutTests(unittest.TestCase):
    def setUp(self):
        # Manufactured parser vectors, not captures or device evidence.
        self.txq = struct.pack(">IBHHBHHHI", 1, 0xAB, 0x17, 0x1234, 3, 15, 1023, 7, 0x10203040)
        self.rate = struct.pack(">IBHH5B", 1, 0, 0x1E, 0, 1, 2, 3, 4, 5)

    def parse(self, data, stage="serializer-buffer", command=COMMAND_ID):
        return decode(data, command_id=command, buffer_stage=stage)

    def test_positional_txq_layout(self):
        result = self.parse(self.txq)
        self.assertEqual(result["logical_length"], 20)
        self.assertEqual(result["opaque_header_byte"], 0xAB)
        self.assertEqual(result["opaque_header_halfword"], 0x1234)
        self.assertEqual(result["fields"], {"u8_0": 3, "u16_0": 15, "u16_1": 1023,
                                           "u16_2": 7, "u32_0": 0x10203040})

    def test_rate_five_bytes(self):
        self.assertEqual(self.parse(self.rate)["fields"], {f"u8_{i}": i + 1 for i in range(5)})

    def test_dword_swapped_padded_stage(self):
        padded = self.rate + b"\0\0"
        swapped = b"".join(padded[i:i + 4][::-1] for i in range(0, 16, 4))
        self.assertEqual(self.parse(swapped, "host-wmi-buffer")["fields"], self.parse(self.rate)["fields"])

    def test_bad_padding_rejected(self):
        padded = self.rate + b"\0\1"
        swapped = b"".join(padded[i:i + 4][::-1] for i in range(0, 16, 4))
        with self.assertRaisesRegex(ValueError, "padding"):
            self.parse(swapped, "host-wmi-buffer")

    def test_lengths_rejected(self):
        for value in (b"", b"\0" * 8, self.txq[:-1], self.txq + b"\0", b"\0" * 1025):
            with self.subTest(size=len(value)), self.assertRaises(ValueError):
                self.parse(value)

    def test_unaligned_transport_rejected(self):
        with self.assertRaisesRegex(ValueError, "aligned"):
            self.parse(self.rate, "host-wmi-buffer")

    def test_unknown_type_header_and_namespace_rejected(self):
        for value in (struct.pack(">IBHH", 1, 0, 0x18, 0), b"\0\0\0\2" + self.txq[4:]):
            with self.assertRaises(ValueError):
                self.parse(value)
        with self.assertRaises(ValueError):
            self.parse(self.txq, command=0x9009)

    def test_stage_must_be_explicit_and_correct(self):
        with self.assertRaises(ValueError):
            self.parse(self.txq, "wire")
        with self.assertRaises(ValueError):
            self.parse(self.txq, "host-wmi-buffer")


if __name__ == "__main__":
    unittest.main()
