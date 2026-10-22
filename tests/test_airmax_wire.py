"""Unit tests for controller/airmax_wire.py wire protocol serialization.

Validates binary wire formats against specifications in docs/UMAC_DATAPATH.md:
- WMI rate schedule 188-byte layout and opcodes (Gen1 0x9044, Gen2 0x9045)
- airMAX Poll Subtype 0x1E (16 bytes, RateByte packing for Xtensa 0x009b7684)
- airMAX Poll Subtype 0x17 (20 bytes, halfwords AIFS, CWmin, CWmax, bitmask 0x3a10)
- HTT Type 5 aggregation config packed word: 5 | (max_ampdu << 8) | (max_amsdu << 16)
- 32-bit dword endianness swap between MIPS host (BE) and Xtensa target (LE)
"""

import struct
import unittest

from controller.airmax_wire import (
    HTT_TAG_AGGR_CFG,
    POLL_SUBTYPE_RATE_OVERRIDE,
    POLL_SUBTYPE_TXQ,
    TXQ_QFLAGS_MASK,
    WHAL_VHT20_BASE_INDEX,
    WHAL_VHT40_BASE_INDEX,
    WHAL_VHT80_BASE_INDEX,
    WMI_RATE_SCHED_CMDID_GEN1,
    WMI_RATE_SCHED_CMDID_GEN2,
    WMI_UBNT_POLL_CMDID_GEN1,
    WMI_UBNT_POLL_CMDID_GEN2,
    WmiRateSchedule,
    build_htt_type5_aggr_cfg,
    build_poll_subtype_17_txq,
    build_poll_subtype_1e_rate_override,
    build_wmi_rate_schedule_188b,
    decode_rate_byte,
    encode_rate_byte,
    endian_swap_dword,
    get_whal_code_byte,
    get_whal_rate_index,
    normalize_bw,
    parse_htt_type5_aggr_cfg,
    parse_poll_subtype_17_txq,
    parse_poll_subtype_1e_rate_override,
    parse_wmi_rate_schedule_188b,
)


class TestAirmaxWireProtocol(unittest.TestCase):
    """Test suite for binary wire serializers and deserializers."""

    def test_endian_swap_dword_int(self):
        """Test 32-bit dword endian swap on integer values."""
        self.assertEqual(endian_swap_dword(0x12345678), 0x78563412)
        self.assertEqual(endian_swap_dword(0x00000001), 0x01000000)
        self.assertEqual(endian_swap_dword(0x80000000), 0x00000080)
        # Roundtrip idempotence
        val = 0xA1B2C3D4
        self.assertEqual(endian_swap_dword(endian_swap_dword(val)), val)

    def test_endian_swap_dword_bytes(self):
        """Test 32-bit dword endian swap on byte buffers."""
        data = b"\x01\x02\x03\x04\x10\x20\x30\x40"
        expected = b"\x04\x03\x02\x01\x40\x30\x20\x10"
        swapped = endian_swap_dword(data)
        self.assertEqual(swapped, expected)
        # Roundtrip
        self.assertEqual(endian_swap_dword(swapped), data)

    def test_endian_swap_dword_length_validation(self):
        """Test that dword swap enforces 4-byte alignment unless padding is requested."""
        with self.assertRaises(ValueError):
            endian_swap_dword(b"\x01\x02\x03")

        # With padding requested, should pad to 4 bytes
        padded = endian_swap_dword(b"\x01\x02", pad=True)
        self.assertEqual(len(padded), 4)
        self.assertEqual(padded, b"\x00\x00\x02\x01")

    def test_htt_type5_aggr_cfg_formula(self):
        """Test HTT Type 5 aggregation packed word formula: 5 | (max_ampdu << 8) | (max_amsdu << 16)."""
        # Minimum non-zero values
        w1 = build_htt_type5_aggr_cfg(max_ampdu=1, max_amsdu=1)
        self.assertEqual(w1, 5 | (1 << 8) | (1 << 16))
        self.assertEqual(w1, 0x00010105)

        # Standard maximum values: 64 AMPDU subframes, 31 AMSDU subframes
        w_max = build_htt_type5_aggr_cfg(max_ampdu=64, max_amsdu=31)
        expected = 5 | (64 << 8) | (31 << 16)
        self.assertEqual(w_max, expected)
        self.assertEqual(w_max, 0x001F4005)

        # Low byte must be tag 5
        self.assertEqual(w_max & 0xFF, HTT_TAG_AGGR_CFG)
        # Shift 8 must be AMPDU limit (64 = 0x40)
        self.assertEqual((w_max >> 8) & 0xFF, 64)
        # Shift 16 must be AMSDU limit (31 = 0x1F)
        self.assertEqual((w_max >> 16) & 0xFF, 31)

    def test_htt_type5_aggr_cfg_bounds(self):
        """Test boundary checking for HTT type 5 aggregation parameters."""
        with self.assertRaises(ValueError):
            build_htt_type5_aggr_cfg(max_ampdu=65, max_amsdu=10)
        with self.assertRaises(ValueError):
            build_htt_type5_aggr_cfg(max_ampdu=-1, max_amsdu=10)
        with self.assertRaises(ValueError):
            build_htt_type5_aggr_cfg(max_ampdu=32, max_amsdu=32)
        with self.assertRaises(ValueError):
            build_htt_type5_aggr_cfg(max_ampdu=32, max_amsdu=-1)

    def test_htt_type5_aggr_cfg_parser(self):
        """Test parsing of HTT Type 5 packed word."""
        word = build_htt_type5_aggr_cfg(max_ampdu=32, max_amsdu=16)
        ampdu, amsdu = parse_htt_type5_aggr_cfg(word)
        self.assertEqual(ampdu, 32)
        self.assertEqual(amsdu, 16)

        # From bytes
        packed_bytes = struct.pack(">I", word)
        ampdu_b, amsdu_b = parse_htt_type5_aggr_cfg(packed_bytes)
        self.assertEqual(ampdu_b, 32)
        self.assertEqual(amsdu_b, 16)

        # Invalid tag rejection
        with self.assertRaises(ValueError):
            parse_htt_type5_aggr_cfg(0x00101006)

    def test_rate_byte_encoding_xtensa_formula(self):
        """Test RateByte = ((MCS << 1) & 0x1E) | BandwidthFlag | StreamFlag against Xtensa deserializer at 0x009b7684."""
        # 20MHz, 1SS, MCS0:
        # BandwidthFlag = 0x00, StreamFlag = 0, MCS = 0 -> 0x00
        self.assertEqual(encode_rate_byte(mcs=0, bw=20, nss=1), 0x00)

        # 20MHz, 2SS, MCS7:
        # MCS << 1 = 14 = 0x0E, BandwidthFlag = 0x00, StreamFlag = 1 -> 0x0F
        self.assertEqual(encode_rate_byte(mcs=7, bw=20, nss=2), 0x0F)

        # 40MHz, 1SS, MCS7:
        # MCS << 1 = 14 = 0x0E, BandwidthFlag = 0x20, StreamFlag = 0 -> 0x2E
        self.assertEqual(encode_rate_byte(mcs=7, bw=40, nss=1), 0x2E)

        # 40MHz, 2SS, MCS7:
        # MCS << 1 = 14 = 0x0E, BandwidthFlag = 0x20, StreamFlag = 1 -> 0x2F
        self.assertEqual(encode_rate_byte(mcs=7, bw=40, nss=2), 0x2F)

        # 80MHz, 2SS, MCS9:
        # MCS << 1 = 18 = 0x12, BandwidthFlag = 0x40, StreamFlag = 1 -> 0x53
        self.assertEqual(encode_rate_byte(mcs=9, bw=80, nss=2), 0x53)

        # 80MHz, 1SS, MCS9:
        # MCS << 1 = 18 = 0x12, BandwidthFlag = 0x40, StreamFlag = 0 -> 0x52
        self.assertEqual(encode_rate_byte(mcs=9, bw=80, nss=1), 0x52)

        # Verify bits partition
        for mcs in range(10):
            for bw in (20, 40, 80):
                for nss in (1, 2):
                    rb = encode_rate_byte(mcs, bw, nss)
                    # Bit 0 must equal stream flag (1 for 2SS, 0 for 1SS)
                    self.assertEqual(rb & 0x01, 1 if nss > 1 else 0)
                    # Bits 1..4 shifted right by 1 must equal MCS
                    self.assertEqual((rb & 0x1E) >> 1, mcs)
                    # Bits 5..6 must match bandwidth flag
                    expected_bw_flag = 0x20 if bw == 40 else (0x40 if bw == 80 else 0x00)
                    self.assertEqual(rb & 0x60, expected_bw_flag)
                    # Bit 7 must be zero
                    self.assertEqual(rb & 0x80, 0)
                    # Roundtrip decoding
                    d_mcs, d_bw, d_nss = decode_rate_byte(rb)
                    self.assertEqual((d_mcs, d_bw, d_nss), (mcs, bw, nss))

    def test_poll_subtype_1e_rate_override_layout(self):
        """Test airMAX Poll Subtype 0x1E 16-byte structure and offsets."""
        msg = build_poll_subtype_1e_rate_override(
            mcs=7,
            bw=40,
            nss=2,
            secondary_mcs=4,
            secondary_bw=40,
            secondary_nss=2,
            node_id=0x42,
            flags=0x01,
            raw_entry_1b=0x77,
        )

        # Total length must be exactly 16 bytes
        self.assertEqual(len(msg), 16)

        # Header offsets 0..3: Version 1 (big-endian)
        self.assertEqual(msg[0:4], b"\x00\x00\x00\x01")
        # Offset 4: record+4 (0x00)
        self.assertEqual(msg[4], 0x00)
        # Offsets 5..6: Subtype 0x001E (big-endian halfword)
        self.assertEqual(msg[5:7], b"\x00\x1e")
        # Offsets 7..8: record+8 (0x00, 0x00)
        self.assertEqual(msg[7:9], b"\x00\x00")

        # Payload offsets 9..13:
        # Offset 9: node_id (record+c)
        self.assertEqual(msg[9], 0x42)
        # Offset 10: flags (record+d)
        self.assertEqual(msg[10], 0x01)
        # Offset 11: Primary RateByte (record+e)
        expected_primary_rb = encode_rate_byte(mcs=7, bw=40, nss=2)
        self.assertEqual(msg[11], expected_primary_rb)
        self.assertEqual(msg[11], 0x2F)
        # Offset 12: raw_entry_1b (record+f)
        self.assertEqual(msg[12], 0x77)
        # Offset 13: Secondary RateByte (record+10)
        expected_sec_rb = encode_rate_byte(mcs=4, bw=40, nss=2)
        self.assertEqual(msg[13], expected_sec_rb)

        # Offsets 14..15: Zero padding to align 14 -> 16 bytes
        self.assertEqual(msg[14:16], b"\x00\x00")

    def test_poll_subtype_1e_parser(self):
        """Test parsing of Subtype 0x1E message."""
        msg = build_poll_subtype_1e_rate_override(
            mcs=8, bw=80, nss=2, node_id=12, flags=3, raw_entry_1b=9
        )
        parsed = parse_poll_subtype_1e_rate_override(msg)
        self.assertEqual(parsed["version"], 1)
        self.assertEqual(parsed["subtype"], POLL_SUBTYPE_RATE_OVERRIDE)
        self.assertEqual(parsed["node_id"], 12)
        self.assertEqual(parsed["flags"], 3)
        self.assertEqual(parsed["primary_mcs"], 8)
        self.assertEqual(parsed["primary_bw"], 80)
        self.assertEqual(parsed["primary_nss"], 2)
        self.assertEqual(parsed["raw_entry_1b"], 9)

    def test_poll_subtype_1e_endian_swap(self):
        """Test Subtype 0x1E with dword endian swap applied."""
        pre_swap = build_poll_subtype_1e_rate_override(mcs=5, bw=20, nss=1, swap_endian=False)
        post_swap = build_poll_subtype_1e_rate_override(mcs=5, bw=20, nss=1, swap_endian=True)

        self.assertEqual(len(post_swap), 16)
        self.assertEqual(endian_swap_dword(pre_swap), post_swap)
        # Parser with is_swapped=True recovers original fields
        parsed = parse_poll_subtype_1e_rate_override(post_swap, is_swapped=True)
        self.assertEqual(parsed["primary_mcs"], 5)
        self.assertEqual(parsed["primary_bw"], 20)
        self.assertEqual(parsed["primary_nss"], 1)

    def test_poll_subtype_17_txq_layout(self):
        """Test airMAX Poll Subtype 0x17 20-byte contention parameters layout."""
        msg = build_poll_subtype_17_txq(
            aifs=2,
            cwmin=3,
            cwmax=10,
            qflags=0x3A10,
            q_id=1,
        )

        # Total length must be exactly 20 bytes
        self.assertEqual(len(msg), 20)

        # Header offsets 0..3: Version 1
        self.assertEqual(msg[0:4], b"\x00\x00\x00\x01")
        # Offset 4: 0x00
        self.assertEqual(msg[4], 0x00)
        # Offsets 5..6: Subtype 0x0017
        self.assertEqual(msg[5:7], b"\x00\x17")
        # Offsets 7..8: 0x00, 0x00
        self.assertEqual(msg[7:9], b"\x00\x00")

        # Payload
        # Offset 9: q_id (record+c)
        self.assertEqual(msg[9], 0x01)
        # Offsets 10..11: AIFS (halfword, big-endian)
        self.assertEqual(struct.unpack(">H", msg[10:12])[0], 2)
        # Offsets 12..13: CWmin (halfword, big-endian)
        self.assertEqual(struct.unpack(">H", msg[12:14])[0], 3)
        # Offsets 14..15: CWmax (halfword, big-endian)
        self.assertEqual(struct.unpack(">H", msg[14:16])[0], 10)
        # Offsets 16..19: Qflags (word, big-endian)
        self.assertEqual(struct.unpack(">I", msg[16:20])[0], 0x3A10)

    def test_poll_subtype_17_txq_qflags_bitmask_filtering(self):
        """Test that Qflags enforces bitmask 0x3a10 (bits 4, 9, 11, 12, 13)."""
        # If caller passes all 1s (0xFFFFFFFF), only bits 4, 9, 11, 12, 13 (0x3A10) survive
        msg = build_poll_subtype_17_txq(aifs=2, cwmin=7, cwmax=15, qflags=0xFFFFFFFF)
        stored_flags = struct.unpack(">I", msg[16:20])[0]
        self.assertEqual(stored_flags, TXQ_QFLAGS_MASK)
        self.assertEqual(stored_flags, 0x3A10)

        # Individual bit tests:
        # bit 4 (0x0010)
        msg_bit4 = build_poll_subtype_17_txq(aifs=2, cwmin=7, cwmax=15, qflags=0x0010)
        self.assertEqual(struct.unpack(">I", msg_bit4[16:20])[0], 0x0010)

        # Unpermitted bit 3 (0x0008) must be filtered out
        msg_bit3 = build_poll_subtype_17_txq(aifs=2, cwmin=7, cwmax=15, qflags=0x0008)
        self.assertEqual(struct.unpack(">I", msg_bit3[16:20])[0], 0x0000)

    def test_poll_subtype_17_parser(self):
        """Test parsing of Subtype 0x17 message."""
        msg = build_poll_subtype_17_txq(aifs=4, cwmin=15, cwmax=63, qflags=0x3A10, q_id=2)
        parsed = parse_poll_subtype_17_txq(msg)
        self.assertEqual(parsed["version"], 1)
        self.assertEqual(parsed["subtype"], POLL_SUBTYPE_TXQ)
        self.assertEqual(parsed["q_id"], 2)
        self.assertEqual(parsed["aifs"], 4)
        self.assertEqual(parsed["cwmin"], 15)
        self.assertEqual(parsed["cwmax"], 63)
        self.assertEqual(parsed["qflags"], 0x3A10)
        self.assertTrue(parsed["qflags_valid_mask"])

    def test_poll_subtype_17_endian_swap(self):
        """Test Subtype 0x17 with dword endian swap applied."""
        pre_swap = build_poll_subtype_17_txq(aifs=2, cwmin=3, cwmax=10, qflags=0x3A10, swap_endian=False)
        post_swap = build_poll_subtype_17_txq(aifs=2, cwmin=3, cwmax=10, qflags=0x3A10, swap_endian=True)

        self.assertEqual(len(post_swap), 20)
        self.assertEqual(endian_swap_dword(pre_swap), post_swap)
        parsed = parse_poll_subtype_17_txq(post_swap, is_swapped=True)
        self.assertEqual(parsed["aifs"], 2)
        self.assertEqual(parsed["cwmin"], 3)
        self.assertEqual(parsed["cwmax"], 10)
        self.assertEqual(parsed["qflags"], 0x3A10)

    def test_whal_rate_table_calculations(self):
        """Test WHAL rate table row index calculations from UMAC_DATAPATH.md Table B."""
        # VHT20: base 60
        self.assertEqual(get_whal_rate_index(mcs=0, nss=1, bw=20), 60)
        self.assertEqual(get_whal_rate_index(mcs=9, nss=1, bw=20), 69)
        self.assertEqual(get_whal_rate_index(mcs=0, nss=2, bw=20), 70)
        self.assertEqual(get_whal_rate_index(mcs=7, nss=2, bw=20), 77)
        self.assertEqual(get_whal_rate_index(mcs=9, nss=2, bw=20), 79)

        # VHT40: base 90
        self.assertEqual(get_whal_rate_index(mcs=0, nss=1, bw=40), 90)
        self.assertEqual(get_whal_rate_index(mcs=7, nss=2, bw=40), 107)
        self.assertEqual(get_whal_rate_index(mcs=9, nss=2, bw=40), 109)

        # VHT80: base 120
        self.assertEqual(get_whal_rate_index(mcs=0, nss=1, bw=80), 120)
        self.assertEqual(get_whal_rate_index(mcs=9, nss=2, bw=80), 139)

        # Code byte formula: 0xC0 | ((nss-1)<<4) | mcs
        self.assertEqual(get_whal_code_byte(mcs=0, nss=1), 0xC0)
        self.assertEqual(get_whal_code_byte(mcs=7, nss=2), 0xD7)
        self.assertEqual(get_whal_code_byte(mcs=9, nss=2), 0xD9)
        self.assertEqual(get_whal_code_byte(mcs=7, nss=1, is_vht=False), 0x87)
        self.assertEqual(get_whal_code_byte(mcs=7, nss=2, is_vht=False), 0x97)

    def test_wmi_rate_schedule_188b_layout_and_opcodes(self):
        """Test WMI native rate schedule 188-byte serializer, Gen1 opcode 0x9044, Gen2 opcode 0x9045."""
        sched_gen1 = build_wmi_rate_schedule_188b(
            mcs=7,
            nss=2,
            bw=40,
            gen=1,
            node_id=0x100,
            mac="00:15:6D:AA:BB:CC",
            retry_count=4,
        )

        # Total size must be exactly 188 bytes (0xBC bytes)
        self.assertEqual(len(sched_gen1), 188)
        self.assertIsInstance(sched_gen1, bytes)
        self.assertIsInstance(sched_gen1, WmiRateSchedule)

        # Opcode and properties
        self.assertEqual(sched_gen1.opcode, WMI_RATE_SCHED_CMDID_GEN1)
        self.assertEqual(sched_gen1.opcode, 0x9044)
        self.assertEqual(sched_gen1.gen, 1)
        self.assertEqual(sched_gen1.row_index, 107)  # 90 + (2-1)*10 + 7 = 107
        self.assertEqual(sched_gen1.code_byte, 0xD7)

        # Check Gen2 opcode 0x9045
        sched_gen2 = build_wmi_rate_schedule_188b(mcs=7, nss=2, bw=40, gen=2)
        self.assertEqual(sched_gen2.opcode, WMI_RATE_SCHED_CMDID_GEN2)
        self.assertEqual(sched_gen2.opcode, 0x9045)
        self.assertEqual(sched_gen2.gen, 2)
        self.assertEqual(len(sched_gen2), 188)

        # Verify internal byte offsets from UMAC_DATAPATH.md lines 163-172:
        # +0x00: word store (node_id = 0x100)
        self.assertEqual(struct.unpack(">I", sched_gen1[0x00:0x04])[0], 0x100)

        # +0x04, +0x08: 6 bytes from incoming a1 (MAC)
        self.assertEqual(sched_gen1[0x04:0x08], bytes.fromhex("00156daa"))
        self.assertEqual(sched_gen1[0x08:0x0A], bytes.fromhex("bbcc"))

        # +0x0C..0x20: Six words for rate row indices (each 107)
        for i in range(6):
            offset = 0x0C + i * 4
            self.assertEqual(struct.unpack(">I", sched_gen1[offset : offset + 4])[0], 107)

        # +0x24..0x38: Six halfwords expanded to word slots (retry count = 4)
        for i in range(6):
            offset = 0x24 + i * 4
            self.assertEqual(struct.unpack(">I", sched_gen1[offset : offset + 4])[0], 4)

        # +0x54..0x68: Six stream mask words (nss = 2)
        for i in range(6):
            offset = 0x54 + i * 4
            self.assertEqual(struct.unpack(">I", sched_gen1[offset : offset + 4])[0], 2)

        # Total 188 bytes ends at 0xBC (0x84 + 14*4 = 0xBC = 188)
        self.assertEqual(len(sched_gen1), 0xBC)

    def test_wmi_rate_schedule_188b_parser(self):
        """Test parsing of 188-byte native rate schedule."""
        sched = build_wmi_rate_schedule_188b(
            mcs=8,
            nss=2,
            bw=80,
            node_id=0x50,
            mac="aa:bb:cc:dd:ee:ff",
            retry_count=3,
        )
        parsed = parse_wmi_rate_schedule_188b(sched)
        self.assertEqual(parsed["node_id"], 0x50)
        self.assertEqual(parsed["mac"], "aa:bb:cc:dd:ee:ff")
        self.assertEqual(parsed["primary_row_index"], 138)  # 120 + 10 + 8
        self.assertEqual(parsed["retry_counts"], [3] * 6)
        self.assertEqual(parsed["stream_masks"], [2] * 6)

    def test_wmi_rate_schedule_endian_swap(self):
        """Test 188-byte schedule with endian swap."""
        pre_swap = build_wmi_rate_schedule_188b(mcs=7, nss=2, bw=40, swap_endian=False)
        post_swap = build_wmi_rate_schedule_188b(mcs=7, nss=2, bw=40, swap_endian=True)

        self.assertEqual(len(post_swap), 188)
        self.assertEqual(endian_swap_dword(pre_swap), post_swap)
        parsed = parse_wmi_rate_schedule_188b(post_swap, is_swapped=True)
        self.assertEqual(parsed["primary_row_index"], 107)


if __name__ == "__main__":
    unittest.main()
