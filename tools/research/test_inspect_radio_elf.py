import hashlib
import struct
import tempfile
import unittest
from pathlib import Path

from tools.research.inspect_radio_elf import bounded_slice, describe_blob, inspect, RADIO_NAME


def synthetic_module(endian=">", radio_data=b"SGMT"):
    """Tiny ELF32 ET_REL with a nonzero sh_addr, named JAL and embedded SGMT fixture."""
    strings = b"\0ubnt_poll_fixture\0wmi_fixture\0athwlan_AR9888v2_ptp_bin\0athwlan_AR9888v2_ptp_bin_len\0"
    names = b"\0.text\0.data\0.strtab\0.symtab\0.rel.text\0.shstrtab\0"
    sym = lambda name, value, size, kind, section: struct.pack(
        endian + "IIIBBH", strings.index(name) if name else 0, value, size, kind, 0, section)
    symbols = b"\0" * 16
    symbols += sym(b"ubnt_poll_fixture", 0, 4, 0x12, 1)
    symbols += sym(b"wmi_fixture", 4, 4, 0x12, 1)
    symbols += sym(b"athwlan_AR9888v2_ptp_bin\0", 0, len(radio_data), 0x11, 2)
    symbols += sym(b"athwlan_AR9888v2_ptp_bin_len", len(radio_data), 4, 0x11, 2)
    parts = [(b".text", 1, struct.pack(endian + "II", 0x0c000001, 0), 0, 0, 0),
             (b".data", 1, radio_data + struct.pack(endian + "I", len(radio_data)), 0, 0, 0),
             (b".strtab", 3, strings, 0, 0, 0),
             (b".symtab", 2, symbols, 3, 1, 16),
             (b".rel.text", 9, struct.pack(endian + "II", 0, (2 << 8) | 4), 4, 1, 8),
             (b".shstrtab", 3, names, 0, 0, 0)]
    result = bytearray(52)
    headers = [b"\0" * 40]
    for name, kind, data, link, info, entrysize in parts:
        result.extend(b"\0" * (-len(result) % 4))
        offset = len(result)
        result.extend(data)
        headers.append(struct.pack(endian + "10I", names.index(name), kind, 0,
                                   0x1000, offset, len(data), link, info, 4, entrysize))
    result.extend(b"\0" * (-len(result) % 4))
    section_offset = len(result)
    result.extend(b"".join(headers))
    ident = b"\x7fELF" + bytes([1, 2 if endian == ">" else 1, 1]) + b"\0" * 9
    result[:52] = ident + struct.pack(endian + "HHIIIIIHHHHHH", 1, 8, 1, 0, 0,
                                      section_offset, 0, 52, 0, 0, 40, 7, 6)
    return bytes(result)


class RadioMetadataTests(unittest.TestCase):
    def test_slice_exact_end(self):
        self.assertEqual(bounded_slice(b"abcdef", 3, 3), b"def")

    def test_invalid_ranges_fail_closed(self):
        for offset, size in [(-1, 1), (0, 0), (0, -1), (6, 1), (2, 5), (10**30, 1)]:
            with self.subTest(offset=offset, size=size), self.assertRaises(ValueError):
                bounded_slice(b"abcdef", offset, size)

    def test_length_disagreement_fails(self):
        with self.assertRaises(ValueError):
            describe_blob(b"SGMT", 5)

    def test_hash_and_marker_offsets(self):
        data = b"SGMTubnt-poll--ubnt-poll"
        result = describe_blob(data, len(data))
        self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(result["magic_hex"], "53474d54")
        self.assertEqual(result["markers"]["ubnt-poll"], [4, 15])
        self.assertEqual(result["markers"]["_on_swbmiss"], [])

    def test_only_exact_radio_symbols(self):
        self.assertTrue(RADIO_NAME.fullmatch("athwlan_AR9888v2_ptmp_ap_bin"))
        self.assertFalse(RADIO_NAME.fullmatch("athwlan_AR9888v2_ptmp_ap_bin_len"))

    def test_et_rel_offsets_lengths_and_call_decoding_both_endians(self):
        for endian in (">", "<"):
            with self.subTest(endian=endian), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "fixture.ko"
                path.write_bytes(synthetic_module(endian))
                result = inspect(path, decode_mips=True)
                self.assertEqual(result["embedded_radio_images"]["athwlan_AR9888v2_ptp_bin"]["size"], 4)
                reference = result["relocation_references"][0]
                self.assertEqual(reference["owner"], "ubnt_poll_fixture")
                self.assertEqual(reference["target"], "wmi_fixture")
                self.assertEqual(reference["relocated_section"], ".text")
                self.assertEqual(reference["instruction"], "jal")
                self.assertTrue(reference["named_jal_relocation"])
                self.assertEqual(reference["encoded_target_field"], 4)

    def test_tail_jump_not_mislabeled_jal(self):
        with tempfile.TemporaryDirectory() as directory:
            data = bytearray(synthetic_module())
            data[52:56] = struct.pack(">I", 0x08000001)
            path = Path(directory) / "tail.ko"
            path.write_bytes(data)
            reference = inspect(path, decode_mips=True)["relocation_references"][0]
            self.assertEqual(reference["instruction"], "j")
            self.assertFalse(reference["named_jal_relocation"])

    def test_elf_embedded_length_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            data = bytearray(synthetic_module())
            data[64:68] = struct.pack(">I", 5)
            path = Path(directory) / "bad-length.ko"
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "length disagrees"):
                inspect(path)

    def test_sgmt_analysis_inside_elf_is_metadata_only(self):
        from tools.research.sgmt import MAGIC
        data = struct.pack("<IIII", MAGIC, 1, 0x1000, 3) + b"\xffabc" + struct.pack("<II", 0, 0xFFFFFFFF)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "container.ko"
            path.write_bytes(synthetic_module(radio_data=data))
            result = inspect(path, analyze_sgmt=True)["embedded_radio_images"]["athwlan_AR9888v2_ptp_bin"]["sgmt"]
            self.assertEqual(result["decoded_total"], 3)
            self.assertEqual(result["consumed_bytes"], len(data))
            self.assertEqual(result["records"][0]["decoded_sha256"], hashlib.sha256(b"abc").hexdigest())

    def test_invalid_sgmt_fails_optional_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid-container.ko"
            path.write_bytes(synthetic_module())
            with self.assertRaisesRegex(ValueError, "truncated file header"):
                inspect(path, analyze_sgmt=True)


if __name__ == "__main__":
    unittest.main()
